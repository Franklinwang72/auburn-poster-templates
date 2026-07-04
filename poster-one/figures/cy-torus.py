"""The torus: the one and only Calabi-Yau curve, in the poster palette.

Reproduces figures/cy-torus.png for poster-one.tex.
Run from the repository root:  python3 figures/cy-torus.py

Same pooled-quad + true-camera depth sort as the quintic figure (the
torus self-occludes, and matplotlib has no z-buffer); glossy ceramic
finish, one meridian and one parallel drawn in deep blue to suggest the
two flat directions.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

def rgb(h):
    return np.array([int(h[i:i+2], 16) / 255 for i in (1, 3, 5)])

BASE = rgb("#6E86A0")
DEEP = rgb("#2E4A63")
PAPER = rgb("#F7F4EE")

R, r = 1.0, 0.42
NU, NV = 160, 90
ELEV, AZIM = 34, -62

el, az = np.radians(ELEV), np.radians(AZIM)
cam = np.array([np.cos(el)*np.cos(az), np.cos(el)*np.sin(az), np.sin(el)])
L1 = np.array([0.35, 0.45, 0.9]);  L1 /= np.linalg.norm(L1)
L2 = np.array([-0.7, -0.3, 0.35]); L2 /= np.linalg.norm(L2)
H1 = L1 + cam; H1 /= np.linalg.norm(H1)

u = np.linspace(0, 2*np.pi, NU)          # around the hole
v = np.linspace(0, 2*np.pi, NV)          # around the tube
U, V = np.meshgrid(u, v)
X = (R + r*np.cos(V)) * np.cos(U)
Y = (R + r*np.cos(V)) * np.sin(U)
Z = r * np.sin(V)
P = np.stack([X, Y, Z], axis=-1)

quads, colors, depths = [], [], []
for i in range(NV - 1):
    for j in range(NU - 1):
        q = np.array([P[i, j], P[i, j+1], P[i+1, j+1], P[i+1, j]])
        n = np.cross(q[1]-q[0], q[3]-q[0]); nn = np.linalg.norm(n)
        if nn < 1e-12:
            continue
        n /= nn
        diff = 0.38 + 0.46*abs(n @ L1) + 0.20*abs(n @ L2)
        spec = 0.65 * abs(n @ H1)**30
        c = BASE*diff + (PAPER*0.5 + 0.5)*spec
        quads.append(q)
        colors.append(np.clip(np.clip(c, 0, 1)**(1/1.06), 0, 1))
        depths.append(q.mean(axis=0) @ cam)

# one meridian + one parallel, slightly lifted, only on camera-facing side
def circle_pts(kind, c0):
    tt = np.linspace(0, 2*np.pi, 240)
    if kind == "meridian":                       # around the tube, fixed u
        x = (R + (r+0.008)*np.cos(tt)) * np.cos(c0)
        y = (R + (r+0.008)*np.cos(tt)) * np.sin(c0)
        z = (r+0.008) * np.sin(tt)
        nrm = np.stack([np.cos(tt)*np.cos(c0), np.cos(tt)*np.sin(c0),
                        np.sin(tt)], axis=-1)
    else:                                        # around the hole, fixed v
        x = (R + (r+0.008)*np.cos(c0)) * np.cos(tt)
        y = (R + (r+0.008)*np.cos(c0)) * np.sin(tt)
        z = np.full_like(tt, (r+0.008) * np.sin(c0))
        nrm = np.stack([np.cos(c0)*np.cos(tt), np.cos(c0)*np.sin(tt),
                        np.full_like(tt, np.sin(c0))], axis=-1)
    pts = np.stack([x, y, z], axis=-1)
    vis = (nrm @ cam) > 0.15
    return pts, vis

order = np.argsort(depths)
quads = [quads[i] for i in order]
colors = [colors[i] for i in order]

fig = plt.figure(figsize=(9, 9))
ax = fig.add_subplot(111, projection="3d")
ax.computed_zorder = False          # draw in OUR order: surface, then lines
ax.add_collection3d(Poly3DCollection(quads, facecolors=colors,
                                     edgecolors=colors, linewidths=0.15,
                                     zorder=1))
for kind, c0 in (("meridian", np.radians(-62)), ("parallel", 0.55)):
    pts, vis = circle_pts(kind, c0)
    pts_v = pts.copy()
    pts_v[~vis] = np.nan                        # break the hidden part
    ax.plot(pts_v[:, 0], pts_v[:, 1], pts_v[:, 2], color=DEEP, lw=2.8,
            zorder=10)
m = R + r + 0.1
ax.set_xlim(-m, m); ax.set_ylim(-m, m); ax.set_zlim(-m*0.7, m*0.7)
ax.set_box_aspect((1, 1, 0.7)); ax.view_init(elev=ELEV, azim=AZIM)
ax.set_axis_off()
plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
fig.savefig("figures/cy-torus.png", dpi=300, transparent=True)

import matplotlib.image as mpimg
img = mpimg.imread("figures/cy-torus.png")
ys, xs = np.where(img[:, :, 3] > 0.01)
pad = 20
y0, y1 = max(ys.min()-pad, 0), min(ys.max()+pad, img.shape[0])
x0, x1 = max(xs.min()-pad, 0), min(xs.max()+pad, img.shape[1])
mpimg.imsave("figures/cy-torus.png", img[y0:y1, x0:x1])
print("saved figures/cy-torus.png",
      "aspect h/w = %.3f" % ((y1-y0)/(x1-x0)))
