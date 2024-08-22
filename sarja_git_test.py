self.en_yakin_sarj_istasyonuna_git = False
hedef = self.harita.bolge(hedef_enlem, hedef_boylam)

def sarj_hesap (self,guncel_enlem,guncel_boylam,hedef_enlem,hedef_boylam) 
    print(self.batarya)
    #Tanımlar 
    uzaklik = math.sqrt((hedef_enlem-guncel_enlem)**2 + (hedef_boylam-guncel_boylam)**2) 
    uzaklik2_sarj = math.sqrt((hedef_enlem-sarj2_enlem)**2 + (hedef_boylam-sarj2_boylam)**2) 
    #hesaplanması gerekenler
    yakin_sarj = 7
    inis_sarj = (cezeri.yukselti - mutlak_hedef.yukselti) * 0.22 = #inis anında harcanacak maksimum şarj
    kalacak_sarj = self.batarya.veri - ((uzaklik-50)* 0.089) - yakin_sarj 
    if self.yasak == False:
        if uzaklik > 50: 
            if hedef.amac == INIS:
                if kalacak_sarj-inis_sarj < 25:
                    self.dur()
                    self.en_yakin_sarj_istasyonuna_git = True
                elif  kalacak_sarj -inis_sarj - (uzaklik2_sarj *0.089 ) < 30: 
                    self.dur()
                    self.en_yakin_sarj_istasyonuna_git = True
                else: 
                    pass
            else:
                if kalacak_sarj < 25:
                    self.dur()
                    en_yakin_sarj_istasyonuna_git = True
                elif  kalacak_sarj - (uzaklik2_sarj * 0.089) < 30: 
                    self.dur()
                    self.en_yakin_sarj_istasyonuna_git = True
                else :
                    pass
        else:
            print("AKTASAKTASAKTAKTAS")
    else: 
        print("KAPLAN")
    

def en_yakin_sarj_istasyonu(self, guncel_enlem, guncel_boylam, hedef_enlem, hedef_boylam, sarj_menzili ):
    #Gerekli şeyler 
    # ilk olarak şarjın yeteceği tüm istasyonlar bulunur
    #Hedef ve araca yakın olup rotayı en kısa yapacak şarj istasyonu bulunmalı
    sarj_enlem = #gerekli istasyonun enlemi 
    sarj_boylam = #gerekli istasyonun boylamı 
    uzaklik_sarj = math.sqrt((sarj_enlem-guncel_enlem)**2 + (sarj_boylam-guncel_boylam)**2) #gerekli istasyona olan uzaklik 
    # Şarjın yeteceği tüm şarj istasyonlarını bul
    sarj_menzili = ((self.batarya.veri - 40) - 7) / 0.089
    uygun_istasyonlar = []
   
    for istasyon in self.harita.sarj_istasyonlari:
        mesafe = math.sqrt((istasyon.enlem-guncel_enlem)**2 + (istasyon.boylam-guncel_boylam)**2)
        if mesafe <= sarj_menzili:
            uygun_istasyonlar.append(istasyon)
   
    # Hedef ve araca yakın olup rotayı en kısa yapacak şarj istasyonunu bul
    en_iyi_istasyon = None
    en_kisa_mesafe = float('inf')
   
    for istasyon in uygun_istasyonlar:
        # Hedefe olan mesafe + şarj istasyonuna olan mesafe
        toplam_mesafe = math.sqrt((istasyon.enlem-guncel_enlem)**2 + (istasyon.boylam-guncel_boylam)**2)
        toplam_mesafe += math.sqrt((hedef_enlem- istasyon.enlem)**2 + (hedef_boylam - istasyon.boylam)**2)
       
        if toplam_mesafe < en_kisa_mesafe:
            en_kisa_mesafe = toplam_mesafe
            en_iyi_istasyon = istasyon
   
    # Seçilen şarj istasyonunun enlem ve boylamını döndür
    if en_iyi_istasyon:
        self.sarj_enlem = en_iyi_istasyon.enlem
        self.sarj_boylam = en_iyi_istasyon.boylam
        return sarj_enlem, sarj_boylam
    else:
        return None, None

    uzakllik_sarj = math.sqrt((sarj_enlem_enlem-guncel_enlem)**2 + (sarj_boylam-guncel_boylam)**2)
    # Kullanım örneği
    sarj_enlem, sarj_boylam = en_yakin_sarj_istasyonu(hedef, guncel_ sarj_menzili, self.harita)


def hedefe_en_yakin_sarj_istasyonu(self, hedef_enlem, hedef_boylam, harita):
    # Hedefe en yakın şarj istasyonunu bul
    en_yakin_istasyon2 = None
    en_kisa_mesafe2 = float('inf')
    
    for istasyon2 in harita.sarj_istasyonlari:
        mesafe2 = math.sqrt((hedef_enlem- istasyon2.enlem)**2 + (hedef_boylam - istasyon2.boylam)**2)
        
        if mesafe2 < en_kisa_mesafe2:
            en_kisa_mesafe2 = mesafe2
            en_yakin_istasyon2 = istasyon2
    
    # Seçilen şarj istasyonunun enlem ve boylamını döndür
    if en_yakin_istasyon2:
        sarj2_enlem = en_yakin_istasyon2.enlem
        sarj2_boylam = en_yakin_istasyon2.boylam
        return sarj2_enlem, sarj2_boylam
    else:
        return None, None

    # Kullanım örneği
    sarj2_enlem, sarj2_boylam = hedefe_en_yakin_sarj_istasyonu(hedef, self.harita)



