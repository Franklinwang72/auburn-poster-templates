"""All three Calabi-Yau figures in the Auburn navy/orange palette.

Reproduces figures/calabi-yau-quintic.png, figures/curvature-trio.png,
and figures/cy-torus.png for the navy-and-orange posters.
Run from the folder root:  python3 figures/make-figures.py

Same geometry as the paper-white "One" poster set; only the palette
differs: Auburn navy #0B2341, one orange accent #E86100, white ground.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.colors import LinearSegmentedColormap
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

def rgb(h):
    return np.array([int(h[i:i+2], 16) / 255 for i in (1, 3, 5)])

WHITE = np.array([1.0, 1.0, 1.0])
NAVY = rgb("#0B2341")
ORANGE = rgb("#E86100")

def crop(path, pad=24):
    img = mpimg.imread(path)
    ys, xs = np.where(img[:, :, 3] > 0.01)
    y0, y1 = max(ys.min()-pad, 0), min(ys.max()+pad, img.shape[0])
    x0, x1 = max(xs.min()-pad, 0), min(xs.max()+pad, img.shape[1])
    mpimg.imsave(path, img[y0:y1, x0:x1])
    print("saved", path, "aspect h/w = %.3f" % ((y1-y0)/(x1-x0)))

# ======================================================================
# 1. Hero: Hanson quintic slice, height gradient navy -> cream -> orange
# ======================================================================
CMAP = LinearSegmentedColormap.from_list("au", [
    rgb("#081D38"), rgb("#0B2341"), rgb("#31517A"), rgb("#7E94AD"),
    rgb("#CBD4DD"), rgb("#F0E2CE"), rgb("#E88A3C")])

N, ALPHA, NU = 5, 0.30*np.pi, 90
ELEV, AZIM, HAX = 30, 35, 2

u = np.linspace(-1, 1, NU)
v = np.linspace(0, np.pi/2, NU)
U, V = np.meshgrid(u, v)
W = (U**3) + 1j*V

el, az = np.radians(ELEV), np.radians(AZIM)
cam = np.array([np.cos(el)*np.cos(az), np.cos(el)*np.sin(az), np.sin(el)])
L1 = np.array([0.3, 0.5, 0.9]);  L1 /= np.linalg.norm(L1)
L2 = np.array([-0.6, -0.2, 0.5]); L2 /= np.linalg.norm(L2)
H1 = L1 + cam; H1 /= np.linalg.norm(H1)

patches = []
for k1 in range(N):
    for k2 in range(N):
        z1 = np.exp(2j*np.pi*k1/N) * np.cosh(W)**(2.0/N)
        z2 = np.exp(2j*np.pi*k2/N) * np.sinh(W)**(2.0/N)
        patches.append(np.stack([z2.real,
                                 np.cos(ALPHA)*z1.imag + np.sin(ALPHA)*z2.imag,
                                 z1.real], axis=-1))
allh = np.concatenate([P[..., HAX].ravel() for P in patches])
lo, hi = np.percentile(allh, 1), np.percentile(allh, 99)

quads, colors, depths = [], [], []
for P in patches:
    for i in range(P.shape[0]-1):
        for j in range(P.shape[1]-1):
            q = np.array([P[i, j], P[i, j+1], P[i+1, j+1], P[i+1, j]])
            n = np.cross(q[1]-q[0], q[3]-q[0]); nn = np.linalg.norm(n)
            if nn < 1e-12:
                continue
            n /= nn
            t = np.clip((q[:, HAX].mean()-lo)/(hi-lo), 0, 1)
            base = np.array(CMAP(t))[:3]
            diff = 0.34 + 0.48*abs(n@L1) + 0.20*abs(n@L2)
            spec = 0.55*abs(n@H1)**28
            c = base*diff + (WHITE*0.5 + 0.5)*spec
            colors.append(np.clip(np.clip(c, 0, 1)**(1/1.06), 0, 1))
            quads.append(q); depths.append(q.mean(axis=0)@cam)

order = np.argsort(depths)
fig = plt.figure(figsize=(11, 11))
ax = fig.add_subplot(111, projection="3d")
ax.add_collection3d(Poly3DCollection([quads[i] for i in order],
                                     facecolors=[colors[i] for i in order],
                                     edgecolors=[colors[i] for i in order],
                                     linewidths=0.1))
m = 1.35
ax.set_xlim(-m, m); ax.set_ylim(-m, m); ax.set_zlim(-m, m)
ax.set_box_aspect((1, 1, 1)); ax.view_init(elev=ELEV, azim=AZIM)
ax.set_axis_off()
plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
plt.savefig("figures/calabi-yau-quintic.png", dpi=300, transparent=True)
plt.close(fig)
crop("figures/calabi-yau-quintic.png")

# ======================================================================
# 2. Curvature trio: sphere / flat sheet / saddle with cased triangles
# ======================================================================
def shade(base, X, Y, Z, elev, azim):
    el, az = np.radians(elev), np.radians(azim)
    c = np.array([np.cos(el)*np.cos(az), np.cos(el)*np.sin(az), np.sin(el)])
    La = np.array([0.4, 0.3, 0.85]); La /= np.linalg.norm(La)
    Lb = c + np.array([0.1, 0.1, 0.4]); Lb /= np.linalg.norm(Lb)
    d1 = np.stack([np.gradient(A, axis=0) for A in (X, Y, Z)], axis=-1)
    d2 = np.stack([np.gradient(A, axis=1) for A in (X, Y, Z)], axis=-1)
    n = np.cross(d1, d2)
    n /= np.maximum(np.linalg.norm(n, axis=-1, keepdims=True), 1e-12)
    lam = 0.55*np.abs(n @ La) + 0.45*np.abs(n @ Lb)
    s = (0.48 + 0.52*lam)[..., None]
    return np.clip(base*s + WHITE*0.10*(1-s), 0, 1)

def cased(ax, x, y, z):
    ax.plot(x, y, z, color=WHITE, lw=8, zorder=9,
            solid_capstyle="round", solid_joinstyle="round")
    ax.plot(x, y, z, color=NAVY, lw=3.4, zorder=10,
            solid_capstyle="round", solid_joinstyle="round")

def slerp(a, b, t):
    a, b = np.asarray(a, float), np.asarray(b, float)
    th = np.arccos(np.clip(a @ b, -1, 1))
    return (np.sin((1-t)*th)[:, None]*a + np.sin(t*th)[:, None]*b)/np.sin(th)

fig = plt.figure(figsize=(13.2, 4.6))

ax = fig.add_subplot(131, projection="3d")
ax.computed_zorder = False
uu, vv = np.meshgrid(np.linspace(0, 2*np.pi, 80), np.linspace(0, np.pi, 60))
X, Y, Z = np.cos(uu)*np.sin(vv), np.sin(uu)*np.sin(vv), np.cos(vv)
ax.plot_surface(X, Y, Z, facecolors=shade(rgb("#54749B"), X, Y, Z, 18, -50),
                rstride=1, cstride=1, linewidth=0, antialiased=True, zorder=1)
t = np.linspace(0, 1, 60)
A, B, C = np.array([0, 0, 1.0]), np.array([1.0, 0, 0]), np.array([0, -1.0, 0])
for P, Q in ((A, B), (B, C), (C, A)):
    arc = slerp(P, Q, t)*1.015
    cased(ax, arc[:, 0], arc[:, 1], arc[:, 2])
ax.set_xlim(-1.05, 1.05); ax.set_ylim(-1.05, 1.05); ax.set_zlim(-1.05, 1.05)
ax.set_box_aspect((1, 1, 1)); ax.view_init(elev=18, azim=-50)

ax = fig.add_subplot(132, projection="3d")
ax.computed_zorder = False
g = np.linspace(-1, 1, 24)
X, Y = np.meshgrid(g, g); Z = 0*X
ax.plot_surface(X, Y, Z, facecolors=shade(rgb("#AFB8C2"), X, Y, Z, 32, -60),
                rstride=1, cstride=1, linewidth=0, antialiased=True, zorder=1)
tri = np.array([[-0.62, -0.5], [0.72, -0.38], [0.0, 0.66], [-0.62, -0.5]])
cased(ax, tri[:, 0], tri[:, 1], tri[:, 0]*0 + 0.012)
ax.set_xlim(-1.05, 1.05); ax.set_ylim(-1.05, 1.05); ax.set_zlim(-0.7, 0.7)
ax.set_box_aspect((1, 1, 0.55)); ax.view_init(elev=32, azim=-60)

ax = fig.add_subplot(133, projection="3d")
ax.computed_zorder = False
g = np.linspace(-1, 1, 60)
X, Y = np.meshgrid(g, g); Z = 0.55*(X**2 - Y**2)
ax.plot_surface(X, Y, Z, facecolors=shade(rgb("#E39A5F"), X, Y, Z, 24, -55),
                rstride=1, cstride=1, linewidth=0, antialiased=True, zorder=1)
pts = np.array([[-0.62, -0.45], [0.7, -0.5], [0.05, 0.62]])
for i in range(3):
    P, Q = pts[i], pts[(i+1) % 3]
    xy = (1-t)[:, None]*P + t[:, None]*Q
    z = 0.55*(xy[:, 0]**2 - xy[:, 1]**2) + 0.02
    cased(ax, xy[:, 0], xy[:, 1], z)
ax.set_xlim(-1.05, 1.05); ax.set_ylim(-1.05, 1.05); ax.set_zlim(-0.85, 0.85)
ax.set_box_aspect((1, 1, 0.6)); ax.view_init(elev=24, azim=-55)

for a in fig.axes:
    a.set_axis_off()
plt.subplots_adjust(left=0, right=1, top=1, bottom=0, wspace=0)
fig.savefig("figures/curvature-trio.png", dpi=300, transparent=True)
plt.close(fig)
crop("figures/curvature-trio.png", pad=20)

# ======================================================================
# 3. Torus: glossy slate blue, meridian + parallel in navy
# ======================================================================
BASE = rgb("#54749B")
R, r = 1.0, 0.42
NUt, NVt = 160, 90
ELEVt, AZIMt = 34, -62
el, az = np.radians(ELEVt), np.radians(AZIMt)
cam = np.array([np.cos(el)*np.cos(az), np.cos(el)*np.sin(az), np.sin(el)])
H1 = L1 + cam; H1 /= np.linalg.norm(H1)

ut = np.linspace(0, 2*np.pi, NUt)
vt = np.linspace(0, 2*np.pi, NVt)
Ut, Vt = np.meshgrid(ut, vt)
P = np.stack([(R + r*np.cos(Vt))*np.cos(Ut),
              (R + r*np.cos(Vt))*np.sin(Ut),
              r*np.sin(Vt)], axis=-1)

quads, colors, depths = [], [], []
for i in range(NVt-1):
    for j in range(NUt-1):
        q = np.array([P[i, j], P[i, j+1], P[i+1, j+1], P[i+1, j]])
        n = np.cross(q[1]-q[0], q[3]-q[0]); nn = np.linalg.norm(n)
        if nn < 1e-12:
            continue
        n /= nn
        diff = 0.38 + 0.46*abs(n@L1) + 0.20*abs(n@L2)
        spec = 0.65*abs(n@H1)**30
        c = BASE*diff + (WHITE*0.5 + 0.5)*spec
        quads.append(q)
        colors.append(np.clip(np.clip(c, 0, 1)**(1/1.06), 0, 1))
        depths.append(q.mean(axis=0)@cam)

def circle_pts(kind, c0):
    tt = np.linspace(0, 2*np.pi, 240)
    if kind == "meridian":
        x = (R + (r+0.008)*np.cos(tt))*np.cos(c0)
        y = (R + (r+0.008)*np.cos(tt))*np.sin(c0)
        z = (r+0.008)*np.sin(tt)
        nrm = np.stack([np.cos(tt)*np.cos(c0), np.cos(tt)*np.sin(c0),
                        np.sin(tt)], axis=-1)
    else:
        x = (R + (r+0.008)*np.cos(c0))*np.cos(tt)
        y = (R + (r+0.008)*np.cos(c0))*np.sin(tt)
        z = np.full_like(tt, (r+0.008)*np.sin(c0))
        nrm = np.stack([np.cos(c0)*np.cos(tt), np.cos(c0)*np.sin(tt),
                        np.full_like(tt, np.sin(c0))], axis=-1)
    return np.stack([x, y, z], axis=-1), (nrm @ cam) > 0.15

order = np.argsort(depths)
fig = plt.figure(figsize=(9, 9))
ax = fig.add_subplot(111, projection="3d")
ax.computed_zorder = False
ax.add_collection3d(Poly3DCollection([quads[i] for i in order],
                                     facecolors=[colors[i] for i in order],
                                     edgecolors=[colors[i] for i in order],
                                     linewidths=0.15, zorder=1))
for kind, c0 in (("meridian", np.radians(-62)), ("parallel", 0.55)):
    pts, vis = circle_pts(kind, c0)
    ptsv = pts.copy(); ptsv[~vis] = np.nan
    ax.plot(ptsv[:, 0], ptsv[:, 1], ptsv[:, 2], color=NAVY, lw=2.8, zorder=10)
m = R + r + 0.1
ax.set_xlim(-m, m); ax.set_ylim(-m, m); ax.set_zlim(-m*0.7, m*0.7)
ax.set_box_aspect((1, 1, 0.7)); ax.view_init(elev=ELEVt, azim=AZIMt)
ax.set_axis_off()
plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
fig.savefig("figures/cy-torus.png", dpi=300, transparent=True)
plt.close(fig)
crop("figures/cy-torus.png", pad=20)
