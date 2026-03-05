import sys
import traceback
import logging
logging.basicConfig(filename='app_errors.log', level=logging.DEBUG)

try:
     
except Exception as e:
    logging.error(traceback.format_exc())
    import streamlit as st
    st.error(f"App crashed: {e}")
    st.code(traceback.format_exc())
