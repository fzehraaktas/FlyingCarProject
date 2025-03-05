#!/usr/bin/env python
from cezeri_lib.cezeri import Cezeri
import rospy
import math
import time
import random

cezeri = Cezeri(rapor = True)
cezeri.klavye = False
debug = True
"""**********************************************************************************************************************************"""
#Global degiskenler*********************************************************************************************************************
"""**********************************************************************************************************************************"""
baslangic_hedefler = [] #Baslangicda verilen hedefler x ve y cinsinden.
gidilecek_hedefler = [] #Baslangicda verilen hedefler.
gidilen_hedefler = []  #Gidilen hedeflerin eklendigi liste.
loc_stat, baro_stat, magneto_stat, motor_stat, motor_stat_2, emergency, emergency_2, radar_stat = 1, 1, 1, 1, 1, 1, 1, 1 #Konum tespit isleminin nasil olacagini belirleyen deger.
cal_x, cal_y = cezeri.gnss.enlem, cezeri.gnss.boylam #Gnss arizasinda kullanilan hesaplanan konumlar.
lgx, lgy = cal_x, cal_y #Spoffing algilama icin kullanilir.
ldeg = cezeri.manyetometre.veri
cal_degree = cezeri.manyetometre.veri
adv_navi_guncel_x, adv_navi_guncel_y = cezeri.gnss.enlem, cezeri.gnss.boylam
rota = False #Rota guncellendiginde True olan degisken.
setup = True #Ilk calistirmadan sonra False olan degisken.

