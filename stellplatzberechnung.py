import streamlit as st
import pandas as pd
import numpy as np
import geopandas as gpd
from geopandas.tools import sjoin, geocode
import plotly.express as px
from src.mainz import *


st.title('Stellplatzberechnung')

stadt = st.selectbox(label='Stadt', options=[None, 'Mainz'])

if stadt:
    if stadt == "Mainz":
        with st.form("Eingabe von relevanten Daten"):

            addresse = st.text_input(label="Adresse")

            # Wohnungen
            wohnungen = st.text_input(label="Wohnungsgrößen in qm getrennt durch Komma")

            # Gewerbefläche
            gewerbeflaeche = st.number_input(label="Gewerbefläche in qm")

            # Gewerbebesucherverkehr
            gewerbe_besucherverkehr = st.checkbox(label="Erhöhter Gewerbebesucherverkehr")

            f_gewerbe_pkw = st.number_input(label="Faktor Stellplatz pro qm Gewerbefläche")

            quali_moko = st.checkbox(label="qualifiziertes Mobilitätskonzept")
            
            # Every form must have a submit button.
            submitted = st.form_submit_button("Submit")
            if submitted:
                wohnungen = wohnungen.split(',')
                wohnungen = [float(i) for i in wohnungen]
                wohnungen = pd.DataFrame(wohnungen, columns=['Größe'])

                # Berechnung
                pkw, fahrrad, wohnung = mainz(wohnungen, gewerbeflaeche, gewerbe_besucherverkehr, f_gewerbe_pkw)

                # Ausgabe
                standard, moko = st.tabs(['Stellplatzberechnung', 'Mit Mobilitätskonzept'])

                with standard:
                    st.write(f"Stellplatzberechnung für {addresse}")
                    st.write("PKW-Stellplätze")
                    st.dataframe(pkw)

                    stpl_nach_gewerbefaktor = pd.Series(range(30,41), name='Faktor qm Gewerbefläche').to_frame()

                    stpl_nach_gewerbefaktor['Stlpl'] = gewerbeflaeche/stpl_nach_gewerbefaktor['Faktor qm Gewerbefläche']

                    stpl_nach_gewerbefaktor['Stellplätze_gerundet'] = stpl_nach_gewerbefaktor['Stlpl'].apply(lambda x: round_half_up(x))

                    fig = px.line(stpl_nach_gewerbefaktor, x='Faktor qm Gewerbefläche', y='Stellplätze_gerundet')

                    st.plotly_chart(fig, theme="streamlit", use_container_width=True)

                    st.write("Fahrradstellplätze je Wohnung")
                    st.dataframe(wohnung)
                    st.write("Fahrradstellplätze Gesamt")
                    st.dataframe(fahrrad)

                with moko:

                    oev_bonus = gpd.read_file('data/mainz_oev_bonus.geojson')

                    origin = geocode(addresse, provider='nominatim', user_agent='autogis_xx', timeout=4)

                    reduzierung_oev_bonus = sjoin(oev_bonus, origin, how='right')['Reduzierung'].iloc[0]
                    st.write(f"Reduzierung durch ÖV-Bonus: {reduzierung_oev_bonus} %")

                    reduzierung_moko = 10
                    if quali_moko:
                        reduzierung_moko = 30

                    st.write(f"Reduzierung durch Mobilitätskonzept: {reduzierung_moko} %")

                    ergebnis_moko = mainz_moko(pkw, reduzierung_oev_bonus/100, reduzierung_moko/100)

                    st.dataframe(ergebnis_moko)
