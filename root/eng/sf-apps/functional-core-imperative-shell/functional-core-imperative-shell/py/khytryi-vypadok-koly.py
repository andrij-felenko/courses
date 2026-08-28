from dataclasses import dataclass

# ── ЯДРО повертає ОПИС дій (дані), а не виконує їх ──
@dataclass(frozen=True)
class Email:  to: str; template: str
@dataclass(frozen=True)
class Credit: account: str; amount: int

def on_signup(user: User) -> list:
    effects = [Email(to=user.email, template="welcome")]
    if user.referred:                                   # рішення — тут, у ядрі
        effects.append(Credit(account=user.id, amount=100))
    return effects                                      # просто дані, нічого не сталося

# ── ОБОЛОНКА виконує описи; сама нічого не вирішує ──
async def run_signup(user: User) -> None:
    for e in on_signup(user):
        if isinstance(e, Email):  await mailer.send(e.to, e.template)
        if isinstance(e, Credit): await ledger.credit(e.account, e.amount)
