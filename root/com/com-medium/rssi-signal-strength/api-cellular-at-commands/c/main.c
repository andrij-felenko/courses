#include <libmm-glib.h>

void read_signal_metrics(MMModemSignal *signal_object) {
    MMSignalLte *lte_info = mm_modem_signal_get_lte(signal_object);
    if (lte_info) {
        gdouble rsrp = mm_signal_lte_get_rsrp(lte_info);
        gdouble rsrq = mm_signal_lte_get_rsrq(lte_info);
        gdouble rssi = mm_signal_lte_get_rssi(lte_info);
        gdouble snr  = mm_signal_lte_get_snr(lte_info);

        g_print("LTE Metrics -> RSRP: %.1f dBm, RSRQ: %.1f dB, RSSI: %.1f dBm, SINR: %.1f dB\n",
                rsrp, rsrq, rssi, snr);
        g_object_unref(lte_info);
    }
}
