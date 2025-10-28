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


import streamlit as st
import pandas as pd
import os

PALETTE_FILE = "palette.csv"

# --- Initialize palette.csv if not exists ---
if not os.path.exists(PALETTE_FILE):
    df_init = pd.DataFrame([
        {"name":"sky", "r":0.4, "g":0.7, "b":1.0},
        {"name":"sun", "r":1.0, "g":0.8, "b":0.2},
        {"name":"forest", "r":0.2, "g":0.6, "b":0.3}
    ])
    df_init.to_csv(PALETTE_FILE, index=False)

# --- Utility functions ---
def read_palette():
    return pd.read_csv(PALETTE_FILE)

def save_palette(df):
    df.to_csv(PALETTE_FILE, index=False)

def add_color(name, r, g, b):
    df = read_palette()
    df = pd.concat([df, pd.DataFrame([{"name":name,"r":r,"g":g,"b":b}])], ignore_index=True)
    save_palette(df)
    st.success(f"Added color '{name}'")

def update_color(name, r=None, g=None, b=None):
    df = read_palette()
    if name in df["name"].values:
        idx = df.index[df["name"]==name][0]
        if r is not None: df.at[idx,"r"] = r
        if g is not None: df.at[idx,"g"] = g
        if b is not None: df.at[idx,"b"] = b
        save_palette(df)
        st.success(f"Updated color '{name}'")
    else:
        st.warning(f"Color '{name}' not found")

def delete_color(name):
    df = read_palette()
    if name in df["name"].values:
        df = df[df["name"] != name]
        save_palette(df)
        st.success(f"Deleted color '{name}'")
    else:
        st.warning(f"Color '{name}' not found")

# --- Streamlit App ---
st.title("🎨 Color Palette Manager")

st.sidebar.header("Manage Palette")

# --- View palette ---
st.subheader("Current Palette")
palette = read_palette()
st.dataframe(palette)

# --- Add color ---
with st.sidebar.expander("Add New Color"):
    new_name = st.text_input("Color Name")
    new_r = st.slider("Red (0-1)", 0.0, 1.0, 0.5)
    new_g = st.slider("Green (0-1)", 0.0, 1.0, 0.5)
    new_b = st.slider("Blue (0-1)", 0.0, 1.0, 0.5)
    if st.button("Add Color"):
        if new_name.strip() != "":
            add_color(new_name.strip(), new_r, new_g, new_b)
        else:
            st.warning("Please enter a valid color name")

# --- Update color ---
with st.sidebar.expander("Update Existing Color"):
    update_name = st.selectbox("Select Color", palette["name"].tolist())
    update_r = st.slider("Red (0-1)", 0.0, 1.0, float(palette.loc[palette['name']==update_name,'r']))
    update_g = st.slider("Green (0-1)", 0.0, 1.0, float(palette.loc[palette['name']==update_name,'g']))
    update_b = st.slider("Blue (0-1)", 0.0, 1.0, float(palette.loc[palette['name']==update_name,'b']))
    if st.button("Update Color"):
        update_color(update_name, update_r, update_g, update_b)

# --- Delete color ---
with st.sidebar.expander("Delete Color"):
    delete_name = st.selectbox("Select Color to Delete", palette["name"].tolist())
    if st.button("Delete Color"):
        delete_color(delete_name)

import streamlit as st

# --- Load palette from CSV as list of RGB tuples ---
def load_csv_palette():
    df = read_palette()  # uses your existing read_palette() function
    return [(row.r, row.g, row.b) for row in df.itertuples()]

# Load palette
palette_csv = load_csv_palette()

# Show palette in Streamlit
st.subheader("Loaded Palette")
for i, (r, g, b) in enumerate(palette_csv):
    st.write(f"{i+1}: RGB({r:.2f}, {g:.2f}, {b:.2f})")

import streamlit as st
import matplotlib.pyplot as plt

def show_palette(palette):
    fig, ax = plt.subplots(figsize=(6, 2))
    for i, c in enumerate(palette):
        ax.fill_between([i, i+1], 0, 1, color=c)
        ax.text(i+0.5, -0.1, f"{i+1}", ha="center", va="top", fontsize=10)
    ax.axis("off")
    st.pyplot(fig)

# --- Show the loaded CSV palette in Streamlit ---
st.subheader("Palette Preview")
show_palette(palette_csv)


def make_palette(k=6, mode="pastel", base_h=0.60):
    cols = []
    if mode == "csv":
        return load_csv_palette()

    for _ in range(k):
        if mode == "pastel":
            h = random.random(); s = random.uniform(0.15,0.35); v = random.uniform(0.9,1.0)
        elif mode == "vivid":
            h = random.random(); s = random.uniform(0.8,1.0);  v = random.uniform(0.8,1.0)
        elif mode == "mono":
            h = base_h;         s = random.uniform(0.2,0.6);   v = random.uniform(0.5,1.0)
        else: # random
            h = random.random(); s = random.uniform(0.3,1.0); v = random.uniform(0.5,1.0)
        cols.append(tuple(hsv_to_rgb([h,s,v])))

    return cols

import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import random, math
from matplotlib.colors import hsv_to_rgb

# --- Your existing helper functions: shape, rotate_coords, luminance --- #

# --- Palette generator placeholder ---
def make_palette(k=6, mode="pastel"):
    # For now, simple pastel palette
    np.random.seed(0)
    if mode=="pastel":
        return np.random.uniform(0.5, 1.0, (k,3))
    elif mode=="vibrant":
        return np.random.uniform(0.3, 1.0, (k,3))
    else:
        return np.random.uniform(0.0, 1.0, (k,3))

