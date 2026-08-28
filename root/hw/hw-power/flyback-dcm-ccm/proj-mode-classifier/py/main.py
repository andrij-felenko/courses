# Оцінка режиму flyback за виміряним струмом навантаження.
# Усе у фіксованій комі Q16.16; величини заздалегідь відмасштабовані.
# lm_uH — намагнічувальна індукт. первинної, мкГн; n_q16 — Np/Ns у Q16.16.
# Python має довгі цілі, тож переповнення тут немає — але той самий цілочисловий
# тракт лишаємо навмисно, щоб код був дзеркалом прошивки (крок за кроком той самий).

from enum import IntEnum


class FbMode(IntEnum):
    DCM = 0
    BCM = 1
    CCM = 2


def boundary_iout_ma(vin_v, d_q16, n_q16, lm_uH, f_khz):
    """Межовий вихідний струм (мА) за поточної робочої точки.

    Iбм[А] = n·Vin·D·(1−D) / (2·Lm·f).  Розкриваємо масштаби:
      n = n_q16/2^16 ;  D·(1−D) = dd/2^16 ;  Lm[Гн]=lm_uH·1e-6 ;  f[Гц]=f_khz·1e3.
    Отже Iбм[мА] = n_q16·Vin·dd·1e6 / ( 2^32 · 2 · lm_uH · f_khz ).
    """
    dd = (d_q16 * ((1 << 16) - d_q16)) >> 16          # D·(1−D) у Q16.16

    num = n_q16 * vin_v * dd * 1_000_000
    den = (1 << 32) * 2 * lm_uH * f_khz
    if den == 0:
        return 0
    return num // den                                 # цілочислове ділення, як у C


def classify_mode(iout_ma, vin_v, d_q16, n_q16, lm_uH, f_khz):
    """Класифікація з гістерезисом ±9%, щоб не «тремтіло» на самій межі."""
    ibnd = boundary_iout_ma(vin_v, d_q16, n_q16, lm_uH, f_khz)
    hi = ibnd + (ibnd >> 4) + (ibnd >> 5)             # +~9%
    lo = ibnd - (ibnd >> 4) - (ibnd >> 5)             # −~9%
    if iout_ma > hi:
        return FbMode.CCM                             # струм вищий за межу → поличка є
    if iout_ma < lo:
        return FbMode.DCM                             # нижчий → осердя порожніє
    return FbMode.BCM                                 # у вузькій смузі — на межі
