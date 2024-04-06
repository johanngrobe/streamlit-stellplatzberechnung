import streamlit as st

def kontakt():
    st.write("Kontaktieren Sie uns gerne für einen Mobilitätscheck oder -Konzept für Ihre Immobillie.")
    col1, col2 = st.columns(2)
    with col1:
        st.link_button(url="https://outlook.office365.com/owa/calendar/Kennenlernen@namowo.de/bookings/", label="Termin vereinbaren", type="primary")
    with col2:
        st.link_button(url="mailto:info@namowo.de", label="E-Mail senden", type="primary")

def stadt_todo():
    st.error("Steht demnächst zur Verfügung. Bitte kontaktieren Sie uns für eine individuelle Beratung.")
    kontakt()

def stadt_fehlt(stadt:str):
    st.error(f"{stadt} ist noch nicht implementiert. Kontaktieren Sie uns gerne für eine Implementierung.")

    st.link_button(url=f"mailto:standortcheck@namowo.de?subject=Neue%20Stadt&body=Liebes%20namowo-Team%2C%0A%0Aich%20w%C3%BCrde%20mich%20freuen%2C%20wenn%20Sie%20{stadt}%20in%20ihren%20Standortcheck%20implementieren.%0A%0AMit%20freundlichen%20Gr%C3%BC%C3%9Fen", label="E-Mail senden", type="primary")