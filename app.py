import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io
import os
from datetime import datetime, timedelta

# -------------------------------
# 1. App Configuration
# -------------------------------
st.set_page_config(page_title="Advanced Gantt Chart", layout="wide")
st.title("Advanced Gantt Chart for Construction Projects")
st.markdown("This app displays an interactive, detailed Gantt chart based on your project dataset.")

# -------------------------------
# 2. Data Loading from Excel
# -------------------------------
@st.cache_data
def load_data(file_path):
    if not os.path.exists(file_path):
        st.error(f"File {file_path} not found!")
        st.stop()
    df = pd.read_excel(file_path)
    # Clean column names and convert date columns
    df.columns = df.columns.str.strip()
    df["Start Date"] = pd.to_datetime(df["Start Date"], errors="coerce")
    df["End Date"] = pd.to_datetime(df["End Date"], errors="coerce")
    df["Status"] = df["Status"].astype(str)
    # Add extra columns (only in memory) if missing
    extra_cols = {
        "Progress": 0.0,
        "Priority": "Normal",
        "Planned Start": pd.NaT,
        "Actual Start": pd.NaT,
        "Due": pd.NaT,
        "Finish": pd.NaT,
        "Duration": 0,
        "Hours": 0.0,
        "Cost": 0.0
    }
    for col, default in extra_cols.items():
        if col not in df.columns:
            df[col] = default
    return df

DATA_FILE = "construction_timeline.xlsx"
df = load_data(DATA_FILE)  # This is our in‑memory version (original file remains unchanged)

# -------------------------------
# 3. (Optional) Data Editing
# -------------------------------
# You can include your existing interactive editing functionality here.
# (For brevity, we focus on the advanced Gantt chart.)

# -------------------------------
# 4. Filtering (if needed)
# -------------------------------
# (You can add sidebar filters if you want.)
df_filtered = df.copy()  # For now, we use the full dataset

# -------------------------------
# 5. Build Advanced Gantt Chart with Plotly Graph Objects
# -------------------------------
# We will sort tasks by Activity and Start Date.
tasks = df_filtered.sort_values(["Activity", "Start Date"]).reset_index(drop=True)

# Create a list of y-axis labels (combining Activity and Task)
y_labels = tasks.apply(lambda row: f"{row['Activity']} - {row['Task']}", axis=1)

# Initialize an empty Plotly figure
fig = go.Figure()

# Loop over each task to add its bar and progress overlay
bar_height = 0.8  # Height for each bar
for i, row in tasks.iterrows():
    start = row["Start Date"]
    end = row["End Date"]
    if pd.isna(start) or pd.isna(end):
        continue  # Skip tasks with invalid dates
    duration = (end - start).days
    progress = row.get("Progress", 0)
    # Choose a bar color based on Status
    status_lower = row["Status"].strip().lower()
    if status_lower == "finished":
        color = "green"
    elif status_lower == "in progress":
        color = "blue"
    else:
        color = "gray"
    # Calculate the progress duration (in days)
    progress_duration = duration * progress / 100

    # Add the main task bar as a horizontal bar using a shape
    fig.add_shape(
        type="rect",
        x0=start,
        x1=end,
        y0=i - bar_height/2,
        y1=i + bar_height/2,
        fillcolor=color,
        line=dict(width=1, color="black"),
        layer="below"
    )
    
    # Add a progress overlay rectangle (progress fill)
    fig.add_shape(
        type="rect",
        x0=start,
        x1=start + timedelta(days=progress_duration),
        y0=i - bar_height/2,
        y1=i + bar_height/2,
        fillcolor="orange",
        opacity=0.6,
        layer="above",
        line_width=0
    )
    
    # Add an annotation for the task progress percentage
    fig.add_annotation(
        x=end,
        y=i,
        text=f"{progress:.0f}%",
        showarrow=False,
        xanchor="left",
        font=dict(color="black", size=10)
    )
    
    # Add an annotation for the task label (Activity - Task) on the left side
    fig.add_annotation(
        x=start - timedelta(days=1),
        y=i,
        text=y_labels.iloc[i],
        showarrow=False,
        xanchor="right",
        font=dict(color="black", size=10)
    )

# -------------------------------
# 6. Layout Adjustments
# -------------------------------
fig.update_layout(
    title="Advanced Gantt Chart",
    xaxis=dict(
        title="Date",
        type="date",
        tickformat="%Y-%m-%d"
    ),
    yaxis=dict(
        title="Tasks",
        tickmode="array",
        tickvals=list(range(len(tasks))),
        ticktext=y_labels,
        autorange="reversed"
    ),
    margin=dict(l=150, r=50, t=50, b=50),
    height=600,
    template="plotly_white"
)

# -------------------------------
# 7. Display in Streamlit
# -------------------------------
st.header("Advanced Gantt Chart")
st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# 8. Deployment Instructions (Below as text)
# -------------------------------
st.markdown("""
### Deployment Steps for Streamlit Cloud

1. **Prepare Your Repository:**  
   - Create a GitHub repository containing your `app.py` file (with the code above) and your Excel dataset (e.g., `construction_timeline.xlsx`).

2. **Requirements File:**  
   - Create a file named `requirements.txt` in your repository.  
     Example contents:
     ```
     streamlit
     pandas
     plotly
     ```
   - (Add any other packages you use, such as `python-docx` if needed for reports.)

3. **Deploy on Streamlit Cloud:**  
   - Log in to [Streamlit Cloud](https://share.streamlit.io/).  
   - Click "New app" and select your GitHub repository.  
   - Set the main file to `app.py` and deploy.
   - Once deployed, you can share the URL with your boss.

4. **Usage:**  
   - When you update your Excel file (via the interactive editing if enabled), the extra columns are added in memory.  
   - The advanced Gantt chart will display tasks with their durations, progress overlays, and annotations.
   
This solution uses only Streamlit and Plotly, so you can run it directly on Streamlit Cloud without needing to switch to another framework.

""")
