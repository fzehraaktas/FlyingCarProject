#!/usr/bin/env python
from cezeri_lib.cezeri import Cezeri
import rospy
import math
import time

cezeri = Cezeri(rapor = True)

irtifa_araliginda = False
b_gidildi=False
hastane_git=False
hastane_gidildi=False
cezeri_hata=False
sag_yasak=False
sol_yasak=False
yasak=False
ilk_zaman=0
ruzgar_bolge= []
bolge = cezeri.yerel_harita[4]

def donus_tamamla(hedef_enlem,hedef_boylam,guncel_enlem,guncel_boylam):#donus fonksiyonu

        cos = hedef_enlem-guncel_enlem
        sin = hedef_boylam-guncel_boylam
        x = math.degrees(math.atan2(sin,cos))

        if x>180 :
            hedef_aci= x-360
        
        else:
            hedef_aci=x


        if math.radians(hedef_aci)- 0.05 < cezeri.manyetometre.veri < math.radians(hedef_aci)+ 0.05 :
            cezeri.don(0)
      
        else:

            if 0<=hedef_aci<=180 and 0<=math.degrees(cezeri.manyetometre.veri)<=180 or 0>=hedef_aci>=-180 and 0>=math.degrees(cezeri.manyetometre.veri)>=-180  :
                
                donus_aci = math.radians(hedef_aci)-cezeri.manyetometre.veri
                cezeri.dur()
                cezeri.don(donus_aci)      
                cezeri.bekle(0.01)   
                
            elif 0<math.degrees(cezeri.manyetometre.veri)<180 and 0>hedef_aci>-180:

                a= math.radians(hedef_aci)-cezeri.manyetometre.veri
                b= a+2*(math.pi)

                if abs(a)<abs(b):
                    donus_aci=a
                else:
                    donus_aci=b
                
                cezeri.dur()
                cezeri.don(donus_aci)      
                cezeri.bekle(0.01) 
            
            elif 0>math.degrees(cezeri.manyetometre.veri)>-180 and 0<hedef_aci<180 :
                
                a = math.radians(hedef_aci)-cezeri.manyetometre.veri
                b = a-2*(math.pi)

                if abs(a)<abs(b):
                    donus_aci=a
                else:
                    donus_aci=b

                cezeri.dur()
                cezeri.don(donus_aci)      
                cezeri.bekle(0.01)
       
