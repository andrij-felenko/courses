class OrderGateway:
    # ⚠️ додали предметне правило В шлюз — і це вже не шлюз
    def can_cancel(self):
        return self.status in ("new", "paid")

    def cancel(self):
        if not self.can_cancel():
            raise ValueError(f"замовлення в статусі {self.status!r} не скасувати")
        self.status = "cancelled"
        self.save()
