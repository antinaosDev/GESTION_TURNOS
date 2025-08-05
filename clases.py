class Receta:
    def __init__(self,nombre,rut,dv,cat,sub_cat,gene):
        self.name = nombre
        self.rut = rut
        self.dv = dv
        self.cat= cat
        self.sub_c = sub_cat
        self.gene = gene

    def dict_rec(self):
        return {
            'NOMBRE':self.name,
            'RUT':f"{self.rut}-{self.dv}",
            'CATEGORIA':self.cat,
            'SUBCAT':self.sub_c,
            'GENERADOR_TURNO': self.gene
        }
    

# Categorías principales
CATEGORIAS = {
    "Preferencial": "P",
    "General": "G"
}

# Subcategorías con siglas
SUBCATEGORIAS = {
    "Receta Controlada": "CT",
    "Receta Morbilidad": "M",
    "Receta Crónico": "CN"
}
    