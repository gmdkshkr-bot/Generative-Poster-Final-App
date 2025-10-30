# app.py — Upgraded Generative 3D Abstract Poster (Streamlit)
import io
import os
import random
import math
from typing import List, Tuple

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # for Streamlit deployment
import matplotlib.pyplot as plt
from matplotlib.colors import hsv_to_rgb
import streamlit as st

# ---------------- Constants ----------------
PALETTE_FILE = "palette.csv"
DEFAULT_PALETTE = [
    {"name": "sky", "r": 0.4, "g": 0.7, "b": 1.0},
    {"name": "sun", "r": 1.0, "g": 0.8, "b": 0.2},
    {"name": "forest", "r": 0.2, "g": 0.6, "b": 0.3},
]

# ---------------- Utilities ----------------
def ensure_palette_file():
    if not os.path.exists(PALETTE_FILE):
        pd.DataFrame(DEFAULT_PALETTE).to_csv(PALETTE_FILE, index=False)

def read_palette() -> pd.DataFrame:
    ensure_palette_file()
    return pd.read_csv(PALETTE_FILE)

def load_csv_palette() -> List[Tuple[float,float,float]]:
    df = read_palette()
    # ensure columns exist and return list of tuples
    if not {"r","g","b"}.issubset(set(df.columns)):
        raise ValueError("CSV palette must have columns r,g,b (0-1 floats).")
    return [ (float(r), float(g), float(b)) for r,g,b in zip(df["r"], df["g"], df["b"]) ]

# ---------------- Shape generator ----------------
def shape(center=(0.5,0.5), r=0.1, points=500, wobble=0.15,
          kind="blob", sides=5, petals=6, seed=None):
    """Return closed polygon (x, y) for given shape kind."""
    if seed is not None:
        rng = np.random.default_rng(seed)
    else:
        rng = np.random.default_rng()

    t = np.linspace(0, 2*np.pi, points, endpoint=False)

    cx, cy = center
    if kind == "blob":
        # smooth random radius variation
        radii = r * (1 + wobble*(rng.random(points) - 0.5))
        x = cx + radii * np.cos(t)
        y = cy + radii * np.sin(t)

    elif kind == "polygon":
        angles = np.linspace(0, 2*np.pi, sides, endpoint=False)
        x = cx + r * np.cos(angles)
        y = cy + r * np.sin(angles)
        # close polygon
        x = np.append(x, x[0])
        y = np.append(y, y[0])

    elif kind == "heart":
        # parametric heart, scaled by r
        # base parametric heart uses values roughly in [-1..1]; scale by r
        xt = 16 * np.sin(t)**3
        yt = 13*np.cos(t) - 5*np.cos(2*t) - 2*np.cos(3*t) - np.cos(4*t)
        # normalize to roughly unit size then scale by r
        xt = xt / 17.0
        yt = yt / 17.0
        x = cx + r * xt
        y = cy + r * yt

    elif kind == "star":
        n = max(3, int(sides))  # use sides as number of star arms
        angles = np.linspace(0, 2*np.pi, 2*n, endpoint=False)
        # alternate outer and inner radii
        radii = np.tile([r, r*0.45], n)
        x = cx + radii * np.cos(angles)
        y = cy + radii * np.sin(angles)
        x = np.append(x, x[0])
        y = np.append(y, y[0])

    elif kind == "flower":
        radii = r * (1 + 0.3 * np.sin(petals * t))
        x = cx + radii * np.cos(t)
        y = cy + radii * np.sin(t)
        x = np.append(x, x[0])
        y = np.append(y, y[0])

    else:
        radii = r * (1 + wobble*(rng.random(points)-0.5))
        x = cx + radii * np.cos(t)
        y = cy + radii * np.sin(t)

    return x, y

# ---------------- Shading ----------------
def apply_shading(x: np.ndarray, y: np.ndarray, cx: float, cy: float, light_dir=(1,1)):
    """
    Compute per-vertex shading scalar in [0,1].
    Uses normalized radial vectors from center and dot with light direction.
    """
    L = np.array(light_dir, dtype=float)
    if np.linalg.norm(L) == 0:
        L = np.array([1.0, 1.0])
    L = L / np.linalg.norm(L)

    pts = np.vstack([x - cx, y - cy]).T
    norms = np.linalg.norm(pts, axis=1)
    # avoid division by zero: where norm==0, set to small positive
    norms_safe = np.where(norms == 0, 1e-6, norms)
    pts_n = pts / norms_safe[:, None]
    shade = (pts_n @ L + 1.0) / 2.0  # map [-1,1] -> [0,1]
    # clamp
    shade = np.clip(shade, 0.0, 1.0)
    return shade

