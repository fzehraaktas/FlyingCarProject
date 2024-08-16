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
        self.irtifa_araliginda = False
        self.i = 0
        self.gercek_enlem = self.kalkis_enlem
        self.gercek_boylam = self.kalkis_boylam
        self.rota_enlem = 0
        self.rota_boylam = 0
        self.ilk_zaman = 0
        self.yasak=False
        self.sol_yasak=False
        self.sag_yasak=False
        self.en_kisa_uzaklik = float('inf')
        self.hastane_enlem = None
        self.hastane_boylam = None
        self.acil=False

    def gnss_tamir(self):
        
        if self.zaman() - self.ilk_zaman >= 1 :

            self.rota_enlem = self.imu.hiz.x
            self.rota_boylam = self.imu.hiz.z
            self.gercek_enlem += self.rota_enlem 
            self.gercek_boylam += self.rota_boylam 
            self.ilk_zaman = self.zaman()

        print("hesaplama",self.gercek_enlem,self.gercek_boylam)
            
    def acil_durum(self,guncel_enlem,guncel_boylam):
 
        for hastane in self.harita.hastaneler:
            
            uzaklik = math.sqrt((hastane.enlem-guncel_enlem)**2 + (hastane.boylam-guncel_boylam)**2)

            if uzaklik < self.en_kisa_uzaklik:
                self.en_kisa_uzaklik = uzaklik
                self.hastane_enlem = hastane.enlem
                self.hastane_boylam = hastane.boylam

        if self.acil_durum:
            self.acil=True

    def rota_olustur(self):

        hedefler = []
        oncelik = []
        bitis = None

        for hedef in self.hedefler:
            if hedef.amac == INIS:
                bitis = (hedef.bolge.enlem,hedef.bolge.boylam)
            else:
                hedefler.append((hedef.bolge.enlem,hedef.bolge.boylam))
                oncelik.append(hedef.sira)

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

                """ if self.hiz_kontrol(tum_hedefler[i][0],tum_hedefler[i][1],tum_hedefler[j][0],tum_hedefler[j][1]) == True :
                    x = np.sqrt((tum_hedefler[i][0] - tum_hedefler[j][0]) ** 2 + (tum_hedefler[i][1] - tum_hedefler[j][1]) ** 2)
                    a = 1.7*x 
                else: """

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

        return en_kisa_rota

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

    def sag_kontrol(self,kalkis_enlem,kalkis_boylam,hedef_enlem,hedef_boylam,engel_enlem,engel_boylam):                 

        rota_enlem=(hedef_enlem-kalkis_enlem)/100         
        rota_boylam=(hedef_boylam-kalkis_boylam)/100               

        sag_enlem = + rota_boylam       
        sag_boylam = - rota_enlem      
        
        for i in range (100):
            kontrol = False
            self.sag_yasak = False
            engel_enlem = engel_enlem + sag_enlem
            engel_boylam = engel_boylam + sag_boylam
            bolge = self.harita.bolge(engel_enlem,engel_boylam)

            if bolge.ucusa_yasakli_bolge == False and bolge.ruzgar == False and bolge.trafik == False and bolge.yukselti<80:
                kontrol_enlem = engel_enlem
                kontrol_boylam = engel_boylam
                kk_enlem=(kontrol_enlem - kalkis_enlem )/100 #kalkis_kontrol
                kk_boylam=(kontrol_boylam -kalkis_boylam)/100

                vk_enlem = (hedef_enlem - kontrol_enlem)/100 #varis_kontrol
                vk_boylam = (hedef_boylam - kontrol_boylam)/100

                for i in range (100):
                    kalkis_enlem = kalkis_enlem + kk_enlem
                    kalkis_boylam = kalkis_boylam + kk_boylam
                    kontrol_enlem = kontrol_enlem + vk_enlem
                    kontrol_boylam = kontrol_boylam + vk_boylam
                    bolgex = self.harita.bolge(kalkis_enlem,kalkis_boylam)
                    bolgey = self.harita.bolge(kontrol_enlem,kontrol_boylam)


                    if bolgex.ucusa_yasakli_bolge == True or bolgex.ruzgar == True or bolgex.trafik == True or bolgex.yukselti >=90 or bolgey.ucusa_yasakli_bolge == True or bolgey.ruzgar == True or bolgey.trafik == True or bolgey.yukselti >=90: 
                        self.sag_yasak = True
                        kontrol = True
                        break

                    if i == 99:
                        kontrol = True
                        break

            if kontrol == True:
                if self.sag_yasak == True:
                    continue
                else:
                    self.sag_durak_enlem = round(engel_enlem,1)
                    self.sag_durak_boylam = round(engel_boylam,1)
                    break


    def sol_kontrol(self,kalkis_enlem,kalkis_boylam,hedef_enlem,hedef_boylam,engel_enlem,engel_boylam):
        
        rota_enlem=(hedef_enlem-kalkis_enlem)/100
        rota_boylam=(hedef_boylam-kalkis_boylam)/100

        sol_enlem = - rota_boylam
        sol_boylam = + rota_enlem
        
        for i in range (100):
            self.sol_yasak=False
            kontrol = False
            engel_enlem = engel_enlem + sol_enlem
            engel_boylam = engel_boylam + sol_boylam
            bolge = self.harita.bolge(engel_enlem,engel_boylam)
           

            if bolge.ucusa_yasakli_bolge == False and bolge.ruzgar == False and bolge.trafik == False and bolge.yukselti<90:
                kontrol_enlem = engel_enlem
                kontrol_boylam = engel_boylam
                kk_enlem=(kontrol_enlem - kalkis_enlem )/100 #kalkis_kontrol
                kk_boylam=(kontrol_boylam - kalkis_boylam)/100
                vk_enlem = (hedef_enlem - kontrol_enlem)/100 #varis_kontrol
                vk_boylam = (hedef_boylam - kontrol_boylam)/100

                for i in range (100):
                    kalkis_enlem = kalkis_enlem + kk_enlem
                    kalkis_boylam = kalkis_boylam + kk_boylam
                    kontrol_enlem = kontrol_enlem + vk_enlem
                    kontrol_boylam = kontrol_boylam + vk_boylam
                    bolgex = self.harita.bolge(kalkis_enlem,kalkis_boylam)
                    bolgey = self.harita.bolge(kontrol_enlem,kontrol_boylam)

                    if bolgex.ucusa_yasakli_bolge == True or bolgex.ruzgar == True or bolgex.trafik == True or bolgex.yukselti >=90 or bolgey.ucusa_yasakli_bolge == True or bolgey.ruzgar == True or bolgey.trafik == True or bolgey.yukselti >=90: 
                        self.sol_yasak = True 
                        kontrol = True
                        break
                        
                    if i == 99:
                        kontrol = True
                        break

            if kontrol == True:
                if self.sol_yasak == True:
                    continue
                else:
                    self.sol_durak_enlem = round(engel_enlem,1)
                    self.sol_durak_boylam = round(engel_boylam,1)
                    break
                     
    def engel_kac (self,guncel_enlem,guncel_boylam,hedef_enlem,hedef_boylam):
        
        engel_bolge = []
        
        rota_enlem=(hedef_enlem-guncel_enlem)/100
        rota_boylam=(hedef_boylam-guncel_boylam)/100                    

        for i in range (100):
            guncel_enlem = guncel_enlem + rota_enlem
            guncel_boylam = guncel_boylam + rota_boylam
            bolge = self.harita.bolge(guncel_enlem, guncel_boylam)

            if bolge.ucusa_yasakli_bolge == True or bolge.ruzgar ==True or bolge.trafik == True or bolge.yukselti>=90 :
                #print("yasak")
                self.yasak=True
                engel_bolge.append([guncel_enlem,guncel_boylam])
                engel_enlem=engel_bolge[0][0]
                engel_boylam=engel_bolge[0][1]

                self.sag_kontrol(guncel_enlem,guncel_boylam,hedef_enlem,hedef_boylam,engel_enlem,engel_boylam)
                self.sol_kontrol(guncel_enlem,guncel_boylam,hedef_enlem,hedef_boylam,engel_enlem,engel_boylam)
                
                
                k_sag = math.sqrt((self.sag_durak_enlem- round(guncel_enlem,1) )**2 + (self.sag_durak_boylam- round(guncel_boylam,1) )**2)
                v_sag = math.sqrt((self.sag_durak_enlem-hedef_enlem)**2 + (self.sag_durak_boylam-hedef_boylam)**2)

                k_sol = math.sqrt((self.sol_durak_enlem-round(guncel_enlem,1))**2 + (self.sol_durak_boylam-round(guncel_boylam,1) )**2)
                v_sol = math.sqrt((self.sol_durak_enlem-hedef_enlem)**2 + (self.sol_durak_boylam-hedef_boylam)**2)

                sag_uzaklik = k_sag + v_sag     
                sol_uzaklik = k_sol + v_sol     

                if abs(sol_uzaklik - sag_uzaklik)<=20 and sol_uzaklik > sag_uzaklik:
                    #print("sol")
                    self.durak_enlem = self.sol_durak_enlem
                    self.durak_boylam = self.sol_durak_boylam
                    
                elif sol_uzaklik < sag_uzaklik:
                    #print("sol")
                    self.durak_enlem = self.sol_durak_enlem
                    self.durak_boylam = self.sol_durak_boylam
                    
                else:
                    #print("sag")
                    self.durak_enlem = self.sag_durak_enlem
                    self.durak_boylam = self.sag_durak_boylam
                    

                #print("engel",engel_enlem,engel_boylam)
                #print("sag durak", self.sag_durak_enlem , self.sag_durak_boylam)
                #print("sol durak", self.sol_durak_enlem , self.sol_durak_boylam)

            
    def git(self,guncel_enlem,guncel_boylam,hedef_enlem,hedef_boylam):

        self.rota_olustur()

        if self.acil == True:
            print("knk acil bak")
            hedef_enlem = self.hastane_enlem
            hedef_boylam = self.hastane_boylam
        
        for i, hedef in enumerate(self.hedefler):
            if hedef_enlem == hedef.bolge.enlem and hedef_boylam == hedef.bolge.boylam:
                hedef = self.hedefler[i]
                break

        if self.yasak == False:
            
            uzaklik = math.sqrt((hedef_enlem-guncel_enlem)**2 + (hedef_boylam-guncel_boylam)**2)
            self.donus_tamamla(guncel_enlem,guncel_boylam,hedef_enlem,hedef_boylam)

            if uzaklik < 50:
                if uzaklik < 30:
                    if uzaklik < 5:
                        if hedef.amac == INIS:
                            self.dur()
                        elif self.i == (len(self.en_kisa_rota) - 1):
                            self.dur()
                        elif self.acil_durum:
                            self.dur()
                            self.asagi_git(YAVAS)
                        else:
                            self.i +=1  
                    else: 
                        self.ileri_git(YAVAS)
                else:
                    self.ileri_git(ORTA)
            else: 
                self.ileri_git(HIZLI)
        
        else:
            print("engelinamk")
            uzaklik = math.sqrt((self.sol_durak_enlem-guncel_enlem)**2 + (self.sol_durak_boylam-guncel_boylam)**2)
            self.donus_tamamla(guncel_enlem,guncel_boylam,self.durak_enlem,self.durak_boylam)
           
            if uzaklik < 5:     
                self.yasak=False
            else: 
                self.ileri_git(HIZLI)
           

    def inis_yap(self,guncel_enlem,guncel_boylam):
        self.rota_olustur()

        for hedef in self.hedefler:

            if hedef.amac == INIS:
                hedef_enlem = hedef.bolge.enlem
                hedef_boylam = hedef.bolge.boylam

                uzaklik = math.sqrt((hedef_enlem-guncel_enlem)**2 + (hedef_boylam-guncel_boylam)**2)

                if uzaklik < 5:
                    self.dur()   
                    self.asagi_git(YAVAS)

            elif self.i == (len(self.en_kisa_rota) - 1):

                hedef_enlem = self.kalkis_enlem
                hedef_boylam = self.kalkis_boylam

                uzaklik = math.sqrt((hedef_enlem-guncel_enlem)**2 + (hedef_boylam-guncel_boylam)**2)

                if uzaklik < 5:
                    self.dur()   
                    self.asagi_git(YAVAS)
            else:
                pass
    
    def run(self):

        kalkis_enlem = self.kalkis_enlem
        kalkis_boylam = self.kalkis_boylam
        guncel_enlem = self.gnss.enlem
        guncel_boylam = self.gnss.boylam
        
        if self.barometre.irtifa < 100 and self.irtifa_araliginda == False:
            self.yukari_git(HIZLI)     

        else:
            self.irtifa_araliginda = True

        self.rota_olustur()
        self.acil_durum(guncel_enlem,guncel_boylam)

        #print("hesaplanan koordinat" , self.gercek_enlem,self.gercek_boylam)
        #print("guncel koordinat", self.gnss.enlem,self.gnss.boylam)
        #print("imu hiz", self.imu.hiz.x,self.imu.hiz.y,self.imu.hiz.z)
        #print("hedef",hedef_enlem,hedef_boylam)
        #print("kalkis",self.enlem,self.boylam)
        #print("koordinat",guncel_enlem,guncel_boylam)
        
        if self.irtifa_araliginda == True :
            self.git(guncel_enlem,guncel_boylam,self.en_kisa_rota[self.i][0],self.en_kisa_rota[self.i][1])
            self.inis_yap(guncel_enlem,guncel_boylam)
            


cezeri = Cezeri(id = 1)

while robot.is_ok():

    (cezeri.run())
