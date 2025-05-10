import numpy as np
import matplotlib.pyplot as plt
import argparse
import json
import sys
import os

def axaz(u, g, m, vx, vz):

    ax = -u/m * vx**2 * np.sign(vx)
    az = -g - u/m * vz**2 * np.sign(vz)  
    return ax, az

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
    parser = argparse.ArgumentParser(description="Projectile simulation with air resistance using Runge Kutta method.")
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

    # Run simulation
    time, x_vals, z_vals, vx_vals, vz_vals = simulate(params)

    print(f"Final X position: {x_vals[-1]:.2f} m")
    print(f"Final Z position: {z_vals[-1]:.2f} m")
    print(f"Final horizontal velocity (vx): {vx_vals[-1]:.2f} m/s")
    print(f"Final vertical velocity (vz): {vz_vals[-1]:.2f} m/s")
    print(f"Maximum height reached: {max(z_vals):.2f} m")

    param_text = (
        f"x0={params['x0']}, z0={params['z0']}\n"
        f"vx0={params['vx0']}, vz0={params['vz0']}\n"
        f"u={params['u']}, m={params['m']}, g={params['g']}\n"
        f"dt={params['dt']}, t_final={params['t_final']}"
    )

    # Directory to save plots
    output_dir = "exer2_photos"
    os.makedirs(output_dir, exist_ok=True)

    # Plot positions
    plt.figure()
    # plt.subplot(1,2,1)
    plt.plot(x_vals, z_vals)
    plt.xlabel("X Position")
    plt.ylabel("Z Position")
    plt.title("Trajectory")
    plt.grid()
    plt.text(0.72, 0.95, param_text, transform=plt.gca().transAxes,
         fontsize=8, verticalalignment='top', bbox=dict(facecolor='white', alpha=0.5))
    trajectory_file = os.path.join(output_dir, "2_2_trajectory.png")
    plt.savefig(trajectory_file, dpi=300)
    plt.close() 

    # Plot speeds
    # plt.subplot(1,2,2)
    plt.figure()
    plt.plot(time, vx_vals, label='vx')
    plt.plot(time, vz_vals, label='vz')
    plt.xlabel("Time")
    plt.ylabel("Speed")
    plt.title("Velocity evolution")
    plt.legend()
    plt.grid()
    plt.text(0.55, 0.97, param_text, transform=plt.gca().transAxes,
        fontsize=8, verticalalignment='top', bbox=dict(facecolor='white', alpha=0.5))
    velocity_file = os.path.join(output_dir, "2_2_velocity.png")
    plt.savefig(velocity_file, dpi=300)
    plt.close() 

    plt.tight_layout()

    plt.show()

if __name__ == "__main__":
    main()