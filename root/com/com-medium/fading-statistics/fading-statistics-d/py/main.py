import math

def rayleigh_outage_probability(snr_avg_db, snr_th_db):
    gamma_avg = 10.0 ** (snr_avg_db / 10.0)
    gamma_th  = 10.0 ** (snr_th_db / 10.0)
    return 1.0 - math.exp(-gamma_th / gamma_avg)

def required_fading_margin_db(reliability):
    outage_target = 1.0 - reliability
    margin_linear = -1.0 / math.log(1.0 - outage_target)
    return 10.0 * math.log10(margin_linear)

snr_avg_db = 25.0
snr_th_db = 10.0

p_out = rayleigh_outage_probability(snr_avg_db, snr_th_db)
margin_999 = required_fading_margin_db(0.999)

print(f"Середнє SNR: {snr_avg_db:.1f} дБ, Поріг SNR: {snr_th_db:.1f} дБ")
print(f"Поточна імовірність виходу з ладу: {p_out * 100.0:.4f} %")
print(f"Необхідний запас на завмирання для надійності 99.9%: {margin_999:.2f} дБ")
