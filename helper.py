import numpy as np
import matplotlib.pyplot as plt

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
            break
    return y[1]

def getquaternation(ang):
    #gibt die Drehung um die Z-Achse aus, als quaternation Winkel in Bogenmaß V einheitsvektor [cos(W/2),sin(W/2)*Vx,sin(W/2)*Vy,sin(W/2)*Vz]
    angle = (int(ang) / 180) * np.pi  # winkel in Bogenmaß
    #Brauchen nur Drehung um z Achse daher Einheitsvektor (0,0,1)
    x = np.array([np.cos(angle / 2), 0, 0, np.sin(angle / 2)])
    return x