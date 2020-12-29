from app.Test_resume import Test_resume

class Compare():
    old_resume: Test_resume
    new_resume: Test_resume
    resume: { }
    def __init__(self, old_resume, new_resume, compare=True):
        self.resume = { }
        self.old_resume = old_resume
        self.new_resume = new_resume
        if compare:
            self.compare()
    
    def compare(self):
        for key, value in self.new_resume.resume.items():
            if key=="creditos_analizados" or key=="total_creditos_analizados":
                self.resume[key] = value
            elif key=="porcentaje_entidades_correctas" or key=="porcentaje_paginas_correctas":
                self.resume[key+"_"+str(self.new_resume.id_prueba_realizada)] = value
                self.resume[key+"_"+str(self.old_resume.id_prueba_realizada)] = self.old_resume.resume[key]
                self.resume[key+"_mejor"] = 1 if value>self.old_resume.resume[key] else 0 if value==self.old_resume.resume[key] else -1
            elif key=="entidades":
                self.resume[key] = { }
                for key2, value2 in value.items():
                    self.resume[key][key2] = { }
                    for key3, value3 in value2.items():
                        if key3=="porcentaje_entidades_correctas" or key3=="porcentaje_paginas_correctas":
                            self.resume[key][key2][key3+"_"+str(self.new_resume.id_prueba_realizada)] = value3
                            self.resume[key][key2][key3+"_"+str(self.old_resume.id_prueba_realizada)] = self.old_resume.resume[key][key2][key3]
                            self.resume[key][key2][key3+"_mejor"] = 1 if value3>self.old_resume.resume[key][key2][key3] else 0 if value3==self.old_resume.resume[key][key2][key3] else -1
                        elif key3 not in ["entidades_correctas", "entidades_incorrectas", "porcentaje_entidades_correctas", 
                                            "paginas_correctas", "paginas_incorrectas", "porcentaje_paginas_correctas"]:
                            self.resume[key][key2][key3] = { }
                            self.resume[key][key2][key3]["porcentaje_entidades_correctas_"+str(self.new_resume.id_prueba_realizada)] = value3["porcentaje_entidades_correctas"]
                            self.resume[key][key2][key3]["porcentaje_entidades_correctas_"+str(self.old_resume.id_prueba_realizada)] = self.old_resume.resume[key][key2][key3]["porcentaje_entidades_correctas"]
                            self.resume[key][key2][key3]["porcentaje_entidades_correctas_mejor"] = 1 if value3["porcentaje_entidades_correctas"]>self.old_resume.resume[key][key2][key3]["porcentaje_entidades_correctas"] else 0 if value3["porcentaje_entidades_correctas"]==self.old_resume.resume[key][key2][key3]["porcentaje_entidades_correctas"] else -1
                            #pags
                            self.resume[key][key2][key3]["porcentaje_paginas_correctas_"+str(self.new_resume.id_prueba_realizada)] = value3["porcentaje_paginas_correctas"]
                            self.resume[key][key2][key3]["porcentaje_paginas_correctas_"+str(self.old_resume.id_prueba_realizada)] = self.old_resume.resume[key][key2][key3]["porcentaje_paginas_correctas"]
                            self.resume[key][key2][key3]["porcentaje_paginas_correctas_mejor"] = 1 if value3["porcentaje_paginas_correctas"]>self.old_resume.resume[key][key2][key3]["porcentaje_paginas_correctas"] else 0 if value3["porcentaje_paginas_correctas"]==self.old_resume.resume[key][key2][key3]["porcentaje_paginas_correctas"] else -1
        self.resume["id_pruebas_realizadas_analizadas"] = [self.old_resume.id_prueba_realizada, self.new_resume.id_prueba_realizada]
