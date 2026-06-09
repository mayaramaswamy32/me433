import numpy as np
import matplotlib.pyplot as plt

thetas = np.linspace(-90, 90, 1000) # angles

K_wall = 0.5
theta_wall = 45


F_wall = np.zeros_like(thetas)

# left wall: pushes you RIGHT (positive force) when you go too far left
F_wall[thetas < -theta_wall] = -np.clip(K_wall * (-thetas[thetas < -theta_wall] - theta_wall) / 10, 0, 1)

# right wall: pushes you LEFT (negative force) when you go too far right  
F_wall[thetas > theta_wall] = -np.clip(-K_wall * (thetas[thetas > theta_wall] - theta_wall) / 10, -1, 0)

clicks = 4
K_d = 1.0
F_click = -np.clip(-K_d * np.sin(clicks * np.radians(thetas)), -1, 1)

# I normalized clicks by capping from +1 to -1
theta_c = 0
width = 20
F_bump = np.zeros_like(thetas)
mask = np.abs(thetas - theta_c) < width
F_bump[mask] = -np.sin(np.pi * (thetas[mask] - theta_c) / width)

F_full = np.clip(F_wall + F_click, -1, 1)

fig, axes = plt.subplots(2, 2, figsize=(12, 8), sharex=True)
fig.suptitle("Haptic Paddle: Force vs. Displacement", fontsize=14)

# Equations for each plot
equations = [
    "F = −K·(θ−θ_wall), clamped to [−1,0] or [0,1]",
    "F = −K_d·sin(n·θ), where I made n = 4",
    "F = −sin(π·(θ−θ_c)/width)  for |θ−θ_c| < width",
    "F = (F_wall + F_click, −1, 1)",
]

plots = [
    (axes[0,0], F_wall,   "Virtual Walls",  "C0"),
    (axes[0,1], F_click, "Clicks (n=4)",  "C2"),
    (axes[1,0], F_bump,   "Bump / Dip",     "C3"),
    (axes[1,1], F_full,   "Full Toggle System",    "C4"),
]

for (ax, F, title, color), eq in zip(plots, equations):
    ax.plot(thetas, F, color=color, linewidth=2)
    ax.axhline(0, color='gray', linewidth=0.8, linestyle='--')
    ax.axvline(0, color='gray', linewidth=0.5, linestyle=':')
    if title == "Virtual Walls":
        ax.axvline(-theta_wall, color='steelblue', linewidth=1, linestyle='--', alpha=0.6)
        ax.axvline( theta_wall, color='steelblue', linewidth=1, linestyle='--', alpha=0.6)
        ax.text(-theta_wall, -1.15, 'wall 1', ha='center', fontsize=8, color='steelblue')
        ax.text( theta_wall, -1.15, 'wall 2', ha='center', fontsize=8, color='steelblue')
    ax.set_title(title, fontsize=11, fontweight='bold')
    ax.set_ylabel("F_desired (normalized)")
    ax.set_ylim(-1.3, 1.3)
    ax.set_xlim(-90, 90)
    ax.fill_between(thetas, F, 0, alpha=0.15, color=color)
    ax.grid(True, alpha=0.3)
    # equation box in corner to show eqns I used
    ax.text(0.02, 0.97, eq, transform=ax.transAxes,
            fontsize=7.5, verticalalignment='top',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                      edgecolor='lightgray', alpha=0.8),
            fontfamily='monospace')

for ax in axes[1]:
    ax.set_xlabel("θ (degrees)")

plt.tight_layout()
plt.savefig("haptic_force_curves.png", dpi=150)
plt.show()