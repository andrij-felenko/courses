class BillingService:
    def calculate_invoice(self, amount: float, is_vip: bool, overdue_days: int) -> float:
        # Базова ставка знижки для VIP-клієнтів
        discount = 0.0
        if is_vip:
            discount = 0.15
        
        # Штраф за прострочення: якщо є заборгованість, знижка анулюється
        if overdue_days > 0:
            discount = 0.0
        
        # Нарахування податку (ПДВ 20%) після врахування знижки
        taxable_amount = amount * (1.0 - discount)
        total = taxable_amount * 1.20
        return round(total, 2)
