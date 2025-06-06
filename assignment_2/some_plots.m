%------------------------------comparison plot-------------------------------------%

GA_stats = [143.1600, 145.3230, 148.3550];         % [min, avg, max]
GRASP_stats = [143.0850, 143.6640, 144.8900];      % [min, avg, max]
ILP_value = 145.22;                      % unique value

data = [
    GA_stats;
    GRASP_stats;
    [NaN, ILP_value, NaN]  % ILP only has one bar
];

% Labels for X axis
xticklabels = {'GA', 'GRASP', 'ILP'};

% Plot
figure;
b = bar(data, 'grouped');
set(gca, 'XTickLabel', xticklabels);

% Customize bar colors
b(1).FaceColor = [0.2 0.4 0.8];  % Min
b(2).FaceColor = [1.0 0.5 0.0];  % Avg
b(3).FaceColor = [1.0 0.8 0.0];  % Max

legend({'Min', 'Avg', 'Max'}, 'Location', 'northoutside', 'Orientation', 'horizontal');
ylabel('Average Shortest Path Length');
title('Comparison of GA, GRASP and ILP');

% Improve visual layout
grid on;
ylim([ILP_value - 1, max([GA_stats GRASP_stats]) + 1]);

saveas(gcf, 'comparison_fixed.pdf');

%-----------------------function for graph construction----------------------------%

Nodes = load('Nodes200.txt');
Links = load('Links200.txt');

function plotTopology(Nodes, Links, controllers)
    g = graph(Links(:,1), Links(:,2));
    plot(g, 'XData', Nodes(:,1), 'YData', Nodes(:,2), ...
         'NodeColor', [0.6 0.6 0.6], 'EdgeAlpha', 0.3, ...
         'MarkerSize', 4);
    hold on;
    plot(Nodes(controllers,1), Nodes(controllers,2), 'ro', ...
         'MarkerSize', 8, 'MarkerFaceColor', 'r');
    hold off;
end

%------------------------------ga graph--------------------------------------------%

best_solution = [20 30 53 65 90 107 108 110 121 146 163 173];

figure;
plotTopology(Nodes, Links, best_solution); 
title('Best Controller Placement (GA)');
saveas(gcf, 'ga_topology.pdf');

%------------------------------grasp graph-----------------------------------------%

best_solution = [20 30 65 68 90 91 107 108 131 146 163 173];

figure;
plotTopology(Nodes, Links, best_solution);  
title('Best Controller Placement (GRASP)');
saveas(gcf, 'grasp_topology.pdf');
