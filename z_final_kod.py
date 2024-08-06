import numpy as np
from itertools import permutations, product
import time

class Cezeri(CezeriParent):   

    def __init__(self, id = 1):
        super().__init__(id = id, keyboard = False, sensor_mode = DUZELTILMIS)
        self.kalkis_konum = (self.gnss.enlem, self.gnss.boylam)
        self.kalkis_enlem = self.gnss.enlem
        self.kalkis_boylam = self.gnss.boylam
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
        #print("ruzgar aranıyor...")

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

    def rota_olustur(self,hedefler,oncelik,bitis):
        if bitis==None:
            bitis_koordinat = []
            bitis_koordinat = np.array(bitis_koordinat)
        else:
            bitis_koordinat = np.array(bitis)

        baslangic_koordinat = np.array(self.kalkis_konum)
        
        hedef_kombinler = []
        tum_kombinler = []
        tuples =[]
        kombin = []
        mesafeler = []
        hedefler = np.array(hedefler)
        oncelik = np.array(oncelik)

        if len(hedefler) == 0 and len(bitis_koordinat) != 0:
            tum_hedefler = np.vstack((baslangic_koordinat,bitis_koordinat))
        elif len(hedefler) != 0 and len(bitis_koordinat) == 0:
            tum_hedefler = np.vstack((baslangic_koordinat,hedefler))
        elif len(hedefler) != 0 and len(bitis_koordinat) != 0 :
            tum_hedefler = np.vstack((baslangic_koordinat,hedefler,bitis_koordinat))
        
        for i in range(len(tum_hedefler)):
            mesafe = []
            for j in range(len(tum_hedefler)):
                """if self.hiz_kontrol(tum_hedefler[i][0],tum_hedefler[i][1],tum_hedefler[j][0],tum_hedefler[j][1]) == True :
                    x = np.sqrt((tum_hedefler[i][0] - tum_hedefler[j][0]) ** 2 + (tum_hedefler[i][1] - tum_hedefler[j][1]) ** 2)
                    a = 1.7*x 
                else:"""
                
                a = np.sqrt((tum_hedefler[i][0] - tum_hedefler[j][0]) ** 2 + (tum_hedefler[i][1] - tum_hedefler[j][1]) ** 2)
                mesafe.append(a)

            mesafeler.append(mesafe)

        mesafeler = np.array(mesafeler)

        def oncelik_index(oncelik,bitis_koordinat):

            if len(oncelik)>0:
                num_priorities = oncelik.max()
                indexes = []
                for i in range(1, num_priorities+1):
                    ind = np.where(oncelik == i)[0]
                    indexes.append(ind+1)

                zero_ind = np.where(oncelik == 0)[0]
                if 0 in oncelik:
                    indexes.append(zero_ind+1)

                baslangic = np.array([0])
                bitis =  np.array([len(oncelik)+1])

                if len(bitis_koordinat) != 0:
                    indexes.append(bitis)

                indexes.insert(0,baslangic)

            else:
                indexes = []
                baslangic = np.array([0])
                bitis =  np.array([len(oncelik)+1])
                indexes.append(bitis)
                indexes.insert(0,baslangic)

            return indexes

        for indexes in oncelik_index(oncelik,bitis_koordinat):
            tuples.append(tuple(indexes.tolist()))
            a=list(permutations(indexes))
            hedef_kombinler += [a]

        for tpl in product(*hedef_kombinler):
            combined = ()
            for i, t in enumerate(tuples):
                combined += (tpl[i] if len(tpl[i]) > 1 else tpl[i][0],)
            kombin.append(combined)


        for tpl in kombin:
            new_tpl = tuple([elem for sub_tpl in tpl for elem in (sub_tpl if isinstance(sub_tpl, tuple) else (sub_tpl,))])
            tum_kombinler.append(new_tpl)

        toplam_mesafe = [sum([mesafeler[tum_kombinler[i][j], tum_kombinler[i][j+1]] for j in range(len(tum_kombinler[i])-1)]) for i in range(len(tum_kombinler))]
        en_kisa_rota_indexi = np.argmin(toplam_mesafe)
        en_kisa_rota_kombini = tum_kombinler[en_kisa_rota_indexi]
        en_kisa_rota = [tum_hedefler[i].tolist() for i in en_kisa_rota_kombini]
        del en_kisa_rota[0]
        if self.baslangica_don: 
            en_kisa_rota.append((self.kalkis_enlem,self.kalkis_boylam))

        self.en_kisa_rota = en_kisa_rota
        
    
    def run(self):

        kalkis_enlem = self.kalkis_enlem
        kalkis_boylam = self.kalkis_boylam
        guncel_enlem = self.gnss.enlem
        guncel_boylam = self.gnss.boylam
        irtifa_araliginda = False
        hedefler = []
        oncelik = []
        bitis = None

        for hedef in self.hedefler:
            if hedef.amac == INIS:
                bitis = (hedef.bolge.enlem,hedef.bolge.boylam)
            else:
                hedefler.append((hedef.bolge.enlem,hedef.bolge.boylam))
                oncelik.append(hedef.sira)

        
        #print("hedefler",hedefler)
        #print("oncelik",oncelik)
        #print("bitis",bitis)

        
        if self.barometre.irtifa < 100 and irtifa_araliginda == False:
            self.yukari_git(HIZLI)     

        else:
            irtifa_araliginda = True

        self.rota_olustur(hedefler,oncelik,bitis)
        
        
        
        #print("imu hiz", self.imu.hiz.x,self.imu.hiz.y,self.imu.hiz.z)
        #print("hedef",hedef_enlem,hedef_boylam)
        #print("kalkis",self.enlem,self.boylam)
        #print("koordinat",guncel_enlem,guncel_boylam)
        
        if irtifa_araliginda == True :
            for hedefx in self.hedefler:
                print(hedefx.bolge.enlem)

            for hedef in self.en_kisa_rota:
                hedef_enlem = hedef[0]
                hedef_boylam = hedef[1]
            
            """
                    if hedefx.bolge.enlem == hedef_enlem and hedefx.bolge.boylam == hedef_boylam:
                        hedefy = self.hedefler[i]
                  
                if hedefy.amac == INIS:
                    print("inis")
                    self.inis_yap(guncel_enlem,guncel_boylam,hedef_enlem,hedef_boylam)
                else:
                    self.git(guncel_enlem,guncel_boylam,hedef_enlem,hedef_boylam)"""


cezeri = Cezeri(id = 1)


while robot.is_ok():

    (cezeri.run())
