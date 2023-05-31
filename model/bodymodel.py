from model.sentence import Sentence


class BodyModel:
    def __init__(self, value: int, name: str, context):
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
    def sysid(self) -> int:
        if self.value >= 1000000:
            val = self.value // 100000
        else:
            val = self.value // 10000
        val -= 10
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
        Assign directly to the paragraph.
        """
        if type(text) == str:
            self._paragraph = text.strip()

    def clean_sentences(self):
        """
        Clean up the sentence list.
        """
        self._sentences.clear()

    def add_into_paragraph(self, context):
        """
        If context is an iterable object containing a sentence object,
        add text from the sentence object to the paragraph;
        if context is a string, connect the content directly after the paragraph.
        """
        if type(context) == str:
            self._paragraph += f"\n{context.strip()}"
        else:
            for new in context:
                if new.value not in self._paragraph:
                    self._paragraph += f"\n{new.value}。\n"

    def add_into_sentences(self, context):
        """
        Add multiple sentence objects.
        """
        for new in context:
            for old in self._sentences:
                if new == old:
                    break
            else:
                self._sentences.append(new)

    def convert_for_paragraph(self):
        """
        Convert sentences of a list of sentences into paragraphs.
        """
        if len(self._sentences):
            self._paragraph = "。\n\n".join([x.value for x in self._sentences])
            self._paragraph += "。"
        else:
            self._paragraph = ''

    def convert_into_sentences(self):
        """
        Split the paragraph into a list of sentences,
        the list of sentences will be reset!!!
        """
        length = len(self._paragraph)
        assert length
        self._sentences = []
        # The timing of breaking out of the loop takes advantage of the fact that the find function returns -1
        left = 0
        right = 0
        while left < length and right >= 0:
            # Obtain the cut-off point in the string from the starting point to the end
            right = self._paragraph.find('。\n', left)
            try:
                text = Sentence(self._paragraph[left:right])
            except ValueError:
                # Skip empty strings, but do not affect the starting point forward
                pass
            else:
                self._sentences.append(text)
            finally:
                left = right + 1
