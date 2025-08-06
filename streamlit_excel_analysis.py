import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import io

st.set_page_config(layout="wide")

# Color palette
color_palette = {
    "Dark Blue": "#2066a8",
    "Med Blue": "#8ecdda",
    "Light Blue": "#cde1ec",
    "Gray": "#ededed",
    "Light Red": "#f6d6c2",
    "Med Red": "#d47264",
    "Dark Red": "#ae282c",
    "Dark Teal": "#1f6f6f",
    "Med Teal": "#54a1a1",
    "Light Teal": "#9fc8c8",
    "Soft Peach": "#fee8c8",
    "Orange Mid": "#fdbb84",
    "Strong Orange": "#e34a33",
    "Black (Default)": "#000000"
}

# Helper function to load data from Excel
def load_excel(file):
    try:
        df = pd.read_excel(file, skiprows=1, names=["No.", "Water"])
        df["Water"] = df["Water"].astype(str).str.replace(',', '.')
        df["Water"] = pd.to_numeric(df["Water"], errors='coerce')

        # Extract only numeric rows
        data_rows = df[pd.to_numeric(df["No."], errors='coerce').notnull()]
        mean_value = data_rows["Water"].mean()
        std_dev_value = data_rows["Water"].std()

        return data_rows, mean_value, std_dev_value
    except Exception as e:
        st.error(f"Error loading {file.name}: {e}")
        return None, None, None

uploaded_files = st.file_uploader("Upload Excel files", type=["xls", "xlsx"], accept_multiple_files=True)

if uploaded_files:
    dfs = {}
    means = []
    std_devs = []
    settings = {}

    for i, file in enumerate(uploaded_files):
        df, mean, std_dev = load_excel(file)
        if df is not None:
            means.append(mean)
            std_devs.append(std_dev)
            name = file.name
            dfs[name] = df
            settings[name] = {
                "color": list(color_palette.values())[i % len(color_palette)],
                "label": name
            }

    combine_files = st.checkbox("Combine data from multiple files")

    if combine_files:
        selected_files = st.multiselect("Select files to average", list(dfs.keys()), default=list(dfs.keys()))
        combined_data = pd.concat([dfs[name] for name in selected_files])
        combined_mean = combined_data["Water"].mean()
        combined_std = combined_data["Water"].std()
        means.append(combined_mean)
        std_devs.append(combined_std)
        settings["Combined"] = {
            "color": "#000000",
            "label": "Combined"
        }
        labels = list(dfs.keys()) + ["Combined"]
    else:
        labels = list(dfs.keys())

  # Auswahl der sichtbaren Balken
st.markdown("### Customize Displayed Bars and Order")

visible_bars = st.multiselect("Select bars to display", labels, default=labels)

# Auswahl der Reihenfolge – nur für sichtbare Balken sinnvoll
bar_order = st.multiselect("Select bar order (drag to reorder)", visible_bars, default=visible_bars)

# Final geordnete, sichtbare Balken
ordered_visible_bars = [label for label in bar_order if label in visible_bars]

# Schriftgröße
font_size = st.slider("Font size", min_value=8, max_value=24, value=15)

# Plotting
fig, ax = plt.subplots()

bar_heights = [means[labels.index(label)] for label in ordered_visible_bars]
bar_errors = [std_devs[labels.index(label)] for label in ordered_visible_bars]
bar_labels = [settings[label]["label"] for label in ordered_visible_bars]
bar_colors = [settings[label]["color"] for label in ordered_visible_bars]
indices = range(len(ordered_visible_bars))

ax.bar(indices, bar_heights, yerr=bar_errors, capsize=5, color=bar_colors)
ax.set_xticks(indices)
ax.set_xticklabels(bar_labels, fontsize=font_size)
ax.set_ylabel("Contact angle (°)", fontsize=font_size)

st.pyplot(fig)
