import time

class TimeBasedSlidingWindow:
    def __init__(self, window_duration_sec: float, num_buckets: int):
        self.window_duration = window_duration_sec
        self.num_buckets = num_buckets
        self.bucket_duration = window_duration_sec / num_buckets
        
        # Кожен кошик: [epoch_index, total_calls, failed_calls]
        self.buckets = [[0, 0, 0] for _ in range(num_buckets)]

    def _get_current_epoch(self) -> int:
        return int(time.time() / self.bucket_duration)

    def record_call(self, is_failure: bool) -> None:
        epoch = self._get_current_epoch()
        idx = epoch % self.num_buckets
        bucket = self.buckets[idx]

        # Якщо кошик застарів, очищаємо його за O(1)
        if bucket[0] != epoch:
            bucket[0] = epoch
            bucket[1] = 0
            bucket[2] = 0

        bucket[1] += 1
        if is_failure:
            bucket[2] += 1

    def get_metrics(self) -> tuple[int, int, float]:
        current_epoch = self._get_current_epoch()
        min_valid_epoch = current_epoch - self.num_buckets + 1

        total_calls = 0
        total_failures = 0

        # Агрегація за O(B) де B фіксоване
        for epoch, calls, fails in self.buckets:
            if epoch >= min_valid_epoch and epoch <= current_epoch:
                total_calls += calls
                total_failures += fails

        if total_calls == 0:
            return 0, 0, 0.0

        failure_rate = total_failures / total_calls
        return total_calls, total_failures, failure_rate
