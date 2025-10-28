import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import random, math
from matplotlib.colors import hsv_to_rgb

# === Utility: Color brightness
def luminance(rgb):
    r, g, b = rgb
    return 0.299 * r + 0.587 * g + 0.114 * b

# === Blob shape generator
def blob(center=(0.5, 0.5), r=0.3, points=200, wobble=0.15):
    angles = np.linspace(0, 2 * math.pi, points, endpoint=False)
    radii = r * (1 + wobble * (np.random.rand(points) - 0.5))
    x = center[0] + radii * np.cos(angles)
    y = center[1] + radii * np.sin(angles)
    return x, y

# === Shape generator (circle, polygon, blob)
def shape(center=(0.5, 0.5), r=0.3, points=200, wobble=0.15, shape_type="blob"):
    if shape_type == "circle":
        angles = np.linspace(0, 2 * math.pi, points)
        x = center[0] + r * np.cos(angles)
        y = center[1] + r * np.sin(angles)
        return x, y

    elif shape_type == "polygon":
        n_sides = random.randint(3, 9)
        angles = np.linspace(0, 2 * math.pi, n_sides, endpoint=False)
        x = center[0] + r * np.cos(angles)
        y = center[1] + r * np.sin(angles)
        return np.append(x, x[0]), np.append(y, y[0])

    else:
        return blob(center, r, points, wobble)

# === Rotate coordinates (for 3D-like tilt)
def rotate_coords(x, y, cx, cy, angle):
    x_rot = (x - cx) * np.cos(angle) - (y - cy) * np.sin(angle) + cx
    y_rot = (x - cx) * np.sin(angle) + (y - cy) * np.cos(angle) + cy
    return x_rot, y_rot


# === Streamlit App === #
st.title("🎨 Generative Abstract Shape Viewer")

st.sidebar.header("Shape Controls")

# --- Controls ---
shape_type = st.sidebar.selectbox("Select Shape Type", ["blob", "circle", "polygon"])
radius = st.sidebar.slider("Radius (r)", 0.05, 0.5, 0.3, 0.01)
points = st.sidebar.slider("Number of Points", 50, 400, 200, 10)
wobble = st.sidebar.slider("Wobble (for blobs)", 0.0, 0.5, 0.15, 0.01)
angle = st.sidebar.slider("Rotation Angle (radians)", -math.pi, math.pi, 0.0, 0.1)

center_x = st.sidebar.slider("Center X", 0.0, 1.0, 0.5, 0.01)
center_y = st.sidebar.slider("Center Y", 0.0, 1.0, 0.5, 0.01)

color = st.sidebar.color_picker("Shape Color", "#1f77b4")
bg_color = st.sidebar.color_picker("Background Color", "#ffffff")

# --- Draw shape ---
x, y = shape(center=(center_x, center_y), r=radius, points=points, wobble=wobble, shape_type=shape_type)
x_rot, y_rot = rotate_coords(x, y, center_x, center_y, angle)

fig, ax = plt.subplots(figsize=(6, 6))
ax.set_facecolor(bg_color)
ax.fill(x_rot, y_rot, color=color, alpha=0.8)
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis("off")

st.pyplot(fig)

# --- Optional: Save button ---
if st.button("💾 Save as PNG"):
    fig.savefig("generated_shape.png", dpi=300, bbox_inches="tight", facecolor=bg_color)
    st.success("Saved as generated_shape.png")
