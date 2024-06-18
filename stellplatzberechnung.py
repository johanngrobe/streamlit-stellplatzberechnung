import streamlit as st
import pandas as pd
import numpy as np
import geopandas as gpd
from geopandas.tools import sjoin, geocode
# import plotly.express as px
import streamlit as st
from streamlit_folium import st_folium
import folium
import streamlit as st
import smtplib
import os
import datetime
import random
import locale
from email_validator import validate_email, EmailNotValidError
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import src.smtp as smtp
from src.mainz import *
from src.origin import geocode_address
from src.kosten import kostenberechnung, ersparnis
from src.kontakt import kontakt, stadt_todo, stadt_fehlt

locale.setlocale(locale.LC_ALL, 'de_DE')


st.title('namowo Standortcheck (Alpha)')
st.markdown('### Berechnen Sie den Stellplatzbedarf für Ihre Immobilie')

col1, col2 = st.columns([0.8, 0.2])
with col1:
    st.write('Dies ist eine Light-Version. Haben Sie Interesse an einer Vollversion des Standortschecks mit detaillierten Stellplatzberechnungen? Kontaktieren Sie uns!')
with col2:
    st.link_button(url=f"mailto:standortcheck@namowo.de?subject=Erweiterte%20Version%20des%20Standortchecks&body=Liebes%20namowo-Team%2C%0A%0Aich%20habe%20Interesse%20an%20einer%20erweiterten%20Version%20des%20Standortchecks.%0A%0AMit%20freundlichen%20Gr%C3%BC%C3%9Fen", label="E-Mail senden", type="primary")

## Load secrets.toml variables
options = os.getenv(smtp.smtp_server)
server = os.getenv(smtp.smtp_server)
port = os.getenv(smtp.smtp_port)
username = os.getenv(smtp.smtp_username)
password = os.getenv(smtp.smtp_password)
recipient = os.getenv(smtp.recipient_email)

if 'submit_standort' not in st.session_state:
    st.session_state['submit_standort'] = False

if 'submit_daten' not in st.session_state:
    st.session_state['submit_daten'] = False

if 'submit_anteiL_stpl' not in st.session_state:
    st.session_state['submit_anteiL_stpl'] = False

if 'addresse' not in st.session_state:
    st.session_state['addresse'] = None

if 'stadt' not in st.session_state:
    st.session_state['stadt'] = None

with st.form("Standort ihrer Immobilie"):
    st.write("### Bitte geben Sie den Standort Ihrer Immobilie an")
    st.write("Hinweis: Derzeit funktionieren nur Adressen in Mainz.")
    col1, col2 = st.columns([0.7, 0.3])
    with col1:
        strasse = st.text_input(label="Straße*", placeholder="Straße",)
    with col2:
        hausnummer = st.text_input(label="Hausnummer", placeholder="Hausnummer")
    col1, col2 = st.columns([0.3, 0.7])
    with col1:
        plz = st.text_input(label="PLZ*", max_chars=5, placeholder="PLZ")
    with col2:
        stadt = st.text_input(label="Ort*", placeholder="Ort")
    st.markdown('<p style="font-size: 13px;">*Pflichtfelder</p>', unsafe_allow_html=True) # indication to user that both fields must be filled
    st.session_state.submit_standort = st.form_submit_button("Standort bestätigen")

