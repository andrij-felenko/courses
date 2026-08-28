def years_to_guess(bits: int, guesses_per_sec: float, live_sessions: int) -> float:
    """Сподіваний час (у роках) наосліп угадати БУДЬ-ЯКУ з live_sessions
    чинних сесій, коли номер має `bits` бітів ентропії від CSPRNG."""
    space = 2 ** bits                       # 2^b рівноймовірних значень
    guesses = space / live_sessions         # сподівано спроб до першого влучання = 2^b / S
    seconds = guesses / guesses_per_sec
    return seconds / (365.25 * 24 * 3600)

years_to_guess(bits=64, guesses_per_sec=10_000, live_sessions=100_000)
# → 584.5  (≈ 585 років)
years_to_guess(bits=32, guesses_per_sec=10_000, live_sessions=100_000)
# → 1.36e-07  (≈ 4.3 секунди — ось чому 32 біти нікуди не годяться)
