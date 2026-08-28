# plugins/markdown_exporter.py — сторонній файл у теці plugins/.
PLUGIN_API = 3                      # під яку версію контракту зібрано

class MarkdownExporter:
    extension = "md"
    def export(self, doc) -> bytes:
        text = "\n\n".join(f"# {b.title}\n\n{b.body}" for b in doc.blocks)
        return text.encode("utf-8")

def register(host) -> None:         # умовлена точка входу
    host.register_exporter(MarkdownExporter())
