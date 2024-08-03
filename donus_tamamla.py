def donus_tamamla(self,hedef_enlem,hedef_boylam,guncel_enlem,guncel_boylam):#donus fonksiyonu

        cos = hedef_enlem-guncel_enlem
        sin = hedef_boylam-guncel_boylam
        x = math.degrees(math.atan2(sin,cos))

        if x>180 :
            hedef_aci= x-360
            
        else:
            hedef_aci=x

        if math.radians(hedef_aci)- 0.05 < self.manyetometre.veri < math.radians(hedef_aci)+ 0.05 :
            self.dur()
        
        else:

            if 0<=hedef_aci<=180 and 0<=math.degrees(self.manyetometre.veri)<=180 or 0>=hedef_aci>=-180 and 0>=math.degrees(self.manyetometre.veri)>=-180  :
                    
                donus_aci = math.radians(hedef_aci)-self.manyetometre.veri
                self.don(donus_aci) 
              
                   
            elif 0<math.degrees(self.manyetometre.veri)<180 and 0>hedef_aci>-180:

                a= math.radians(hedef_aci)-self.manyetometre.veri
                b= a+2*(math.pi)

                if abs(a)<abs(b):
                    donus_aci=a
                else:
                    donus_aci=b

                self.don(donus_aci)  
                
       
            elif 0>math.degrees(self.manyetometre.veri)>-180 and 0<hedef_aci<180 :         
                a = math.radians(hedef_aci)-self.manyetometre.veri
                b = a-2*(math.pi)

                if abs(a)<abs(b):
                    donus_aci=a
                else:
                    donus_aci=b

                self.don(donus_aci)    