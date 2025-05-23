function generate_sdn_lp()
    % PARAMETERS
    num_nodes = 200;
    Cmax = 1000;
    n_controllers = 12;
    links_file = 'Links200.txt';
    lengths_file = 'L200.txt';
    lp_filename = 'sdn_problem.lp';

    % STEP 1: Load graph and compute ACTUAL shortest paths
    fprintf('Loading and analyzing distance matrix...\n');
    dist_matrix = compute_shortest_paths(lengths_file, num_nodes);

    % STEP 2: Generate LP file
    generate_lp_file(1:num_nodes, dist_matrix, Cmax, n_controllers, lp_filename);
    
    fprintf('\nLP file "%s" generated successfully.\n', lp_filename);
   
end

function dist_matrix = compute_shortest_paths(lengths_file, num_nodes)
    % Load the adjacency/distance matrix
    L = load(lengths_file);  % This might be adjacency matrix, not shortest paths
    
    if size(L, 1) ~= num_nodes || size(L, 2) ~= num_nodes
        error('L200.txt must be a 200x200 matrix.');
    end
    
    % Check if L contains shortest paths or just direct connections
    num_zeros = sum(L(:) == 0);
    diagonal_zeros = sum(diag(L) == 0);
    off_diagonal_zeros = num_zeros - diagonal_zeros;
    
    fprintf('Matrix analysis:\n');
    fprintf('Total zeros: %d, Diagonal zeros: %d, Off-diagonal zeros: %d\n', ...
        num_zeros, diagonal_zeros, off_diagonal_zeros);
    
    if off_diagonal_zeros > num_nodes * 2  % Too many zeros, likely adjacency matrix
        fprintf('Matrix appears to be adjacency matrix, computing shortest paths...\n');
        
        % Convert to proper distance matrix for shortest path computation
        G = L;
        G(G == 0 & eye(num_nodes) == 0) = inf;  % Set non-connected pairs to infinity
        G(eye(num_nodes) == 1) = 0;  % Diagonal remains zero
        
        % Compute all-pairs shortest paths using Floyd-Warshall
        dist_matrix = floyd_warshall(G);
        
        % Check if graph is connected
        if any(isinf(dist_matrix(:)))
            fprintf('WARNING: Graph is not fully connected!\n');
            fprintf('Number of infinite distances: %d\n', sum(isinf(dist_matrix(:))));
            
            % Replace infinite distances with a large value for LP solving
            max_finite = max(dist_matrix(isfinite(dist_matrix)));
            dist_matrix(isinf(dist_matrix)) = max_finite * 10;
        end
        
    else
        fprintf('Matrix appears to contain shortest paths already.\n');
        dist_matrix = L;
    end
    
    % Final statistics
    fprintf('Final distance matrix stats:\n');
    fprintf('Min: %.2f, Max: %.2f, Mean: %.2f\n', ...
        min(dist_matrix(:)), max(dist_matrix(:)), mean(dist_matrix(:)));
    fprintf('Zero distances: %d (should be %d for diagonal only)\n', ...
        sum(dist_matrix(:) == 0), num_nodes);
end

function D = floyd_warshall(G)
    % Floyd-Warshall algorithm for all-pairs shortest paths
    n = size(G, 1);
    D = G;
    
    fprintf('Computing shortest paths using Floyd-Warshall...\n');
    
    for k = 1:n
        if mod(k, 50) == 0
            fprintf('Progress: %d/%d\n', k, n);
        end
        
        for i = 1:n
            for j = 1:n
                if D(i,k) + D(k,j) < D(i,j)
                    D(i,j) = D(i,k) + D(k,j);
                end
            end
        end
    end
    
    fprintf('Shortest path computation completed.\n');
end

function generate_lp_file(nodes, dist_matrix, Cmax, n_controllers, filename)
    N = length(nodes);
    fid = fopen(filename, 'w');

    %% Objective function - minimize average distance to closest controller
    fprintf(fid, 'min: ');
    terms = {};
    for i = 1:N  % controllers
        for j = 1:N  % switches
            cost = dist_matrix(i,j);
            if isfinite(cost)
                % Scale by 1/N to get average, and use full precision
                terms{end+1} = sprintf('%.8f y_%d_%d', cost/N, i, j);
            end
        end
    end
    fprintf(fid, '%s;\n\n', strjoin(terms, ' + '));

    %% Constraint: Exactly n controllers
    fprintf(fid, '%s = %d;\n\n', ...
        strjoin(arrayfun(@(i) sprintf('x_%d', i), 1:N, 'UniformOutput', false), ' + '), n_controllers);

    %% Constraint: Each switch assigned to exactly one controller
    for j = 1:N
        terms = arrayfun(@(i) sprintf('y_%d_%d', i, j), 1:N, 'UniformOutput', false);
        fprintf(fid, '%s = 1;\n', strjoin(terms, ' + '));
    end
    fprintf(fid, '\n');

    %% Constraint: Can only assign to active controllers
    for i = 1:N
        for j = 1:N
            fprintf(fid, 'y_%d_%d <= x_%d;\n', i, j, i);
        end
    end
    fprintf(fid, '\n');

    %% Constraint: Controller-controller max distance
    for i = 1:N
        for j = i+1:N
            if isfinite(dist_matrix(i,j)) && dist_matrix(i,j) > Cmax
                fprintf(fid, 'x_%d + x_%d <= 1;\n', i, j);
            end
        end
    end
    fprintf(fid, '\n');

    %% Constraint: Each selected controller must serve at least itself
    for i = 1:N
        fprintf(fid, 'y_%d_%d >= x_%d;\n', i, i, i);
    end
    fprintf(fid, '\n');

    %% Declare binary variables
    fprintf(fid, 'bin\n');
    for i = 1:N
        fprintf(fid, 'x_%d\n', i);
    end
    for i = 1:N
        for j = 1:N
            fprintf(fid, 'y_%d_%d\n', i, j);
        end
    end

    fprintf(fid, ';\n');
    fclose(fid);
end