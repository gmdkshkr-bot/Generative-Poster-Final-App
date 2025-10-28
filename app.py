import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random, math, os
from matplotlib.colors import hsv_to_rgb

# === Helpers ===
def luminance(rgb):
    r, g, b = rgb
    return 0.299*r + 0.587*g + 0.114*b

def blob(center=(0.5,0.5), r=0.3, points=200, wobble=0.15):
    angles = np.linspace(0, 2*math.pi, points, endpoint=False)
    radii = r * (1 + wobble*(np.random.rand(points)-0.5))
    x = center[0] + radii * np.cos(angles)
    y = center[1] + radii * np.sin(angles)
    return x, y

def shape(center=(0.5,0.5), r=0.3, points=200, wobble=0.15, shape_type="blob"):
    if shape_type=="circle":
        angles=np.linspace(0,2*math.pi,points)
        x=center[0]+r*np.cos(angles)
        y=center[1]+r*np.sin(angles)
        return x, y
    elif shape_type=="polygon":
        n_sides=random.randint(3,9)
        angles=np.linspace(0,2*math.pi,n_sides,endpoint=False)
        x=center[0]+r*np.cos(angles)
        y=center[1]+r*np.sin(angles)
        return np.append(x,x[0]), np.append(y,y[0])
    else:
        return blob(center,r,points,wobble)

def rotate_coords(x, y, cx, cy, angle):
    x_rot = (x-cx)*np.cos(angle) - (y-cy)*np.sin(angle) + cx
    y_rot = (x-cx)*np.sin(angle) + (y-cy)*np.cos(angle) + cy
    return x_rot, y_rot

# --- Palette ---
def make_palette(k=6, mode="pastel", base_h=0.6):
    cols=[]
    for _ in range(k):
        if mode=="pastel":
            h=random.random(); s=random.uniform(0.15,0.35); v=random.uniform(0.9,1.0)
        elif mode=="vivid":
            h=random.random(); s=random.uniform(0.8,1.0); v=random.uniform(0.8,1.0)
        elif mode=="mono":
            h=base_h; s=random.uniform(0.2,0.6); v=random.uniform(0.5,1.0)
        else:
            h=random.random(); s=random.uniform(0.3,1.0); v=random.uniform(0.5,1.0)
        cols.append(tuple(hsv_to_rgb([h,s,v])))
    return cols

# --- Draw Poster ---
def draw_poster(
    palette_mode="pastel", shape_type="blob", n_layers=10, wobble=0.15,
    background="#FFFFFF", title_color="#000000", seed=0,
    shadow_offset=0.02, brightness_strength=0.3,
    alpha_min=0.6, alpha_max=0.9,
    light_angle=45, rotation_range=0.3):

    random.seed(seed); np.random.seed(seed)
    fig = plt.figure(figsize=(6,8), facecolor=background)
    ax = plt.gca(); ax.axis('off'); ax.set_facecolor(background)

    palette = make_palette(6, mode=palette_mode)
    dx = shadow_offset * math.cos(math.radians(light_angle))
    dy = -shadow_offset * math.sin(math.radians(light_angle))

    for i in range(n_layers):
        cx, cy = random.random(), random.random()
        rr = random.uniform(0.15,0.45)
        angle = random.uniform(-rotation_range, rotation_range)
        x, y = shape(center=(cx, cy), r=rr, wobble=wobble, shape_type=shape_type)
        x, y = rotate_coords(x, y, cx, cy, angle)

        # shadow
        x_s, y_s = x + dx, y + dy
        ax.fill(x_s, y_s, color=(0,0,0), alpha=0.45, edgecolor=(0,0,0,0))

        # main shape
        base_color = np.array(random.choice(palette))
        brightness_factor = 0.7 + brightness_strength*(i/n_layers)
        color = np.clip(base_color*brightness_factor,0,1)
        alpha = random.uniform(alpha_min, alpha_max)
        ax.fill(x, y, color=color, alpha=alpha, edgecolor=(0,0,0,0))

    # text contrast
    bg_rgb = tuple(int(background.lstrip("#")[i:i+2],16)/255 for i in (0,2,4))
    text_rgb = tuple(int(title_color.lstrip("#")[i:i+2],16)/255 for i in (0,2,4))
    if abs(luminance(bg_rgb)-luminance(text_rgb))<0.5:
        title_color="#FFFFFF" if luminance(bg_rgb)<0.5 else "#000000"

    ax.text(0.01,0.95,"Final Poster",fontsize=26,weight="bold",color=title_color,transform=ax.transAxes)
    ax.text(0.01,0.91,"Week 8 • Arts & Big Data",fontsize=14,color=title_color,transform=ax.transAxes)
    ax.text(0.01,0.88,f"Style: {palette_mode.title()} / Shape: {shape_type.title()}",fontsize=13,color=title_color,transform=ax.transAxes)

    return fig

# === Streamlit UI ===
st.title("🎨 Generative Poster (Streamlit Ready)")

st.sidebar.header("Controls")
palette_mode = st.sidebar.selectbox("Palette Mode", ["pastel","vivid","mono","random"], index=0)
shape_type = st.sidebar.selectbox("Shape Type", ['blob','circle','polygon'], index=0)
n_layers = st.sidebar.slider("Layers", 3, 20, 10)
wobble = st.sidebar.slider("Wobble", 0.01, 0.9, 0.05, 0.01)
shadow_offset = st.sidebar.slider("Shadow Offset", 0.0, 0.1, 0.01, 0.005)
brightness_strength = st.sidebar.slider("Brightness", 0.0, 0.9, 0.6, 0.05)
alpha_min = st.sidebar.slider("Alpha Min", 0.1, 1.0, 0.25, 0.05)
alpha_max = st.sidebar.slider("Alpha Max", 0.1, 1.0, 0.55, 0.05)
light_angle = st.sidebar.slider("Light Angle", 0, 360, 50, 5)
rotation_range = st.sidebar.slider("Rotation Range", 0.0, 1.0, 0.1, 0.05)
background = st.sidebar.color_picker("Background Color", "#FFFFFF")
title_color = st.sidebar.color_picker("Title Color", "#000000")
seed = st.sidebar.number_input("Random Seed", 0, 9999, 0)

if st.button("🎨 Generate Poster"):
    fig = draw_poster(
        palette_mode=palette_mode, shape_type=shape_type, n_layers=n_layers, wobble=wobble,
        background=background, title_color=title_color, seed=seed,
        shadow_offset=shadow_offset, brightness_strength=brightness_strength,
        alpha_min=alpha_min, alpha_max=alpha_max,
        light_angle=light_angle, rotation_range=rotation_range
    )
    st.pyplot(fig=fig)

    # Save button
    if st.button("💾 Save Poster"):
        filename = f"poster_{seed}.png"
        fig.savefig(filename, dpi=300, bbox_inches='tight')
        st.success(f"Saved as {filename}")
