import numpy as np
import matplotlib.pyplot as plt
import argparse
import json
import sys
import os

def simulate_euler(params):
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
    vx_vals, vz_vals = [], []

    for _ in time:
        x_vals.append(x)
        z_vals.append(z)
        vx_vals.append(vx)
        vz_vals.append(vz)

        ax = -u/m * vx**2 * np.sign(vx)
        az = -g - u/m * vz**2 * np.sign(vz)

        vx += dt * ax
        vz += dt * az
        x += dt * vx
        z += dt * vz

    return time, x_vals, z_vals, vx_vals, vz_vals

def axaz(u, g, m, vx, vz):

    ax = -u/m * vx**2 * np.sign(vx)
    az = -g - u/m * vz**2 * np.sign(vz)  
    return ax, az

def simulate_runge_kutta(params):
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
    vx_vals, vz_vals = [], []

    for _ in time:
        x_vals.append(x)
        z_vals.append(z)
        vx_vals.append(vx)
        vz_vals.append(vz)

        ax1, az1 = axaz(u, g, m, vx, vz)
        vx1, vz1 = vx, vz

        # K2
        ax2, az2 = axaz(u, g, m, vx + 1/2*dt*ax1, vz + 1/2*dt*az1)
        vx2, vz2 = vx + 1/2*dt*ax1, vz + 1/2*dt*az1

        # K3
        ax3, az3 = axaz(u, g, m, vx + 1/2*dt*ax2, vz + 1/2*dt*az2)
        vx3, vz3 = vx + 1/2*dt*ax2, vz + 1/2*dt*az2

        # K4
        ax4, az4 = axaz(u, g, m, vx + dt*ax3, vz + dt*az3)
        vx4, vz4 = vx + dt*ax3, vz + dt*az3

        # === Update velocities using RK4 weighted average ===
        vx += (dt/6) * (ax1 + 2*ax2 + 2*ax3 + ax4)
        vz += (dt/6) * (az1 + 2*az2 + 2*az3 + az4)

        # === Update positions using RK4 weighted average ===
        x += (dt/6) * (vx1 + 2*vx2 + 2*vx3 + vx4)
        z += (dt/6) * (vz1 + 2*vz2 + 2*vz3 + vz4)


    return time, x_vals, z_vals, vx_vals, vz_vals

def main():
    parser = argparse.ArgumentParser(description="Compare Euler and RK4 methods for projectile simulation.")
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

    # Load parameters from file or command-line arguments
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

    # Run simulations
    t, x_e, z_e, vx_e, vz_e = simulate_euler(params)
    _, x_rk, z_rk, vx_rk, vz_rk = simulate_runge_kutta(params)

    # Print comparison table
    print("\nComparison of Final Values:")
    print(f"{'Metric':<25} {'Euler':<15} {'RK4':<15}")
    print("-" * 55)
    print(f"{'Final x position':<25} {x_e[-1]:<15.2f} {x_rk[-1]:<15.2f}")
    print(f"{'Final z position':<25} {z_e[-1]:<15.2f} {z_rk[-1]:<15.2f}")
    print(f"{'Final vx':<25} {vx_e[-1]:<15.2f} {vx_rk[-1]:<15.2f}")
    print(f"{'Final vz':<25} {vz_e[-1]:<15.2f} {vz_rk[-1]:<15.2f}")
    print(f"{'Max height (z)':<25} {max(z_e):<15.2f} {max(z_rk):<15.2f}")

    param_text = (
        f"x0={params['x0']}, z0={params['z0']}\n"
        f"vx0={params['vx0']}, vz0={params['vz0']}\n"
        f"u={params['u']}, m={params['m']}, g={params['g']}\n"
        f"dt={params['dt']}, t_final={params['t_final']}"
    )

    # Prepare output
    output_dir = "exer2_photos"
    os.makedirs(output_dir, exist_ok=True)

    # Plot trajectory 
    plt.figure()
    plt.plot(x_e, z_e, '--', label='Euler')
    plt.plot(x_rk, z_rk, '-', label='RK4')
    plt.xlabel("X Position")
    plt.ylabel("Z Position")
    plt.title("Trajectory Comparison")
    plt.legend()
    plt.grid()
    plt.text(0.72, 0.83, param_text, transform=plt.gca().transAxes,
         fontsize=8, verticalalignment='top', bbox=dict(facecolor='white', alpha=0.5))
    plt.savefig(os.path.join(output_dir, "2_3_comparison_trajectory.png"), dpi=300)
    plt.close()

    # Plot speed
    plt.figure()
    plt.plot(t, vx_e, '--', label='vx Euler', color='tab:blue')
    plt.plot(t, vx_rk, '-', label='vx RK4', color='tab:cyan')
    plt.plot(t, vz_e, '--', label='vz Euler', color='tab:red')
    plt.plot(t, vz_rk, '-', label='vz RK4', color='tab:orange')
    plt.xlabel("Time (s)")
    plt.ylabel("Velocity (m/s)")
    plt.title("Velocity Comparison (Euler vs RK4)")
    plt.legend()
    plt.grid()
    plt.text(0.48, 0.96, param_text, transform=plt.gca().transAxes,
        fontsize=8, verticalalignment='top', bbox=dict(facecolor='white', alpha=0.5))
    plt.savefig(os.path.join(output_dir, "2_3_comparison_velocity.png"), dpi=300)
    plt.close()

if __name__ == "__main__":
    main()