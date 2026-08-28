import hmac, hashlib, time, math, random
from enum import Enum

class CircuitState(Enum):
    CLOSED = 1
    OPEN = 2
    HALF_OPEN = 3

class CircuitBreaker:
    def __init__(self, threshold: int = 3, reset_timeout_sec: float = 10.0):
        self.threshold = threshold
        self.reset_timeout_sec = reset_timeout_sec
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.next_attempt_time = 0.0

    def can_execute(self, now: float) -> bool:
        if self.state == CircuitState.OPEN:
            if now >= self.next_attempt_time:
                self.state = CircuitState.HALF_OPEN
                return True
            return False
        return True

    def on_success(self):
        self.failure_count = 0
        self.state = CircuitState.CLOSED

    def on_failure(self, now: float):
        self.failure_count += 1
        if self.failure_count >= self.threshold:
            self.state = CircuitState.OPEN
            self.next_attempt_time = now + self.reset_timeout_sec

class EgressGateway:
    def __init__(self):
        self.cb = CircuitBreaker()

    def process_message(self, msg_id: str, url: str, payload: str, secret: str, attempt: int, max_attempts: int, transport_fn) -> str:
        now = time.time()
        if not self.cb.can_execute(now):
            return "RETRY"

        signed_payload = f"{int(now)}.{payload}".encode()
        sig = hmac.new(secret.encode(), signed_payload, hashlib.sha256).hexdigest()
        headers = {
            "Content-Type": "application/json",
            "X-Signature": f"t={int(now)},v1={sig}",
            "X-Idempotency-Key": msg_id,
        }

        try:
            status_code = transport_fn(url, payload, headers)
            if 200 <= status_code < 300:
                self.cb.on_success()
                return "SENT"
            if 400 <= status_code < 500 and status_code != 429:
                return "DLQ"
            self.cb.on_failure(time.time())
        except Exception:
            self.cb.on_failure(time.time())

        if attempt + 1 >= max_attempts:
            return "DLQ"
        return "RETRY"

    def calculate_backoff(self, attempt: int, base_sec: float = 0.1, max_sec: float = 5.0) -> float:
        temp = min(max_sec, base_sec * (2 ** attempt))
        jitter = temp * 0.5 * random.random()
        return temp + jitter
