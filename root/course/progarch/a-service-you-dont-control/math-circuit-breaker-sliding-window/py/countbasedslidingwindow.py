class CountBasedSlidingWindow:
    def __init__(self, size: int, failure_rate_threshold: float):
        self.size = size
        self.threshold = failure_rate_threshold
        self.buffer = [0] * size
        self.head = 0
        self.total_failures = 0
        self.total_recorded = 0

    def record_call(self, is_failure: bool) -> None:
        new_val = 1 if is_failure else 0
        old_val = self.buffer[self.head]
        
        # Заміщуємо найстаріше значення та оновлюємо суму за O(1)
        self.buffer[self.head] = new_val
        self.total_failures += new_val - old_val
        self.head = (self.head + 1) % self.size
        
        if self.total_recorded < self.size:
            self.total_recorded += 1

    def failure_rate(self) -> float:
        if self.total_recorded == 0:
            return 0.0
        return self.total_failures / self.total_recorded

    def should_trip(self) -> bool:
        if self.total_recorded < self.size:
            return False  # Очікуємо повного заповнення буфера
        return self.failure_rate() >= self.threshold
