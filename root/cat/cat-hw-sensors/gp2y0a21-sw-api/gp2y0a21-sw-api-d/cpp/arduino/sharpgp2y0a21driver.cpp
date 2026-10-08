#include <Arduino.h>

class SharpGP2Y0A21Driver {
public:
    static constexpr uint8_t LUT_POINTS = 11;

    struct CalibNode {
        uint16_t voltage_mv;
        uint16_t distance_mm;
    };

    struct CalibProfile {
        CalibNode nodes[LUT_POINTS];
        uint16_t crc16;
    };

private:
    CalibProfile _profile;
    DistanceDiagnostics _diag;
    DistanceFilter _filter;
    bool _customCalibrated;

    static uint16_t computeCrc16(const uint8_t* data, size_t len) {
        uint16_t crc = 0xFFFF;
        for (size_t i = 0; i < len; i++) {
            crc ^= data[i];
            for (uint8_t j = 0; j < 8; j++) {
                crc = (crc & 1) ? ((crc >> 1) ^ 0xA001) : (crc >> 1);
            }
        }
        return crc;
    }

public:
    SharpGP2Y0A21Driver(float filterAlpha = 0.2f)
        : _filter(filterAlpha), _customCalibrated(false) {
        
        static const CalibNode defaultLut[LUT_POINTS] = {
            {3100, 100}, {2500, 120}, {2000, 150}, {1550, 200},
            {1250, 250}, {1050, 300}, {800,  400}, {650,  500},
            {520,  600}, {450,  700}, {400,  800}
        };
        memcpy(_profile.nodes, defaultLut, sizeof(defaultLut));
        _profile.crc16 = computeCrc16(reinterpret_cast<const uint8_t*>(_profile.nodes), sizeof(defaultLut));
    }

    bool setCalibration(const CalibProfile& profile) {
        uint16_t checkCrc = computeCrc16(reinterpret_cast<const uint8_t*>(profile.nodes), sizeof(profile.nodes));
        if (profile.crc16 != checkCrc) return false;

        memcpy(&_profile, &profile, sizeof(CalibProfile));
        _customCalibrated = true;
        return true;
    }

    SensorRangeStatus update(uint16_t rawAdcMv, uint16_t &outDistanceMm) {
        uint16_t filteredMv = _filter.update(rawAdcMv);
        SensorRangeStatus status = _diag.process(filteredMv);

        if (status != SensorRangeStatus::Ok) {
            if (status == SensorRangeStatus::BlindZone) {
                outDistanceMm = _profile.nodes[0].distance_mm;
            } else if (status == SensorRangeStatus::TooFar) {
                outDistanceMm = _profile.nodes[LUT_POINTS - 1].distance_mm;
            } else {
                outDistanceMm = 0;
            }
            return status;
        }

        for (size_t i = 0; i < LUT_POINTS - 1; ++i) {
            if (filteredMv <= _profile.nodes[i].voltage_mv && filteredMv >= _profile.nodes[i + 1].voltage_mv) {
                int32_t v1 = _profile.nodes[i].voltage_mv;
                int32_t v2 = _profile.nodes[i + 1].voltage_mv;
                int32_t d1 = _profile.nodes[i].distance_mm;
                int32_t d2 = _profile.nodes[i + 1].distance_mm;

                int32_t dist = d1 + ((static_cast<int32_t>(filteredMv) - v1) * (d2 - d1)) / (v2 - v1);
                outDistanceMm = static_cast<uint16_t>(dist);
                return SensorRangeStatus::Ok;
            }
        }

        outDistanceMm = _profile.nodes[LUT_POINTS - 1].distance_mm;
        return SensorRangeStatus::TooFar;
    }
};
