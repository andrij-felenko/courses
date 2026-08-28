DISCORD_EPOCH = 1_420_070_400_000          # 1 січня 2015, у мс від епохи Unix
BUCKET_MS     = 10 * 24 * 60 * 60 * 1000    # 864_000_000 — 10 діб

def ms_since_epoch(id: int) -> int:
    return id >> 22                          # старші 42 біти — годинник

def bucket_of(id: int) -> int:
    return ms_since_epoch(id) // BUCKET_MS   # ціле ділення — номер вікна

def unix_ms(id: int) -> int:
    return ms_since_epoch(id) + DISCORD_EPOCH

# Наскрізний приклад із розбору:
mid = 181_193_932_800_000_000
assert ms_since_epoch(mid) == 43_200_000_000
assert bucket_of(mid) == 50
assert unix_ms(mid) == 1_463_270_400_000     # ~травень 2016
