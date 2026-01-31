# Bureaucracy Friction Radar (BFR)

## Project Overview
Bureaucracy Friction Radar is a simple web-based tool that helps identify delays and inefficiencies in administrative and bureaucratic processes using data analysis and visualization.

## Problem Statement
Many government and institutional processes involve long waiting times, multiple steps and repeated visits. These issues cause frustration and waste time, but are rarely measured in a structured way.

## Solution
This project calculates a **Friction Score** for each process based on:
- Waiting time  
- Number of steps  
- Repeat visits  

Processes with higher scores indicate higher bureaucratic friction and need improvement.

## Technologies Used
- **Python**
- **Streamlit** (web application)
- **Pandas** (data handling)
- **Matplotlib** (charts & graphs)
- **Google Sheets / Looker Studio** (optional dashboards)
- **Gemini** (ideation and content support)

---

## How It Works
1. Upload a CSV or Excel file with process data.
2. The app automatically maps required columns.
3. Friction scores are calculated and visualized.
4. Results can be downloaded as a CSV.
5. If no file is uploaded, a demo dataset is loaded.

---

## How to Run
```bash
pip install -r requirements.txt
streamlit run app.py

