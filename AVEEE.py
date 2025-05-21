import pandas as pd
import streamlit as st
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="Work Hours & Pay Analyzer",
    page_icon="⏱️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .header-style {
        font-size: 24px;
        font-weight: bold;
        color: #2a4365;
        margin-bottom: 10px;
    }
    .date-range-box {
        background-color: #2a4365;
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .metric-box {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .highlight {
        font-size: 1.4em;
        font-weight: bold;
        color: #2a4365;
    }
    .subheader {
        font-size: 1.1em;
        color: #4a5568;
        margin-bottom: 5px;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    df = pd.read_csv('AVEEE.csv')
    df['date'] = pd.to_datetime(df['date'])
    df['hours'] = pd.to_numeric(df['hours'], errors='coerce').fillna(0)
    df['payforaverage'] = pd.to_numeric(df['payforaverage'], errors='coerce').fillna(0)
    return df

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
    st.title("⏱️ Work Hours & Pay Analyzer")
    st.markdown("Analyze your working hours and compensation across different time periods")
    
    df = load_data()
    
    # Sidebar for inputs
    with st.sidebar:
        st.header("Settings")
        selected_month = st.selectbox(
            "Select Month:",
            options=list(month_names.keys()),
            format_func=lambda x: month_names[x]
        )
        
        show_details = st.checkbox("Show daily details", value=False)
        
        if st.button("Calculate Metrics", type="primary", use_container_width=True):
            st.session_state.calculate = True
        else:
            st.session_state.calculate = False
    
    # Main content area
    if 'calculate' in st.session_state and st.session_state.calculate:
        start_date, end_date = month_ranges[selected_month]
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        
        filtered = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
        
        if not filtered.empty:
            total_hours = filtered['hours'].sum()
            total_pay = filtered['payforaverage'].sum()
            work_days = len(filtered[filtered['hours'] > 0])
            avg_hours = total_hours / work_days if work_days > 0 else 0
            avg_pay = total_pay / work_days if work_days > 0 else 0
            pay_per_hour = total_pay / total_hours if total_hours > 0 else 0
            
            # Date range box
            st.markdown(f"""
            <div class="date-range-box">
                <h2 style='color: white; margin: 0;'>📅 {month_names[selected_month]}</h2>
                <p style='color: white; margin: 0; font-size: 1.1em;'>{start_date.date()} to {end_date.date()}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Main metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("<div class='metric-box'>"
                           f"<div class='subheader'>⏳ Total Hours</div>"
                           f"<div class='highlight'>{total_hours:.2f}</div>"
                           "</div>", unsafe_allow_html=True)
                
                st.markdown("<div class='metric-box'>"
                           f"<div class='subheader'>📊 Working Days</div>"
                           f"<div class='highlight'>{work_days}</div>"
                           "</div>", unsafe_allow_html=True)
            
            with col2:
                st.markdown("<div class='metric-box'>"
                           f"<div class='subheader'>Total Pay</div>"
                           f"<div class='highlight'>{total_pay:,.2f}</div>"
                           "</div>", unsafe_allow_html=True)
                
                st.markdown("<div class='metric-box'>"
                           f"<div class='subheader'>📅 Avg Hours/Day</div>"
                           f"<div class='highlight'>{avg_hours:.2f}</div>"
                           "</div>", unsafe_allow_html=True)
            
            with col3:
                st.markdown("<div class='metric-box'>"
                           f"<div class='subheader'>Avg Pay/Day</div>"
                           f"<div class='highlight'>{avg_pay:,.2f}</div>"
                           "</div>", unsafe_allow_html=True)
                
                st.markdown("<div class='metric-box'>"
                           f"<div class='subheader'>Pay Rate/Hour</div>"
                           f"<div class='highlight'>{pay_per_hour:,.2f}</div>"
                           "</div>", unsafe_allow_html=True)
            
            # Daily details
            if show_details:
                st.subheader("Daily Breakdown")
                st.dataframe(
                    filtered[['date', 'hours', 'payforaverage']].style.format({
                        'hours': '{:.2f}',
                        'payforaverage': '{:,.2f}'
                    }).background_gradient(cmap='Blues'),
                    use_container_width=True
                )
        else:
            st.warning("No data found for the selected period.")

if __name__ == "__main__":
    main()
