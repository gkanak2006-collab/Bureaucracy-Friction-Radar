import os
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

st.set_page_config(page_title="Bureaucracy Friction Radar", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
.stApp {
  background: linear-gradient(135deg, #f4f7fb 0%, #eef2f7 100%);
  color: #0b1220;
}

.banner {
  width: 100%;
  background-image: 
    linear-gradient(rgba(0, 0, 0, 0.45), rgba(0, 0, 0, 0.45)),
    url("https://images.unsplash.com/photo-1506784983877-45594efa4cbe?auto=format&fit=crop&w=1600&q=80");
  background-size: cover;
  background-position: center;
  border-radius: 18px;
  padding: 48px;
  margin-bottom: 24px;
}
.banner h1 {
  font-size: 34px;
  margin: 0;
  color: #a7c6db;
  font-weight: 800;
}
.banner p {
  color: #dae4ed;
  margin: 6px 0 0;
}

.card {
  background:#ffffff;
  border-left: 6px solid #63c987;
  padding: 16px;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(2,6,23,0.6);
  color: #0b1220;
}

.panel-img {
  width:100%;
  border-radius:8px;
  margin-top:8px;
  box-shadow: 0 4px 12px rgba(2,6,23,0.6);
}

h2,h3,h4 {
  color: #0b1220 !important;
}

.accent-line {
  height:6px;
  background: linear-gradient(90deg, #FF7F50, #FFD700);
  border-radius:4px;
  margin:12px 0;
}
div.stDownloadButton > button {
    background-color: #236796;
    color: white;
    border-radius: 10px;
    padding: 10px 18px;
    font-weight: 600;
    border: none;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="banner">
  <h1>Bureaucracy Friction Radar (BFR)</h1>
  <p>Upload administrative process data to analyze inefficiencies and identify high-friction areas.</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.title("⚙️ BFR Controls")
uploaded_file = st.sidebar.file_uploader( "Upload administrative data", type=["csv", "xlsx"])

st.markdown("<br>", unsafe_allow_html=True)

st.info("📄 Data can be collaboratively maintained using **Google Sheets** "
    "and can be exported as CSV for analysis in this tool.")

def _map_columns(cols):
    norm = {c: c.strip().lower().replace("_", " ") for c in cols}
    mapping = {}

    for expected, keywords in {
        'Process_Name': ['process', 'process name', 'process_name', 'name'],
        'Waiting_Time': ['waiting', 'time', 'wait'],
        'Number_of_Steps': ['step', 'numsteps', 'numberofsteps'],
        'Repeat_Visits': ['repeat', 'visit', 'revisit']
    }.items():
        found = None
        for c, nc in norm.items():
            if any(k in nc for k in keywords):
                found = c
                break
        mapping[expected] = found
    return mapping

df = None
if uploaded_file:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        st.sidebar.success("Data uploaded successfully.")
    except Exception as e:
        st.sidebar.error(f"Failed to read uploaded file: {e}")
        st.stop()
else:
    sample_path = os.path.join(os.path.dirname(__file__), "sample_data.csv")
    if os.path.exists(sample_path):
        try:
            df = pd.read_csv(sample_path)
            st.sidebar.info("No upload detected — loaded example dataset 'sample_data.csv' from the app folder.")
        except Exception as e:
            st.sidebar.error(f"Failed to read sample data: {e}")
            st.stop()
    else:
        st.info("Upload a CSV/XLSX on the sidebar to load data and begin.")
        st.stop()

original_cols = list(df.columns)
mapping = _map_columns(original_cols)

renames = {}
warnings = []
for target, found in mapping.items():
    if found is None:
        warnings.append(target)
    else:
        renames[found] = target

if renames:
    df = df.rename(columns=renames)

if warnings:
    msg_lines = []
    if 'Process_Name' in warnings:
        df['Process_Name'] = df.index.astype(str)
        msg_lines.append("'Process_Name' missing — using row index as process names.")
    for c in ['Waiting_Time', 'Number_of_Steps', 'Repeat_Visits']:
        if c in warnings:
            df[c] = 0
            msg_lines.append(f"'{c}' missing — filled with zeros.")
    if msg_lines:
        st.warning("Auto-applied fixes: " + " ".join(msg_lines))
else:
    st.success("Columns mapped successfully.")

df.columns = [col.strip().replace(" ", "_") for col in df.columns]

st.subheader("Raw Data Preview")
st.dataframe(df.head(200))

for col in ["Waiting_Time", "Number_of_Steps", "Repeat_Visits"]:
    if col not in df.columns:
        df[col] = 0
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

st.subheader("Friction Analysis")
st.write("A Friction Score is calculated based on time taken, number of steps and repeated visits. Higher score means more bureaucratic friction.")

if 'Friction_Score' not in df.columns:
    df["Friction_Score"] = df["Waiting_Time"] + df["Number_of_Steps"] + df["Repeat_Visits"]


process_count = df.shape[0]
avg_friction = df["Friction_Score"].mean()
try:
    top_process = df.loc[df["Friction_Score"].idxmax()]["Process_Name"] if not df.empty else "—"
except Exception:
    top_process = "—"


st.dataframe(df[["Process_Name", "Friction_Score"]].sort_values("Friction_Score", ascending=False))

st.subheader("Friction Score by Process")
fig, ax = plt.subplots(figsize=(10, 5), facecolor="#FFFFFF")
fig.patch.set_facecolor('#FFFFFF')
ax.set_facecolor("#FFFFFF")

bars = ax.bar(df["Process_Name"].astype(str), df["Friction_Score"], color="#0B3D91")
ax.set_xlabel("Administrative Process", color="black")
ax.set_ylabel("Friction Score", color="black")
ax.set_title("High-Friction Administrative Processes", color="black")
ax.tick_params(axis='x', colors='black')
ax.tick_params(axis='y', colors='black')
plt.xticks(rotation=45, ha="right")
fig.tight_layout()
st.pyplot(fig, use_container_width=True)


st.subheader(" Advanced Visualization (Looker Studio)")
st.write("The friction analysis results can be exported to **Google Looker Studio** to build executive dashboards for decision-makers.")
st.markdown("- 🔍 Identify high-friction departments\n- 📉 Monitor improvement over time\n- 🏛 Enable data-driven governance decisions")

st.subheader("Key Insights")
if df["Friction_Score"].notnull().any():
    highest_friction = df.loc[df["Friction_Score"].idxmax()]
    st.write(f"🔴 *{highest_friction['Process_Name']}* has the highest friction, indicating excessive delays or complexity.")

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"""
    <div class="card">
      <h4>📊 Quick Stats</h4>
      <div class="accent-line"></div>
      <p><strong>Processes:</strong> {process_count}<br><strong>Avg Friction:</strong> {avg_friction:.1f}</p>
      <img class="panel-img" src="https://images.unsplash.com/photo-1559526324-593bc073d938?auto=format&fit=crop&w=800&q=60" />
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
    <div class="card">
      <h4>🔍 Top Concern</h4>
      <div class="accent-line"></div>
      <p><strong>Highest Friction:</strong> {top_process}</p>
      <img class="panel-img" src="https://i.pinimg.com/736x/41/45/d7/4145d7ec283ba66142f00cf3c58a1818.jpg" />
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown("""
    <div class="card">
      <h4>💡 Tip</h4>
      <div class="accent-line"></div>
      <p>Use filters and export results to build dashboards for stakeholders.</p>
      <img class="panel-img" src="https://images.unsplash.com/photo-1516251193007-45ef944ab0c6?auto=format&fit=crop&w=800&q=60" />
    </div>
    """, unsafe_allow_html=True)


st.subheader("🛠 Recommended Actions")
st.markdown("""
- ✅ **Simplify approval steps for high-friction processes**  
 Many bureaucratic processes have unnecessary steps that slow down approvals. By reviewing and removing redundant steps, administrators can make the workflow faster and less frustrating for users.

- 💻 **Introduce digital submissions and tracking**  
 Replacing manual paperwork with online forms and tracking systems reduces errors, eliminates the need for physical visits and allows applicants and staff to monitor the status of requests in real time.

- 🔄 **Reduce manual dependencies between departments**  
 Processes often get delayed when one department waits on another to complete a task. Introducing parallel workflows or automated handoffs can significantly decrease bottlenecks.

- 📊 **Monitor friction scores periodically to track improvements**  
 Regularly measuring the friction score for each process helps identify areas that need attention, track the impact of changes, and ensure that the system continues to become more efficient over time.
""")

st.info("This tool (MVP) helps administrators detect bottlenecks early, understand which processes cause the most delays or frustration, and implement targeted improvements.")


st.write("---")
if not df.empty:
    csv = df.to_csv(index=False)
    st.download_button("Export analysis as CSV", data=csv, file_name="bfr_analysis.csv", mime="text/csv")

st.caption("Built with Streamlit | Google Sheets | Looker Studio | Gemini")
st.success("✅ Thank you for using the Bureaucracy Friction Radar!")
st.write("Developed by Kanak Gupta, 2026")