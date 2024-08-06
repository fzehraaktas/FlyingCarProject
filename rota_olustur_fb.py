import numpy as np
import itertools

class Cezeri:
    def __init__(self) :

    def rota_olustur(self,hedefler,oncelik,bitis):
        if bitis==None:
            bitis_koordinat = []
            bitis_koordinat = np.array(bitis_koordinat)
        else:
            bitis_koordinat = np.array(bitis)

        baslangic_koordinat = np.array(self.kalkis_konum)
        
        hedef_kombinler = []
        tum_kombinler = []
        tuples =[]
        kombin = []
        mesafeler = []
        hedefler = np.array(hedefler)
        oncelik = np.array(oncelik)

        if len(hedefler) == 0 and len(bitis_koordinat) != 0:
            tum_hedefler = np.vstack((baslangic_koordinat,bitis_koordinat))
        elif len(hedefler) != 0 and len(bitis_koordinat) == 0:
            tum_hedefler = np.vstack((baslangic_koordinat,hedefler))
        elif len(hedefler) != 0 and len(bitis_koordinat) != 0 :
            tum_hedefler = np.vstack((baslangic_koordinat,hedefler,bitis_koordinat))
        
        for i in range(len(tum_hedefler)):
            mesafe = []
            for j in range(len(tum_hedefler)):
                """if self.hiz_kontrol(tum_hedefler[i][0],tum_hedefler[i][1],tum_hedefler[j][0],tum_hedefler[j][1]) == True :
                    x = np.sqrt((tum_hedefler[i][0] - tum_hedefler[j][0]) ** 2 + (tum_hedefler[i][1] - tum_hedefler[j][1]) ** 2)
                    a = 1.7*x 
                else:"""
                
                a = np.sqrt((tum_hedefler[i][0] - tum_hedefler[j][0]) ** 2 + (tum_hedefler[i][1] - tum_hedefler[j][1]) ** 2)
                mesafe.append(a)

            mesafeler.append(mesafe)

        mesafeler = np.array(mesafeler)

        def oncelik_index(oncelik,bitis_koordinat):

            if len(oncelik)>0:
                num_priorities = oncelik.max()
                indexes = []
                for i in range(1, num_priorities+1):
                    ind = np.where(oncelik == i)[0]
                    indexes.append(ind+1)

                zero_ind = np.where(oncelik == 0)[0]
                if 0 in oncelik:
                    indexes.append(zero_ind+1)

                baslangic = np.array([0])
                bitis =  np.array([len(oncelik)+1])

                if len(bitis_koordinat) != 0:
                    indexes.append(bitis)

                indexes.insert(0,baslangic)

            else:
                indexes = []
                baslangic = np.array([0])
                bitis =  np.array([len(oncelik)+1])
                indexes.append(bitis)
                indexes.insert(0,baslangic)

            return indexes

        for indexes in oncelik_index(oncelik,bitis_koordinat):
            tuples.append(tuple(indexes.tolist()))
            a=list(permutations(indexes))
            hedef_kombinler += [a]

        for tpl in product(*hedef_kombinler):
            combined = ()
            for i, t in enumerate(tuples):
                combined += (tpl[i] if len(tpl[i]) > 1 else tpl[i][0],)
            kombin.append(combined)


        for tpl in kombin:
            new_tpl = tuple([elem for sub_tpl in tpl for elem in (sub_tpl if isinstance(sub_tpl, tuple) else (sub_tpl,))])
            tum_kombinler.append(new_tpl)

        toplam_mesafe = [sum([mesafeler[tum_kombinler[i][j], tum_kombinler[i][j+1]] for j in range(len(tum_kombinler[i])-1)]) for i in range(len(tum_kombinler))]
        en_kisa_rota_indexi = np.argmin(toplam_mesafe)
        en_kisa_rota_kombini = tum_kombinler[en_kisa_rota_indexi]
        en_kisa_rota = [tum_hedefler[i].tolist() for i in en_kisa_rota_kombini]
        del en_kisa_rota[0]
        if self.baslangica_don: 
            en_kisa_rota.append((self.kalkis_enlem,self.kalkis_boylam))

        print("en_kisa_rota",en_kisa_rota)
