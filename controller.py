import mujoco
import numpy as np
from helper import getvectorfromangle, getquaternation


class Controller:

    # Inititalisierung der Klasse
    def __init__(self, model, data):
        self.model = model
        self.data = data
        self.umgefallen = [False] * 10
        self.resetted = False

    # soll die Simulation auf ihre Anfangswerte zurücksetzen
    def resetsimulation(self):
        check_eingabe = False
        inputlist = ["Ja", "Nein", "ja", "nein", "JA", "NEIN"]

        # Abfangen des möglichen Eingabefehlers
        while check_eingabe == False:

            inputcommand = input("Wollen Sie die Simulation resetten?")
            if inputcommand in inputlist:
                check_eingabe = True
            else:
                print("Ungültige Eingabe! Bitte Ja oder Nein eingeben!")

        mujoco.mj_resetDataKeyframe(self.model, self.data, 1)
        return

    def checkfalldown(self):
        # Teleportieren der Kegel, Pins und Kugel hier einfügen
        for i in range(1, 11):  # prüfe ob pins umgefallen
            if self.data.sensordata[self.model.sensor("Pin" + str(i) + "Sensor").adr + 2] < 0.100 and self.umgefallen[
                i - 1] == False:
                self.umgefallen[i - 1] = True
                self.model.geom("PinLicht" + str(i)).rgba= [0, 0, 0, 1]
        return 

    def setsecondthrow(self):
        for i in range(1, 11):
            if self.umgefallen[i - 1]:
                self.data.joint("pin" + str(i) + "joint").qpos = self.model.joint("pin" + str(i) + "joint").qpos0
                self.data.qpos[self.model.joint("pin" + str(i) + "joint").qposadr + 2] = \
                    self.model.joint("pin" + str(i) + "joint").qpos0[3] + 0.5
            else:
                self.data.qpos[self.model.joint("pin" + str(i) + "joint").qposadr] = \
                    self.model.joint("pin" + str(i) + "joint").qpos0[0]

            resetted = True

        # Für debugging
        # print(data.qvel)
        for i in range(len(self.data.qvel)):
            self.data.qvel[i] = 0
        self.data.joint("rotforce").qpos[1] = self.model.body("arm").pos[1]
        self.data.ctrl[self.model.actuator("adhere_arm3").id] = 10
        self.data.ctrl[self.model.actuator("adhere_arm4").id] = 10
        self.data.ctrl[self.model.actuator("adhere_arm5").id] = 10
        self.data.ctrl[self.model.actuator("adhere_arm6").id] = 10
        # Für debugging
        # print(data.qvel)
        return self.data

    # Funktion setzt die initialen Werte für die Position des Armes
    def setstartingposarm(self):
        check_eingabe = False

        # Abfangen des möglichen Eingabefehlers
        while check_eingabe == False:

            ypos = input("Von wo soll der Arm gestartet werden. Geben Sie die y Koordinante ein!\n Sie können dabei"
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

    # Funktion setzt den Arm senkrecht oder mit gewissen Winkel zur Abwurflinie
    def setstartinganglefromarm(self):
        check_eingabe = False

        # Abfangen des möglichen Eingabefehlers
        while check_eingabe == False:

            anglepos = input("Um wie viel Grad soll der Arm zur Abwurflinie ausgelenkt sein.\n Geben Sie eine Zahl "
                             "zwischen -10 und 10 ein. \n Wie gemessen wird, entnehmen Sie der Readme.")

            # Änderung der Orientierung des Arms und ändern der Polarkoordinaten der Kugel funktioniert noch nicht richtig
            try:
                if float(anglepos) != 0:
                    self.model.body("arm").quat = getquaternation(-float(anglepos))
                    #self.model.body("Kugel").quat = getquaternation(-float(anglepos))
                    #self.model.body("Kugel").pos[0] = 0.1 * np.sin(float(anglepos)) + self.model.body("Kugel").pos[0]
                    #self.model.body("Kugel").pos[1] = 0.1 * np.cos(float(anglepos)) + self.model.body("Kugel").pos[1]
                if -10 <= float(anglepos) <= 10:
                    check_eingabe = True
                else:
                    print("Der eingegebene Wert liegt außerhalb des zu betrachtenden Intervalls!")
            except ValueError:
                print("Der eingegebene Wert ist nicht von einem gültigen Datentyp!")
        return self.model

    # Funktion setzt die initialen Werte für die Kraft die wirken soll.
    def setstartingctrl(self):
        check_eingabe = False

        # Abfangen des möglichen Eingabefehlers
        while check_eingabe == False:
            inputctrl = input("Geben Sie ein wie viel Kraft sie auf die Kugel bringen möchten!\n Sie können dabei"
                              " Werte zwischen 100 und 1 eingeben!")
            try:
                self.data.ctrl[self.model.actuator("schwung").id] = inputctrl
                if float(inputctrl) >= 1.0 and float(inputctrl) <= 100.0:
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

    # Funktion setzt rotation der Kugel
    def setrotationatstart(self):
        check_eingabe = False
        # Fehlerabfrage wieder mit den Werten, Winkel zwischen 0<winkel<90
        inputangle = input('Welche Rotation wollen sie haben? Geben sie den Winkel (Ganze Zahl) \n'
                           'ein den Sie haben möchten (ohne °).\nEntsprechendes Beipiel entnehmen Sie der '
                           'Readme.')
        while check_eingabe == False:
            try:
                #self.data.ctrl[self.model.actuator("rotation").id] = 0
                if int(inputangle) < 0:
                    self.model.actuator("rotation").gear[3] =  getvectorfromangle(int(inputangle))
                else:
                    self.model.actuator("rotation").gear[3] =  -getvectorfromangle(-int(inputangle))
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
    
    def setrangeofarm(self):
        check_eingabe = False
        # Fehlerabfrage um wie viel Grad der Arm ausgelenkt wird min 30 bis max 90 °
        inputangle = input('Um wie viel Grad darf der Arm ausgelenkt werden?\n Geben Sie eine ganze Zahl zwischen'
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
    
    def releaseball(self):
        self.data.ctrl[self.model.actuator("adhere_arm3").id] = 0
        self.data.ctrl[self.model.actuator("adhere_arm4").id] = 0
        self.data.ctrl[self.model.actuator("adhere_arm5").id] = 0
        self.data.ctrl[self.model.actuator("adhere_arm6").id] = 0
        self.data.ctrl[self.model.actuator("rotation").id] = 0
        self.model.body("haltmagnet2").pos[1] = 20.5 
        self.model.body("haltmagnet3").pos[1] = 20.5 
        self.model.body("haltmagnet4").pos[1] = 20.5 
        self.model.body("haltmagnet5").pos[1] = 20.5 
        self.data.ctrl[self.model.actuator("schwung").id] = -5
        return self.model, self.data
    
    def revertrangeofarm(self):
        self.model.joint("armschwung").range[1] = 40 / 180 * np.pi
        return self.model
    
    def startadhesion(self):
        self.data.ctrl[self.model.actuator("schwung").id] = 5
        self.data.ctrl[self.model.actuator("adhere_arm3").id] = 10
        self.data.ctrl[self.model.actuator("adhere_arm4").id] = 10
        self.data.ctrl[self.model.actuator("adhere_arm5").id] = 10
        self.data.ctrl[self.model.actuator("adhere_arm6").id] = 10
        return self.data
    
    def controlFriction(self):
        
        pos_x = self.data.joint("rotforce").qpos[0]
        pos_y = self.data.joint("rotforce").qpos[1]
        pos_z = self.data.joint("rotforce").qpos[2]
        
        if (pos_x >= 18):
            self.model.geom("rollarea").friction = 0
        elif (pos_x < 18 and pos_x >= 15 and pos_y >= -0.5 and pos_y <= 0.5):
            self.model.geom("rollarea").friction = 0
        elif ((pos_x < 18 and pos_x >= 15 and pos_y < -0.5) or (pos_x < 18 and pos_x >= 15 and pos_y < 0.5)):
            self.data.ctrl[self.model.actuator("rotation").id] = self.data.ctrl[self.model.actuator("rotation").id] + 0.0002
            self.model.geom("rollarea").friction = 0.25
        elif (pos_x < 15 and pos_x >= 10 and pos_y >= -0.5 and pos_y <= 0.5):
            self.data.ctrl[self.model.actuator("rotation").id] = self.data.ctrl[self.model.actuator("rotation").id] + 0.0004
            self.model.geom("rollarea").friction = 0.25
        elif (pos_x < 10 and pos_x >= 5 and pos_y >= -0.5 and pos_y <= 0.5):
            self.data.ctrl[self.model.actuator("rotation").id] = self.data.ctrl[self.model.actuator("rotation").id] + 0.0005
            self.model.geom("rollarea").friction = 0.5
        elif ((pos_x < 15 and pos_x >= 5 and pos_y < -0.5) or (pos_x < 18 and pos_x >= 15 and pos_y < 0.5)):
            self.data.ctrl[self.model.actuator("rotation").id] = self.data.ctrl[self.model.actuator("rotation").id] + 0.0006
            self.model.geom("rollarea").friction = 0.75
        elif (pos_x < 5):
            self.data.ctrl[self.model.actuator("rotation").id] = self.data.ctrl[self.model.actuator("rotation").id] + 0.0006
            self.model.geom("rollarea").friction = 0.75
        elif (pos_x < 0):
            self.data.ctrl[self.model.actuator("rotation").id] = 0
            
        
        return self.model 
        
        
        