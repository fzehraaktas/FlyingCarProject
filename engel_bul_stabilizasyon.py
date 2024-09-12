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

            if bolge.ucusa_yasakli_bolge == False and bolge.ruzgar == False and bolge.yukselti < 100 :
                kontrol_enlem = engel_enlem
                kontrol_boylam = engel_boylam
                kk_enlem=(kontrol_enlem - kalkis_enlem )/100 #kalkis_kontrol
                kk_boylam=(kontrol_boylam -kalkis_boylam)/100

                for i in range (100):
                    kalkis_enlem = kalkis_enlem + kk_enlem
                    kalkis_boylam = kalkis_boylam + kk_boylam
                    bolgex = self.harita.bolge(kalkis_enlem,kalkis_boylam)

                    if bolgex.ucusa_yasakli_bolge == True or bolgex.ruzgar == True or bolgex == self.trafik_bolge or bolgex.yukselti >= 100: 
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

            if bolge.ucusa_yasakli_bolge == False and bolge.ruzgar == False and bolge.yukselti< 100 :
                
                kontrol_enlem = engel_enlem
                kontrol_boylam = engel_boylam
                kk_enlem=(kontrol_enlem - kalkis_enlem )/100 #kalkis_kontrol
                kk_boylam=(kontrol_boylam - kalkis_boylam)/100

                for i in range (100):
                    kalkis_enlem = kalkis_enlem + kk_enlem
                    kalkis_boylam = kalkis_boylam + kk_boylam
                    bolgex = self.harita.bolge(kalkis_enlem,kalkis_boylam)

                    if bolgex.ucusa_yasakli_bolge == True or bolgex.ruzgar == True or bolgex.yukselti >= 100 or bolgex == self.trafik_bolge: 
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

                if bolge.ucusa_yasakli_bolge == True or bolge.ruzgar == True or bolge.yukselti>= 100:
            
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
                       
                        self.durak_enlem = self.sol_durak_enlem
                        self.durak_boylam = self.sol_durak_boylam
                        uzaklik = math.sqrt((self.durak_enlem-guncel_enlem)**2 + (self.durak_boylam-guncel_boylam)**2)
                        if uzaklik < 5:  
                            self.yasak = False
                        else: 
                            self.yasak = True
                        
                    else:
                    
                        self.durak_enlem = self.sag_durak_enlem
                        self.durak_boylam = self.sag_durak_boylam
                        uzaklik = math.sqrt((self.durak_enlem-guncel_enlem)**2 + (self.durak_boylam-guncel_boylam)**2)

                        if uzaklik < 5:  
                            self.yasak = False
                        else: 
                            self.yasak = True

        else:      
            self.sag_kontrol(guncel_enlem,guncel_boylam,hedef_enlem,hedef_boylam,self.trafik_enlem,self.trafik_boylam)
            self.sol_kontrol(guncel_enlem,guncel_boylam,hedef_enlem,hedef_boylam,self.trafik_enlem,self.trafik_boylam)
                
            k_sag = math.sqrt((self.sag_durak_enlem- round(guncel_enlem,1) )**2 + (self.sag_durak_boylam- round(guncel_boylam,1) )**2)
            v_sag = math.sqrt((self.sag_durak_enlem-hedef_enlem)**2 + (self.sag_durak_boylam-hedef_boylam)**2)

            k_sol = math.sqrt((self.sol_durak_enlem-round(guncel_enlem,1))**2 + (self.sol_durak_boylam-round(guncel_boylam,1) )**2)
            v_sol = math.sqrt((self.sol_durak_enlem-hedef_enlem)**2 + (self.sol_durak_boylam-hedef_boylam)**2)

            sag_uzaklik = k_sag + v_sag     
            sol_uzaklik = k_sol + v_sol    

            if sol_uzaklik < sag_uzaklik:
                self.durak_enlem = self.sol_durak_enlem
                self.durak_boylam = self.sol_durak_boylam
                uzaklik = math.sqrt((self.durak_enlem-guncel_enlem)**2 + (self.durak_boylam-guncel_boylam)**2)
               
                if uzaklik < 5:  
                    self.trafik_engel = False
                    self.yasak = False
                    
                else: 
                    self.yasak = True
                    
            else:
                self.durak_enlem = self.sag_durak_enlem
                self.durak_boylam = self.sag_durak_boylam
                uzaklik = math.sqrt((self.durak_enlem-guncel_enlem)**2 + (self.durak_boylam-guncel_boylam)**2)

                if uzaklik < 5:  
                    self.trafik_engel = False
                    self.yasak = False
                    
                else: 
                    self.yasak = True
