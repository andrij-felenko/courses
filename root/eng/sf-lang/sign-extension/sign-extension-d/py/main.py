# Знакове розширення value з num_bits бітів.
def sign_extend(value, num_bits):
    m = 1 << (num_bits - 1)          # біт-знак на місці
    return (value ^ m) - m           # (v ^ M) − M

raw = 0x0FFF                         # 12 бітів усі одиниці = −1
print(sign_extend(raw, 12))         # −1  (а не 4095!)

raw = 0x07FF                         # найбільше додатне 12-бітне
print(sign_extend(raw, 12))         # 2047
