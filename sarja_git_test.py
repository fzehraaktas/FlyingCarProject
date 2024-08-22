    def git(self,guncel_enlem,guncel_boylam,hedef_enlem,hedef_boylam):

        if self.acil == True:
            #print("knk acil bak")
            hedef_enlem = self.hastane_enlem
            hedef_boylam = self.hastane_boylam

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

            if self.sarj_git == False:
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

                        else:  
                            self.i +=1 

                    else: 
                        self.ileri_git(YAVAS)
                else:
                    self.ileri_git(HIZLI)
            else:
                #sarja_git

        else:

            #print("engel")
            self.engel_kac(guncel_enlem,guncel_boylam,hedef_enlem,hedef_boylam)
            uzaklik = math.sqrt((self.durak_enlem-guncel_enlem)**2 + (self.durak_boylam-guncel_boylam)**2)
            self.donus_tamamla(guncel_enlem,guncel_boylam,self.durak_enlem,self.durak_boylam)

            if uzaklik < 5:     
                self.yasak=False
            
            else: 
                self.ileri_git(HIZLI)
