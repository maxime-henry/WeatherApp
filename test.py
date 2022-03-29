import streamlit as st


name = st.text_input('Name')
if not name:
  st.warning('Please input a name.')
#   st.stop()
st.success('Thank you for inputting a name.')