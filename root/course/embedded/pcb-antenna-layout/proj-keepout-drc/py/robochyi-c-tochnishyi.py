# Знайти у рядку значення JSON-ключа виду  "key": "value"  і повернути value
# (або None, якщо ключа немає). Свідомо вузька реалізація під ПЛАСКІ рядкові
# поля звіту DRC — не загальний парсер JSON (екранованих лапок усередині
# значень тут не буває).
def json_str_field(line, key):
    k = line.find(f'"{key}"')               # шукаємо "key"
    if k < 0:
        return None
    colon = line.find(":", k + len(key) + 2)
    if colon < 0:
        return None
    q1 = line.find('"', colon)              # відкривна лапка значення
    if q1 < 0:
        return None
    q2 = line.find('"', q1 + 1)             # закривна лапка значення
    if q2 < 0:
        return None
    return line[q1 + 1:q2]


# Підрахунок порушень: читаємо звіт построково, для кожного рядка з полем
# "severity" дивимось значення; "error" із потрібного правила — критично.
# Повертає (кількість КРИТИЧНИХ keep-out антени, кількість усіх помилок).
def scan_report(f, rule_name):
    ant_crit = 0
    all_err = 0
    for line in f:
        sev = json_str_field(line, "severity")
        if sev == "error":
            all_err += 1
            # опис порушення KiCad кладе поруч полем "description"
            desc = json_str_field(line, "description")
            if desc is not None and rule_name in desc:
                ant_crit += 1
    return ant_crit, all_err
