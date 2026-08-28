# Перекладач ЖИВЕ НА МЕЖІ — в окремому модулі, не в sales і не в billing.
# Це антикорупційний шар бухгалтерії: приймає чужу модель, віддає свою.
from sales import Lead
from billing import Payer

def lead_to_payer(lead: Lead, tax_id: str, iban: str) -> Payer:
    # беремо лише те, що справді перетинає кордон: id та ім'я.
    # stage, probability, owner_id ЛИШАЮТЬСЯ за дверима — бухгалтерії чужі.
    return Payer(
        id=lead.id,
        name=lead.name,
        tax_id=tax_id,
        credit_limit=0,   # стартовий ліміт — правило БУХГАЛТЕРІЇ, не ліда
        iban=iban,
    )
