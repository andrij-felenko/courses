# Розібрати поле позначень рядка BOM ("R1-R4, R7") у список окремих нормалізованих
# позначень: ["R1","R2","R3","R4","R7"]. Спершу ділимо за комами, тоді кожен
# шматок розгортаємо як можливий діапазон.
def parse_refdes_field(field):
    refs = []
    # поле вже без зовнішніх лапок (їх зняв split_csv_line), тож ділимо просто за комами
    for tok in field.split(','):
        t = trim(tok)
        if t:
            refs.extend(expand_range(t))
    return refs
