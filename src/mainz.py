"""
Berechnet die Anzahl der Stellplätze für verschiedene Städte
Bislang implementierte Städte:
- Mainz
"""
import pandas as pd
import numpy as np
import decimal
import math

def round_half_up(n:float, decimals:int=0):
    """Bestimmt einen gerundete Zahl ab ,5 wird aufgerundet

    ARGS:
    n (float): Zahl die gerundet werden soll
    decimals (int): Nachkommastelle auf die gerundet werden soll (Default=0)
    """
    multiplier = 10**decimals
    return math.floor(n * multiplier + 0.5) / multiplier

def mainz(wohnungen: pd.DataFrame, gewerbeflaeche: int, gewerbe_besucherverkehr: bool=False, f_gewerbe_pkw: int=None, fahrrad_je_wohnung: bool=False):
    """ Berechnet den Stellplatzbedarf für Mainz
    
    Args:
        wohnungen (DataFrame): Größe der Wohnungen in qm
        gewerbeflaeche (int): Größe der Nutzfläche für Gewerbe in qm
        gewerbe_besucherverkehr (bool): erhöhter Besuchsverkehr z. B. Schalter-, Abfertigungs- oder Beratungsräume, Arztpraxen u. dergleichen (Default=False)
        fahrrad_je_wohnung (bool): Soll die Anzahl der Fahrradabstellplätze je Wohnung returned werden (Default=False)

    Returns:
        pandas DataFrames mit Stellplatzberechnung für Pkw, Fahrrad und Fahrradabstellplätze je Wohnungen
    """     
    # Informationen aus der Stellplatzsatzung vom 23.09.2023
    f_wohnen_pkw = 1 # Stellplätze pro Wohnung
    q_wohnen_pkw_besucher = 0.1 # Anteil der Stellplätze für Besucher
    f_wohnen_fahrrad = 50 # Je 50 qm ein Fahrradstellplatz
    f_wohnen_fahrrad_rest = 35 # Bei Rest für angerissene 35 qm
    q_wohnen_fahrrad_besucher = 0.2 # Anteil der Fahrradabstellplätze für Besucher
    min_wohnen_fahrrad_besucher = 2 # Mindestanzahl der Fahrradabstellplätze für Besucher von Wohnen
    f_gewerbe_fahrrad = 70 # Je 70qm Gewerbenutzfläche einen Fahrradstellplatz
    q_gewerbe_fahrrad_besucher = 0.5 # Anteil der Fahrradabstellplätze für Besucher von gewerblichen Fahrradabstellplätzen
    
    # Informationen aus der VwV
    f_gewerbe_pkw_min = 40 # Mindestzahl der Stellplätze pro 40 qm Gewerbenutzfläche
    f_gewerbe_pkw_max = 30 # Maximalanzahl der Stellplätze pro 30 qm Gewerbenutzfläche
    q_gewerbe_pkw_besucher = 0.7 # Antiel der Beusucherstellplätze für Gewerbe

    # wenn höher Besucherverkehr verliegt
    if gewerbe_besucherverkehr:
        f_gewerbe_pkw_min = 30
        f_gewerbe_pkw_max = 20
        q_gewerbe_pkw_besucher = 0.75
        f_gewerbe_fahrrad = 35
        q_gewerbe_fahrrad_besucher = 0.75    
        
    # Anazhl der Pkw-Stellplätze je Wohneinheit
    s_pkw_wohnen = len(wohnungen) * f_wohnen_pkw
    # Anzahl der Pkw-Stellplätze für Besucher
    s_pkw_wohnen_bes = s_pkw_wohnen * q_wohnen_pkw_besucher

    # Anzahl der Pkw-Stellplätze für Gewerbe
    s_pkw_gewerbe_min = gewerbeflaeche / f_gewerbe_pkw_min
    s_pkw_gewerbe_min_bes = s_pkw_gewerbe_min * q_gewerbe_pkw_besucher
    s_pkw_gewerbe_max = gewerbeflaeche / f_gewerbe_pkw_max
    s_pkw_gewerbe_max_bes = s_pkw_gewerbe_max * q_gewerbe_pkw_besucher

    # Wenn eigener Stellplatzwert für das Gewerbe definiert wird
    if f_gewerbe_pkw:
        s_pkw_gewerbe = gewerbeflaeche / f_gewerbe_pkw
        s_pkw_gewerbe_bes = s_pkw_gewerbe * q_gewerbe_pkw_besucher        


        stpl_pkw = pd.DataFrame(
            {
                "Nutzung": ['Wohnen','Gewerbe'],
                f"Stellplätze({f_gewerbe_pkw}qm/Stellplatz)": [s_pkw_wohnen,s_pkw_gewerbe],
                "davon_Besucher": [s_pkw_wohnen_bes, s_pkw_gewerbe_bes],
                f"Stellplätze_min({f_gewerbe_pkw_min}qm/Stellplatz)": [s_pkw_wohnen,s_pkw_gewerbe_min],
                "davon_Besucher_min": [s_pkw_wohnen_bes, s_pkw_gewerbe_min_bes],
                f"Stellplätze_max({f_gewerbe_pkw_max}qm/Stellplatz)": [s_pkw_wohnen,s_pkw_gewerbe_max],
                "davon_Besucher_max": [s_pkw_wohnen_bes, s_pkw_gewerbe_max_bes],
            }
        )
    else:

        stpl_pkw = pd.DataFrame(
            {
                "Nutzung": ['Wohnen','Gewerbe'],
                f"Stellplätze_min({f_gewerbe_pkw_min}qm/Stellplatz)": [s_pkw_wohnen,s_pkw_gewerbe_min],
                "davon_Besucher_min": [s_pkw_wohnen_bes, s_pkw_gewerbe_min_bes],
                f"Stellplätze_max({f_gewerbe_pkw_max}qm/Stellplatz)": [s_pkw_wohnen,s_pkw_gewerbe_max],
                "davon_Besucher_max": [s_pkw_wohnen_bes, s_pkw_gewerbe_max_bes],
            }
        )
    stpl_pkw.loc['Gesamt']= stpl_pkw.sum()
    stpl_pkw.loc['Gesamt','Nutzung'] = 'Summe'

    # Fahrradstellplätze beziehen sich auf die Wohnungen und nicht auf die Gesamtwohnfläche
    # Berechnung überarbeiten!
    wohnungen['Fahrradabstellplätze'] = wohnungen['Größe'].apply(lambda x: mainz_fahrrad(x, f_wohnen_fahrrad, f_wohnen_fahrrad_rest))
    wohnungen['Fahrradabstellplätze_Besucher'] = wohnungen['Fahrradabstellplätze'] * q_wohnen_fahrrad_besucher
    wohnungen.loc['Gesamt']= wohnungen.sum()

    if wohnungen.loc['Gesamt']['Fahrradabstellplätze_Besucher'] <= min_wohnen_fahrrad_besucher:
        wohnungen.loc['Gesamt']['Fahrradabstellplätze_Besucher'] = 2

    s_gewerbe_fahrrad = gewerbeflaeche / f_gewerbe_fahrrad
    s_gewerbe_fahrrad_bes = s_gewerbe_fahrrad * q_gewerbe_fahrrad_besucher

    s_fahrrad = wohnungen.loc['Gesamt']['Fahrradabstellplätze'] + s_gewerbe_fahrrad
    s_fahrrad_bes = wohnungen.loc['Gesamt']['Fahrradabstellplätze_Besucher'] + s_gewerbe_fahrrad_bes

    stpl_fahrrad = pd.DataFrame(
        {
            "Nutzung": ['Wohnen','Gewerbe'],
            "Stellplätze": [wohnungen.loc['Gesamt']['Fahrradabstellplätze'],s_gewerbe_fahrrad],
            "Besucher": [wohnungen.loc['Gesamt']['Fahrradabstellplätze_Besucher'], s_gewerbe_fahrrad_bes],
        }
    )
    stpl_fahrrad.loc['Gesamt']= stpl_fahrrad.sum()
    stpl_fahrrad.loc['Gesamt','Nutzung'] = 'Summe'
    
    return stpl_pkw, stpl_fahrrad, wohnungen


