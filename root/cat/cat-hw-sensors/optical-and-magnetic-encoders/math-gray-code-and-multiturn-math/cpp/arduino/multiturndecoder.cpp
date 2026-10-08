#include <Arduino.h>

class MultiTurnDecoder {
private:
    uint8_t _st_bits;
    uint8_t _mt_bits;
    float _gear_ratio;

public:
    MultiTurnDecoder(uint8_t st_bits, uint8_t mt_bits, float gear_ratio)
        : _st_bits(st_bits), _mt_bits(mt_bits), _gear_ratio(gear_ratio) {}

    struct Result {
        uint32_t singleTurn;
        uint32_t multiTurn;
        float angleRadian;
        float outputAngleRadian;
    };

    Result decode(uint64_t rawFrame) const {
        Result res;
        uint64_t stMask = (1ULL << _st_bits) - 1ULL;
        res.singleTurn = static_cast<uint32_t>(rawFrame & stMask);
        res.multiTurn = static_cast<uint32_t>(rawFrame >> _st_bits);

        uint64_t totalCounts = (static_cast<uint64_t>(res.multiTurn) << _st_bits) | res.singleTurn;
        double maxCounts = static_cast<double>(1ULL << (_st_bits + _mt_bits));

        res.angleRadian = static_cast<float>(2.0 * TWO_PI * (totalCounts / maxCounts));
        res.outputAngleRadian = res.angleRadian / _gear_ratio;
        return res;
    }
};