"""**********************************************************************************************************************************"""
#Fonksiyonlar***************************************************************************************************************************
"""**********************************************************************************************************************************"""
#Arac siradaki hedefe gitmesi icin engelsiz bir rota cizer.
#Girdi olarak daha onceden gidilmis hedefleri alir.
def AdvNavi():
    if debug: print("***AdvNavi fonksiyonu calisti***")
    global gidilecek_hedefler, baslangic_x, motor_stat_2, emergency_2, adv_navi_guncel_x, adv_navi_guncel_y
    hedefc = 0 #Hedef sayisi
    Waypoints = [] #Dodurulecek liste
    kalan_hedefler = gidilecek_hedefler[:] #Gidilen hedeflerin cikartildigi liste
    adv_navi_guncel_x, adv_navi_guncel_y = Data_Center("lokasyon") #Aracin guncel konumu
    mevcut_sarj = Data_Center("batarya") #Aracin mevcut sarj yuzdesi durumu
    kalkis = False #Bir onceki waypointte inis yapip yapmadigi bilgisini alir ve ona gore sarj hesaplanir

    #En yakin siradaki hedef bulunur.
    def EnYakinHedef(adv_navi_guncel_x, adv_navi_guncel_y, liste):
        en_kucuk_sira = 1000
        ilk_gidilecekler = []
        ilk_gidilecekler_inis = []
        en_yakin_mesafe = 100000
        inis = False
        #Kalan hedefler arasindaki en kucuk sira numarasi bulunur
        list_len = len(liste)
        for hedef in liste:
            if (hedef.sira < en_kucuk_sira) and (hedef.sira != 0):
                en_kucuk_sira = hedef.sira
        if en_kucuk_sira == 1000: en_kucuk_sira = 0
        #En kucuk sira numarasina sahip hedefler listeye eklenir
        for hedef in liste:
            if hedef.sira == en_kucuk_sira:
                ilk_gidilecekler.append(hedef)
        
        #Inis yapilacak hedefler baska bir listeye eklenir mevcut listeden silinir
        for hedef in ilk_gidilecekler:
            if hedef.amac == cezeri.INIS:
                ilk_gidilecekler_inis.append(hedef)
                ilk_gidilecekler.remove(hedef)

        #Listedeki hedeflerden en yakini bulunur
        if 0 < len(ilk_gidilecekler):
            for hedef in ilk_gidilecekler:
                a = abs(hedef.bolge.enlem - adv_navi_guncel_x)
                b = abs(hedef.bolge.boylam - adv_navi_guncel_y)
                c = math.sqrt(a**2 + b**2)
                if c < en_yakin_mesafe:
                    hx = hedef.bolge.enlem
                    hy = hedef.bolge.boylam
                    en_yakin_mesafe = c
                    gonderilen_hedef = hedef
                    inis = False
                        
        else:
            for hedef in ilk_gidilecekler_inis:
                a = abs(hedef.bolge.enlem - adv_navi_guncel_x)
                b = abs(hedef.bolge.boylam - adv_navi_guncel_y)
                c = math.sqrt(a**2 + b**2)
                if c < en_yakin_mesafe:
                    hx = hedef.bolge.enlem
                    hy = hedef.bolge.boylam
                    en_yakin_mesafe = c
                    gonderilen_hedef = hedef
                    inis = True

        return hx, hy, inis, gonderilen_hedef
        
    #Hedefe gitmek icin uzerinden gecilecek noktalar bulunur.
    def UGBB(hx, hy, adv_navi_guncel_x, adv_navi_guncel_y):
        uzerinden_gecilen_bolgeler_x = []
        uzerinden_gecilen_bolgeler_y = []
        uzerinden_gecilen_bolgeler = []
        kontrol_bitti = False
        kontrol_noktasi_y = adv_navi_guncel_y
        kontrol_noktasi_x = adv_navi_guncel_x
        x_uzunluk = hx - adv_navi_guncel_x
        y_uzunluk = hy - adv_navi_guncel_y
        hipotenus = math.sqrt(x_uzunluk**2 + y_uzunluk**2)
        if int(hipotenus) != 0:
            x_adim = x_uzunluk/int(hipotenus)
            y_adim = y_uzunluk/int(hipotenus)
        else:
            x_adim = 0
            y_adim = 0
        while kontrol_bitti == False:
            kontrol_noktasi_x += (x_adim/100)
            kontrol_noktasi_y += (y_adim/100)
            if kontrol_noktasi_y < 0:
                y_yarim = -0.5
            else:
                y_yarim = 0.5
            if kontrol_noktasi_x < 0:
                x_yarim = -0.5
            else:
                x_yarim = 0.5
            if ((int(kontrol_noktasi_x)+x_yarim),(int(kontrol_noktasi_y)+y_yarim)) not in uzerinden_gecilen_bolgeler:
                uzerinden_gecilen_bolgeler.append(((int(kontrol_noktasi_x)+x_yarim),(int(kontrol_noktasi_y)+y_yarim)))
                uzerinden_gecilen_bolgeler_y.append(int(kontrol_noktasi_y)+y_yarim)
                uzerinden_gecilen_bolgeler_x.append(int(kontrol_noktasi_x)+x_yarim)

            if int(kontrol_noktasi_x) == int(hx) and int(kontrol_noktasi_y) == int(hy):
                kontrol_bitti = True
        return uzerinden_gecilen_bolgeler_x, uzerinden_gecilen_bolgeler_y 

    #Uzerinden gecilecek noktalar kontrol edilir. Engel yoksa hedef waypoint olaraka atanir.
    def BolgeKontrol(uzerinden_gecilen_bolgeler_x, uzerinden_gecilen_bolgeler_y):
        bolgec = 0
        engel_bulundu = False
        yavas_bolge = False
        y = 0
        x = 0
        bolge_sayisi = len(uzerinden_gecilen_bolgeler_y)
        while bolgec != bolge_sayisi and engel_bulundu == False:
            y = uzerinden_gecilen_bolgeler_y[bolgec]
            x = uzerinden_gecilen_bolgeler_x[bolgec]
            if(x == adv_navi_guncel_x and y == adv_navi_guncel_y):
                bolgec+=1
                continue
            bolge = cezeri.harita.bolge(x, y)
            if (bolge.yukselti) >= 100:
                if debug: print("\033[1mEngel tipi:\033[0m Yukselti")
                engel_bulundu = True
                engel_type = "Yukselti"
                break
            elif bolge.ucusa_yasakli_bolge and (bolge.enlem <= -21.5 and bolge.boylam >= 20.5):
                engel_bulundu = True
                if debug: print("\033[1mEngel tipi:\033[0m Ucusa yasakli bolge")
                break
            elif bolge.ruzgar:
                if debug: print("\033[1mEngel tipi:\033[0m Ruzgar")
                engel_bulundu = True
                engel_type = "Ruzgar"
                break
            elif bolge.yavas_bolge:
                yavas_bolge = True
            bolgec+=1
        return engel_bulundu, x, y, yavas_bolge
    
    def NaviTargetAngle(ehx,ehy):
        x=ehx-adv_navi_guncel_x
        y=ehy-adv_navi_guncel_y
        angleB = math.degrees(math.atan((y-0.00000000000000000000000000000000000000000000000000000000000001) / (x-0.000000000000000000000000000000000000000000001)))
        
        if x > 0 and y < 0:
            angleB = angleB
        elif x < 0 and y < 0:
            angleB = angleB + 180
        elif x < 0 and y > 0:
            angleB = angleB - 180
        elif x > 0 and y > 0:
            angleB = angleB
        
        while angleB > 180: angleB-=360
        while angleB < -180: angleB+=360
        return angleB

    #Yerel bolgelerden hangisinin aracin onu oldugunu bulur.
    def Yerel_YerelYon(sdeg):
        if sdeg > 180: sdeg = sdeg-360

        if sdeg == 0: bolge = 5
        elif -90 < sdeg < 0: bolge = 8
        elif sdeg == -90: bolge = 7
        elif -180 < sdeg < -90: bolge = 6
        elif sdeg in (180, -180): bolge = 3
        elif 90 < sdeg < 180: bolge = 0
        elif sdeg == 90: bolge = 1
        elif 0 < sdeg < 90: bolge = 2

        return bolge

    def Yerel4Yon(sdeg):
        if sdeg > 180: sdeg = sdeg-360

        if 45 >= sdeg > -45: bolge = 5
        elif -45 >= sdeg > -135: bolge = 7
        elif (-135 >= sdeg >= -180) or (135 < sdeg <= 180): bolge = 3
        elif 135 >= sdeg > 45: bolge = 1

        return bolge

    #Uzerinden gecilecek noktalar uzerinde engel varsa engel olan noktanin sagina yada soluna -yakin olana- waypoint atilir yoksa dogrudan konuma waypoint atilir.
    def EngelOnlem(aci, ehx, ehy, hx, hy):
        print("Engel onlem calistirildi")
        irtifa = 100
        fehx, fehy = ehx, ehy
        engel_bolgesi = [cezeri.harita.bolge(ehx, ehy)]
        taranan_engel_bolgesi = []
        taranan_engel_bolgesi_x = []
        taranan_engel_bolgesi_y = []
        yasak_bolge = False
        kose = False

        #Engel yasak bolgenin bulundugu alanda mi (Sistem hatasina onlem)
        if (ehx <= -21.5 and ehy >= 20.5): yasak_bolge = True
        else: yasak_bolge = False

        #Mevcut engel bolgesinin tespiti
        while True:
            bolge = None
            for sb in engel_bolgesi:
                if sb not in taranan_engel_bolgesi:
                    bolge = sb
            if bolge == None: break

            taranan_engel_bolgesi.append(bolge)
            ehx = bolge.enlem
            ehy = bolge.boylam
            t_bolge = cezeri.harita.bolge(ehx+1, ehy)
            if t_bolge.yukselti >= irtifa or t_bolge.ruzgar or t_bolge.trafik or (yasak_bolge and t_bolge.ucusa_yasakli_bolge):
                engel_bolgesi.append(t_bolge)
            t_bolge = cezeri.harita.bolge(ehx-1, ehy)
            if t_bolge.yukselti >= irtifa or t_bolge.ruzgar or t_bolge.trafik or (yasak_bolge and t_bolge.ucusa_yasakli_bolge):
                engel_bolgesi.append(t_bolge)
            t_bolge = cezeri.harita.bolge(ehx, ehy+1)
            if t_bolge.yukselti >= irtifa or t_bolge.ruzgar or t_bolge.trafik or (yasak_bolge and t_bolge.ucusa_yasakli_bolge):
                engel_bolgesi.append(t_bolge)
            t_bolge = cezeri.harita.bolge(ehx, ehy-1)
            if t_bolge.yukselti >= irtifa or t_bolge.ruzgar or t_bolge.trafik or (yasak_bolge and t_bolge.ucusa_yasakli_bolge):
                engel_bolgesi.append(t_bolge)
        for bolge in taranan_engel_bolgesi:
            taranan_engel_bolgesi_x.append(bolge.enlem)
            taranan_engel_bolgesi_y.append(bolge.boylam)

        #Mevcut engel bolgesinin enlerinin tespiti
        max_x, max_y, min_x, min_y = -5000000, -5000000, 5000000, 5000000
        for sb in taranan_engel_bolgesi:
            if sb.enlem > max_x: max_x = sb.enlem
            if sb.enlem < min_x: min_x = sb.enlem
            if sb.boylam > max_y: max_y = sb.boylam
            if sb.boylam < min_y: min_y = sb.boylam
        
        gyerel = YerelYon(aci) #Esit acilar
        yerel = Yerel_YerelYon(aci) #Dik acilar
        yyerel = Yerel4Yon(aci) #4aci

        if debug: print("Tespit edilen engelin koseleri:")
        if debug: print((max_x, max_y),(min_x, min_y))

        if debug: print("Yerel yon:")
        if debug: print(yyerel, yerel)
        if debug: print(aci)
        

        #Sag Sol Karari
        ssag = None
        yan_kenar = max_y - min_y
        ust_kenar = max_x - min_x

        #koselere gelirse
        if (fehx, fehy) in [(min_x, max_y), (min_x, min_y), (max_x, max_y), (max_x, min_y)]:
            #if debug: print("Koselerden birindesiniz")
            if (fehx, fehy) in [(min_x, max_y), (max_x, min_y)]:
                if yan_kenar <= ust_kenar: ssag = True
                else: ssag = False
            else:
                if yan_kenar <= ust_kenar: ssag = False
                else: ssag = True
            kose = True

        #kenarlara gelirse
        else:
            #if debug: print("Kenarlardan birindesiniz", hx, hy, adv_navi_guncel_x, adv_navi_guncel_y, fehx, fehy)
            #Engelli alanin icinde olma durumu
            if (max_x >= adv_navi_guncel_x >= min_x) and (max_y >= adv_navi_guncel_y >= min_y):
                kfx, kfy = adv_navi_guncel_x, adv_navi_guncel_y
                yon = 0
                #X+ deneme > 1
                if yon == 0:
                    yon = 1
                    for i in range(20):
                        kfx+=1
                        if kfx in taranan_engel_bolgesi_x:
                            kfx = adv_navi_guncel_x
                            yon = 0
                            break
                #X- deneme > 2        
                if yon == 0:
                    yon = 2
                    for i in range(20):
                        kfx-=1
                        if kfx in taranan_engel_bolgesi_x:
                            kfx = adv_navi_guncel_x
                            break
                #Y+ deneme > 3
                if yon == 0:
                    yon = 3
                    for i in range(20):
                        kfy+=1
                        if kfy in taranan_engel_bolgesi_y:
                            kfy = adv_navi_guncel_y
                            yon = 0
                            break
                #Y- deneme > 4
                if yon == 0:
                    yon = 4
                    for i in range(20):
                        kfy+=1
                        if kfy in taranan_engel_bolgesi_y:
                            kfy = adv_navi_guncel_y
                            yon = 0
                            break
            
                if yon == 1: fehx = max_x+1
                elif yon == 2: fehx = min_x-1
                elif yon == 3: fehy = max_y+1
                elif yon == 4: fehy = min_y-1

                return fehx, fehy
            
            #Engelin engelli alanin icinde olma durumu
            if (max_x > fehx > min_x) and (max_y > fehy > min_y):
                if yyerel == 1:
                    if yerel in (1, 2): ssag = True
                    elif yerel == 0: ssag= False
                elif yyerel == 5:
                    if yerel in (5, 8): ssag = True
                    elif yerel == 2: ssag= False
                elif yyerel == 7:
                    if yerel in (6, 7): ssag = True
                    elif yerel == 8: ssag= False
                elif yyerel == 3:
                    if yerel in (3, 6): ssag = True
                    elif yerel == 0: ssag= False

            #Engelin dikey kenarin uzerinde olma durumu
            if debug: print(12313123124123412412414)
            if fehx in (max_x, min_x): #Dikey kenar
                #if debug: print(1, hy, max_y, min_y)
                if yerel in (2, 5, 8, 7):
                    if debug: print(1)
                    if (abs(max_y - hy)) < (abs(min_y - hy)): ssag = False
                    else: ssag = True
                else:
                    if debug: print(2)
                    if (abs(max_y - hy)) < (abs(min_y - hy)): ssag = True
                    else: ssag = False
            elif fehy in (max_y, min_y): #Engelin yatay kenarin uzerinde olma durumu
                #if debug: print(2, hx, max_x, min_x)
                if yerel in (0, 1, 2, 5):
                    if (abs(max_x - hx)) < (abs(min_x - hx)): ssag = True
                    else: ssag = False
                else:
                    if (abs(max_x - hx)) < (abs(min_x - hx)): ssag = False
                    else: ssag = True
        if debug: print("ssag", ssag)
        if debug: print(yerel, gyerel, yyerel)

        #Yeni konumun hesaplanmasi
        sol_ehx = fehx
        sol_ehy = fehy
        #Kose ise
        while kose:
            if (adv_navi_guncel_x, adv_navi_guncel_y) in [((min_x-1), (max_y+1)), ((min_x-1), (min_y-1)), ((max_x+1), (max_y+1)), ((max_x+1), (min_y-1))]:
                print(0)
                if (yerel == 2) and ((adv_navi_guncel_x, adv_navi_guncel_y) == ((max_x+1), (max_y+1))):
                    if ssag: fehx, fehy = (max_x+1), fehy
                    else: fehx, fehy = fehx, (max_y+1)
                    break
                elif (yerel == 8) and ((adv_navi_guncel_x, adv_navi_guncel_y) == ((max_x+1), (min_y-1))):
                    if ssag: fehx, fehy = fehx, (min_y-1)
                    else: fehx, fehy = (max_x+1), fehy
                    break
                elif (yerel == 6) and ((adv_navi_guncel_x, adv_navi_guncel_y) == ((min_x-1), (min_y-1))):
                    if ssag: fehx, fehy = (min_x-1), fehy
                    else: fehx, fehy = fehx, (min_y-1)
                    break
                elif (yerel == 0) and ((adv_navi_guncel_x, adv_navi_guncel_y) == ((min_x-1), (max_y+1))):
                    if ssag: fehx, fehy = fehx, (max_y+1)
                    else: fehx, fehy = (min_x-1), fehy
                    break
            print(1)

            if (fehx, fehy) == (min_x, max_y):
                if yerel == 8:
                    if ssag: fehx, fehy = (min_x-1), (min_y-1)
                    else: fehx, fehy = (max_x+1), (max_y+1)
                    break
                else:
                    fehx-=1
                    fehy+=1
                    break
            elif (fehx, fehy) == (min_x, min_y):
                if yerel == 2:
                    if ssag: fehx, fehy = (max_x+1), (min_y-1)
                    else: fehx, fehy = (min_x-1), (max_y+1)
                    break
                else:
                    fehx-=1
                    fehy-=1
                    break
            elif (fehx, fehy) == (max_x, min_y):
                if yerel == 0:
                    if ssag: fehx, fehy = (max_x+1), (max_y+1)
                    else: fehx, fehy = (min_x-1), (min_y-1)
                    break
                else:
                    fehx+=1
                    fehy-=1
                    break
            elif (fehx, fehy) == (max_x, max_y):
                if yerel == 6:
                    if ssag: fehx, fehy = (min_x-1), (max_y+1)
                    else: fehx, fehy = (max_x+1), (min_y-1)
                    break
                else:
                    fehx+=1
                    fehy+=1
                    break
        
        #Kenarlar
        #Yeni X bulunur
        while (True and (kose == False)):
            #if debug: print(2)
            if gyerel in (3, 5):
                if adv_navi_guncel_x in ((fehx-1), (fehx+1)): break
                if yerel in (2, 8): fehx-=1
                elif yerel in (0, 6): fehx+=1
                break
            if ssag == True: #Sag
                if yerel == 1: fehx+=1
                if yerel == 2: fehx+=1
                if yerel == 8: fehx-=1
                if yerel == 7: fehx-=1
                if yerel == 6: fehx-=1
                if yerel == 0: fehx+=1
                if fehx < min_x or fehx > max_x: break
            elif ssag == False: #Sol
                if yerel == 1: sol_ehx-=1
                if yerel == 2: sol_ehx-=1
                if yerel == 8: sol_ehx+=1
                if yerel == 7: sol_ehx+=1
                if yerel == 6: sol_ehx+=1
                if yerel == 0: sol_ehx-=1
                if sol_ehx < min_x or sol_ehx > max_x:
                    fehx = sol_ehx
                    break
        #Yeni Y bulunur
        while (True and (kose == False)):
            #if debug: print(3)
            if gyerel in (1, 7):
                if adv_navi_guncel_y in ((fehy-1), (fehy+1)): break
                if yerel in (0, 2): fehy-=1
                elif yerel in (6, 8): fehy+=1
                break
            if ssag == True: #Sag
                if yerel == 2: fehy-=1
                if yerel == 5: fehy-=1
                if yerel == 8: fehy-=1
                if yerel == 6: fehy+=1
                if yerel == 3: fehy+=1
                if yerel == 0: fehy+=1
                if fehy < min_y or fehy > max_y: break
            elif ssag == False: #Sol
                if yerel == 2: sol_ehy+=1
                if yerel == 5: sol_ehy+=1
                if yerel == 8: sol_ehy+=1
                if yerel == 6: sol_ehy-=1
                if yerel == 3: sol_ehy-=1
                if yerel == 0: sol_ehy-=1
                if sol_ehy < min_y or sol_ehy > max_y:
                    fehy = sol_ehy
                    break
            
    
        #Belirlenen bolgenin engelli olma durumu
        t_t_bolge = cezeri.harita.bolge(fehx, fehy)
        while (t_t_bolge.yukselti) >= 100 or (t_t_bolge.ucusa_yasakli_bolge and (fehx <= -21.5 and fehy >= 20.5)) or t_t_bolge.ruzgar or t_t_bolge.trafik:
            if ssag == True:
                if yerel in (8, 7):
                    fehy += 1
                elif yerel in (6, 3):
                    fehx += 1
                elif yerel in (0, 1):
                    fehy -=1
                else:
                    fehx -= 1
            else:
                if yerel in (8, 7):
                    fehy -= 1
                elif yerel in (8, 7):
                    fehx -= 1
                elif yerel in (0, 1):
                    fehy +=1
                else:
                    fehx += 1
            t_t_bolge = cezeri.harita.bolge(fehx, fehy)
        #if debug: print(fehx, fehy)
        #Kodun sonu
        return fehx, fehy
    
    def EnYakinIstasyon(gx, gy):
        en_yakin_istasyon_index_numarasi = 0
        en_yakin_istasyon_mesafesi = 10000
        sayac = 0
        ####En yakin istasyon aramasi####
        for i in cezeri.harita.sarj_istasyonlari:
            ix = i.enlem
            iy = i.boylam
            a=ix-gx
            b=iy-gy
            c = math.sqrt(a**2 + b**2)
            if en_yakin_istasyon_mesafesi > c:
                en_yakin_istasyon_mesafesi = c
                en_yakin_istasyon_index_numarasi = sayac
            sayac+=1
        hedef_istasyon = cezeri.harita.sarj_istasyonlari[en_yakin_istasyon_index_numarasi]
        hx = hedef_istasyon.enlem
        hy = hedef_istasyon.boylam
        return hx, hy

    #En yakin istasyona giden yolun waypointleri listeye eklenir.
    def IstasyonaGit(hx, hy):
        global adv_navi_guncel_x, adv_navi_guncel_y
        if debug: print("**IstasyonaGit*fonksiyonu*calisti*")
        engel = True
        hx, hy = EnYakinIstasyon(adv_navi_guncel_x, adv_navi_guncel_y)
        if debug: print("\033[1m\033[93mGidilecek istasyon:\033[0m")
        if debug: print(hx, hy)
        while engel == True:
            if debug: print("\033[1m\033[93m*****Waypoint*Basi*****\033[0m")
            if debug: print("\033[1mHedef noktasi:\033[0m %.2f, %.2f" % (hx, hy))
            if debug: print("\033[1mGuncel nokta:\033[0m %.2f, %.2f" % (adv_navi_guncel_x,adv_navi_guncel_y))
            UGBx, UGBy = UGBB(hx, hy, adv_navi_guncel_x, adv_navi_guncel_y)
            engel, ehx, ehy, yavas_bolge = BolgeKontrol(UGBx, UGBy)
            if ((hx, hy) == (-37.5, -6.5)) and ((ehx, ehy) == (-38.5, -7.5) or (-38.5, -6.5) or (-38.5, -5.5) or (-37.5, -5.5) or (-37.5, -7.5) or (-36.5, -5.5) or (-36.5, -6.5) or (-36.5, -7.5)):
                Waypoints.append((hx, hy, True, None, False, yavas_bolge))
                if debug: print(hx, hy)
                adv_navi_guncel_x, adv_navi_guncel_y = hx, hy
                if debug: print(adv_navi_guncel_x, adv_navi_guncel_y)
                if debug: print("adadadadsadsadsadsadssad")
                return adv_navi_guncel_x, adv_navi_guncel_y
            if debug: print("\033[1mEngel durumu ve konumu:\033[0m %s, %.2f, %.2f" % (engel, ehx, ehy))
            #Hedefe vardi
            if(ehx == hx and ehy == hy):
                engel = False
                adv_navi_guncel_x = hx
                adv_navi_guncel_y = hy
                Waypoints.append((hx, hy, True, None, False, yavas_bolge))
                if debug: print("Engel yok hedef atanan waypoint:")
                if debug: print(hx, hy)
                return adv_navi_guncel_x, adv_navi_guncel_y
            #Guzargah uzerinde engel varsa hedef noktasi engelden kacinacak sekilde guncelleniyor.
            elif engel == True:
                aci = NaviTargetAngle(ehx, ehy)
                if debug: print(123)
                khx, khy = EngelOnlem(aci, ehx, ehy, hx, hy)
                Waypoints.append((khx, khy, False, None, False, yavas_bolge))
                if debug: print("Engel var yol atanan waypoint:")
                if debug: print(khx, khy)
                adv_navi_guncel_x = khx
                adv_navi_guncel_y = khy

    def InilebilirBolgeyeGit():
        global adv_navi_guncel_x, adv_navi_guncel_y
        def EnYakinBolge():
            global adv_navi_guncel_x, adv_navi_guncel_y
            c = 10000000
            inilebilir_bolgeler = []
            if adv_navi_guncel_x > 0 and adv_navi_guncel_y > 0:
                for i in list(range(1, 51)):
                    for i2 in list(range(1, 51)):
                        bolge = cezeri.harita.bolge(i-0.5, i2-0.5)
                        if bolge.inilebilir == True:
                            inilebilir_bolgeler.append(bolge)
            if adv_navi_guncel_x < 0 and adv_navi_guncel_y > 0:
                for i in list(range(-49, 1)):
                    for i2 in list(range(1, 51)):
                        bolge = cezeri.harita.bolge(i-0.5, i2-0.5)
                        if bolge.inilebilir == True:
                            inilebilir_bolgeler.append(bolge)
            if adv_navi_guncel_x < 0 and adv_navi_guncel_y < 0:
                for i in list(range(-49, 1)):
                    for i2 in list(range(-49, 1)):
                        bolge = cezeri.harita.bolge(i-0.5, i2-0.5)
                        if bolge.inilebilir == True:
                            inilebilir_bolgeler.append(bolge)
            if adv_navi_guncel_x > 0 and adv_navi_guncel_y < 0:
                for i in list(range(1, 51)):
                    for i2 in list(range(-49, 1)):
                        bolge = cezeri.harita.bolge(i-0.5, i2-0.5)
                        if bolge.inilebilir == True:
                            inilebilir_bolgeler.append(bolge)

            for bolge in inilebilir_bolgeler:
                x = abs(bolge.enlem - adv_navi_guncel_x)
                y = abs(bolge.boylam - adv_navi_guncel_y)
                c2 = math.sqrt(x**2 + y**2)
                if c2 < c:
                    belirlenen_bolge = bolge
                    c = c2
            return belirlenen_bolge.enlem, belirlenen_bolge.boylam
        
        hx, hy = EnYakinBolge()
        engel = True
        if debug: print("\n\033[1m\033[91mAcil inis bolgesi:\033[0m")
        if debug: print(hx, hy)
        while engel == True:
            if debug: print("\n\033[1m\033[91m*****Waypoint*Basi*****\033[0m")
            if debug: print("\033[1mHedef noktasi:\033[0m %.2f, %.2f" % (hx, hy))
            if debug: print("\033[1mGuncel nokta:\033[0m %.2f, %.2f" % (adv_navi_guncel_x,adv_navi_guncel_y))
            UGBx, UGBy = UGBB(hx, hy, adv_navi_guncel_x, adv_navi_guncel_y)
            engel, ehx, ehy, yavas_bolge = BolgeKontrol(UGBx, UGBy)
            if ((hx, hy) == (-37.5, -6.5)) and ((ehx, ehy) == (-38.5, -7.5) or (-38.5, -6.5) or (-38.5, -5.5) or (-37.5, -5.5) or (-37.5, -7.5) or (-36.5, -5.5) or (-36.5, -6.5) or (-36.5, -7.5)):
                Waypoints.append((hx, hy, True, None, False, yavas_bolge))
                return adv_navi_guncel_x, adv_navi_guncel_y
            if debug: print("\033[1mEngel durumu ve konumu:\033[0m %s, %.2f, %.2f" % (engel, ehx, ehy))
            #Hedefe vardi
            if(ehx == hx and ehy == hy):
                engel = False
                adv_navi_guncel_x = hx
                adv_navi_guncel_y = hy
                Waypoints.append((hx, hy, True, None, False, yavas_bolge))
                if debug: print("Engel yok hedef atanan waypoint:")
                if debug: print(hx, hy)
                return adv_navi_guncel_x, adv_navi_guncel_y
            #Guzargah uzerinde engel varsa hedef noktasi engelden kacinacak sekilde guncelleniyor.
            elif engel == True:
                aci = NaviTargetAngle(ehx, ehy)
                if debug: print(234)
                khx, khy = EngelOnlem(aci, ehx, ehy, hx, hy)
                Waypoints.append((khx, khy, False, None, False, yavas_bolge))
                if debug: print("Engel var yol atanan waypoint:")
                if debug: print(khx, khy)
                adv_navi_guncel_x = khx
                adv_navi_guncel_y = khy

    def HastaneyeGit():
        global adv_navi_guncel_x, adv_navi_guncel_y
        if debug: print("**HastaneyeGit*fonksiyonu*calisti*")
        def EnYakinHastane():
            global adv_navi_guncel_x, adv_navi_guncel_y
            en_yakin_hastane_index_numarasi = 0
            en_yakin_hastane_mesafesi = 10000
            sayac = 0
            ####En yakin hastane aramasi####
            for i in cezeri.harita.hastaneler:
                ix = i.enlem
                iy = i.boylam
                a=ix-gx
                b=iy-gy
                c = math.sqrt(a**2 + b**2)
                if en_yakin_hastane_mesafesi > c:
                    en_yakin_hastane_mesafesi = c
                    en_yakin_hastane_index_numarasi = sayac
                sayac+=1
            hedef_hastane = cezeri.harita.hastaneler[en_yakin_hastane_index_numarasi]
            hx = hedef_hastane.enlem
            hy = hedef_hastane.boylam
            return hx, hy

        engel = True
        hx, hy = EnYakinHastane()
        if debug: print("\033[1m\033[91mGidilecek hastane:\033[0m")
        if debug: print(hx, hy)
        while engel == True:
            if debug: print("\033[1m\033[91m*****Waypoint*Basi*****\033[0m")
            if debug: print("\033[1mHedef noktasi:\033[0m %.2f, %.2f" % (hx, hy))
            if debug: print("\033[1mGuncel nokta:\033[0m %.2f, %.2f" % (adv_navi_guncel_x,adv_navi_guncel_y))
            UGBx, UGBy = UGBB(hx, hy, adv_navi_guncel_x, adv_navi_guncel_y)
            engel, ehx, ehy, yavas_bolge = BolgeKontrol(UGBx, UGBy)
            if ((hx, hy) == (-37.5, -6.5)) and ((ehx, ehy) == (-38.5, -7.5) or (-38.5, -6.5) or (-38.5, -5.5) or (-37.5, -5.5) or (-37.5, -7.5) or (-36.5, -5.5) or (-36.5, -6.5) or (-36.5, -7.5)):
                Waypoints.append((hx, hy, True, None, False, yavas_bolge))
                return adv_navi_guncel_x, adv_navi_guncel_y
            if debug: print("\033[1mEngel durumu ve konumu:\033[0m %s, %.2f, %.2f" % (engel, ehx, ehy))
            #Hedefe vardi
            if(ehx == hx and ehy == hy):
                engel = False
                adv_navi_guncel_x = hx
                adv_navi_guncel_y = hy
                Waypoints.append((hx, hy, True, None, False, yavas_bolge))
                if debug: print("Engel yok hedef atanan waypoint:")
                if debug: print(hx, hy)
                return adv_navi_guncel_x, adv_navi_guncel_y
            #Guzargah uzerinde engel varsa hedef noktasi engelden kacinacak sekilde guncelleniyor.
            elif engel == True:
                aci = NaviTargetAngle(ehx, ehy)
                if debug: print(345)
                khx, khy = EngelOnlem(aci, ehx, ehy, hx, hy)
                Waypoints.append((khx, khy, False, None, False, yavas_bolge))
                if debug: print("Engel var yol atanan waypoint:")
                if debug: print(khx, khy)
                adv_navi_guncel_x = khx
                adv_navi_guncel_y = khy

    def BaslangicaDon(baslangic_x, baslangic_y):
        global adv_navi_guncel_x, adv_navi_guncel_y
        print("*BaslangicaDon*Fonksiyonu*Calisti*")
        engel = True
        hx = baslangic_x
        hy = baslangic_y
        while engel == True:
            print("\033[1m\033[91m*****Waypoint*Basi*****\033[0m")
            print("\033[1mHedef noktasi:\033[0m %.2f, %.2f" % (hx, hy))
            print("\033[1mGuncel nokta:\033[0m %.2f, %.2f" % (adv_navi_guncel_x, adv_navi_guncel_y))
            UGBx, UGBy = UGBB(hx, hy, adv_navi_guncel_x, adv_navi_guncel_y)
            engel, ehx, ehy, yavas_bolge = BolgeKontrol(UGBx, UGBy)
            if ((hx, hy) == (-37.5, -6.5)) and ((ehx, ehy) == (-38.5, -7.5) or (-38.5, -6.5) or (-38.5, -5.5) or (-37.5, -5.5) or (-37.5, -7.5) or (-36.5, -5.5) or (-36.5, -6.5) or (-36.5, -7.5)):
                Waypoints.append((hx, hy, True, None, False, yavas_bolge))
                return adv_navi_guncel_x, adv_navi_guncel_y
            print("\033[1mEngel durumu ve konumu:\033[0m %s, %.2f, %.2f" % (engel, ehx, ehy))
            #Hedefe vardi
            if(ehx == hx and ehy == hy):
                engel = False
                adv_navi_guncel_x = hx
                adv_navi_guncel_y = hy
                Waypoints.append((hx, hy, True, None, False, yavas_bolge))
                print("Engel yok hedef atanan waypoint:")
                print(hx, hy)
                return adv_navi_guncel_x, adv_navi_guncel_y
            #Guzargah uzerinde engel varsa hedef noktasi engelden kacinacak sekilde guncelleniyor.
            elif engel == True:
                print(adv_navi_guncel_x, adv_navi_guncel_y, hx, hy)
                aci = NaviTargetAngle(hx, hy)
                print(456)
                khx, khy = EngelOnlem(aci, ehx, ehy, hx, hy)
                Waypoints.append((khx, khy, False, None, False, yavas_bolge))
                print("Engel var yol atanan waypoint:")
                print(khx, khy)
                adv_navi_guncel_x = khx
                adv_navi_guncel_y = khy
    
    def ChargeCheck(hedef_x, hedef_y, f_inis, mevcut_sarj, kalkis, kalan_hedefler):
        global adv_navi_guncel_x, adv_navi_guncel_y
        req_charge = 0
        hedef_sarj_istasyonu = False
        sona_yetiyor = False
        #Degisken kopyalama
        cc_adv_navi_guncel_x, cc_adv_navi_guncel_y = adv_navi_guncel_x, adv_navi_guncel_y
        cc_fhx, cc_fhy = hedef_x, hedef_y
        cc_mevcut_sarj = mevcut_sarj
        cc_hedefc = hedefc

        #Mevcut konumdan hedefe ne kadar sarj gerekiyor
        if kalkis: req_charge += 10 #Kalkis yapacak mi
        while not (cc_fhx == adv_navi_guncel_x and cc_fhy == adv_navi_guncel_y):
            hx, hy = cc_fhx, cc_fhy
            if int(cc_fhx) == int(adv_navi_guncel_x) and int(cc_fhy) == int(adv_navi_guncel_y):
                break
            UGBx, UGBy = UGBB(hx, hy, adv_navi_guncel_x, adv_navi_guncel_y)
            engel, ehx, ehy, yavas_bolge = BolgeKontrol(UGBx, UGBy)
            if(ehx == hx and ehy == hy):
                engel = False
                inis = f_inis
            elif ((hx, hy) == (-37.5, -6.5)) and ((ehx, ehy) == (-38.5, -7.5) or (-38.5, -6.5) or (-38.5, -5.5) or (-37.5, -5.5) or (-37.5, -7.5) or (-36.5, -5.5) or (-36.5, -6.5) or (-36.5, -7.5)):
                inis = True
                engel = False
            if engel == True:
                aci = NaviTargetAngle(hx, hy)
                hx, hy = EngelOnlem(aci, ehx, ehy, hx, hy)
                inis = False
            if debug: print("Engel durum, konum:")
            if debug: print(engel, ehx, ehy)
            if debug: print("Guncel konum:")
            if debug: print(adv_navi_guncel_x, adv_navi_guncel_y)
            if debug: print("Hedef konum:")
            if debug: print(hx, hy)

            a = abs(hx - adv_navi_guncel_x)
            b = abs(hy - adv_navi_guncel_y)
            c = math.sqrt(a**2 + b**2)
            t = (c * 20) / 12
            req_charge += ((t * 1.3) + 1) #((Sefer suresi) * saniyede harcanan sarj) + donuste harcanan sarj)
            if inis: req_charge += 2 #Inis islemi %2 sarj harcar

            if debug: print("Gerekli sarj:")
            if debug: print(req_charge)
            if debug: print("*****************")
            adv_navi_guncel_x = hx
            adv_navi_guncel_y = hy
        
            cc_mevcut_sarj -= req_charge
            req_charge = 0
            cc_hedefc-=1
        
        #Hedeften son hedefe yetiyor mu
        cc_kalan_hedefler = kalan_hedefler[:]
        cc_fhx2, cc_fhy2 = cc_fhx, cc_fhy
        cc_mevcut_sarj2 = cc_mevcut_sarj
        adv_navi_guncel_x2, adv_navi_guncel_y2 = adv_navi_guncel_x, adv_navi_guncel_y
        if cezeri.baslangica_don: baslangic = True
        else: baslangic = False
        while (cc_hedefc > 0) or (baslangic):
            print(cc_hedefc)
            if cc_hedefc > 0: cc_fhx, cc_fhy, f_inis, hedef = EnYakinHedef(adv_navi_guncel_x2, adv_navi_guncel_y2, cc_kalan_hedefler)
            else:
                cc_fhx, cc_fhy, f_inis = baslangic_x, baslangic_y, True
                baslangic = True
            while not (cc_fhx == adv_navi_guncel_x2 and cc_fhy == adv_navi_guncel_y2):
                hx, hy = cc_fhx, cc_fhy
                if int(cc_fhx) == int(adv_navi_guncel_x2) and int(cc_fhy) == int(adv_navi_guncel_y2):
                    break
                UGBx, UGBy = UGBB(hx, hy, adv_navi_guncel_x2, adv_navi_guncel_y2)
                engel, ehx, ehy, yavas_bolge = BolgeKontrol(UGBx, UGBy)
                if(ehx == hx and ehy == hy):
                    engel = False
                    inis = f_inis
                elif ((hx, hy) == (-37.5, -6.5)) and ((ehx, ehy) == (-38.5, -7.5) or (-38.5, -6.5) or (-38.5, -5.5) or (-37.5, -5.5) or (-37.5, -7.5) or (-36.5, -5.5) or (-36.5, -6.5) or (-36.5, -7.5)):
                    inis = True
                    engel = False
                if engel == True:
                    aci = NaviTargetAngle(hx, hy)
                    hx, hy = EngelOnlem(aci, ehx, ehy, hx, hy)
                    inis = False

                a = abs(hx - adv_navi_guncel_x2)
                b = abs(hy - adv_navi_guncel_y2)
                c = math.sqrt(a**2 + b**2)
                t = (c * 20) / 12
                req_charge += ((t * 1.3) + 1) #((Sefer suresi) * saniyede harcanan sarj) + donuste harcanan sarj)
                if inis: req_charge += 2 #Inis islemi %2 sarj harcar

                adv_navi_guncel_x2 = hx
                adv_navi_guncel_y2 = hy
                if baslangic == False: cc_kalan_hedefler.remove(hedef)

            
            cc_mevcut_sarj2 -= req_charge
            req_charge = 0
            cc_hedefc-=1
            if (cc_hedefc <= 0) and baslangic: break


        if cc_mevcut_sarj2 > 20: sona_yetiyor = True
        cc_fhx, cc_fhy = cc_fhx2, cc_fhy2

        print("sona yetiyor", sona_yetiyor, cc_mevcut_sarj2)
        #Hedef sarj istasyonu mu sorgulama
        for i in cezeri.harita.sarj_istasyonlari:
            if i.enlem == cc_fhx and i.boylam == cc_fhy:
                hedef_sarj_istasyonu = True
                break
        print("hedefc", hedefc)

        #Hedef noktadan sarj istasyonuna ne kadar sarj gerekiyor
        if ((hedefc >= 1) and (hedef_sarj_istasyonu == False)) and (sona_yetiyor == False): #Hedef son hedef veya sarj istasyonu degilse uygulanacak
            if debug: print("Hedeften istasyona>>>>>>>>>>>")
            if inis == True: req_charge += 10
            cc_fhx, cc_fhy = EnYakinIstasyon(adv_navi_guncel_x, adv_navi_guncel_y)
            if debug: print("En yakin istasyon:")
            if debug: print(cc_fhx, cc_fhy)
            while not (cc_fhx == adv_navi_guncel_x and cc_fhy == adv_navi_guncel_y):
                hx, hy = cc_fhx, cc_fhy
                if int(cc_fhx) == int(adv_navi_guncel_x) and int(cc_fhy) == int(adv_navi_guncel_y): break
                UGBx, UGBy = UGBB(hx, hy, adv_navi_guncel_x, adv_navi_guncel_y)
                engel, ehx, ehy, yavas_bolge = BolgeKontrol(UGBx, UGBy)
                if(ehx == hx and ehy == hy):
                    engel = False
                    inis = f_inis
                elif ((hx, hy) == (-37.5, -6.5)) and ((ehx, ehy) == (-38.5, -7.5) or (-38.5, -6.5) or (-38.5, -5.5) or (-37.5, -5.5) or (-37.5, -7.5) or (-36.5, -5.5) or (-36.5, -6.5) or (-36.5, -7.5)):
                    inis = True
                    engel = False
                if engel == True:
                    aci = NaviTargetAngle(hx, hy)
                    hx, hy = EngelOnlem(aci, ehx, ehy, hx, hy)
                    inis = False

                if debug: print("Engel durum, konum:")
                if debug: print(engel, ehx, ehy)
                if debug: print("Guncel konum:")
                if debug: print(adv_navi_guncel_x, adv_navi_guncel_y)
                if debug: print("Hedef konum:")
                if debug: print(hx, hy)
            
                a = abs(hx - adv_navi_guncel_x)
                b = abs(hy - adv_navi_guncel_y)
                c = math.sqrt(a**2 + b**2)
                t = (c * 20) / 12
                req_charge += ((t * 1.3) + 1) #((Sefer suresi) * saniyede harcanan sarj) + donuste harcanan sarj)
                
                adv_navi_guncel_x = hx
                adv_navi_guncel_y = hy
            req_charge += 2 #Inis islemi %2 sarj harcar
            cc_mevcut_sarj2 = cc_mevcut_sarj
            cc_mevcut_sarj2 -= req_charge
        else: cc_mevcut_sarj2 = cc_mevcut_sarj
        adv_navi_guncel_x, adv_navi_guncel_y = cc_adv_navi_guncel_x, cc_adv_navi_guncel_y

        if cc_mevcut_sarj2 <= 20: return cc_mevcut_sarj, False
        else: return cc_mevcut_sarj, True

    if motor_stat == 2:
        motor_stat_2 = 2
        InilebilirBolgeyeGit()
        return Waypoints

    if emergency == 2:
        emergency_2 = 2
        HastaneyeGit()
        return Waypoints

    for hedef in kalan_hedefler:
        hedefc+=1
    if debug: print("Gidilecek toplam hedef: %.2f" % hedefc)

    while hedefc != 0:
        cezeri.bekle(0.1)
        if debug: print("\n\033[1m\033[95m*****Waypoint*Basi*****\033[0m")
        hx, hy, inis, hedef = EnYakinHedef(adv_navi_guncel_x, adv_navi_guncel_y, kalan_hedefler)
        f_inis = inis
        fhx, fhy = hx, hy
        sira = 1
        if debug: print("\033[1mHedef noktasi:\033[0m %.2f, %.2f" % (hx, hy))
        if debug: print("\033[1mGuncel nokta:\033[0m %.2f, %.2f" % (adv_navi_guncel_x,adv_navi_guncel_y))
        if debug: print("\033[1mMevcut sarj:\033[0m %.2f" % (mevcut_sarj))
        #Guncel noktadan hedef noktaya sarj yetme durumu kontrolu
        mevcut_sarj, CChech = ChargeCheck(hx, hy, f_inis, mevcut_sarj, kalkis, kalan_hedefler)
        if debug: print("\033[1mSarj istasyonuna gitme durumu (False: gidilecek):", CChech)
        if debug: print("\033[1mHedefe gidildikten sonra kalacak sarj:\033[0m %.2f" % (mevcut_sarj))
        if CChech == False:
            if debug: print("Sarj istasyonuna gidilecek")
            mevcut_sarj = 100
            IstasyonaGit(hx, hy)
            if debug: print("AdvNavis: ", adv_navi_guncel_x, adv_navi_guncel_y)
            
        while not (fhx == adv_navi_guncel_x and fhy == adv_navi_guncel_y):
            cezeri.bekle(0.1)
            if debug: print("\n\033[1m\033[95m*****Waypoint*Basi*****\033[0m")
            hx, hy = fhx, fhy
            if debug: print("\033[1mHedef noktasi:\033[0m %.2f, %.2f" % (hx, hy))
            if debug: print("\033[1mGuncel nokta:\033[0m %.2f, %.2f" % (adv_navi_guncel_x,adv_navi_guncel_y))
            if int(fhx) == int(adv_navi_guncel_x) and int(fhy) == int(adv_navi_guncel_y):
                kalan_hedefler.remove(hedef)
                hedefc-=1
                continue
            UGBx, UGBy = UGBB(hx, hy, adv_navi_guncel_x, adv_navi_guncel_y)
            engel, ehx, ehy, yavas_bolge = BolgeKontrol(UGBx, UGBy)
            if ((hx, hy) == (-37.5, -6.5)) and ((ehx, ehy) == (-38.5, -7.5) or (-38.5, -6.5) or (-38.5, -5.5) or (-37.5, -5.5) or (-37.5, -7.5) or (-36.5, -5.5) or (-36.5, -6.5) or (-36.5, -7.5)):
                Waypoints.append((hx, hy, True, None, False, yavas_bolge))
                engel = False
            elif (((adv_navi_guncel_x, adv_navi_guncel_y) == (-37.5, -6.5)) and ((ehx, ehy) == (-38.5, -7.5) or (-38.5, -6.5) or (-38.5, -5.5) or (-37.5, -5.5) or (-37.5, -7.5) or (-36.5, -5.5) or (-36.5, -6.5) or (-36.5, -7.5))):
                if hx <= -37.5: Waypoints.append((-39.5, -6.5, False, None, False, yavas_bolge))
                elif hx > -37.5: Waypoints.append((-35.5, -6.5, False, None, False, yavas_bolge))
                engel = False
            elif(ehx == hx) and (ehy == hy): #Hedefe giderken engel var mi sorgulaniyor.
                engel = False
                inis = f_inis
            if debug: print("\033[1mEngel durumu ve konumu:\033[0m %s, %.2f, %.2f" % (engel, ehx, ehy))
            #Guzargah uzerinde engel varsa hedef noktasi engelden kacinacak sekilde guncelleniyor.
            if engel == True:
                aci = NaviTargetAngle(hx, hy)
                hx, hy = EngelOnlem(aci, ehx, ehy, hx, hy)
                if debug: print("\033[1mKacinilan bolge:\033[0m %.2f, %.2f" % (hx, hy))
                inis = False
            
            #Hedef sarj istasyonu mu kotrol edilir sarj istasyonu ise sarj 100 yapilir
            hedef_sarj_istasyonu = False
            for i in cezeri.harita.sarj_istasyonlari:
                ix = i.enlem
                iy = i.boylam
                if ix == hx and iy == hy:
                    hedef_sarj_istasyonu = True
                    inis = True
            if hedef_sarj_istasyonu == True:
                mevcut_sarj = 100

            kalkis = inis
            Waypoints.append((hx, hy, inis, hedef, False, yavas_bolge))
            adv_navi_guncel_x = hx
            adv_navi_guncel_y = hy
            if debug: print("\033[1mYeni Waypoint:\033[0m %s, %.2f, %.2f" % (engel, adv_navi_guncel_x, adv_navi_guncel_y))
            if (engel == False) and (hedef != None):
                kalan_hedefler.remove(hedef)
                hedefc-=1

    if cezeri.baslangica_don:
        BaslangicaDon(baslangic_x, baslangic_y)
    if debug: print("\033[1m\033[92m*Waypointler*Ayarlandi\033[0m*\n***********************")
    return Waypoints

