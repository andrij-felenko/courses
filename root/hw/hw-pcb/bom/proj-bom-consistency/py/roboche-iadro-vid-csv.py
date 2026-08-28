import sys

# Розбити ОДИН рядок CSV на поля за правилами RFC 4180:
#  - кома РОЗДІЛЯЄ поля ТІЛЬКИ поза лапками;
#  - поле в лапках може містити коми (вони — частина значення);
#  - подвоєна лапка "" усередині лапок означає одну літеральну лапку.
def split_csv_line(line):
    fields = []
    cur = []
    in_quotes = False
    i = 0
    while i < len(line):
        c = line[i]
        if in_quotes:
            if c == '"':
                if i + 1 < len(line) and line[i + 1] == '"':   # "" → одна лапка
                    cur.append('"')
                    i += 1                                     # проковтнути другу
                else:
                    in_quotes = False                          # кінець поля в лапках
            else:
                cur.append(c)                                  # звичайний символ усередині лапок
        else:
            if c == '"':
                in_quotes = True                               # початок поля в лапках
            elif c == ',':
                fields.append("".join(cur))                    # кома ПОЗА лапками — роздільник
                cur = []
            else:
                cur.append(c)
        i += 1
    fields.append("".join(cur))                                # останнє поле
    return fields
