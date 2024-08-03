
class Cezeri(CezeriParent):    
    def __init__(self, id = 0):
        super().__init__(id = id, keyboard = False, sensor_mode = DUZELTILMIS)

        self.baslangic_bolgesi = self.harita.bolge(self.gnss.enlem, self.gnss.boylam)


    def donus_tamamla(self,hedef_enlem,hedef_boylam,guncel_enlem,guncel_boylam):#donus fonksiyonu

    def run(self):

        hedef = self.hedefler[0]
        hedef_enlem = hedef.bolge.enlem
        hedef_boylam = hedef.bolge.boylam
        guncel_enlem = self.gnss.enlem
        guncel_boylam = self.gnss.boylam
        irtifa_araliginda = False
        uzaklik=math.sqrt((hedef_enlem-guncel_enlem)**2 + (hedef_boylam-guncel_boylam)**2)

        if self.barometre.irtifa < 100 and irtifa_araliginda == False:
            self.yukari_git(HIZLI)  
            
        else:
            irtifa_araliginda = True
            Cezeri.donus_tamamla(self,hedef_enlem,hedef_boylam,guncel_enlem,guncel_boylam)
 
 
        if uzaklik < 50:
            if uzaklik < 30:
                if uzaklik < 5:
                    self.dur()
                    self.asagi_git(YAVAS)
                    print("gittik")
                else: 
                    self.ileri_git(YAVAS)
            else:
                self.ileri_git(ORTA)
        else: 
            self.ileri_git(HIZLI)


cezeri_1 = Cezeri(id = 1)

while robot.is_ok():
    (cezeri_1.run())