#Yerel bolgelerden hangisinin aracin onu oldugunu bulur.
def YerelYon(sdeg):
    if sdeg > 180: sdeg = sdeg-360
    if -22.5 <= sdeg < 22.5: bolge = 5
    elif -67.5 <= sdeg < -22.5: bolge = 8
    elif -112.5 <= sdeg < -67.5: bolge = 7
    elif -157.5 <= sdeg < -112.5: bolge = 6
    elif sdeg < -157.5 or sdeg > 157.5: bolge = 3
    elif 112.5 <= sdeg < 157.5: bolge = 0
    elif 67.5 <= sdeg < 112.5: bolge = 1
    elif 22.5 <= sdeg < 67.5: bolge = 2
    return bolge

#Hedef acisini, donus hizini ve sabitleme sayisini alarak araci donurur.
def SetYaw(hdeg):
    RoutinCheck()
    global cal_degree, ldeg
    sdeg = Data_Center("degree")
    if magneto_stat == 1:
        if sdeg < hdeg:
            cezeri.don(5)
            while (hdeg-sdeg) > 180: sdeg = Data_Center("degree")
            cezeri.don(1)
            while (hdeg-sdeg) > 100: sdeg = Data_Center("degree")
            cezeri.don(0.5)
            while (hdeg-sdeg) > 50: sdeg = Data_Center("degree")
            cezeri.don(0.1)
            while (hdeg-sdeg) > 10: sdeg = Data_Center("degree")
            cezeri.don(0.03)
            while (hdeg-sdeg) > 1: sdeg = Data_Center("degree")
            cezeri.don(0.01)
            while (hdeg-sdeg) > 0.05:
                sdeg = Data_Center("degree")
                if hdeg == 180: break
            cezeri.don(0.002)
            while (hdeg-sdeg) > 0.001:
                sdeg = Data_Center("degree")
                if hdeg == 180: break
            cezeri.dur()
        elif sdeg > hdeg:
            cezeri.don(-5)
            while -(hdeg-sdeg) > 180: sdeg = Data_Center("degree")
            cezeri.don(-1)
            while -(hdeg-sdeg) > 100: sdeg = Data_Center("degree")
            cezeri.don(-0.5)
            while -(hdeg-sdeg) > 50: sdeg = Data_Center("degree")
            cezeri.don(-0.1)
            while -(hdeg-sdeg) > 10: sdeg = Data_Center("degree")
            cezeri.don(-0.03)
            while -(hdeg-sdeg) > 1: sdeg = Data_Center("degree")
            cezeri.don(-0.01)
            while -(hdeg-sdeg) > 0.05:
                sdeg = Data_Center("degree")
                if hdeg == -180: break
            cezeri.don(-0.002)
            while -(hdeg-sdeg) > 0.001:
                sdeg = Data_Center("degree")
                if hdeg == -180: break
            cezeri.dur()
        cal_degree = hdeg
        print("ldegesit")
        ldeg = Data_Center("degree")
        print(ldeg)
        return
    
    else:
        if debug: print("Ariza Donusu")
        if debug: print(hdeg)
        if debug: print("**********")
        if debug: print(cal_degree)
        yaw_deg = abs(hdeg - cal_degree)
        if debug: print(yaw_deg)
        yaw_time = abs((abs(yaw_deg) / (0.1 * (180/math.pi)))/math.pi)
        if yaw_time > 10: yaw_time += yaw_time/90
        if yaw_time < 2: yaw_time -= yaw_time/10
        if debug: print(yaw_time)
        if hdeg > cal_degree: cezeri.don(0.1)
        elif hdeg < cal_degree: cezeri.don(-0.1)
        cezeri.bekle(yaw_time)
        cezeri.dur()
        cal_degree = hdeg
        ldeg = hdeg
    return

