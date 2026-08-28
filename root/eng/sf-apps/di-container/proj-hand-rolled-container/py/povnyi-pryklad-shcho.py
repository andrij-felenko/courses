# ── «інфраструктура»: несправжня, але поводиться чесно ──
class Config:
    def __init__(self):                       # листок: нічого не просить
        self.log_path = "/var/log/app.log"

class Logger:
    def __init__(self):                       # листок
        self.lines = []
    def info(self, msg): self.lines.append(msg)

class HttpClient:
    def __init__(self, config: Config, logger: Logger):
        self.config, self.logger = config, logger

class StripeGateway:
    def __init__(self, http: HttpClient):
        self.http = http
    def charge(self, cents): self.http.logger.info(f"charge {cents}")

class PaymentService:
    def __init__(self, gateway: StripeGateway, logger: Logger):
        self.gateway, self.logger = gateway, logger
    def pay(self, cents):
        self.gateway.charge(cents)
        self.logger.info("paid")

# ── композиційний корінь: реєстрація + один resolve на верхівку ──
c = (Container()
     .bind(HttpClient,     HttpClient)
     .bind(StripeGateway,  StripeGateway)
     .bind(PaymentService, PaymentService))

payments = c.resolve(PaymentService)          # обійшов увесь граф, зібрав від листя до кореня
payments.pay(500)

# ── доказ, що Logger — ОДИН на весь граф (кеш спрацював) ──
assert payments.logger is payments.gateway.http.logger    # той самий примірник!
print(payments.logger.lines)   # ['charge 500', 'paid'] — обидва рядки в ОДНОМУ журналі
