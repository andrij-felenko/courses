# Перевірити кожен рядок BOM окремо + зібрати мапу «позначення → номер рядка»,
# дорогою ловлячи дублікати. Повертає кількість знайдених проблем.
def check_bom_internal(rows, ref_to_line):
    problems = 0
    for r in rows:
        # (1) Кількість мусить дорівнювати довжині переліку позначень.
        if r.qty != len(r.refs):
            print("[E%d] рядок %d: К-сть=%d, а позначень перелічено %d"
                  % (BomError.ERR_QTY_MISMATCH, r.line_no, r.qty, len(r.refs)))
            problems += 1
        # (2) Монтуємо без MPN — нічого замовити. DNP без MPN — НОРМА, не чіпаємо.
        if not r.dnp and not r.has_mpn:
            print("[E%d] рядок %d: монтований рядок без MPN — закупити нічим"
                  % (BomError.ERR_NO_MPN, r.line_no))
            problems += 1
        # (3) Дублікати позначень: те саме позначення вже зустрічалось.
        for ref in r.refs:
            if ref in ref_to_line:
                print("[E%d] позначення %s повторюється: рядки %d і %d"
                      % (BomError.ERR_DUP_REFDES, ref, ref_to_line[ref], r.line_no))
                problems += 1
            else:
                ref_to_line[ref] = r.line_no
    return problems
