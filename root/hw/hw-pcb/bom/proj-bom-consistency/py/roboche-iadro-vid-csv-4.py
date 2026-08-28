from dataclasses import dataclass

@dataclass
class BomRow:
    refs:    list    # розгорнуті, нормалізовані позначення цього рядка
    qty:     int     # заявлена кількість
    has_mpn: bool    # чи вказано номер деталі
    dnp:     bool    # чи це «не монтувати»
    line_no: int     # номер рядка у файлі (для звіту)

# Чи містить поле примітки ознаку «не монтувати»?
def is_dnp(note):
    n = note.upper()                           # до верхнього регістру
    return "DNP" in n or "DNI" in n or "DO NOT" in n

# Прочитати CSV переліку компонентів у список рядків.
# Колонки за порядком: 0 позначення, 1 кількість, 2 MPN, 3 примітка.
def read_bom(path):
    rows = []
    try:
        fp = open(path, "r", newline="", encoding="utf-8")
    except OSError:
        print(f"не відкрити {path}")
        return rows

    with fp:
        header_skipped = False
        for line_no, raw in enumerate(fp, start=1):
            line = raw.rstrip("\r\n")
            if not line:                       # порожній рядок — пропуск
                continue
            if not header_skipped:             # шапка
                header_skipped = True
                continue

            f = split_csv_line(line)
            if len(f) < 4:                     # надто короткий — ігнор
                continue

            rows.append(BomRow(
                refs=parse_refdes_field(f[0]),
                qty=int(trim(f[1])) if trim(f[1]).lstrip("-").isdigit() else 0,
                has_mpn=bool(trim(f[2])),
                dnp=is_dnp(f[3]),
                line_no=line_no,
            ))
    return rows
