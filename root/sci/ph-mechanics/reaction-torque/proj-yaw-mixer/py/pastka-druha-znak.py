from enum import IntEnum


# Напрям обертання конкретного гвинта — фізичний факт, не вподобання.
class PropSpin(IntEnum):
    CCW = +1
    CW = -1


# Коефіцієнт рискання ВИВОДИТЬСЯ з напряму гвинта, а не вбивається вручну.
# Так неможливо випадково розійтися зі знаком реактивного моменту.
def yaw_coeff(spin):
    # CCW-гвинт штовхає раму CW → додатна команда yaw має пришвидшити його.
    return float(spin)   # PropSpin.CCW → +1, PropSpin.CW → −1


# Заповнити стовпець yaw матриці з фактичних напрямів моторів.
# rows — список рядків [throttle, roll, pitch, yaw]; правимо на місці.
def build_yaw_column(spin, rows):
    for i in range(4):
        rows[i][3] = yaw_coeff(spin[i])
