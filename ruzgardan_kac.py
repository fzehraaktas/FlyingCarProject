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
