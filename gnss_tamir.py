
def gnss_tamir(self)
ilk_zaman = 0
now = self.zaman()

while now - ilk_zaman > 1 :
    now = self.zaman()

    rota_enlem += self.imu.hiz.x/20
    rota_boylam += self.imu.hiz.y/20

    gercek_enlem=Cezeri.enlem+rota_enlem
    gercek_boylam=Cezeri.boylam+rota_boylam

    if self.gnss.enlem == 0 and self.gnss.boylam == 0:
        self_hata=True
    else:
        self_hata=False

    if self.gnss.spoofing == True:
        self_hata=True

    ilk_zaman = self.zaman()
              
        
if self_hata==False:
    print("hata yok") 
    print("gnss",self.gnss.enlem,self.gnss.boylam)
    print("olcum", gercek_enlem, gercek_boylam)
      
else:
    print("hata!")
    print("gnss",self.gnss.enlem,self.gnss.boylam)
    print("olcum", gercek_enlem, gercek_boylam)