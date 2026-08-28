def send_command(cmd: Command) -> Result:
    key = uuid4().hex                         # ОДИН ключ на команду — крізь усі спроби
    deadline = monotonic() + 10.0             # весь бюджет — 10 с, монотонний годинник
    backoff = 0.5
    while True:
        left = deadline - monotonic()
        if left <= 0:
            raise Timeout("бюджет вичерпано")  # чесне «не знаю»
        try:
            return post("/hub/command", cmd, key, timeout=min(left, 3.0))
        except NetworkError as e:
            if not is_retryable(e):           # 4xx — не мережа, повторювати нема сенсу
                raise
            pause = min(backoff + random() * backoff, left)
            sleep(pause)                       # відступ + розкид
            backoff *= 2                        # 0.5 → 1 → 2 → 4 с
