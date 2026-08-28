from dataclasses import dataclass

@dataclass
class DataSet:
    name: str
    born_many_places: bool          # G1: той самий ключ народжується в кількох місцях одразу?
    avail_partition_nonneg: bool    # G2: доступність запису під розривом — незаперечна?
    natural_home: bool              # G3: чи є природний «дім» на запис?

def decide(ds: DataSet) -> tuple[str, str]:
    pressures = []
    if ds.born_many_places:        pressures.append("гео/офлайн")
    if ds.avail_partition_nonneg:  pressures.append("доступність-під-розривом")
    if not pressures:                                  # жоден тиск не назвався
        return "один лідер + читальні репліки", "пауза на failover"
    if not ds.natural_home:                            # тиск є, природного дому нема
        return "безлідерна (кворум W+R>N)", "конфлікти + тюнинг кворуму"
    return "мультилідер (лідер на дім/регіон)", "конфлікти на спільних ключах"

DH = [
    #          назва               G1     G2     G3
    DataSet("Твін дому",           False, False, True),
    DataSet("Реєстр",              False, False, True),
    DataSet("Телеметрія",          False, False, True),
    DataSet("Крос-регіон (гіп.)",  False, False, True),
]

for ds in DH:
    model, price = decide(ds)
    print(f"{ds.name:<18} → {model}  ·  ціна: {price}")
