# ===== setup and blob function =====
import random, math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import hsv_to_rgb
import streamlit as st
import pandas as pd
import os

# ------- Shape generator -------
def shape(center=(0.5,0.5), r=0.1, points=500, wobble=0.15, kind="blob", sides=5, petals=6):
    t = np.linspace(0, 2*np.pi, points)

    if kind == "blob":
        radii = r * (1 + wobble*(np.random.rand(points)-0.5))
        x = center[0] + radii * np.cos(t)
        y = center[1] + radii * np.sin(t)

    elif kind == "polygon":
        angles = np.linspace(0, 2*np.pi, sides, endpoint=False)
        x = center[0] + r * np.cos(angles)
        y = center[1] + r * np.sin(angles)

    elif kind == "heart":
        x = center[0] + r * 16*np.sin(t)**3 / 16
        y = center[1] + r * (13*np.cos(t) - 5*np.cos(2*t)
                             - 2*np.cos(3*t) - np.cos(4*t)) / 16

    elif kind == "star":
        n = 5
        angles = np.linspace(0, 2*np.pi, 2*n+1)
        radii = np.array([r, r/2]*n + [r])
        x = center[0] + radii * np.cos(angles)
        y = center[0] + radii * np.sin(angles)

    elif kind == "flower":
        radii = r * (1 + 0.3 * np.sin(petals * t))
        x = center[0] + radii * np.cos(t)
        y = center[1] + radii * np.sin(t)

    else:
        radii = r * (1 + wobble*(np.random.rand(points)-0.5))
        x = center[0] + radii * np.cos(t)
        y = center[1] + radii * np.sin(t)

    return x, y

# ------- 3D shading -------
def apply_shading(x, y, cx, cy, light_dir=(1,1)):
    L = np.array(light_dir)/np.linalg.norm(light_dir)
    pts = np.vstack([x-cx, y-cy]).T
    norm = np.sqrt((pts**2).sum(axis=1))
    pts_n = pts / norm[:,None]
    shade = (pts_n @ L + 1)/2
    return shade

# ------- Palette CSV CRUD -------
PALETTE_FILE = "palette.csv"
if not os.path.exists(PALETTE_FILE):
    df_init = pd.DataFrame([
        {"name":"sky", "r":0.4, "g":0.7, "b":1.0},
        {"name":"sun", "r":1.0, "g":0.8, "b":0.2},
        {"name":"forest", "r":0.2, "g":0.6, "b":0.3}
    ])
    df_init.to_csv(PALETTE_FILE, index=False)

def read_palette():
    return pd.read_csv(PALETTE_FILE)

def load_csv_palette():
    df = read_palette()
    return [(row.r, row.g, row.b) for row in df.itertuples()]

# ------- Palette Generator -------
def make_palette(k=20, mode="pastel", base_h=0.60):
    cols = []
    if mode == "csv":
        return load_csv_palette()

    for _ in range(k):
        if mode == "pastel":
            h = random.random(); s = random.uniform(0.15,0.35); v = random.uniform(0.9,1.0)
        elif mode == "vivid":
            h = random.random(); s = random.uniform(0.8,1.0); v = random.uniform(0.8,1.0)
        elif mode == "mono":
            h = base_h; s = random.uniform(0.1,0.6); v = random.uniform(0.5,1.0)
        elif mode == "neon":
            h = random.random(); s = random.uniform(0.85,1.0); v = random.uniform(0.92,1.0)
        elif mode == "earth":
            h = random.uniform(0.05,0.12); s = random.uniform(0.3,0.6); v = random.uniform(0.3,0.7)
        elif mode == "ocean":
            h = random.uniform(0.45,0.6); s = random.uniform(0.4,0.8); v = random.uniform(0.5,1.0)
        elif mode == "sunset":
            h = random.uniform(0.05,0.15); s = random.uniform(0.6,1.0); v = random.uniform(0.7,1.0)
        elif mode == "analogous":
            h = random.uniform(base_h-0.1, base_h+0.1); s = random.uniform(0.45,1.0); v = random.uniform(0.6,1.0)
        elif mode == "triadic":
            h = random.random(); s = random.uniform(0.5,1.0); v = random.uniform(0.6,1.0)
        else:
            h = random.random(); s = random.uniform(0.3,1.0); v = random.uniform(0.5,1.0)
        cols.append(tuple(hsv_to_rgb([h,s,v])))
    return cols

