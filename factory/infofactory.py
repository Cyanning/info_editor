import sqlite3
from model.structure import Structure


class InfoFactory:
    def __init__(self):
        self.db = sqlite3.connect("../resource/creature.db")

    def get_structures_by_name(self, key_name: str):
        """
        返回所有名字包含关键字的structure对象
        """
        cur = self.db.cursor()
        cur.execute("SELECT value, name, pval FROM info WHERE name LIKE ?", (f"%{key_name}%",))
        for data in cur.fetchall():
            yield Structure(*data)

    def get_astructure_by_value(self, key_value: int):
        """
        返回对应value的structure对象
        """
        cur = self.db.cursor()
        cur.execute("SELECT value, name, pval FROM info WHERE value=?", (key_value,))
        data = cur.fetchone()
        if data is not None:
            yield Structure(*data)

    def create_structure(self, struc: Structure):
        """
        插入一个新结构
        """
        if not struc.value_compliance() or not struc.name_compliance() or struc.pval == 0:
            raise ValueError("插入的数据不完整")
        cur = self.db.cursor()
        cur.execute("SELECT COUNT(*) FROM info WHERE value={}".format(struc.value))
        if cur.fetchone()[0] > 0:
            raise ValueError("插入的数据重复")
        cur.execute(
            "INSERT INTO info (value,name,pval,sysid,sex,is_parent) VALUES (?,?,?,?,?,?)",
            (struc.value, struc.name, struc.pval, struc.sysid(), struc.gender(), struc.is_parent())
        )
        self.db.commit()

    def generate_new_sturcture(self, sysid: int, is_parent: int, sex: int):
        """
        返回一个可用value
        """
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
        return Structure(startnum, "", 0)

    def patrilineal_link(self, struc: Structure):
        """
        返回 父级关系链
        """
        cur = self.db.cursor()
        link = [struc]

        def recursion(_pval):
            cur.execute("SELECT value, name, pval FROM info WHERE value=?", (_pval,))
            res = cur.fetchone()
            if res is not None:
                _struc = Structure(*res)
                link.append(_struc)
                if _struc.pval != 0:
                    recursion(_struc.pval)

        recursion(struc.pval)
        link.reverse()
        return link

    def close(self):
        self.db.close()