#Aracin kalkis yapmasini saglar.
def TakeOff(salt):
    alt = Data_Center("irtifa")
    while alt < salt:
        alt = Data_Center("irtifa")
        cezeri.yukari_git(cezeri.HIZLI)
    cezeri.dur()

#Aracin isin yapmasini saglar.
def Land(son):
    if debug: print("inis basliyor")
    we = False
    if Data_Center("yerden_yukseklik") >= 15 or Data_Center("yerden_yukseklik") <= 0:
        while we == False:
            RoutinCheck()
            cezeri.asagi_git(cezeri.HIZLI)
            if Data_Center("yerden_yukseklik") <= 15:
                we = True
    if Data_Center("yerden_yukseklik") < 15 and Data_Center("yerden_yukseklik") != 0:
        cezeri.asagi_git(cezeri.YAVAS)
    cezeri.bekle(8)
    for i in cezeri.harita.sarj_istasyonlari:
        if i.enlem == hx and i.boylam == hy:
            while Data_Center("batarya") != 100:
                cezeri.bekle(0.25)
            break

#Hedef acisini hesaplar.
def TargetAngle(hx,hy):
    gx, gy = Data_Center("lokasyon")
    x=hx-gx
    y=hy-gy
    if debug: print(x,y)

    #Bu 3. bolge icindir diger bolgeler test edilmelidir
    if y == 0:
        y+=0.0000000000000000000000000000001
    if x ==0:
        x+=0.0000000000000000000000000000001
    
    xy = y / x
    angleB = math.degrees(math.atan(xy))
    if debug: print("assdf", angleB)
    if x > 0 and y < 0: #4. bolge
        angleB = angleB
    elif x < 0 and y < 0: #3. bolge
        angleB = angleB - 180
    elif x < 0 and y > 0: #2. bolge
        angleB = angleB + 180
    elif x > 0 and y > 0: #1. bolge
        angleB = angleB
    #print("angleB", angleB)
    return angleB

