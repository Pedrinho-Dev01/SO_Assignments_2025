# SO_mini_assignment

An assigment for the Simulation and Optimization course.

## Members
- Daniel Pedrinho Nº107378
- Sara Almeida Nº108796

# Usage:
## 2.1

### Command Line Arguments
x0 = Initial x position
z0 = Initial z position
vx0 = Initial x velocity
vz0 = Initial z velocity
u = Drag coefficient
m = Mass of the object
g = Gravity <!-- Defaulted to 9.81, not necessary to use parameter -->
dt = Time step
t_final = Final time

```bash
python3 simulation2_1.py --x0 0 --z0 0 --vx0 10 --vz0 10 --u 0.1 --m 1.0 --g 9.81 --dt 0.01 --t_final 5.0 
```

### Input File
Example file provided in <span style="color:red; font-weight: bold;">simu2_1_input_file.json</span>

```bash
python3 simulation2_1.py --param_file simu2_1_input_file.json
```

