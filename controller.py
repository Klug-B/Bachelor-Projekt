import mujoco
import numpy as np


class Controller:
    def __init__(self, model, data):
        self.model = model
        self.data = data

    def resetsimulation(self):
        inputcommand = input("Wollen Sie die Simulation resetten?")
        # Fehlerabfrage wenn ja dann reset nein return
        mujoco.mj_resetDataKeyframe(self.model, self.data, 1)
        return

    def setsecondthrow(self):
        # Teleportieren der Kegel, Pins und Kugel hier einfügen
        return

    def setstartingposarm(self):
        ypos = input("Von wo soll der Arm gestartet werden. Geben Sie die y Koordinante ein!\n Sie können dabei"
                     "Werte zwischen -0.53 und 0.53!")
        # Fehlerabfrage vom Wert selber und dass , ein . ist
        self.model.body("arm").pos[1] = ypos
        return self.model.body("arm").pos

    def setstartingctrl(self):
        inputctrl = input("Geben Sie ein wie viel Kraft sie auf die Kugel bringen möchten!\n Sie können dabei"
                          "Werte zwischen -100 und -1 eingeben!")
        self.data.ctrl[self.model.actuator("schwung").id] = inputctrl
        return self.data.ctrl[self.model.actuator("schwung").id]

    def setstartingposball(self):
        self.data.joint("rotforce").qpos[1] = self.model.body("arm").pos[1]
        return self.data.joint("rotforce").qpos
