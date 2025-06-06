% GA Final Script with the best parameters found by tuning

clc; clear;

% [popul_size, mut_rate, elitism] = ga_tune();
popul_size = 100;  
mut_rate = 0.1;   
elitism = 1;  
n_runs = 10;
max_time = 30;

fprintf('\nRunning final GA with best parameters...\n');
fprintf('  PopSize = %d, MutationRate = %.2f, Elitism = %d\n', ...
        popul_size, mut_rate, elitism);

ga_results = ga_algorithm(popul_size, mut_rate, elitism, n_runs, max_time);

fprintf('\nFinal Results:\n');
disp(ga_results);

% Save final GA configuration and results to CSV
T = table(popul_size, mut_rate, elitism, ...
          ga_results.min, ga_results.mean, ga_results.max, ...
          'VariableNames', {'PopSize', 'MutationRate', 'Elitism', 'Min', 'Mean', 'Max'});

writetable(T, 'ga_final_results_table.csv');

%-------------------------------plotting fitness per run------------------------------------%
// fitness_runs = ga_results.all(:);  % ensure column vector
// runs = 1:length(fitness_runs);

// figure;
// plot(runs, fitness_runs, '-o', 'LineWidth', 2);
// xlabel('Run Number');
// ylabel('Best Fitness');
// title('Best Fitness per GA Run');
// grid on;

// saveas(gcf, 'ga_runs_linechart.pdf');