#Aracin hedef acilara kadar ilerlemesini saglar.
def Forwt(hx, hy, hiz, gx, gy):
    def Traffic():
        yon = YerelYon(Data_Center("degree"))
        if yon==0: sol, sag = 3, 1
        elif yon == 1: sol, sag = 0, 2
        elif yon == 2: sol, sag = 1, 5
        elif yon == 5: sol, sag = 2, 8
        elif yon == 8: sol, sag = 5, 7
        elif yon == 7: sol, sag = 8, 6
        elif yon == 6: sol, sag = 7, 3
        elif yon == 3: sol, sag = 6, 0

        if (cezeri.yerel_harita[yon].trafik or cezeri.yerel_harita[sol].trafik or cezeri.yerel_harita[sag].trafik):
            s1 = cezeri.zaman
            while cezeri.yerel_harita[yon].trafik or cezeri.yerel_harita[sol].trafik or cezeri.yerel_harita[sag].trafik: cezeri.geri_git(cezeri.HIZLI)
            s2 = cezeri.zaman
            cezeri.dur()
            cezeri.bekle(random.uniform(2, 3))
            cezeri.ileri_git(cezeri.HIZLI)
            return (s2-s1)*2
        return 0

    if debug: print("Forwt fonksiyonu calisti")
    global loc_stat, rota, cal_x, cal_y, motor_stat, motor_stat_2, emergency, emergency_2
    arrive = False
    irtifasetlendi = False
    gidilen_sure, ilk_zaman, son_zaman = 0, 0, 0
    x = hx - gx
    y = hy - gy
    c = (math.sqrt(x**2 + y**2))*20

    if hiz == 1:
        time = c/4
        cezeri.ileri_git(cezeri.YAVAS)
    elif hiz == 2:
        time = c/8
        cezeri.ileri_git(cezeri.ORTA)
    elif hiz == 3:
        time = c/12
        cezeri.ileri_git(cezeri.HIZLI)
    ilk_zaman = cezeri.zaman
    gidilecek_sure2 = time
    asa=True
    ttime = 0
    ttimes1, ttimes2 = 0, 0
    while arrive==False:
        ttimes1 = cezeri.zaman
        RoutinCheck()
        if ttime <= 0: ttime = Traffic()
        else:
            if ttimes2 != 0: ttime -= ttimes2 - ttimes1
        
        #GNSS arizasinda yapilacak islem
        son_zaman = cezeri.zaman
        if loc_stat == 2:
            gidilen_sure = son_zaman - ilk_zaman
            gidilecek_sure = time-gidilen_sure
            while gidilecek_sure > 0:
                ft = cezeri.zaman
                Traffic()
                RoutinCheck()
                if hiz == 1:
                    cezeri.ileri_git(cezeri.YAVAS)
                elif hiz == 2:
                    cezeri.ileri_git(cezeri.ORTA)
                elif hiz == 3:
                    cezeri.ileri_git(cezeri.HIZLI)
                """if (rota == True) or (motor_stat == 2 and motor_stat_2 == 1) or (emergency == 2 and emergency_2 == 1):
                    #cal_x, cal_y = 
                    if debug: print("cikti")
                    break"""
                lt = cezeri.zaman
                gidilecek_sure-=(lt-ft)
            cal_x, cal_y = hx, hy
            return

        if (rota == True) or (motor_stat == 2 and motor_stat_2 == 1) or (emergency == 2 and emergency_2 == 1):
            if debug: print("cikti")
            break

        if hiz == 1:
            cezeri.ileri_git(cezeri.YAVAS)
        elif hiz == 2:
            cezeri.ileri_git(cezeri.ORTA)
        elif hiz == 3:
            cezeri.ileri_git(cezeri.HIZLI)

        gx, gy = Data_Center("lokasyon")
        if ((irtifasetlendi == False) and (hx, hy) == (-37.5, -6.5)) and (int(gx), int(gy)) in [(-38, -7), (-38, -6), (-38, -5), (-37, -5), (-37, -7), (-36, -5), (-36, -6), (-36, -7)]:
                cezeri.dur()
                TakeOff(155)
                irtifasetlendi = True
                cezeri.ileri_git(cezeri.YAVAS)
        if ((irtifasetlendi == False) and (hx, hy) != (-37.5, -6.5)) and (int(gx), int(gy)) in [(-38, -7), (-38, -6), (-38, -5), (-37, -5), (-37, -7), (-36, -5), (-36, -6), (-36, -7)]:
                cezeri.bekle(0.5)
                cezeri.dur()
                alt = Data_Center("irtifa")
                while alt > 100:
                    alt = Data_Center("irtifa")
                    cezeri.asagi_git(cezeri.HIZLI)
                cezeri.dur()
                irtifasetlendi = True
                if hiz == 1: cezeri.ileri_git(cezeri.YAVAS)
                elif hiz == 2: cezeri.ileri_git(cezeri.ORTA)
                elif hiz == 3: cezeri.ileri_git(cezeri.HIZLI)
        
        #print("AA1")
        gx, gy = Data_Center("lokasyon")
        #print(hx, hy, gx, gy)
        if (int(gx) == int(hx) and int(gy) == int(hy)) or (gidilecek_sure2 <= 0):
            if debug: print("hedefe varildi")
            cezeri.dur()
            cal_x, cal_y = Data_Center("lokasyon")
            arrive=True
            cezeri.bekle(0.05)
        if asa == True:
            asa = False
            if debug: print(cezeri.zaman)

