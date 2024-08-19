if uzaklik < 5:
                self.dur()   
                    if self.radar.hata =! True:
                        İf self.radar.mesafe > 30:
                            self.asagi_git(HİZLİ)
                        elif self.radar.mesafe > 10:
                            self.asagi_git(ORTA)
                        else:
                            self.asagi_git(YAVAS)
                    elif self.lidar.hata =! True:
                        İf self.lidar.mesafe > 30:
                            self.asagi_git(HİZLİ)
                        elif self.lidar.mesafe > 10:
                              self.asagi_git(ORTA)
                        else:
                               self.asagi_git(YAVAS)
                    else:  
                          self.asagi_git(YAVAS)
