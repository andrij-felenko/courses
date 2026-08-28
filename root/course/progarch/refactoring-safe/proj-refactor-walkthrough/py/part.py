from dataclasses import dataclass

@dataclass
class Line:
    meter: str
    tariff: str          # "day" | "night" | "business"
    kwh: int

@dataclass
class Account:
    customer: str
    active: bool
    lines: list[Line]

def statement(acc: Account) -> str:
    ta = 0                         # total amount, у копійках
    vc = 0                         # volume credits — бонусні кВт·год
    out = f"Рахунок — {acc.customer}\n"

    for l in acc.lines:
        # ціна рядка за тарифом
        a = 0
        if l.tariff == "day":
            a = l.kwh * 250
            if l.kwh > 100:
                a += (l.kwh - 100) * 30
        elif l.tariff == "night":
            a = l.kwh * 120
        elif l.tariff == "business":
            a = l.kwh * 300
            if l.kwh > 500:
                a += (l.kwh - 500) * 40
        else:
            raise ValueError(f"невідомий тариф: {l.tariff}")

        # бонусні кВт·год — лише активним і не бізнесу
        if acc.active:
            if l.tariff != "business":
                vc += max(l.kwh - 200, 0)
                if l.tariff == "night":
                    vc += l.kwh // 500

        out += f"  {l.meter}: {l.kwh} кВт·год — {a / 100:.2f} грн\n"
        ta += a

    out += f"Разом: {ta / 100:.2f} грн\n"
    out += f"Бонусні кіловати: {vc}\n"
    return out