#Surekli olarak kontrol edilmesi ve onlem alinmasi gereken durumlari kontrol eder.
def RoutinCheck():
    cezeri.aktif()
    #Ucus sirasinde meydana gelen hatalari tespit eder.
    def Stim():
        global loc_stat, motor_stat, lgx, lgy
        hatac=0
        hata=[]
        if (cezeri.gnss.hata) or (cezeri.gnss.enlem == 0 and cezeri.gnss.boylam == 0 and cezeri.gnss.irtifa == 0):
            hatac+=1
            hata.append(109)
        if (cezeri.gnss.spoofing) or (((cezeri.gnss.irtifa+2 < Data_Center("irtifa")) or (cezeri.gnss.irtifa-2 > Data_Center("irtifa"))) and ((lgx+1 < cezeri.gnss.enlem or lgx-1 > cezeri.gnss.enlem) or (lgy+1 < cezeri.gnss.boylam or lgy-1 > cezeri.gnss.boylam))):
            hatac+=1
            hata.append(101)
        lgx, lgy = Data_Center("lokasyon")
        if (cezeri.barometre.hata) or (cezeri.lidar.mesafe > 0 and cezeri.barometre.irtifa == 0) or (cezeri.radar.mesafe > 0 and cezeri.barometre.irtifa == 0):
            hatac+=1
            hata.append(102)
        if (cezeri.radar.hata) or (cezeri.lidar.mesafe > 0 and cezeri.radar.mesafe == 0):
            hatac+=1
            hata.append(103)
        if cezeri.lidar.hata:
            hatac+=1
            hata.append(104)
        if cezeri.imu.hata:
            hatac+=1
            hata.append(105)
        if (cezeri.manyetometre.hata) or ((ldeg+5 < (cezeri.manyetometre.veri * (180/math.pi))) or (ldeg-5 > (cezeri.manyetometre.veri * (180/math.pi)))):
            hatac+=1
            hata.append(106)
        if cezeri.batarya.hata:
            hatac+=1
            hata.append(107)
        if cezeri.motor.hata:
            hatac+=1
            hata.append(108)
        for motor in cezeri.motor.veri:
            if motor == 0 and motor_stat == 1:
                hatac+=1
                hata.append(110)
                break
        if cezeri.acil_durum == True and emergency == 1:
            hatac+=1
            hata.append(111)
        if hatac != 0:
            HataOnlem(hata)
    
    def RotaCheck():
        global baslangic_hedefler, gidilecek_hedefler, rota, gidilen_hedefler, motor_stat
        kontrol_hedefleri = []
        for hedef in cezeri.hedefler:
            kontrol_hedefleri.append(hedef.bolge.enlem)
            kontrol_hedefleri.append(hedef.bolge.boylam)
        if kontrol_hedefleri != baslangic_hedefler and motor_stat == 1:
            if debug: print("Uyari: Rota degisti")
            cezeri.dur()
            baslangic_hedefler = kontrol_hedefleri
            gidilecek_hedefler = []
            for hedef in cezeri.hedefler:
                gidilecek_hedefler.append(hedef)
            gidilecek_hedefler = list(set(gidilecek_hedefler) - set(gidilen_hedefler))
            rota = True
    
    hata = []
    hata = Stim()
    RotaCheck()
    
    return hata

