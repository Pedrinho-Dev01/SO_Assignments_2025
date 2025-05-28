% GA Final Script with the best parameters found by tuning

clc; clear;

[popul_size, mut_rate, elitism] = ga_tune();

n_runs = 10;
fprintf('\nRunning final GA with best parameters...\n');
fprintf('  PopSize = %d, MutationRate = %.2f, Elitism = %d\n', ...
        popul_size, mut_rate, elitism);

ga_results = ga_algorithm(popul_size, mut_rate, elitism, n_runs);

fprintf('\nFinal Results:\n');
disp(ga_results);
