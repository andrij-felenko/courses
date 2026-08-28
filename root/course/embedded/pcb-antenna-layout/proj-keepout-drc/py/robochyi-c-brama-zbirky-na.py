import sys

# Назва правила з .kicad_dru — за нею впізнаємо КРИТИЧНІ порушення keep-out.
# Має дослівно збігатися з (rule "...") у файлі правил.
ANT_RULE_NAME = "no copper in antenna keepout"


def main(argv):
    if len(argv) < 2:
        print(f"вжиток: {argv[0]} drc.json", file=sys.stderr)
        return 2                           # 2 — помилка виклику, не плати

    # Звіт DRC малий — кілька КБ навіть на щільній платі, тож читаємо цілком;
    # для гігабайтних файлів так робити не можна.
    try:
        with open(argv[1], "r", encoding="utf-8") as f:
            report = f.read()
    except OSError as e:
        print(f"{argv[1]}: {e}", file=sys.stderr)
        return 2

    # Скільки порушень саме НАШОГО правила keep-out антени?
    ant_viol = report.count(ANT_RULE_NAME)

    # Груба оцінка ВСІХ порушень: KiCad у JSON виставляє "severity": "error".
    # (Для точного числа потрібен справжній парсер — див. пастки нижче.)
    all_errors = report.count('"severity": "error"')

    print(f"DRC: усього помилок={all_errors}, з них keep-out антени={ant_viol}")

    if ant_viol > 0:
        print(
            f"ЗБІРКУ СПИНЕНО: {ant_viol} порушень keep-out антени.\n"
            "Під меандром або в зоні ANT_KEEPOUT є мідь — імовірно\n"
            "заливка землі на ВНУТРІШНЬОМУ шарі. Прибери мідь із зони.",
            file=sys.stderr)
        return 1                           # 1 — критично: зрив радіотракту
    if all_errors > 0:
        print(f"Увага: {all_errors} інших порушень DRC (не keep-out). "
              "Перевір звіт.", file=sys.stderr)
        return 1                           # теж валимо збірку, але іншим текстом

    print("DRC чисто: міді в зоні антени немає на жодному шарі.")
    return 0                               # 0 — конвеєр пускає далі


if __name__ == "__main__":
    sys.exit(main(sys.argv))
