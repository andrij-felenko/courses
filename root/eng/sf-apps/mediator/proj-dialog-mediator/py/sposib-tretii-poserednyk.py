# РОБОТА виноситься геть від посередника:
class EmailField(Field):
    @property
    def valid(self) -> bool: return bool(EMAIL_RE.match(self.value))

class PasswordField(Field):
    @property
    def valid(self) -> bool: return len(self.value) >= 8

class PromoService:                        # може ходити в мережу — посереднику байдуже
    def check(self, code: str) -> int: return PROMO.get(code.strip(), 0)

# ПОСЕРЕДНИК лише координує: питає й вирішує, а не обчислює:
def notify(self, e) -> None:
    if e.field is F.PROMO:   self.discount = self.promo_svc.check(self.promo.value)
    if e.field is F.COUNTRY: self.region.set_options(self.regions.of(self.country.value))
    self.submit_enabled = (
        self.email.valid and self.password.valid          # ПИТАЄ поле, не рахує саме
        and self.confirm.value == self.password.value
        and self.address.valid and self.terms.checked)
