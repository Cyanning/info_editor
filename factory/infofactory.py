import sqlite3
from model.structure import Structure


class InfoFactory:
    def __init__(self):
        self.db = sqlite3.connect("../resource/creature.db")

    def create_structure(self, struc: Structure):
        if not struc.value_compliance() or not struc.name_compliance() or struc.pval == 0:
            raise ValueError("插入的数据不完整")
        cur = self.db.cursor()
        cur.execute("SELECT COUNT(*) FROM info WHERE value={}".format(struc.value))
        if cur.fetchone()[0] > 0:
            raise ValueError("插入的数据重复")
        cur.execute(
            "INSERT INTO info (value,name,pval) VALUES (?,?,?)",
            (struc.value, struc.name, struc.pval)
        )
        self.db.commit()

    def close(self):
        self.db.close()
