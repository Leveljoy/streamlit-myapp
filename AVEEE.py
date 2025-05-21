import pandas as pd
import streamlit as st
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="Work Hours & Pay Analyzer",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .header-style {
        font-size: 24px;
        font-weight: bold;
        color: #2a4365;
        margin-bottom: 10px;
    }
    .box {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 15px;
    }
    .metric {
        font-size: 1.3em;
        font-weight: bold;
        color: #2a4365;
    }
    .subtext {
        font-size: 1em;
        color: #555;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    try:
        df = pd.read_csv('AVEEE.csv')
    except:
        df = pd.DataFrame(columns=['date', 'hours', 'payforaverage'])

    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['hours'] = pd.to_numeric(df['hours'], errors='coerce').fillna(0)
    df['payforaverage'] = pd.to_numeric(df['payforaverage'], errors='coerce').fillna(0)
    return df

def save_data(df):
    df.to_csv('AVEEE.csv', index=False, encoding='utf-8-sig')

# Month mapping
month_ranges = {
    1: ('2025-01-11', '2024-12-09'),
    2: ('2025-02-11', '2025-01-09'),
    3: ('2025-03-11', '2025-02-09'),
    4: ('2025-04-11', '2025-03-09'),
    5: ('2025-01-11', '2025-04-09'),
    6: ('2025-02-11', '2025-05-09'),
    7: ('2025-03-11', '2025-06-09'),
    8: ('2025-04-11', '2025-07-09'),
    9: ('2025-05-11', '2025-08-09'),
    10: ('2025-06-11', '2025-09-09'),
    11: ('2025-07-11', '2025-10-09'),
    12: ('2025-08-11', '2025-11-09')
}

month_names = {
    1: "January", 2: "February", 3: "March", 4: "April",
    5: "May (Jan 11 - Apr 9)", 6: "June (Feb 11 - May 9)",
    7: "July (Mar 11 - Jun 9)", 8: "August (Apr 11 - Jul 9)",
    9: "September (May 11 - Aug 9)", 10: "October (Jun 11 - Sep 9)",
    11: "November (Jul 11 - Oct 9)", 12: "December (Aug 11 - Nov 9)"
}

def main():
    st.title("Work Hours & Pay Analyzer")

    # Load data into session state
    if 'df' not in st.session_state:
        st.session_state.df = load_data()
        st.session_state.edited_data = None

    df = st.session_state.df

    with st.sidebar:
        st.header("Settings")
        selected_month = st.selectbox(
            "Select Month:",
            options=list(month_names.keys()),
            format_func=lambda x: month_names[x]
        )
        calculate_clicked = st.button("Calculate")
        save_clicked = st.button("Save")

    start_date, end_date = month_ranges[selected_month]
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Filter for selected range
    filtered = df[(df['date'] >= start_date) & (df['date'] <= end_date)].copy()

    # Editable table
    st.subheader("Work Data (Editable)")
    filtered_display = filtered.copy()
    filtered_display['date'] = filtered_display['date'].dt.strftime('%Y-%m-%d')

    edited_df = st.data_editor(
        filtered_display,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "date": "Date",
            "hours": st.column_config.NumberColumn("Hours", format="%.2f"),
            "payforaverage": st.column_config.NumberColumn("Pay", format="%.2f")
        },
        key=f"edit_{selected_month}"
    )

    # Store edited data in session state without saving yet
    if edited_df is not None:
        st.session_state.edited_data = edited_df.copy()
        st.session_state.edited_data['date'] = pd.to_datetime(st.session_state.edited_data['date'])

    if save_clicked:
        if st.session_state.edited_data is not None:
            # Remove old data for this period
            df = df[~((df['date'] >= start_date) & (df['date'] <= end_date))]
            # Add edited data
            df = pd.concat([df, st.session_state.edited_data], ignore_index=True)
            st.session_state.df = df
            save_data(df)
            st.success("Data saved successfully.")
        else:
            st.warning("No changes to save.")

    if calculate_clicked:
        if st.session_state.edited_data is not None:
            filtered = st.session_state.edited_data.copy()
        else:
            filtered = df[(df['date'] >= start_date) & (df['date'] <= end_date)].copy()

        total_hours = filtered['hours'].sum()
        total_pay = filtered['payforaverage'].sum()
        work_days = len(filtered[filtered['hours'] > 0])
        avg_hours = total_hours / work_days if work_days > 0 else 0
        avg_pay = total_pay / work_days if work_days > 0 else 0
        pay_per_hour = total_pay / total_hours if total_hours > 0 else 0

        st.markdown(f"""
        <div class='box'>
            <h3>{month_names[selected_month]}</h3>
            <p class='subtext'>{start_date.date()} to {end_date.date()}</p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"<div class='box'><div class='subtext'>Total Hours</div><div class='metric'>{total_hours:.2f}</div></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='box'><div class='subtext'>Working Days</div><div class='metric'>{work_days}</div></div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div class='box'><div class='subtext'>Total Pay</div><div class='metric'>{total_pay:.2f}</div></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='box'><div class='subtext'>Avg Hours/Day</div><div class='metric'>{avg_hours:.2f}</div></div>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"<div class='box'><div class='subtext'>Avg Pay/Day</div><div class='metric'>{avg_pay:.2f}</div></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='box'><div class='subtext'>Pay Rate per Hour</div><div class='metric'>{pay_per_hour:.2f}</div></div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
