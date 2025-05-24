function stats = grasp_algorithm(alpha, max_time, n_runs)

    % Default parameters
    Cmax = 1000;
    n_controllers = 12;

    % Load adjacency matrix
    L = load('../L200.txt');
    num_nodes = size(L,1);
    
    % Set off-diagonal zeros to inf
    G = L;
    G(G == 0 & ~eye(num_nodes)) = inf;
    G(eye(num_nodes) == 1) = 0;
    
    % Compute all-pairs shortest paths using Floyd-Warshall
    dist_matrix = floyd_warshall(G);
    
    % If any inf remain, set to large value
    if any(isinf(dist_matrix(:)))
        max_finite = max(dist_matrix(isfinite(dist_matrix)));
        dist_matrix(isinf(dist_matrix)) = max_finite * 10;
    end

    % Precompute infeasible controller pairs (distance > Cmax)
    infeasible_pairs = dist_matrix > Cmax & ~eye(num_nodes);

    % Store objective values for statistics
    obj_values = zeros(n_runs,1);

    for run = 1:n_runs
        t_start = tic;
        best_obj = Inf;
        while toc(t_start) < max_time
            controllers = grasp_construct(dist_matrix, infeasible_pairs, n_controllers, alpha);
            assignment = assign_nodes(dist_matrix, controllers);
            obj = compute_objective(dist_matrix, controllers, assignment);
            [controllers_ls, assignment_ls, obj_ls] = local_search(dist_matrix, infeasible_pairs, controllers, assignment, obj, n_controllers);
            if obj_ls < best_obj
                best_obj = obj_ls;
            end
        end
        obj_values(run) = best_obj;
    end

    % Report statistics
    fprintf('\nGRASP results over %d runs (each %.0f seconds):\n', n_runs, max_time);
    fprintf('Minimum objective: %.4f\n', min(obj_values));
    fprintf('Average objective: %.4f\n', mean(obj_values));
    fprintf('Maximum objective: %.4f\n', max(obj_values));

    % Return stats
    stats.min = min(obj_values);
    stats.mean = mean(obj_values);
    stats.max = max(obj_values);
end

function controllers = grasp_construct(dist_matrix, infeasible_pairs, n_controllers, alpha)
    num_nodes = size(dist_matrix,1);
    controllers = [];
    candidates = 1:num_nodes;

    while numel(controllers) < n_controllers
        % For each candidate, compute its minimum distance to already selected controllers (or inf if none)
        min_dist = zeros(1, numel(candidates));
        for idx = 1:numel(candidates)
            c = candidates(idx);
            if isempty(controllers)
                min_dist(idx) = 0; % First controller, no constraints
            else
                dists = dist_matrix(c, controllers);
                min_dist(idx) = min(dists);
            end
        end

        % Build Restricted Candidate List (RCL)
        threshold = min(min_dist) + alpha * (max(min_dist) - min(min_dist));
        RCL = candidates(min_dist <= threshold);

        % Remove candidates violating Cmax with already selected controllers
        feasible = true(1, numel(RCL));
        for i = 1:numel(RCL)
            c = RCL(i);
            if any(infeasible_pairs(c, controllers))
                feasible(i) = false;
            end
        end
        RCL = RCL(feasible);

        if isempty(RCL)
            % If no feasible candidates, break and fill randomly (should rarely happen)
            left = setdiff(candidates, controllers);
            RCL = left;
        end

        % Randomly select from RCL
        new_controller = RCL(randi(numel(RCL)));
        controllers = [controllers, new_controller];
        candidates = setdiff(candidates, new_controller);
    end
end

function assignment = assign_nodes(dist_matrix, controllers)
    % Assign each node to its closest controller
    num_nodes = size(dist_matrix,1);
    assignment = zeros(1,num_nodes);
    for j = 1:num_nodes
        [~, idx] = min(dist_matrix(controllers, j));
        assignment(j) = controllers(idx);
    end
end

function obj = compute_objective(dist_matrix, controllers, assignment)
    % Average distance from each node to its assigned controller
    num_nodes = size(dist_matrix,1);
    sum_dist = 0;
    for j = 1:num_nodes
        sum_dist = sum_dist + dist_matrix(assignment(j), j);
    end
    obj = sum_dist / num_nodes;
end

function [controllers_best, assignment_best, obj_best] = local_search(dist_matrix, infeasible_pairs, controllers, assignment, obj, n_controllers)
    % Simple local search: try swapping one controller at a time
    num_nodes = size(dist_matrix,1);
    controllers_best = controllers;
    assignment_best = assignment;
    obj_best = obj;
    improved = true;

    while improved
        improved = false;
        for i = 1:n_controllers
            for candidate = setdiff(1:num_nodes, controllers_best)
                % Check Cmax constraint
                temp = controllers_best;
                temp(i) = candidate;
                if any(any(infeasible_pairs(temp, temp)))
                    continue;
                end
                % Assign nodes
                assignment_temp = assign_nodes(dist_matrix, temp);
                obj_temp = compute_objective(dist_matrix, temp, assignment_temp);
                if obj_temp < obj_best
                    controllers_best = temp;
                    assignment_best = assignment_temp;
                    obj_best = obj_temp;
                    improved = true;
                    break;
                end
            end
            if improved
                break;
            end
        end
    end
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
