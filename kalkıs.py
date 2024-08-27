elif self.barometre.hata == False and self.irtifa_araliginda == False:
    if self.barometre.irtifa < 10 and self.barometre.irtifa < 100:
    self.yukari_git(YAVAS)
    elif self.barometre.irtifa < 30 and self.barometre.irtifa < 100:
        self.yukari_git(ORTA)
    elif self.barometre.irtifa < 100:
        self.yukari_git(HIZLI)
    else: 
        self.irtifa_araliginda = True 
elif self.gnss.hata == False and self.irtifa_araliginda == False:
    if self.gnss.irtifa < 10:
        self.yukari_git(YAVAS)
    elif self.gnss.irtifa < 30:
        self.yukari_git(ORTA)
    elif self.gnss.irtifa < 100:
        self.yukari_git(HIZLI)
    else: 
        self.irtifa_araliginda = True 
elif  self.irtifa_araliginda == False:
    kalkıs = self.harita.bolge(guncel_enlem,guncel_boylam)
    imu_yuksel = self.imu.hiz.y * self.zaman()
    if (imu_yuksel + kalkıs.yukselti) > 100:
        self.irtifa_araliginda = True 
    elif (imu_yuksel + kalkıs.yukselti) > 50:
        self.yukari_git(HIZLI)
    else: 
        self.yukari_git(YAVAS)
        
