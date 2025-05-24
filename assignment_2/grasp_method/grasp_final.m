% GRASP Final Script

clear; clc;

alpha = 0.3;
max_time = 30;
n_runs = 10;

results = [];  

fprintf('Running GRASP with alpha=%.2f', alpha);
stats = grasp_algorithm(alpha, max_time, n_runs);
results = [alpha, stats.min, stats.mean, stats.max];
fprintf(' ... completed.\n');