if st.session_state.submit_standort:
    addresse = f"{strasse} {hausnummer}, {plz} {stadt}"
    try:
        st.session_state.addresse = geocode_address(addresse)
        # st.write("Adresse gefunden: ", addresse)
    except:
        st.error("Adresse konnte nicht gefunden werden. Bitte überprüfen Sie die Eingabe oder wählen Sie den Standort Ihrer Immobilie über die Karte aus.")

        with st.form("Ortsangabe über Karte"):
            DEFAULT_LATITUDE = 50.001086
            DEFAULT_LONGITUDE = 8.258680

            m = folium.Map(location=[DEFAULT_LATITUDE, DEFAULT_LONGITUDE], zoom_start=10)
            f_map = st_folium(m, width=725)
            if f_map.get("last_clicked"):
                selected_latitude = f_map["last_clicked"]["lat"]
                selected_longitude = f_map["last_clicked"]["lng"]
            
            submit_karte = st.form_submit_button("Eingabe bestätigen")

    valide_staedte = gpd.read_file('data/valide_staedte.geojson')
    stadt_check = gpd.sjoin(valide_staedte, st.session_state.addresse, how="inner", op='contains')

    if  stadt_check.empty:
        st.session_state.stadt = None
        stadt_fehlt(stadt)
        # with st.container(border=True):
        #     email = st.text_input("**Ihre E-Mail-Addresse***", value=st.session_state.get('email', ''), key='email') # input widget for contact email
        #     message = st.text_area("**Ihre Nachricht***", value=st.session_state.get('message', ''), key='message') # input widget for message

        #     st.markdown('<p style="font-size: 13px;">*Pflichtfelder</p>', unsafe_allow_html=True) # indication to user that both fields must be filled

        #     if st.button("Senden", type="primary"):
        #         if not email or not message:
        #             st.error("Bitte füllen Sie alle Felder aus.") # error for any blank field
        #         else:
        #             try:
        #                 # Robust email validation
        #                 valid = validate_email(email, check_deliverability=True)
        #                 # Email configuration - **IMPORTANT**: for security these details should be present in the "Secrets" section of Streamlit

        #                 # Create an SMTP connection
        #                 server = smtplib.SMTP(server, port)
        #                 server.starttls()
        #                 server.login(username, password)

        #                 # Compose the email message
        #                 subject = "Neue Stadt für das Stellplatztool" # subject of the email you will receive upon contact.
        #                 body = f"Email: {email}\nMessage: {message}"
        #                 msg = MIMEMultipart()
        #                 msg['From'] = username
        #                 msg['To'] = recipient
        #                 msg['Subject'] = subject
        #                 msg.attach(MIMEText(body, 'plain'))

        #                 # Send the email
        #                 server.sendmail(username, recipient, msg.as_string())

        #                 # Send the confirmation email to the message sender # If you do not want to send a confirmation email leave this section commented
        #                 current_datetime = datetime.datetime.now()
        #                 formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
        #                 confirmation_subject = f"Bestätigung der Benachrichtgung ({formatted_datetime})"
        #                 confirmation_body = f"Vielen Dank für ihre Interesse an unserem Stellplatztool. \n\nYour message: {message}"
        #                 confirmation_msg = MIMEMultipart()
        #                 confirmation_msg['From'] = username
        #                 confirmation_msg['To'] = email  # Use the sender's email address here
        #                 confirmation_msg['Subject'] = confirmation_subject
        #                 confirmation_msg.attach(MIMEText(confirmation_body, 'plain'))
        #                 server.sendmail(username, email, confirmation_msg.as_string())

        #                 # Close the SMTP server connection
        #                 server.quit()

        #                 st.success("Erfolgreich versendet") # Success message to the user.
                        
        #                 #### NOTE FOR DEVELOPERS: UPON DEPLOYMENT DELETE THE SECTION BELOW ####
        #                 # st.info("""This would have been a message sent successfully!  
        #                 # For more information on activating the contact form, please check the [documentation](https://github.com/jlnetosci/streamlit-contact-form).""") # Please delete this info box if you have the contact form setup correctly.

        #                 # time.sleep(3)
        #                 # streamlit_js_eval(js_expressions="parent.window.location.reload()")


        #             except EmailNotValidError as e:
        #                 st.error(f"E-Mail Adresse nicht korrekt: {e}") # error in case any of the email validation checks have not passed
    else:
        st.session_state.stadt = stadt_check

