class CredentialsGroup implements Mediator {
  readonly id = "creds" as const;
  email    = new Field("email", this);
  password = new Field("password", this);
  confirm  = new Field("confirm", this);
  constructor(private parent: Mediator) {}

  notify(_sender: FieldId, _e: string) {          // як ПОСЕРЕДНИК своїх полів
    this.confirm.error =
      this.confirm.value && this.confirm.value !== this.password.value
        ? "паролі не збігаються" : "";
    this.parent.notify(this.id, "changed");       // як КОЛЕГА координатора
  }
  get valid() {
    return EMAIL_RE.test(this.email.value)
        && this.password.value.length >= 8
        && this.confirm.value === this.password.value;
  }
}

class RegistrationDialog implements Mediator {
  creds   = new CredentialsGroup(this);
  address = new AddressGroup(this);               // симетрична: country/region/shipSame/shipping
  terms   = new Check("terms", this);
  submit  = { enabled: false };

  notify(_sender: FieldId, _e: string) {          // ЖОДНОЇ польової логіки — сама координація
    this.submit.enabled = this.creds.valid && this.address.valid && this.terms.checked;
  }
}
