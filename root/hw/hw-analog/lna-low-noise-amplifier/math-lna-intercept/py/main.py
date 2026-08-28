from dataclasses import dataclass

# Усе в дБ / дБм. Модель — третій порядок (нахили 1:1 і 3:1).
@dataclass
class LnaLin:
    iip3_dBm: float            # точка перетину 3-го порядку, зведена до ВХОДУ
    gain_dB: float             # підсилення каскаду
    noise_floor_out_dBm: float # шумова підлога приймача на ВИХОДІ

# Наскільки завада IM3 нижча за корисний сигнал (у dBc), за рівня сусіда p_in:
#   розрив = 2·(IIP3 − Pin)
def im3_below_carrier_dBc(d: LnaLin, p_in_dBm: float) -> float:
    return 2.0 * (d.iip3_dBm - p_in_dBm)         # завжди додатне число дБ «вниз»

# Абсолютний рівень IM3-завади на ВИХОДІ (дБм):
#   корисний на виході = Pin + G;  завада нижча за нього на розрив
def im3_output_level_dBm(d: LnaLin, p_in_dBm: float) -> float:
    carrier_out = p_in_dBm + d.gain_dB           # вихідний корисний тон
    return carrier_out - im3_below_carrier_dBc(d, p_in_dBm)
    # рівносильно: 3*Pin − 2*IIP3 + G

# Запас завади над шумовою підлогою (дБ): >0 — завада вилазить з-під підлоги (шкодить);
#   <0 — тоне в шумі (нешкідлива на цьому рівні сусідів).
def im3_margin_over_floor_dB(d: LnaLin, p_in_dBm: float) -> float:
    return im3_output_level_dBm(d, p_in_dBm) - d.noise_floor_out_dBm

def demo() -> None:
    lna = LnaLin(
        iip3_dBm            =-10.0,   # IIP3 = −10 дБм
        gain_dB             = 18.0,  # G = 18 дБ
        noise_floor_out_dBm =-95.0,  # підлога на виході
    )
    p_in = -30.0                     # два сусіди по −30 дБм

    below   = im3_below_carrier_dBc(lna, p_in)   # 2·(−10 −(−30)) = 40 дБ
    im3_out = im3_output_level_dBm(lna, p_in)    # (−30+18) − 40 = −52 дБм
    margin  = im3_margin_over_floor_dB(lna, p_in)# −52 −(−95) = +43 дБ

    # below   ≈ 40 дБ   — завада на 40 дБ під корисним сигналом
    # im3_out ≈ −52 дБм — абсолютний рівень завади на виході
    # margin  ≈ +43 дБ  — завада НА 43 дБ ВИЩЕ підлоги → виразно шкодить!

    # Який рівень сусідів каскад іще терпить? Прирівняймо заваду до підлоги:
    #   3*Pin − 2*IIP3 + G = floor  →  Pin = (floor + 2*IIP3 − G)/3
    p_in_max = (lna.noise_floor_out_dBm + 2.0*lna.iip3_dBm - lna.gain_dB) / 3.0
    # = (−95 + 2·(−10) − 18)/3 = (−95 −20 −18)/3 = −133/3 ≈ −44.3 дБм
    # Тобто поки сусіди слабші за ≈ −44 дБм, завада сидить під підлогою.
