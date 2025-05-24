% GRASP Alpha Parameter Optimizer

clear; clc;

alphas = 0:0.1:1;         % Greediness (0=greedy, 1=random)
max_time = 10;            % seconds per run
n_runs   = 3;             % number of GRASP runs per alpha

results = [];             % Store results

for a = 1:length(alphas)
    alpha = alphas(a);
    fprintf('Testing alpha=%.2f ...\n', alpha);
    stats = grasp_algorithm(alpha, max_time, n_runs);
    results = [results; alpha, stats.min, stats.mean, stats.max];
end

% Display results as a table
results_table = array2table(results, ...
    'VariableNames', {'Alpha','MinObj','MeanObj','MaxObj'});
disp(results_table);

% Find and print the optimal alpha
[~, best_idx] = min(results(:,2));
best_alpha = results(best_idx, 1);
fprintf('The optimal value of alpha is: %.2f\n', best_alpha);

% Plot mean objective vs. alpha
figure;
plot(results(:,1), results(:,3), '-o', 'LineWidth', 2);
xlabel('\alpha (greediness/randomness)');
ylabel('Mean Objective');
title('GRASP Parameter: Alpha');
grid on;
