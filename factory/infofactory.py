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

    def generate_new_value(self, sysid: int, is_parent: int, sex: int):
        cur = self.db.cursor()
        cur.execute(
            "SELECT value FROM info WHERE sysid=? AND is_parent=? AND sex=? ORDER BY value",
            (sysid, is_parent, sex)
        )
        if is_parent:
            startnum = (sysid + 10) * 10000 + sex * 1000 + 1
        else:
            startnum = (sysid + 10) * 100000 + sex * 10000
        for val, in cur.fetchall():
            if startnum == val:
                startnum += 1
            else:
                break
        return startnum

    def close(self):
        self.db.close()


if __name__ == '__main__':
    t = InfoFactory()
    t.close()
    print(t.generate_new_value(0, 0, 0))
