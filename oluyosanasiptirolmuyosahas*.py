
import numpy as np
from itertools import permutations, product
import time

class Cezeri(CezeriParent):   

    def __init__(self, id = 1):

        super().__init__(id = id, keyboard = False, sensor_mode = DUZELTILMIS)      
        self.kalkis_konum = (self.gnss.enlem, self.gnss.boylam)                                  
        self.kalkis_enlem = self.gnss.enlem
        self.kalkis_boylam = self.gnss.boylam
        self.irtifa_araliginda = False
        self.i = 0
        self.gercek_enlem = 0
        self.gercek_boylam = 0
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
        self.sag_ok = False
        self.sol_ok = False
        self.motor_hata = False
        self.en_yakin_sarj_istasyonuna_git = False
        self.yavas_git = False

    def gnss_tamir(self):
        hiz = math.sqrt((self.imu.hiz.x)**2 + (self.imu.hiz.y)**2)

        if self.gnss.enlem == 0 and self.gnss.boylam == 0:
            gecen_zaman= self.zaman() - self.ilk_zaman
            yol_x = gecen_zaman*(self.imu.hiz.x)
            yol_y = gecen_zaman*(self.imu.hiz.y)
            self.gercek_enlem = self.guncel_enlem 
            self.gercek_enlem += yol_x
            self.gercek_boylam = self.guncel_boylam
            self.gercek_boylam += yol_y
            
        else:
            self.ilk_zaman = self.zaman()
            self.guncel_enlem=self.gnss.enlem
            self.guncel_boylam=self.gnss.boylam

        #print("hesaplama",self.gercek_enlem,self.gercek_boylam)
        #print("zaman", self.ilk_zaman)"""

    def motor_ariza(self,guncel_enlem,guncel_boylam):

        for motor in self.motor.rpm:

            if motor == 0 :
                self.motor_hata = True
                
    def hiz_kontrol(self, guncel_enlem, guncel_boylam, hedef_enlem, hedef_boylam):
        rota_enlem=(hedef_enlem-guncel_enlem)/40
        rota_boylam=(hedef_boylam-guncel_boylam)/40

        for i in range (40):
            guncel_enlem = guncel_enlem + rota_enlem
            guncel_boylam = guncel_boylam + rota_boylam
            bolge = self.harita.bolge(guncel_enlem, guncel_boylam)

            if bolge.yavas_bolge == True:
                print("hiz bolgesi")
                self.yavas_git = True  
            else:
                self.yavas_git = False  
            
    def hastane(self,guncel_enlem,guncel_boylam):
 
        for hastane in self.harita.hastaneler:
            
            uzaklik = math.sqrt((hastane.enlem-guncel_enlem)**2 + (hastane.boylam-guncel_boylam)**2)

            if uzaklik < self.en_kisa_uzaklik:
                self.en_kisa_uzaklik = uzaklik
                self.hastane_enlem = hastane.enlem
                self.hastane_boylam = hastane.boylam

        if self.acil_durum:
            self.acil = True
        else:
            self.acil = False

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

                self.hiz_kontrol(tum_hedefler[i][0],tum_hedefler[i][1],tum_hedefler[j][0],tum_hedefler[j][1])

                if self.yavas_git == True :
                    x = np.sqrt((tum_hedefler[i][0] - tum_hedefler[j][0]) ** 2 + (tum_hedefler[i][1] - tum_hedefler[j][1]) ** 2)
                    a = 1.7*x 
                else: 
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
            manyet_veri = imu_manyet

        else:
            manyet_veri = self.manyetometre.veri

        if x>180 :
            hedef_aci= x-360

        else:
            hedef_aci=x

        if math.radians(hedef_aci)- 0.05 < manyet_veri < math.radians(hedef_aci)+ 0.05 :
            pass

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
        
        for i in range (250):
            kontrol = False
            self.sag_yasak = False
            engel_enlem = engel_enlem + sag_enlem
            engel_boylam = engel_boylam + sag_boylam
            bolge = self.harita.bolge(engel_enlem,engel_boylam)

            if bolge.ucusa_yasakli_bolge == False and bolge.ruzgar == False and bolge.trafik == False and bolge.yukselti<100:
                kontrol_enlem = engel_enlem
                kontrol_boylam = engel_boylam
                kk_enlem=(kontrol_enlem - kalkis_enlem )/100 #kalkis_kontrol
                kk_boylam=(kontrol_boylam -kalkis_boylam)/100

                for i in range (100):
                    kalkis_enlem = kalkis_enlem + kk_enlem
                    kalkis_boylam = kalkis_boylam + kk_boylam
                    bolgex = self.harita.bolge(kalkis_enlem,kalkis_boylam)
                    
                    if bolgex.ucusa_yasakli_bolge == True or bolgex.ruzgar == True or bolgex.trafik == True or bolgex.yukselti >=100 :
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
                    self.sag_durak_enlem = engel_enlem
                    self.sag_durak_boylam = engel_boylam
                    break

    def sol_kontrol(self,kalkis_enlem,kalkis_boylam,hedef_enlem,hedef_boylam,engel_enlem,engel_boylam):
        
        rota_enlem=(hedef_enlem-kalkis_enlem)/100
        rota_boylam=(hedef_boylam-kalkis_boylam)/100

        sol_enlem = - rota_boylam
        sol_boylam = + rota_enlem
        
        for i in range (250):
            self.sol_yasak=False
            kontrol = False
            engel_enlem = engel_enlem + sol_enlem
            engel_boylam = engel_boylam + sol_boylam
            bolge = self.harita.bolge(engel_enlem,engel_boylam)
           

            if bolge.ucusa_yasakli_bolge == False and bolge.ruzgar == False and bolge.trafik == False and bolge.yukselti<100:
                kontrol_enlem = engel_enlem
                kontrol_boylam = engel_boylam
                kk_enlem=(kontrol_enlem - kalkis_enlem )/100 #kalkis_kontrol
                kk_boylam=(kontrol_boylam - kalkis_boylam)/100


                for i in range (100):
                    kalkis_enlem = kalkis_enlem + kk_enlem
                    kalkis_boylam = kalkis_boylam + kk_boylam
                    bolgex = self.harita.bolge(kalkis_enlem,kalkis_boylam)

                    if bolgex.ucusa_yasakli_bolge == True or bolgex.ruzgar == True or bolgex.trafik == True or bolgex.yukselti >=100 :
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
                    self.sol_durak_enlem = engel_enlem
                    self.sol_durak_boylam = engel_boylam
                    break
                     
    def engel_kac (self,guncel_enlem,guncel_boylam,hedef_enlem,hedef_boylam):
        
        engel_bolge = []
        
        rota_enlem=(hedef_enlem-guncel_enlem)/100
        rota_boylam=(hedef_boylam-guncel_boylam)/100         

        #print("hedef",hedef_enlem,hedef_boylam)           

        for i in range (100):
            guncel_enlem = guncel_enlem + rota_enlem
            guncel_boylam = guncel_boylam + rota_boylam
            bolge = self.harita.bolge(guncel_enlem, guncel_boylam)

            if bolge.ucusa_yasakli_bolge == True or bolge.ruzgar == True or bolge.trafik == True or bolge.yukselti>=100 :
                #print("yasak")
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

                """
                if abs(sol_uzaklik - sag_uzaklik)<= 10 and sol_uzaklik > sag_uzaklik:
                    #print("sol")
                    self.durak_enlem = self.sol_durak_enlem
                    self.durak_boylam = self.sol_durak_boylam
                    uzaklik = math.sqrt((self.durak_enlem-guncel_enlem)**2 + (self.durak_boylam-guncel_boylam)**2)
                    if uzaklik < 3:  
                        self.yasak = False
                    else: 
                        self.yasak = True"""
                 
                if sol_uzaklik < sag_uzaklik:
                    #print("sol")
                    self.durak_enlem = self.sol_durak_enlem
                    self.durak_boylam = self.sol_durak_boylam
                    uzaklik = math.sqrt((self.durak_enlem-guncel_enlem)**2 + (self.durak_boylam-guncel_boylam)**2)
                    if uzaklik < 5:  
                        self.yasak = False
                    else: 
                        self.yasak = True
                    
                else:
                    #print("sag")
                    self.durak_enlem = self.sag_durak_enlem
                    self.durak_boylam = self.sag_durak_boylam
                    uzaklik = math.sqrt((self.durak_enlem-guncel_enlem)**2 + (self.durak_boylam-guncel_boylam)**2)
                    if uzaklik < 5:  
                        self.yasak = False
                    else: 
                        self.yasak = True
                    
        #print("yasak", self.yasak)

    def sarj_hesap (self,guncel_enlem,guncel_boylam,hedef_enlem,hedef_boylam) :
    
        uzaklik = math.sqrt((hedef_enlem-guncel_enlem)**2 + (hedef_boylam-guncel_boylam)**2) 
        bolge = self.harita.bolge(hedef_enlem,hedef_boylam)

        for i, hedef in enumerate(self.hedefler):
            if hedef_enlem == hedef.bolge.enlem and hedef_boylam == hedef.bolge.boylam:
                hedef = self.hedefler[i]
                break

        inis_sarj = (self.barometre.irtifa - bolge.yukselti) * 0.15 
        kalacak_sarj = self.batarya.veri - (uzaklik *0.075)
        
        if hedef.amac == INIS:
            kalacak_sarj = kalacak_sarj - inis_sarj
            print("lan olum")
        else:
            pass

        if kalacak_sarj < 23 :
            self.en_yakin_sarj_istasyonuna_git = True
        else:
            pass

        print("kalacak_sarj",kalacak_sarj,"sarja git :",self.en_yakin_sarj_istasyonuna_git)
           
    def en_yakin_sarj_istasyonu(self, guncel_enlem, guncel_boylam, hedef_enlem, hedef_boylam):
        
        uygun_istasyonlar = []
        en_iyi_istasyon = None
        
        for istasyon in self.harita.sarj_istasyonlari:
            uzaklik = math.sqrt((istasyon.enlem-guncel_enlem)**2 + (istasyon.boylam-guncel_boylam)**2)
            sarj_bolge = self.harita.bolge(istasyon.enlem,istasyon.boylam)
            inis_sarj = (self.barometre.irtifa - sarj_bolge.yukselti) * 0.15 
            kalacak_sarj = self.batarya.veri - (uzaklik *0.075) - inis_sarj

            if kalacak_sarj > 25:
                uygun_istasyonlar.append(istasyon)
            else:
                continue

        en_kisa_uzaklik = float('inf')

        for istasyon in uygun_istasyonlar:
            toplam_uzaklik = math.sqrt((istasyon.enlem-guncel_enlem)**2 + (istasyon.boylam-guncel_boylam)**2)
            toplam_uzaklik += math.sqrt((hedef_enlem- istasyon.enlem)**2 + (hedef_boylam - istasyon.boylam)**2)
        
            if toplam_uzaklik < en_kisa_uzaklik:
                en_kisa_uzaklik = toplam_uzaklik
                en_iyi_istasyon = istasyon
    
        if en_iyi_istasyon is not None:
            self.sarj_enlem = en_iyi_istasyon.enlem
            self.sarj_boylam = en_iyi_istasyon.boylam
            
               
        #uzaklik_sarj = math.sqrt((self.sarj_enlem-guncel_enlem)**2 + (self.sarj_boylam-guncel_boylam)**2)
            
    def git(self,guncel_enlem,guncel_boylam,hedef_enlem,hedef_boylam):
          

        if self.acil == True:
            hedef_enlem = self.hastane_enlem
            hedef_boylam = self.hastane_boylam
        
        if self.motor_hata == True or self.motor.hata == 1 :
            print("in")
            bolge = self.harita.bolge(guncel_enlem,guncel_boylam)
            if bolge.inilebilir :
                hedef_enlem = guncel_enlem
                hedef_boylam = guncel_boylam

        if self.en_yakin_sarj_istasyonuna_git == True:
            hedef_enlem = self.sarj_enlem
            hedef_boylam = self.sarj_boylam

        for i, hedef in enumerate(self.hedefler):
            if hedef_enlem == hedef.bolge.enlem and hedef_boylam == hedef.bolge.boylam:
                hedef = self.hedefler[i]
                break
        
        self.engel_kac(guncel_enlem,guncel_boylam,hedef_enlem,hedef_boylam)

        if self.yasak == False :
            self.donus_tamamla(guncel_enlem,guncel_boylam,hedef_enlem,hedef_boylam)
            uzaklik = math.sqrt((hedef_enlem-guncel_enlem)**2 + (hedef_boylam-guncel_boylam)**2)

            if self.yavas_git == True:

                if uzaklik < 5:
                    if hedef.amac == INIS:
                        if self.en_yakin_sarj_istasyonuna_git == True:
                            self.dur()
                            if self.lidar.mesafe < 15:
                                self.asagi_git(YAVAS) 
                            else:
                                self.asagi_git(HIZLI) 

                        if  self.batarya.veri == 100:
                            self.en_yakin_sarj_istasyonuna_git = False
                            self.irtifa_araliginda = False 
           
                        else:
                            self.dur()
                            if self.lidar.mesafe < 15:
                                self.asagi_git(YAVAS) 
                            else:
                                self.asagi_git(HIZLI) 

                    elif self.i == (len(self.en_kisa_rota) - 1):
                        print("abo")
                        self.dur()
                        self.asagi_git(YAVAS)

                    elif self.acil_durum:  
                        print("hehe:)")
                        self.dur()
                        self.asagi_git(YAVAS) 
           
                    else:  
                        self.i +=1 

                else: 
                    self.ileri_git(YAVAS)

            else:

                if uzaklik < 20:
                    if uzaklik < 5:
                        if hedef.amac == INIS:
                            if self.en_yakin_sarj_istasyonuna_git == True:
                                self.dur()
                                if self.lidar.mesafe < 15:
                                    self.asagi_git(YAVAS) 
                                else:
                                    self.asagi_git(HIZLI) 

                            if  self.batarya.veri == 100:
                                self.en_yakin_sarj_istasyonuna_git = False
                                self.irtifa_araliginda = False 
            
                            else:
                                self.dur()
                                if self.lidar.mesafe < 15:
                                    self.asagi_git(YAVAS) 
                                else:
                                    self.asagi_git(HIZLI) 

                        elif self.i == (len(self.en_kisa_rota) - 1):
                            print("abo")
                            self.dur()
                            self.asagi_git(YAVAS)

                        elif self.acil_durum:  
                            print("hehe:)")
                            self.dur()
                            self.asagi_git(YAVAS) 
            
                        else:  
                            self.i +=1 

                    else: 
                        self.ileri_git(YAVAS)
                else:
                    self.ileri_git(HIZLI)

        else:
            #print("engel")    
            uzaklik = math.sqrt((self.durak_enlem-guncel_enlem)**2 + (self.durak_boylam-guncel_boylam)**2)
            self.donus_tamamla(guncel_enlem,guncel_boylam,self.durak_enlem,self.durak_boylam)

            if self.yavas_git == True:
                if uzaklik < 5:  
                    self.yasak = False
                else: 
                    self.ileri_git(YAVAS)

            else:
                if uzaklik < 10:
                    if uzaklik < 5:  
                        self.yasak = False
                    else: 
                        self.ileri_git(YAVAS)
                else: 
                    self.ileri_git(HIZLI)

    def inis_yap(self,guncel_enlem,guncel_boylam):

        uzaklik = math.sqrt((hedef_enlem-guncel_enlem)**2 + (hedef_boylam-guncel_boylam)**2)

        if uzaklik < 5:
            self.dur()   
            self.asagi_git(YAVAS)

    def run(self):

        kalkis_enlem = self.kalkis_enlem
        kalkis_boylam = self.kalkis_boylam
        guncel_enlem = self.gnss.enlem
        guncel_boylam = self.gnss.boylam
        
        if self.barometre.irtifa < 100 and self.irtifa_araliginda == False:
            self.yukari_git(HIZLI)     
        else:
            self.dur()
            self.irtifa_araliginda = True

        
        hiz = math.sqrt((self.imu.hiz.x)**2 + (self.imu.hiz.z)**2)
        print("yavas bolge:",self.yavas_git ,"hiz",hiz)

        self.rota_olustur()
        hedef_enlem = self.en_kisa_rota[self.i][0]
        hedef_boylam = self.en_kisa_rota[self.i][1]
        self.hastane(guncel_enlem,guncel_boylam)
        self.motor_ariza(guncel_enlem,guncel_boylam)
        self.hiz_kontrol(guncel_enlem, guncel_boylam, hedef_enlem, hedef_boylam)
        self.sarj_hesap (guncel_enlem,guncel_boylam,hedef_enlem,hedef_boylam) 
        self.en_yakin_sarj_istasyonu(guncel_enlem, guncel_boylam, hedef_enlem, hedef_boylam)

        if self.irtifa_araliginda == True :
            
            self.git(guncel_enlem,guncel_boylam,self.en_kisa_rota[self.i][0],self.en_kisa_rota[self.i][1])
            

cezeri_1 = Cezeri(id = 1)


while robot.is_ok():

    (cezeri_1.run())

