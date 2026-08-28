class Order:
    def __init__(self, total: float, policy: DiscountPolicy):
        self.total = total
        self._policy = policy                     # контекст тримає СТРАТЕГІЮ полем

    def final_price(self) -> float:
        return self.total - self._policy.discount(self)  # делегує, не знаючи, яка саме

    def set_policy(self, policy: DiscountPolicy) -> None:  # підмінити на льоту
        self._policy = policy

# збірка: хто саме — вирішується ЗЗОВНІ, в одному місці
order = Order(1000, VipDiscount())
order.final_price()               # 800
order.set_policy(SeasonalDiscount(0.30))
order.final_price()               # 700
