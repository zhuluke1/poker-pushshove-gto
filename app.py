# app.py
import streamlit as st
import pandas as pd
from gto_calculator import calculate_push_fold_gto

# Set page title and layout
st.set_page_config(page_title="Poker GTO Push/Fold Calculator", layout="wide")
st.title("Poker GTO Push/Fold Calculator")
st.markdown("""
This tool calculates Game Theory Optimal (GTO) push/fold ranges for heads-up Texas Hold'em.
Select the effective stack size and position to view the recommended strategy.
""")

# Input widgets
col1, col2 = st.columns(2)
with col1:
    stack_size = st.slider("Effective Stack Size (BB)", min_value=1.0, max_value=20.0, value=10.0, step=0.5)
with col2:
    position = st.selectbox("Position", options=["Small Blind (SB)", "Big Blind (BB)"], index=0)

# Calculate GTO ranges
sb_pos = position == "Small Blind (SB)"
with st.spinner("Calculating GTO ranges..."):
    sb_strategy, bb_strategy = calculate_push_fold_gto(stack_size)

# Prepare DataFrames for display
df_sb = pd.DataFrame.from_dict(sb_strategy, orient='index', columns=['Push Frequency'])
df_sb = df_sb.sort_values(by='Push Frequency', ascending=False)
df_bb = pd.DataFrame.from_dict(bb_strategy, orient='index', columns=['Call Frequency'])
df_bb = df_bb.sort_values(by='Call Frequency', ascending=False)

# Display results
st.subheader(f"SB Push GTO Strategy for {stack_size} BB")
st.dataframe(df_sb, height=400)
st.download_button(
    label="Download SB Push Strategy as CSV",
    data=df_sb.to_csv(index=True),
    file_name=f"sb_push_strategy_{stack_size}bb.csv",
    mime="text/csv"
)

st.subheader(f"BB Call GTO Strategy for {stack_size} BB")
st.dataframe(df_bb, height=400)
st.download_button(
    label="Download BB Call Strategy as CSV",
    data=df_bb.to_csv(index=True),
    file_name=f"bb_call_strategy_{stack_size}bb.csv",
    mime="text/csv"
)

# Add some additional information
st.markdown("### Notes")
st.markdown("""
- **Push Frequency**: A value of 1.0 means always push, 0.0 means never push, and values in between indicate a mixed strategy.
- **Call Frequency**: A value of 1.0 means always call, 0.0 means never call.
- The ranges are computed using a precomputed equity table for efficiency.
- For more accurate results, consider increasing the Monte Carlo iterations in `hand_equity.py` and recomputing the equity table.
""")