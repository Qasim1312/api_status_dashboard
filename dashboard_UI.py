import streamlit as st
import pandas as pd
import os
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dashboard_logic import fetch_website_status, save_to_csv
import time

# Set page configuration
st.set_page_config(page_title="Algozen Backtesting Service Dashboard", page_icon="🏂", layout="wide", initial_sidebar_state="expanded")

# Initialize session state for history, first load, and environment selection
if 'history' not in st.session_state:
    st.session_state['history'] = []
if 'first_load' not in st.session_state:
    st.session_state['first_load'] = True
if 'environment' not in st.session_state:
    st.session_state['environment'] = 'Dev'  # Default to Dev
if 'previous_environment' not in st.session_state:
    st.session_state['previous_environment'] = 'Dev'
if 'last_refresh_time' not in st.session_state:
    st.session_state['last_refresh_time'] = time.time()

# Function to initialize the dashboard title
def initialize_dashboard():
    st.session_state['initialized'] = True
    st.markdown("<h1 style='text-align: center;'>🏂 Algozen Backtesting Service Dashboard</h1>", unsafe_allow_html=True)

# Call the initialize_dashboard function to display the title
initialize_dashboard()

# Dropdown for selecting environment
environment = st.selectbox('Select Environment', ['Dev', 'Staging', 'Prod'])
st.session_state['environment'] = environment

# Clear session state and displayed data if environment changes
if st.session_state['environment'] != st.session_state['previous_environment']:
    st.session_state['history'] = []
    st.session_state['first_load'] = True
    st.session_state['previous_environment'] = st.session_state['environment']
    st.experimental_rerun()

# URLs based on environment
urls = {
    'Dev': [
        {"url": "http://dev.algozen.io/api/v2/backtest/backtest", "pass_method": "200 OK", "service_name": "Backtest"},
        {"url": "https://dev.algozen.io/api/v2/backtest/flow", "pass_method": "200 OK", "service_name": "Flow"},
        {"url": "https://dev.algozen.io/canvas", "pass_method": "200 OK", "service_name": "Canvas"},
        {"url": "https://dev.algozen.io/dashboard", "pass_method": "200 OK", "service_name": "Dashboard"},
        {"url": "https://dev.algozen.io/algo_view", "pass_method": "200 OK", "service_name": "AlgoView"},
        {"url": "https://dev.algozen.io/logicboard", "pass_method": "200 OK", "service_name": "LogicBoard"},
    ],
    'Staging': [
        {"url": "https://staging.algozen.io/canvas", "pass_method": "200 OK", "service_name": "Canvas"},
        {"url": "https://staging.algozen.io/dashboard", "pass_method": "200 OK", "service_name": "Dashboard"},
        {"url": "https://staging.algozen.io/algo_view", "pass_method": "200 OK", "service_name": "AlgoView"},
        {"url": "https://staging.algozen.io/logicboard", "pass_method": "200 OK", "service_name": "LogicBoard"},
    ],
    'Prod': [
        {"url": "https://algozen.io/canvas", "pass_method": "200 OK", "service_name": "Canvas"},
        {"url": "https://algozen.io/dashboard", "pass_method": "200 OK", "service_name": "Dashboard"},
        {"url": "https://algozen.io/algo_view", "pass_method": "200 OK", "service_name": "AlgoView"},
        {"url": "https://algozen.io/logicboard", "pass_method": "200 OK", "service_name": "LogicBoard"},
    ]
}[st.session_state['environment']]

# Determine the appropriate CSV file path based on the environment
CSV_FILE_PATH = f'website_status_{st.session_state["environment"].lower()}.csv'

