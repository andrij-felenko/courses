from abc import ABC, abstractmethod

class DocBuilder(ABC):              # РОЛІ кроків — те, ЩО можна робити
    @abstractmethod
    def add_header(self, text): ...
    @abstractmethod
    def add_paragraph(self, text): ...
    @abstractmethod
    def get_result(self): ...

class HtmlBuilder(DocBuilder):                # одне представлення — HTML
    def __init__(self):        self._out = ""
    def add_header(self, t):    self._out += f"<h1>{t}</h1>\n"
    def add_paragraph(self, t): self._out += f"<p>{t}</p>\n"
    def get_result(self):       return self._out

class PlainBuilder(DocBuilder):               # інше представлення — текст
    def __init__(self):        self._out = ""
    def add_header(self, t):    self._out += t.upper() + "\n"
    def add_paragraph(self, t): self._out += t + "\n"
    def get_result(self):       return self._out

class Director:                    # знає лише ПОРЯДОК, не знає матеріалу
    def build(self, b: DocBuilder):
        b.add_header("Звіт")
        b.add_paragraph("Перший абзац.")
        b.add_paragraph("Другий абзац.")

director = Director()
html = HtmlBuilder()
director.build(html)               # той самий обхід...
print(html.get_result())           # ...дав HTML

plain = PlainBuilder()
director.build(plain)              # ...той самий обхід...
print(plain.get_result())          # ...дав звичайний текст
