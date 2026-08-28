import re

REGIONS = {
    "Україна": ["Київська", "Львівська", "Одеська"],
    "Польща":  ["Мазовецьке", "Малопольське"],
    "США":     [],            # штат вводять окремо — список порожній
}
PROMO = {"WELCOME": 10, "BOOK5": 5}
EMAIL_RE = re.compile(r"\S+@\S+\.\S+")

class RegistrationDialog:
    def __init__(self) -> None:
        self.email     = Field("email", self)
        self.password  = Field("password", self)
        self.confirm   = Field("confirm", self)
        self.country   = Select("country", self)
        self.region    = Select("region", self)
        self.ship_same = Check("shipSame", self)
        self.shipping  = Field("shipping", self)
        self.promo     = Field("promo", self)
        self.terms     = Check("terms", self)
        self.submit_enabled = False
        self.discount = 0

    def notify(self, sender: str, event: str) -> None:   # УСЯ поведінка — тут
        if sender == "country":
            self.region.set_options(REGIONS.get(self.country.value, []))
        if sender == "shipSame":
            self.shipping.enabled = not self.ship_same.checked
            if self.ship_same.checked:
                self.shipping.value = ""
        if sender == "promo":
            self.discount = PROMO.get(self.promo.value.strip(), 0)
        self._revalidate()

    def _revalidate(self) -> None:
        filled = lambda f: f.value.strip() != ""
        region_ok = len(self.region.options) == 0 or filled(self.region)
        ship_ok   = self.ship_same.checked or filled(self.shipping)
        self.submit_enabled = bool(
            EMAIL_RE.match(self.email.value)
            and len(self.password.value) >= 8
            and self.confirm.value == self.password.value
            and filled(self.country) and region_ok and ship_ok
            and self.terms.checked)
