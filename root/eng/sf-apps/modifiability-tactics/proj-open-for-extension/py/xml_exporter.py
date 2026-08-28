# --- exporters/xml_exporter.py: НОВИЙ файл. Більше не чіпаємо НІЧОГО ---
from ..registry import register, Row

@register
class XmlExporter:
    format = "xml"
    def export(self, rows: list[Row]) -> str:
        cell = lambda k, v: f"<{k}>{v}</{k}>"
        row = lambda r: "  <row>" + "".join(cell(k, v) for k, v in r.items()) + "</row>"
        return "<rows>\n" + "\n".join(row(r) for r in rows) + "\n</rows>"
