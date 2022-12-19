import mujoco
import numpy as np
import traceback


class Controller:
    
    # Inititalisierung der Klasse
    def __init__(self, model, data):
        self.model = model
        self.data = data

    # soll den die Simulation auf ihr Anfangswerte zurücksetzen
    def resetsimulation(self):
        check_eingabe = False
        inputlist = ["Ja","Nein", "ja", "nein", "JA", "NEIN"]
        
        
        # Abfangen des möglichen Eingabefehlers
        while check_eingabe == False:
        
            inputcommand = input("Wollen Sie die Simulation resetten?")
            if inputcommand in inputlist:
                check_eingabe = True
            else:
                print("Ungültige Eingabe! Bitte Ja oder Nein eingeben!")
        
        mujoco.mj_resetDataKeyframe(self.model, self.data, 1)
        return

    def setsecondthrow(self):
        # Teleportieren der Kegel, Pins und Kugel hier einfügen
        # evlt abfangen
        return

    
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

    
    # Funktion setzt die initialen Werte für die Kraft die wirken soll.
    def setstartingctrl(self):
        check_eingabe = False
                          
        # Abfangen des möglichen Eingabefehlers
        while check_eingabe == False: 
                          
            inputctrl = input("Geben Sie ein wie viel Kraft sie auf die Kugel bringen möchten!\n Sie können dabei"
                          " Werte zwischen -100 und -1 eingeben!")
                          
            try:
                self.data.ctrl[self.model.actuator("schwung").id] = inputctrl
                if float(inputctrl) >= -100 and float(inputctrl) <= -1:
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
