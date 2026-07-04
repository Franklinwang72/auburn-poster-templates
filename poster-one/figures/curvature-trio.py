"""Curvature trio: sphere / flat sheet / saddle, each with a triangle.

Reproduces figures/curvature-trio.png for poster-one.tex.
Run from the repository root:  python3 figures/curvature-trio.py

The lay-reader's entrance to curvature: on a sphere a triangle's angles
add to more than 180 degrees, on a flat sheet exactly 180, on a saddle
less. Poster palette, transparent background.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def rgb(h):
    return np.array([int(h[i:i+2], 16) / 255 for i in (1, 3, 5)])

INK = rgb("#1E1E1E")
PAPER = rgb("#F7F4EE")

def cased(ax, x, y, z):
    """A dark triangle edge with a light casing, so it reads on ANY
    surface colour (the black line vanished on the dark sphere)."""
    ax.plot(x, y, z, color=PAPER, lw=8, zorder=9,
            solid_capstyle="round", solid_joinstyle="round")
    ax.plot(x, y, z, color=INK, lw=3.4, zorder=10,
            solid_capstyle="round", solid_joinstyle="round")

def shade(base, X, Y, Z, elev, azim):
    """Two-light Lambert facecolors: key light + camera-side fill."""
    el, az = np.radians(elev), np.radians(azim)
    cam = np.array([np.cos(el)*np.cos(az), np.cos(el)*np.sin(az), np.sin(el)])
    L1 = np.array([0.4, 0.3, 0.85]); L1 /= np.linalg.norm(L1)
    L2 = cam + np.array([0.1, 0.1, 0.4]); L2 /= np.linalg.norm(L2)
    dx1 = np.stack([np.gradient(A, axis=0) for A in (X, Y, Z)], axis=-1)
    dx2 = np.stack([np.gradient(A, axis=1) for A in (X, Y, Z)], axis=-1)
    n = np.cross(dx1, dx2)
    n /= np.maximum(np.linalg.norm(n, axis=-1, keepdims=True), 1e-12)
    lam = 0.55 * np.abs(n @ L1) + 0.45 * np.abs(n @ L2)
    s = (0.48 + 0.52 * lam)[..., None]
    return np.clip(base * s + PAPER * 0.10 * (1 - s), 0, 1)

def slerp(a, b, t):
    a, b = np.asarray(a, float), np.asarray(b, float)
    th = np.arccos(np.clip(a @ b, -1, 1))
    return (np.sin((1 - t) * th)[:, None] * a + np.sin(t * th)[:, None] * b) \
        / np.sin(th)

fig = plt.figure(figsize=(13.2, 4.6))

# ---- sphere: angles add to MORE than 180 ------------------------------
ax = fig.add_subplot(131, projection="3d")
ax.computed_zorder = False          # draw in OUR order: surface, then lines
u, v = np.meshgrid(np.linspace(0, 2*np.pi, 80), np.linspace(0, np.pi, 60))
X, Y, Z = np.cos(u)*np.sin(v), np.sin(u)*np.sin(v), np.cos(v)
ax.plot_surface(X, Y, Z, facecolors=shade(rgb("#7E93AA"), X, Y, Z, 18, -50),
                rstride=1, cstride=1, linewidth=0, antialiased=True, zorder=1)
t = np.linspace(0, 1, 60)
A, B, C = np.array([0, 0, 1.0]), np.array([1.0, 0, 0]), np.array([0, -1.0, 0])
for P, Q in ((A, B), (B, C), (C, A)):
    arc = slerp(P, Q, t) * 1.015
    cased(ax, arc[:, 0], arc[:, 1], arc[:, 2])
ax.set_xlim(-1.05, 1.05); ax.set_ylim(-1.05, 1.05); ax.set_zlim(-1.05, 1.05)
ax.set_box_aspect((1, 1, 1)); ax.view_init(elev=18, azim=-50)

# ---- flat sheet: exactly 180 ------------------------------------------
ax = fig.add_subplot(132, projection="3d")
ax.computed_zorder = False
g = np.linspace(-1, 1, 24)
X, Y = np.meshgrid(g, g); Z = 0*X
ax.plot_surface(X, Y, Z, facecolors=shade(rgb("#A9B6C2"), X, Y, Z, 32, -60),
                rstride=1, cstride=1, linewidth=0, antialiased=True, zorder=1)
tri = np.array([[-0.62, -0.5], [0.72, -0.38], [0.0, 0.66], [-0.62, -0.5]])
cased(ax, tri[:, 0], tri[:, 1], tri[:, 0]*0 + 0.012)
ax.set_xlim(-1.05, 1.05); ax.set_ylim(-1.05, 1.05); ax.set_zlim(-0.7, 0.7)
ax.set_box_aspect((1, 1, 0.55)); ax.view_init(elev=32, azim=-60)

# ---- saddle: LESS than 180 --------------------------------------------
ax = fig.add_subplot(133, projection="3d")
ax.computed_zorder = False
g = np.linspace(-1, 1, 60)
X, Y = np.meshgrid(g, g); Z = 0.55 * (X**2 - Y**2)
ax.plot_surface(X, Y, Z, facecolors=shade(rgb("#C7B8A1"), X, Y, Z, 24, -55),
                rstride=1, cstride=1, linewidth=0, antialiased=True, zorder=1)
pts = np.array([[-0.62, -0.45], [0.7, -0.5], [0.05, 0.62]])
t = np.linspace(0, 1, 60)
for i in range(3):
    P, Q = pts[i], pts[(i + 1) % 3]
    xy = (1 - t)[:, None] * P + t[:, None] * Q
    z = 0.55 * (xy[:, 0]**2 - xy[:, 1]**2) + 0.02
    cased(ax, xy[:, 0], xy[:, 1], z)
ax.set_xlim(-1.05, 1.05); ax.set_ylim(-1.05, 1.05); ax.set_zlim(-0.85, 0.85)
ax.set_box_aspect((1, 1, 0.6)); ax.view_init(elev=24, azim=-55)

for ax in fig.axes:
    ax.set_axis_off()
plt.subplots_adjust(left=0, right=1, top=1, bottom=0, wspace=0)
fig.savefig("figures/curvature-trio.png", dpi=300, transparent=True)

# crop transparent margins
import matplotlib.image as mpimg
img = mpimg.imread("figures/curvature-trio.png")
ys, xs = np.where(img[:, :, 3] > 0.01)
pad = 20
y0, y1 = max(ys.min()-pad, 0), min(ys.max()+pad, img.shape[0])
x0, x1 = max(xs.min()-pad, 0), min(xs.max()+pad, img.shape[1])
mpimg.imsave("figures/curvature-trio.png", img[y0:y1, x0:x1])
print("saved figures/curvature-trio.png",
      "aspect h/w = %.3f" % ((y1-y0)/(x1-x0)))
