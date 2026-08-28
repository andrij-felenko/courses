# Головна функція: тягне байти з кільцевого буфера. Коли готовий валідний кадр —
# заповнює out (сирі канали + прапорці) і повертає (out, us[16]); інакше None.
def sbus_read(out):
    frame = sbus_poll()
    if frame is None:                       # цілого кадру ще нема
        return None

    out.ch = sbus_unpack_channels(frame[1:])    # 16 каналів із frame[1..22]
    sbus_read_flags(frame[23], out)             # прапорці з байта 23

    us = [sbus_raw_to_us(c) for c in out.ch]    # сире → мкс

    return out, us