# Check if 5 minutes have passed since the last refresh
current_time = time.time()
if current_time - st.session_state['last_refresh_time'] >= 300 or st.session_state['first_load']:
    st.session_state['last_refresh_time'] = current_time
    st.session_state['first_load'] = False

    def display_status_tables():
        # Add custom CSS for table styling
        st.markdown("""
            <style>
            .status-table {
                width: 100%;
                border-collapse: collapse;
            }
            .status-table th, .status-table td {
                border: 1px solid #ddd;
                padding: 8px;
            }
            .status-table th {
                background-color: #f2f2f2;
                text-align: left;
            }
            .status-table tr:nth-child(even) {
                background-color: #f9f9f9;
            }
            .status-table tr:hover {
                background-color: #ddd;
            }
            .status-table .normal {
                color: black;
            }
            .status-table .error {
                color: black;
            }
            .status-table .icon {
                margin-left: 10px;
            }
            </style>
        """, unsafe_allow_html=True)

        if os.path.exists(CSV_FILE_PATH):
            df = pd.read_csv(CSV_FILE_PATH)
            for service_name in df["Service Name"].unique():
                st.subheader(f"{service_name} Status")
                latest_status = df[df["Service Name"] == service_name].tail(1)
                latest_status["Uptime/Downtime"] = latest_status["Uptime/Downtime"].apply(lambda x: "normal" if x == 1 else "error")
                latest_status["Pass/Fail"] = latest_status["Pass/Fail"].apply(lambda x: "normal" if x == 1 else "error")
                latest_status["Latency (ms)"] = latest_status["Latency (ms)"].apply(lambda x: "error" if pd.isnull(x) else x)
                # Convert the DataFrame to HTML with custom formatting
                html_table = latest_status.to_html(classes='status-table', escape=False, index=False)
                # Replace "normal" and "error" with custom HTML
                html_table = html_table.replace("normal", "<span class='normal'>normal<span class='icon'>✅</span></span>")
                html_table = html_table.replace("error", "<span class='error'>error<span class='icon'>❌</span></span>")
                st.markdown(html_table, unsafe_allow_html=True)

                with st.expander("Show History"):
                    history_df = df[df["Service Name"] == service_name].tail(100).sort_values(by="Last Check Time", ascending=False)
                    history_df["Uptime/Downtime"] = history_df["Uptime/Downtime"].apply(lambda x: "normal" if x == 1 else "error")
                    history_df["Pass/Fail"] = history_df["Pass/Fail"].apply(lambda x: "normal" if x == 1 else "error")
                    history_df["Latency (ms)"] = history_df["Latency (ms)"].apply(lambda x: "error" if pd.isnull(x) else x)
                    # Convert the DataFrame to HTML with custom formatting
                    history_html_table = history_df.to_html(classes='status-table', escape=False, index=False)
                    # Replace "normal" and "error" with custom HTML
                    history_html_table = history_html_table.replace("normal", "<span class='normal'>normal<span class='icon'>✅</span></span>")
                    history_html_table = history_html_table.replace("error", "<span class='error'>error<span class='icon'>❌</span></span>")
                    st.markdown(history_html_table, unsafe_allow_html=True)

                with st.expander("Show Scatter Plots"):
                    plot_scatter(df, service_name)

    def plot_scatter(df, service_name):
        history_df = df[df["Service Name"] == service_name]
        history_df["Uptime/Downtime"] = history_df["Uptime/Downtime"].apply(lambda x: "normal" if x == 1 else "error")
        history_df["Pass/Fail"] = history_df["Pass/Fail"].apply(lambda x: "normal" if x == 1 else "error")
        history_df["Latency (ms)"] = history_df["Latency (ms)"].apply(lambda x: "error" if pd.isnull(x) else x)

        fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.1, subplot_titles=("Uptime/Downtime", "Pass/Fail", "Latency"))

        # Uptime/Downtime scatter plot
        fig.add_trace(go.Scatter(x=history_df["Last Check Time"], y=history_df["Uptime/Downtime"].apply(lambda x: 1 if x == "normal" else 0), mode='markers', name='Uptime/Downtime'), row=1, col=1)
        # Pass/Fail scatter plot
        fig.add_trace(go.Scatter(x=history_df["Last Check Time"], y=history_df["Pass/Fail"].apply(lambda x: 1 if x == "normal" else 0), mode='markers', name='Pass/Fail'), row=2, col=1)

        # Latency scatter plot
        fig.add_trace(go.Scatter(x=history_df["Last Check Time"], y=history_df["Latency (ms)"].apply(lambda x: x if x != "error" else None), mode='markers', name='Latency'), row=3, col=1)

        # Update layout
        fig.update_layout(height=800, title_text=f"{service_name} Status Scatter Plots", showlegend=False)
        fig.update_xaxes(title_text="Time", row=3, col=1)
        fig.update_yaxes(title_text="Uptime / Downtime", row=1, col=1)
        fig.update_yaxes(title_text="Pass /  Fail", row=2, col=1)
        fig.update_yaxes(title_text="Latency (ms)", row=3, col=1)

        # Display the plots
        st.plotly_chart(fig, use_container_width=True)

    def update_dashboard():
        st.markdown("<hr style='border-top: 2px solid black;'>", unsafe_allow_html=True)
        status_data = fetch_website_status(urls)
        st.session_state['history'].append(status_data)
        save_to_csv(status_data, CSV_FILE_PATH)
        display_status_tables()

    # Perform the update
    update_dashboard()
