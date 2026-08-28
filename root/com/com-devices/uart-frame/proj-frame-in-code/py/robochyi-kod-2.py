from dataclasses import dataclass

@dataclass
class RxResult:
    data: int = 0              # зібраний байт
    framing_error: bool = False  # стоп був не «1»
    parity_error: bool = False   # парність не збіглася

# bits[0] = старт, bits[1..8] = дані (D0..D7), bits[9] = парність, bits[10] = стоп
# (для 8N1 parity пропускаємо: передати mode = Parity.NONE і зсунути стоп на 9)
def parse_frame(bits, mode: Parity) -> RxResult:
    r = RxResult()

    data = 0
    for i in range(8):
        data |= (bits[1 + i] & 1) << i     # D0 першим → лягає в біт 0
    r.data = data

    idx = 9                                 # наступна позиція після даних
    if mode is not Parity.NONE:
        expected = parity_bit(data, mode)
        if (bits[idx] & 1) != expected:
            r.parity_error = True           # прийнятий P не збігся з перерахованим
        idx += 1                            # стоп зсувається на 10

    if (bits[idx] & 1) != 1:                # стоп ЗОБОВ'ЯЗАНИЙ бути «1»
        r.framing_error = True              # інакше межі кадру втрачено

    return r
