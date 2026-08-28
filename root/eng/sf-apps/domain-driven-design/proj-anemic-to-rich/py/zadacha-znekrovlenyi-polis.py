# Знекровлена модель: сам поліс нічого не вміє, лише тримає поля навстіж
class Policy:
    def __init__(self):
        self.id = ""
        self.status = "draft"        # "draft" | "active" | "grace" | "cancelled"
        self.premium = 0             # сума внеску, у копійках? у гривнях? хтозна
        self.currency = "UAH"
        self.due_date = None
        self.payments = []           # суми платежів, теж голі числа


# Правило живе ЗЗОВНІ, у сервісі — і кожен викликач тримає свій уламок
class PolicyService:
    def activate(self, p):
        if p.status != "draft":
            raise ValueError("wrong state")
        p.status = "active"

    def enter_grace_period(self, p):
        # тут ЗАБУЛИ перевірити, що поліс узагалі активний
        p.status = "grace"

    def add_payment(self, p, amount):
        p.payments.append(amount)    # жодної перевірки: додасться й від'ємне
