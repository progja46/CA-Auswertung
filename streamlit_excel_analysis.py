import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import io

st.set_page_config(layout="wide")

# Helper function to load data from Excel
def load_excel(file):
    try:
        df = pd.read_excel(file, skiprows=1, names=["No.", "Water"])
        df = df.dropna()
        df["Water"] = pd.to_numeric(df["Water"].str.replace(',', '.'), errors='coerce')
        return df
    except Exception as e:
        st.error(f"Error loading {file.name}: {e}")
        return None

# File uploader
uploaded_files = st.file_uploader("Upload Excel files", type=["xls", "xlsx"], accept_multiple_files=True)

if uploaded_files:
    dfs = {}
    means = []
    std_devs = []

    for file in uploaded_files:
        df = load_excel(file)
        if df is not None:
            means.append(df["Water"].mean())
            std_devs.append(df["Water"].std())
            dfs[file.name] = df

    # Option to average across multiple files
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

    # Select visible bars
    labels = list(dfs.keys()) + (["Combined"] if combine_files else [])
    visible_bars = st.multiselect("Select bars to display", labels, default=labels)

    # Font size slider
    font_size = st.slider("Font size", min_value=8, max_value=24, value=15)

    # Plotting
    fig, ax = plt.subplots()

    indices = range(len(labels))
    visible_indices = [i for i, label in enumerate(labels) if label in visible_bars]

    bar_heights = [means[i] for i in visible_indices]
    bar_errors = [std_devs[i] for i in visible_indices]

    plt.bar(visible_indices, bar_heights, yerr=bar_errors, capsize=5)
    plt.xticks(visible_indices, [labels[i] for i in visible_indices], fontsize=font_size)
    plt.ylabel("Contact angle (°)", fontsize=font_size)

    st.pyplot(fig)

    # Table preview
    table_data = {"File": labels, "Mean": means, "Std Dev": std_devs}
    table_df = pd.DataFrame(table_data)
    st.dataframe(table_df)

    # File name input
    file_name = st.text_input("Output file name (without extension)", value="results")

    # Download plot as PNG
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    st.download_button("Download plot as PNG", buf, f"{file_name}.png", "image/png")

    # Download table as Excel
    excel_buf = io.BytesIO()
    with pd.ExcelWriter(excel_buf, engine="xlsxwriter") as writer:
        table_df.to_excel(writer, index=False)
    excel_buf.seek(0)
    st.download_button("Download table as Excel", excel_buf, f"{file_name}.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

else:
    st.info("Please upload at least one Excel file.")
