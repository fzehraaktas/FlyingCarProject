import math
import itertools

class Cezeri(CezeriParent):
    def __init__(self, id = 0):
        super().__init__(id = id, keyboard = False, sensor_mode = DUZELTILMIS)
        #print(self.gnss.irtifa)


    def run(self):
        super().run()
        #print(self.manyetometre.veri)


class Itfaiye(ItfaiyeParent):
    def __init__(self, id = 0):
        super().__init__(id = id, keyboard = False, sensor_mode = DUZELTILMIS)
        #print(self.gnss.irtifa)


    def run(self):
        super().run()
        #print(self.manyetometre.veri)

class Kargo(KargoParent):
    def __init__(self, id = 0):
        super().__init__(id = id, keyboard = False, sensor_mode = DUZELTILMIS)
        #print(self.gnss.irtifa)


    def run(self):
        super().run()
        #print(self.manyetometre.veri)

class Ambulans(AmbulansParent):
    def __init__(self, id = 0):
        super().__init__(id = id, keyboard = False, sensor_mode = DUZELTILMIS)
        #print(self.gnss.irtifa)


    def run(self):
        super().run()
        #print(self.manyetometre.veri)


# Ana program
itfaiye_1 = Itfaiye(id=1)
#kargo_1 = Kargo(id=1)

while robot.is_ok():
    itfaiye_1.run()
    #kargo_1.run()
