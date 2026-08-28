# Додатковий запобіжник: скид парсера за тишею на лінії.
# now_us — монотонний час у мкс. Кличемо замість push().
# (self.frame_start_us ініціалізуємо нулем у __init__)
CRSF_FRAME_TIMEOUT_US = 1750   # трохи більше за час 64 Б на 420k

def push_timed(parser, byte, now_us):
    if (parser.state != CrsfState.ST_SYNC and
            ((now_us - parser.frame_start_us) & 0xFFFFFFFF) > CRSF_FRAME_TIMEOUT_US):
        parser.reset()          # задовга пауза → кинути недобраний кадр
    if parser.state == CrsfState.ST_SYNC:
        parser.frame_start_us = now_us    # засікаємо початок нового кадру
    parser.push(byte)
