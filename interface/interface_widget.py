class InterfaceWidgets:
    def __init__(self, *rows_keywords: list[str]):
        # Dictionary to store objects
        self.widgets = {}
        # Store keywords on a two-dimensional array
        self.keywords = list(rows_keywords)

    def __setitem__(self, key, value):
        if type(key) == str:
            self.widgets[key] = value
        else:
            raise KeyError

    def __getitem__(self, item):
        if type(item) == str:
            return self.widgets[item]
        elif type(item) == int:
            return self.widgets[self.keywords[item]]
        else:
            raise KeyError

    def iter_widgets(self):
        for kw in self.widgets:
            yield kw, self.widgets[kw]

    def iter_keywords(self, index: int = None):
        if index is None:
            for i, _keywords in enumerate(self.keywords):
                yield i, _keywords
        elif index < len(self.keywords):
            for _keyword in self.keywords[index]:
                yield _keyword
        else:
            raise ValueError

    def iter_widgets_with_index(self):
        for kw in self.widgets:
            row_num = -1
            row_span = 0
            col_num = 0
            col_span = 0
            for i, rows in enumerate(self.keywords):
                if kw in self.keywords[i]:
                    if row_num == -1:
                        row_num = i
                        col_num = self.keywords[i].index(kw)
                        col_span = self.keywords[i].count(kw)
                    row_span += 1
            if row_num > -1:
                yield self.widgets[kw], row_num, col_num, row_span, col_span
