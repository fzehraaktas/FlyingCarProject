import math
import itertools

# Trafik
bolgeler = [None, None, None, None, None]
sarj_durumlari = [None, None, None, None, None]
inisebaslandimitrafik = [None, None, None, None, None]
yukseltitrafik = [None, None, None, None, None]

def bolgeler_arasi_mesafe(bolge_1, bolge_2):
    enlem_fark = bolge_1.enlem - bolge_2.enlem
    boylam_fark = bolge_1.boylam - bolge_2.boylam

    return math.sqrt(enlem_fark**2 + boylam_fark**2)
 
# Trafik
bolgeler = [None, None, None, None, None]
sarj_durumlari = [None, None, None, None, None]
inisebaslandimitrafik = [None, None, None, None, None]
yukseltitrafik = [None, None, None, None, None]

def bolgeler_arasi_mesafe(bolge_1, bolge_2):
    enlem_fark = bolge_1.enlem - bolge_2.enlem
    boylam_fark = bolge_1.boylam - bolge_2.boylam

    return math.sqrt(enlem_fark**2 + boylam_fark**2)
 
class Cezeri(CezeriParent):  
    def __init__(self, id = 0):
        super().__init__(id = id, keyboard = False, sensor_mode = NORMAL)
        ##print(self.gnss.irtifa)
        self.baslangic_bolgesi = self.harita.bolge(self.gnss.enlem, self.gnss.boylam)

        self.engelsiniri = 270
        self.birimbatarya = 11
  
        self.test2 = True

        #*******|| Filtre ||********
        self.filteredimux_list = []
        self.filteredimuy_list = []
        self.filteredimuz_list = []
        self.filteredgnssenlem_list = []
        self.filteredgnssboylam_list = []
        self.filteredmanyetometre_list = []
        self.standard_deviation_gnss_enlem = 0
        self.standard_deviation_gnss_boylam = 0
        self.standard_deviation_imu_x = 0
        self.standard_deviation_imu_z = 0
        self.filtered_gnss_enlem = self.FilterData(200, gnssenlem=True)
        self.filtered_gnss_boylam = self.FilterData(200, gnssboylam=True)
        self.filtered_manyetometre = self.FilterData(500, manyetometre=True)
        self.son_GNSS_enlem = self.filtered_gnss_enlem
        self.son_GNSS_boylam = self.filtered_gnss_boylam
        self.son_manyetometre = self.filtered_manyetometre
        self.standard_deviation_gnss_enlem = self.baslangic_bolgesi.enlem - self.filtered_gnss_enlem
        self.standard_deviation_gnss_boylam = self.baslangic_bolgesi.boylam - self.filtered_gnss_boylam
        self.standard_deviation_imu_x = self.FilterData(50, deviationimux=True) 
        self.standard_deviation_imu_z = self.FilterData(50, deviationimuz=True) 
        #*******|| Filtre ||********

        #*********|| FTR ||***********
        self.azami_yukseklik = 280 # gidis 320 gelis 280
        #*********|| FTR ||***********

        #*******|| Batarya ||******** 
        if self.batarya.hata == 1:
            self.kalan_batarya = 80
            self.eski_batarya_veri = 80
        else:
            self.kalan_batarya = self.batarya.veri - 20
            self.eski_batarya_veri = self.batarya.veri - 20

        self.bataryabekle = 0
        self.sonstation = 0
        self.eskibolgeistasyon = 0
        self.eskibolgeistasyon2 = 0
 
        #*******|| Batarya ||******** 

        #*******|| Hedef Bölge Hesabı ||********

        self.siralimi = True
        self.hedefrotasi = self.HedefSirasiniBelirle() # Hedefleri sıralar
        self.hedefrotasi = self.HedefSirasiniDuzenle(self.hedefrotasi)

        self.hedefrotasicount = 0
        self.hedef = self.hedefrotasi[self.hedefrotasicount]
        if hasattr(self.hedefrotasi[self.hedefrotasicount], 'bolge'):
            self.hedef_bolge = self.hedefrotasi[self.hedefrotasicount].bolge
        else:
            self.hedef_bolge = self.hedefrotasi[self.hedefrotasicount]
            self.hedef.amac = 2
        self.baslangicadonulsunmu = False
 
        self.hedefbolgedegistimi_count = 0 
        self.eskihedefler = [(hedef.bolge.enlem, hedef.bolge.boylam) for hedef in self.hedefler]
        #for hedef in self.hedefler:
            #print(hedef, hedef.amac)
        #*******|| Hedef Bölge Hesabı ||********
 
        #*******|| Kalkış yap / İniş yap ||******** 
        self.hedefe_ulasildi = False 
        self.sarj_istasyonuna_ulasildi = False  
        self.hedef_enlemboylam_ulasildi = False  
        self.kalkis_yap = False
        self.yukseklige_ulasildi = False
        self.yenihedefdurcount = 0
        #*******|| Kalkış yap / İniş yap ||********
 
        #*******|| Acil Durum ||********
        self.acildurumdogrulandi = False
        self.hastane_dur_count = 0
        self.hastane_distance = 9999
        #*******|| Acil Durum ||********

        #*******|| Motor Arızası ||********
        self.motorasagigit = False
        self.motorarizasidogrulandi = False
        self.motor_dur_count = 0
        self.motorarizasivar = False
        self.gnssmotorhata = False
        #*******|| Motor Arızası ||********

        #*******|| GNSS Arızası ||********
        self.gnss_dur = 0
        self.gnss_userhata = self.gnss.hata
        self.spoofingbekleme = 0
        self.onceki_zaman_gnss = self.zaman()
        self.gnss_userdata_x = self.filtered_gnss_enlem
        self.gnss_userdata_z = self.filtered_gnss_boylam
        self.gnsshatasidogrulandi = False
        #*******|| GNSS Arızası ||********

        #*******|| Manyetometre Arızası ||********
        self.onceki_zaman_manyetometre = self.zaman()
        self.manyetometre_user_data = self.filtered_manyetometre
        self.previous_gecicideger = 0.0
        #*******|| Manyetometre Arızası ||********

        #*******|| Rota Hesabı ||********
        self.rota = []   
        self.rota_count = 0
        self.arac_x, self.arac_y = self.filtered_gnss_enlem, self.filtered_gnss_boylam
        self.durcount = 0 
        #*******|| Rota Hesabı ||********
        #*******|| Rota Oluşturulması / Kısaltılması ||******** 
        self.arac_yukselti = self.baslangic_bolgesi.yukselti
        self.RotayiYenidenHesapla()
        #*******|| Rota Oluşturulması / Kısaltılması ||******** 

        self.uzunbinadogrulandi = False
        self.uzunbinadaninis = False
        self.sonradarverileri = []
        self.sonlidarverileri = []

        self.sensor_mode = ''
        if self.imu.acisal_hiz.y==0 or self.imu.acisal_hiz.x==0 or self.imu.acisal_hiz.z==0:
            self.sensormode = "DUZELTILMIS"
        else:
            self.sensormode = "NORMAL"

    def run(self):
        super().run()
        ##print(self.manyetometre.veri)
        #*******||Filter||********
        if not self.gnss_userhata or not self.gnss.hata:
            self.filtered_gnss_enlem = self.FilterData(50, gnssenlem=True)
            self.filtered_gnss_boylam = self.FilterData(50, gnssboylam=True)

            #*******||Trafik||******** 

            # bolgetrafik = self.harita.bolge(self.filtered_gnss_enlem, self.filtered_gnss_boylam)

            # if self.tamamlandi:
                # bolgeler[self.id - 1] = None
            # else:
                # bolgeler[self.id - 1] = bolgetrafik
                # sarj_durumlari[self.id - 1] = self.batarya
                # if self.gnss.irtifa < 100:
                #     inisebaslandimitrafik[self.id - 1] = True
                # else:
                #     inisebaslandimitrafik[self.id - 1] = False
                # yukseltitrafik[self.id - 1] = self.gnss.irtifa

                # bekle = False

                # for i in range(len(bolgeler)):
                #     if i == self.id - 1:
                #         continue

                #     oteki_bolge = bolgeler[i]            
                #     if oteki_bolge == None:
                #         continue
                #     oteki_sarj = sarj_durumlari[i]

                #     cezeriler_arasi_mesafe = bolgeler_arasi_mesafe(oteki_bolge, bolgetrafik)
                #     if cezeriler_arasi_mesafe <= 65:

                #         batarya_veri = round(self.batarya.veri, 0)
                #         oteki_batarya_veri = round(oteki_sarj.veri, 0)
                #         inisebasladimiben = inisebaslandimitrafik[self.id - 1]
                #         inisebasladimioteki = inisebaslandimitrafik[i]
                #         yukseltiben = self.id - 1
                #         yukseltioteki = i

                #         if not inisebasladimiben and inisebasladimioteki:
                #             self.dur()
                #             bekle = True
                #         elif yukseltiben<yukseltioteki:
                #             bekle = True
                #             self.dur()

                #         if inisebasladimiben:
                #             bekle = False
                
                # if bekle:
                #     self.dur()
                #     return

            #*******||Trafik||******** 
     
        if not self.manyetometre.hata:
            self.filtered_manyetometre = self.FilterData(100, manyetometre=True)
        #*******||Filter||********

        #*******|| Kalkış / Bitiş / İniş||********
        if self.uzunbinadogrulandi:
            #if self.UzunBinayaKalkisYap():
             #   self.uzunbinadogrulandi = False
            #else:
               # return
            pass

        if self.hedef_bolge.yukselti < 280:
            if self.barometre.hata:
                if self.gnss.hata:
                    pass
                else:
                    if self.gnss.irtifa > 350 or self.uzunbinadaninis:
                        self.sonlidarverileri.append(self.lidar.mesafe)
                        if len(self.sonlidarverileri)>15:
                            self.sonlidarverileri.pop(0)
                        self.uzunbinadaninis = True
                        if self.lidar.hata:
                            self.sonradarverileri.append(self.radar.mesafe)
                            if len(self.sonradarverileri)>15:
                                self.sonradarverileri.pop(0)
                            if self.radar.hata:
                                pass 
                            else:
                                if all(value > 100 for value in self.sonradarverileri):
                                    if self.UzunBinadanInisYap(True):
                                        return
                        else:
                            if all(value > 100 for value in self.sonlidarverileri):
                                if self.UzunBinadanInisYap(True):
                                    return
            else:
                if self.barometre.irtifa > 350 or self.uzunbinadaninis:
                    self.sonlidarverileri.append(self.lidar.mesafe)
                    if len(self.sonlidarverileri)>15:
                        self.sonlidarverileri.pop(0)
                    self.uzunbinadaninis = True
                    if self.lidar.hata:
                        self.sonradarverileri.append(self.radar.mesafe)
                        if len(self.sonradarverileri)>15:
                            self.sonradarverileri.pop(0)
                        if self.radar.hata:
                            pass
                        else:
                            if all(value > 100 for value in self.sonradarverileri):
                                if self.UzunBinadanInisYap():
                                    return
                    else:
                        if all(value > 100 for value in self.sonlidarverileri):
                            if self.UzunBinadanInisYap():
                                return
                
        if not self.kalkis_yap: 
            if self.KalkisYap():
                pass
            else:
                return
        if self.sarj_istasyonuna_ulasildi:
            if self.batarya.hata:
                if self.bataryabekle < 100:
                    self.bataryabekle += 1
                    return
                else:
                    pass
            else:
                if self.batarya.veri <= 98.9: 
                    return
                else:
                    self.hedefrotasicount += 1
                    if hasattr(self.hedefrotasi[self.hedefrotasicount], 'bolge'):
                        self.hedef = self.hedefrotasi[self.hedefrotasicount]
                        self.hedef_bolge = self.hedefrotasi[self.hedefrotasicount].bolge
                    else:
                        if len(self.hedefrotasi) <= (self.hedefrotasicount + 1):
                            if self.baslangica_don: 
                                self.hedef.amac = 0
                                self.hedef_bolge = self.hedefrotasi[self.hedefrotasicount]
                        else:             
                            self.hedef.amac = 2
                            self.hedef_bolge = self.hedefrotasi[self.hedefrotasicount]
                            
                    # Rota
                    self.rota = []
                    self.rota_count = 0
                    self.arac_x, self.arac_y = self.filtered_gnss_enlem, self.filtered_gnss_boylam
                    self.durcount = 0

                    # Kalkış Yap / Hedefe Ulaşıldı
                    self.hedefe_ulasildi = False
                    self.hedef_enlemboylam_ulasildi =False
                    self.kalkis_yap = False
                    self.yukseklige_ulasildi = False
                    self.RotayiYenidenHesapla()

                    self.sarj_istasyonuna_ulasildi = False

                    return
        if self.hedefe_ulasildi:
            return
        if self.gnsshatasidogrulandi:
            self.HedefeinisYap(gnsshata = True)
            return
        if self.hedef_enlemboylam_ulasildi:
            self.HedefeinisYap()
            return
        #*******|| Kalkış / Bitiş / İniş||********

        #*******||Spoff Detect / GNSS Detect||********
        if self.gnss_userhata == 0: 
            if self.spoofingbekleme<50:
                self.spoofingbekleme += 1
            elif self.son_GNSS_enlem > self.filtered_gnss_enlem+15 or self.son_GNSS_enlem < self.filtered_gnss_enlem-15:
                self.gnss_userhata = 1
        if self.gnss.hata == 1:
            self.gnss_userhata = 1
        if self.gnss_userhata == 0:
            self.son_GNSS_enlem = self.filtered_gnss_enlem
            self.son_GNSS_boylam = self.filtered_gnss_boylam
            self.son_manyetometre = self.filtered_manyetometre 

            self.gnss_userdata_x = self.filtered_gnss_enlem
            self.gnss_userdata_z = self.filtered_gnss_boylam
            self.onceki_zaman_gnss = self.zaman()
        else:
            if self.gnss_dur < 1:
                self.dur()
                self.gnss_dur += 1
                return

            dt = self.zaman() - self.onceki_zaman_gnss
            self.onceki_zaman_gnss = self.zaman()
            self.gnss_userdata_x += self.FilterData(100, imux=True) * dt
            self.gnss_userdata_z += self.FilterData(100, imuz=True) * dt
            
            self.filtered_gnss_enlem = self.gnss_userdata_x
            self.filtered_gnss_boylam = self.gnss_userdata_z 
        
        #*******||Spoff Detect / GNSS Detect||******** 
        
        if self.yukseklige_ulasildi or self.gnss_userhata == 0:
            #*******|| Hedef Değişti mi? / Başlangıca Dönülsün mü? ||********
            if self.motorarizasivar or self.acildurumdogrulandi:
                hedef_bolge_degistimi = False
            else:
                yenihedefler = [(hedef.bolge.enlem, hedef.bolge.boylam) for hedef in self.hedefler]
                if self.eskihedefler == yenihedefler: 
                    hedef_bolge_degistimi = False
                else:
                    if self.hedefbolgedegistimi_count < 10:
                        self.dur()
                        self.hedefbolgedegistimi_count += 1 
                        return
                    else:
                        self.hedefbolgedegistimi_count = 0
                        hedef_bolge_degistimi = True
                        self.eskihedefler = [(hedef.bolge.enlem, hedef.bolge.boylam) for hedef in self.hedefler]
             
            if not hedef_bolge_degistimi:  
                pass
            else:
                self.hedefrotasi = self.HedefSirasiniBelirle() # Hedefleri sıralar
                self.hedefrotasi = self.HedefSirasiniDuzenle(self.hedefrotasi)
                self.hedefbolgedegistimi_count = 0
                self.hedef = self.hedefrotasi[self.hedefrotasicount]
                if hasattr(self.hedefrotasi[self.hedefrotasicount], 'bolge'):
                    self.hedef_bolge = self.hedefrotasi[self.hedefrotasicount].bolge
                else:
                    self.hedef_bolge = self.hedefrotasi[self.hedefrotasicount]

                #*******|| Kalkış yap / İniş yap ||********
                self.hedefe_ulasildi = False   
                self.hedef_enlemboylam_ulasildi =False
                self.kalkis_yap = False
                self.yukseklige_ulasildi = False
                self.yenihedefdurcount = 0
                #*******|| Kalkış yap / İniş yap ||********

                #*******|| Acil Durum ||********
                self.acildurumdogrulandi = False
                self.hastane_dur_count = 0
                self.hastane_distance = 9999
                #*******|| Acil Durum ||********

                #*******|| Motor Arızası ||********
                self.motorasagigit = False
                self.motorarizasidogrulandi = False
                self.motor_dur_count = 0
                #*******|| Motor Arızası ||********

                #*******|| GNSS Arızası ||********
                self.gnss_dur = 0

                self.gnss_userhata = self.gnss.hata
                #*******|| GNSS Arızası ||********

                #*******|| Rota Hesabı ||********
                self.rota = []
                self.rota_count = 0
                self.arac_x, self.arac_y = self.filtered_gnss_enlem, self.filtered_gnss_boylam
                self.durcount = 0 
                #*******|| Rota Hesabı ||********

                self.RotayiYenidenHesapla()

                return
 
            #*******|| Hedef Değişti mi? / Başlangıca Dönülsün mü? ||********
            #*******|| Acil Durum ||********
            if self.acil_durum and not self.acildurumdogrulandi:
                if self.hastane_dur_count < 10: 
                    self.dur() 
                    self.hastane_dur_count += 1 
                    return 
                else: 
                    self.acildurumdogrulandi = True
                    self.hedef_bolge.enlem, self.hedef_bolge.boylam, yukselti = self.EnYakinHastaneyiBul()

                    # Rota
                    self.rota = []
                    self.rota_count = 0
                    self.arac_x, self.arac_y = self.filtered_gnss_enlem, self.filtered_gnss_boylam
                    self.durcount = 0

                    # Kalkış Yap / Hedefe Ulaşıldı
                    self.hedefe_ulasildi = False
                    self.hedef_enlemboylam_ulasildi =False
                    self.kalkis_yap = False
                    self.yukseklige_ulasildi = False

                    self.RotayiYenidenHesapla()

                    return
            #*******|| Acil Durum ||********

            #*******|| Motor Arızası ||********
            if 0 in self.motor.rpm: # MOTOR BOZULDU MU
                self.motorarizasivar = True

                if self.motor_dur_count < 5: 
                    self.dur()
                    self.motor_dur_count += 1
                    return
                elif self.motor_dur_count == 5:
                    # EN YAKIN BOLGEYI BUL
                    inilebilir_bolgeler = []
                    inilebilir_bolgeler = self.EnYakinInilebilirBolgeyiBul(self.filtered_gnss_enlem, self.filtered_gnss_boylam) # (x, y) 1ms
                    distance1 = 9999
                    inis_bolgesi = []

                    for bolge in inilebilir_bolgeler:
                        distance = math.sqrt((bolge.enlem-self.filtered_gnss_enlem)**2+(bolge.boylam-self.filtered_gnss_boylam)**2)
                        if distance < distance1:
                            distance1 = distance
                            inis_bolgesi = bolge 

                    self.hedef_bolge.enlem = inis_bolgesi.enlem
                    self.hedef_bolge.boylam = inis_bolgesi.boylam
                    self.motor_dur_count += 1
                    return 
                else:
                    mesafex, mesafey = self.hedef_bolge.enlem - self.filtered_gnss_enlem, self.hedef_bolge.boylam - self.filtered_gnss_boylam
                    if abs(mesafey) < 5 and abs(mesafex) < 5 or self.gnssmotorhata: 
                        if self.gnss_userhata:
                            self.gnssmotorhata = True
                        else:
                            self.gnssmotorhata = False
                        self.HedefeinisYap()
                        return
                    else:
                        if self.motor_dur_count == 6:
                            self.dur()
                            self.motor_dur_count += 1
                            return
                        else:
                            if self.gnss_userhata:
                                #self.ileri_git(HIZLI)
                                self.HedefeDon(self.hedef_bolge.enlem, self.hedef_bolge.boylam, self.filtered_gnss_enlem, self.filtered_gnss_boylam)
                            else:
                                self.HedefeDon(self.hedef_bolge.enlem, self.hedef_bolge.boylam, self.filtered_gnss_enlem, self.filtered_gnss_boylam)
                            return
            #*******|| Motor Arızası ||********

            #**|| Hedef Bölgesine git ||**
            if self.rota[self.rota_count] == self.rota[-1]:
                hedefx, hedefy = self.hedef_bolge.enlem, self.hedef_bolge.boylam
                mesafe_x, mesafe_y = hedefx - self.filtered_gnss_enlem, hedefy - self.filtered_gnss_boylam
                if self.gnss_userhata:
                    katsayideger = 10 
                    test1 = False
                elif self.manyetometre.hata:
                    katsayideger = 4.5
                    test1 = False
                else:  
                    katsayideger = 4.5
                    test1 = True  

                if abs(mesafe_y) < katsayideger and abs(mesafe_x) < katsayideger:
                    self.test2 = True
                    self.hedef_enlemboylam_ulasildi = True

                    if self.hedef.amac == 0: 
                        if self.gnss_userhata: 
                            self.gnsshatasidogrulandi = True
                            return
                        else:
                            self.HedefeinisYap()
                            if self.lidar.mesafe>15 and not self.lidar.hata:
                                self.HedefeDon(hedefx, hedefy, self.filtered_gnss_enlem, self.filtered_gnss_boylam)
                            elif self.radar.mesafe>15 and not self.radar.hata:
                                self.HedefeDon(hedefx, hedefy, self.filtered_gnss_enlem, self.filtered_gnss_boylam)
                    elif self.hedef.amac == 1:
                        if self.yenihedefdurcount < 10: 
                            self.dur()
                            self.yenihedefdurcount += 1  
                            return
                        else:
                            #print("TEST1")
                            self.yenihedefdurcount = 0
                            self.hedefrotasicount += 1
                            if hasattr(self.hedefrotasi[self.hedefrotasicount], 'bolge'):
                                #print("TEST3")
                                self.hedef = self.hedefrotasi[self.hedefrotasicount]
                                self.hedef_bolge = self.hedefrotasi[self.hedefrotasicount].bolge
                            else:
                                #print("TEST2", self.baslangica_don)
                                if len(self.hedefrotasi) <= (self.hedefrotasicount + 1):
                                    if self.baslangica_don: 
                                        self.hedef.amac = 0
                                        self.hedef_bolge = self.hedefrotasi[self.hedefrotasicount]
                                    else:  
                                        pass
                                
                                else:             
                                    self.hedef.amac = 2
                                    self.hedef_bolge = self.hedefrotasi[self.hedefrotasicount]
                                  
                            # Rota
                            self.rota = []
                            self.rota_count = 0
                            self.arac_x, self.arac_y = self.filtered_gnss_enlem, self.filtered_gnss_boylam
                            self.durcount = 0

                            # Kalkış Yap / Hedefe Ulaşıldı
                            self.hedefe_ulasildi = False
                            self.hedef_enlemboylam_ulasildi =False
                            self.kalkis_yap = False
                            self.yukseklige_ulasildi = False
                            self.RotayiYenidenHesapla()

                            return
                    elif self.hedef.amac == 2:
                        self.hedef_enlemboylam_ulasildi = False
                        self.SarjIstasyonunainisYap()
                        return
                
                elif abs(mesafe_y) < katsayideger+20 and abs(mesafe_x) < katsayideger+20 and test1 and self.test2: 
                    self.dur()
                    self.test2 = False

                elif abs(mesafe_y) < katsayideger+27 and abs(mesafe_x) < katsayideger+27 and self.hedef_bolge.yukselti>100 and self.test2: 
                    self.dur()
                    self.uzunbinadogrulandi = True
                    self.test2 = False
                    return
                
                else:
                    if self.gnss_userhata and False:
                        self.ileri_git(HIZLI)
                    else:
                        self.HedefeDon(hedefx, hedefy, self.filtered_gnss_enlem, self.filtered_gnss_boylam)
            #**|| Hedef Bölgesine git ||**
            #**|| Way Pointe git ||**
            else:
                hedefx, hedefy = self.rota[self.rota_count][0], self.rota[self.rota_count][1]

                mesafe_x, mesafe_y = hedefx - self.filtered_gnss_enlem, hedefy - self.filtered_gnss_boylam

                if abs(mesafe_y) < 15 and abs(mesafe_x) < 15: 

                    #*| Ne kadar duracağını belirle |*
                    if self.rota[self.rota_count+1][2]:  
                        durcount1 = 5 
                    elif self.rota[self.rota_count+1][3]:
                        durcount1 = 50
                    elif self.rota[self.rota_count+1][4]:
                        durcount1 = 50
                    elif self.rota[self.rota_count+1] == self.rota[-1]:
                        durcount1 = 1
                    else:
                        durcount1 = 0
                        aci = math.atan2(self.hedef_bolge.boylam - self.filtered_gnss_boylam, self.hedef_bolge.enlem - self.filtered_gnss_enlem)
                        aci_farki = aci - self.filtered_manyetometre
                        aci_farki = (aci_farki + math.pi) % (2 * math.pi) - math.pi
                        
                        if abs(aci_farki) > 0.05:
                            durcount1 = 1
                        else:
                            durcount1 = 0

                    if self.durcount < durcount1:
                        self.dur()
                        self.durcount += 1
                        return
                    else:
                        self.durcount = 0
                        self.rota_count += 1
                        return
                else:
                    if self.gnss_userhata and False:
                        self.ileri_git(HIZLI)
                    else:
                        self.HedefeDon(hedefx, hedefy, self.filtered_gnss_enlem, self.filtered_gnss_boylam)
            #**|| Way Pointe git ||**
 
    # Verilen 2 bölge arasını istenilen parçaya bölüp engel var mı yok mu bilgisini saklar
    def AradaEngelVarmi(self, bolge1, bolge2, segment_length=1):
        arac_x, arac_y = bolge1[0], bolge1[1]
        hedefenlem, hedefboylam = bolge2[0], bolge2[1]
        angle = 0

        total_distance = math.sqrt((hedefenlem - arac_x) ** 2 + (hedefboylam - arac_y) ** 2)
    
        # Determine the number of segments
        num_segments = int(total_distance // segment_length)
        
        # Calculate the direction vector
        direction_x = (hedefenlem - arac_x) / total_distance
        direction_y = (hedefboylam - arac_y) / total_distance

        waypoints = []
        for i in range(num_segments + 1):
            new_x = arac_x + i * segment_length * direction_x
            new_y = arac_y + i * segment_length * direction_y
            waypoints.append((new_x, new_y))
        
        # Add the target point to ensure it is included as the final waypoint
        waypoints.append((hedefenlem, hedefboylam))

        for wp in waypoints:
            bolge = self.harita.bolge(wp[0], wp[1])
            bolge1 = self.harita.bolge(wp[0]+2.5, wp[1]+2.5)
            bolge2 = self.harita.bolge(wp[0]-2.5, wp[1]-2.5)
            bolge3 = self.harita.bolge(wp[0]+2.5, wp[1]-2.5)
            bolge4 = self.harita.bolge(wp[0]-2.5, wp[1]+2.5)

            if bolge.yukselti > self.engelsiniri: # Engel Var mı?
                return True

            elif bolge.ruzgar or bolge1.ruzgar or bolge2.ruzgar or bolge3.ruzgar or bolge4.ruzgar: 
                return True

            elif bolge.ucusa_yasakli_bolge or bolge1.ucusa_yasakli_bolge or bolge2.ucusa_yasakli_bolge or bolge3.ucusa_yasakli_bolge or bolge4.ucusa_yasakli_bolge:
                return True

            elif bolge.yavas_bolge or bolge1.yavas_bolge or bolge2.yavas_bolge or bolge3.yavas_bolge or bolge4.yavas_bolge:
                return True

            else:
                pass 

        return False

    # Başlangıca Döner
    def BaslangicaDon(self):
        return self.baslangic_bolgesi
    
    # Engeli geçmek için en yakın alternatif yola olan açıyı verir
    def EngelGec(self, aracx, aracy, angle_radyan, ngl = 181, senaryo = ''):
        orjinal_angle = math.degrees(angle_radyan)
        if orjinal_angle > 180:
            orjinal_angle -= 360
        elif orjinal_angle < -180:
            orjinal_angle += 360
        orjinal_angle = round(orjinal_angle)

        blok_boyutu = 20
        if senaryo == '':
            angle_katsayisi = 30
        elif senaryo == 'RUZGARLIBOLGE':
            angle_katsayisi = 75
        elif senaryo == 'YASAKLIBOLGE':
            angle_katsayisi = 45
        elif senaryo == 'YAVASBOLGE':
            angle_katsayisi = 30

        angle_katsayisi_siniri = ngl

        alternatif_yol = False
        
        # Alternatif yolları bul
        for angle_offset in range(angle_katsayisi, angle_katsayisi_siniri, angle_katsayisi):
            for sign in [1, -1]:  # 2 Tarafıda kontrol et: left (-1) and right (+1)
                test_angle = orjinal_angle + sign * angle_offset
        
                # Açı (-180,180) arasında olması lazım
                if test_angle > 180:
                    test_angle -= 360
                elif test_angle < -180:
                    test_angle += 360
                
                # Eğer yol temiz ise oradan git
                if senaryo == '':
                    # Yeni konumu hesapla
                    new_x, new_y = self.EngelTespit(aracx, aracy, test_angle, 25, False)
                    test_x, test_y = self.EngelTespit(aracx, aracy, test_angle, 20, False)
                    test2_x, test2_y = self.EngelTespit(aracx, aracy, test_angle, 10, False)
                    test3_x, test3_y = self.EngelTespit(aracx, aracy, test_angle, 5, False)
                    if not self.harita.bolge(new_x, new_y).ruzgar and not self.harita.bolge(new_x, new_y).ucusa_yasakli_bolge:
                        if self.harita.bolge(new_x, new_y).yukselti < self.engelsiniri and self.harita.bolge(test_x, test_y).yukselti < self.engelsiniri and self.harita.bolge(test2_x, test2_y).yukselti < self.engelsiniri and self.harita.bolge(test3_x, test3_y).yukselti < self.engelsiniri:
                            alternatif_yol = True
                            break
                    
                elif senaryo == 'RUZGARLIBOLGE':
                    # Yeni konumu hesapla
                    new_x, new_y = self.EngelTespit(aracx, aracy, test_angle, 30, False)
                    test_x, test_y = self.EngelTespit(aracx, aracy, test_angle, 25, False)
                    test2_x, test2_y = self.EngelTespit(aracx, aracy, test_angle, 20, False)
                    test3_x, test3_y = self.EngelTespit(aracx, aracy, test_angle, 10, False)
                    test4_x, test4_y = self.EngelTespit(aracx, aracy, test_angle, 5, False)
                    if self.harita.bolge(new_x, new_y).yukselti < self.engelsiniri and not self.harita.bolge(new_x, new_y).ucusa_yasakli_bolge:
                        if not self.harita.bolge(new_x, new_y).ruzgar and not self.harita.bolge(test_x, test_y).ruzgar and not self.harita.bolge(test2_x, test2_y).ruzgar and not self.harita.bolge(test3_x, test3_y).ruzgar and not self.harita.bolge(test4_x, test4_y).ruzgar:
                            alternatif_yol = True
                            break
                    
                elif senaryo == 'YASAKLIBOLGE':
                    new_x, new_y = self.EngelTespit(aracx, aracy, test_angle, 30, False)
                    test_x, test_y = self.EngelTespit(aracx, aracy, test_angle, 25, False)
                    test2_x, test2_y = self.EngelTespit(aracx, aracy, test_angle, 20, False)
                    test3_x, test3_y = self.EngelTespit(aracx, aracy, test_angle, 10, False)
                    test4_x, test4_y = self.EngelTespit(aracx, aracy, test_angle, 5, False)
                    if not self.harita.bolge(new_x, new_y).ruzgar and self.harita.bolge(new_x, new_y).yukselti < self.engelsiniri:
                        if not self.harita.bolge(new_x, new_y).ucusa_yasakli_bolge and \
                        not self.harita.bolge(test4_x, test4_y).ucusa_yasakli_bolge and \
                        not self.harita.bolge(test3_x, test3_y).ucusa_yasakli_bolge and \
                        not self.harita.bolge(test2_x, test2_y).ucusa_yasakli_bolge and \
                        not self.harita.bolge(test_x, test_y).ucusa_yasakli_bolge:
                            alternatif_yol = True
                            break
                            alternatif_yol = True
                            break

                elif senaryo == 'YAVASBOLGE':
                    if not self.harita.bolge(new_x, new_y).ruzgar and not self.harita.bolge(new_x, new_y).ucusa_yasakli_bolge and self.harita.bolge(new_x, new_y).yukselti < self.engelsiniri:
                        if not self.harita.bolge(new_x, new_y).yavas_bolge and not self.harita.bolge(test_x, test_y).yavas_bolge and not self.harita.bolge(test2_x, test2_y).yavas_bolge:
                            alternatif_yol = True
                            break
                    
            if alternatif_yol:
                break
        
        if alternatif_yol: # Alternatif yol var ise
            # Cezeriyi o açıya döndür ve düz git
            current_angle = test_angle
            return new_x, new_y
        else:
            return 0,0

    # 20m ötedeki alanın irtifasını ölçerek engel olup olmadığını 2. kez doğrular
    def EngelTespit(self, Ax, Ay, angle_ra, blokboyutu = 20, radianorangle = True):
        # Açıyı Derece Cinsinden Bul
        if radianorangle:
            angle = math.degrees(angle_ra) # [-180,180]
        else:
            angle = angle_ra 
        
        if angle > 180: # [-180, 180]
            angle -= 360
        elif angle < -180:
            angle += 360
        angle_round = round(angle) 

        blok_boyutu = blokboyutu # 20 metre

        if angle_round == 0:
            new_Ax = Ax + blok_boyutu
            new_Ay = Ay
        elif angle_round == 45:
            new_Ax = Ax + blok_boyutu / math.sqrt(2)
            new_Ay = Ay + blok_boyutu / math.sqrt(2)
        elif angle_round == 90:
            new_Ax = Ax
            new_Ay = Ay + blok_boyutu
        elif angle_round == 135:
            new_Ax = Ax - blok_boyutu / math.sqrt(2)
            new_Ay = Ay + blok_boyutu / math.sqrt(2)
        elif abs(angle_round) == 180:
            new_Ax = Ax - blok_boyutu
            new_Ay = Ay
        elif angle_round == -135:
            new_Ax = Ax - blok_boyutu / math.sqrt(2)
            new_Ay = Ay - blok_boyutu / math.sqrt(2)
        elif angle_round == -90:
            new_Ax = Ax
            new_Ay = Ay - blok_boyutu
        elif angle_round == -45:
            new_Ax = Ax + blok_boyutu / math.sqrt(2)
            new_Ay = Ay - blok_boyutu / math.sqrt(2)
        else:
            radian_angle = math.radians(angle)
            new_Ax = Ax + blok_boyutu * math.cos(radian_angle)
            new_Ay = Ay + blok_boyutu * math.sin(radian_angle)

        return new_Ax, new_Ay

    # En Yakın hastaneyi bulur
    def EnYakinHastaneyiBul(self):
        yeniHedefx = 0
        yeniHedefy = 0
        yeniHedefz = 0
        
        for hastane in self.harita.hastaneler:
            distance1 = math.sqrt((hastane.enlem-self.filtered_gnss_enlem)**2 + (hastane.boylam-self.filtered_gnss_boylam)**2)
            if distance1 < self.hastane_distance:
                self.hastane_distance = distance1
                yeniHedefx = hastane.enlem
                yeniHedefy = hastane.boylam
                yeniHedefz = hastane.yukselti

        self.hastane_distance = 9999
        return yeniHedefx, yeniHedefy, yeniHedefz
    
    # En Yakın iniş bölgesini bulur
    def EnYakinInisBolgesiniBul(self):
        yeniHedefx = 0
        yeniHedefy = 0
        yeniHedefz = 0
        
        for inisbolgesi in self.harita.inis_bolgeleri:
            distance1 = math.sqrt((inisbolgesi.enlem-filtered_gnss_enlem)**2 + (inisbolgesi.boylam-self.filtered_gnss_boylam)**2)
            if distance1 < self.hastane_distance:
                self.hastane_distance = distance1
                yeniHedefx = inisbolgesi.enlem
                yeniHedefy = inisbolgesi.boylam
                yeniHedefz = inisbolgesi.yukselti

        self.inisbolgesi_distance = 9999
        return yeniHedefx, yeniHedefy, yeniHedefz

    # En Yakın iniş bölgesini bulur
    def EnYakinInilebilirBolgeyiBul(self, x, y):
        inilebilirbolgeler = []
        blokboyutu1 = 0
        bolge = self.harita.bolge(x, y)
        if bolge.inilebilir:
            inilebilirbolgeler.append(bolge)
            return inilebilirbolgeler
        for _ in range(100):
            blokboyutu1 += 20
            for angle in range(-180, 180, 10):
                bolge_x, bolge_y = self.EngelTespit(x, y, angle, blokboyutu=blokboyutu1, radianorangle=False) # 20m sonranin x ve y sini verir
                bolge = self.harita.bolge(bolge_x, bolge_y)
                if bolge.inilebilir:
                    inilebilirbolgeler.append(bolge)
            if len(inilebilirbolgeler) > 0:
                break
        return inilebilirbolgeler  

    # Verilen Hedefe Döner ve Düz Gider
    def HedefeDon(self, hedef_x, hedef_y, arac_x, arac_y, duzgit=True): 
        hizkatsayisi = 1.5
        aci = math.atan2(hedef_y - arac_y, hedef_x - arac_x)
        DEAD_ZONE = 0.1
                
        if self.manyetometre.hata:
            gecicideger = self.FilterData(100, acisalhiz=True)

            current_time = self.zaman()
            dt = current_time - self.onceki_zaman_manyetometre
            self.onceki_zaman_manyetometre = current_time
            
            # Apply damping to reduce the effect of sudden large changes
            self.manyetometre_user_data -= gecicideger * dt
            self.filtered_manyetometre = self.manyetometre_user_data
            
            aci_farki = aci - self.manyetometre_user_data
            
            magnitude = 0.02
            hizkatsayisi = 0.2
        else:
            if self.filtered_manyetometre > math.pi - 0.3:  # Adjust the threshold as necessary
                self.filtered_manyetometre -= 2 * math.pi
            elif self.filtered_manyetometre < -math.pi + 0.3:
                self.filtered_manyetometre += 2 * math.pi
                
            self.manyetometre_user_data = self.filtered_manyetometre
            aci_farki = aci - self.filtered_manyetometre
            self.onceki_zaman_manyetometre = self.zaman() 

            if self.motorarizasivar and self.gnss_userhata:
                magnitude = 0.05
                hizkatsayisi = 1 
            elif self.gnss_userhata:
                magnitude = 0.005
            else:
                magnitude = 0.01
                if self.hedef_enlemboylam_ulasildi:
                    magnitude = 0.008
                    hizkatsayisi = 0.75

        aci_farki = (aci_farki + math.pi) % (2 * math.pi) - math.pi

        if abs(aci_farki) < magnitude: 
            if duzgit:
                newx, newy = self.EngelTespit(self.filtered_gnss_enlem, self.filtered_gnss_boylam, self.filtered_manyetometre)
                if self.harita.bolge(newx, newy).yavas_bolge or self.harita.bolge(self.filtered_gnss_enlem, self.filtered_gnss_boylam).yavas_bolge:
                    self.ileri_git(YAVAS)
                else:
                    self.ileri_git(HIZLI)
            else:
                pass
        else:
            if self.manyetometre.hata:
                self.don(aci_farki)
            else: 
                if self.gnss_userhata:
                    if aci_farki>0.05:
                        self.dur()
                    self.don(aci_farki * hizkatsayisi)
                else:
                    self.don(aci_farki * hizkatsayisi)
     
    # İniş yapar
    def HedefeinisYap(self, gnsshata=False):
        self.dur()
        bolge = self.harita.bolge(self.filtered_gnss_enlem, self.filtered_gnss_boylam)
        if bolge.inilebilir or gnsshata:
            if self.lidar.hata:
                if self.radar.hata:
                    self.asagi_git(YAVAS)
                else:  
                    if self.radar.mesafe <= 5:
                        self.hedefe_ulasildi = True
                        return True
                    elif self.radar.mesafe <= 15:
                        self.asagi_git(YAVAS)
                        return False
                    else:
                        self.asagi_git(HIZLI)
                        return False
                
            else:
                if self.lidar.mesafe <= 5:
                    self.hedefe_ulasildi = True
                    return True
                elif self.lidar.mesafe <= 15:
                    self.asagi_git(YAVAS)
                    return False
                else:
                    self.asagi_git(HIZLI)
                    return False
            
        else:
            self.ileri_git(YAVAS) # EKSIK: Hedefe don sonra yavasca ileri git.
            return False
        
    # Şarj bölgesine iniş yapar sonra kalkar
    def SarjIstasyonunainisYap(self, gnsshata=False):
        self.dur()
        bolge = self.harita.bolge(self.filtered_gnss_enlem, self.filtered_gnss_boylam)
        if bolge.inilebilir or gnsshata:
            if self.lidar.hata:
                if self.radar.hata:
                    self.asagi_git(YAVAS)
                else:
                    if self.radar.mesafe <= 2:
                        self.sarj_istasyonuna_ulasildi = True
                        return True
                    elif self.radar.mesafe <= 15:
                        self.asagi_git(YAVAS)
                        return False
                    else:
                        self.asagi_git(HIZLI)
                        return False
               
            else:
                if self.lidar.mesafe <= 2:
                    self.sarj_istasyonuna_ulasildi = True
                    return True
                elif self.lidar.mesafe <= 15:
                    self.asagi_git(YAVAS)
                    return False
                else:
                    self.asagi_git(HIZLI)
                    return False
            
        else:
            self.ileri_git(YAVAS) # EKSIK: Hedefe don sonra yavasca ileri git.
            return False
     
    # Gidilecek hedefleri sıralar: Hedefler sırasız iseler en uygun mesafeye göre sıralar
    def HedefSirasiniBelirle(self):
        sira = [None] * len(self.hedefler)
        self.siralimi = True

        for hedef in self.hedefler:
            if hedef.sira == -1:
                sira.append(hedef)
            elif hedef.sira == 0:
                sira.insert(0, hedef)
                self.siralimi = False
            else:
                sira[hedef.sira-1] = hedef
        
        return [i for i in sira if i is not None]

    def HedefSirasiniDuzenle(self, sira):
        if not self.siralimi and len(sira)>2:
            best_order = None
            best_distance = 9999  

            sira.insert(0, self.baslangic_bolgesi)
            middle_part = sira[1:-1] 

            for perm in itertools.permutations(middle_part):
                total_distance = self.distance(sira[0], perm[0])  # From start to the first permuted element
                for i in range(1, len(perm)):
                    total_distance += self.distance(perm[i-1], perm[i])
                total_distance += self.distance(perm[-1], sira[-1])  # From the last permuted element to the end
                
                # Check if this is the shortest path found
                if total_distance < best_distance:  
                    best_distance = total_distance
                    best_order = perm

            # Rebuild the sira list with the best middle order
            sira = [sira[0]] + list(best_order) + [sira[-1]]
        else: 
            sira.insert(0, self.baslangic_bolgesi)

        if self.baslangica_don:
            sira.append(self.baslangic_bolgesi)

        sira = self.ensure_battery_capacity(sira) 

        del sira[0]

        seen = set()
        new_sira = []
        for hedef in sira:
            if hasattr(hedef, 'bolge'):
                enlem_boylam = (hedef.bolge.enlem, hedef.bolge.boylam)
            else:
                enlem_boylam = (hedef.enlem, hedef.boylam)

            if enlem_boylam in seen:
                if hasattr(hedef, 'bolge'):
                    continue  # Skip adding this element, as we prefer the one without 'bolge'
                else:
                    # Remove the previously added item with 'bolge' attribute
                    new_sira = [h for h in new_sira if (
                        (h.bolge.enlem, h.bolge.boylam) if hasattr(h, 'bolge') else (h.enlem, h.boylam)
                    ) != enlem_boylam]
            else:
                seen.add(enlem_boylam)
                new_sira.append(hedef)
        
        sira = new_sira

        return sira
     
    # Batarya yetecek mi kontrol eder
    def ensure_battery_capacity(self, sira):
        kapat = 0
        total_distance = 0
        i = 0

        battery_levels = []

        while i < len(sira) - 1:
            current_distance = self.distance(sira[i], sira[i+1])
            total_distance += current_distance

            battery_levels.append(self.kalan_batarya)

            self.kalan_batarya -= current_distance /  self.birimbatarya  # 1 batarya  self.birimbatarya metre

            if self.kalan_batarya < 0:
                best_battery_station = None
                best_battery_station2 = []
                best_battery_distance = 9999
                self.kalan_batarya += current_distance /  self.birimbatarya
                backtrack_index = i
                 
                for station in self.harita.sarj_istasyonlari:
                    if station == self.sonstation:
                        continue
                    distance_to_station = self.distance(sira[i], station)
                    distance_station_to_next = self.distance(station, sira[i+1])
                    
                    if (distance_station_to_next < current_distance) and (distance_to_station <= (self.kalan_batarya* self.birimbatarya)):
                        if len(best_battery_station2)>0:
                            if distance_station_to_next<best_battery_station2[-1]:
                                self.sonstation = station
                                best_battery_station = station
                                best_battery_distance = distance_to_station
                                best_battery_station2.append(distance_station_to_next)
                            else:
                                pass                         
                        else:
                            self.sonstation = station
                            best_battery_station = station
                            best_battery_distance = distance_to_station
                            best_battery_station2.append(distance_station_to_next)
                    else:
                        self.sonstation
                
                if best_battery_station:
                    sira.insert(i + 1, best_battery_station)
                    self.kalan_batarya = 79
                    self.eskibolgeistasyon = 0
                    self.eskibolgeistasyon2 = 0
                else:
                    best_battery_station = self.OncekiNoktadanStationBul(i-1, sira, current_distance, battery_levels[-2])
                    if best_battery_station:
                        sira.insert(i, best_battery_station)
                        self.kalan_batarya = 79
                        i -= 1
                    else:
                        kapat = True
                        break
            else:
                if hasattr(sira[i+1], 'bolge'):
                    self.sonstation = sira[i+1].bolge
                else:
                    self.sonstation = sira[i+1]
            
            if kapat>20:
                break
            i += 1
            kapat += 1
 
        return sira
    
    def OncekiNoktadanStationBul(self, index, sira, original_distance, battery):
        while index >= 0:
            for station in self.harita.sarj_istasyonlari:
                if station == self.eskibolgeistasyon or station == self.eskibolgeistasyon2:
                    continue
                distance_to_station = self.distance(sira[index], station)
                distance_station_to_next = self.distance(station, sira[index + 1])

                # Check if the station is feasible from the previous point
                if (distance_station_to_next < original_distance) and (distance_to_station <= (battery * self.birimbatarya)):
                    if hasattr(sira[index], 'bolge'):
                        self.eskibolgeistasyon = sira[index].bolge
                    else:
                        self.eskibolgeistasyon = sira[index]
                    self.eskibolgeistasyon2 = station
                    return station

            index -= 1

        return None

    # Distance verir 2 bolge arasindaki. Bolge olmasada olur.
    def distance(self, hedef1, hedef2):
        enlem1 = hedef1.enlem if hasattr(hedef1, 'enlem') else hedef1.bolge.enlem
        boylam1 = hedef1.boylam if hasattr(hedef1, 'boylam') else hedef1.bolge.boylam
        enlem2 = hedef2.enlem if hasattr(hedef2, 'enlem') else hedef2.bolge.enlem
        boylam2 = hedef2.boylam if hasattr(hedef2, 'boylam') else hedef2.bolge.boylam
        return math.sqrt((enlem2 - enlem1) ** 2 + (boylam2 - boylam1) ** 2)

    def otoyoldangit(self, nextx, nexty, otoyol):
        mindistance = float('inf')
        enyakinnoktax = nextx
        enyakinnoktay = nexty

        for otoyolveri in self.harita.otoyol_veri:
            distance = math.sqrt((otoyolveri.enlem - nextx) ** 2 + (otoyolveri.boylam - nexty) ** 2)
            if distance < mindistance:
                mindistance= distance
                enyakinnoktax = otoyolveri.enlem
                enyakinnoktay = otoyolveri.boylam
        
        return enyakinnoktax, enyakinnoktay

    # INIT fonksiyonu    
    def RotayiYenidenHesapla(self):
        for _ in range(1000):
            self.angle = math.atan2(self.hedef_bolge.boylam - self.arac_y, self.hedef_bolge.enlem - self.arac_x) # Hedefe olan açı (Radyan)
            new_x, new_y = self.EngelTespit(self.arac_x, self.arac_y, self.angle, blokboyutu=20)
            new_x, new_y = self.otoyoldangit(new_x, new_y, self.harita.otoyol_veri)
            # new_test_x, new_test_y = self.EngelTespit(self.arac_x, self.arac_y, self.angle, blokboyutu=15)
            # new_test_x2, new_test_y2 = self.EngelTespit(self.arac_x, self.arac_y, self.angle, blokboyutu=10)
            # new_test_x3, new_test_y3 = self.EngelTespit(self.arac_x, self.arac_y, self.angle, blokboyutu=5)
            # # engelvarmi = False
            # ruzgarvarmi = False
            # yasaklibolgevarmi = False
            # bolge = self.harita.bolge(new_x, new_y)
            # bolgetest = self.harita.bolge(new_test_x, new_test_y)
            # bolgetest2 = self.harita.bolge(new_test_x2, new_test_y2)
            # bolgetest3 = self.harita.bolge(new_test_x3, new_test_y3)

            # if self.arac_yukselti > 330:
            #     new_x, new_y = self.EngelTespit(self.arac_x, self.arac_y, self.angle, blokboyutu=45)
            #     self.arac_x, self.arac_y = new_x, new_y
            #     self.arac_yukselti = self.hedef_bolge.yukselti

            # if bolgetest.yukselti > self.engelsiniri:
            #     new_x, new_y = self.EngelGec(self.arac_x, self.arac_y, self.angle)
            #     engelvarmi = True
            # elif bolge.yukselti > self.engelsiniri or bolge.yavas_bolge:
            #     new_x, new_y = self.EngelGec(self.arac_x, self.arac_y, self.angle)
            #     engelvarmi = True  
            # elif bolgetest.ruzgar: 
            #     new_x, new_y = self.EngelGec(self.arac_x, self.arac_y, self.angle, senaryo = 'RUZGARLIBOLGE')
            #     ruzgarvarmi = True 
            # elif bolge.ruzgar:
            #     new_x, new_y = self.EngelGec(self.arac_x, self.arac_y, self.angle, senaryo = 'RUZGARLIBOLGE')
            #     ruzgarvarmi = True  
            # elif bolge.ucusa_yasakli_bolge:
            #     new_x, new_y = self.EngelGec(self.arac_x, self.arac_y, self.angle, senaryo = 'YASAKLIBOLGE')
            #     yasaklibolgevarmi = True   
            # elif bolgetest.ucusa_yasakli_bolge or bolgetest2.ucusa_yasakli_bolge or bolgetest3.ucusa_yasakli_bolge:
            #     new_x, new_y = self.EngelGec(self.arac_x, self.arac_y, self.angle, senaryo = 'YASAKLIBOLGE')
            #     yasaklibolgevarmi = True   
            # elif bolge.yavas_bolge:
            #     new_x, new_y = self.EngelGec(self.arac_x, self.arac_y, self.angle, senaryo = 'YAVASBOLGE')
            #     yasaklibolgevarmi = True  
            # elif bolgetest.yavas_bolge:
            #     new_x, new_y = self.EngelGec(self.arac_x, self.arac_y, self.angle, senaryo = 'YAVASBOLGE')
            #     yasaklibolgevarmi = True  
            
            mesafe_x = self.hedef_bolge.enlem - self.arac_x
            mesafe_y = self.hedef_bolge.boylam - self.arac_y 

            if abs(mesafe_y) < 30 and abs(mesafe_x) < 30: 
                break
            elif self.hedef_bolge.yukselti > 300:
                if abs(mesafe_y) < 50 and abs(mesafe_x) < 50: 
                    break

            #self.rota.append((new_x, new_y, engelvarmi, ruzgarvarmi, yasaklibolgevarmi)) # Enlem Boylam Engel
            self.rota.append((new_x, new_y, False, False, False)) # FTR icin suanlik boyle 16 mart cemre
            self.arac_x, self.arac_y = new_x, new_y

        self.arac_yukselti = self.hedef_bolge.yukselti

        self.rota.insert(0, (self.filtered_gnss_enlem, self.filtered_gnss_boylam, False, False, False))
        #*******|| Rota Oluşturulması ||********
        #*******|| Rota Kısaltılması ||********
        # index = 0 
        # while index < len(self.rota) - 1: 
        #     last_no_obstacle_index = index 
        #     # Start from the next waypoint and try to find the farthest waypoint without obstacles
        #     for index2 in range(index + 1, len(self.rota)):
        #         waypoint2 = self.rota[index2]

        #         # Check if there is an obstacle between the current waypoint and the next
        #         if self.AradaEngelVarmi(self.rota[index], waypoint2, segment_length=1):
        #             break
        #         elif self.AradaEngelVarmi(self.rota[index], waypoint2, segment_length=15):
        #             break
        #         elif self.AradaEngelVarmi(self.rota[index], waypoint2, segment_length=10):
        #             break
        #         elif self.AradaEngelVarmi(self.rota[index], waypoint2, segment_length=5):
        #             break
        #         elif self.AradaEngelVarmi(self.rota[index], waypoint2, segment_length=2):
        #             break
        #         #elif self.rota[index2][4] or self.rota[index][4] or self.rota[index2][3] or self.rota[index][3]:
        #            # break
        #         else:
        #             # If no obstacle, set index2 as the new waypoint to compare from index
        #             last_no_obstacle_index = index2

        #     # Delete waypoints between the current one and the last one without an obstacle
        #     if last_no_obstacle_index > index + 1:
        #         del self.rota[index + 1:last_no_obstacle_index]
            
        #     index += 1

        del self.rota[0]
        #*******|| Rota Kısaltılması ||********
     
    # Azami Yüksekliğe Yükselir
    def KalkisYap(self): 
        if self.motorarizasivar:
            pass
        #elif self.baslangica_don:
           # pass
        else:    
            hedefx, hedefy = self.rota[self.rota_count][0], self.rota[self.rota_count][1]
            self.HedefeDon(hedefx, hedefy, self.filtered_gnss_enlem, self.filtered_gnss_boylam, duzgit=False)
        if self.gnss_userhata:
            if self.barometre.irtifa >= (self.azami_yukseklik-10) and not self.kalkis_yap:
                self.yukseklige_ulasildi=True
                self.dur()
                self.kalkis_yap = True
                return True
            elif self.yukseklige_ulasildi == False: 
                self.yukari_git(HIZLI)
                return False
            else:  
                pass
        else:
            if self.gnss.irtifa >= (self.azami_yukseklik-10) and not self.kalkis_yap:
                self.yukseklige_ulasildi=True
                self.dur()
                self.kalkis_yap = True
                return True
            elif self.yukseklige_ulasildi == False:
                self.yukari_git(HIZLI)
                return False
            else:  
                pass

    def UzunBinayaKalkisYap(self):
        if self.barometre.hata:
            if self.gnss.irtifa < 265:
                self.yukari_git(HIZLI)
                return False
            else:
                return True
        else:
            if self.barometre.irtifa < 265:
                self.yukari_git(HIZLI)
                return False
            else:
                return True
    
    def UzunBinadanInisYap(self, barometre=False):
        self.dur()
        if barometre:
            if self.gnss.irtifa>278:
                self.asagi_git(HIZLI)
                return True
            else:
                self.uzunbinadaninis = False
                return False
        else:
            if self.barometre.irtifa>278:
                self.asagi_git(HIZLI)
                return True
            else:
                self.uzunbinadaninis = False
                return False
            
    # İstenilen değeri istenildiği kadar filtrelenir ve geri gönderilir
    def FilterData(self, katsayi, manyetometre=False, gnssenlem=False, gnssboylam=False, imux=False, imuy=False, imuz=False, acisalhiz=False, deviationimux=False, deviationimuz=False):
        if manyetometre:
            filtered_list = [self.manyetometre.veri for _ in range(katsayi)]
            return sum(filtered_list) / len(filtered_list)
        elif gnssenlem:
            filtered_list = [self.gnss.enlem for _ in range(katsayi)]
            return sum(filtered_list) / len(filtered_list)
        elif gnssboylam: 
            filtered_list = [self.gnss.boylam for _ in range(katsayi)]
            return sum(filtered_list) / len(filtered_list)
        elif imux:
            filtered_list = [self.imu.hiz.x for _ in range(katsayi)]
            if len(self.filteredimux_list)<4:
                self.filteredimux_list.append(sum(filtered_list) / len(filtered_list)) 
                return sum(filtered_list) / len(filtered_list) + self.standard_deviation_imu_x
            else:
                self.filteredimux_list.append(sum(filtered_list) / len(filtered_list))
                deneme = sum(self.filteredimux_list)/5.0
                self.filteredimux_list.pop(0)
                return deneme + self.standard_deviation_imu_x
        elif imuy:
            filtered_list = [self.imu.hiz.y for _ in range(katsayi)]
            if len(self.filteredimuy_list)<4:
                self.filteredimuy_list.append(sum(filtered_list) / len(filtered_list)) 
                return sum(filtered_list) / len(filtered_list)
            else:
                self.filteredimuy_list.append(sum(filtered_list) / len(filtered_list))
                deneme = sum(self.filteredimuy_list)/5.0
                self.filteredimuy_list.pop(0)
                return deneme
        elif imuz:
            filtered_list = [self.imu.hiz.z for _ in range(katsayi)]
            if len(self.filteredimuz_list)<4:
                self.filteredimuz_list.append(sum(filtered_list) / len(filtered_list)) 
                return sum(filtered_list) / len(filtered_list) + self.standard_deviation_imu_z
            else:
                self.filteredimuz_list.append(sum(filtered_list) / len(filtered_list))
                deneme = sum(self.filteredimuz_list)/5.0
                self.filteredimuz_list.pop(0)
                return deneme + self.standard_deviation_imu_z
        elif acisalhiz:
            filtered_list = [self.imu.acisal_hiz.y for _ in range(katsayi)]
            #if abs(sum(filtered_list) / len(filtered_list)) < 0.2:
               # return 0
            return (sum(filtered_list) / len(filtered_list))

        elif deviationimux:
            filtered_list = [(0 - self.FilterData(40, imux=True)) for _ in range(katsayi)]
            return (sum(filtered_list) / len(filtered_list))
        
        elif deviationimuz:
            filtered_list = [(0 - self.FilterData(40, imuz=True)) for _ in range(katsayi)]
            return (sum(filtered_list) / len(filtered_list))
        
# Ana program
#itfaiye_1 = Itfaiye(id=1)
#kargo_1 = Kargo(id=1) 
#ambulans_1 = Ambulans(id=1)
cezeri_1 = Cezeri(id=1)

while robot.is_ok():
    #itfaiye_1.run()
    #kargo_1.run() 
    #ambulans_1.run()
    cezeri_1.run()
          
class Itfaiye(ItfaiyeParent):
    def __init__(self, id = 0):
        super().__init__(id = id, keyboard = False, sensor_mode = NORMAL)
        ##print(self.gnss.irtifa)
        #print(self.harita.yangin_bolgeleri)
        #print(self.harita.yangin_bolgeleri[0])
        #print(self.baslangica_don)

        self.hedef_amaclar = []
        self.hedef_amac = None

        # ITFAIYE
        self.suacik = False
        # ITFAIYE

        self.baslangic_bolgesi = self.harita.bolge(self.gnss.enlem, self.gnss.boylam)
        self.baslangic_bolgesi.amac = 0 # KULLANILMIYOR SUANDA AMA KALSIN CEMRE MART 11
        # self.hedef_amaclar.append(0) # Baslangic bolgesi amaci

        self.engelsiniri = 260.0 - 10 # Azami Yukseklik - 10 (HATA PAYI)
        self.azami_yukseklik = 260.0 # Itfaiye Azami Yukseklik
        self.birimbatarya = 11
  
        self.test2 = True

        #*******|| Filtre ||********
        self.filteredimux_list = []
        self.filteredimuy_list = []
        self.filteredimuz_list = []
        self.filteredgnssenlem_list = []
        self.filteredgnssboylam_list = []
        self.filteredmanyetometre_list = []
        self.standard_deviation_gnss_enlem = 0
        self.standard_deviation_gnss_boylam = 0
        self.standard_deviation_imu_x = 0
        self.standard_deviation_imu_z = 0
        self.filtered_gnss_enlem = self.FilterData(200, gnssenlem=True)
        self.filtered_gnss_boylam = self.FilterData(200, gnssboylam=True)
        self.filtered_manyetometre = self.FilterData(500, manyetometre=True)
        self.son_GNSS_enlem = self.filtered_gnss_enlem
        self.son_GNSS_boylam = self.filtered_gnss_boylam
        self.son_manyetometre = self.filtered_manyetometre
        self.standard_deviation_gnss_enlem = self.baslangic_bolgesi.enlem - self.filtered_gnss_enlem
        self.standard_deviation_gnss_boylam = self.baslangic_bolgesi.boylam - self.filtered_gnss_boylam
        self.standard_deviation_imu_x = self.FilterData(50, deviationimux=True) 
        self.standard_deviation_imu_z = self.FilterData(50, deviationimuz=True) 
        #*******|| Filtre ||********

        #*******|| Batarya ||******** 
        if self.batarya.hata == 1:
            self.kalan_batarya = 80
            self.eski_batarya_veri = 80
        else:
            self.kalan_batarya = self.batarya.veri - 20
            self.eski_batarya_veri = self.batarya.veri - 20

        self.bataryabekle = 0
        self.sonstation = 0
        self.eskibolgeistasyon = 0
        self.eskibolgeistasyon2 = 0
        #*******|| Batarya ||******** 

        #*******|| Hedef Bölge Hesabı ||********
        self.siralimi = True
        self.hedefrotasi = self.HedefSirasiniBelirle() # Hedefleri sıralar
        self.hedefrotasi = self.HedefSirasiniDuzenle(self.hedefrotasi)

        self.hedefrotasicount = 0
        self.hedef = self.hedefrotasi[self.hedefrotasicount]
        if hasattr(self.hedefrotasi[self.hedefrotasicount], 'bolge'):
            self.hedef_bolge = self.hedefrotasi[self.hedefrotasicount].bolge
        else:
            self.hedef_bolge = self.hedefrotasi[self.hedefrotasicount]
            self.hedef_amac = self.hedef_amaclar[self.hedefrotasicount]
        self.baslangicadonulsunmu = False
 
        self.hedefbolgedegistimi_count = 0 
        self.eskihedefler = [(hedef.enlem, hedef.boylam) for hedef in self.harita.yangin_bolgeleri]
        #print(self.eskihedefler)
        #print(self.baslangic_bolgesi, "TEST")
        #for bolge in self.hedefrotasi:
            #print(bolge.enlem, bolge.boylam, bolge.amac)
        #*******|| Hedef Bölge Hesabı ||********
 
        #*******|| Kalkış yap / İniş yap ||******** 
        self.hedefe_ulasildi = False 
        self.sarj_istasyonuna_ulasildi = False  
        self.hedef_enlemboylam_ulasildi = False  
        self.kalkis_yap = False
        self.yukseklige_ulasildi = False
        self.yenihedefdurcount = 0
        #*******|| Kalkış yap / İniş yap ||********
 
        #*******|| Acil Durum ||********
        self.acildurumdogrulandi = False
        self.hastane_dur_count = 0
        self.hastane_distance = 9999
        #*******|| Acil Durum ||********

        #*******|| Motor Arızası ||********
        self.motorasagigit = False
        self.motorarizasidogrulandi = False
        self.motor_dur_count = 0
        self.motorarizasivar = False
        self.gnssmotorhata = False
        #*******|| Motor Arızası ||********

        #*******|| GNSS Arızası ||********
        self.gnss_dur = 0
        self.gnss_userhata = self.gnss.hata
        self.spoofingbekleme = 0
        self.onceki_zaman_gnss = self.zaman()
        self.gnss_userdata_x = self.filtered_gnss_enlem
        self.gnss_userdata_z = self.filtered_gnss_boylam
        self.gnsshatasidogrulandi = False
        #*******|| GNSS Arızası ||********

        #*******|| Manyetometre Arızası ||********
        self.onceki_zaman_manyetometre = self.zaman()
        self.manyetometre_user_data = self.filtered_manyetometre
        self.previous_gecicideger = 0.0
        #*******|| Manyetometre Arızası ||********

        #*******|| Rota Hesabı ||********
        self.rota = []   
        self.rota_count = 0
        self.arac_x, self.arac_y = self.filtered_gnss_enlem, self.filtered_gnss_boylam
        self.durcount = 0 
        #*******|| Rota Hesabı ||********

        #*******|| Rota Oluşturulması / Kısaltılması ||******** 
        self.arac_yukselti = self.baslangic_bolgesi.yukselti
        self.RotayiYenidenHesapla()
        #*******|| Rota Oluşturulması / Kısaltılması ||******** 

        self.uzunbinadogrulandi = False
        self.uzunbinadaninis = False
        self.sonradarverileri = []
        self.sonlidarverileri = []

        self.sensor_mode = ''
        if self.imu.acisal_hiz.y==0 or self.imu.acisal_hiz.x==0 or self.imu.acisal_hiz.z==0:
            self.sensormode = "DUZELTILMIS"
        else:
            self.sensormode = "NORMAL"
 
    def run(self):
        super().run()
        ##print(self.manyetometre.veri)
        #*******||Filter||********
        if not self.gnss_userhata or not self.gnss.hata:
            self.filtered_gnss_enlem = self.FilterData(50, gnssenlem=True)
            self.filtered_gnss_boylam = self.FilterData(50, gnssboylam=True)

            #*******||Trafik||******** 

            bolgetrafik = self.harita.bolge(self.filtered_gnss_enlem, self.filtered_gnss_boylam)

            if self.tamamlandi:
                bolgeler[self.id - 1] = None
            else:
                bolgeler[self.id - 1] = bolgetrafik
                sarj_durumlari[self.id - 1] = self.batarya
                if self.gnss.irtifa < 100:
                    inisebaslandimitrafik[self.id - 1] = True
                else:
                    inisebaslandimitrafik[self.id - 1] = False
                yukseltitrafik[self.id - 1] = self.gnss.irtifa

                bekle = False

                for i in range(len(bolgeler)):
                    if i == self.id - 1:
                        continue

                    oteki_bolge = bolgeler[i]            
                    if oteki_bolge == None:
                        continue
                    oteki_sarj = sarj_durumlari[i]

                    cezeriler_arasi_mesafe = bolgeler_arasi_mesafe(oteki_bolge, bolgetrafik)
                    if cezeriler_arasi_mesafe <= 65:

                        batarya_veri = round(self.batarya.veri, 0)
                        oteki_batarya_veri = round(oteki_sarj.veri, 0)
                        inisebasladimiben = inisebaslandimitrafik[self.id - 1]
                        inisebasladimioteki = inisebaslandimitrafik[i]
                        yukseltiben = self.id - 1
                        yukseltioteki = i

                        if not inisebasladimiben and inisebasladimioteki:
                            self.dur()
                            bekle = True
                        elif yukseltiben<yukseltioteki:
                            bekle = True
                            self.dur()

                        if inisebasladimiben:
                            bekle = False
                
                if bekle:
                    self.dur()
                    return

            #*******||Trafik||******** 
     
        if not self.manyetometre.hata:
            self.filtered_manyetometre = self.FilterData(100, manyetometre=True)
        #*******||Filter||********

        #*******|| Kalkış / Bitiş / İniş||********
        if self.uzunbinadogrulandi:
            if self.UzunBinayaKalkisYap():
                self.uzunbinadogrulandi = False
            else:
                return

        if self.hedef_bolge.yukselti < (self.azami_yukseklik - 20):
            if self.barometre.hata:
                if self.gnss.hata:
                    pass
                else:
                    if self.gnss.irtifa > (self.azami_yukseklik + 30) or self.uzunbinadaninis:
                        self.sonlidarverileri.append(self.lidar.mesafe)
                        if len(self.sonlidarverileri)>15:
                            self.sonlidarverileri.pop(0)
                        self.uzunbinadaninis = True
                        if self.lidar.hata:
                            self.sonradarverileri.append(self.radar.mesafe)
                            if len(self.sonradarverileri)>15:
                                self.sonradarverileri.pop(0)
                            if self.radar.hata:
                                pass 
                            else:
                                if all(value > (self.azami_yukseklik - 20) for value in self.sonradarverileri):
                                    if self.UzunBinadanInisYap(True):
                                        return
                        else:
                            if all(value > (self.azami_yukseklik - 20) for value in self.sonlidarverileri):
                                if self.UzunBinadanInisYap(True):
                                    return
            else:
                if self.barometre.irtifa > (self.azami_yukseklik + 30) or self.uzunbinadaninis:
                    self.sonlidarverileri.append(self.lidar.mesafe)
                    if len(self.sonlidarverileri)>15:
                        self.sonlidarverileri.pop(0)
                    self.uzunbinadaninis = True
                    if self.lidar.hata:
                        self.sonradarverileri.append(self.radar.mesafe)
                        if len(self.sonradarverileri)>15:
                            self.sonradarverileri.pop(0)
                        if self.radar.hata:
                            pass
                        else:
                            if all(value > (self.azami_yukseklik - 20) for value in self.sonradarverileri):
                                if self.UzunBinadanInisYap():
                                    return
                    else:
                        if all(value > (self.azami_yukseklik - 20) for value in self.sonlidarverileri):
                            if self.UzunBinadanInisYap():
                                return
                
        if not self.kalkis_yap: 
            if self.KalkisYap():
                pass
            else:
                return
        if self.sarj_istasyonuna_ulasildi:
            if self.batarya.hata:
                if self.bataryabekle < 100:
                    self.bataryabekle += 1
                    return
                else:
                    pass
            else:
                if self.batarya.veri <= 98.9: 
                    return
                else:
                    self.hedefrotasicount += 1
                    if hasattr(self.hedefrotasi[self.hedefrotasicount], 'bolge'):
                        self.hedef = self.hedefrotasi[self.hedefrotasicount]
                        self.hedef_bolge = self.hedefrotasi[self.hedefrotasicount].bolge
                    else:
                        if len(self.hedefrotasi) <= (self.hedefrotasicount + 1):
                            if self.baslangica_don: 
                                self.hedef_amac = 0
                                self.hedef_bolge = self.hedefrotasi[self.hedefrotasicount]
                        else:             
                            self.hedef_amac = self.hedef_amaclar[self.hedefrotasicount]
                            self.hedef_bolge = self.hedefrotasi[self.hedefrotasicount]
                            
                    # Rota
                    self.rota = []
                    self.rota_count = 0
                    self.arac_x, self.arac_y = self.filtered_gnss_enlem, self.filtered_gnss_boylam
                    self.durcount = 0

                    # Kalkış Yap / Hedefe Ulaşıldı
                    self.hedefe_ulasildi = False
                    self.hedef_enlemboylam_ulasildi =False
                    self.kalkis_yap = False
                    self.yukseklige_ulasildi = False
                    self.RotayiYenidenHesapla()

                    self.sarj_istasyonuna_ulasildi = False

                    return
        if self.hedefe_ulasildi:
            print("GÖREV TAMAMLANDI")
            return
        if self.gnsshatasidogrulandi:
            self.HedefeinisYap(gnsshata = True)
            return
        if self.hedef_enlemboylam_ulasildi:
            self.HedefeinisYap()
            return
        #*******|| Kalkış / Bitiş / İniş||********

        #*******||Spoff Detect / GNSS Detect||********
        if self.gnss_userhata == 0: 
            if self.spoofingbekleme<50:
                self.spoofingbekleme += 1
            elif self.son_GNSS_enlem > self.filtered_gnss_enlem+15 or self.son_GNSS_enlem < self.filtered_gnss_enlem-15:
                self.gnss_userhata = 1
        if self.gnss.hata == 1:
            self.gnss_userhata = 1
        if self.gnss_userhata == 0:
            self.son_GNSS_enlem = self.filtered_gnss_enlem
            self.son_GNSS_boylam = self.filtered_gnss_boylam
            self.son_manyetometre = self.filtered_manyetometre 

            self.gnss_userdata_x = self.filtered_gnss_enlem
            self.gnss_userdata_z = self.filtered_gnss_boylam
            self.onceki_zaman_gnss = self.zaman()
        else:
            if self.gnss_dur < 1:
                self.dur()
                self.gnss_dur += 1
                return

            dt = self.zaman() - self.onceki_zaman_gnss
            self.onceki_zaman_gnss = self.zaman()
            self.gnss_userdata_x += self.FilterData(100, imux=True) * dt
            self.gnss_userdata_z += self.FilterData(100, imuz=True) * dt
            
            self.filtered_gnss_enlem = self.gnss_userdata_x
            self.filtered_gnss_boylam = self.gnss_userdata_z 
        #*******||Spoff Detect / GNSS Detect||******** 
        
        if self.yukseklige_ulasildi or self.gnss_userhata == 0:
            #*******|| Hedef Değişti mi? / Başlangıca Dönülsün mü? ||********
            if self.motorarizasivar or self.acildurumdogrulandi:
                hedef_bolge_degistimi = False
            else:
                hedef_bolge_degistimi = False
                ### ITFAIYEDE HEDEF BOLGE DEGISMIYOR DIYE VARSAYDIM DEGISIYORSA GEREKEN LOGIC BURAYA EKLENECEK
                pass
             
            if not hedef_bolge_degistimi:  
                pass
            else:
                self.hedefrotasi = self.HedefSirasiniBelirle() # Hedefleri sıralar
                self.hedefrotasi = self.HedefSirasiniDuzenle(self.hedefrotasi)
                self.hedefbolgedegistimi_count = 0
                self.hedef = self.hedefrotasi[self.hedefrotasicount]
                if hasattr(self.hedefrotasi[self.hedefrotasicount], 'bolge'):
                    self.hedef_bolge = self.hedefrotasi[self.hedefrotasicount].bolge
                else:
                    self.hedef_bolge = self.hedefrotasi[self.hedefrotasicount]

                #*******|| Kalkış yap / İniş yap ||********
                self.hedefe_ulasildi = False   
                self.hedef_enlemboylam_ulasildi =False
                self.kalkis_yap = False
                self.yukseklige_ulasildi = False
                self.yenihedefdurcount = 0
                #*******|| Kalkış yap / İniş yap ||********

                #*******|| Acil Durum ||********
                self.acildurumdogrulandi = False
                self.hastane_dur_count = 0
                self.hastane_distance = 9999
                #*******|| Acil Durum ||********

                #*******|| Motor Arızası ||********
                self.motorasagigit = False
                self.motorarizasidogrulandi = False
                self.motor_dur_count = 0
                #*******|| Motor Arızası ||********

                #*******|| GNSS Arızası ||********
                self.gnss_dur = 0

                self.gnss_userhata = self.gnss.hata
                #*******|| GNSS Arızası ||********

                #*******|| Rota Hesabı ||********
                self.rota = []
                self.rota_count = 0
                self.arac_x, self.arac_y = self.filtered_gnss_enlem, self.filtered_gnss_boylam
                self.durcount = 0 
                #*******|| Rota Hesabı ||********

                self.RotayiYenidenHesapla()

                return
             #*******|| Hedef Değişti mi? / Başlangıca Dönülsün mü? ||********
            
            #*******|| Acil Durum ||********
            if self.acil_durum and not self.acildurumdogrulandi:
                if self.hastane_dur_count < 10: 
                    self.dur() 
                    self.hastane_dur_count += 1 
                    return 
                else: 
                    self.acildurumdogrulandi = True
                    self.hedef_bolge.enlem, self.hedef_bolge.boylam, yukselti = self.EnYakinHastaneyiBul()

                    # Rota
                    self.rota = []
                    self.rota_count = 0
                    self.arac_x, self.arac_y = self.filtered_gnss_enlem, self.filtered_gnss_boylam
                    self.durcount = 0

                    # Kalkış Yap / Hedefe Ulaşıldı
                    self.hedefe_ulasildi = False
                    self.hedef_enlemboylam_ulasildi =False
                    self.kalkis_yap = False
                    self.yukseklige_ulasildi = False

                    self.RotayiYenidenHesapla()

                    return
            #*******|| Acil Durum ||********

            #*******|| Motor Arızası ||********
            if 0 in self.motor.rpm: # MOTOR BOZULDU MU
                self.motorarizasivar = True

                if self.motor_dur_count < 5: 
                    self.dur()
                    self.motor_dur_count += 1
                    return
                elif self.motor_dur_count == 5:
                    # EN YAKIN BOLGEYI BUL
                    inilebilir_bolgeler = []
                    inilebilir_bolgeler = self.EnYakinInilebilirBolgeyiBul(self.filtered_gnss_enlem, self.filtered_gnss_boylam) # (x, y) 1ms
                    distance1 = 9999
                    inis_bolgesi = []

                    for bolge in inilebilir_bolgeler:
                        distance = math.sqrt((bolge.enlem-self.filtered_gnss_enlem)**2+(bolge.boylam-self.filtered_gnss_boylam)**2)
                        if distance < distance1:
                            distance1 = distance
                            inis_bolgesi = bolge 

                    self.hedef_bolge.enlem = inis_bolgesi.enlem
                    self.hedef_bolge.boylam = inis_bolgesi.boylam
                    self.motor_dur_count += 1
                    return 
                else:
                    mesafex, mesafey = self.hedef_bolge.enlem - self.filtered_gnss_enlem, self.hedef_bolge.boylam - self.filtered_gnss_boylam
                    if abs(mesafey) < 5 and abs(mesafex) < 5 or self.gnssmotorhata: 
                        if self.gnss_userhata:
                            self.gnssmotorhata = True
                        else:
                            self.gnssmotorhata = False
                        self.HedefeinisYap()
                        return
                    else:
                        if self.motor_dur_count == 6:
                            self.dur()
                            self.motor_dur_count += 1
                            return
                        else:
                            if self.gnss_userhata:
                                #self.ileri_git(HIZLI)
                                self.HedefeDon(self.hedef_bolge.enlem, self.hedef_bolge.boylam, self.filtered_gnss_enlem, self.filtered_gnss_boylam)
                            else:
                                self.HedefeDon(self.hedef_bolge.enlem, self.hedef_bolge.boylam, self.filtered_gnss_enlem, self.filtered_gnss_boylam)
                            return
            #*******|| Motor Arızası ||********

            #**|| Hedef Bölgesine git ||**
            if self.rota[self.rota_count] == self.rota[-1]:
                hedefx, hedefy = self.hedef_bolge.enlem, self.hedef_bolge.boylam
                mesafe_x, mesafe_y = hedefx - self.filtered_gnss_enlem, hedefy - self.filtered_gnss_boylam
                if self.gnss_userhata:
                    katsayideger = 10 
                    test1 = False
                elif self.manyetometre.hata:
                    katsayideger = 4.5
                    test1 = False
                else:  
                    katsayideger = 4.5
                    test1 = True  

                if abs(mesafe_y) < katsayideger and abs(mesafe_x) < katsayideger:
                    self.test2 = True

                    if self.hedef_amac == 0: 
                        self.hedef_enlemboylam_ulasildi = True
                        #print("HELOLLFJOFJOF")
                        if self.gnss_userhata: 
                            self.gnsshatasidogrulandi = True
                            return
                        else:
                            self.HedefeinisYap()
                            if self.lidar.mesafe>15 and not self.lidar.hata:
                                self.HedefeDon(hedefx, hedefy, self.filtered_gnss_enlem, self.filtered_gnss_boylam)
                            elif self.radar.mesafe>15 and not self.radar.hata:
                                self.HedefeDon(hedefx, hedefy, self.filtered_gnss_enlem, self.filtered_gnss_boylam)
                    elif self.hedef_amac == 1:
                        if self.yenihedefdurcount < 10: 
                            self.dur()
                            self.yenihedefdurcount += 1  
                            return
                        else:
                            self.hedef_enlemboylam_ulasildi = True
                            self.yenihedefdurcount = 0
                            self.hedefrotasicount += 1
                            if hasattr(self.hedefrotasi[self.hedefrotasicount], 'bolge'):
                                self.hedef = self.hedefrotasi[self.hedefrotasicount]
                                self.hedef_bolge = self.hedefrotasi[self.hedefrotasicount].bolge
                            else:
                                if len(self.hedefrotasi) <= (self.hedefrotasicount + 1):
                                    if self.baslangica_don: 
                                        self.hedef_amac = 0 
                                        self.hedef_bolge = self.hedefrotasi[self.hedefrotasicount]
                                        #self.hedef_amac = self.hedef_amaclar[self.hedefrotasicount]
                                    else:  
                                        pass
                                
                                else:  
                                    # self.hedef_amac = 2 # suan gerek yok 8 mart 2025 cemre
                                    self.hedef_bolge = self.hedefrotasi[self.hedefrotasicount]
                                    self.hedef_amac = self.hedef_amaclar[self.hedefrotasicount]
                                  
                            # Rota
                            self.rota = []
                            self.rota_count = 0
                            self.arac_x, self.arac_y = self.filtered_gnss_enlem, self.filtered_gnss_boylam
                            self.durcount = 0

                            # Kalkış Yap / Hedefe Ulaşıldı
                            self.hedefe_ulasildi = False
                            self.hedef_enlemboylam_ulasildi =False
                            self.kalkis_yap = False
                            self.yukseklige_ulasildi = False
                            self.RotayiYenidenHesapla()

                            return
                    elif self.hedef_amac == 2:
                        #print("HELLO")
                        self.hedef_enlemboylam_ulasildi = False
                        self.SarjIstasyonunainisYap()
                        return
                    elif self.hedef_amac == 3: # Yangın bolgesi (baslangica don calismiyor o yuzden baslangica don false olsa bile baslangica donecek)

                        #if self.harita.yangin_bolgeleri is not []: # Sadece bir yangin icin calisir
                        if self.su_seviyesi > 6:
                            #print("su acik")
                            self.dur()
                            self.su_ac(True)
                            self.suacik = True
                        
                            #print(self.su_seviyesi)
                            return
                        
                        else: # Siradaki hedefe bak. 
                            self.hedef_enlemboylam_ulasildi = True
                            self.su_ac(False)
                            self.suacik = False
                            if hasattr(self.hedefrotasi[self.hedefrotasicount], 'bolge'): # Buraya hic gelmiyor die dokunmuoz suanlik Cemre 11 mart
                                self.hedef = self.hedefrotasi[self.hedefrotasicount]
                                self.hedef_bolge = self.hedefrotasi[self.hedefrotasicount].bolge
                            else:
                                if self.hedef_bolge == self.hedefrotasi[-1]: # Kargoyu bıraktık ve son hedef buydu baslangica geri dön
                                    self.hedef_amac = 0
                                    self.hedef_bolge = self.baslangic_bolgesi

                                elif len(self.hedefrotasi) <= (self.hedefrotasicount + 1):
                                    if self.baslangica_don: 
                                        self.hedef_amac = 0 
                                        self.hedef_bolge = self.hedefrotasi[self.hedefrotasicount]
                                        #self.hedef_amac = self.hedef_amaclar[self.hedefrotasicount]
                                    else:  
                                        pass
                                else:  
                                    # self.hedef_amac = 2 # suan gerek yok 8 mart 2025 cemre
                                    self.hedef_bolge = self.hedefrotasi[self.hedefrotasicount]
                                    self.hedef_amac = self.hedef_amaclar[self.hedefrotasicount]
                                  
                            # Rota
                            self.rota = []
                            self.rota_count = 0
                            self.arac_x, self.arac_y = self.filtered_gnss_enlem, self.filtered_gnss_boylam
                            self.durcount = 0

                            # Kalkış Yap / Hedefe Ulaşıldı
                            self.hedefe_ulasildi = False
                            self.hedef_enlemboylam_ulasildi =False
                            self.kalkis_yap = False
                            self.yukseklige_ulasildi = False
                            self.RotayiYenidenHesapla()

                            return
                    else:
                        self.hedef_enlemboylam_ulasildi = True
                    
                
                elif abs(mesafe_y) < katsayideger+20 and abs(mesafe_x) < katsayideger+20 and test1 and self.test2: 
                    self.dur()
                    self.test2 = False

                elif abs(mesafe_y) < katsayideger+27 and abs(mesafe_x) < katsayideger+27 and self.hedef_bolge.yukselti>250 and self.test2: 
                    self.dur()
                    self.uzunbinadogrulandi = True
                    self.test2 = False
                    return
                
                else:
                    if self.gnss_userhata and False:
                        self.ileri_git(HIZLI)
                    else:
                        self.HedefeDon(hedefx, hedefy, self.filtered_gnss_enlem, self.filtered_gnss_boylam)
            #**|| Hedef Bölgesine git ||**
            #**|| Way Pointe git ||**
            else:
                hedefx, hedefy = self.rota[self.rota_count][0], self.rota[self.rota_count][1]

                mesafe_x, mesafe_y = hedefx - self.filtered_gnss_enlem, hedefy - self.filtered_gnss_boylam

                if abs(mesafe_y) < 15 and abs(mesafe_x) < 15: 

                    #*| Ne kadar duracağını belirle |*
                    if self.rota[self.rota_count+1][2]:  
                        durcount1 = 5 
                    elif self.rota[self.rota_count+1][3]:
                        durcount1 = 50
                    elif self.rota[self.rota_count+1][4]:
                        durcount1 = 50
                    elif self.rota[self.rota_count+1] == self.rota[-1]:
                        durcount1 = 1
                    else:
                        durcount1 = 0
                        aci = math.atan2(self.hedef_bolge.boylam - self.filtered_gnss_boylam, self.hedef_bolge.enlem - self.filtered_gnss_enlem)
                        aci_farki = aci - self.filtered_manyetometre
                        aci_farki = (aci_farki + math.pi) % (2 * math.pi) - math.pi
                        
                        if abs(aci_farki) > 0.05:
                            durcount1 = 1
                        else:
                            durcount1 = 0

                    if self.durcount < durcount1:
                        self.dur()
                        self.durcount += 1
                        return
                    else:
                        self.durcount = 0
                        self.rota_count += 1
                        return
                else:
                    if self.gnss_userhata and False:
                        self.ileri_git(HIZLI)
                    else:
                        self.HedefeDon(hedefx, hedefy, self.filtered_gnss_enlem, self.filtered_gnss_boylam)
            #**|| Way Pointe git ||**
    
    # Verilen 2 bölge arasını istenilen parçaya bölüp engel var mı yok mu bilgisini saklar
    def AradaEngelVarmi(self, bolge1, bolge2, segment_length=1):
        arac_x, arac_y = bolge1[0], bolge1[1]
        hedefenlem, hedefboylam = bolge2[0], bolge2[1]
        angle = 0

        total_distance = math.sqrt((hedefenlem - arac_x) ** 2 + (hedefboylam - arac_y) ** 2)
    
        # Determine the number of segments
        num_segments = int(total_distance // segment_length)
        
        # Calculate the direction vector
        direction_x = (hedefenlem - arac_x) / total_distance
        direction_y = (hedefboylam - arac_y) / total_distance

        waypoints = []
        for i in range(num_segments + 1):
            new_x = arac_x + i * segment_length * direction_x
            new_y = arac_y + i * segment_length * direction_y
            waypoints.append((new_x, new_y))
        
        # Add the target point to ensure it is included as the final waypoint
        waypoints.append((hedefenlem, hedefboylam))

        for wp in waypoints:
            bolge = self.harita.bolge(wp[0], wp[1])
            bolge1 = self.harita.bolge(wp[0]+2.5, wp[1]+2.5)
            bolge2 = self.harita.bolge(wp[0]-2.5, wp[1]-2.5)
            bolge3 = self.harita.bolge(wp[0]+2.5, wp[1]-2.5)
            bolge4 = self.harita.bolge(wp[0]-2.5, wp[1]+2.5)

            if bolge.yukselti > self.engelsiniri: # Engel Var mı?
                return True

            elif bolge.ruzgar or bolge1.ruzgar or bolge2.ruzgar or bolge3.ruzgar or bolge4.ruzgar: 
                return True

            elif bolge.ucusa_yasakli_bolge or bolge1.ucusa_yasakli_bolge or bolge2.ucusa_yasakli_bolge or bolge3.ucusa_yasakli_bolge or bolge4.ucusa_yasakli_bolge:
                return True

            elif bolge.yavas_bolge or bolge1.yavas_bolge or bolge2.yavas_bolge or bolge3.yavas_bolge or bolge4.yavas_bolge:
                return True

            else:
                pass 

        return False

    # Başlangıca Döner
    def BaslangicaDon(self):
        return self.baslangic_bolgesi
    
    # Engeli geçmek için en yakın alternatif yola olan açıyı verir
    def EngelGec(self, aracx, aracy, angle_radyan, ngl = 181, senaryo = ''):
        orjinal_angle = math.degrees(angle_radyan)
        if orjinal_angle > 180:
            orjinal_angle -= 360
        elif orjinal_angle < -180:
            orjinal_angle += 360
        orjinal_angle = round(orjinal_angle)

        blok_boyutu = 20
        if senaryo == '':
            angle_katsayisi = 30
        elif senaryo == 'RUZGARLIBOLGE':
            angle_katsayisi = 75
        elif senaryo == 'YASAKLIBOLGE':
            angle_katsayisi = 75
        elif senaryo == 'YAVASBOLGE':
            angle_katsayisi = 30

        angle_katsayisi_siniri = ngl

        alternatif_yol = False
        
        # Alternatif yolları bul
        for angle_offset in range(angle_katsayisi, angle_katsayisi_siniri, angle_katsayisi):
            for sign in [1, -1]:  # 2 Tarafıda kontrol et: left (-1) and right (+1)
                test_angle = orjinal_angle + sign * angle_offset
        
                # Açı (-180,180) arasında olması lazım
                if test_angle > 180:
                    test_angle -= 360
                elif test_angle < -180:
                    test_angle += 360
                
                # Eğer yol temiz ise oradan git
                if senaryo == '':
                    # Yeni konumu hesapla
                    new_x, new_y = self.EngelTespit(aracx, aracy, test_angle, 25, False)
                    test_x, test_y = self.EngelTespit(aracx, aracy, test_angle, 20, False)
                    test2_x, test2_y = self.EngelTespit(aracx, aracy, test_angle, 10, False)
                    test3_x, test3_y = self.EngelTespit(aracx, aracy, test_angle, 5, False)
                    if not self.harita.bolge(new_x, new_y).ruzgar and not self.harita.bolge(new_x, new_y).ucusa_yasakli_bolge:
                        if self.harita.bolge(new_x, new_y).yukselti < self.engelsiniri and self.harita.bolge(test_x, test_y).yukselti < self.engelsiniri and self.harita.bolge(test2_x, test2_y).yukselti < self.engelsiniri and self.harita.bolge(test3_x, test3_y).yukselti < self.engelsiniri:
                            alternatif_yol = True
                            break
                    
                elif senaryo == 'RUZGARLIBOLGE':
                    # Yeni konumu hesapla
                    new_x, new_y = self.EngelTespit(aracx, aracy, test_angle, 30, False)
                    test_x, test_y = self.EngelTespit(aracx, aracy, test_angle, 25, False)
                    test2_x, test2_y = self.EngelTespit(aracx, aracy, test_angle, 20, False)
                    test3_x, test3_y = self.EngelTespit(aracx, aracy, test_angle, 10, False)
                    test4_x, test4_y = self.EngelTespit(aracx, aracy, test_angle, 5, False)
                    if self.harita.bolge(new_x, new_y).yukselti < self.engelsiniri and not self.harita.bolge(new_x, new_y).ucusa_yasakli_bolge:
                        if not self.harita.bolge(new_x, new_y).ruzgar and not self.harita.bolge(test_x, test_y).ruzgar and not self.harita.bolge(test2_x, test2_y).ruzgar and not self.harita.bolge(test3_x, test3_y).ruzgar and not self.harita.bolge(test4_x, test4_y).ruzgar:
                            alternatif_yol = True
                            break
                    
                elif senaryo == 'YASAKLIBOLGE':
                    new_x, new_y = self.EngelTespit(aracx, aracy, test_angle, 30, False)
                    test_x, test_y = self.EngelTespit(aracx, aracy, test_angle, 25, False)
                    test2_x, test2_y = self.EngelTespit(aracx, aracy, test_angle, 20, False)
                    test3_x, test3_y = self.EngelTespit(aracx, aracy, test_angle, 10, False)
                    test4_x, test4_y = self.EngelTespit(aracx, aracy, test_angle, 5, False)
                    if not self.harita.bolge(new_x, new_y).ruzgar and self.harita.bolge(new_x, new_y).yukselti < self.engelsiniri:
                        if not self.harita.bolge(new_x, new_y).ucusa_yasakli_bolge and \
                        not self.harita.bolge(test4_x, test4_y).ucusa_yasakli_bolge and \
                        not self.harita.bolge(test3_x, test3_y).ucusa_yasakli_bolge and \
                        not self.harita.bolge(test2_x, test2_y).ucusa_yasakli_bolge and \
                        not self.harita.bolge(test_x, test_y).ucusa_yasakli_bolge:
                            alternatif_yol = True
                            break
                            alternatif_yol = True
                            break

                elif senaryo == 'YAVASBOLGE':
                    if not self.harita.bolge(new_x, new_y).ruzgar and not self.harita.bolge(new_x, new_y).ucusa_yasakli_bolge and self.harita.bolge(new_x, new_y).yukselti < self.engelsiniri:
                        if not self.harita.bolge(new_x, new_y).yavas_bolge and not self.harita.bolge(test_x, test_y).yavas_bolge and not self.harita.bolge(test2_x, test2_y).yavas_bolge:
                            alternatif_yol = True
                            break
                    
            if alternatif_yol:
                break
        
        if alternatif_yol: # Alternatif yol var ise
            # Cezeriyi o açıya döndür ve düz git
            current_angle = test_angle
            return new_x, new_y
        else:
            return 0,0

    # 20m ötedeki alanın irtifasını ölçerek engel olup olmadığını 2. kez doğrular
    def EngelTespit(self, Ax, Ay, angle_ra, blokboyutu = 20, radianorangle = True):
        # Açıyı Derece Cinsinden Bul
        if radianorangle:
            angle = math.degrees(angle_ra) # [-180,180]
        else:
            angle = angle_ra 
        
        if angle > 180: # [-180, 180]
            angle -= 360
        elif angle < -180:
            angle += 360
        angle_round = round(angle) 

        blok_boyutu = blokboyutu # 20 metre

        if angle_round == 0:
            new_Ax = Ax + blok_boyutu
            new_Ay = Ay
        elif angle_round == 45:
            new_Ax = Ax + blok_boyutu / math.sqrt(2)
            new_Ay = Ay + blok_boyutu / math.sqrt(2)
        elif angle_round == 90:
            new_Ax = Ax
            new_Ay = Ay + blok_boyutu
        elif angle_round == 135:
            new_Ax = Ax - blok_boyutu / math.sqrt(2)
            new_Ay = Ay + blok_boyutu / math.sqrt(2)
        elif abs(angle_round) == 180:
            new_Ax = Ax - blok_boyutu
            new_Ay = Ay
        elif angle_round == -135:
            new_Ax = Ax - blok_boyutu / math.sqrt(2)
            new_Ay = Ay - blok_boyutu / math.sqrt(2)
        elif angle_round == -90:
            new_Ax = Ax
            new_Ay = Ay - blok_boyutu
        elif angle_round == -45:
            new_Ax = Ax + blok_boyutu / math.sqrt(2)
            new_Ay = Ay - blok_boyutu / math.sqrt(2)
        else:
            radian_angle = math.radians(angle)
            new_Ax = Ax + blok_boyutu * math.cos(radian_angle)
            new_Ay = Ay + blok_boyutu * math.sin(radian_angle)

        return new_Ax, new_Ay

    # En Yakın hastaneyi bulur
    def EnYakinHastaneyiBul(self):
        yeniHedefx = 0
        yeniHedefy = 0
        yeniHedefz = 0
        
        for hastane in self.harita.hastaneler:
            distance1 = math.sqrt((hastane.enlem-self.filtered_gnss_enlem)**2 + (hastane.boylam-self.filtered_gnss_boylam)**2)
            if distance1 < self.hastane_distance:
                self.hastane_distance = distance1
                yeniHedefx = hastane.enlem
                yeniHedefy = hastane.boylam
                yeniHedefz = hastane.yukselti

        self.hastane_distance = 9999
        return yeniHedefx, yeniHedefy, yeniHedefz
    
    # En Yakın iniş bölgesini bulur
    def EnYakinInisBolgesiniBul(self):
        yeniHedefx = 0
        yeniHedefy = 0
        yeniHedefz = 0
        
        for inisbolgesi in self.harita.inis_bolgeleri:
            distance1 = math.sqrt((inisbolgesi.enlem-filtered_gnss_enlem)**2 + (inisbolgesi.boylam-self.filtered_gnss_boylam)**2)
            if distance1 < self.hastane_distance:
                self.hastane_distance = distance1
                yeniHedefx = inisbolgesi.enlem
                yeniHedefy = inisbolgesi.boylam
                yeniHedefz = inisbolgesi.yukselti

        self.inisbolgesi_distance = 9999
        return yeniHedefx, yeniHedefy, yeniHedefz

    # En Yakın iniş bölgesini bulur
    def EnYakinInilebilirBolgeyiBul(self, x, y):
        inilebilirbolgeler = []
        blokboyutu1 = 0
        bolge = self.harita.bolge(x, y)
        if bolge.inilebilir:
            inilebilirbolgeler.append(bolge)
            return inilebilirbolgeler
        for _ in range(100):
            blokboyutu1 += 20
            for angle in range(-180, 180, 10):
                bolge_x, bolge_y = self.EngelTespit(x, y, angle, blokboyutu=blokboyutu1, radianorangle=False) # 20m sonranin x ve y sini verir
                bolge = self.harita.bolge(bolge_x, bolge_y)
                if bolge.inilebilir:
                    inilebilirbolgeler.append(bolge)
            if len(inilebilirbolgeler) > 0:
                break
        return inilebilirbolgeler  

    # Verilen Hedefe Döner ve Düz Gider
    def HedefeDon(self, hedef_x, hedef_y, arac_x, arac_y, duzgit=True): 
        hizkatsayisi = 1.5
        aci = math.atan2(hedef_y - arac_y, hedef_x - arac_x)
        DEAD_ZONE = 0.1
                
        if self.manyetometre.hata:
            gecicideger = self.FilterData(100, acisalhiz=True)

            current_time = self.zaman()
            dt = current_time - self.onceki_zaman_manyetometre
            self.onceki_zaman_manyetometre = current_time
            
            # Apply damping to reduce the effect of sudden large changes
            self.manyetometre_user_data -= gecicideger * dt
            self.filtered_manyetometre = self.manyetometre_user_data
            
            aci_farki = aci - self.manyetometre_user_data
            
            magnitude = 0.02
            hizkatsayisi = 0.2
        else:
            if self.filtered_manyetometre > math.pi - 0.3:  # Adjust the threshold as necessary
                self.filtered_manyetometre -= 2 * math.pi
            elif self.filtered_manyetometre < -math.pi + 0.3:
                self.filtered_manyetometre += 2 * math.pi
                
            self.manyetometre_user_data = self.filtered_manyetometre
            aci_farki = aci - self.filtered_manyetometre
            self.onceki_zaman_manyetometre = self.zaman() 

            if self.motorarizasivar and self.gnss_userhata:
                magnitude = 0.05
                hizkatsayisi = 1 
            elif self.gnss_userhata:
                magnitude = 0.005
            else:
                magnitude = 0.01
                if self.hedef_enlemboylam_ulasildi:
                    magnitude = 0.008
                    hizkatsayisi = 0.75

        aci_farki = (aci_farki + math.pi) % (2 * math.pi) - math.pi

        if abs(aci_farki) < magnitude: 
            if duzgit:
                newx, newy = self.EngelTespit(self.filtered_gnss_enlem, self.filtered_gnss_boylam, self.filtered_manyetometre)
                if self.harita.bolge(newx, newy).yavas_bolge or self.harita.bolge(self.filtered_gnss_enlem, self.filtered_gnss_boylam).yavas_bolge:
                    self.ileri_git(YAVAS)
                else:
                    self.ileri_git(HIZLI)
            else:
                pass
        else:
            if self.manyetometre.hata:
                self.don(aci_farki)
            else: 
                if self.gnss_userhata:
                    if aci_farki>0.05:
                        self.dur()
                    self.don(aci_farki * hizkatsayisi)
                else:
                    self.don(aci_farki * hizkatsayisi)
     
    # İniş yapar
    def HedefeinisYap(self, gnsshata=False):
        self.dur()
        bolge = self.harita.bolge(self.filtered_gnss_enlem, self.filtered_gnss_boylam)
        #print("--------------")
        #print(bolge.inilebilir, self.lidar.hata)
        if bolge.inilebilir or gnsshata or bolge.inis_bolgesi or True: # bolge inilebilir vs. calismadigi icin suanlik bu 2. kontrol yapilmayacak
            if self.lidar.hata:
                if self.radar.hata:
                    self.asagi_git(YAVAS)
                else:  
                    if self.radar.mesafe <= 5:
                        self.hedefe_ulasildi = True
                        return True
                    elif self.radar.mesafe <= 15:
                        self.asagi_git(YAVAS)
                        return False
                    else:
                        self.asagi_git(HIZLI)
                        return False
                
            else:
                if self.lidar.mesafe <= 5:
                    self.hedefe_ulasildi = True
                    return True
                elif self.lidar.mesafe <= 15:
                    self.asagi_git(YAVAS)
                    return False
                else:
                    self.asagi_git(HIZLI)
                    return False
            
        else:
            self.ileri_git(YAVAS) # EKSIK: Hedefe don sonra yavasca ileri git.
            return False
        
    # Şarj bölgesine iniş yapar sonra kalkar
    def SarjIstasyonunainisYap(self, gnsshata=False):
        self.dur()
        bolge = self.harita.bolge(self.filtered_gnss_enlem, self.filtered_gnss_boylam)
        if bolge.inilebilir or gnsshata:
            if self.lidar.hata:
                if self.radar.hata:
                    self.asagi_git(YAVAS)
                else:
                    if self.radar.mesafe <= 2:
                        self.sarj_istasyonuna_ulasildi = True
                        return True
                    elif self.radar.mesafe <= 15:
                        self.asagi_git(YAVAS)
                        return False
                    else:
                        self.asagi_git(HIZLI)
                        return False
               
            else:
                if self.lidar.mesafe <= 2:
                    self.sarj_istasyonuna_ulasildi = True
                    return True
                elif self.lidar.mesafe <= 15:
                    self.asagi_git(YAVAS)
                    return False
                else:
                    self.asagi_git(HIZLI)
                    return False
            
        else:
            #print("HELLO TEST #")
            self.ileri_git(YAVAS) # EKSIK: Hedefe don sonra yavasca ileri git.
            return False
     
    # Gidilecek hedefleri sıralar: Hedefler sırasız iseler en uygun mesafeye göre sıralar
    def HedefSirasiniBelirle(self):
        sira = [None] * len(self.harita.yangin_bolgeleri)
        self.siralimi = False

        for hedef in self.harita.yangin_bolgeleri:
            hedef.amac = 1
            self.hedef_amaclar.append(3)
            #if hedef.sira == -1:
              #  sira.append(hedef)
            #elif hedef.sira == 0:
               # sira.insert(0, hedef)
               # self.siralimi = False
            #else:
               # sira[hedef.sira-1] = hedef
            sira.append(hedef)
        
        return [i for i in sira if i is not None]

    def HedefSirasiniDuzenle(self, sira):
        if not self.siralimi and len(sira)>2:
            best_order = None
            best_distance = 9999  

            sira.insert(0, self.baslangic_bolgesi)
            middle_part = sira[1:-1] 

            for perm in itertools.permutations(middle_part):
                total_distance = self.distance(sira[0], perm[0])  # From start to the first permuted element
                for i in range(1, len(perm)):
                    total_distance += self.distance(perm[i-1], perm[i])
                total_distance += self.distance(perm[-1], sira[-1])  # From the last permuted element to the end
                
                # Check if this is the shortest path found
                if total_distance < best_distance:  
                    best_distance = total_distance
                    best_order = perm

            # Rebuild the sira list with the best middle order
            sira = [sira[0]] + list(best_order) + [sira[-1]]
        else: 
            sira.insert(0, self.baslangic_bolgesi)

        if self.baslangica_don:
            sira.append(self.baslangic_bolgesi)
            self.hedef_amaclar.append(0)

        sira = self.ensure_battery_capacity(sira) 

        del sira[0]

        seen = set()
        new_sira = []
        for hedef in sira:
            if hasattr(hedef, 'bolge'):
                enlem_boylam = (hedef.bolge.enlem, hedef.bolge.boylam)
            else:
                enlem_boylam = (hedef.enlem, hedef.boylam)

            if enlem_boylam in seen:
                if hasattr(hedef, 'bolge'):
                    continue  # Skip adding this element, as we prefer the one without 'bolge'
                else:
                    # Remove the previously added item with 'bolge' attribute
                    new_sira = [h for h in new_sira if (
                        (h.bolge.enlem, h.bolge.boylam) if hasattr(h, 'bolge') else (h.enlem, h.boylam)
                    ) != enlem_boylam]
            else:
                seen.add(enlem_boylam)
                new_sira.append(hedef)
        
        sira = new_sira

        return sira
     
    # Batarya yetecek mi kontrol eder
    def ensure_battery_capacity(self, sira):
        kapat = 0
        total_distance = 0
        i = 0

        battery_levels = []

        while i < len(sira) - 1:
            current_distance = self.distance(sira[i], sira[i+1])
            total_distance += current_distance

            battery_levels.append(self.kalan_batarya)

            self.kalan_batarya -= current_distance /  self.birimbatarya  # 1 batarya  self.birimbatarya metre

            if self.kalan_batarya < 0:
                best_battery_station = None
                best_battery_station2 = []
                best_battery_distance = 9999
                self.kalan_batarya += current_distance /  self.birimbatarya
                backtrack_index = i
                 
                for station in self.harita.sarj_istasyonlari:
                    if station == self.sonstation:
                        continue
                    distance_to_station = self.distance(sira[i], station)
                    distance_station_to_next = self.distance(station, sira[i+1])
                    
                    if (distance_station_to_next < current_distance) and (distance_to_station <= (self.kalan_batarya* self.birimbatarya)):
                        if len(best_battery_station2)>0:
                            if distance_station_to_next<best_battery_station2[-1]:
                                self.sonstation = station
                                best_battery_station = station
                                best_battery_distance = distance_to_station
                                best_battery_station2.append(distance_station_to_next)
                            else:
                                pass                         
                        else:
                            self.sonstation = station
                            best_battery_station = station
                            best_battery_distance = distance_to_station
                            best_battery_station2.append(distance_station_to_next)
                    else:
                        self.sonstation
                
                if best_battery_station:
                    sira.insert(i + 1, best_battery_station)
                    self.kalan_batarya = 79
                    self.eskibolgeistasyon = 0
                    self.eskibolgeistasyon2 = 0
                else:
                    best_battery_station = self.OncekiNoktadanStationBul(i-1, sira, current_distance, battery_levels[-2])
                    if best_battery_station:
                        sira.insert(i, best_battery_station)
                        self.kalan_batarya = 79
                        i -= 1
                    else:
                        kapat = True
                        break
            else:
                if hasattr(sira[i+1], 'bolge'):
                    self.sonstation = sira[i+1].bolge
                else:
                    self.sonstation = sira[i+1]
            
            if kapat>20:
                break
            i += 1
            kapat += 1
 
        return sira
    
    def OncekiNoktadanStationBul(self, index, sira, original_distance, battery):
        while index >= 0:
            for station in self.harita.sarj_istasyonlari:
                if station == self.eskibolgeistasyon or station == self.eskibolgeistasyon2:
                    continue
                distance_to_station = self.distance(sira[index], station)
                distance_station_to_next = self.distance(station, sira[index + 1])

                # Check if the station is feasible from the previous point
                if (distance_station_to_next < original_distance) and (distance_to_station <= (battery * self.birimbatarya)):
                    if hasattr(sira[index], 'bolge'):
                        self.eskibolgeistasyon = sira[index].bolge
                    else:
                        self.eskibolgeistasyon = sira[index]
                    self.eskibolgeistasyon2 = station
                    return station

            index -= 1

        return None

    # Distance verir 2 bolge arasindaki. Bolge olmasada olur.
    def distance(self, hedef1, hedef2):
        enlem1 = hedef1.enlem if hasattr(hedef1, 'enlem') else hedef1.bolge.enlem
        boylam1 = hedef1.boylam if hasattr(hedef1, 'boylam') else hedef1.bolge.boylam
        enlem2 = hedef2.enlem if hasattr(hedef2, 'enlem') else hedef2.bolge.enlem
        boylam2 = hedef2.boylam if hasattr(hedef2, 'boylam') else hedef2.bolge.boylam
        return math.sqrt((enlem2 - enlem1) ** 2 + (boylam2 - boylam1) ** 2)

    # INIT fonksiyonu    
    def RotayiYenidenHesapla(self):
        mesafe_x = self.hedef_bolge.enlem - self.arac_x
        mesafe_y = self.hedef_bolge.boylam - self.arac_y 
        if abs(mesafe_y) < 30 and abs(mesafe_x) < 30: 
            self.angle = math.atan2(self.hedef_bolge.boylam - self.arac_y, self.hedef_bolge.enlem - self.arac_x) # Hedefe olan açı (Radyan)
            new_x, new_y = self.EngelTespit(self.arac_x, self.arac_y, self.angle, blokboyutu=2)
            self.rota.append((new_x, new_y, False, False, False)) # Eğer sıradakı hedef çok yakınsa öylesine aradan boş bir konum girki hata vermesin
            self.arac_yukselti = self.hedef_bolge.yukselti
        else:
            for _ in range(1000):
                self.angle = math.atan2(self.hedef_bolge.boylam - self.arac_y, self.hedef_bolge.enlem - self.arac_x) # Hedefe olan açı (Radyan)
                new_x, new_y = self.EngelTespit(self.arac_x, self.arac_y, self.angle, blokboyutu=20)
                new_test_x, new_test_y = self.EngelTespit(self.arac_x, self.arac_y, self.angle, blokboyutu=15)
                new_test_x2, new_test_y2 = self.EngelTespit(self.arac_x, self.arac_y, self.angle, blokboyutu=10)
                new_test_x3, new_test_y3 = self.EngelTespit(self.arac_x, self.arac_y, self.angle, blokboyutu=5)
                engelvarmi = False
                ruzgarvarmi = False
                yasaklibolgevarmi = False
                bolge = self.harita.bolge(new_x, new_y)
                bolgetest = self.harita.bolge(new_test_x, new_test_y)
                bolgetest2 = self.harita.bolge(new_test_x2, new_test_y2)
                bolgetest3 = self.harita.bolge(new_test_x3, new_test_y3)

                if self.arac_yukselti > self.azami_yukseklik + 10:
                    new_x, new_y = self.EngelTespit(self.arac_x, self.arac_y, self.angle, blokboyutu=45)
                    self.arac_x, self.arac_y = new_x, new_y
                    self.arac_yukselti = self.hedef_bolge.yukselti

                if bolgetest.yukselti > self.engelsiniri:
                    new_x, new_y = self.EngelGec(self.arac_x, self.arac_y, self.angle)
                    engelvarmi = True
                elif bolge.yukselti > self.engelsiniri or bolge.yavas_bolge:
                    new_x, new_y = self.EngelGec(self.arac_x, self.arac_y, self.angle)
                    engelvarmi = True  
                elif bolgetest.ruzgar: 
                    new_x, new_y = self.EngelGec(self.arac_x, self.arac_y, self.angle, senaryo = 'RUZGARLIBOLGE')
                    ruzgarvarmi = True 
                elif bolge.ruzgar:
                    new_x, new_y = self.EngelGec(self.arac_x, self.arac_y, self.angle, senaryo = 'RUZGARLIBOLGE')
                    ruzgarvarmi = True  
                elif bolge.ucusa_yasakli_bolge:
                    new_x, new_y = self.EngelGec(self.arac_x, self.arac_y, self.angle, senaryo = 'YASAKLIBOLGE')
                    yasaklibolgevarmi = True   
                elif bolgetest.ucusa_yasakli_bolge or bolgetest2.ucusa_yasakli_bolge or bolgetest3.ucusa_yasakli_bolge:
                    new_x, new_y = self.EngelGec(self.arac_x, self.arac_y, self.angle, senaryo = 'YASAKLIBOLGE')
                    yasaklibolgevarmi = True   
                elif bolge.yavas_bolge:
                    new_x, new_y = self.EngelGec(self.arac_x, self.arac_y, self.angle, senaryo = 'YAVASBOLGE')
                    yasaklibolgevarmi = True  
                elif bolgetest.yavas_bolge:
                    new_x, new_y = self.EngelGec(self.arac_x, self.arac_y, self.angle, senaryo = 'YAVASBOLGE')
                    yasaklibolgevarmi = True  
                
                mesafe_x = self.hedef_bolge.enlem - self.arac_x
                mesafe_y = self.hedef_bolge.boylam - self.arac_y 

                if abs(mesafe_y) < 30 and abs(mesafe_x) < 30: 
                    break
                elif self.hedef_bolge.yukselti > 200:
                    if abs(mesafe_y) < 50 and abs(mesafe_x) < 50: 
                        break

                self.rota.append((new_x, new_y, engelvarmi, ruzgarvarmi, yasaklibolgevarmi)) # Enlem Boylam Engel
                self.arac_x, self.arac_y = new_x, new_y

            self.arac_yukselti = self.hedef_bolge.yukselti

            self.rota.insert(0, (self.filtered_gnss_enlem, self.filtered_gnss_boylam, False, False, False))
            #*******|| Rota Oluşturulması ||********
            #*******|| Rota Kısaltılması ||********
            index = 0 
            while index < len(self.rota) - 1: 
                last_no_obstacle_index = index 
                # Start from the next waypoint and try to find the farthest waypoint without obstacles
                for index2 in range(index + 1, len(self.rota)):
                    waypoint2 = self.rota[index2]

                    # Check if there is an obstacle between the current waypoint and the next
                    if self.AradaEngelVarmi(self.rota[index], waypoint2, segment_length=1):
                        break
                    elif self.AradaEngelVarmi(self.rota[index], waypoint2, segment_length=15):
                        break
                    elif self.AradaEngelVarmi(self.rota[index], waypoint2, segment_length=10):
                        break
                    elif self.AradaEngelVarmi(self.rota[index], waypoint2, segment_length=5):
                        break
                    elif self.AradaEngelVarmi(self.rota[index], waypoint2, segment_length=2):
                        break
                    #elif self.rota[index2][4] or self.rota[index][4] or self.rota[index2][3] or self.rota[index][3]:
                    # break
                    else:
                        # If no obstacle, set index2 as the new waypoint to compare from index
                        last_no_obstacle_index = index2

                # Delete waypoints between the current one and the last one without an obstacle
                if last_no_obstacle_index > index + 1:
                    del self.rota[index + 1:last_no_obstacle_index]
                
                index += 1

            del self.rota[0]

        #print(self.hedef_bolge)
        #print(self.baslangic_bolgesi)
        #print("------------")
        #print(self.rota)
            #*******|| Rota Kısaltılması ||********
     
    # Azami Yüksekliğe Yükselir
    def KalkisYap(self): 
        if self.motorarizasivar:
            pass
        #elif self.baslangica_don:
           # pass
        else:    
            hedefx, hedefy = self.rota[self.rota_count][0], self.rota[self.rota_count][1]
            self.HedefeDon(hedefx, hedefy, self.filtered_gnss_enlem, self.filtered_gnss_boylam, duzgit=False)
        if self.gnss_userhata:
            if self.barometre.irtifa >= (self.azami_yukseklik-10) and not self.kalkis_yap:
                self.yukseklige_ulasildi=True
                self.dur()
                self.kalkis_yap = True
                return True
            elif self.yukseklige_ulasildi == False: 
                self.yukari_git(HIZLI)
                return False
            else:  
                pass
        else:
            if self.gnss.irtifa >= (self.azami_yukseklik-10) and not self.kalkis_yap:
                self.yukseklige_ulasildi=True
                self.dur()
                self.kalkis_yap = True
                return True
            elif self.yukseklige_ulasildi == False:
                self.yukari_git(HIZLI)
                return False
            else:  
                pass

    def UzunBinayaKalkisYap(self):
        if self.barometre.hata:
            if self.gnss.irtifa < self.azami_yukseklik+45:
                self.yukari_git(HIZLI)
                return False
            else:
                return True
        else:
            if self.barometre.irtifa < self.azami_yukseklik+45:
                self.yukari_git(HIZLI)
                return False
            else:
                return True
    
    def UzunBinadanInisYap(self, barometre=False):
        self.dur()
        if barometre:
            if self.gnss.irtifa>118:
                self.asagi_git(HIZLI)
                return True
            else:
                self.uzunbinadaninis = False
                return False
        else:
            if self.barometre.irtifa>118:
                self.asagi_git(HIZLI)
                return True
            else:
                self.uzunbinadaninis = False
                return False
            
    # İstenilen değeri istenildiği kadar filtrelenir ve geri gönderilir
    def FilterData(self, katsayi, manyetometre=False, gnssenlem=False, gnssboylam=False, imux=False, imuy=False, imuz=False, acisalhiz=False, deviationimux=False, deviationimuz=False):
        if manyetometre:
            filtered_list = [self.manyetometre.veri for _ in range(katsayi)]
            return sum(filtered_list) / len(filtered_list)
        elif gnssenlem:
            filtered_list = [self.gnss.enlem for _ in range(katsayi)]
            return sum(filtered_list) / len(filtered_list)
        elif gnssboylam: 
            filtered_list = [self.gnss.boylam for _ in range(katsayi)]
            return sum(filtered_list) / len(filtered_list)
        elif imux:
            filtered_list = [self.imu.hiz.x for _ in range(katsayi)]
            if len(self.filteredimux_list)<4:
                self.filteredimux_list.append(sum(filtered_list) / len(filtered_list)) 
                return sum(filtered_list) / len(filtered_list) + self.standard_deviation_imu_x
            else:
                self.filteredimux_list.append(sum(filtered_list) / len(filtered_list))
                deneme = sum(self.filteredimux_list)/5.0
                self.filteredimux_list.pop(0)
                return deneme + self.standard_deviation_imu_x
        elif imuy:
            filtered_list = [self.imu.hiz.y for _ in range(katsayi)]
            if len(self.filteredimuy_list)<4:
                self.filteredimuy_list.append(sum(filtered_list) / len(filtered_list)) 
                return sum(filtered_list) / len(filtered_list)
            else:
                self.filteredimuy_list.append(sum(filtered_list) / len(filtered_list))
                deneme = sum(self.filteredimuy_list)/5.0
                self.filteredimuy_list.pop(0)
                return deneme
        elif imuz:
            filtered_list = [self.imu.hiz.z for _ in range(katsayi)]
            if len(self.filteredimuz_list)<4:
                self.filteredimuz_list.append(sum(filtered_list) / len(filtered_list)) 
                return sum(filtered_list) / len(filtered_list) + self.standard_deviation_imu_z
            else:
                self.filteredimuz_list.append(sum(filtered_list) / len(filtered_list))
                deneme = sum(self.filteredimuz_list)/5.0
                self.filteredimuz_list.pop(0)
                return deneme + self.standard_deviation_imu_z
        elif acisalhiz:
            filtered_list = [self.imu.acisal_hiz.y for _ in range(katsayi)]
            #if abs(sum(filtered_list) / len(filtered_list)) < 0.2:
               # return 0
            return (sum(filtered_list) / len(filtered_list))

        elif deviationimux:
            filtered_list = [(0 - self.FilterData(40, imux=True)) for _ in range(katsayi)]
            return (sum(filtered_list) / len(filtered_list))
        
        elif deviationimuz:
            filtered_list = [(0 - self.FilterData(40, imuz=True)) for _ in range(katsayi)]
            return (sum(filtered_list) / len(filtered_list))

# Kargo       
class Kargo(KargoParent):
  def __init__(self, id = 0):
      super().__init__(id = id, keyboard = False, sensor_mode = NORMAL)
      #print(self.hedefler)
      #print("------------")
      #print(self.harita.teslimat_bolgeleri, "TEST")
      #print("Cemre")
      #print(self.harita.teslimat_bolgeleri[0].enlem, self.harita.teslimat_bolgeleri[0].boylam)
      #print("Cemre")
      #print(self.baslangica_don)
      #print("Cemre")

      self.hedef_amaclar = []
      self.hedef_amac = None

      # Kargo
      self.kargoteslimedildimi = False
      # Kargo

      self.baslangic_bolgesi = self.harita.bolge(self.gnss.enlem, self.gnss.boylam)
      #print(self.baslangic_bolgesi.enlem, self.baslangic_bolgesi.boylam)
      self.baslangic_bolgesi.amac = 0 # KULLANILMIYOR SUANDA AMA KALSIN CEMRE MART 11
      # self.hedef_amaclar.append(0) # Baslangic bolgesi amaci

      self.engelsiniri = 60.0 - 15 # Azami Yukseklik - 10 (HATA PAYI)
      self.azami_yukseklik = 60.0 # Kargo Azami Yukseklik
      self.birimbatarya = 11

      self.test2 = True

      #*******|| Filtre ||********
      self.filteredimux_list = []
      self.filteredimuy_list = []
      self.filteredimuz_list = []
      self.filteredgnssenlem_list = []
      self.filteredgnssboylam_list = []
      self.filteredmanyetometre_list = []
      self.standard_deviation_gnss_enlem = 0
      self.standard_deviation_gnss_boylam = 0
      self.standard_deviation_imu_x = 0
      self.standard_deviation_imu_z = 0
      self.filtered_gnss_enlem = self.FilterData(200, gnssenlem=True)
      self.filtered_gnss_boylam = self.FilterData(200, gnssboylam=True)
      self.filtered_manyetometre = self.FilterData(500, manyetometre=True)
      self.son_GNSS_enlem = self.filtered_gnss_enlem
      self.son_GNSS_boylam = self.filtered_gnss_boylam
      self.son_manyetometre = self.filtered_manyetometre
      self.standard_deviation_gnss_enlem = self.baslangic_bolgesi.enlem - self.filtered_gnss_enlem
      self.standard_deviation_gnss_boylam = self.baslangic_bolgesi.boylam - self.filtered_gnss_boylam
      self.standard_deviation_imu_x = self.FilterData(50, deviationimux=True) 
      self.standard_deviation_imu_z = self.FilterData(50, deviationimuz=True) 
      #*******|| Filtre ||********

      #*******|| Batarya ||******** 
      if self.batarya.hata == 1:
          self.kalan_batarya = 80
          self.eski_batarya_veri = 80
      else:
          self.kalan_batarya = self.batarya.veri - 20
          self.eski_batarya_veri = self.batarya.veri - 20

      self.bataryabekle = 0
      self.sonstation = 0
      self.eskibolgeistasyon = 0
      self.eskibolgeistasyon2 = 0
      #*******|| Batarya ||******** 

      #*******|| Hedef Bölge Hesabı ||********
      self.siralimi = True
      self.hedefrotasi = self.HedefSirasiniBelirle() # Hedefleri sıralar
      self.hedefrotasi = self.HedefSirasiniDuzenle(self.hedefrotasi)

      #print(self.hedefrotasi, self.hedef_amaclar)
      #for index, hedef in enumerate(self.hedefrotasi):
          #print(index, hedef.enlem, hedef.boylam, self.hedef_amaclar[index])
          ##print(hedef, self.hedef_amaclar[index])

      self.hedefrotasicount = 0
      self.hedef = self.hedefrotasi[self.hedefrotasicount]
      if hasattr(self.hedefrotasi[self.hedefrotasicount], 'bolge'):
          self.hedef_bolge = self.hedefrotasi[self.hedefrotasicount].bolge
      else:
          self.hedef_bolge = self.hedefrotasi[self.hedefrotasicount]
          self.hedef_amac = self.hedef_amaclar[self.hedefrotasicount]
      self.baslangicadonulsunmu = False

      self.hedefbolgedegistimi_count = 0 
      self.eskihedefler = [(hedef.enlem, hedef.boylam) for hedef in self.harita.teslimat_bolgeleri]
      #*******|| Hedef Bölge Hesabı ||********

      #*******|| Kalkış yap / İniş yap ||******** 
      self.hedefe_ulasildi = False 
      self.sarj_istasyonuna_ulasildi = False  
      self.hedef_enlemboylam_ulasildi = False  
      self.hedef_enlemboylam_ulasildi_kargo = False
      self.kalkis_yap = False
      self.yukseklige_ulasildi = False
      self.yenihedefdurcount = 0
      #*******|| Kalkış yap / İniş yap ||********

      #*******|| Acil Durum ||********
      self.acildurumdogrulandi = False
      self.hastane_dur_count = 0
      self.hastane_distance = 9999
      #*******|| Acil Durum ||********

      #*******|| Motor Arızası ||********
      self.motorasagigit = False
      self.motorarizasidogrulandi = False
      self.motor_dur_count = 0
      self.motorarizasivar = False
      self.gnssmotorhata = False
      #*******|| Motor Arızası ||********

      #*******|| GNSS Arızası ||********
      self.gnss_dur = 0
      self.gnss_userhata = self.gnss.hata
      self.spoofingbekleme = 0
      self.onceki_zaman_gnss = self.zaman()
      self.gnss_userdata_x = self.filtered_gnss_enlem
      self.gnss_userdata_z = self.filtered_gnss_boylam
      self.gnsshatasidogrulandi = False
      #*******|| GNSS Arızası ||********

      #*******|| Manyetometre Arızası ||********
      self.onceki_zaman_manyetometre = self.zaman()
      self.manyetometre_user_data = self.filtered_manyetometre
      self.previous_gecicideger = 0.0
      #*******|| Manyetometre Arızası ||********

      #*******|| Rota Hesabı ||********
      self.rota = []   
      self.rota_count = 0
      self.arac_x, self.arac_y = self.filtered_gnss_enlem, self.filtered_gnss_boylam
      self.durcount = 0 
      #*******|| Rota Hesabı ||********

      #*******|| Rota Oluşturulması / Kısaltılması ||******** 
      self.arac_yukselti = self.baslangic_bolgesi.yukselti
      self.RotayiYenidenHesapla()
      #*******|| Rota Oluşturulması / Kısaltılması ||******** 

      self.uzunbinadogrulandi = False
      self.uzunbinadaninis = False
      self.sonradarverileri = []
      self.sonlidarverileri = []

      self.sensor_mode = ''
      if self.imu.acisal_hiz.y==0 or self.imu.acisal_hiz.x==0 or self.imu.acisal_hiz.z==0:
          self.sensormode = "DUZELTILMIS"
      else:
          self.sensormode = "NORMAL"

  def run(self):
      super().run()

      #print(self.kargo_durumu)


      ##print(self.manyetometre.veri)
      #*******||Filter||********
      if not self.gnss_userhata or not self.gnss.hata:
          self.filtered_gnss_enlem = self.FilterData(50, gnssenlem=True)
          self.filtered_gnss_boylam = self.FilterData(50, gnssboylam=True)

          #*******||Trafik||******** 

          bolgetrafik = self.harita.bolge(self.filtered_gnss_enlem, self.filtered_gnss_boylam)

          if self.tamamlandi:
              bolgeler[self.id - 1] = None
          else:
              bolgeler[self.id - 1] = bolgetrafik
              sarj_durumlari[self.id - 1] = self.batarya
              if self.gnss.irtifa < 100:
                  inisebaslandimitrafik[self.id - 1] = True
              else:
                  inisebaslandimitrafik[self.id - 1] = False
              yukseltitrafik[self.id - 1] = self.gnss.irtifa

              bekle = False

              for i in range(len(bolgeler)):
                  if i == self.id - 1:
                      continue

                  oteki_bolge = bolgeler[i]            
                  if oteki_bolge == None:
                      continue
                  oteki_sarj = sarj_durumlari[i]

                  cezeriler_arasi_mesafe = bolgeler_arasi_mesafe(oteki_bolge, bolgetrafik)
                  if cezeriler_arasi_mesafe <= 65:

                      batarya_veri = round(self.batarya.veri, 0)
                      oteki_batarya_veri = round(oteki_sarj.veri, 0)
                      inisebasladimiben = inisebaslandimitrafik[self.id - 1]
                      inisebasladimioteki = inisebaslandimitrafik[i]
                      yukseltiben = self.id - 1
                      yukseltioteki = i

                      if not inisebasladimiben and inisebasladimioteki:
                          self.dur()
                          bekle = True
                      elif yukseltiben<yukseltioteki:
                          bekle = True
                          self.dur()

                      if inisebasladimiben:
                          bekle = False
              
              if bekle:
                  self.dur()
                  return

          #*******||Trafik||******** 
    
      if not self.manyetometre.hata:
          self.filtered_manyetometre = self.FilterData(100, manyetometre=True)
      #*******||Filter||********

      #*******|| Kalkış / Bitiş / İniş||********
      if self.uzunbinadogrulandi:
          if self.UzunBinayaKalkisYap():
              self.uzunbinadogrulandi = False
          else:
              return

      if self.hedef_bolge.yukselti < (self.azami_yukseklik - 20):
          if self.barometre.hata:
              if self.gnss.hata:
                  pass
              else:
                  if self.gnss.irtifa > (self.azami_yukseklik + 30) or self.uzunbinadaninis:
                      self.sonlidarverileri.append(self.lidar.mesafe)
                      if len(self.sonlidarverileri)>15:
                          self.sonlidarverileri.pop(0)
                      self.uzunbinadaninis = True
                      if self.lidar.hata:
                          self.sonradarverileri.append(self.radar.mesafe)
                          if len(self.sonradarverileri)>15:
                              self.sonradarverileri.pop(0)
                          if self.radar.hata:
                              pass 
                          else:
                              if all(value > (self.azami_yukseklik - 20) for value in self.sonradarverileri):
                                  if self.UzunBinadanInisYap(True):
                                      return
                      else:
                          if all(value > (self.azami_yukseklik - 20) for value in self.sonlidarverileri):
                              if self.UzunBinadanInisYap(True):
                                  return
          else:
              if self.barometre.irtifa > (self.azami_yukseklik + 30) or self.uzunbinadaninis:
                  self.sonlidarverileri.append(self.lidar.mesafe)
                  if len(self.sonlidarverileri)>15:
                      self.sonlidarverileri.pop(0)
                  self.uzunbinadaninis = True
                  if self.lidar.hata:
                      self.sonradarverileri.append(self.radar.mesafe)
                      if len(self.sonradarverileri)>15:
                          self.sonradarverileri.pop(0)
                      if self.radar.hata:
                          pass
                      else:
                          if all(value > (self.azami_yukseklik - 20) for value in self.sonradarverileri):
                              if self.UzunBinadanInisYap():
                                  return
                  else:
                      if all(value > (self.azami_yukseklik - 20) for value in self.sonlidarverileri):
                          if self.UzunBinadanInisYap():
                              return
              
      if not self.kalkis_yap: 
          if self.KalkisYap():
              pass
          else:
              return
      if self.sarj_istasyonuna_ulasildi:
          if self.batarya.hata:
              if self.bataryabekle < 100:
                  self.bataryabekle += 1
                  return
              else:
                  pass
          else:
              if self.batarya.veri <= 98.9: 
                  return
              else:
                  self.hedefrotasicount += 1
                  if hasattr(self.hedefrotasi[self.hedefrotasicount], 'bolge'):
                      self.hedef = self.hedefrotasi[self.hedefrotasicount]
                      self.hedef_bolge = self.hedefrotasi[self.hedefrotasicount].bolge
                  else:
                      if len(self.hedefrotasi) <= (self.hedefrotasicount + 1):
                          if self.baslangica_don: 
                              self.hedef_amac = 0
                              self.hedef_bolge = self.hedefrotasi[self.hedefrotasicount]
                      else:             
                          self.hedef_amac = self.hedef_amaclar[self.hedefrotasicount]
                          self.hedef_bolge = self.hedefrotasi[self.hedefrotasicount]
                          
                  # Rota
                  self.rota = []
                  self.rota_count = 0
                  self.arac_x, self.arac_y = self.filtered_gnss_enlem, self.filtered_gnss_boylam
                  self.durcount = 0

                  # Kalkış Yap / Hedefe Ulaşıldı
                  self.hedefe_ulasildi = False
                  self.hedef_enlemboylam_ulasildi =False
                  self.kalkis_yap = False
                  self.yukseklige_ulasildi = False
                  self.RotayiYenidenHesapla()

                  self.sarj_istasyonuna_ulasildi = False

                  return
      if self.hedefe_ulasildi:
          print("GÖREV TAMAMLANDI")
          if self.kargo_durumu: # Sadece bir kargo icin calisir
            self.teslim_et()
            print("Kargo ulaşıldı")
                                        
          return
      if self.gnsshatasidogrulandi:
          self.HedefeinisYap(gnsshata = True)
          return
      if self.hedef_enlemboylam_ulasildi:
          self.HedefeinisYap()
      if self.hedef_enlemboylam_ulasildi_kargo:
          self.kargoyainisyap()
      #*******|| Kalkış / Bitiş / İniş||********

      #*******||Spoff Detect / GNSS Detect||********
      if self.gnss_userhata == 0: 
          if self.spoofingbekleme<50:
              self.spoofingbekleme += 1
          elif self.son_GNSS_enlem > self.filtered_gnss_enlem+15 or self.son_GNSS_enlem < self.filtered_gnss_enlem-15:
              self.gnss_userhata = 1
      if self.gnss.hata == 1:
          self.gnss_userhata = 1
      if self.gnss_userhata == 0:
          self.son_GNSS_enlem = self.filtered_gnss_enlem
          self.son_GNSS_boylam = self.filtered_gnss_boylam
          self.son_manyetometre = self.filtered_manyetometre 

          self.gnss_userdata_x = self.filtered_gnss_enlem
          self.gnss_userdata_z = self.filtered_gnss_boylam
          self.onceki_zaman_gnss = self.zaman()
      else:
          if self.gnss_dur < 1:
              self.dur()
              self.gnss_dur += 1
              return

          dt = self.zaman() - self.onceki_zaman_gnss
          self.onceki_zaman_gnss = self.zaman()
          self.gnss_userdata_x += self.FilterData(100, imux=True) * dt
          self.gnss_userdata_z += self.FilterData(100, imuz=True) * dt
          
          self.filtered_gnss_enlem = self.gnss_userdata_x
          self.filtered_gnss_boylam = self.gnss_userdata_z 
      #*******||Spoff Detect / GNSS Detect||******** 
      
      if self.yukseklige_ulasildi or self.gnss_userhata == 0:
          #*******|| Hedef Değişti mi? / Başlangıca Dönülsün mü? ||********
          if self.motorarizasivar or self.acildurumdogrulandi:
              hedef_bolge_degistimi = False
          else:
              hedef_bolge_degistimi = False
              ### ITFAIYEDE HEDEF BOLGE DEGISMIYOR DIYE VARSAYDIM DEGISIYORSA GEREKEN LOGIC BURAYA EKLENECEK
              pass
            
          if not hedef_bolge_degistimi:  
              pass
          else:
              self.hedefrotasi = self.HedefSirasiniBelirle() # Hedefleri sıralar
              self.hedefrotasi = self.HedefSirasiniDuzenle(self.hedefrotasi)
              self.hedefbolgedegistimi_count = 0
              self.hedef = self.hedefrotasi[self.hedefrotasicount]
              if hasattr(self.hedefrotasi[self.hedefrotasicount], 'bolge'):
                  self.hedef_bolge = self.hedefrotasi[self.hedefrotasicount].bolge
              else:
                  self.hedef_bolge = self.hedefrotasi[self.hedefrotasicount]

              #*******|| Kalkış yap / İniş yap ||********
              self.hedefe_ulasildi = False   
              self.hedef_enlemboylam_ulasildi =False
              self.kalkis_yap = False
              self.yukseklige_ulasildi = False
              self.yenihedefdurcount = 0
              #*******|| Kalkış yap / İniş yap ||********

              #*******|| Acil Durum ||********
              self.acildurumdogrulandi = False
              self.hastane_dur_count = 0
              self.hastane_distance = 9999
              #*******|| Acil Durum ||********

              #*******|| Motor Arızası ||********
              self.motorasagigit = False
              self.motorarizasidogrulandi = False
              self.motor_dur_count = 0
              #*******|| Motor Arızası ||********

              #*******|| GNSS Arızası ||********
              self.gnss_dur = 0

              self.gnss_userhata = self.gnss.hata
              #*******|| GNSS Arızası ||********

              #*******|| Rota Hesabı ||********
              self.rota = []
              self.rota_count = 0
              self.arac_x, self.arac_y = self.filtered_gnss_enlem, self.filtered_gnss_boylam
              self.durcount = 0 
              #*******|| Rota Hesabı ||********

              self.RotayiYenidenHesapla()

              return
            #*******|| Hedef Değişti mi? / Başlangıca Dönülsün mü? ||********
          
          #*******|| Acil Durum ||********
          if self.acil_durum and not self.acildurumdogrulandi:
              if self.hastane_dur_count < 10: 
                  self.dur() 
                  self.hastane_dur_count += 1 
                  return 
              else: 
                  self.acildurumdogrulandi = True
                  self.hedef_bolge.enlem, self.hedef_bolge.boylam, yukselti = self.EnYakinHastaneyiBul()

                  # Rota
                  self.rota = []
                  self.rota_count = 0
                  self.arac_x, self.arac_y = self.filtered_gnss_enlem, self.filtered_gnss_boylam
                  self.durcount = 0

                  # Kalkış Yap / Hedefe Ulaşıldı
                  self.hedefe_ulasildi = False
                  self.hedef_enlemboylam_ulasildi =False
                  self.kalkis_yap = False
                  self.yukseklige_ulasildi = False

                  self.RotayiYenidenHesapla()

                  return
          #*******|| Acil Durum ||********

          #*******|| Motor Arızası ||********
          if 0 in self.motor.rpm: # MOTOR BOZULDU MU
              self.motorarizasivar = True

              if self.motor_dur_count < 5: 
                  self.dur()
                  self.motor_dur_count += 1
                  return
              elif self.motor_dur_count == 5:
                  # EN YAKIN BOLGEYI BUL
                  inilebilir_bolgeler = []
                  inilebilir_bolgeler = self.EnYakinInilebilirBolgeyiBul(self.filtered_gnss_enlem, self.filtered_gnss_boylam) # (x, y) 1ms
                  distance1 = 9999
                  inis_bolgesi = []

                  for bolge in inilebilir_bolgeler:
                      distance = math.sqrt((bolge.enlem-self.filtered_gnss_enlem)**2+(bolge.boylam-self.filtered_gnss_boylam)**2)
                      if distance < distance1:
                          distance1 = distance
                          inis_bolgesi = bolge 

                  self.hedef_bolge.enlem = inis_bolgesi.enlem
                  self.hedef_bolge.boylam = inis_bolgesi.boylam
                  self.motor_dur_count += 1
                  return 
              else:
                  mesafex, mesafey = self.hedef_bolge.enlem - self.filtered_gnss_enlem, self.hedef_bolge.boylam - self.filtered_gnss_boylam
                  if abs(mesafey) < 5 and abs(mesafex) < 5 or self.gnssmotorhata: 
                      if self.gnss_userhata:
                          self.gnssmotorhata = True
                      else:
                          self.gnssmotorhata = False
                      self.HedefeinisYap()
                      return
                  else:
                      if self.motor_dur_count == 6:
                          self.dur()
                          self.motor_dur_count += 1
                          return
                      else:
                          if self.gnss_userhata:
                              #self.ileri_git(HIZLI)
                              self.HedefeDon(self.hedef_bolge.enlem, self.hedef_bolge.boylam, self.filtered_gnss_enlem, self.filtered_gnss_boylam)
                          else:
                              self.HedefeDon(self.hedef_bolge.enlem, self.hedef_bolge.boylam, self.filtered_gnss_enlem, self.filtered_gnss_boylam)
                          return
          #*******|| Motor Arızası ||********

          #**|| Hedef Bölgesine git ||**
          if self.rota[self.rota_count] == self.rota[-1]:
              hedefx, hedefy = self.hedef_bolge.enlem, self.hedef_bolge.boylam
              mesafe_x, mesafe_y = hedefx - self.filtered_gnss_enlem, hedefy - self.filtered_gnss_boylam
              if self.gnss_userhata:
                  katsayideger = 10 
                  test1 = False
              elif self.manyetometre.hata:
                  katsayideger = 4.5
                  test1 = False
              else:  
                  katsayideger = 4.5
                  test1 = True  

              if abs(mesafe_y) < katsayideger and abs(mesafe_x) < katsayideger:
                  #print("Hedef bolge ulasildi", self.hedef_bolge.enlem, self.hedef_bolge.boylam, self.hedef_amac)
                  self.test2 = True

                  if self.hedef_amac == 0: 
                      self.hedef_enlemboylam_ulasildi = True
                      if self.gnss_userhata: 
                          self.gnsshatasidogrulandi = True
                          return
                      else:
                          self.HedefeinisYap()
                          if self.lidar.mesafe>15 and not self.lidar.hata:
                              self.HedefeDon(hedefx, hedefy, self.filtered_gnss_enlem, self.filtered_gnss_boylam)
                          elif self.radar.mesafe>15 and not self.radar.hata:
                              self.HedefeDon(hedefx, hedefy, self.filtered_gnss_enlem, self.filtered_gnss_boylam)
                  elif self.hedef_amac == 1:
                      if self.yenihedefdurcount < 10: 
                          self.dur()
                          self.yenihedefdurcount += 1  
                          return
                      else:
                          self.hedef_enlemboylam_ulasildi = True
                          self.yenihedefdurcount = 0
                          self.hedefrotasicount += 1
                          if hasattr(self.hedefrotasi[self.hedefrotasicount], 'bolge'):
                              self.hedef = self.hedefrotasi[self.hedefrotasicount]
                              self.hedef_bolge = self.hedefrotasi[self.hedefrotasicount].bolge
                          else:
                              if len(self.hedefrotasi) <= (self.hedefrotasicount + 1):
                                  if self.baslangica_don: 
                                      #print("test1")
                                      self.hedef_amac = 0 
                                      self.hedef_bolge = self.hedefrotasi[self.hedefrotasicount]
                                      #self.hedef_amac = self.hedef_amaclar[self.hedefrotasicount]
                                  else:  
                                      #print('test2')
                                      pass
                              
                              else:  
                                  #print('test3') # Hata burada
                                  # self.hedef_amac = 2 # suan gerek yok 8 mart 2025 cemre
                                  self.hedef_bolge = self.hedefrotasi[self.hedefrotasicount]
                                  self.hedef_amac = self.hedef_amaclar[self.hedefrotasicount]
                                
                          # Rota
                          self.rota = []
                          self.rota_count = 0
                          self.arac_x, self.arac_y = self.filtered_gnss_enlem, self.filtered_gnss_boylam
                          self.durcount = 0

                          # Kalkış Yap / Hedefe Ulaşıldı
                          self.hedefe_ulasildi = False
                          self.hedef_enlemboylam_ulasildi =False
                          self.kalkis_yap = False
                          self.yukseklige_ulasildi = False
                          self.RotayiYenidenHesapla()

                          return
                  elif self.hedef_amac == 2:
                      #print("HELLO")
                      self.hedef_enlemboylam_ulasildi = False
                      self.SarjIstasyonunainisYap()
                      return             
                  elif self.hedef_amac == 3: # Kargo bolgesi (baslangica don calismiyor o yuzden baslangica don false olsa bile baslangica donecek)
                      self.hedef_enlemboylam_ulasildi_kargo = True
                      return
                      
                      
                      #print("KARGO Konumuna gelindi")
                      if self.kargo_durumu: # Sadece bir kargo icin calisir
                          if not self.kargoteslimedildimi:
                              self.dur()
                              self.kargoteslimedildimi = True
                              self.teslim_et()
                              #print("Kargo ulaşıldı")
                                                      
                          return
                      
                      else: # Siradaki hedefe bak. 
                          self.hedef_enlemboylam_ulasildi = True
                          self.kargoteslimedildimi = False
                          if hasattr(self.hedefrotasi[self.hedefrotasicount], 'bolge'): # Buraya hic gelmiyor die dokunmuoz suanlik Cemre 11 mart
                              self.hedef = self.hedefrotasi[self.hedefrotasicount]
                              self.hedef_bolge = self.hedefrotasi[self.hedefrotasicount].bolge
                          else:
                              if self.hedef_bolge == self.hedefrotasi[-1]: # Kargoyu bıraktık ve son hedef buydu baslangica geri dön
                                  self.hedef_amac = 0
                                  self.hedef_bolge = self.baslangic_bolgesi

                              elif len(self.hedefrotasi) <= (self.hedefrotasicount + 1):
                                  if self.baslangica_don: 
                                      #print("test1")
                                      self.hedef_amac = 0 
                                      self.hedef_bolge = self.hedefrotasi[self.hedefrotasicount]
                                      #self.hedef_amac = self.hedef_amaclar[self.hedefrotasicount]
                                  else:  
                                      #print('test2')
                                      pass
                              else:  
                                  #print('test3') # Hata burada
                                  # self.hedef_amac = 2 # suan gerek yok 8 mart 2025 cemre
                                  self.hedef_bolge = self.hedefrotasi[self.hedefrotasicount]
                                  self.hedef_amac = self.hedef_amaclar[self.hedefrotasicount]
                                
                          # Rota
                          self.rota = []
                          self.rota_count = 0
                          self.arac_x, self.arac_y = self.filtered_gnss_enlem, self.filtered_gnss_boylam
                          self.durcount = 0

                          # Kalkış Yap / Hedefe Ulaşıldı
                          self.hedefe_ulasildi = False
                          self.hedef_enlemboylam_ulasildi =False
                          self.kalkis_yap = False
                          self.yukseklige_ulasildi = False
                          self.RotayiYenidenHesapla()

                          return
                      
                      

                  #print("Siradaki hedef", self.hedef_bolge.enlem, self.hedef_bolge.boylam)
                  
                  
              
              elif abs(mesafe_y) < katsayideger+20 and abs(mesafe_x) < katsayideger+20 and test1 and self.test2: 
                  self.dur()
                  self.test2 = False

              elif abs(mesafe_y) < katsayideger+27 and abs(mesafe_x) < katsayideger+27 and self.hedef_bolge.yukselti>250 and self.test2: 
                  self.dur()
                  self.uzunbinadogrulandi = True
                  self.test2 = False
                  return
              
              else:
                  if self.gnss_userhata and False:
                      self.ileri_git(HIZLI)
                  else:
                      self.HedefeDon(hedefx, hedefy, self.filtered_gnss_enlem, self.filtered_gnss_boylam)
          #**|| Hedef Bölgesine git ||**
          #**|| Way Pointe git ||**
          else:
              hedefx, hedefy = self.rota[self.rota_count][0], self.rota[self.rota_count][1]

              mesafe_x, mesafe_y = hedefx - self.filtered_gnss_enlem, hedefy - self.filtered_gnss_boylam

              if abs(mesafe_y) < 15 and abs(mesafe_x) < 15: 

                  #*| Ne kadar duracağını belirle |*
                  if self.rota[self.rota_count+1][2]:  
                      durcount1 = 5 
                  elif self.rota[self.rota_count+1][3]:
                      durcount1 = 50
                  elif self.rota[self.rota_count+1][4]:
                      durcount1 = 50
                  elif self.rota[self.rota_count+1] == self.rota[-1]:
                      durcount1 = 1
                  else:
                      durcount1 = 0
                      aci = math.atan2(self.hedef_bolge.boylam - self.filtered_gnss_boylam, self.hedef_bolge.enlem - self.filtered_gnss_enlem)
                      aci_farki = aci - self.filtered_manyetometre
                      aci_farki = (aci_farki + math.pi) % (2 * math.pi) - math.pi
                      
                      if abs(aci_farki) > 0.05:
                          durcount1 = 1
                      else:
                          durcount1 = 0

                  if self.durcount < durcount1:
                      self.dur()
                      self.durcount += 1
                      return
                  else:
                      self.durcount = 0
                      self.rota_count += 1
                      return
              else:
                  if self.gnss_userhata and False:
                      self.ileri_git(HIZLI)
                  else:
                      self.HedefeDon(hedefx, hedefy, self.filtered_gnss_enlem, self.filtered_gnss_boylam)
          #**|| Way Pointe git ||**
  
  # Kargoya İniş yapar ve kargoyu birakir
  def kargoyainisyap(self, gnsshata=False):
      self.dur()
      bolge = self.harita.bolge(self.filtered_gnss_enlem, self.filtered_gnss_boylam)
      if bolge.inilebilir or gnsshata or bolge.inis_bolgesi or True: # bolge inilebilir vs. calismadigi icin suanlik bu 2. kontrol yapilmayacak
          if self.lidar.hata:
              if self.radar.hata:
                  self.asagi_git(YAVAS)
              else:  
                  if self.radar.mesafe <= 5:
                      self.hedefe_ulasildi = True
                      return True
                  elif self.radar.mesafe <= 15:
                      self.asagi_git(YAVAS)
                      return False
                  else:
                      self.asagi_git(HIZLI)
                      return False
              
          else:
              if self.lidar.mesafe <= 5:
                  self.teslim_et()
                  self.hedefe_ulasildi = True
                  return True
              elif self.lidar.mesafe <= 15:
                  self.asagi_git(YAVAS)
                  return False
              else:
                  self.asagi_git(HIZLI)
                  return False
          
      else:
          self.ileri_git(YAVAS) # EKSIK: Hedefe don sonra yavasca ileri git.
          return False
      
  # Verilen 2 bölge arasını istenilen parçaya bölüp engel var mı yok mu bilgisini saklar
  def AradaEngelVarmi(self, bolge1, bolge2, segment_length=1):
      arac_x, arac_y = bolge1[0], bolge1[1]
      hedefenlem, hedefboylam = bolge2[0], bolge2[1]
      angle = 0

      total_distance = math.sqrt((hedefenlem - arac_x) ** 2 + (hedefboylam - arac_y) ** 2)
  
      # Determine the number of segments
      num_segments = int(total_distance // segment_length)
      
      # Calculate the direction vector
      direction_x = (hedefenlem - arac_x) / total_distance
      direction_y = (hedefboylam - arac_y) / total_distance

      waypoints = []
      for i in range(num_segments + 1):
          new_x = arac_x + i * segment_length * direction_x
          new_y = arac_y + i * segment_length * direction_y
          waypoints.append((new_x, new_y))
      
      # Add the target point to ensure it is included as the final waypoint
      waypoints.append((hedefenlem, hedefboylam))

      for wp in waypoints:
          bolge = self.harita.bolge(wp[0], wp[1])
          bolge1 = self.harita.bolge(wp[0]+2.5, wp[1]+2.5)
          bolge2 = self.harita.bolge(wp[0]-2.5, wp[1]-2.5)
          bolge3 = self.harita.bolge(wp[0]+2.5, wp[1]-2.5)
          bolge4 = self.harita.bolge(wp[0]-2.5, wp[1]+2.5)

          if bolge.yukselti > self.engelsiniri: # Engel Var mı?
              return True

          elif bolge.ruzgar or bolge1.ruzgar or bolge2.ruzgar or bolge3.ruzgar or bolge4.ruzgar: 
              return True

          elif bolge.ucusa_yasakli_bolge or bolge1.ucusa_yasakli_bolge or bolge2.ucusa_yasakli_bolge or bolge3.ucusa_yasakli_bolge or bolge4.ucusa_yasakli_bolge:
              return True

          elif bolge.yavas_bolge or bolge1.yavas_bolge or bolge2.yavas_bolge or bolge3.yavas_bolge or bolge4.yavas_bolge:
              return True

          else:
              pass 

      return False

  # Başlangıca Döner
  def BaslangicaDon(self):
      return self.baslangic_bolgesi
  
  # Engeli geçmek için en yakın alternatif yola olan açıyı verir
  def EngelGec(self, aracx, aracy, angle_radyan, ngl = 181, senaryo = ''):
      orjinal_angle = math.degrees(angle_radyan)
      if orjinal_angle > 180:
          orjinal_angle -= 360
      elif orjinal_angle < -180:
          orjinal_angle += 360
      orjinal_angle = round(orjinal_angle)

      blok_boyutu = 20
      if senaryo == '':
          angle_katsayisi = 30
      elif senaryo == 'RUZGARLIBOLGE':
          angle_katsayisi = 75
      elif senaryo == 'YASAKLIBOLGE':
          angle_katsayisi = 75
      elif senaryo == 'YAVASBOLGE':
          angle_katsayisi = 30

      angle_katsayisi_siniri = ngl

      alternatif_yol = False
      
      # Alternatif yolları bul
      for angle_offset in range(angle_katsayisi, angle_katsayisi_siniri, angle_katsayisi):
          for sign in [1, -1]:  # 2 Tarafıda kontrol et: left (-1) and right (+1)
              test_angle = orjinal_angle + sign * angle_offset
      
              # Açı (-180,180) arasında olması lazım
              if test_angle > 180:
                  test_angle -= 360
              elif test_angle < -180:
                  test_angle += 360
              
              # Eğer yol temiz ise oradan git
              if senaryo == '':
                  # Yeni konumu hesapla
                  new_x, new_y = self.EngelTespit(aracx, aracy, test_angle, 25, False)
                  test_x, test_y = self.EngelTespit(aracx, aracy, test_angle, 20, False)
                  test2_x, test2_y = self.EngelTespit(aracx, aracy, test_angle, 10, False)
                  test3_x, test3_y = self.EngelTespit(aracx, aracy, test_angle, 5, False)
                  if not self.harita.bolge(new_x, new_y).ruzgar and not self.harita.bolge(new_x, new_y).ucusa_yasakli_bolge:
                      if self.harita.bolge(new_x, new_y).yukselti < self.engelsiniri and self.harita.bolge(test_x, test_y).yukselti < self.engelsiniri and self.harita.bolge(test2_x, test2_y).yukselti < self.engelsiniri and self.harita.bolge(test3_x, test3_y).yukselti < self.engelsiniri:
                          alternatif_yol = True
                          break
                  
              elif senaryo == 'RUZGARLIBOLGE':
                  # Yeni konumu hesapla
                  new_x, new_y = self.EngelTespit(aracx, aracy, test_angle, 30, False)
                  test_x, test_y = self.EngelTespit(aracx, aracy, test_angle, 25, False)
                  test2_x, test2_y = self.EngelTespit(aracx, aracy, test_angle, 20, False)
                  test3_x, test3_y = self.EngelTespit(aracx, aracy, test_angle, 10, False)
                  test4_x, test4_y = self.EngelTespit(aracx, aracy, test_angle, 5, False)
                  if self.harita.bolge(new_x, new_y).yukselti < self.engelsiniri and not self.harita.bolge(new_x, new_y).ucusa_yasakli_bolge:
                      if not self.harita.bolge(new_x, new_y).ruzgar and not self.harita.bolge(test_x, test_y).ruzgar and not self.harita.bolge(test2_x, test2_y).ruzgar and not self.harita.bolge(test3_x, test3_y).ruzgar and not self.harita.bolge(test4_x, test4_y).ruzgar:
                          alternatif_yol = True
                          break
                  
              elif senaryo == 'YASAKLIBOLGE':
                  new_x, new_y = self.EngelTespit(aracx, aracy, test_angle, 30, False)
                  test_x, test_y = self.EngelTespit(aracx, aracy, test_angle, 25, False)
                  test2_x, test2_y = self.EngelTespit(aracx, aracy, test_angle, 20, False)
                  test3_x, test3_y = self.EngelTespit(aracx, aracy, test_angle, 10, False)
                  test4_x, test4_y = self.EngelTespit(aracx, aracy, test_angle, 5, False)
                  if not self.harita.bolge(new_x, new_y).ruzgar and self.harita.bolge(new_x, new_y).yukselti < self.engelsiniri:
                      if not self.harita.bolge(new_x, new_y).ucusa_yasakli_bolge and \
                      not self.harita.bolge(test4_x, test4_y).ucusa_yasakli_bolge and \
                      not self.harita.bolge(test3_x, test3_y).ucusa_yasakli_bolge and \
                      not self.harita.bolge(test2_x, test2_y).ucusa_yasakli_bolge and \
                      not self.harita.bolge(test_x, test_y).ucusa_yasakli_bolge:
                          alternatif_yol = True
                          break
                          alternatif_yol = True
                          break

              elif senaryo == 'YAVASBOLGE':
                  if not self.harita.bolge(new_x, new_y).ruzgar and not self.harita.bolge(new_x, new_y).ucusa_yasakli_bolge and self.harita.bolge(new_x, new_y).yukselti < self.engelsiniri:
                      if not self.harita.bolge(new_x, new_y).yavas_bolge and not self.harita.bolge(test_x, test_y).yavas_bolge and not self.harita.bolge(test2_x, test2_y).yavas_bolge:
                          alternatif_yol = True
                          break
                  
          if alternatif_yol:
              break
      
      if alternatif_yol: # Alternatif yol var ise
          # Cezeriyi o açıya döndür ve düz git
          current_angle = test_angle
          return new_x, new_y
      else:
          return 0,0

  # 20m ötedeki alanın irtifasını ölçerek engel olup olmadığını 2. kez doğrular
  def EngelTespit(self, Ax, Ay, angle_ra, blokboyutu = 20, radianorangle = True):
      # Açıyı Derece Cinsinden Bul
      if radianorangle:
          angle = math.degrees(angle_ra) # [-180,180]
      else:
          angle = angle_ra 
      
      if angle > 180: # [-180, 180]
          angle -= 360
      elif angle < -180:
          angle += 360
      angle_round = round(angle) 

      blok_boyutu = blokboyutu # 20 metre

      if angle_round == 0:
          new_Ax = Ax + blok_boyutu
          new_Ay = Ay
      elif angle_round == 45:
          new_Ax = Ax + blok_boyutu / math.sqrt(2)
          new_Ay = Ay + blok_boyutu / math.sqrt(2)
      elif angle_round == 90:
          new_Ax = Ax
          new_Ay = Ay + blok_boyutu
      elif angle_round == 135:
          new_Ax = Ax - blok_boyutu / math.sqrt(2)
          new_Ay = Ay + blok_boyutu / math.sqrt(2)
      elif abs(angle_round) == 180:
          new_Ax = Ax - blok_boyutu
          new_Ay = Ay
      elif angle_round == -135:
          new_Ax = Ax - blok_boyutu / math.sqrt(2)
          new_Ay = Ay - blok_boyutu / math.sqrt(2)
      elif angle_round == -90:
          new_Ax = Ax
          new_Ay = Ay - blok_boyutu
      elif angle_round == -45:
          new_Ax = Ax + blok_boyutu / math.sqrt(2)
          new_Ay = Ay - blok_boyutu / math.sqrt(2)
      else:
          radian_angle = math.radians(angle)
          new_Ax = Ax + blok_boyutu * math.cos(radian_angle)
          new_Ay = Ay + blok_boyutu * math.sin(radian_angle)

      return new_Ax, new_Ay

  # En Yakın hastaneyi bulur
  def EnYakinHastaneyiBul(self):
      yeniHedefx = 0
      yeniHedefy = 0
      yeniHedefz = 0
      
      for hastane in self.harita.hastaneler:
          distance1 = math.sqrt((hastane.enlem-self.filtered_gnss_enlem)**2 + (hastane.boylam-self.filtered_gnss_boylam)**2)
          if distance1 < self.hastane_distance:
              self.hastane_distance = distance1
              yeniHedefx = hastane.enlem
              yeniHedefy = hastane.boylam
              yeniHedefz = hastane.yukselti

      self.hastane_distance = 9999
      return yeniHedefx, yeniHedefy, yeniHedefz
  
  # En Yakın iniş bölgesini bulur
  def EnYakinInisBolgesiniBul(self):
      yeniHedefx = 0
      yeniHedefy = 0
      yeniHedefz = 0
      
      for inisbolgesi in self.harita.inis_bolgeleri:
          distance1 = math.sqrt((inisbolgesi.enlem-filtered_gnss_enlem)**2 + (inisbolgesi.boylam-self.filtered_gnss_boylam)**2)
          if distance1 < self.hastane_distance:
              self.hastane_distance = distance1
              yeniHedefx = inisbolgesi.enlem
              yeniHedefy = inisbolgesi.boylam
              yeniHedefz = inisbolgesi.yukselti

      self.inisbolgesi_distance = 9999
      return yeniHedefx, yeniHedefy, yeniHedefz

  # En Yakın iniş bölgesini bulur
  def EnYakinInilebilirBolgeyiBul(self, x, y):
      inilebilirbolgeler = []
      blokboyutu1 = 0
      bolge = self.harita.bolge(x, y)
      if bolge.inilebilir:
          inilebilirbolgeler.append(bolge)
          return inilebilirbolgeler
      for _ in range(100):
          blokboyutu1 += 20
          for angle in range(-180, 180, 10):
              bolge_x, bolge_y = self.EngelTespit(x, y, angle, blokboyutu=blokboyutu1, radianorangle=False) # 20m sonranin x ve y sini verir
              bolge = self.harita.bolge(bolge_x, bolge_y)
              if bolge.inilebilir:
                  inilebilirbolgeler.append(bolge)
          if len(inilebilirbolgeler) > 0:
              break
      return inilebilirbolgeler  

  # Verilen Hedefe Döner ve Düz Gider
  def HedefeDon(self, hedef_x, hedef_y, arac_x, arac_y, duzgit=True): 
      hizkatsayisi = 1.5
      aci = math.atan2(hedef_y - arac_y, hedef_x - arac_x)
      DEAD_ZONE = 0.1
              
      if self.manyetometre.hata:
          gecicideger = self.FilterData(100, acisalhiz=True)

          current_time = self.zaman()
          dt = current_time - self.onceki_zaman_manyetometre
          self.onceki_zaman_manyetometre = current_time
          
          # Apply damping to reduce the effect of sudden large changes
          self.manyetometre_user_data -= gecicideger * dt
          self.filtered_manyetometre = self.manyetometre_user_data
          
          aci_farki = aci - self.manyetometre_user_data
          
          magnitude = 0.02
          hizkatsayisi = 0.2
      else:
          if self.filtered_manyetometre > math.pi - 0.3:  # Adjust the threshold as necessary
              self.filtered_manyetometre -= 2 * math.pi
          elif self.filtered_manyetometre < -math.pi + 0.3:
              self.filtered_manyetometre += 2 * math.pi
              
          self.manyetometre_user_data = self.filtered_manyetometre
          aci_farki = aci - self.filtered_manyetometre
          self.onceki_zaman_manyetometre = self.zaman() 

          if self.motorarizasivar and self.gnss_userhata:
              magnitude = 0.05
              hizkatsayisi = 1 
          elif self.gnss_userhata:
              magnitude = 0.005
          else:
              magnitude = 0.01
              if self.hedef_enlemboylam_ulasildi:
                  magnitude = 0.008
                  hizkatsayisi = 0.75

      aci_farki = (aci_farki + math.pi) % (2 * math.pi) - math.pi

      if abs(aci_farki) < magnitude: 
          if duzgit:
              newx, newy = self.EngelTespit(self.filtered_gnss_enlem, self.filtered_gnss_boylam, self.filtered_manyetometre)
              if self.harita.bolge(newx, newy).yavas_bolge or self.harita.bolge(self.filtered_gnss_enlem, self.filtered_gnss_boylam).yavas_bolge:
                  self.ileri_git(YAVAS)
              else:
                  self.ileri_git(HIZLI)
          else:
              pass
      else:
          if self.manyetometre.hata:
              self.don(aci_farki)
          else: 
              if self.gnss_userhata:
                  if aci_farki>0.05:
                      self.dur()
                  self.don(aci_farki * hizkatsayisi)
              else:
                  self.don(aci_farki * hizkatsayisi)
    
  # İniş yapar
  def HedefeinisYap(self, gnsshata=False):
      self.dur()
      bolge = self.harita.bolge(self.filtered_gnss_enlem, self.filtered_gnss_boylam)
      #print("--------------")
      #print(bolge.inilebilir, self.lidar.hata)
      if bolge.inilebilir or gnsshata or bolge.inis_bolgesi or True: # bolge inilebilir vs. calismadigi icin suanlik bu 2. kontrol yapilmayacak
          if self.lidar.hata:
              if self.radar.hata:
                  self.asagi_git(YAVAS)
              else:  
                  if self.radar.mesafe <= 5:
                      self.hedefe_ulasildi = True
                      return True
                  elif self.radar.mesafe <= 15:
                      self.asagi_git(YAVAS)
                      return False
                  else:
                      self.asagi_git(HIZLI)
                      return False
              
          else:
              if self.lidar.mesafe <= 5:
                  self.hedefe_ulasildi = True
                  return True
              elif self.lidar.mesafe <= 15:
                  self.asagi_git(YAVAS)
                  return False
              else:
                  self.asagi_git(HIZLI)
                  return False
          
      else:
          self.ileri_git(YAVAS) # EKSIK: Hedefe don sonra yavasca ileri git.
          return False
      
  # Şarj bölgesine iniş yapar sonra kalkar
  def SarjIstasyonunainisYap(self, gnsshata=False):
      self.dur()
      bolge = self.harita.bolge(self.filtered_gnss_enlem, self.filtered_gnss_boylam)
      if bolge.inilebilir or gnsshata:
          if self.lidar.hata:
              if self.radar.hata:
                  self.asagi_git(YAVAS)
              else:
                  if self.radar.mesafe <= 2:
                      self.sarj_istasyonuna_ulasildi = True
                      return True
                  elif self.radar.mesafe <= 15:
                      self.asagi_git(YAVAS)
                      return False
                  else:
                      self.asagi_git(HIZLI)
                      return False
              
          else:
              if self.lidar.mesafe <= 2:
                  self.sarj_istasyonuna_ulasildi = True
                  return True
              elif self.lidar.mesafe <= 15:
                  self.asagi_git(YAVAS)
                  return False
              else:
                  self.asagi_git(HIZLI)
                  return False
          
      else:
          #print("HELLO TEST #")
          self.ileri_git(YAVAS) # EKSIK: Hedefe don sonra yavasca ileri git.
          return False
    
  # Gidilecek hedefleri sıralar: Hedefler sırasız iseler en uygun mesafeye göre sıralar
  def HedefSirasiniBelirle(self):
      sira = [None] * len(self.harita.teslimat_bolgeleri)
      self.siralimi = False

      for hedef in self.harita.teslimat_bolgeleri:
          hedef.amac = 1
          self.hedef_amaclar.append(3)
          #if hedef.sira == -1:
            #  sira.append(hedef)
          #elif hedef.sira == 0:
              # sira.insert(0, hedef)
              # self.siralimi = False
          #else:
              # sira[hedef.sira-1] = hedef
          sira.append(hedef)
      
      return [i for i in sira if i is not None]

  def HedefSirasiniDuzenle(self, sira):
      if not self.siralimi and len(sira)>2:
          best_order = None
          best_distance = 9999  

          sira.insert(0, self.baslangic_bolgesi)
          middle_part = sira[1:-1] 

          for perm in itertools.permutations(middle_part):
              total_distance = self.distance(sira[0], perm[0])  # From start to the first permuted element
              for i in range(1, len(perm)):
                  total_distance += self.distance(perm[i-1], perm[i])
              total_distance += self.distance(perm[-1], sira[-1])  # From the last permuted element to the end
              
              # Check if this is the shortest path found
              if total_distance < best_distance:  
                  best_distance = total_distance
                  best_order = perm

          # Rebuild the sira list with the best middle order
          sira = [sira[0]] + list(best_order) + [sira[-1]]
      else: 
          sira.insert(0, self.baslangic_bolgesi)

      if self.baslangica_don:
          sira.append(self.baslangic_bolgesi)
          self.hedef_amaclar.append(0)

      sira = self.ensure_battery_capacity(sira) 

      del sira[0]

      seen = set()
      new_sira = []
      for hedef in sira:
          if hasattr(hedef, 'bolge'):
              enlem_boylam = (hedef.bolge.enlem, hedef.bolge.boylam)
          else:
              enlem_boylam = (hedef.enlem, hedef.boylam)

          if enlem_boylam in seen:
              if hasattr(hedef, 'bolge'):
                  continue  # Skip adding this element, as we prefer the one without 'bolge'
              else:
                  # Remove the previously added item with 'bolge' attribute
                  new_sira = [h for h in new_sira if (
                      (h.bolge.enlem, h.bolge.boylam) if hasattr(h, 'bolge') else (h.enlem, h.boylam)
                  ) != enlem_boylam]
          else:
              seen.add(enlem_boylam)
              new_sira.append(hedef)
      
      sira = new_sira

      return sira
    
  # Batarya yetecek mi kontrol eder
  def ensure_battery_capacity(self, sira):
      kapat = 0
      total_distance = 0
      i = 0

      battery_levels = []

      while i < len(sira) - 1:
          current_distance = self.distance(sira[i], sira[i+1])
          total_distance += current_distance

          battery_levels.append(self.kalan_batarya)

          self.kalan_batarya -= current_distance /  self.birimbatarya  # 1 batarya  self.birimbatarya metre

          if self.kalan_batarya < 0:
              best_battery_station = None
              best_battery_station2 = []
              best_battery_distance = 9999
              self.kalan_batarya += current_distance /  self.birimbatarya
              backtrack_index = i
                
              for station in self.harita.sarj_istasyonlari:
                  if station == self.sonstation:
                      continue
                  distance_to_station = self.distance(sira[i], station)
                  distance_station_to_next = self.distance(station, sira[i+1])
                  
                  if (distance_station_to_next < current_distance) and (distance_to_station <= (self.kalan_batarya* self.birimbatarya)):
                      if len(best_battery_station2)>0:
                          if distance_station_to_next<best_battery_station2[-1]:
                              self.sonstation = station
                              best_battery_station = station
                              best_battery_distance = distance_to_station
                              best_battery_station2.append(distance_station_to_next)
                          else:
                              pass                         
                      else:
                          self.sonstation = station
                          best_battery_station = station
                          best_battery_distance = distance_to_station
                          best_battery_station2.append(distance_station_to_next)
                  else:
                      self.sonstation
              
              if best_battery_station:
                  sira.insert(i + 1, best_battery_station)
                  self.kalan_batarya = 79
                  self.eskibolgeistasyon = 0
                  self.eskibolgeistasyon2 = 0
              else:
                  best_battery_station = self.OncekiNoktadanStationBul(i-1, sira, current_distance, battery_levels[-2])
                  if best_battery_station:
                      sira.insert(i, best_battery_station)
                      self.kalan_batarya = 79
                      i -= 1
                  else:
                      kapat = True
                      break
          else:
              if hasattr(sira[i+1], 'bolge'):
                  self.sonstation = sira[i+1].bolge
              else:
                  self.sonstation = sira[i+1]
          
          if kapat>20:
              break
          i += 1
          kapat += 1

      return sira
  
  def OncekiNoktadanStationBul(self, index, sira, original_distance, battery):
      while index >= 0:
          for station in self.harita.sarj_istasyonlari:
              if station == self.eskibolgeistasyon or station == self.eskibolgeistasyon2:
                  continue
              distance_to_station = self.distance(sira[index], station)
              distance_station_to_next = self.distance(station, sira[index + 1])

              # Check if the station is feasible from the previous point
              if (distance_station_to_next < original_distance) and (distance_to_station <= (battery * self.birimbatarya)):
                  if hasattr(sira[index], 'bolge'):
                      self.eskibolgeistasyon = sira[index].bolge
                  else:
                      self.eskibolgeistasyon = sira[index]
                  self.eskibolgeistasyon2 = station
                  return station

          index -= 1

      return None

  # Distance verir 2 bolge arasindaki. Bolge olmasada olur.
  def distance(self, hedef1, hedef2):
      enlem1 = hedef1.enlem if hasattr(hedef1, 'enlem') else hedef1.bolge.enlem
      boylam1 = hedef1.boylam if hasattr(hedef1, 'boylam') else hedef1.bolge.boylam
      enlem2 = hedef2.enlem if hasattr(hedef2, 'enlem') else hedef2.bolge.enlem
      boylam2 = hedef2.boylam if hasattr(hedef2, 'boylam') else hedef2.bolge.boylam
      return math.sqrt((enlem2 - enlem1) ** 2 + (boylam2 - boylam1) ** 2)

  # INIT fonksiyonu    
  def RotayiYenidenHesapla(self):
      mesafe_x = self.hedef_bolge.enlem - self.arac_x
      mesafe_y = self.hedef_bolge.boylam - self.arac_y 
      if abs(mesafe_y) < 30 and abs(mesafe_x) < 30: 
          #print("Line 1213 Test")
          self.angle = math.atan2(self.hedef_bolge.boylam - self.arac_y, self.hedef_bolge.enlem - self.arac_x) # Hedefe olan açı (Radyan)
          new_x, new_y = self.EngelTespit(self.arac_x, self.arac_y, self.angle, blokboyutu=2)
          self.rota.append((new_x, new_y, False, False, False)) # Eğer sıradakı hedef çok yakınsa öylesine aradan boş bir konum girki hata vermesin
          self.arac_yukselti = self.hedef_bolge.yukselti
      else:
          for _ in range(1000):
              self.angle = math.atan2(self.hedef_bolge.boylam - self.arac_y, self.hedef_bolge.enlem - self.arac_x) # Hedefe olan açı (Radyan)
              new_x, new_y = self.EngelTespit(self.arac_x, self.arac_y, self.angle, blokboyutu=20)
              new_test_x, new_test_y = self.EngelTespit(self.arac_x, self.arac_y, self.angle, blokboyutu=15)
              new_test_x2, new_test_y2 = self.EngelTespit(self.arac_x, self.arac_y, self.angle, blokboyutu=10)
              new_test_x3, new_test_y3 = self.EngelTespit(self.arac_x, self.arac_y, self.angle, blokboyutu=5)
              engelvarmi = False
              ruzgarvarmi = False
              yasaklibolgevarmi = False
              bolge = self.harita.bolge(new_x, new_y)
              bolgetest = self.harita.bolge(new_test_x, new_test_y)
              bolgetest2 = self.harita.bolge(new_test_x2, new_test_y2)
              bolgetest3 = self.harita.bolge(new_test_x3, new_test_y3)

              if self.arac_yukselti > self.azami_yukseklik + 10:
                  #print("Test23452")
                  new_x, new_y = self.EngelTespit(self.arac_x, self.arac_y, self.angle, blokboyutu=45)
                  self.arac_x, self.arac_y = new_x, new_y
                  self.arac_yukselti = self.hedef_bolge.yukselti

              if bolgetest.yukselti > self.engelsiniri:
                  new_x, new_y = self.EngelGec(self.arac_x, self.arac_y, self.angle)
                  engelvarmi = True
              elif bolge.yukselti > self.engelsiniri or bolge.yavas_bolge:
                  new_x, new_y = self.EngelGec(self.arac_x, self.arac_y, self.angle)
                  engelvarmi = True  
              elif bolgetest.ruzgar or bolgetest2.ruzgar or bolgetest3.ruzgar: 
                  new_x, new_y = self.EngelGec(self.arac_x, self.arac_y, self.angle, senaryo = 'RUZGARLIBOLGE')
                  ruzgarvarmi = True 
              elif bolge.ruzgar:
                  new_x, new_y = self.EngelGec(self.arac_x, self.arac_y, self.angle, senaryo = 'RUZGARLIBOLGE')
                  ruzgarvarmi = True  
              elif bolge.ucusa_yasakli_bolge:
                  new_x, new_y = self.EngelGec(self.arac_x, self.arac_y, self.angle, senaryo = 'YASAKLIBOLGE')
                  yasaklibolgevarmi = True   
              elif bolgetest.ucusa_yasakli_bolge or bolgetest2.ucusa_yasakli_bolge or bolgetest3.ucusa_yasakli_bolge:
                  new_x, new_y = self.EngelGec(self.arac_x, self.arac_y, self.angle, senaryo = 'YASAKLIBOLGE')
                  yasaklibolgevarmi = True   
              elif bolge.yavas_bolge:
                  new_x, new_y = self.EngelGec(self.arac_x, self.arac_y, self.angle, senaryo = 'YAVASBOLGE')
                  yasaklibolgevarmi = True  
              elif bolgetest.yavas_bolge:
                  new_x, new_y = self.EngelGec(self.arac_x, self.arac_y, self.angle, senaryo = 'YAVASBOLGE')
                  yasaklibolgevarmi = True  
              
              mesafe_x = self.hedef_bolge.enlem - self.arac_x
              mesafe_y = self.hedef_bolge.boylam - self.arac_y 

              if abs(mesafe_y) < 30 and abs(mesafe_x) < 30: 
                  break
              elif self.hedef_bolge.yukselti > 100:
                  #print("KOTU DURUM BU KOD CALISMAMASI LAZIM")
                  if abs(mesafe_y) < 50 and abs(mesafe_x) < 50: 
                      break

              self.rota.append((new_x, new_y, engelvarmi, ruzgarvarmi, yasaklibolgevarmi)) # Enlem Boylam Engel
              self.arac_x, self.arac_y = new_x, new_y

          self.arac_yukselti = self.hedef_bolge.yukselti
          #print(self.rota)
          #print("+++++++++++")
          self.rota.insert(0, (self.filtered_gnss_enlem, self.filtered_gnss_boylam, False, False, False))
          #*******|| Rota Oluşturulması ||********
          #*******|| Rota Kısaltılması ||********
          index = 0 
          while index < len(self.rota) - 1: 
              last_no_obstacle_index = index 
              # Start from the next waypoint and try to find the farthest waypoint without obstacles
              for index2 in range(index + 1, len(self.rota)):
                  waypoint2 = self.rota[index2]

                  # Check if there is an obstacle between the current waypoint and the next
                  if self.AradaEngelVarmi(self.rota[index], waypoint2, segment_length=1):
                      break
                  elif self.AradaEngelVarmi(self.rota[index], waypoint2, segment_length=15):
                      break
                  elif self.AradaEngelVarmi(self.rota[index], waypoint2, segment_length=10):
                      break
                  elif self.AradaEngelVarmi(self.rota[index], waypoint2, segment_length=5):
                      break
                  elif self.AradaEngelVarmi(self.rota[index], waypoint2, segment_length=2):
                      break
                  #elif self.rota[index2][4] or self.rota[index][4] or self.rota[index2][3] or self.rota[index][3]:
                  # break
                  else:
                      # If no obstacle, set index2 as the new waypoint to compare from index
                      last_no_obstacle_index = index2

              # Delete waypoints between the current one and the last one without an obstacle
              if last_no_obstacle_index > index + 1:
                  del self.rota[index + 1:last_no_obstacle_index]
              
              index += 1

          del self.rota[0]

      #print(self.hedef_bolge)
      #print(self.baslangic_bolgesi)
      #print("------------")
      #print(self.rota)
          #*******|| Rota Kısaltılması ||********
    
  # Azami Yüksekliğe Yükselir
  def KalkisYap(self): 
      if self.motorarizasivar:
          pass
      #elif self.baslangica_don:
          # pass
      else:    
          hedefx, hedefy = self.rota[self.rota_count][0], self.rota[self.rota_count][1]
          self.HedefeDon(hedefx, hedefy, self.filtered_gnss_enlem, self.filtered_gnss_boylam, duzgit=False)
      if self.gnss_userhata:
          if self.barometre.irtifa >= (self.azami_yukseklik-6) and not self.kalkis_yap:
              self.yukseklige_ulasildi=True
              self.dur()
              self.kalkis_yap = True
              return True
          elif self.yukseklige_ulasildi == False: 
              self.yukari_git(HIZLI)
              return False
          else:  
              pass
      else:
          if self.gnss.irtifa >= (self.azami_yukseklik-4) and not self.kalkis_yap:
              self.yukseklige_ulasildi=True
              self.dur()
              self.kalkis_yap = True
              return True
          elif self.yukseklige_ulasildi == False and self.gnss.irtifa >= (self.azami_yukseklik-10):
              self.yukari_git(YAVAS)
          elif self.yukseklige_ulasildi == False:
              self.yukari_git(HIZLI)
              return False
          else:  
              pass

  def UzunBinayaKalkisYap(self):
      if self.barometre.hata:
          if self.gnss.irtifa < self.azami_yukseklik+45:
              self.yukari_git(HIZLI)
              return False
          else:
              return True
      else:
          if self.barometre.irtifa < self.azami_yukseklik+45:
              self.yukari_git(HIZLI)
              return False
          else:
              return True
  
  def UzunBinadanInisYap(self, barometre=False):
      self.dur()
      if barometre:
          if self.gnss.irtifa>118:
              self.asagi_git(HIZLI)
              return True
          else:
              self.uzunbinadaninis = False
              return False
      else:
          if self.barometre.irtifa>118:
              self.asagi_git(HIZLI)
              return True
          else:
              self.uzunbinadaninis = False
              return False
          
  # İstenilen değeri istenildiği kadar filtrelenir ve geri gönderilir
  def FilterData(self, katsayi, manyetometre=False, gnssenlem=False, gnssboylam=False, imux=False, imuy=False, imuz=False, acisalhiz=False, deviationimux=False, deviationimuz=False):
      if manyetometre:
          filtered_list = [self.manyetometre.veri for _ in range(katsayi)]
          return sum(filtered_list) / len(filtered_list)
      elif gnssenlem:
          filtered_list = [self.gnss.enlem for _ in range(katsayi)]
          return sum(filtered_list) / len(filtered_list)
      elif gnssboylam: 
          filtered_list = [self.gnss.boylam for _ in range(katsayi)]
          return sum(filtered_list) / len(filtered_list)
      elif imux:
          filtered_list = [self.imu.hiz.x for _ in range(katsayi)]
          if len(self.filteredimux_list)<4:
              self.filteredimux_list.append(sum(filtered_list) / len(filtered_list)) 
              return sum(filtered_list) / len(filtered_list) + self.standard_deviation_imu_x
          else:
              self.filteredimux_list.append(sum(filtered_list) / len(filtered_list))
              deneme = sum(self.filteredimux_list)/5.0
              self.filteredimux_list.pop(0)
              return deneme + self.standard_deviation_imu_x
      elif imuy:
          filtered_list = [self.imu.hiz.y for _ in range(katsayi)]
          if len(self.filteredimuy_list)<4:
              self.filteredimuy_list.append(sum(filtered_list) / len(filtered_list)) 
              return sum(filtered_list) / len(filtered_list)
          else:
              self.filteredimuy_list.append(sum(filtered_list) / len(filtered_list))
              deneme = sum(self.filteredimuy_list)/5.0
              self.filteredimuy_list.pop(0)
              return deneme
      elif imuz:
          filtered_list = [self.imu.hiz.z for _ in range(katsayi)]
          if len(self.filteredimuz_list)<4:
              self.filteredimuz_list.append(sum(filtered_list) / len(filtered_list)) 
              return sum(filtered_list) / len(filtered_list) + self.standard_deviation_imu_z
          else:
              self.filteredimuz_list.append(sum(filtered_list) / len(filtered_list))
              deneme = sum(self.filteredimuz_list)/5.0
              self.filteredimuz_list.pop(0)
              return deneme + self.standard_deviation_imu_z
      elif acisalhiz:
          filtered_list = [self.imu.acisal_hiz.y for _ in range(katsayi)]
          #if abs(sum(filtered_list) / len(filtered_list)) < 0.2:
              # return 0
          return (sum(filtered_list) / len(filtered_list))

      elif deviationimux:
          filtered_list = [(0 - self.FilterData(40, imux=True)) for _ in range(katsayi)]
          return (sum(filtered_list) / len(filtered_list))
      
      elif deviationimuz:
          filtered_list = [(0 - self.FilterData(40, imuz=True)) for _ in range(katsayi)]
          return (sum(filtered_list) / len(filtered_list))


class Ambulans(AmbulansParent):
    def __init__(self, id = 0):
        super().__init__(id = id, keyboard = False, sensor_mode = NORMAL)
        #print(self.gnss.irtifa)


    def run(self):
        super().run()
        print("Hello")
        #print(self.manyetometre.veri)

 
# Ana program
#itfaiye_1 = Itfaiye(id=1)
kargo_1 = Kargo(id=1) 
#ambulans_1 = Ambulans(id=1)
#cezeri_1 = Cezeri(id=1)

while robot.is_ok():
    #itfaiye_1.run()
    kargo_1.run() 
    #ambulans_1.run()
    #cezeri_1.run()
  