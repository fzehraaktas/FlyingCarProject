def hiz_kontrol(self,konum1_enlem,konum1_boylam,konum2_enlem,konum2_boylam):  

    yavas_kontrol =[]
 
    if konum1_enlem < konum2_enlem:
        x=+1
        a=int(round((konum2_enlem - konum1_enlem)))
        
    else:
        x=-1
        a=int(round((konum1_enlem - konum2_enlem)))
        

    if konum1_boylam < konum2_boylam:
        y=+1
        b=int(round((konum2_boylam - konum1_boylam)))
        
    else:
        y=-1
        b=int(round((konum1_boylam - konum2_boylam)))


    for i in range (0,a,1):
        konum1_enlem += x 
        yavas_boylam = konum1_boylam
        for j in range(0,b,1):
            yavas_boylam += y
            yavas_kontrol.append([konum1_enlem,yavas_boylam])
        
        
    return yavas_kontrol

print(hiz_kontrol(11,2,20,-6))