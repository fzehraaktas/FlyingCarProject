    def  hiz_kontrol(self, kalkis_enlem, kalkis_boylam, hedef_enlem, hedef_boylam)
        rota_enlem=(hedef_enlem-kalkis_enlem)/40
        rota_boylam=(hedef_boylam-kalkis_boylam)/40

        for i in range (40):
            kalkis_enlem = kalkis_enlem + rota_enlem
            kalkis_boylam = kalkis_boylam + rota_boylam
            bolge = self.harita.bolge(kalkis_enlem, kalkis_boylam)

            if bolge.yavas_bolge == True:
                print("hız bölgesi")
                return True 
            else:
                return False 