# ------- Poster Drawer -------
def draw_poster(palette_mode, blob_shape, n_layers, wobble, points,
                sides, petals, radius_min, radius_max, alpha_min, alpha_max,
                seed, base_h):
    random.seed(seed); np.random.seed(seed)
    fig, ax = plt.subplots(figsize=(7,10))
    ax.axis("off")
    ax.set_facecolor((0.97,0.97,0.97))

    palette = make_palette(15, palette_mode, base_h)

    for _ in range(n_layers):
        cx, cy = random.random(), random.random()
        rr = random.uniform(radius_min, radius_max)
        x, y = shape((cx,cy), r=rr, wobble=wobble, points=points, kind=blob_shape, sides=sides, petals=petals)

        color = random.choice(palette)
        alpha = random.uniform(alpha_min, alpha_max)
        ax.fill(x, y, color=color, alpha=alpha, edgecolor=(0,0,0,0))

        # drop shadow
        xs = x + 0.01; ys = y - 0.01
        ax.fill(xs, ys, color=(0,0,0), alpha=alpha*0.4)

        shade = apply_shading(x, y, cx, cy, (1,1))
        base_color = np.array(color)
        spec = shade**12
        _ = [tuple(base_color*0.6 + s*0.4 + spec[j]*0.2) for j,s in enumerate(shade)]

    ax.text(0.05, 0.95, "Final Poster • Interactiv • 3D • CSV",
            transform=ax.transAxes, fontsize=18, weight="bold")
    ax.text(0.05, 0.91, "Week 9 • Art & Big Data",
            transform=ax.transAxes, fontsize=12)
    ax.text(0.05, 0.88, f"{palette_mode} • {blob_shape} • {n_layers} layers • seed : {seed}",
            transform=ax.transAxes, fontsize=12)
                    
    return fig


# ================= STREAMLIT UI ======================

st.title("Generative 3D Abstract Poster (CSV + Shapes)")

palette_mode = st.sidebar.selectbox("Palette Mode",
    ["pastel","vivid","mono","neon","ocean","sunset","analogous","triadic","csv","random"])

blob_shape = st.sidebar.selectbox("Shape",
    ["blob","polygon","heart","star","flower"])

n_layers = st.sidebar.slider("Layers", 3, 20, 8)
wobble = st.sidebar.slider("Wobble", 0.01, 9.0, 0.15)
points = st.sidebar.slider("Points", 100, 1000, 200, 100)
sides = st.sidebar.slider("Polygon Sides", 3, 10, 5, 1)
petals = st.sidebar.slider("Flower Petals", 2, 20, 7, 1) 
radius_min = st.sidebar.slider("Minimum Radius", 0.01, 0.2, 0.01)
radius_max = st.sidebar.slider("Maximum Radius", 0.05, 0.3, 0.25)
alpha_min = st.sidebar.slider("Alpha Min", 0.05, 0.5, 0.1)
alpha_max = st.sidebar.slider("Alpha Max", 0.5, 1.0, 0.9)
seed = st.sidebar.slider("Seed", 0, 9999, 0)
base_h = st.sidebar.slider("Base Hue", 0.0, 1.0, 0.6)


fig = draw_poster(palette_mode, blob_shape, n_layers, wobble, points,
                sides, petals, radius_min, radius_max, alpha_min, alpha_max,
                seed, base_h)
st.pyplot(fig)
