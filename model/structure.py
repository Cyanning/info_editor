class Structure:
    def __init__(self, _value: int = 0, _name: str = ""):
        self.value = _value
        self.name = _name

    def gender(self) -> int:
        if self.value >= 1000000:
            val = self.value // 10000
        else:
            val = self.value // 1000
        val %= 10
        return val

    def sysid(self) -> int:
        if self.value >= 1000000:
            val = self.value // 100000
        else:
            val = self.value // 10000
        val -= 10
        return val

    def value_(self):
        if self.value < 1000000:
            val = "%d " % self.value
        else:
            val = str(self.value)
        return val

    def name_neutral(self):
        if "（" in self.name and "）" in self.name:
            start = self.name.index("（")
            end = self.name.index("）") + 1
            return self.name[:start] + self.name[end:]

    def name_compliance(self):
        if "(" in self.name:
            self.name.replace("(", "（")
        if ")" in self.name:
            self.name.replace("(", "）")

        res = not self.name.count("（") == self.name.count("）") == 1
        return res
