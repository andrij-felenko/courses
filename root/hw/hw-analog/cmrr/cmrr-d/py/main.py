import math

# Похибка на вході (В) від синфазної завади vcm (В)
# за паспортного cmrr_db (дБ).
def cm_error_input(vcm, cmrr_db):
    ratio = 10.0 ** (cmrr_db / 20.0)  # дБ → у разах
    return vcm / ratio                # зведена до входу завада

# Приклад: 1 В синфазного, CMRR = 100 дБ
# cm_error_input(1.0, 100.0) -> 1e-05 В = 10 мкВ
