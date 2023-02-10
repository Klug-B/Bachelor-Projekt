import numpy as np
import matplotlib.pyplot as plt
# Plotter der das plotten der Kurve des Kugel übernimmt
class Plotter:
    
    # erstellt ein Array für die x- und y-Werte der Kurve
    def __init__(self, x, y):
        self.curvex = np.array([x])
        self.curvey = np.array([y])

    # fügt zu dem Array weitere Punkte der Kurve hinzu
    def updatecurves(self, x, y):
        self.curvex = np.append(self.curvex, x)
        self.curvey = np.append(self.curvey, y)

    # erstellt ein Koordinatensystem von dem Kurvenverlauf der Kugel
    def plotcurves(self):
        plt.plot((self.curvey),np.flip(self.curvex))
        plt.axis([-1, 1, 0.1, 20.0])
        plt.title("Bowlingkurve")
        plt.show()