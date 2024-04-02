from model.sentence import Sentence
from model.structure import Structure


class BodyModel(Structure):
    def __init__(self, value: int, name: str, context: list = None):
        super().__init__(value, name, 0)
        self.paragraph: str = ""
        self.sentences: list[Sentence] = []
        if context is not None:
            self.sentences = [Sentence(_str_) for _str_ in context]
            self.convert_forparagraph()

    def __getitem__(self, item):
        if not isinstance(item, int) and abs(item) < len(self.sentences):
            raise IndexError
        return self.sentences[item]

    def __len__(self):
        return len(self.sentences)

    def __contains__(self, item):
        if isinstance(item, Sentence):
            return any((x == item for x in self.sentences))
        else:
            raise ValueError

    @property
    def paragraph(self):
        return self.paragraph

    @paragraph.setter
    def paragraph(self, text):
        """
        Assign directly to the paragraph.
        """
        if isinstance(text, str):
            self.paragraph = text.strip()

    def cleansentences(self):
        """
        Clean up the sentence list.
        """
        self.sentences.clear()

    def add_intoparagraph(self, context):
        """
        If context is an iterable object containing a sentence object,
        add text from the sentence object to the paragraph;
        if context is a string, connect the content directly after the paragraph.
        """
        if isinstance(context, str):
            self.paragraph += f"\n{context.strip()}"
        else:
            for new in context:
                if new.value not in self.paragraph:
                    self.paragraph += f"\n{new.value}。\n"

    def add_intosentences(self, context):
        """
        Add multiple sentence objects.
        """
        for new in context:
            for old in self.sentences:
                if new == old:
                    break
            else:
                self.sentences.append(new)

    def convert_forparagraph(self):
        """
        Convert sentences of a list of sentences into paragraphs.
        """
        if len(self.sentences):
            self.paragraph = "。\n\n".join([x.value for x in self.sentences])
            self.paragraph += "。"
        else:
            self.paragraph = ''

    def convert_intosentences(self):
        """
        Split the paragraph into a list of sentences, the list of sentences will be reset!!!
        """
        length = len(self.paragraph)
        assert length
        self.sentences = []
        # The timing of breaking out of the loop takes advantage of the fact that the find function returns -1
        left = 0
        right = 0
        while left < length and right >= 0:
            # Obtain the cut-off point in the string from the starting point to the end
            right = self.paragraph.find('。\n', left)
            try:
                text = Sentence(self.paragraph[left:right])
            except ValueError:
                # Skip empty strings, but do not affect the starting point forward
                pass
            else:
                self.sentences.append(text)
            finally:
                left = right + 1
