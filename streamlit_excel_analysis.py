""
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
        df = df.dropna()
        df["Water"] = df["Water"].astype(str).str.replace(',', '.')
        df["Water"] = pd.to_numeric(df["Water"], errors='coerce')
        return df
    except Exception as e:
        st.error(f"Error loading {file.name}: {e}")
        return None

uploaded_files = st.file_uploader("Upload Excel files", type=["xls", "xlsx"], accept_multiple_files=True)

if uploaded_files:
    dfs = {}
    means = []
    std_devs = []
    settings = {}

    for i, file in enumerate(uploaded_files):
        df = load_excel(file)
        if df is not None:
            means.append(df["Water"].mean())
            std_devs.append(df["Water"].std())
            name = file.name
            dfs[name] = df
            settings[name] = {
                "color": list(color_palette.values())[i % len(color_palette)],
                "label": name
            }

    combine_files = st.checkbox("Combine data from multiple files")

    if combine_files:
        selected_files = st.multiselect("Select files to average", list(dfs.keys()), default=list(dfs.keys()))
        selected_means = [means[i] for i, name in enumerate(dfs) if name in selected_files]
        selected_stds = [std_devs[i] for i, name in enumerate(dfs) if name in selected_files]

        if selected_means:
            combined_mean = np.mean(selected_means)
            combined_std = np.sqrt(np.mean(np.array(selected_stds) ** 2))
            means.append(combined_mean)
            std_devs.append(combined_std)
            settings["Combined"] = {
                "color": "#000000",
                "label": "Combined"
            }

    labels = list(dfs.keys()) + (["Combined"] if combine_files else [])
    visible_bars = st.multiselect("Select bars to display", labels, default=labels)
    font_size = st.slider("Font size", min_value=8, max_value=24, value=15)

    st.subheader("Customize Appearance")
    for name in labels:
        if name not in settings:
            continue
        cols = st.columns([3, 2, 2])
        with cols[0]:
            settings[name]["label"] = st.text_input(f"Label for {name}", value=settings[name]["label"], key=f"label_{name}")
        with cols[1]:
            color_name = st.selectbox(
                f"Color for {name}",
                options=list(color_palette.keys()),
                index=list(color_palette.values()).index(settings[name]["color"]) if settings[name]["color"] in color_palette.values() else 0,
                key=f"color_select_{name}"
            )
        with cols[2]:
            settings[name]["color"] = st.color_picker(f"Pick color for {name}", value=color_palette[color_name], key=f"picker_{name}")

    # Plotting
    fig, ax = plt.subplots()
    indices = range(len(labels))
    visible_indices = [i for i, label in enumerate(labels) if label in visible_bars]

    bar_heights = [means[i] for i in visible_indices]
    bar_errors = [std_devs[i] for i in visible_indices]
    bar_labels = [settings[labels[i]]["label"] for i in visible_indices]
    bar_colors = [settings[labels[i]]["color"] for i in visible_indices]

    ax.bar(visible_indices, bar_heights, yerr=bar_errors, capsize=5, color=bar_colors)
    ax.set_xticks(visible_indices)
    ax.set_xticklabels(bar_labels, fontsize=font_size)
    ax.set_ylabel("Contact angle (°)", fontsize=font_size)

    st.pyplot(fig)

    # Table preview
    table_data = {"File": [settings[label]["label"] for label in labels], "Mean": means, "Std Dev": std_devs}
    table_df = pd.DataFrame(table_data)
    st.dataframe(table_df)

    file_name = st.text_input("Output file name (without extension)", value="results")

    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    st.download_button("Download plot as PNG", buf, f"{file_name}.png", "image/png")

    excel_buf = io.BytesIO()
    with pd.ExcelWriter(excel_buf, engine="xlsxwriter") as writer:
        table_df.to_excel(writer, index=False)
    excel_buf.seek(0)
    st.download_button("Download table as Excel", excel_buf, f"{file_name}.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

else:
    st.info("Please upload at least one Excel file.")
