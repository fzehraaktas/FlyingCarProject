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
                    self.sag_ok = True
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
                    self.sol_ok = True
                    break
                     
    def engel_kac (self,guncel_enlem,guncel_boylam,hedef_enlem,hedef_boylam):
        
        engel_bolge = []
        
        rota_enlem=(hedef_enlem-guncel_enlem)/200
        rota_boylam=(hedef_boylam-guncel_boylam)/200

        for i in range (200):
            guncel_enlem = guncel_enlem + rota_enlem
            guncel_boylam = guncel_boylam + rota_boylam
            bolge = self.harita.bolge(guncel_enlem, guncel_boylam)

            if bolge.ucusa_yasakli_bolge == True or bolge.ruzgar ==True or bolge.trafik == True or bolge.yukselti>=90 :
                #print("yasak")
                
                engel_bolge.append([guncel_enlem,guncel_boylam])
                engel_enlem=engel_bolge[0][0]
                engel_boylam=engel_bolge[0][1]

                self.sag_kontrol(guncel_enlem,guncel_boylam,hedef_enlem,hedef_boylam,engel_enlem,engel_boylam)
                self.sol_kontrol(guncel_enlem,guncel_boylam,hedef_enlem,hedef_boylam,engel_enlem,engel_boylam)

                if self.sag_ok == True and self.sol_ok == True:
                    k_sag = math.sqrt((self.sag_durak_enlem- round(guncel_enlem,1) )**2 + (self.sag_durak_boylam- round(guncel_boylam,1) )**2)
                    v_sag = math.sqrt((self.sag_durak_enlem-hedef_enlem)**2 + (self.sag_durak_boylam-hedef_boylam)**2)

                    k_sol = math.sqrt((self.sol_durak_enlem-round(guncel_enlem,1))**2 + (self.sol_durak_boylam-round(guncel_boylam,1) )**2)
                    v_sol = math.sqrt((self.sol_durak_enlem-hedef_enlem)**2 + (self.sol_durak_boylam-hedef_boylam)**2)

                    sag_uzaklik = k_sag + v_sag     
                    sol_uzaklik = k_sol + v_sol     

                    if abs(sol_uzaklik - sag_uzaklik)<=50 and sol_uzaklik > sag_uzaklik:
                        self.yasak=True
                        print("sol")
                        self.durak_enlem = self.sol_durak_enlem
                        self.durak_boylam = self.sol_durak_boylam
                     
                        
                    elif sol_uzaklik < sag_uzaklik:
                        print("sol")
                        self.durak_enlem = self.sol_durak_enlem
                        self.durak_boylam = self.sol_durak_boylam
                     
                    else:
                        print("sag")
                        self.durak_enlem = self.sag_durak_enlem
                        self.durak_boylam = self.sag_durak_boylam
                        

                elif self.sag_ok == False and self.sol_ok == True:
                    print("soll")
                    self.durak_enlem = self.sol_durak_enlem
                    self.durak_boylam = self.sol_durak_boylam
                    self.yasak=True
                  
                elif self.sag_ok == True and self.sol_ok == False:
                    print("sagg")
                    self.durak_enlem = self.sag_durak_enlem
                    self.durak_boylam = self.sag_durak_boylam
                    self.yasak=True

                #print("engel",engel_enlem,engel_boylam)
                #print("sag durak", self.sag_durak_enlem , self.sag_durak_boylam)
                #print("sol durak", self.sol_durak_enlem , self.sol_durak_boylam)
