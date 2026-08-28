#include <cstdint>

enum class LinkEwState : uint8_t {
    Ok,
    JammedSpot,
    JammedBarrage,
    PulseJamming
};

[[nodiscard]] constexpr LinkEwState classifyRfTelemetry(
    int16_t rssi_dbm, int8_t snr_db, uint8_t agc_gain_code,
    bool sync_hit, bool crc_err, uint8_t per_pct) noexcept 
{
    // 1. Надвисокий RSSI та скинутий AGC при відсутності синхронізації — засліплення LNA
    if (rssi_dbm >= -45 && agc_gain_code <= 25 && !sync_hit) {
        return LinkEwState::JammedBarrage;
    }
    
    // 2. Високий RSSI, але пакетні втрати перевищують 80% — прицільне глушіння
    if (rssi_dbm >= -70 && per_pct >= 80 && snr_db < -5) {
        return LinkEwState::JammedSpot;
    }
    
    // 3. Преамбула захоплена, але масові помилки CRC при середньому RSSI — імпульсна завада
    if (sync_hit && crc_err && per_pct >= 50) {
        return LinkEwState::PulseJamming;
    }
    
    return LinkEwState::Ok;
}