# ---------------- Palette generator ----------------
def make_palette(k=15, mode="pastel", base_h=0.6, rng_seed=None):
    rng = random.Random(rng_seed)
    cols = []
    if mode == "csv":
        return load_csv_palette()

    for i in range(k):
        if mode == "pastel":
            h = rng.random(); s = rng.uniform(0.15,0.35); v = rng.uniform(0.9,1.0)
        elif mode == "vivid":
            h = rng.random(); s = rng.uniform(0.8,1.0); v = rng.uniform(0.8,1.0)
        elif mode == "mono":
            h = base_h; s = rng.uniform(0.1,0.6); v = rng.uniform(0.5,1.0)
        elif mode == "neon":
            h = rng.random(); s = rng.uniform(0.85,1.0); v = rng.uniform(0.92,1.0)
        elif mode == "earth":
            h = rng.uniform(0.05,0.12); s = rng.uniform(0.3,0.6); v = rng.uniform(0.3,0.7)
        elif mode == "ocean":
            h = rng.uniform(0.45,0.6); s = rng.uniform(0.4,0.8); v = rng.uniform(0.5,1.0)
        elif mode == "sunset":
            h = rng.uniform(0.05,0.15); s = rng.uniform(0.6,1.0); v = rng.uniform(0.7,1.0)
        elif mode == "analogous":
            h = rng.uniform(base_h-0.1, base_h+0.1); s = rng.uniform(0.45,1.0); v = rng.uniform(0.6,1.0)
        elif mode == "triadic":
            # pick one of triadic hues
            base = rng.random()
            tri = (base, (base + 1/3.0) % 1.0, (base + 2/3.0) % 1.0)
            h = tri[i % 3]
            s = rng.uniform(0.5,1.0); v = rng.uniform(0.6,1.0)
        elif mode == "random":
            h = rng.random(); s = rng.uniform(0.3,1.0); v = rng.uniform(0.4,1.0)
        else:
            h = rng.random(); s = rng.uniform(0.3,1.0); v = rng.uniform(0.5,1.0)

        rgb = tuple(hsv_to_rgb([h, s, v]))
        cols.append(rgb)
    return cols

# ---------------- Poster drawer ----------------
def draw_poster(palette_mode: str, blob_shape: str, n_layers: int, wobble: float,
                points: int, sides: int, petals: int,
                radius_min: float, radius_max: float,
                alpha_min: float, alpha_max: float,
                seed: int, base_h: float, width=7, height=10):
    # reproducible RNGs
    random.seed(seed)
    np.random.seed(seed)

    fig, ax = plt.subplots(figsize=(width, height))
    ax.axis("off")
    ax.set_facecolor((0.97, 0.97, 0.97))

    palette = make_palette(30, palette_mode, base_h, rng_seed=seed)

    # draw layers back-to-front
    for i in range(n_layers):
        cx, cy = random.random(), random.random()
        rr = random.uniform(radius_min, radius_max)
        x, y = shape((cx, cy), r=rr, wobble=wobble, points=points,
                     kind=blob_shape, sides=sides, petals=petals, seed=seed + i)

        color = random.choice(palette)
        alpha = random.uniform(alpha_min, alpha_max)

        # drop shadow (slightly offset and blurred-looking via alpha)
        shadow_offset_x = 0.012 * (0.8 + random.random()*0.4)
        shadow_offset_y = -0.012 * (0.8 + random.random()*0.4)
        xs = x + shadow_offset_x
        ys = y + shadow_offset_y
        ax.fill(xs, ys, color=(0,0,0), alpha=alpha*0.35, edgecolor=None)

        # compute shading and derive face color taking mean shading to get consistent face color
        shade = apply_shading(x, y, cx, cy, light_dir=(1.0, 1.0))
        shade_mean = float(np.clip(np.mean(shade), 0.0, 1.0))
        base_color = np.array(color)
        # ambient + diffuse contributions; specular accent depending on shade distribution
        face_rgb = base_color * (0.6 + 0.4 * shade_mean)
        face_rgb = np.clip(face_rgb, 0.0, 1.0)
        face_rgba = (face_rgb[0], face_rgb[1], face_rgb[2], alpha)

        # draw filled polygon
        ax.fill(x, y, facecolor=face_rgba, edgecolor=None)

        # subtle highlight rim: overlay with low-alpha white using high-shade vertices
        highlight_strength = np.clip((shade - 0.85), 0.0, 1.0)
        if highlight_strength.max() > 0.01:
            # draw a faint stroke to simulate specular rim (use average)
            rim_alpha = 0.06 * highlight_strength.mean()
            ax.plot(x, y, linewidth=0.8, color=(1,1,1, rim_alpha))

    # header text
    ax.text(0.05, 0.95, "Final Poster • Interactive • 3D • CSV",
            transform=ax.transAxes, fontsize=18, weight="bold")
    ax.text(0.05, 0.92, "Week 9 • Art & Big Data",
            transform=ax.transAxes, fontsize=12)
    ax.text(0.05, 0.90, f"{palette_mode} • {blob_shape} • {n_layers} layers • seed : {seed}",
            transform=ax.transAxes, fontsize=11)

    plt.tight_layout(pad=0)
    return fig

