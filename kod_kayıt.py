import numpy as np
import time

class Cezeri(CezeriParent):    
    def __init__(self, id = 1):
        super().__init__(id = id, keyboard = False, sensor_mode = DUZELTILMIS)
        self.baslangic_bolgesi = self.harita.bolge(self.gnss.enlem, self.gnss.boylam)
        self.enlem = self.gnss.enlem
        self.boylam = self.gnss.boylam
        self.gidildi=False



    def donus_tamamla(self,guncel_enlem,guncel_boylam,hedef_enlem,hedef_boylam):#donus fonksiyonu
 
        imux = self.imu.hiz.x
        imuz = self.imu.hiz.z
        imu_manyet = math.atan2(imuz,imux)

        cos = hedef_enlem-guncel_enlem
        sin = hedef_boylam-guncel_boylam
        x = math.degrees(math.atan2(sin,cos))

        if self.manyetometre.hata:
            #print("hata!!",self.manyetometre.veri,imu_manyet)
            manyet_veri = imu_manyet

        else:
            #print("hata yok",self.manyetometre.veri,imu_manyet)
            manyet_veri = self.manyetometre.veri

        if x>180 :
            hedef_aci= x-360

        else:
            hedef_aci=x

        if math.radians(hedef_aci)- 0.05 < manyet_veri < math.radians(hedef_aci)+ 0.05 :
            self.dur()
        
        else:

            if 0<=hedef_aci<=180 and 0<=math.degrees(manyet_veri)<=180 or 0>=hedef_aci>=-180 and 0>=math.degrees(manyet_veri)>=-180  :
                    
                donus_aci = math.radians(hedef_aci)-manyet_veri
                self.don(donus_aci) 

   
            elif 0<math.degrees(manyet_veri)<180 and 0>hedef_aci>-180:

                a= math.radians(hedef_aci)-manyet_veri
                b= a+2*(math.pi)

                if abs(a)<abs(b):
                    donus_aci=a
                else:
                    donus_aci=b

                self.don(donus_aci)  
                
            elif 0>math.degrees(manyet_veri)>-180 and 0<hedef_aci<180 :         
                a = math.radians(hedef_aci)-manyet_veri
                b = a-2*(math.pi)

                if abs(a)<abs(b):
                    donus_aci=a
                else:
                    donus_aci=b

                self.don(donus_aci) 

    
    def gnss_tamir(self,guncel_enlem,guncel_boylam,zaman):

        self.gnss_hata = False
        self.gercek_enlem = self.enlem
        self.gercek_boylam = self.boylam

    
        if guncel_boylam == 0 and guncel_boylam == 0:
            self.gnss_hata=True
            print("hata!")
            print("gnss",self.gercek_enlem,self.gercek_boylam)
             
        else:
            self.gnss_hata=False
            print("hata yok") 
            print("gnss" ,guncel_enlem,guncel_boylam)

        if self.gnss.spoofing == True:
            self.gnss_hata = True
            
            self.gercek_enlem += self.zaman()*self.imu.hiz.x
            self.gercek_boylam += (self.zaman()*self.imu.hiz.z

    def git(self,guncel_enlem,guncel_boylam,hedef_enlem,hedef_boylam):
     
        uzaklik = math.sqrt((hedef_enlem-guncel_enlem)**2 + (hedef_boylam-guncel_boylam)**2)
        self.donus_tamamla(guncel_enlem,guncel_boylam,hedef_enlem,hedef_boylam)
        if uzaklik < 50:
            if uzaklik < 30:
                if uzaklik < 5:
                    self.dur()
                    self.gidildi=True
                else: 
                    self.ileri_git(YAVAS)
            else:
                self.ileri_git(ORTA)
        else: 
            self.ileri_git(HIZLI)
        
    def inis_yap(self,guncel_enlem,guncel_boylam,hedef_enlem,hedef_boylam):

        uzaklik = math.sqrt((hedef_enlem-guncel_enlem)**2 + (hedef_boylam-guncel_boylam)**2)

        if uzaklik < 5:
            self.dur()   
            self.asagi_git(YAVAS)
            return True


    def ruzgar(self,kalkis_enlem,kalkis_boylam,hedef_enlem,hedef_boylam):
        print("ruzgar aranıyor...")

        sag_yasak=False
        sol_yasak=False
        self.yasak=False
        ruzgar_bolge =[]
        
        rota_enlem=(hedef_enlem-kalkis_enlem)/40
        rota_boylam=(hedef_boylam-kalkis_boylam)/40

        sag_enlem = + rota_boylam
        sag_boylam = - rota_enlem

        sol_enlem = -rota_boylam
        sol_boylam = +rota_enlem
        
        for i in range (40):
            kalkis_enlem = kalkis_enlem + rota_enlem
            kalkis_boylam = kalkis_boylam + rota_boylam
            bolge = self.harita.bolge(kalkis_enlem, kalkis_boylam)

            if bolge.ruzgar == True:
                print("ruzgar bulundu")
                ruzgar_bolge.append([kalkis_enlem,kalkis_boylam])
                engel_sag_enlem=ruzgar_bolge[0][0]
                engel_sag_boylam=ruzgar_bolge[0][1]
                
                engel_sol_enlem=ruzgar_bolge[0][0]
                engel_sol_boylam=ruzgar_bolge[0][1]

                for i in range (10):
                    engel_sag_enlem = engel_sag_enlem+sag_enlem
                    engel_sag_boylam = engel_sag_boylam+sag_boylam
                    bolge_sag = self.harita.bolge(engel_sag_enlem,engel_sag_boylam)

                    if bolge_sag.ruzgar == False:
                        sag_durak_enlem=engel_sag_enlem
                        sag_durak_boylam=engel_sag_boylam 
                        sag_x_enlem=engel_sag_enlem
                        sag_x_boylam=engel_sag_boylam
                        rota_sag_enlem=(hedef_enlem-sag_x_enlem)/40
                        rota_sag_boylam=(hedef_boylam-sag_x_boylam)/40
                    
                for i in range (10):
                    engel_sol_enlem += sol_enlem
                    engel_sol_boylam += sol_boylam
                    bolge_sol = self.harita.bolge(engel_sol_enlem,engel_sol_boylam)

                    if bolge_sol.ruzgar==False:
                        sol_durak_enlem=engel_sol_enlem
                        sol_durak_boylam=engel_sol_boylam
                        sol_x_enlem=engel_sol_enlem
                        sol_x_boylam=engel_sol_boylam
                        rota_sol_enlem=(hedef_enlem-sol_x_enlem)/40
                        rota_sol_boylam=(hedef_boylam-sol_x_boylam)/40
                                
                for i in range (40):
                    sag_x_enlem = sag_x_enlem+rota_sag_enlem
                    sag_x_boylam = sag_x_boylam+rota_sag_boylam
                    bolgey = self.harita.bolge(sag_x_enlem,sag_x_boylam)

                    if bolgey.ruzgar==True: 
                        sag_yasak=True
                        
                    sol_x_enlem = sol_x_enlem+rota_sol_enlem
                    sol_x_boylam = sol_x_boylam+rota_sol_boylam
                    bolgez = self.harita.bolge(sol_x_enlem,sol_x_boylam)

                    if bolgez.ruzgar==True: 
                        sol_yasak=True      
                      
                    if i==39:
                        self.yasak=True 

        if self.yasak==True:
            print("yasak")
            if sag_yasak==False:
                #sagdan git
                self.durak_enlem=sag_durak_enlem
                self.durak_boylam=sag_durak_boylam
            else:
                #soldan git
                self.durak_enlem=sol_durak_enlem
                self.durak_boylam=sol_durak_boylam

            print("durak",self.durak_enlem,self.durak_boylam)
    
    def run(self):

        kalkis_enlem = self.enlem
        kalkis_boylam = self.boylam
        hedef = self.hedefler[0]
        hedef_enlem = hedef.bolge.enlem
        hedef_boylam = hedef.bolge.boylam
        guncel_enlem = self.gnss.enlem
        guncel_boylam = self.gnss.boylam
        irtifa_araliginda = False
        
        if self.barometre.irtifa < 100 and irtifa_araliginda == False:
            self.yukari_git(HIZLI)     

        else:
            irtifa_araliginda = True

        #print("imu hiz", self.imu.hiz.x,self.imu.hiz.y,self.imu.hiz.z)
        #print("hedef",hedef_enlem,hedef_boylam)
        #print("kalkis",self.enlem,self.boylam)
        #print("koordinat",guncel_enlem,guncel_boylam)
        print("zaman",self.zaman())
        print("hesaplama",self.gercek_enlem,self.gercek_boylam)

        self.ruzgar(kalkis_enlem,kalkis_boylam,hedef_enlem,hedef_boylam)

        if irtifa_araliginda == True and self.yasak==False :
            self.git(guncel_enlem,guncel_boylam,hedef_enlem,hedef_boylam)

        elif irtifa_araliginda == True and self.yasak==True: 
            durak_enlem=self.durak_enlem
            durak_boylam=self.durak_boylam 

            if self.gidildi:

                self.git(guncel_enlem,guncel_boylam,hedef_enlem,hedef_boylam)
            else:    
                self.git(guncel_enlem,guncel_boylam,durak_enlem,durak_boylam)

        self.inis_yap(guncel_enlem,guncel_boylam,hedef_enlem,hedef_boylam)



cezeri = Cezeri(id = 1)


while robot.is_ok():

    (cezeri.run())