#include <math.h>

typedef struct {
    double temp_c;
    double vcc_volts;
    double tx_bias_ma;
    double tx_power_dbm;
    double rx_power_dbm;
} dom_data_t;

dom_data_t decode_sff8472_dom(const unsigned char *a2_page_bytes) {
    dom_data_t dom;
    
    /* Температура: 16-біт signed integer */
    short raw_temp = (short)((a2_page_bytes[96] << 8) | a2_page_bytes[97]);
    dom.temp_c = (double)raw_temp / 256.0;

    /* Напруга Vcc: 16-біт unsigned integer */
    unsigned short raw_vcc = (unsigned short)((a2_page_bytes[98] << 8) | a2_page_bytes[99]);
    dom.vcc_volts = (double)raw_vcc / 10000.0;

    /* Струм накачки: 16-біт unsigned integer */
    unsigned short raw_bias = (unsigned short)((a2_page_bytes[100] << 8) | a2_page_bytes[101]);
    dom.tx_bias_ma = (double)raw_bias * 0.002;

    /* Потужність Tx у мкВт -> переведення в дБм */
    unsigned short raw_tx = (unsigned short)((a2_page_bytes[102] << 8) | a2_page_bytes[103]);
    double tx_mw = (double)raw_tx * 0.0001;
    dom.tx_power_dbm = (tx_mw > 0.0) ? 10.0 * log10(tx_mw) : -40.0;

    /* Потужність Rx у мкВт -> переведення в дБм */
    unsigned short raw_rx = (unsigned short)((a2_page_bytes[104] << 8) | a2_page_bytes[105]);
    double rx_mw = (double)raw_rx * 0.0001;
    dom.rx_power_dbm = (rx_mw > 0.0) ? 10.0 * log10(rx_mw) : -40.0;

    return dom;
}
