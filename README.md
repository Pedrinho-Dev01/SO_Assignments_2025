# SO_mini_assignment

An assigment for the Simulation and Optimization course.

## Members
- Daniel Pedrinho Nº107378
- Sara Almeida Nº108796

# Usage 

Run the commands provided below in the **root** directory of the repository. 

## Exercise 1:

### Exercise 1.1
```bash
python3 exercise1/simulation1_1.py 
```

### Exercise 1.2
```bash
python3 exercise1/simulation1_2.py 
```

## Exercise 2:

### Command Line Arguments
x0 = Initial x position \
z0 = Initial z position \
vx0 = Initial x velocity \
vz0 = Initial z velocity \
u = Drag coefficient \
m = Mass of the object \
g = Gravity <!-- Defaulted to 9.81, not necessary to use parameter --> \
dt = Time step \
t_final = Final time

### Exercise 2.1
```bash
python3 exercise2/simulation2_1.py --x0 0 --z0 0 --vx0 10 --vz0 10 --u 0.1 --m 1.0 --g 9.81 --dt 0.01 --t_final 5.0 
```

#### Input File
Example file provided in <span style="color:red; font-weight: bold;">exercise2/simu_input_file.json</span>

```bash
python3 exercise2/simulation2_1.py --param_file exercise2/simu_input_file.json
```

### Exercise 2.2
```bash
python3 exercise2/simulation2_2.py --x0 0 --z0 0 --vx0 10 --vz0 10 --u 0.1 --m 1.0 --g 9.81 --dt 0.01 --t_final 5.0 
```

#### Input File
Example file provided in <span style="color:red; font-weight: bold;">exercise2/simu_input_file.json</span>

```bash
python3 exercise2/simulation2_2.py --param_file exercise2/simu_input_file.json
```

### Exercise 2.3
```bash
python3 exercise2/simulation2_3.py --x0 0 --z0 0 --vx0 10 --vz0 10 --u 0.1 --m 1.0 --g 9.81 --dt 0.01 --t_final 5.0 
```

#### Input File
Example file provided in <span style="color:red; font-weight: bold;">exercise2/simu_input_file.json</span>

```bash
python3 exercise2/simulation2_3.py --param_file exercise2/simu_input_file.json
```


