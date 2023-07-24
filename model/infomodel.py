from model.structure import Structure


class InfoModel(Structure):
    def __init__(self, value: int, name: str, pval: int):
        super().__init__(value, name, pval)
        self.correspondents = []

    def generate_correspondents(self):
        pass
