import numpy as np
import itertools

bolgeler = [None, None, None, None, None]
cezeri = [None, None, None, None, None]

class Cezeri(CezeriParent):   

    def __init__(self, id = 1):
        super().__init__(id = id, keyboard = False, sensor_mode = NORMAL)  

    def run(self):
        pass  


cezeri_1 = Cezeri(id = 1)

while robot.is_ok():

    (cezeri_1.run())