#Tespit edilen hatalara onlem alir.
def HataOnlem(hata):
    global loc_stat, baro_stat, motor_stat, emergency, magneto_stat, radar_stat
    if (101 in hata or 109 in hata) and loc_stat == 1:
        if debug: print("GNSS hatasi duzeltildi!!!")
        loc_stat = 2
    if 102 in hata and baro_stat == 1:
        if debug: print("Barometre hatasi duzeltildi!!!")
        baro_stat = 2
        #barometre: kalkista sure kulln iniste radardan veri gelene kadar hizli.
    if 110 in hata and motor_stat == 1:
        if debug: print("Motor arizasina onlem aliniyor!!!")
        motor_stat = 2
        cezeri.dur()
    if 111 in hata and emergency == 1:
        if debug: print("Acil durum! En yakin hastaneye gidiliyor!")
        emergency = 2
    if 106 in hata and magneto_stat == 1:
        if debug: print("Manyetometre hatasi duzeltildi!!!")
        magneto_stat = 2
        #manyetometre
    if 103 in hata and radar_stat == 1:
        if debug: print("Radar hatasi duzeltildi!!!")
        radar_stat = 2
        #radar
    """if 104 in hata:
        #lidar:
    if 105 in hata:
        #imu:
    if 107 in hata:
        #batarya
    if 108 in hata:
        #motor"""

