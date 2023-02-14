import mujoco
import numpy as np
from helper import getvectorfromangle


class Controller:

    # Inititalisierung der Klasse
    # model und data zuzm Steuern der Simulation
    # umgefallen und resetted verfolgen Zustand der Pins
    def __init__(self, model, data):
        self.model = model
        self.data = data
        self.umgefallen = [False] * 10
        self.resetted = False

    # checkfalldown ueberprueft anhand der Y-Koordinate, ob Pins umgefallen sind
    def checkfalldown(self):
        # Teleportieren der Kegel, Pins und Kugel hier einfuegen
        for i in range(1, 11):  # pruefe ob pins umgefallen
            if self.data.sensordata[self.model.sensor("Pin" + str(i) + "Sensor").adr + 2] < 0.100 and self.umgefallen[
                i - 1] == False:
                self.umgefallen[i - 1] = True
                self.model.geom("PinLicht" + str(i)).rgba = [0, 0, 0, 1] # zugehoeriges Licht auf Board wird Schwarz
        return self.model

    # ueberprueft, ob alle 10 Pins umgefallen sind
    def strike(self):
        for i in range(1, 11):
            if not self.umgefallen[i - 1]:
                return False
        return True

    # setzt die Pins, welche umgefallen sind, auf die Auffangbox     
    def setsecondthrow(self):
        self.model.geom("Lichtwurf1").rgba = [0, 0, 0, 1]
        self.model.geom("Lichtwurf2").rgba = [1, 0, 0, 1]
        for i in range(1, 11):
            if self.umgefallen[i - 1]:
                self.data.joint("pin" + str(i) + "joint").qpos = self.model.joint("pin" + str(i) + "joint").qpos0
                self.data.qpos[self.model.joint("pin" + str(i) + "joint").qposadr + 2] = \
                    self.model.joint("pin" + str(i) + "joint").qpos0[2] + 1
                self.data.qpos[self.model.joint("pin" + str(i) + "joint").qposadr] = \
                    self.model.joint("pin" + str(i) + "joint").qpos0[0] - 0.1

        return self.data, self.model

    # Funktion setzt die initialen Werte für die Position des Armes
    def setstartingposarm(self):
        check_eingabe = False

        # Abfangen des moeglichen Eingabefehlers
        while check_eingabe == False:

            ypos = input("Von wo soll der Arm gestartet werden. Geben Sie die y Koordinante ein!\nSie können dabei"
                         " Werte zwischen -0.53 und 0.53!")

            # Fehlerabfrage vom Wert selber und dass , ein . ist
            try:
                self.model.body("arm").pos[1] = ypos
                if float(ypos) >= -0.53 and float(ypos) <= 0.53:
                    check_eingabe = True
                else:
                    print("Der eingegebene Wert liegt außerhalb des zu betrachtenden Intervalls!")
            except ValueError:
                print("Der eingegebene Wert ist nicht von einem gültigen Datentyp!")

        return self.model.body("arm").pos

    # Funktion setzt die initialen Werte für die Kraft die wirken soll.
    def setstartingctrl(self):
        check_eingabe = False

        # Abfangen des moeglichen Eingabefehlers
        while check_eingabe == False:
            inputctrl = input("Geben Sie ein wie viel Kraft sie auf die Kugel bringen möchten!\nSie können dabei"
                              " Werte zwischen 1 und 5 eingeben!")
            try:
                self.data.ctrl[self.model.actuator("schwung").id] = inputctrl
                if float(inputctrl) >= 1.0 and float(inputctrl) <= 5.0:
                    check_eingabe = True
                else:
                    print("Der eingegebene Wert liegt außerhalb des zu betrachtenden Intervalls!")
            except ValueError:
                print("Der eingegebene Wert ist nicht von einem gültigen Datentyp!")

        return self.data.ctrl[self.model.actuator("schwung").id]

    # Funktion setzt die Startposition des Balls.
    def setstartingposball(self):
        self.data.joint("rotforce").qpos[1] = self.model.body("arm").pos[1]
        return self.data.joint("rotforce").qpos

    # Funktion setzt Rotation der Kugel
    def setrotationatstart(self):
        check_eingabe = False
        # Fehlerabfrage wieder mit den Werten, Winkel zwischen 0<winkel<90
        inputangle = input('Welche Rotation wollen sie haben? Geben sie den Winkel (Ganze Zahl) \n'
                           'ein den Sie haben möchten (ohne °).\nEntsprechendes Beipiel entnehmen Sie der '
                           'Readme.')
        while check_eingabe == False:
            try:
                if int(inputangle) < 0:
                    self.model.actuator("rotation").gear[3] = -getvectorfromangle(int(inputangle))
                else:
                    self.model.actuator("rotation").gear[3] = getvectorfromangle(int(inputangle))
                if -90 < int(inputangle) < 90:
                    check_eingabe = True
                else:
                    inputangle = input(
                        "Die Eingabe war außerhalb des vorgegebenen Intervalls. Versuchen Sie es erneut!")
                    check_eingabe = False

            except ValueError:
                inputangle = input("Die Eingabe hatte den falschen Datentyp. Geben Sie eine ganze Zahl zwischen"
                                   " -90 und 90 ein.")
        return self.model

    # setzt den Bewegungsradius fuer den Arm, je weiter der Arm auslenkt desto laenger bewegt sich die Kugel mit dem Arm
    # und desto laenger wirkt die Rotation auf die Kugel
    def setrangeofarm(self):
        check_eingabe = False
        # Fehlerabfrage um wie viel Grad der Arm ausgelenkt wird min 30 bis max 90 °
        inputangle = input('Um wie viel Grad darf der Arm ausgelenkt werden?\nGeben Sie eine ganze Zahl zwischen'
                           ' 30 und 90 ein.')

        while check_eingabe == False:
            try:
                self.model.joint("armschwung").range[0] = ((-int(inputangle) - 10) / 180) * np.pi
                if 30 <= int(inputangle) <= 90:
                    check_eingabe = True
                else:
                    inputangle = input(
                        "Die Eingabe war außerhalb des vorgegebenen Intervalls. Versuchen Sie es erneut!")
                    check_eingabe = False

            except ValueError:
                inputangle = input("Die Eingabe hatte den falschen Datentyp. Geben Sie eine ganze Zahl zwischen"
                                   "30 und 90 ein.")
        return self.model

    # gibt den Ball aus dem Magnetfeld frei 
    def releaseball(self):
        self.data.ctrl[self.model.actuator("adhere_arm3").id] = 0
        self.data.ctrl[self.model.actuator("adhere_arm4").id] = 0
        self.data.ctrl[self.model.actuator("adhere_arm5").id] = 0
        self.data.ctrl[self.model.actuator("adhere_arm6").id] = 0
        self.data.ctrl[self.model.actuator("rotation").id] = 0
        self.data.ctrl[self.model.actuator("schwung").id] = -5
        return self.model, self.data

    # startet das Magnetfeld, welches die Kugel am Ball haelt
    def startadhesion(self):
        self.data.ctrl[self.model.actuator("schwung").id] = 5
        self.data.ctrl[self.model.actuator("adhere_arm3").id] = 10
        self.data.ctrl[self.model.actuator("adhere_arm4").id] = 10
        self.data.ctrl[self.model.actuator("adhere_arm5").id] = 10
        self.data.ctrl[self.model.actuator("adhere_arm6").id] = 10
        return self.data

    # kontrolliert die Reibung in den verschiedenen Bereichen der Bowlingbahn um das
    # Oelmuster auf der Bahn zu simulieren
    def controlFriction(self):

        pos_x = self.data.joint("rotforce").qpos[0]
        pos_y = self.data.joint("rotforce").qpos[1]

        if (pos_x >= 18):
            self.model.geom("rollarea").friction = 0
            self.data.ctrl[self.model.actuator("rotation").id] = self.data.ctrl[
                                                                     self.model.actuator("rotation").id] + 0.0003
        elif (pos_x < 18 and pos_x >= 15 and pos_y >= -0.5 and pos_y <= 0.5):
            self.model.geom("rollarea").friction = 0
        elif ((pos_x < 18 and pos_x >= 15 and pos_y < -0.5) or (pos_x < 18 and pos_x >= 15 and pos_y < 0.5)):
            self.data.ctrl[self.model.actuator("rotation").id] = self.data.ctrl[
                                                                     self.model.actuator("rotation").id] + 0.0005
            self.model.geom("rollarea").friction = 0.25
        elif (pos_x < 15 and pos_x >= 10 and pos_y >= -0.5 and pos_y <= 0.5):
            self.data.ctrl[self.model.actuator("rotation").id] = self.data.ctrl[
                                                                     self.model.actuator("rotation").id] + 0.0007
            self.model.geom("rollarea").friction = 0.25
        elif (pos_x < 10 and pos_x >= 5 and pos_y >= -0.5 and pos_y <= 0.5):
            self.data.ctrl[self.model.actuator("rotation").id] = self.data.ctrl[
                                                                     self.model.actuator("rotation").id] + 0.0008
            self.model.geom("rollarea").friction = 0.5
        elif ((pos_x < 15 and pos_x >= 5 and pos_y < -0.5) or (pos_x < 18 and pos_x >= 15 and pos_y < 0.5)):
            self.data.ctrl[self.model.actuator("rotation").id] = self.data.ctrl[
                                                                     self.model.actuator("rotation").id] + 0.001
            self.model.geom("rollarea").friction = 0.75
        elif (pos_x < 5):
            self.data.ctrl[self.model.actuator("rotation").id] = self.data.ctrl[
                                                                     self.model.actuator("rotation").id] + 0.00105
            self.model.geom("rollarea").friction = 0.75
        elif (pos_x < 0):
            self.data.ctrl[self.model.actuator("rotation").id] = 0

        return self.model