def mainz_moko(pkw: pd.DataFrame, öv: int, moko: int):
    """ Berechnung die Stellplatzreduzierung durch ÖV-Bonus und Mobilitätskonzept

        ARGS:
        pkw (pd.DataFrame): Stellplatzberechnung für Pkw
        öv (int): Reduzierungsquote des ÖPNV-Bonus z.B. 10, 20 oder 30 %
        moko (int): Reduzierungsquote des Mobilitätskonzepts z.B. 10 oder 30 %

        Returns DataFrame mit reduzierten Stellplätzen
    """
    pkw = pkw.drop(columns='Nutzung')
    # total = pkw.T['Gesamt'].apply(lambda x: round_half_up(x))
    total = pkw.T['Gesamt']
    total = total * (1 - öv) * (1 - moko)
    total = total.apply(lambda x: round_half_up(x))
    
    return total


def mainz_fahrrad(wohnungsgröße,f_wohnen_fahrrad ,f_wohnen_fahrrad_rest):
    """ Berechnet die Anzahl der Fahrradstellplätze pro Wohnung in Mainz
    
        ARGS:
        wohnungsgröße (float): Größe der Wohnung in qm
        f_wohnen_fahrrad (int): Anzahl der qm für ersten Fahrradstellplatz
        f_wohnen_fahrrad_rest (int): Anzahl der qm für jeden weiteren Fahrradstellplatz
    
        Return: Anzahl der Fahrradstellplätze für eine Wohnung
    """
    stpl = 1
    if wohnungsgröße > f_wohnen_fahrrad:
        wohnungsgröße -= f_wohnen_fahrrad
        stpl+= math.ceil(wohnungsgröße / f_wohnen_fahrrad_rest)
        
    return stpl