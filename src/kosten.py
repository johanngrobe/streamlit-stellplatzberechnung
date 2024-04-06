def kostenberechnung(stpl_gesamt:float, anteil_unterirdischer_stpl:int = 50, preis_unterirdischer_stpl:int=47000, preis_oberirdischer_stpl:int=3300):
    """
    Berechnung der Kosten für Stellplätze

    ARGS:
    anteil_unterirdischer_stpl (int): Anteil der unterirdischen Stellplätze in Prozent
    preis_unterirdischer_stpl (int): Preis pro unterirdischem Stellplatz
    preis_oberirdischer_stpl (int): Preis pro oberirdischem Stellplatz

    RETURNS:
    kosten (int): Kosten für Stellplätze
    """
    unterirdische_stpl = anteil_unterirdischer_stpl / 100
    oberirdische_stpl = 1 - unterirdische_stpl

    kosten = stpl_gesamt * (unterirdische_stpl * preis_unterirdischer_stpl + oberirdische_stpl * preis_oberirdischer_stpl)

    return kosten

def ersparnis(kosten_max:float, kosten_min:float):
    """
    Berechnung der Kostenersparnis

    ARGS:
    kosten_max (float): Maximale Kosten
    kosten_min (float): Minimale Kosten

    RETURNS:
    ersparnis (float): Kostenersparnis
    ersparnis_prozent (float): Kostenersparnis in Prozent
    """
    ersparnis = kosten_max - kosten_min
    ersparnis_prozent = ersparnis / kosten_max * 100

    return ersparnis, ersparnis_prozent