# archivo: app.py
import streamlit as st
from nomina_basica import calcular_nomina

st.title("Calculadora de Nómina Mexicana")

sueldo_diario = st.number_input("Sueldo diario", min_value=0.0, value=500.0)
factor = st.number_input("Factor de integración", min_value=1.0, value=1.0452, format="%.4f")
dias = st.number_input("Días trabajados", min_value=1, max_value=31, value=15)

if st.button("Calcular"):
    resultado = calcular_nomina(sueldo_diario, factor, dias)
    st.subheader("Resultado")
    st.json(resultado)