# --- Streamlit UI ---
st.title("🎨 Generative Poster")

st.sidebar.header("Poster Settings")
palette_mode = st.sidebar.selectbox("Palette Mode", ["pastel", "vibrant", "random"])
shape_type = st.sidebar.selectbox("Shape Type", ["blob", "circle", "polygon"])
n_layers = st.sidebar.slider("Number of Layers", 5, 30, 10)
wobble = st.sidebar.slider("Wobble", 0.0, 0.5, 0.15)
rotation_range = st.sidebar.slider("Rotation Range (rad)", 0.0, 1.0, 0.3)
shadow_offset = st.sidebar.slider("Shadow Offset", 0.0, 0.1, 0.02)
light_angle = st.sidebar.slider("Light Angle (deg)", 0, 360, 45)
brightness_strength = st.sidebar.slider("Brightness Strength", 0.0, 1.0, 0.3)
alpha_min = st.sidebar.slider("Alpha Min", 0.1, 1.0, 0.6)
alpha_max = st.sidebar.slider("Alpha Max", 0.1, 1.0, 0.9)
background = st.sidebar.color_picker("Background Color", "#FFFFFF")
title_color = st.sidebar.color_picker("Title Color", "#000000")
seed = st.sidebar.number_input("Random Seed", 0, 9999, 0)

# --- Generate Poster ---
if st.button("🎨 Generate Poster"):
    random.seed(seed)
    np.random.seed(seed)
    plt.close("all")
    fig = plt.figure(figsize=(6,8), facecolor=background)
    ax = plt.gca()
    ax.set_facecolor(background)
    ax.axis("off")

    palette = make_palette(6, mode=palette_mode)

    dx = shadow_offset * math.cos(math.radians(light_angle))
    dy = -shadow_offset * math.sin(math.radians(light_angle))

    for i in range(n_layers):
        cx, cy = random.random(), random.random()
        rr = random.uniform(0.15, 0.45)
        angle = random.uniform(-rotation_range, rotation_range)
        x, y = shape(center=(cx, cy), r=rr, wobble=wobble, shape_type=shape_type)
        x, y = rotate_coords(x, y, cx, cy, angle)

        # Shadow
        x_s, y_s = x + dx, y + dy
        ax.fill(x_s, y_s, color=(0,0,0), alpha=0.45, edgecolor=(0,0,0,0))

        # Main shape
        base_color = np.array(random.choice(palette))
        brightness_factor = 0.7 + brightness_strength*(i/n_layers)
        color = np.clip(base_color*brightness_factor,0,1)
        alpha = random.uniform(alpha_min, alpha_max)
        ax.fill(x, y, color=color, alpha=alpha, edgecolor=(0,0,0,0))

    # Adjust title color for contrast
    bg_rgb = tuple(int(background.lstrip("#")[i:i+2],16)/255 for i in (0,2,4))
    text_rgb = tuple(int(title_color.lstrip("#")[i:i+2],16)/255 for i in (0,2,4))
    if abs(luminance(bg_rgb)-luminance(text_rgb))<0.5:
        title_color = "#FFFFFF" if luminance(bg_rgb)<0.5 else "#000000"

    ax.text(0.01,0.95,"Final Poster",fontsize=26,weight="bold",
             color=title_color,transform=ax.transAxes,alpha=1.0)
    ax.text(0.01,0.91,"Week 8 • Arts & Big Data",fontsize=14,
             color=title_color,transform=ax.transAxes,alpha=1.0)
    ax.text(0.01,0.88,f"Style: {palette_mode.title()} / Shape: {shape_type.title()}",fontsize=13,
             color=title_color,transform=ax.transAxes,alpha=1.0)

    st.pyplot(fig)

    # --- Download buttons ---
    fig.savefig("final_poster.png", dpi=300, facecolor=background, bbox_inches="tight")
    st.download_button("💾 Download PNG", data=open("final_poster.png","rb").read(),
                       file_name="final_poster.png", mime="image/png")


interact(
    draw_poster,
    n_layers=widgets.IntSlider(min=3,max=20,step=1,value=10, description="Layers"),
    wobble=widgets.FloatSlider(min=0.01,max=9.0,step=0.01,value=0.05, description="Wobble"),
    palette_mode=widgets.Dropdown(options=["pastel","vivid","mono","random","csv"], value="csv"),
    shape_type=Dropdown(
        options=['blob','circle','polygon'],
        value='polygon', description='Shape:'),
    background=ColorPicker(value='#FFFFFF',description='Background'),
    title_color=ColorPicker(value='#000000',description='Text'),
    seed=widgets.IntSlider(min=0,max=9999,step=1,value=9345, description="Seed"),
    shadow_offset=FloatSlider(value=0.01,min=0.0,max=0.1,step=0.005,description='Shadow Offset'),
    brightness_strength=FloatSlider(value=0.6,min=0.0,max=0.9,step=0.05,description='Brightness'),
    alpha_min=FloatSlider(value=0.25,min=0.1,max=1.0,step=0.05,description='Alpha Min'),
    alpha_max=FloatSlider(value=0.55,min=0.1,max=1.0,step=0.05,description='Alpha Max'),
    light_angle=IntSlider(value=50,min=0,max=360,step=5,description='Light Angle'),
    rotation_range=FloatSlider(value=0.1,min=0.0,max=1.0,step=0.05,description='Rotation')
);
