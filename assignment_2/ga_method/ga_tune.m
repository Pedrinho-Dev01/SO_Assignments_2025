function [best_popul_size, best_mutation_prob, best_elitism] = ga_tune()
% ga_tune - Function to test multiple GA configurations and return the best
% Outputs:
%   best_popul_size    - best population size
%   best_mutation_prob - best mutation prob
%   best_elitism       - best elitism count

% Parameter ranges to test
popul_sizes = [20, 50, 100, 150, 200];
mutation_probs = [0.01, 0.05, 0.1];
elitism_counts = [1, 2];
n_runs = 3;  % Short for tuning
max_time = 30; 

results = [];

for p = 1:length(popul_sizes)
    for m = 1:length(mutation_probs)
        for e = 1:length(elitism_counts)
            pop = popul_sizes(p);
            mut = mutation_probs(m);
            elite = elitism_counts(e);

            fprintf('Testing GA with Pop=%d, Mut=%.2f, Elitism=%d\n', pop, mut, elite);
            stats = ga_algorithm(pop, mut, elite, n_runs, max_time);
            results = [results; pop, mut, elite, stats.min, stats.mean, stats.max];
        end
    end
end

% Display all results
results_table = array2table(results, ...
    'VariableNames', {'PopSize','MutationRate','Elitism','Min','Mean','Max'});
disp(results_table);

% Identify best by lowest Mean
[~, best_idx] = min(results(:,5));
best_popul_size = results(best_idx, 1);
best_mutation_prob = results(best_idx, 2);
best_elitism = results(best_idx, 3);

fprintf('\nBest Configuration Found:\n');
fprintf('  Population Size: %d\n', best_popul_size);
fprintf('  Mutation Rate: %.2f\n', best_mutation_prob);
fprintf('  Elitism Count: %d\n', best_elitism);
end
