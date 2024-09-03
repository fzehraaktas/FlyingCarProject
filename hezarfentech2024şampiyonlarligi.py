import numpy as np
from itertools import permutations, product
import time

bolgeler = [None, None, None, None, None]
cezeri = [None, None, None, None, None]

class Cezeri(CezeriParent):   

    def __init__(self, id = 1):

        super().__init__(id = id, keyboard = False, sensor_mode = DUZELTILMIS)      
        self.kalkis = self.harita.bolge(self.gnss.enlem, self.gnss.boylam)
        self.kalkis_konum = (self.gnss.enlem, self.gnss.boylam)                                  
        self.kalkis_enlem = self.gnss.enlem
        self.kalkis_boylam = self.gnss.boylam
        self.irtifa_araliginda = False
        self.i = 0
        self.rota_enlem = 0
        self.rota_boylam = 0
        self.yasak = False
        self.sol_yasak=False
        self.sag_yasak=False
        self.en_kisa_uzaklik = float('inf')
        self.hastane_enlem = None
        self.hastane_boylam = None
        self.acil=False
        self.motor_hata = False
        self.en_yakin_sarj_istasyonuna_git = False
        self.guncel_enlem = self.gnss.enlem
        self.guncel_boylam = self.gnss.boylam
        self.irtifa = 0 
        self.imu_yuksel = 0
        self.son_irtifa = 0
        self.yavas = False
        self.yavas_git = False
        self.trafik_kac = False
        self.trafik_engel = False
        self.trafik_enlem = 0 
        self.trafik_boylam = 0
        self.trafik_bolge = 0
        self.tr_ok = False
        self.kaldır = False
        self.inmek_yasak = False

    def motor_ariza(self,guncel_enlem,guncel_boylam):

        for motor in self.motor.rpm:
            if motor == 0 :
                self.motor_hata = True
                #print("hata:",self.motor.hata)
                
    def hiz_kontrol(self, kalkis_enlem, kalkis_boylam, hedef_enlem, hedef_boylam):
        rota_enlem=(hedef_enlem-kalkis_enlem)/100
        rota_boylam=(hedef_boylam-kalkis_boylam)/100

        for i in range (100):
            kalkis_enlem = kalkis_enlem + rota_enlem
            kalkis_boylam = kalkis_boylam + rota_boylam
            bolge = self.harita.bolge(kalkis_enlem, kalkis_boylam)

            if bolge.yavas_bolge == True:
                self.yavas_git = True
                
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
                if  self.yavas_git == True :
                    x = np.sqrt((tum_hedefler[i][0] - tum_hedefler[j][0]) ** 2 + (tum_hedefler[i][1] - tum_hedefler[j][1]) ** 2)
                    a = 2*x 
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
        
        for i in range (250):
            kontrol = False
            self.sag_yasak = False
            engel_enlem = engel_enlem + sag_enlem
            engel_boylam = engel_boylam + sag_boylam
            bolge = self.harita.bolge(engel_enlem,engel_boylam)

            if bolge.ucusa_yasakli_bolge == False and bolge.ruzgar == False and bolge.yukselti< self.irtifa :
                kontrol_enlem = engel_enlem
                kontrol_boylam = engel_boylam
                kk_enlem=(kontrol_enlem - kalkis_enlem )/100 #kalkis_kontrol
                kk_boylam=(kontrol_boylam -kalkis_boylam)/100

                for i in range (100):
                    kalkis_enlem = kalkis_enlem + kk_enlem
                    kalkis_boylam = kalkis_boylam + kk_boylam
                    bolgex = self.harita.bolge(kalkis_enlem,kalkis_boylam)

                    if bolgex.ucusa_yasakli_bolge == True or bolgex.ruzgar == True or bolgex == self.trafik_bolge or bolgex.yukselti >= self.irtifa: 
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

            if bolge.ucusa_yasakli_bolge == False and bolge.ruzgar == False and bolge.yukselti< self.irtifa :
                
                kontrol_enlem = engel_enlem
                kontrol_boylam = engel_boylam
                kk_enlem=(kontrol_enlem - kalkis_enlem )/100 #kalkis_kontrol
                kk_boylam=(kontrol_boylam - kalkis_boylam)/100

                for i in range (100):
                    kalkis_enlem = kalkis_enlem + kk_enlem
                    kalkis_boylam = kalkis_boylam + kk_boylam
                    bolgex = self.harita.bolge(kalkis_enlem,kalkis_boylam)

                    if bolgex.ucusa_yasakli_bolge == True or bolgex.ruzgar == True or bolgex.yukselti >= self.irtifa or bolgex == self.trafik_bolge: 
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
        trafik_bolge= []

        rota_enlem=(hedef_enlem-guncel_enlem)/100
        rota_boylam=(hedef_boylam-guncel_boylam)/100         

        if self.trafik_engel == False:

            for i in range (100):
                guncel_enlem = guncel_enlem + rota_enlem
                guncel_boylam = guncel_boylam + rota_boylam
                bolge = self.harita.bolge(guncel_enlem, guncel_boylam)
                hedef = self.harita.bolge(hedef_enlem, hedef_boylam)

                uzaklik = math.sqrt((bolge.enlem-hedef.enlem)**2 + (bolge.boylam-hedef.boylam)**2)

                if uzaklik < 100 and hedef.yukselti > 120:
                    self.yasak = False
                    continue

                if bolge.ucusa_yasakli_bolge == True or bolge.ruzgar == True or bolge.yukselti>= self.irtifa :
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

        else:
            print("nalan")                    
            self.sag_kontrol(guncel_enlem,guncel_boylam,hedef_enlem,hedef_boylam,self.trafik_enlem,self.trafik_boylam)
            self.sol_kontrol(guncel_enlem,guncel_boylam,hedef_enlem,hedef_boylam,self.trafik_enlem,self.trafik_boylam)
                
            k_sag = math.sqrt((self.sag_durak_enlem- round(guncel_enlem,1) )**2 + (self.sag_durak_boylam- round(guncel_boylam,1) )**2)
            v_sag = math.sqrt((self.sag_durak_enlem-hedef_enlem)**2 + (self.sag_durak_boylam-hedef_boylam)**2)

            k_sol = math.sqrt((self.sol_durak_enlem-round(guncel_enlem,1))**2 + (self.sol_durak_boylam-round(guncel_boylam,1) )**2)
            v_sol = math.sqrt((self.sol_durak_enlem-hedef_enlem)**2 + (self.sol_durak_boylam-hedef_boylam)**2)

            sag_uzaklik = k_sag + v_sag     
            sol_uzaklik = k_sol + v_sol    

            if sol_uzaklik < sag_uzaklik:
                print("sol")
                self.durak_enlem = self.sol_durak_enlem
                self.durak_boylam = self.sol_durak_boylam
                uzaklik = math.sqrt((self.durak_enlem-guncel_enlem)**2 + (self.durak_boylam-guncel_boylam)**2)
                print(uzaklik)

                if uzaklik < 5:  
                    self.yasak = False
                    self.trafik_engel = False
                else: 
                    self.yasak = True
                    
            else:
                print("sag")
                self.durak_enlem = self.sag_durak_enlem
                self.durak_boylam = self.sag_durak_boylam
                uzaklik = math.sqrt((self.durak_enlem-guncel_enlem)**2 + (self.durak_boylam-guncel_boylam)**2)

                if uzaklik < 5:  
                    self.yasak = False
                    self.trafik_engel = False
                else: 
                    self.yasak = True

    def hedefe_en_yakin_sarj_istasyonu(self, hedef_enlem, hedef_boylam):

        en_yakin_istasyon2 = None
        en_kisa_mesafe2 = float('inf')

        for istasyon2 in self.harita.sarj_istasyonlari:
            mesafe2 = math.sqrt((hedef_enlem- istasyon2.enlem)**2 + (hedef_boylam - istasyon2.boylam)**2)

            if mesafe2 < en_kisa_mesafe2:
                en_kisa_mesafe2 = mesafe2
                en_yakin_istasyon2 = istasyon2

        if en_yakin_istasyon2 is not None:
            self.sarj2_enlem = en_yakin_istasyon2.enlem
            self.sarj2_boylam = en_yakin_istasyon2.boylam


    def sarj_hesap (self,guncel_enlem,guncel_boylam,hedef_enlem,hedef_boylam) :

        self.rota_olustur()
        self.hedefe_en_yakin_sarj_istasyonu(hedef_enlem, hedef_boylam)
        uzaklik = math.sqrt((hedef_enlem-guncel_enlem)**2 + (hedef_boylam-guncel_boylam)**2) 
        sarj_uzaklik = math.sqrt((hedef_enlem-self.sarj2_enlem)**2 + (hedef_boylam-self.sarj2_boylam)**2)  
        bolge = self.harita.bolge(hedef_enlem,hedef_boylam)

        for i, hedef in enumerate(self.hedefler):
            if hedef_enlem == hedef.bolge.enlem and hedef_boylam == hedef.bolge.boylam:
                hedef = self.hedefler[i]
                break
            else:
                pass

        inis_sarj = abs(self.irtifa - bolge.yukselti) * 0.15

        if self.yavas == True: 
            self.kalacak_sarj = self.batarya.veri - (uzaklik *0.175) 
            harcanacak_sarj = self.kalacak_sarj - (sarj_uzaklik *0.175)
        else:
            self.kalacak_sarj = self.batarya.veri - (uzaklik *0.075)         
            harcanacak_sarj = self.kalacak_sarj - (sarj_uzaklik *0.075)

        if hedef.amac == INIS:     
            self.kalacak_sarj = self.kalacak_sarj - inis_sarj
            harcanacak_sarj = harcanacak_sarj - inis_sarj

        if self.kalacak_sarj < 21 :
            self.en_yakin_sarj_istasyonuna_git = True

        elif harcanacak_sarj < 21 and hedef.amac == ZIYARET :
            self.en_yakin_sarj_istasyonuna_git = True


        #print("kalacak_sarj",kalacak_sarj,"sarja git:",self.en_yakin_sarj_istasyonuna_git)
        #print("harcanacak_sarj",harcanacak_sarj)
                           
    def en_yakin_sarj_istasyonu(self,guncel_enlem, guncel_boylam, hedef_enlem, hedef_boylam):
                
        self.sarj_hesap(guncel_enlem,guncel_boylam,hedef_enlem,hedef_boylam)
        uygun_istasyonlar = []
        en_iyi_istasyon = None
            
        for istasyon in self.harita.sarj_istasyonlari:
            uzaklik = math.sqrt((istasyon.enlem-guncel_enlem)**2 + (istasyon.boylam-guncel_boylam)**2)
            sarj_bolge = self.harita.bolge(istasyon.enlem,istasyon.boylam)
            inis_sarj = (self.barometre.irtifa - sarj_bolge.yukselti) * 0.13

            if self.yavas == True:
                kalacak_sarj = self.batarya.veri - (uzaklik *0.175) - inis_sarj
            else:
                kalacak_sarj = self.batarya.veri - (uzaklik *0.075) - inis_sarj

            if kalacak_sarj > 21:
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

    def kalkis_yap(self):

        self.imu_yuksel += (self.imu.hiz.y)/25

        if ((self.gnss.enlem == 0 and self.gnss.boylam == 0) or self.gnss.spoofing == True) and self.barometre.hata == 1:#ikisi de bozuksa 
            self.irtifa = self.son_irtifa  + self.imu_yuksel
            #print("ikisi de bozuk")

        elif ((self.gnss.enlem == 0 and self.gnss.boylam == 0) or self.gnss.spoofing == True) and self.barometre.hata == 0:#gnss bozuk 
            #print("gnss bozuk")
            self.irtifa = self.barometre.irtifa

        elif self.barometre.hata == 1:#baro bozuk
            self.irtifa = self.gnss.irtifa
            #print("barobozuk")

        else:
            self.son_irtifa = self.barometre.irtifa
            self.irtifa = self.barometre.irtifa
            #print("bozukluk yok")

    def inis_yap(self,guncel_enlem,guncel_boylam):

        inis = self.harita.bolge(guncel_enlem,guncel_boylam)
        
        if self.radar.hata == 0 and self.lidar.hata == 0 :#hata yoksa
            #print("bozuk yok")
            self.mesafe = self.lidar.mesafe

        elif self.radar.hata == 1 and self.lidar.hata == 0:#sadece radar hatası varsa
            #print("radar bozuk")
            self.mesafe = self.lidar.mesafe

        elif self.radar.hata == 0 and self.lidar.hata == 1:#sadece lidar hatası varsa
            #print("lidar bozuk")
            self.mesafe = self.radar.mesafe

        else:#ikisi de bozuksa
            #print("ikisi de bozuk")
            self.mesafe = self.irtifa - inis.yukselti 

        if self.mesafe < 10:
            self.asagi_git(YAVAS)

        else:
            self.asagi_git(HIZLI)

    def git(self,guncel_enlem,guncel_boylam,hedef_enlem,hedef_boylam):

        self.rota_olustur()
        self.hastane(guncel_enlem,guncel_boylam)
        self.motor_ariza(guncel_enlem,guncel_boylam)

        if self.acil == True:
            print("knk acil bak")
            hedef_enlem = self.hastane_enlem
            hedef_boylam = self.hastane_boylam
        
        if self.motor_hata == True or self.motor.hata == 1 :
            print("in")
            bolge = self.harita.bolge(guncel_enlem,guncel_boylam)

            if bolge.inilebilir :
                self.dur()
                hedef_enlem = guncel_enlem
                hedef_boylam = guncel_boylam

        self.sarj_hesap(guncel_enlem,guncel_boylam,hedef_enlem,hedef_boylam)
        self.en_yakin_sarj_istasyonu(guncel_enlem, guncel_boylam, hedef_enlem, hedef_boylam)
    
        if self.en_yakin_sarj_istasyonuna_git == True:
            hedef_enlem = self.sarj_enlem
            hedef_boylam = self.sarj_boylam

        for i, hedef in enumerate(self.hedefler):
            if hedef_enlem == hedef.bolge.enlem and hedef_boylam == hedef.bolge.boylam:
                hedef = self.hedefler[i]
                break

        self.engel_kac(guncel_enlem,guncel_boylam,hedef_enlem,hedef_boylam)
        #print("YASAK :",self.yasak)

        hedef_uzaklik = math.sqrt((hedef_enlem-guncel_enlem)**2 + (hedef_boylam-guncel_boylam)**2)
        self.hedef_bolge = self.harita.bolge(hedef_enlem,hedef_boylam) 

        if self.hedef_bolge.yukselti > self.irtifa:  
            self.yasak = False 

        if self.yasak == False:
            #print("hedefe gidiyoz")
            self.donus_tamamla(guncel_enlem,guncel_boylam,hedef_enlem,hedef_boylam)
            uzaklik = math.sqrt((hedef_enlem-guncel_enlem)**2 + (hedef_boylam-guncel_boylam)**2)

            if uzaklik < 35:
                if uzaklik < 5:
                    if hedef.amac == INIS:

                        if self.en_yakin_sarj_istasyonuna_git == True:
                            print("ha!")
                            self.dur()
                            self.inis_yap(guncel_enlem,guncel_boylam)

                        if  self.batarya.veri == 100:
                            self.en_yakin_sarj_istasyonuna_git = False
                            self.kaldır = False
                            self.inmek_yasak = False
                            self.irtifa_araliginda = False 
                            
                        else:
                            self.dur()
                            self.inis_yap(guncel_enlem,guncel_boylam)

                    elif self.i == (len(self.en_kisa_rota) - 1):
                        print("abo")
                        self.dur()
                        self.asagi_git(YAVAS)

                    elif self.acil_durum:  
                        print("hehe:)")
                        self.dur()
                        self.inis_yap(guncel_enlem,guncel_boylam)

                    else:  
                        if self.irtifa > 120: 
                            self.irtifa_araliginda = False

                        self.kaldır = False
                        self.inmek_yasak = False
                        self.i +=1 
                else: 

                    if self.inmek_yasak == False and self.hedef_bolge.yukselti > 120:
                        self.dur()
                        self.kaldır = True
                        self.irtifa_araliginda = False

                    else: 

                        if self.yavas == True or uzaklik < 10:
                            self.dur()
                            self.ileri_git(7)

                        else:
                            self.ileri_git(HIZLI)
            else:
                
                if self.yavas == True:
                    self.dur()
                    self.ileri_git(7)

                else:
                    self.ileri_git(HIZLI)

        else:
            print("engel")
            uzaklik = math.sqrt((self.durak_enlem-guncel_enlem)**2 + (self.durak_boylam-guncel_boylam)**2)
            self.donus_tamamla(guncel_enlem,guncel_boylam,self.durak_enlem,self.durak_boylam)

            if uzaklik < 5:  
                self.dur()
                self.yasak = False
                self.trafik_engel = False
            else: 
                if self.yavas == True:
                    self.dur()
                    self.ileri_git(7)
                else:
                    self.ileri_git(HIZLI)

    def run(self):

        if ( self.gnss.enlem == 0 and self.gnss.boylam == 0 ) or self.gnss.spoofing == True:
            self.guncel_enlem += (self.imu.hiz.x/30)
            self.guncel_boylam += (self.imu.hiz.z/30)

        else:
            self.guncel_enlem = self.gnss.enlem
            self.guncel_boylam = self.gnss.boylam

        bolge = self.harita.bolge (self.guncel_enlem, self.guncel_boylam)
        bolgeler[self.id - 1] = bolge
        cezeri[self.id - 1 ] = self

        for i in range (len(bolgeler)):

            if i == (self.id - 1):
                continue
                
            oteki_bolge = bolgeler[i]
            if oteki_bolge == None:
                continue

            oteki_cezeri = cezeri[i]
            if oteki_cezeri == None :
                continue

            cezeriler_arasi_mesafe = math.sqrt((oteki_bolge.enlem - self.guncel_enlem)**2 + (oteki_bolge.boylam - self.guncel_boylam)**2)

            if cezeriler_arasi_mesafe <= 30:

                if self.id < oteki_cezeri.id and self.tr_ok == False:
                    self.trafik_kac = True
                    self.dur()
                    self.tr_ok = True
                        
                elif self.id >= oteki_cezeri.id and self.tr_ok == False:
                    self.trafik_bolge = self.harita.bolge(oteki_bolge.enlem,oteki_bolge.boylam)
                    self.trafik_enlem = oteki_bolge.enlem
                    self.trafik_boylam = oteki_bolge.boylam
                    self.trafik_engel = True
                    self.tr_ok = True

            else:
                self.trafik_kac = False
                self.tr_ok = False

        self.rota_olustur()

        bolge_1= self.harita.bolge(self.guncel_enlem + self.imu.hiz.x, self.guncel_boylam + self.imu.hiz.z)
        bolge_2 = self.harita.bolge(self.guncel_enlem , self.guncel_boylam )

        if bolge_1.yavas_bolge == True or bolge_2.yavas_bolge == True:
            print("yavvas")
            self.yavas = True
        else:
            self.yavas = False

        self.kalkis_yap()
        
        if self.irtifa < 100 and self.irtifa_araliginda == False:
            self.yukari_git(HIZLI)     

        elif self.irtifa > 120 and self.irtifa_araliginda == False and self.inmek_yasak == False and self.kaldır == False:
            self.donus_tamamla(self.guncel_enlem,self.guncel_boylam,self.en_kisa_rota[self.i][0],self.en_kisa_rota[self.i][1])

            if self.lidar.mesafe < 60 :
                self.ileri_git(HIZLI)

            else:
                self.dur()
                self.asagi_git(HIZLI)

        elif bolge_2.yukselti + 20 > self.irtifa and self.irtifa_araliginda == False and self.kaldır == True: 
            self.yukari_git(HIZLI)
            self.inmek_yasak = True

        else:
            self.irtifa_araliginda = True

        if self.irtifa_araliginda == True and self.trafik_kac == False:
            self.git(self.guncel_enlem,self.guncel_boylam,self.en_kisa_rota[self.i][0],self.en_kisa_rota[self.i][1])
            
                 
cezeri_1 = Cezeri(id = 1)

while robot.is_ok():

    (cezeri_1.run())

