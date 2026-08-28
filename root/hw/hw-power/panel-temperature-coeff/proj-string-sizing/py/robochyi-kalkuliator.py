from dataclasses import dataclass
from math import floor, ceil


@dataclass
class Panel:
    voc: float      # Voc за STC, В
    vmpp: float     # Vmpp за STC, В
    pmax: float     # Pmax за STC, Вт
    b_voc: float    # βVoc,  %/°C  (від'ємний)
    b_vmpp: float   # βVmpp, %/°C  (від'ємний; нема в даташиті → став b_voc)
    g_pmax: float   # γPmax, %/°C  (від'ємний)
    noct: float     # NOCT, °C


@dataclass
class Inverter:
    v_max: float        # абсолютний максимум входу, В
    v_mppt_min: float   # нижня межа вікна MPPT, В


@dataclass
class Site:
    t_air_cold: float        # рекордний місцевий мінімум повітря, °C
    t_air_hot: float         # розрахунковий гарячий максимум повітря, °C
    ghi_hot: float = 1000.0  # освітленість у гарячий полудень, Вт/м²


def cell_temp(t_air, noct, ghi):
    """Температура елемента через NOCT (лінійна теплова модель)."""
    return t_air + (noct - 20.0) * ghi / 800.0


def scale(v_stc, coeff_pct, t_cell):
    """Значення за температурою елемента: лінійний температурний коефіцієнт."""
    return v_stc * (1.0 + coeff_pct / 100.0 * (t_cell - 25.0))


def size_string(p: Panel, inv: Inverter, s: Site):
    # ── ХОЛОДНИЙ бік: стеля напруги. Voc, елемент ≈ повітря (сонце ще низьке) ──
    t_cold = s.t_air_cold                       # без NOCT: гріти нема чому
    voc_cold = scale(p.voc, p.b_voc, t_cold)    # Voc однієї панелі на морозі
    n_max = floor(inv.v_max / voc_cold)         # більше — пробій входу

    # ── ГАРЯЧИЙ бік: підлога напруги. Vmpp, елемент через NOCT ──
    t_hot = cell_temp(s.t_air_hot, p.noct, s.ghi_hot)
    vmpp_hot = scale(p.vmpp, p.b_vmpp, t_hot)   # Vmpp однієї панелі на спеці
    n_min = ceil(inv.v_mppt_min / vmpp_hot)     # менше — випадаєш із вікна MPPT

    # ── Втрата потужності на спеці ──
    pmax_hot = scale(p.pmax, p.g_pmax, t_hot)
    loss_pct = (1.0 - pmax_hot / p.pmax) * 100.0

    return {
        "t_cold": t_cold, "voc_cold": voc_cold, "n_max": n_max,
        "t_hot": t_hot, "vmpp_hot": vmpp_hot, "n_min": n_min,
        "pmax_hot": pmax_hot, "loss_pct": loss_pct,
    }