while cezeri.aktif() and cezeri.acil_durum==False:#Start
    hedef = cezeri.hedefler[0]

    hedef_enlem = hedef.bolge.enlem
    hedef_boylam = hedef.bolge.boylam
    
    guncel_enlem = cezeri.gnss.enlem
    guncel_boylam = cezeri.gnss.boylam

    son_enlem = cezeri.gnss.enlem
    son_boylam = cezeri.gnss.boylam
    now = cezeri.zaman

    if cezeri.acil_durum ==True:
        break

    if cezeri.barometre.irtifa < cezeri.irtifa_araligi[0] and irtifa_araliginda == False:
        cezeri.yukari_git(cezeri.HIZLI)  
        a_enlem=cezeri.gnss.enlem
        a_boylam=cezeri.gnss.boylam

    elif cezeri.acil_durum==False:

        if irtifa_araliginda == False:
            irtifa_araliginda = True
            yukseklik = cezeri.gnss.irtifa
            cezeri.dur()

        rota_enlem=(hedef_enlem-a_enlem)/40
        rota_boylam=(hedef_boylam-a_boylam)/40

        sag_enlem = +rota_boylam
        sag_boylam = -rota_enlem

        sol_enlem = -rota_boylam
        sol_boylam = +rota_enlem

        for i in range (40):
            a_enlem = a_enlem+rota_enlem
            a_boylam = a_boylam+rota_boylam
            bolgex = cezeri.harita.bolge(a_enlem,a_boylam)

            if bolgex.ruzgar==True:
                ruzgar_bolge.append([a_enlem,a_boylam])
                engel_sag_enlem=ruzgar_bolge[0][0]
                engel_sag_boylam=ruzgar_bolge[0][1]
                
                engel_sol_enlem=ruzgar_bolge[0][0]
                engel_sol_boylam=ruzgar_bolge[0][1]

                for i in range (10):
                    engel_sag_enlem = engel_sag_enlem+sag_enlem
                    engel_sag_boylam = engel_sag_boylam+sag_boylam
                    bolge_sag = cezeri.harita.bolge(engel_sag_enlem,engel_sag_boylam)

                    if bolge_sag.ruzgar==False:
                        sag_durak_enlem=engel_sag_enlem
                        sag_durak_boylam=engel_sag_boylam 
                        sag_x_enlem=engel_sag_enlem
                        sag_x_boylam=engel_sag_boylam
                        rota_sag_enlem=(hedef_enlem-sag_x_enlem)/40
                        rota_sag_boylam=(hedef_boylam-sag_x_boylam)/40
                    

                for i in range (10):
                    engel_sol_enlem = engel_sol_enlem+sol_enlem
                    engel_sol_boylam = engel_sol_boylam+sol_boylam
                    bolge_sol = cezeri.harita.bolge(engel_sol_enlem,engel_sol_boylam)

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
                    bolgey = cezeri.harita.bolge(sag_x_enlem,sag_x_boylam)

                    if bolgey.ruzgar==True: 
                        sag_yasak=True
                        
                    sol_x_enlem = sol_x_enlem+rota_sol_enlem
                    sol_x_boylam = sol_x_boylam+rota_sol_boylam
                    bolgez = cezeri.harita.bolge(sol_x_enlem,sol_x_boylam)

                    if bolgez.ruzgar==True: 
                        sol_yasak=True      
                      
                    if i==39:
                        yasak=True 

        if yasak==True:

            if sag_yasak==False:
                #sagdan git
                durak_enlem=sag_durak_enlem
                durak_boylam=sag_durak_boylam
            else:
                #soldan git
                durak_enlem=sol_durak_enlem
                durak_boylam=sol_durak_boylam

            donus_tamamla(durak_enlem,durak_boylam,guncel_enlem,guncel_boylam)

            if durak_boylam- 0.3 < guncel_boylam < durak_boylam + 0.3 and durak_enlem-0.3 < guncel_enlem < durak_enlem +0.3 :
                cezeri.dur()
                yasak=False
            else: 
                cezeri.ileri_git(cezeri.ORTA)

        if b_gidildi==False and yasak==False:
            donus_tamamla(hedef_enlem,hedef_boylam,guncel_enlem,guncel_boylam)
           
            if hedef_boylam - 5 < guncel_boylam < hedef_boylam + 5 and hedef_enlem-5 < guncel_enlem < hedef_enlem+5 :
                if  hedef_boylam - 1 < guncel_boylam < hedef_boylam + 1 and hedef_enlem-1 < guncel_enlem < hedef_enlem+1 :
                    if hedef_boylam - 0.3 < guncel_boylam < hedef_boylam + 0.3 and hedef_enlem-0.3 < guncel_enlem < hedef_enlem+0.3 :
                        cezeri.dur()
                        b_gidildi=True
                    else: 
                        cezeri.ileri_git(cezeri.YAVAS)
                else: 
                    cezeri.ileri_git(cezeri.ORTA)
            else: 
                cezeri.ileri_git(cezeri.HIZLI)

        elif b_gidildi==True:#b_gidildi=True
            if cezeri.lidar.hata == True or bolge.yagmur == True: 
                if cezeri.radar.mesafe >= 1 :
                    if cezeri.radar.mesafe > 25:
                        cezeri.asagi_git(cezeri.HIZLI)
                    else:
                        if cezeri.radar.mesafe > 10:
                            cezeri.asagi_git(cezeri.ORTA)
                        else: 
                            cezeri.asagi_git(cezeri.YAVAS)
                else: 
                    cezeri.asagi_git(cezeri.YAVAS)
                    cezeri.bekle(1)
                    cezeri.dur()
            else: 
                if cezeri.lidar.mesafe >= 1 :
                    if cezeri.lidar.mesafe > 25:
                        cezeri.asagi_git(cezeri.HIZLI)
                    else:
                        if cezeri.lidar.mesafe > 10:
                            cezeri.asagi_git(cezeri.ORTA)
                        else: 
                            cezeri.asagi_git(cezeri.YAVAS)
                else: 
                    cezeri.asagi_git(cezeri.YAVAS)
                    cezeri.bekle(1)
                    cezeri.dur()

