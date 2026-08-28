from enum import Enum
from dataclasses import dataclass
from typing import assert_never

class F(Enum):                          # закритий перелік полів
    EMAIL = "email";   PASSWORD = "password"; CONFIRM = "confirm"
    COUNTRY = "country"; REGION = "region";   SHIP_SAME = "shipSame"
    SHIPPING = "shipping"; PROMO = "promo";   TERMS = "terms"

@dataclass(frozen=True)
class Changed: field: F
@dataclass(frozen=True)
class Toggled: field: F                 # у реальному коді — звузити до прапорців
DialogEvent = Changed | Toggled

def notify(self, e: DialogEvent) -> None:
    match e.field:
        case F.COUNTRY:  self.region.set_options(REGIONS.get(self.country.value, []))
        case F.SHIP_SAME:
            self.shipping.enabled = not self.ship_same.checked
            if self.ship_same.checked: self.shipping.value = ""
        case F.PROMO:    self.discount = PROMO.get(self.promo.value.strip(), 0)
        case F.EMAIL | F.PASSWORD | F.CONFIRM | F.REGION | F.SHIPPING | F.TERMS:
            pass                        # лише ревалідація
        case other:
            assert_never(other)         # новий F без гілки → перевіряч типів підкреслить
    self._revalidate()
