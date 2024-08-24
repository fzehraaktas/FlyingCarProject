
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


        """
        for hedef in self.hedefler:
            print("hedef",hedef)"""


    """
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
                #print("hata:",self.motor.hata)
                
    def hiz_kontrol(self, kalkis_enlem, kalkis_boylam, hedef_enlem, hedef_boylam):
        rota_enlem=(hedef_enlem-kalkis_enlem)/40
        rota_boylam=(hedef_boylam-kalkis_boylam)/40

        for i in range (40):
            kalkis_enlem = kalkis_enlem + rota_enlem
            kalkis_boylam = kalkis_boylam + rota_boylam
            bolge = self.harita.bolge(kalkis_enlem, kalkis_boylam)

            if bolge.yavas_bolge == True:
                print("hiz bolgesi")
                return True  
            else:
                return False  
            
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

                """ if self.hiz_kontrol(tum_hedefler[i][0],tum_hedefler[i][1],tum_hedefler[j][0],tum_hedefler[j][1]) == True :
                    x = np.sqrt((tum_hedefler[i][0] - tum_hedefler[j][0]) ** 2 + (tum_hedefler[i][1] - tum_hedefler[j][1]) ** 2)
                    a = 1.7*x 
                else: 
                    """

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
        
        for i in range (200):
            kontrol = False
            self.sag_yasak = False
            engel_enlem = engel_enlem + sag_enlem
            engel_boylam = engel_boylam + sag_boylam
            bolge = self.harita.bolge(engel_enlem,engel_boylam)

            if bolge.ucusa_yasakli_bolge == False and bolge.ruzgar == False and bolge.trafik == False and bolge.yukselti<90:
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


                    if bolgex.ucusa_yasakli_bolge == True or bolgex.ruzgar == True or bolgex.trafik == True or bolgex.yukselti >=90 : #or bolgey.ucusa_yasakli_bolge == True or bolgey.ruzgar == True or bolgey.trafik == True or bolgey.yukselti >=90: 
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
        
        for i in range (200):
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

                    if bolgex.ucusa_yasakli_bolge == True or bolgex.ruzgar == True or bolgex.trafik == True or bolgex.yukselti >=90 : #or bolgey.ucusa_yasakli_bolge == True or bolgey.ruzgar == True or bolgey.trafik == True or bolgey.yukselti >=90: 
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

        print("hedef",hedef_enlem,hedef_boylam)           

        for i in range (100):
            guncel_enlem = guncel_enlem + rota_enlem
            guncel_boylam = guncel_boylam + rota_boylam
            bolge = self.harita.bolge(guncel_enlem, guncel_boylam)

            if bolge.ucusa_yasakli_bolge == True or bolge.ruzgar ==True or bolge.trafik == True or bolge.yukselti>=100 :
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
                if abs(sol_uzaklik - sag_uzaklik)<= 30 and sol_uzaklik > sag_uzaklik:
                    print("sol")
                    self.durak_enlem = self.sol_durak_enlem
                    self.durak_boylam = self.sol_durak_boylam
                 
                """
              
                if sol_uzaklik < sag_uzaklik:
                    #print("sol")
                    self.durak_enlem = self.sol_durak_enlem
                    self.durak_boylam = self.sol_durak_boylam
                    self.yasak = True
                    
                else:
                    #print("sag")
                    self.durak_enlem = self.sag_durak_enlem
                    self.durak_boylam = self.sag_durak_boylam
                    self.yasak = True
                    

                #print("engel",engel_enlem,engel_boylam)
                #print("sag durak", self.sag_durak_enlem , self.sag_durak_boylam)
                #print("sol durak", self.sol_durak_enlem , self.sol_durak_boylam)


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
            
        else:
            pass

    def sarj_hesap (self,guncel_enlem,guncel_boylam,hedef_enlem,hedef_boylam) :
    
        self.hedefe_en_yakin_sarj_istasyonu(hedef_enlem, hedef_boylam)
        uzaklik = math.sqrt((hedef_enlem-guncel_enlem)**2 + (hedef_boylam-guncel_boylam)**2) 
        uzaklik2_sarj = math.sqrt((hedef_enlem-self.sarj2_enlem)**2 + (hedef_boylam-self.sarj2_boylam)**2) 
        bolge = self.harita.bolge(hedef_enlem,hedef_boylam)

        for i, hedef in enumerate(self.hedefler):
            if hedef_enlem == hedef.bolge.enlem and hedef_boylam == hedef.bolge.boylam:
                hedef = self.hedefler[i]
                break

        yakin_sarj = 7
        inis_sarj = (self.barometre.irtifa - bolge.yukselti) * 0.22 
        kalacak_sarj = self.batarya.veri - ((uzaklik-50)* 0.089) - yakin_sarj 

        if uzaklik > 50: 
            if hedef.amac == INIS:
                if kalacak_sarj-inis_sarj < 25:
                    self.en_yakin_sarj_istasyonuna_git = True
                elif  kalacak_sarj -inis_sarj - (uzaklik2_sarj *0.089 ) < 30: 
                    self.en_yakin_sarj_istasyonuna_git = True
                else: 
                    pass
            else:
                if kalacak_sarj < 25:
                    self.en_yakin_sarj_istasyonuna_git = True
                elif  kalacak_sarj - (uzaklik2_sarj * 0.089) < 30: 
                    self.en_yakin_sarj_istasyonuna_git = True
                else : 
                    pass
                           
        else: 
            pass
            #print("KAPLAN")

    def en_yakin_sarj_istasyonu(self, guncel_enlem, guncel_boylam, hedef_enlem, hedef_boylam):

        self.sarj_hesap (guncel_enlem,guncel_boylam,hedef_enlem,hedef_boylam)
        sarj_menzili = ((self.batarya.veri - 40) - 7) / 0.089
        uygun_istasyonlar = []
        en_iyi_istasyon = None
    
        for istasyon in self.harita.sarj_istasyonlari:
            mesafe = math.sqrt((istasyon.enlem-guncel_enlem)**2 + (istasyon.boylam-guncel_boylam)**2)
            if mesafe <= sarj_menzili:
                uygun_istasyonlar.append(istasyon)
    
        en_kisa_mesafe = float('inf')
    
        for istasyon in uygun_istasyonlar:
            toplam_mesafe = math.sqrt((istasyon.enlem-guncel_enlem)**2 + (istasyon.boylam-guncel_boylam)**2)
            toplam_mesafe += math.sqrt((hedef_enlem- istasyon.enlem)**2 + (hedef_boylam - istasyon.boylam)**2)
        
            if toplam_mesafe < en_kisa_mesafe:
                en_kisa_mesafe = toplam_mesafe
                en_iyi_istasyon = istasyon
    
        if en_iyi_istasyon is not None:
            self.sarj_enlem = en_iyi_istasyon.enlem
            self.sarj_boylam = en_iyi_istasyon.boylam

        else:
            pass

        #uzaklik_sarj = math.sqrt((self.sarj_enlem-guncel_enlem)**2 + (self.sarj_boylam-guncel_boylam)**2)
            
    def git(self,guncel_enlem,guncel_boylam,hedef_enlem,hedef_boylam):
    
        if self.acil == True:
            #print("knk acil bak")
            hedef_enlem = self.hastane_enlem
            hedef_boylam = self.hastane_boylam

        #print("hedef",hedef_enlem,hedef_boylam)
        
        self.rota_olustur()
        self.motor_ariza(guncel_enlem,guncel_boylam)
        self.en_yakin_sarj_istasyonu(guncel_enlem, guncel_boylam, hedef_enlem, hedef_boylam)
        
        if self.motor_hata == True or self.motor.hata == 1 :
            print("in")
            bolge = self.harita.bolge(guncel_enlem,guncel_boylam)
            if bolge.inilebilir :
                hedef_enlem = guncel_enlem
                hedef_boylam = guncel_boylam

        if self.en_yakin_sarj_istasyonuna_git == True:
            #print("sarja_git guzel kardesim")
            hedef_enlem = self.sarj_enlem
            hedef_boylam = self.sarj_boylam
            #print("sarj" ,self.sarj_enlem,self.sarj_boylam)

        for i, hedef in enumerate(self.hedefler):
            if hedef_enlem == hedef.bolge.enlem and hedef_boylam == hedef.bolge.boylam:
                hedef = self.hedefler[i]
                break
        
        self.engel_kac(guncel_enlem,guncel_boylam,hedef_enlem,hedef_boylam)
        print("YASAK :",self.yasak)

        if self.yasak == False :
            print("hedefe gidiyoz")
            self.donus_tamamla(guncel_enlem,guncel_boylam,hedef_enlem,hedef_boylam)
            uzaklik = math.sqrt((hedef_enlem-guncel_enlem)**2 + (hedef_boylam-guncel_boylam)**2)
            #print(uzaklik)
            if uzaklik < 20:
                if uzaklik < 5:
                    if hedef.amac == INIS:

                        if self.en_yakin_sarj_istasyonuna_git == True:
                            #print("ha!")
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

        elif self.yasak == True:
            #print("engel")
             
            uzaklik_engel = math.sqrt((self.durak_enlem-guncel_enlem)**2 + (self.durak_boylam-guncel_boylam)**2)
            self.donus_tamamla(guncel_enlem,guncel_boylam,self.durak_enlem,self.durak_boylam)
            print(uzaklik_engel)
                 
            if uzaklik_engel < 10:
                if uzaklik_engel < 7:  
                    self.yasak = False
                else: 
                    self.ileri_git(YAVAS)
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
            self.dur()
            self.irtifa_araliginda = True

        """
        if self.gnss.enlem == 0 and self.gnss.boylam == 0:
            guncel_enlem = self.gercek_enlem
            guncel_boylam = self.gercek_boylam"""

        self.rota_olustur()
        self.hastane(guncel_enlem,guncel_boylam)

        #self.gnss_tamir()      
        #print("acil",self.acil)
        #print("hesaplanan koordinat" , self.gercek_enlem,self.gercek_boylam)
        #print("guncel koordinat", self.gnss.enlem,self.gnss.boylam)
        #print("imu hiz", self.imu.hiz.x,self.imu.hiz.y,self.imu.hiz.z)
        #print("hedef",hedef_enlem,hedef_boylam)
        #print("kalkis",self.enlem,self.boylam)
        #print("koordinat",self.gnss.enlem,self.gnss.boylam)

        """
        for i, sarj in enumerate(self.harita.sarj_istasyonlari):
            print("sarj:",i,sarj.enlem,sarj.boylam)

        for i, hastane in enumerate(self.harita.hastaneler):
            print("hastane:",i,hastane.enlem,hastane.boylam) """

        if self.irtifa_araliginda == True :
            self.git(guncel_enlem,guncel_boylam,self.en_kisa_rota[self.i][0],self.en_kisa_rota[self.i][1])
            

cezeri = Cezeri(id = 1)
while robot.is_ok():

    (cezeri.run())