while cezeri.aktif() and cezeri.acil_durum==True:#hastane git.

    uzaklik = []
    bolge_sayisi= 0
    bolge_enlem = []
    bolge_boylam = []
    now=cezeri.zaman

    guncel_enlem = cezeri.gnss.enlem
    guncel_boylam = cezeri.gnss.boylam

    for hastane in cezeri.harita.hastaneler:
        bolge_sayisi+=1
        bolge_enlem.append(hastane.enlem)
        bolge_boylam.append(hastane.boylam)
        x = abs(a_enlem-hastane.enlem)
        y = abs(a_boylam-hastane.boylam)
        z = (x**2 + y**2) ** 0.5
        uzaklik.append(z)
   
   
    eleman = min(uzaklik)
    for i in range(0,bolge_sayisi-1,+1):
        if eleman == uzaklik[i]:
            hastane_enlem=bolge_enlem[i]
            hastane_boylam=bolge_boylam[i]
            hastane_git=True
    
    while now-ilk_zaman > 1  and hastane_gidildi==False:
        now=cezeri.zaman

        rota_enlem += cezeri.imu.hiz.x/20
        rota_boylam += cezeri.imu.hiz.y/20

        gercek_enlem=son_enlem+rota_enlem
        gercek_boylam=son_boylam+rota_boylam

        if cezeri.gnss.enlem==0 and cezeri.gnss.boylam==0:
            cezeri_hata=True
        else:
            cezeri_hata=False

        if cezeri.gnss.spoofing==True:
            cezeri_hata=True

        ilk_zaman=cezeri.zaman


    if hastane_gidildi==False and hastane_git==True:

        if cezeri_hata==False:
            donus_tamamla(hastane_enlem,hastane_boylam,guncel_enlem,guncel_boylam)

            if hastane_boylam - 5 < guncel_boylam < hastane_boylam + 5 and hastane_enlem-5 < guncel_enlem < hastane_enlem+5 :
                if  hastane_boylam - 1 < guncel_boylam < hastane_boylam + 1 and hastane_enlem-1 < guncel_enlem < hastane_enlem+1 :
                    if hastane_boylam - 0.3 < guncel_boylam < hastane_boylam + 0.3 and hastane_enlem-0.3 < guncel_enlem < hastane_enlem+0.3 :
                        cezeri.dur()
                        hastane_gidildi=True
                    else: 
                        cezeri.ileri_git(cezeri.YAVAS)
                else: 
                    cezeri.ileri_git(cezeri.ORTA)
            else: 
                cezeri.ileri_git(cezeri.HIZLI)

        else:
            donus_tamamla(hastane_enlem,hastane_boylam,gercek_enlem,gercek_boylam)

            if hastane_boylam - 5 < gercek_boylam < hastane_boylam + 5 and hastane_enlem-5 < gercek_enlem < hastane_enlem+5 :
                if  hastane_boylam - 1 < gercek_boylam < hastane_boylam + 1 and hastane_enlem-1 < gercek_enlem < hastane_enlem+1 :
                    if hastane_boylam - 0.3 < gercek_boylam < hastane_boylam + 0.3 and hastane_enlem-0.3 < gercek_enlem < hastane_enlem+0.3 :
                        cezeri.dur()
                        hastane_gidildi=True
                    else: 
                        cezeri.ileri_git(cezeri.YAVAS)
                else: 
                    cezeri.ileri_git(cezeri.ORTA)
            else: 
                cezeri.ileri_git(cezeri.HIZLI)

        

    elif hastane_gidildi==True:
        if cezeri.lidar.hata == True or bolge.yagmur == True: 
            if cezeri.radar.mesafe >= 1 :
                if cezeri.radar.mesafe > 25:
                    cezeri.asagi_git(cezeri.HIZLI)
                else:
                    if cezeri.radar.mesafe > 10:
                        cezeri.asagi_git(cezeri.ORTA)
                    else: 
                        cezeri.asagi_git(cezeri.YAVAS)
            else: 
                cezeri.asagi_git(cezeri.YAVAS)
                cezeri.bekle(1)
                cezeri.dur()

        else: 
            if cezeri.lidar.mesafe >= 1 :
                if cezeri.lidar.mesafe > 25:
                    cezeri.asagi_git(cezeri.HIZLI)
                else:
                    if cezeri.lidar.mesafe > 10:
                        cezeri.asagi_git(cezeri.ORTA)
                    else: 
                        cezeri.asagi_git(cezeri.YAVAS)
            else: 
                cezeri.asagi_git(cezeri.YAVAS)
                cezeri.bekle(1)
                cezeri.dur()