#Cagirilan veriyi dondurur. Cagirilabilen veriler (irtifa, lokasyon, batarya)
def Data_Center(istenilen_veri):
    global cal_degree
    cezeri.aktif()
    if istenilen_veri == "irtifa":
        if baro_stat == 1:
            irtifa = cezeri.barometre.irtifa
        elif baro_stat == 2:
            irtifa = cezeri.gnss.irtifa
        return irtifa
    elif istenilen_veri == "lokasyon":
        if loc_stat == 1:
            return cezeri.gnss.enlem, cezeri.gnss.boylam
        elif loc_stat == 2:
            return cal_x, cal_y
    
    elif istenilen_veri == "batarya":
        return cezeri.batarya.veri
    
    elif istenilen_veri == "yerden_yukseklik":
        x, y = Data_Center("lokasyon")
        alt = Data_Center("irtifa")
        yerden_yukseklik = alt - cezeri.harita.bolge(x, y).yukselti
        if alt <= 0:
            if cezeri.radar.mesafe <= 0:
                yerden_yukseklik = 50
            else:
                yerden_yukseklik = cezeri.radar.mesafe
        if radar_stat == 2:
            if cezeri.lidar.mesafe <= 0:
                yerden_yukseklik = 50
            else:
                yerden_yukseklik = cezeri.lidar.mesafe
        return yerden_yukseklik

    elif istenilen_veri == "degree":
        if magneto_stat == 1:
            degree = cezeri.manyetometre.veri * 180 / math.pi
        else:
            degree = cal_degree
        return degree

"""**********************************************************************************************************************************"""
#Setup*bazi_degiskenlere_deger_atama****************************************************************************************************
"""**********************************************************************************************************************************"""
baslangic_x, baslangic_y = Data_Center("lokasyon") #Aracin ilk kalkis yaptigi konumu tutar baslangica donulmesi gerektiginde kullanilir.

"""**********************************************************************************************************************************"""
#Main*Code******************************************************************************************************************************
"""**********************************************************************************************************************************"""

while cezeri.aktif():
    if(setup == True):
        for hedef in cezeri.hedefler:
            gidilecek_hedefler.append(hedef)
            baslangic_hedefler.append(hedef.bolge.enlem)
            baslangic_hedefler.append(hedef.bolge.boylam)
    setup = False
    TakeOff(100)
    Waypoints = AdvNavi()
    sira = 0
    if debug: print("\033[1m\033[92m******Waypointler******\033[0m")
    result = [x[:3] for x in Waypoints]
    if debug: print(result)
    if debug: print("***********************\n\033[1m\033[92m*****Sefer*Basliyor*****\033[0m")
    uzunluk = len(Waypoints)
    while uzunluk != 0:
        gx, gy = Data_Center("lokasyon")
        if (int(gx), int(gy)) == (-37, -6): #Ucus irtifasindan yuksek olan sarj istasyonu icin.
            TakeOff(155)
        else:
            TakeOff(100)
        
        if debug: print("\033[1m\033[95mWaypoint sirasi:\033[0m")
        if debug: print(sira)
        hx, hy, inis, hedef, hedef_hedef, yavas_bolge = Waypoints[sira]
        hiz = 3
        if yavas_bolge: hiz = 1

        uzunluk-=1
        sira+=1
        if debug: print(Data_Center("lokasyon"),hx, hy)
        angle = TargetAngle(hx, hy)
        if debug: print("Donus Acisi:")
        if debug: print(angle)
        SetYaw(angle)
        if debug: print("Guncel waypoint:")
        if debug: print(gx, gy)
        if debug: print("Gidilen waypoint:")
        if debug: print(hx, hy, inis)
        Forwt(hx, hy, hiz, gx, gy)
        if hedef_hedef == True:
            gidilen_hedefler.append(hedef)
        if (rota == True) or (motor_stat == 2 and motor_stat_2 == 1) or (emergency == 2 and emergency_2 == 1):
            del Waypoints[:]
            rota = False
            break
            cezeri.bekle(3)
        cezeri.dur()
        cezeri.bekle(0.25)
        if inis == True:
            if uzunluk == 0: son = True
            else: son =False
            Land(son)
            if uzunluk == 0:
                cezeri.dur()
        if debug: print("**********************")