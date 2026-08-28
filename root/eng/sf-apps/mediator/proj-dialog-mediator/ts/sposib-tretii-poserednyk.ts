// РОБОТА виноситься геть від посередника:
class EmailField extends Field { get valid() { return EMAIL_RE.test(this.value); } }
class PasswordField extends Field { get valid() { return this.value.length >= 8; } }

class PromoService {                       // може ходити в мережу — посереднику байдуже
  check(code: string): number { return PROMO[code.trim()] ?? 0; }
}

// ПОСЕРЕДНИК лише координує: питає й вирішує, а не обчислює:
notify(e: DialogEvent) {
  if (e.field === "promo")   this.discount = this.promoSvc.check(this.promo.value);
  if (e.field === "country") this.region.setOptions(this.regions.of(this.country.value));
  this.submit.enabled =
    this.email.valid && this.password.valid &&        // ПИТАЄ поле, не рахує саме
    this.confirm.value === this.password.value &&
    this.address.valid && this.terms.checked;
}
