import random
equipos = ["Equipo1", "Equipo2", "Equipo3", "Equipo4", "Equipo5", "Equipo6"]

class TodosVsTodos():
    @classmethod
    def generar_encuentros(self, equipos: list):
        if len(equipos) <= 3:
            return False
        
        encuentros:list[tuple] = []
        for equipo_a in equipos:
            for equipo_b in equipos:
                if equipos.index(equipo_b) > equipos.index(equipo_a):
                    #print(equipo_b)
                    encuentros.append((equipo_a, equipo_b))
        
        #ordenamiento 
        encuentros_ord: list[tuple] = []
        ref_index = 0
        for _ in encuentros:
            encuentros_ord.append(encuentros[ref_index])
            
            if ref_index >= 0:
                ref_index += 1
                ref_index *= -1
            else:
                ref_index *= -1
                            
        print(encuentros)
        return encuentros_ord
            
encuentros = TodosVsTodos.generar_encuentros(equipos)
print(encuentros)
        