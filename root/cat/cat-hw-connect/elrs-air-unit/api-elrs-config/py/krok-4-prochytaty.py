def parse_link_stats(payload: bytes) -> dict:
    """Тіло кадру 0x14 (10 байтів) → метрики здоров'я лінка."""
    def s8(v):                          # байт → знаковий int8 (250 → −6)
        return v - 256 if v >= 128 else v
    return {
        "up_rssi_ant1": -payload[0],    # висхідний RSSI, антена 1 (дБм, ЗАВЖДИ від'ємний)
        "up_rssi_ant2": -payload[1],    # висхідний RSSI, антена 2 (дБм)
        "up_lq":         payload[2],    # висхідна якість лінка (%, 0…100)
        "up_snr":        s8(payload[3]), # висхідний SNR (дБ, ЗНАКОВИЙ!)
        "active_ant":    payload[4],    # активна антена (0 / 1)
        "rf_mode":       payload[5],    # радіорежим (профіль швидкості)
        "up_tx_power":   payload[6],    # потужність передавача (код)
        "dn_rssi":      -payload[7],    # низхідний RSSI (дБм)
        "dn_lq":         payload[8],    # низхідна якість лінка (%)
        "dn_snr":        s8(payload[9]),# низхідний SNR (дБ, ЗНАКОВИЙ!)
    }

# Виловивши кадр type=0x14 тим самим циклом, що в sniff():
#   stats = parse_link_stats(frame[3:3 + 10])
#   print(f"RSSI {stats['up_rssi_ant1']} дБм, LQ {stats['up_lq']}%, "
#         f"SNR {stats['up_snr']} дБ")
# Друкує напр.: RSSI -63 дБм, LQ 100%, SNR 9 дБ
