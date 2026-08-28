class CredentialsGroup:
    def __init__(self, parent) -> None:
        self.id, self._parent = "creds", parent
        self.email    = Field("email", self)
        self.password = Field("password", self)
        self.confirm  = Field("confirm", self)

    def notify(self, sender: str, e: str) -> None:      # як ПОСЕРЕДНИК полів
        self.confirm.error = ("паролі не збігаються"
            if self.confirm.value and self.confirm.value != self.password.value else "")
        self._parent.notify(self.id, "changed")         # як КОЛЕГА координатора

    @property
    def valid(self) -> bool:
        return bool(EMAIL_RE.match(self.email.value)
                    and len(self.password.value) >= 8
                    and self.confirm.value == self.password.value)

class RegistrationDialog:
    def __init__(self) -> None:
        self.creds   = CredentialsGroup(self)
        self.address = AddressGroup(self)               # симетрична група доставки
        self.terms   = Check("terms", self)
        self.submit_enabled = False

    def notify(self, sender: str, e: str) -> None:      # сама координація, без полів
        self.submit_enabled = (self.creds.valid and self.address.valid
                               and self.terms.checked)
