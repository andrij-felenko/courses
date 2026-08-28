#include <libmm-glib.h>
#include <iostream>
#include <memory>

void read_signal_metrics(MMModemSignal *signal_object) {
    // Використання RAII-обгортки для управління ресурсами GLib об'єкта
    using LteSignalPtr = std::unique_ptr<MMSignalLte, decltype([](MMSignalLte* p) { g_object_unref(p); })>;
    LteSignalPtr lte_info{mm_modem_signal_get_lte(signal_object)};

    if (lte_info) {
        const double rsrp = mm_signal_lte_get_rsrp(lte_info.get());
        const double rsrq = mm_signal_lte_get_rsrq(lte_info.get());
        const double rssi = mm_signal_lte_get_rssi(lte_info.get());
        const double snr  = mm_signal_lte_get_snr(lte_info.get());

        std::cout << "LTE Metrics -> RSRP: " << rsrp << " dBm, RSRQ: " << rsrq
                  << " dB, RSSI: " << rssi << " dBm, SINR: " << snr << " dB\n";
    }
}
