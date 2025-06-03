function ga_calculate = ga_algorithm(popul_size, prob_mutation, elitism_count, n_runs, max_time)
    % Genetic Algorithm with elitist selection for SDN controller placement
    % Inputs:
    %   popul_size     - number of individuals in population
    %   prob_mutation  - mutation rate
    %   elitism_count  - number of elite individuals kept
    %   n_runs         - how many times to run the GA
    % Output:
    %   ga_calculate   - struct with min, mean, max fitness across runs

    n_controllers = 12;
    n_nodes = 200;
    Cmax = 1000;

    L = load('../L200.txt');
    dist_matrix = preprocess_distances(L);
    infeasible_pairs = dist_matrix > Cmax;

    best_values = zeros(n_runs, 1);

    for run = 1:n_runs
        t_start = tic;

        % Initialize population
        population = {};
        while numel(population) < popul_size
            individual = randperm(n_nodes, n_controllers);
            if is_valid(individual, infeasible_pairs)
                population{end+1} = individual;
            end
        end

        fitness = evaluate_population(population, dist_matrix);
        best_fit = min(fitness);
        best_time = 0;
        s_best = population{find(fitness == best_fit, 1)};

        % Evolve population
        while toc(t_start) < max_time
            new_population = {};
            while numel(new_population) < popul_size
                p1 = tournament_selection(population, fitness);
                p2 = tournament_selection(population, fitness);
                child = crossover(p1, p2, n_controllers, infeasible_pairs);
                child = mutate(child, n_nodes, prob_mutation, infeasible_pairs);
                new_population{end+1} = child;
            end

            % Select elitism_count best from old population
            [~, idx_old] = sort(fitness);
            elite_individuals = population(idx_old(1:elitism_count));
            elite_fitness = fitness(idx_old(1:elitism_count));
            
            % Evaluate new_population
            new_population_fitness = evaluate_population(new_population, dist_matrix);
            
            % Select the best remaining individuals from new_population
            remaining_needed = popul_size - elitism_count;
            [~, idx_off] = sort(new_population_fitness);
            selected_new_population = new_population(idx_off(1:remaining_needed));
            selected_fitness = new_population_fitness(idx_off(1:remaining_needed));
            
            % Combine to form next generation
            population = [elite_individuals, selected_new_population];
            fitness = [elite_fitness; selected_fitness];


            % Track best solution
            [current_best, i_best] = min(fitness);
            if current_best < best_fit
                best_fit = current_best;
                best_time = toc(t_start);
                s_best = population{i_best};
            end
        end

        fprintf('Run %d: Best = %.4f at %.2fs | Solution: %s\n', ...
                run, best_fit, best_time, mat2str(s_best));
        best_values(run) = best_fit;
    end

    % Return stats
    ga_calculate.min = min(best_values);
    ga_calculate.mean = mean(best_values);
    ga_calculate.max = max(best_values);
end

% === Helper functions ===

% Getting a distance matrix with shortest path lengths between all node pairs
function dist_matrix = preprocess_distances(L)
    n = size(L,1);
    L(L == 0 & ~eye(n)) = inf;
    L(eye(n) == 1) = 0;
    dist_matrix = floyd_warshall(L); % computes the shortest paths
end

function D = floyd_warshall(G)
    n = size(G, 1);
    D = G;
    for k = 1:n
        for i = 1:n
            for j = 1:n
                if D(i,k) + D(k,j) < D(i,j)
                    D(i,j) = D(i,k) + D(k,j);
                end
            end
        end
    end
end

% Function to check if a set of controllers is valid - distances <= Cmax)
function valid = is_valid(controllers, infeasible_pairs)
    if numel(controllers) < 2
        valid = true;
        return;
    end

    pairs = nchoosek(controllers, 2);
    for k = 1:size(pairs,1)
        if infeasible_pairs(pairs(k,1), pairs(k,2))
            valid = false;
            return;
        end
    end
    valid = true;
end

% Computes the objective value of each individual in the population
function fitness = evaluate_population(population, dist_matrix)
    fitness = zeros(numel(population), 1);
    for i = 1:numel(population)
        fitness(i) = compute_objective(population{i}, dist_matrix);
    end
end

% Calculates the fitness of a solution
function obj = compute_objective(controllers, dist_matrix)
    total = 0;
    for j = 1:size(dist_matrix, 1)
        dists = dist_matrix(controllers, j);
        total = total + min(dists);
    end
    obj = total / size(dist_matrix, 1);
end

% Selection of an individual using tournament selection
function selected = tournament_selection(population, fitness)
    k = 2;
    candidates = randperm(numel(population), k);
    [~, idx] = min(fitness(candidates));
    selected = population{candidates(idx)};
end

% Child solution by combining two parents solutions. 
function child = crossover(p1, p2, n_controllers, infeasible_pairs)
    common = intersect(p1, p2);
    remaining = setdiff(union(p1, p2), common);
    child = common;
    while numel(child) < n_controllers && ~isempty(remaining)
        idx = randi(numel(remaining));
        candidate = remaining(idx);
        if is_valid([child, candidate], infeasible_pairs)
            child = [child, candidate];
        end
        remaining(idx) = [];
    end
    if numel(child) < n_controllers
        rest = setdiff(1:size(infeasible_pairs,1), child);
        for r = rest(randperm(numel(rest)))
            if is_valid([child, r], infeasible_pairs)
                child = [child, r];
                if numel(child) == n_controllers
                    break;
                end
            end
        end
    end
end

% Tries to modify one gene in the individuall
function mutated = mutate(ind, num_nodes, prob_mutation, infeasible_pairs)
    mutated = ind;
    if rand < prob_mutation
        for attempt = 1:10 %10 attempts are made to find a valid mutation
            idx = randi(numel(ind));
            new_gene = randi(num_nodes);
            trial = mutated;
            trial(idx) = new_gene;
            if numel(unique(trial)) == numel(trial) && is_valid(trial, infeasible_pairs)
                mutated = trial;
                break;
            end
        end
    end
end