else:
    def display_status_tables():
        if os.path.exists(CSV_FILE_PATH):
            df = pd.read_csv(CSV_FILE_PATH)
            for service_name in df["Service Name"].unique():
                st.subheader(f"{service_name} Status")
                latest_status = df[df["Service Name"] == service_name].tail(1)
                latest_status["Uptime/Downtime"] = latest_status["Uptime/Downtime"].apply(lambda x: "normal" if x == 1 else "error")
                latest_status["Pass/Fail"] = latest_status["Pass/Fail"].apply(lambda x: "normal" if x == 1 else "error")
                latest_status["Latency (ms)"] = latest_status["Latency (ms)"].apply(lambda x: "error" if pd.isnull(x) else x)
                # Convert the DataFrame to HTML with custom formatting
                html_table = latest_status.to_html(classes='status-table', escape=False, index=False)
                # Replace "normal" and "error" with custom HTML
                html_table = html_table.replace("normal", "<span class='normal'>normal<span class='icon'>✅</span></span>")
                html_table = html_table.replace("error", "<span class='error'>error<span class='icon'>❌</span></span>")
                st.markdown(html_table, unsafe_allow_html=True)

                with st.expander("Show History"):
                    history_df = df[df["Service Name"] == service_name].tail(100).sort_values(by="Last Check Time", ascending=False)
                    history_df["Uptime/Downtime"] = history_df["Uptime/Downtime"].apply(lambda x: "normal" if x == 1 else "error")
                    history_df["Pass/Fail"] = history_df["Pass/Fail"].apply(lambda x: "normal" if x == 1 else "error")
                    history_df["Latency (ms)"] = history_df["Latency (ms)"].apply(lambda x: "error" if pd.isnull(x) else x)
                    # Convert the DataFrame to HTML with custom formatting
                    history_html_table = history_df.to_html(classes='status-table', escape=False, index=False)
                    # Replace "normal" and "error" with custom HTML
                    history_html_table = history_html_table.replace("normal", "<span class='normal'>normal<span class='icon'>✅</span></span>")
                    history_html_table = history_html_table.replace("error", "<span class='error'>error<span class='icon'>❌</span></span>")
                    st.markdown(history_html_table, unsafe_allow_html=True)

                with st.expander("Show Scatter Plots"):
                    plot_scatter(df, service_name)

    def plot_scatter(df, service_name):
        history_df = df[df["Service Name"] == service_name]
        history_df["Uptime/Downtime"] = history_df["Uptime/Downtime"].apply(lambda x: "normal" if x == 1 else "error")
        history_df["Pass/Fail"] = history_df["Pass/Fail"].apply(lambda x: "normal" if x == 1 else "error")
        history_df["Latency (ms)"] = history_df["Latency (ms)"].apply(lambda x: "error" if pd.isnull(x) else x)

        fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.1, subplot_titles=("Uptime/Downtime", "Pass/Fail", "Latency"))

        # Uptime/Downtime scatter plot
        fig.add_trace(go.Scatter(x=history_df["Last Check Time"], y=history_df["Uptime/Downtime"].apply(lambda x: 1 if x == "normal" else 0), mode='markers', name='Uptime/Downtime'), row=1, col=1)
        # Pass/Fail scatter plot
        fig.add_trace(go.Scatter(x=history_df["Last Check Time"], y=history_df["Pass/Fail"].apply(lambda x: 1 if x == "normal" else 0), mode='markers', name='Pass/Fail'), row=2, col=1)

        # Latency scatter plot
        fig.add_trace(go.Scatter(x=history_df["Last Check Time"], y=history_df["Latency (ms)"].apply(lambda x: x if x != "error" else None), mode='markers', name='Latency'), row=3, col=1)

        # Update layout
        fig.update_layout(height=800, title_text=f"{service_name} Status Scatter Plots", showlegend=False)
        fig.update_xaxes(title_text="Time", row=3, col=1)
        fig.update_yaxes(title_text="Uptime / Downtime", row=1, col=1)
        fig.update_yaxes(title_text="Pass /  Fail", row=2, col=1)
        fig.update_yaxes(title_text="Latency (ms)", row=3, col=1)

        # Display the plots
        st.plotly_chart(fig, use_container_width=True)

    # Display the current status and history
    display_status_tables()
