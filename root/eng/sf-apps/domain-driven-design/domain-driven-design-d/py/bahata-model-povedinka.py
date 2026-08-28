# Знекровлена модель: сам поліс нічого не вміє, лише зберігає поля
class Policy:
    def __init__(self, due_date):
        self.status = "active"
        self.balance = 0
        self.due_date = due_date

# Правило живе ЗЗОВНІ, у сервісі — і будь-хто може забути його викликати
class PolicyService:
    def enter_grace_period(self, p: Policy) -> None:
        # хто гарантує, що всі перевірки тут, а не в трьох інших сервісах?
        if p.status != "active":
            raise ValueError("wrong state")
        p.status = "grace"
