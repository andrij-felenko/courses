# --- exporters/csv_exporter.py: самодостатній, залежить лише від контракту ---
from ..registry import register, Row

@register
class CsvExporter:
    format = "csv"
    def export(self, rows: list[Row]) -> str:
        if not rows:
            return ""
        cols = list(rows[0].keys())
        head = ",".join(cols)
        body = "\n".join(",".join(str(r[c]) for c in cols) for r in rows)
        return f"{head}\n{body}"
