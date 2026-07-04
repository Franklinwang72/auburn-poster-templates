"""Classic Hanson quintic cross-section, poster palette, smooth gradient.

Reproduces figures/calabi-yau-quintic.png for poster-one.tex.
Run from the repository root:  python3 figures/calabi-yau-quintic.py

This is the iconic Calabi-Yau image (as on the reference asy/luadraw
renderings): the standard Hanson parametrization of one complex slice
of the Fermat quintic,
    z1 = e^{2 pi i k1/n} cosh(w)^{2/n},  z2 = e^{2 pi i k2/n} sinh(w)^{2/n}
over w = u + i v with u in [-1,1], v in [0, pi/2] (n = 5), projected to
R^3 by (Re z2, cos a Im z1 + sin a Im z2, Re z1).

What makes it beautiful, vs a flat-shaded version:
  * SMOOTH height-gradient coloring (deep blue low -> warm sand high),
    the poster-palette answer to the reference's rainbow map;
  * two soft lights + a tight Blinn specular for a ceramic finish;
  * the canonical 3/4 view (elev 30, azim 35 ~ orthographic(3,3,2));
  * all quads pooled in ONE Poly3DCollection, depth-sorted along the
    true camera vector (matplotlib has no z-buffer);
  * u^3 sampling packs more mesh into the flaring rims (a ref trick).
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

def rgb(h):
    return np.array([int(h[i:i+2], 16) / 255 for i in (1, 3, 5)])

PAPER = rgb("#F7F4EE")
CMAP = LinearSegmentedColormap.from_list("poster", [
    rgb("#1B2E40"), rgb("#2E4A63"), rgb("#3F5E7A"), rgb("#7A8FA6"),
    rgb("#AEB9C3"), rgb("#D3CBBC"), rgb("#C7B8A1")])

N, ALPHA = 5, 0.30 * np.pi
NU = 90                         # grid per patch edge
ELEV, AZIM = 30, 35            # the canonical 3/4 view
HAX = 2                         # colour by this projected axis (height)

u = np.linspace(-1, 1, NU)
v = np.linspace(0, np.pi / 2, NU)
U, V = np.meshgrid(u, v)
W = (U ** 3) + 1j * V           # u^3: denser mesh toward the flaring rims

el, az = np.radians(ELEV), np.radians(AZIM)
cam = np.array([np.cos(el)*np.cos(az), np.cos(el)*np.sin(az), np.sin(el)])
L1 = np.array([0.3, 0.5, 0.9]);  L1 /= np.linalg.norm(L1)   # key light
L2 = np.array([-0.6, -0.2, 0.5]); L2 /= np.linalg.norm(L2)  # fill light
H1 = L1 + cam; H1 /= np.linalg.norm(H1)                     # Blinn half-vector

patches = []
for k1 in range(N):
    for k2 in range(N):
        z1 = np.exp(2j*np.pi*k1/N) * np.cosh(W) ** (2.0/N)
        z2 = np.exp(2j*np.pi*k2/N) * np.sinh(W) ** (2.0/N)
        X = z2.real
        Y = np.cos(ALPHA)*z1.imag + np.sin(ALPHA)*z2.imag
        Z = z1.real
        patches.append(np.stack([X, Y, Z], axis=-1))

allh = np.concatenate([P[..., HAX].ravel() for P in patches])
lo, hi = np.percentile(allh, 1), np.percentile(allh, 99)

quads, colors, depths = [], [], []
for P in patches:
    for i in range(P.shape[0] - 1):
        for j in range(P.shape[1] - 1):
            q = np.array([P[i, j], P[i, j+1], P[i+1, j+1], P[i+1, j]])
            n = np.cross(q[1]-q[0], q[3]-q[0]); nn = np.linalg.norm(n)
            if nn < 1e-12:
                continue
            n /= nn
            t = np.clip((q[:, HAX].mean() - lo) / (hi - lo), 0, 1)
            base = np.array(CMAP(t))[:3]
            diff = 0.34 + 0.48*abs(n @ L1) + 0.20*abs(n @ L2)
            spec = 0.55 * abs(n @ H1) ** 28
            c = base*diff + (PAPER*0.5 + 0.5)*spec
            colors.append(np.clip(np.clip(c, 0, 1) ** (1/1.06), 0, 1))
            quads.append(q); depths.append(q.mean(axis=0) @ cam)

order = np.argsort(depths)
quads = [quads[i] for i in order]
colors = [colors[i] for i in order]

fig = plt.figure(figsize=(11, 11))
ax = fig.add_subplot(111, projection="3d")
ax.add_collection3d(Poly3DCollection(quads, facecolors=colors,
                                     edgecolors=colors, linewidths=0.1))
m = 1.35
ax.set_xlim(-m, m); ax.set_ylim(-m, m); ax.set_zlim(-m, m)
ax.set_box_aspect((1, 1, 1)); ax.view_init(elev=ELEV, azim=AZIM)
ax.set_axis_off()
plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
plt.savefig("figures/calabi-yau-quintic.png", dpi=300, transparent=True)

# crop the transparent margins (they waste layout box)
import matplotlib.image as mpimg
img = mpimg.imread("figures/calabi-yau-quintic.png")
ys, xs = np.where(img[:, :, 3] > 0.01)
pad = 24
y0, y1 = max(ys.min()-pad, 0), min(ys.max()+pad, img.shape[0])
x0, x1 = max(xs.min()-pad, 0), min(xs.max()+pad, img.shape[1])
mpimg.imsave("figures/calabi-yau-quintic.png", img[y0:y1, x0:x1])
print("saved figures/calabi-yau-quintic.png",
      "aspect h/w = %.3f" % ((y1-y0)/(x1-x0)))
