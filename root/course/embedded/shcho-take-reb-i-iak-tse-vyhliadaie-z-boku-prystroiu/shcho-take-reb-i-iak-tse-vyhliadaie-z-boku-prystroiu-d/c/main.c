#include <stdint.h>
#include <stdbool.h>

typedef enum {
    LINK_STATE_OK,
    LINK_STATE_JAMMED_SPOT,
    LINK_STATE_JAMMED_BARRAGE,
    LINK_STATE_PULSE_JAMMING
} link_ew_state_t;

link_ew_state_t classify_rf_telemetry(int16_t rssi_dbm, int8_t snr_db, 
                                      uint8_t agc_gain_code, bool sync_hit, 
                                      bool crc_err, uint8_t per_pct) {
    /* 1. Надвисокий RSSI та скинутий AGC при відсутності синхронізації — засліплення LNA */
    if (rssi_dbm >= -45 && agc_gain_code <= 25 && !sync_hit) {
        return LINK_STATE_JAMMED_BARRAGE;
    }
    
    /* 2. Високий RSSI, але пакетні втрати перевищують 80% — прицільне глушіння */
    if (rssi_dbm >= -70 && per_pct >= 80 && snr_db < -5) {
        return LINK_STATE_JAMMED_SPOT;
    }
    
    /* 3. Преамбула захоплена, але масові помилки CRC при середньому RSSI — імпульсна завада */
    if (sync_hit && crc_err && per_pct >= 50) {
        return LINK_STATE_PULSE_JAMMING;
    }
    
    return LINK_STATE_OK;
}
