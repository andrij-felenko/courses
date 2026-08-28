#!/usr/bin/env python3
"""
Автоматичний генератор індексу та графа залежностей для ADR.
Сканує каталог doc/adr/, парсить метадані (заголовок, статус, дату, зв'язки),
створює doc/adr/README.md із таблицею та інтерактивним графом Mermaid.
"""

from dataclasses import dataclass, field
from pathlib import Path
import re
import sys
from typing import List, Optional


@dataclass
class ADRRecord:
    number: int
    title: str
    filename: str
    date: str = "Невідомо"
    status: str = "Proposed"
    supersedes: Optional[int] = None
    superseded_by: Optional[int] = None
    amends: Optional[int] = None
    amended_by: Optional[int] = None


class ADRIndexGenerator:
    def __init__(self, adr_dir: Path):
        self.adr_dir = adr_dir
        self.records: List[ADRRecord] = []

    def parse_file(self, file_path: Path) -> Optional[ADRRecord]:
        name_match = re.match(r"^(\d+)-(.+)\.md$", file_path.name)
        if not name_match:
            return None

        number = int(name_match.group(1))
        content = file_path.read_text(encoding="utf-8")

        # Витягуємо заголовок (H1)
        title_match = re.search(r"^#\s+(?:ADR-)?(?:\d+[\.:])?\s*(.+)$", content, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else name_match.group(2).replace("-", " ")

        # Витягуємо дату
        date_match = re.search(r"(?:Date|Дата):\s*([\d-]+)", content, re.IGNORECASE)
        date_str = date_match.group(1).strip() if date_match else "Невідомо"

        # Витягуємо статус
        status = "Proposed"
        status_section = re.search(
            r"##\s+(?:Status|Статус)\s*\n+([^\n#]+)", content, re.IGNORECASE
        )
        if status_section:
            raw_status_line = status_section.group(1).strip()
            first_token = raw_status_line.split()[0].rstrip(":,;").capitalize()
            status = first_token

        record = ADRRecord(
            number=number,
            title=title,
            filename=file_path.name,
            date=date_str,
            status=status
        )

        # Парсимо перехресні зв'язки (Supersedes / Superseded by / Amends)
        sup_by_match = re.search(r"(?:superseded by|замінено на)\s+.*?(\d+)", content, re.IGNORECASE)
        if sup_by_match:
            record.superseded_by = int(sup_by_match.group(1))

        sup_match = re.search(r"(?:supersedes|замінює)\s+.*?(\d+)", content, re.IGNORECASE)
        if sup_match:
            record.supersedes = int(sup_match.group(1))

        amend_match = re.search(r"(?:amends|доповнює)\s+.*?(\d+)", content, re.IGNORECASE)
        if amend_match:
            record.amends = int(amend_match.group(1))

        return record

    def scan(self) -> None:
        self.records.clear()
        if not self.adr_dir.exists():
            return

        for md_file in sorted(self.adr_dir.glob("*.md")):
            if md_file.name.lower() in ("readme.md", "index.md", "template.md"):
                continue
            rec = self.parse_file(md_file)
            if rec:
                self.records.append(rec)

        self.records.sort(key=lambda r: r.number)

    def generate_markdown(self) -> str:
        lines = [
            "# Реєстр архітектурних рішень (ADR Index)",
            "",
            "> Цей файл згенеровано автоматично скриптом індексації. Не редагуйте вручну.",
            "",
            "## Граф зв'язків та еволюції",
            "",
            "```mermaid",
            "flowchart TD",
        ]

        # Стилізація статусів у Mermaid
        lines.append("    classDef accepted fill:#e7f7ee,stroke:#27ae60,stroke-width:2px,color:#1a1a1a;")
        lines.append("    classDef superseded fill:#eef6ff,stroke:#2457d6,stroke-width:1.5px,stroke-dasharray: 4 4,color:#6b7280;")
        lines.append("    classDef proposed fill:#fdf8e2,stroke:#d4ac0d,stroke-width:1.5px,color:#7d6608;")
        lines.append("    classDef rejected fill:#f5f5f5,stroke:#6b7280,stroke-width:1px,color:#6b7280;")
        lines.append("    classDef deprecated fill:#fdf2f0,stroke:#c0392b,stroke-width:1.5px,color:#c0392b;")

        # Вузли графа
        for r in self.records:
            node_id = f"ADR{r.number:04d}"
            label = f"\"{r.number:04d}: {r.title}\""
            lines.append(f"    {node_id}[{label}]")
            
            cls_name = r.status.lower()
            if "accept" in cls_name:
                lines.append(f"    class {node_id} accepted;")
            elif "superse" in cls_name:
                lines.append(f"    class {node_id} superseded;")
            elif "propos" in cls_name:
                lines.append(f"    class {node_id} proposed;")
            elif "reject" in cls_name:
                lines.append(f"    class {node_id} rejected;")
            elif "deprec" in cls_name:
                lines.append(f"    class {node_id} deprecated;")

        # Зв'язки (стрілки)
        for r in self.records:
            curr_id = f"ADR{r.number:04d}"
            if r.supersedes is not None:
                old_id = f"ADR{r.supersedes:04d}"
                lines.append(f"    {curr_id} -.->|\"замінює\"| {old_id}")
            if r.amends is not None:
                base_id = f"ADR{r.amends:04d}"
                lines.append(f"    {curr_id} -->|\"доповнює\"| {base_id}")

        lines.extend([
            "```",
            "",
            "## Таблиця рішень",
            "",
            "| ID | Дата | Заголовок | Статус | Пов'язані рішення |",
            "|:---|:---|:---|:---|:---|",
        ])

        for r in self.records:
            status_badge = f"**{r.status}**"
            links_desc = []
            if r.supersedes:
                links_desc.append(f"Замінює ADR-{r.supersedes:04d}")
            if r.superseded_by:
                links_desc.append(f"Замінено на ADR-{r.superseded_by:04d}")
            if r.amends:
                links_desc.append(f"Доповнює ADR-{r.amends:04d}")

            links_str = ", ".join(links_desc) if links_desc else "—"
            row = (
                f"| [{r.number:04d}]({r.filename}) "
                f"| {r.date} "
                f"| {r.title} "
                f"| {status_badge} "
                f"| {links_str} |"
            )
            lines.append(row)

        lines.append("")
        return "\n".join(lines)

    def write_index(self, output_path: Optional[Path] = None) -> None:
        target = output_path or (self.adr_dir / "README.md")
        self.scan()
        content = self.generate_markdown()
        target.write_text(content, encoding="utf-8")


if __name__ == "__main__":
    target_dir = Path("doc/adr") if len(sys.argv) < 2 else Path(sys.argv[1])
    generator = ADRIndexGenerator(target_dir)
    generator.write_index()
    print(f"Згенеровано покажчик для {len(generator.records)} ADR у {target_dir / 'README.md'}")
