from model.sentence import *


class BodyModel:
    def __init__(self, value: int, name: str, context):
        """
        :param value: 模型id
        :param context: 信息内容
        """
        super().__init__()
        self.value = int(value)
        self.name = name
        self._sentences = [Sentence(x) for x in context]
        self._paragraph = ''
        self.convert_for_paragraph()

    def __iter__(self):
        return self._sentences.__iter__()

    def __getitem__(self, item):
        if not type(item) == int and abs(item) < len(self._sentences):
            raise IndexError
        return self._sentences[item]

    def __len__(self):
        return len(self._sentences)

    def __contains__(self, item):
        if type(item) is not Sentence:
            raise ValueError
        return any((x == item for x in self._sentences))

    @property
    def gender(self) -> int:
        if self.value >= 1000000:
            val = self.value // 10000
        else:
            val = self.value // 1000
        val %= 10
        return val

    @property
    def value_(self):
        if self.value < 1000000:
            val = "%d " % self.value
        else:
            val = str(self.value)
        return val

    @property
    def paragraph(self):
        return self._paragraph

    @paragraph.setter
    def paragraph(self, text):
        """
        直接赋值给段落
        """
        if type(text) == str:
            self._paragraph = text.strip()

    def clean_sentences(self):
        """
        清理句子列表
        """
        self._sentences.clear()

    def add_into_paragraph(self, context):
        """
        contexts: 为包含句子对象的可迭代对象，则从句子对象中添加文字到段落；
        为字符串则直接在段落后衔接内容
        """
        if type(context) == str:
            self._paragraph += f"\n{context.strip()}"
        else:
            for new in context:
                if new.value not in self._paragraph:
                    self._paragraph += f"\n{new.value}。\n"

    def add_into_sentences(self, context):
        """
        添加多个句子对象
        """
        for new in context:
            for old in self._sentences:
                if new == old:
                    break
            else:
                self._sentences.append(new)

    def convert_for_paragraph(self):
        """
        将句子列表的句子转换为段落
        """
        if len(self._sentences):
            self._paragraph = "。\n\n".join([x.value for x in self._sentences])
            self._paragraph += "。"
        else:
            self._paragraph = ''

    def convert_into_sentences(self):
        """
        !!!将段落拆分到句子列表, 句子列表会被重置!!!
        """
        length = len(self._paragraph)
        assert length
        self._sentences = []
        # 跳出循环的时机利用了 find 函数返回 -1 的特性
        left = 0
        right = 0
        while left < length and right >= 0:
            # 取得从起点角标往后的字符串中切断点角标
            right = self._paragraph.find('。\n', left)
            try:
                text = Sentence(self._paragraph[left:right])
            except ValueError:
                # 跳过空字符串，但不影响起点前移
                pass
            else:
                self._sentences.append(text)
            finally:
                left = right + 1