def en_yakin_yasak_istasyonu(self, guncel_enlem, guncel_boylam, sol_durak_enlem, sol_durak_boylam, sarj_menzili ):
    #Gerekli şeyler 
    # ilk olarak şarjın yeteceği tüm istasyonlar bulunur
    #Hedef ve araca yakın olup rotayı en kısa yapacak şarj istasyonu bulunmalı
    sarj3_enlem = #gerekli istasyonun enlemi 
    sarj3_boylam = #gerekli istasyonun boylamı 
    uzaklik3_sarj = math.sqrt((sarj_enlem-guncel_enlem)**2 + (sarj_boylam-guncel_boylam)**2) #gerekli istasyona olan uzaklik 
    # Şarjın yeteceği tüm şarj istasyonlarını bul
    sarj_menzili = ((self.batarya.veri - 40) - yavasgiderkenkiharcadığısarjsabiti) / 0.089
    uygun_istasyonlar = []
   
    for istasyon3 in self.harita.sarj_istasyonlari:
        mesafe = math.sqrt((istasyon.enlem-guncel_enlem)**2 + (istasyon.boylam-guncel_boylam)**2)
        if mesafe3 <= sarj_menzili:
            uygun_istasyonlar.append(istasyon)
   
    # Hedef ve araca yakın olup rotayı en kısa yapacak şarj istasyonunu bul
    en_iyi_istasyon3 = None
    en_kisa_mesafe3 = float('inf')
   
    for istasyon3 in uygun_istasyonlar:
        # Hedefe olan mesafe + şarj istasyonuna olan mesafe
        toplam_mesafe3 = math.sqrt((istasyon.enlem-guncel_enlem)**2 + (istasyon.boylam-guncel_boylam)**2)
        toplam_mesafe3 += math.sqrt((sol_durak_enlem- istasyon.enlem)**2 + (sol_durak_boylam - istasyon.boylam)**2)
       
        if toplam_mesafe3 < en_kisa_mesafe3:
            en_kisa_mesafe3 = toplam_mesafe3
            en_iyi_istasyon3 = istasyon3
   
    # Seçilen şarj istasyonunun enlem ve boylamını döndür
    if en_iyi_istasyon3:
        sarj3_enlem = en_iyi_istasyon3.enlem
        sarj3_boylam = en_iyi_istasyon3.boylam
        return sarj3_enlem, sarj3_boylam
    else:
        return None, None

    uzakllik3_sarj = math.sqrt((sarj3_enlem_enlem-guncel_enlem)**2 + (sarj3_boylam-guncel_boylam)**2)
    # Kullanım örneği
    sarj3_enlem, sarj3_boylam = en_yakin_yasak_istasyonu(hedef, guncel_ sarj_menzili, self.harita)



    def git(self,guncel_enlem,guncel_boylam,hedef_enlem,hedef_boylam):

        if self.acil == True:
            #print("knk acil bak")
            hedef_enlem = self.hastane_enlem
            hedef_boylam = self.hastane_boylam

         if self.en_yakin_sarj_istasyonuna_git == True:
            hedef_enlem = self.sarj_enlem
            hedef_boylam = self.sarj_boylam

        #print("hedef",hedef_enlem,hedef_boylam)

        self.rota_olustur()
        self.engel_kac(guncel_enlem,guncel_boylam,hedef_enlem,hedef_boylam)
        self.motor_ariza(guncel_enlem,guncel_boylam)
    
        if self.motor_hata == True or self.motor.hata == 1 :
            print("in")
            bolge = self.harita.bolge(guncel_enlem,guncel_boylam)
            if bolge.inilebilir :
                hedef_enlem = guncel_enlem
                hedef_boylam = guncel_boylam

        for i, hedef in enumerate(self.hedefler):
            if hedef_enlem == hedef.bolge.enlem and hedef_boylam == hedef.bolge.boylam:
                hedef = self.hedefler[i]
                break

        if self.yasak == False:

            if self.en_yakin_sarj_istasyonuna_git == False:
                uzaklik = math.sqrt((hedef_enlem-guncel_enlem)**2 + (hedef_boylam-guncel_boylam)**2)
                self.donus_tamamla(guncel_enlem,guncel_boylam,hedef_enlem,hedef_boylam)

                if uzaklik < 10:
                    if uzaklik < 5:
                        if hedef.amac == INIS:
                            self.dur()
                            self.asagi_git(YAVAS)

                        elif self.i == (len(self.en_kisa_rota) - 1):
                            self.dur()
                            self.asagi_git(YAVAS)

                        elif self.acil_durum:  
                            self.dur()
                            self.asagi_git(YAVAS)   

                        elif self.sarja_git == True:
                            self.dur()
                            self.asagi_git(YAVAS)

                        else:  
                            self.i +=1 

