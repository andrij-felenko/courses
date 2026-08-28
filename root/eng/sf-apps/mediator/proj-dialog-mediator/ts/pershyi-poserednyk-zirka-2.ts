const REGIONS: Record<string, string[]> = {
  "Україна": ["Київська", "Львівська", "Одеська"],
  "Польща":  ["Мазовецьке", "Малопольське"],
  "США":     [],            // штат вводять окремо — список порожній
};
const PROMO: Record<string, number> = { WELCOME: 10, BOOK5: 5 };
const EMAIL_RE = /\S+@\S+\.\S+/;

class RegistrationDialog implements Mediator {
  email    = new Field("email", this);
  password = new Field("password", this);
  confirm  = new Field("confirm", this);
  country  = new Select("country", this);
  region   = new Select("region", this);
  shipSame = new Check("shipSame", this);
  shipping = new Field("shipping", this);
  promo    = new Field("promo", this);
  terms    = new Check("terms", this);
  submit   = { enabled: false };
  discount = 0;

  notify(sender: FieldId, _event: string) {      // УСЯ поведінка вікна — тут
    if (sender === "country")
      this.region.setOptions(REGIONS[this.country.value] ?? []);
    if (sender === "shipSame") {
      this.shipping.enabled = !this.shipSame.checked;
      if (this.shipSame.checked) this.shipping.value = "";
    }
    if (sender === "promo")
      this.discount = PROMO[this.promo.value.trim()] ?? 0;
    this.revalidate();
  }

  private revalidate() {
    const filled = (f: Field) => f.value.trim() !== "";
    const regionOk = this.region.options.length === 0 || filled(this.region);
    const shipOk   = this.shipSame.checked || filled(this.shipping);
    this.submit.enabled =
      EMAIL_RE.test(this.email.value) &&
      this.password.value.length >= 8 &&
      this.confirm.value === this.password.value &&
      filled(this.country) && regionOk && shipOk && this.terms.checked;
  }
}