# ---------------- Streamlit UI ----------------
st.set_page_config(layout="centered", page_title="Generative Poster")

st.title("Generative 3D Abstract Poster (CSV + Shapes)")

# palette upload / replace
ensure_palette_file()
st.sidebar.header("Palette CSV")
uploaded = st.sidebar.file_uploader("Upload palette CSV (r,g,b columns, 0..1)", type=["csv"])
if uploaded is not None:
    try:
        df_u = pd.read_csv(uploaded)
        if {"r","g","b"}.issubset(df_u.columns):
            df_u.to_csv(PALETTE_FILE, index=False)
            st.sidebar.success("Palette CSV uploaded and saved.")
        else:
            st.sidebar.error("CSV must contain columns: r,g,b")
    except Exception as e:
        st.sidebar.error(f"Failed to read CSV: {e}")

if st.sidebar.button("Reset built-in palette"):
    pd.DataFrame(DEFAULT_PALETTE).to_csv(PALETTE_FILE, index=False)
    st.sidebar.success("Reset to default palette.")

palette_mode = st.sidebar.selectbox("Palette Mode",
    ["pastel","vivid","mono","neon","ocean","sunset","analogous","triadic","csv","random"])

blob_shape = st.sidebar.selectbox("Shape",
    ["blob","polygon","heart","star","flower"])

n_layers = st.sidebar.slider("Layers", 3, 30, 8, 1)
wobble = st.sidebar.slider("Wobble", 0.01, 2.0, 0.15, 0.01)
points = st.sidebar.slider("Points (smoothness)", 64, 2000, 300, 32)
sides = st.sidebar.slider("Polygon / Star Sides", 3, 12, 5, 1)
petals = st.sidebar.slider("Flower Petals", 2, 24, 7, 1)
radius_min = st.sidebar.slider("Minimum Radius", 0.005, 0.2, 0.01, 0.001)
radius_max = st.sidebar.slider("Maximum Radius", 0.02, 0.4, 0.12, 0.001)
alpha_min = st.sidebar.slider("Alpha Min", 0.01, 0.6, 0.12, 0.01)
alpha_max = st.sidebar.slider("Alpha Max", 0.2, 1.0, 0.9, 0.01)
seed = st.sidebar.number_input("Seed (integer)", min_value=0, max_value=999999, value=0, step=1)
base_h = st.sidebar.slider("Base Hue (mono/analogous)", 0.0, 1.0, 0.6)

# render
if st.sidebar.button("Generate Poster") or "auto_generate" not in st.session_state:
    # ensure at least one run
    st.session_state["auto_generate"] = True
    fig = draw_poster(palette_mode, blob_shape, n_layers, wobble, points,
                      sides, petals, radius_min, radius_max, alpha_min, alpha_max,
                      int(seed), base_h, width=6, height=10)
    st.pyplot(fig)

    # download button
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=300, bbox_inches="tight")
    buf.seek(0)
    st.download_button("Download PNG (300dpi)", data=buf, file_name=f"poster_seed{seed}.png", mime="image/png")

# show current palette table
st.sidebar.header("Current CSV Palette")
try:
    df_palette = read_palette()
    st.sidebar.dataframe(df_palette)
except Exception as e:
    st.sidebar.error("Cannot read palette: " + str(e))
