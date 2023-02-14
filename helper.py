import numpy as np
import matplotlib.pyplot as plt
import math

# Datei die externe mathematische Berechnungen übernimmt 

def getvectorfromangle(ang):
    # Suche zu den Winkel die passende Auslenkung für die Rotation
    a = 0
    x = np.array([0.0, 0.0, 2.0])
    y = np.array([0.0, 0.0, 2.0])
    angle = (int(ang) / 180) * np.pi  # winkel in Bogenmaß
    cos_angle = np.around(np.cos(angle), 3)
    while a <= 200:
        a = a + 0.01
        y[1] = a / 2
        if cos_angle - 0.01 <= np.around(np.dot(x, y) / (2 * np.sqrt((y * y).sum())), 3) <= cos_angle + 0.01:
            y[1] = y[1] / 2
            break
    return y[1]


#Berechnet mittels Trigonometrie den Winkel, welcher beim Camera-Azimuth (der statischen Kamera) von 90 Grad (gerade noch vorne schauen) abgezogen werden muss, sodass die statische Kamera der Bewegung des Balls folgen kann

# Benutzt als Eingabe die Distanz der Kamera zur "nächsten" Ballposition, einerseits nur bezüglich der x-Koordinaten (gk = Gegenkathete) und andererseits nur bezüglich der y-Koordinaten (ak = Ankathete), um so den Winkel zu berechnen, von welchem die Kamera (bezogen auf 90 Grad) abweichen muss
def calcazimuthangle(gk, ak):
    return math.degrees(math.atan(gk/ak))


# Wird verwendet um die Veränderung der Camera-Elevation der Kugel für die statische Kamera zu berechnen, wobei als Eingabe der absolute Wert des Winkels, welcher die Abweichung des Azimuth derselben Kamera beschreibt (s. calcazimuthangle), verwendet werden soll

# Ist die Abweichung des Azimuth hoch, so ist der Ball weit von der Kamera entfernt, wodurch die Elevation keine große Abweichung (bezogen auf den Standardwert 360 für "vollständig horizontal") haben soll, für niedrige Abweichungen soll die Kamera jedoch etwas weiter nach unten schauen

# Benutzt eine Modifikation der Sigmoid-Funktion, welche nur Werte zwischen ca. 15-25 liefert, wobei die eingegebenen Werte zwischen 0 und 100 liegen sollten. Nimmt für niedrige Eingabe in diesem Intervall einen hohen Wert (nahe 25 an) und für hohe Eingaben einen niedrigen Wert an

def getcustomsigmoidelevation(az):
    return -1*(1 / (1 + math.exp(-0.1*(abs(az) - 45)))) * 10 + 25
