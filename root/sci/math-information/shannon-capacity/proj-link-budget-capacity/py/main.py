import math
from dataclasses import dataclass

@dataclass(frozen=True)
class LinkParams:
    name: str
    freq_hz: float        # несуча частота, Гц
    bandwidth_hz: float   # ширина смуги B, Гц
    tx_power_dbm: float   # потужність передавача P_tx, дБм
    tx_gain_dbi: float    # коефіцієнт підсилення антени передавача G_tx, дБі
    rx_gain_dbi: float    # коефіцієнт підсилення антени приймача G_rx, дБі
    path_loss_db: float   # втрати сигналу на трасі, дБ
    noise_fig_db: float   # коефіцієнт шуму приймача NF, дБ
    shannon_gap_db: float # розрив Шеннона для коду, дБ

@dataclass(frozen=True)
class LinkResult:
    noise_floor_dbm: float # поріг шуму, дБм
    rx_power_dbm: float    # потужність сигналу на вході приймача, дБм
    snr_db: float          # відношення сигнал/шум, дБ
    snr_linear: float      # відношення сигнал/шум у лінійній шкалі
    capacity_bps: float    # теоретична ємність за Шенноном, біт/с
    practical_bps: float   # практично досяжна швидкість, біт/с
    spectral_eff: float    # спектральна ефективність, біт/с/Гц

def calculate_link(link: LinkParams) -> LinkResult:
    thermal_density_dbm = -174.0  # спектральна густина теплового шуму при T = 290 K
    
    # 1. Повний рівень шуму у смузі: N_total = -174 + 10*log10(B) + NF
    noise_floor = thermal_density_dbm + 10.0 * math.log10(link.bandwidth_hz) + link.noise_fig_db
    
    # 2. Потужність на приймачі: P_rx = P_tx + G_tx + G_rx - PathLoss
    rx_power = link.tx_power_dbm + link.tx_gain_dbi + link.rx_gain_dbi - link.path_loss_db
    
    # 3. Відношення сигнал/шум
    snr_db = rx_power - noise_floor
    snr_lin = 10.0 ** (snr_db / 10.0)
    
    # 4. Теоретична ємність за Шенноном: C = B * log2(1 + SNR)
    capacity = link.bandwidth_hz * math.log2(1.0 + snr_lin)
    spectral_eff = capacity / link.bandwidth_hz
    
    # 5. Практична швидкість із розривом Гапа Gamma
    gap_lin = 10.0 ** (link.shannon_gap_db / 10.0)
    practical = link.bandwidth_hz * math.log2(1.0 + snr_lin / gap_lin)
    
    return LinkResult(
        noise_floor_dbm=noise_floor,
        rx_power_dbm=rx_power,
        snr_db=snr_db,
        snr_linear=snr_lin,
        capacity_bps=capacity,
        practical_bps=practical,
        spectral_eff=spectral_eff
    )

if __name__ == '__main__':
    scenarios = [
        LinkParams("Wi-Fi 6 (802.11ax, 5 ГГц, кімната 5 м)", 5.18e9, 80e6, 20.0, 3.0, 3.0, 68.0, 6.0, 2.0),
        LinkParams("5G NR (Sub-6 GHz, міська забудова 800 м)", 3.5e9, 100e6, 43.0, 15.0, 0.0, 112.0, 7.0, 2.0),
        LinkParams("LoRa (868 МГц, дальній лінк IoT 10 км)", 868e6, 125e3, 14.0, 2.0, 2.0, 140.0, 5.0, 1.5),
    ]
    
    for sc in scenarios:
        res = calculate_link(sc)
        print("====================================================")
        print(f"Сценарій: {sc.name}")
        print("----------------------------------------------------")
        print(f"  Частота / смуга:       {sc.freq_hz / 1e9:.2f} ГГц / {sc.bandwidth_hz / 1e6:.2f} МГц")
        print(f"  Рівень шуму N_total:   {res.noise_floor_dbm:.2f} дБм")
        print(f"  Прийнятий сигнал P_rx: {res.rx_power_dbm:.2f} дБм")
        print(f"  Відношення SNR:        {res.snr_db:.2f} дБ (x{res.snr_linear:.3f})")
        print(f"  Спектральна ефективн.: {res.spectral_eff:.2f} біт/с/Гц")
        print(f"  Ємність Шеннона C:     {res.capacity_bps / 1e6:.2f} Мбіт/с")
        print(f"  Практична швидкість:   {res.practical_bps / 1e6:.2f} Мбіт/с (розрив {sc.shannon_gap_db:.1f} дБ)\n")
