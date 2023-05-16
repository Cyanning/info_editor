import hashlib


class Sentence:
    def __init__(self, context: str):
        value = context.strip()
        if not len(value):
            raise ValueError
        self.value = value

    def __eq__(self, other):
        return self.value == other

    def __ne__(self, other):
        return self.value != other

    def __len__(self):
        return len(self.value)

    def __get__(self, instance, owner):
        return self.value

    def __set__(self, instance, value):
        raise AttributeError

    @property
    def gethash(self):
        """
        设置语句的hash值
        """
        sha256 = hashlib.sha256()
        sha256.update(self.value.encode('UTF-8'))
        hashstring = sha256.hexdigest()
        return hashstring
