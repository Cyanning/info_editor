class Structure:
    def __init__(self, value: int, name: str, pval: int):
        self.value = value
        self.name = name
        self.pval = pval

    def __repr__(self):
        return "( {} | {} | {} )".format(self.value, self.name, self.pval)

    def gender(self) -> int:
        if self.value < 1000000:
            val = self.value // 1000
        else:
            val = self.value // 10000
        val %= 10
        return val

    def sysid(self) -> int:
        if self.value < 1000000:
            val = self.value // 10000
        else:
            val = self.value // 100000
        val -= 10
        return val

    def is_parent(self):
        if self.value < 1000000:
            flag = True
        else:
            flag = False
        return flag

    def value_(self) -> str:
        if self.value < 1000000:
            val = "%d " % self.value
        else:
            val = str(self.value)
        return val

    def name_neutral(self) -> str:
        if "（" in self.name and "）" in self.name:
            start = self.name.index("（")
            end = self.name.index("）") + 1
            return self.name[:start] + self.name[end:]

    def value_compliance(self) -> bool:
        if 100000 <= self.value <= 212000:
            flag = True
        elif 1000000 <= self.value <= 2120000:
            flag = True
        else:
            flag = False
        return flag

    def name_compliance(self) -> bool:
        if "(" in self.name:
            self.name.replace("(", "（")
        if ")" in self.name:
            self.name.replace("(", "）")

        if len(self.name) < 1:
            flag = False
        elif not self.name.count("（") == self.name.count("）") == 1:
            flag = False
        else:
            flag = True
        return flag
