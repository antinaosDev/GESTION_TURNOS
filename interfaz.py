import streamlit as st 
from servidor_fb import *

st.title("Agenda de turnos")

st.text(leer_registro("login"))
