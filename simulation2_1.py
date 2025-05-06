import numpy as np
import matplotlib.pyplot as plt
import argparse
import json
import sys

def simulate(params):
    # Unpack parameters
    x = params['x0']
    z = params['z0']
    vx = params['vx0']
    vz = params['vz0']
    u = params['u']
    m = params['m']
    g = params['g']
    dt = params['dt']
    t_final = params['t_final']

    time = np.arange(0, t_final, dt)
    x_vals, z_vals = [], []

    for _ in time:
        x_vals.append(x)
        z_vals.append(z)

        ax = -u/m * vx**2 * np.sign(vx)
        az = -g - u/m * vz**2 * np.sign(vz)

        vx += dt * ax
        vz += dt * az
        x += dt * vx
        z += dt * vz

    return x_vals, z_vals

def main():
    parser = argparse.ArgumentParser(description="Projectile simulation with air resistance using Euler method.")
    parser.add_argument("--x0", type=float, help="Initial x position")
    parser.add_argument("--z0", type=float, help="Initial z position")
    parser.add_argument("--vx0", type=float, help="Initial x velocity")
    parser.add_argument("--vz0", type=float, help="Initial z velocity")
    parser.add_argument("--u", type=float, help="Air resistance coefficient")
    parser.add_argument("--m", type=float, help="Mass")
    parser.add_argument("--g", type=float, default=9.81, help="Gravity (default: 9.81)")
    parser.add_argument("--dt", type=float, help="Time step")
    parser.add_argument("--t_final", type=float, help="Final simulation time")
    parser.add_argument("--param_file", type=str, help="Path to JSON file with parameters")

    args = parser.parse_args()

    # Load parameters
    if args.param_file:
        try:
            with open(args.param_file, 'r') as f:
                params = json.load(f)
        except Exception as e:
            print("Failed to read parameter file:", e)
            sys.exit(1)
    else:
        required = ['x0', 'z0', 'vx0', 'vz0', 'u', 'm', 'dt', 't_final']
        if not all(getattr(args, k) is not None for k in required):
            print("Missing required arguments. Use --help for usage.")
            sys.exit(1)
        params = vars(args)

    # Run simulation
    x_vals, z_vals = simulate(params)

    # Plot result
    plt.plot(x_vals, z_vals)
    plt.xlabel("x position")
    plt.ylabel("z position")
    plt.title("Projectile Motion with Air Resistance")
    plt.grid()
    plt.show()

if __name__ == "__main__":
    main()