if st.session_state.stadt is not None:
    # st.dataframe(st.session_state.stadt[['name', 'lage_bonus']])
    if st.session_state.stadt.name.iloc[0] == "Mainz":
        with st.form("Eingabe von relevanten Daten"):
            st.write("### Bitte machen Sie weitere Angaben zur Immobilie")
            # Wohnungen
            # wohnungen = st.text_input(label="Wohnungsgrößen in qm getrennt durch Komma")
            col1, col2 = st.columns(2)
            with col1:
                anzahl_wohnungen = st.number_input(label="Anzahl der Wohnungen", value=0, min_value=0, step=1, placeholder="")
            with col2:
                # Gewerbefläche
                gewerbeflaeche = st.number_input(label="Gewerbefläche in m\u00b2", value=0, min_value=0,step=1, placeholder="")

            input_unterirdische_stpl = st.number_input(label="Anteil unterirdischer Stellplätze in % (z. B. Tiefgarage)", value=50, min_value=0, max_value=100, step=1)

            # Gewerbebesucherverkehr
            # gewerbe_besucherverkehr = st.checkbox(label="Erhöhter Gewerbebesucherverkehr")
            gewerbe_besucherverkehr = False

            # f_gewerbe_pkw = st.number_input(label="Faktor Stellplatz pro qm Gewerbefläche")
            f_gewerbe_pkw = 35

            # quali_moko = st.checkbox(label="qualifiziertes Mobilitätskonzept")
            
            # Every form must have a submit button.
            st.session_state.submit_daten = st.form_submit_button("Eingabe bestätigen")

            
        if st.session_state.submit_daten:

            # wohnungen = wohnungen.split(',')
            # wohnungen = [float(i) for i in wohnungen]
            wohnungen = random.sample(range(50, 100), anzahl_wohnungen)
            wohnungen = pd.DataFrame(wohnungen, columns=['Größe'])
            try:
            # Berechnung
                pkw, fahrrad, wohnung = mainz(wohnungen, gewerbeflaeche, gewerbe_besucherverkehr, f_gewerbe_pkw)
            except:
                st.error("Fehler bei Stellplatzberechnung")                
            # st.dataframe(pkw)
            pkw_nach_satzung = int(pkw.T['Gesamt'][1])
            st.markdown(f"#### Pkw-Stellplätze gemäß Stellplatzsatzung: {pkw_nach_satzung}")

            st.write("### Mögliche Ersparnisse durch namowo")
            
            try:
                kosten_gesamt = kostenberechnung(pkw_nach_satzung, input_unterirdische_stpl)

                oev_bonus = st.session_state.stadt['lage_bonus'].iloc[0] /100

                unquali_moko = 0.1
                quali_moko = 0.3

                ergebnis_oev_bonus = mainz_moko(pkw, oev_bonus, 0)
                # st.dataframe(ergebnis_oev_bonus)
                pkw_oev_bonus = ergebnis_oev_bonus.iloc[0]
                # st.write(pkw_oev_bonus)
                einsparung_oev_bonus = pkw_nach_satzung - pkw_oev_bonus
                einsparung_prozent_oev_bonus = einsparung_oev_bonus / pkw_nach_satzung * 100

                kosten_oev_bonus = kostenberechnung(pkw_oev_bonus, input_unterirdische_stpl)
                ersparnis_oev_bonus, ersparing_oev_bonus_prozent = ersparnis(kosten_gesamt, kosten_oev_bonus)
                
                ergebnis_unquali_moko = mainz_moko(pkw, oev_bonus, unquali_moko)
                pkw_unquali_moko = ergebnis_unquali_moko.iloc[0]
                einsparung_unquali_moko = pkw_nach_satzung - pkw_unquali_moko
                einsparung_prozent_unquali_moko = einsparung_unquali_moko / pkw_nach_satzung * 100

                kosten_unquali_moko = kostenberechnung(pkw_unquali_moko, input_unterirdische_stpl)
                ersparnis_unquali_moko = kosten_gesamt - kosten_unquali_moko

                ergebnis_quali_moko = mainz_moko(pkw, oev_bonus, quali_moko)
                pkw_quali_moko = ergebnis_quali_moko.iloc[0]
                einsparung_quali_moko = pkw_nach_satzung - pkw_quali_moko
                einsparung_prozent_quali_moko = einsparung_quali_moko / pkw_nach_satzung * 100
                kosten_quali_moko = kostenberechnung(pkw_quali_moko, input_unterirdische_stpl)
                ersparnis_quali_moko, ersparnis_quali_moko_prozent = ersparnis(kosten_gesamt, kosten_quali_moko)


                st.markdown(f"""
                        |                                                        | Einsparung in €*       | eingesparte Pkw-Stellplätze|
                        |--------------------------------------------------------|:----------------------:|:--------------------------:|
                        |Mit ÖV-Bonus nach Stellplatzsatzung                     |{f"{ersparnis_oev_bonus:n}"}    |   {f"{einsparung_oev_bonus:n}"}|
                        |Mobilitätscheck<br>(Unqualifiziertes Mobilitätskonzept) | {f"{ersparnis_unquali_moko:n}"} | {f"{einsparung_unquali_moko:n}"}
                        |Qualifiziertes Mobilitätskonzept                        | {f"{ersparnis_quali_moko:n}"}| {f"{einsparung_quali_moko:n}"}
                        """, unsafe_allow_html=True)
                st.write(r"$\textsf{\footnotesize * Annahme: Kosten pro unterirdischer Stellplatz 47.000 €, oberirdischer Stellplatz 3.300 €}$")

                kontakt()

                st.write("Bitte beachten Sie, dass die berechnete Ersparnis nur eine Schätzung ist und keine rechtliche Verbindlichkeit darstellt.")
            except:
                st.error("Bitte machen Sie Angaben zur Immobilie.")

                # Ausgabe
                # standard, moko = st.tabs(['Stellplatzberechnung', 'Mit Mobilitätskonzept'])

                # with standard:
                #     # st.write(f"Stellplatzberechnung für {addresse}")
                #     st.write("PKW-Stellplätze")
                #     st.dataframe(pkw)

                    # Datailberechnung ausgeblendet
                    # stpl_nach_gewerbefaktor = pd.Series(range(30,41), name='Faktor qm Gewerbefläche').to_frame()
                    # stpl_nach_gewerbefaktor['Stlpl'] = gewerbeflaeche/stpl_nach_gewerbefaktor['Faktor qm Gewerbefläche']
                    # stpl_nach_gewerbefaktor['Stellplätze_gerundet'] = stpl_nach_gewerbefaktor['Stlpl'].apply(lambda x: round_half_up(x))
                    # fig = px.line(stpl_nach_gewerbefaktor, x='Faktor qm Gewerbefläche', y='Stellplätze_gerundet')
                    # st.plotly_chart(fig, theme="streamlit", use_container_width=True)

                    # st.write("Fahrradstellplätze je Wohnung")
                    # st.dataframe(wohnung)
                    # st.write("Fahrradstellplätze Gesamt")
                    # st.dataframe(fahrrad)

                # with moko:

                #     oev_bonus = gpd.read_file('data/mainz_oev_bonus.geojson')

                #     reduzierung_oev_bonus = sjoin(oev_bonus, st.session_state.addresse, how='right')['Reduzierung'].iloc[0]
                #     st.write(f"Reduzierung durch ÖV-Bonus: {reduzierung_oev_bonus} %")

                #     reduzierung_moko = 10
                #     if quali_moko:
                #         reduzierung_moko = 30

                #     st.write(f"Reduzierung durch Mobilitätskonzept: {reduzierung_moko} %")

                #     ergebnis_moko = mainz_moko(pkw, reduzierung_oev_bonus/100, reduzierung_moko/100)

                #     st.dataframe(ergebnis_moko)
    elif st.session_state.stadt.name.iloc[0] == "Essen":
        stadt_todo()

    elif st.session_state.stadt.name.iloc[0] == "Köln":
        stadt_todo()

    elif st.session_state.stadt.name.iloc[0] == "Frankfurt am Main":
        stadt_todo()

    elif st.session_state.stadt.name.iloc[0] == "Mönchengladbach":
        stadt_todo()

    elif st.session_state.stadt.name.iloc[0] == "Oberursel":
        stadt_todo()

    else:
        stadt_fehlt(stadt)
