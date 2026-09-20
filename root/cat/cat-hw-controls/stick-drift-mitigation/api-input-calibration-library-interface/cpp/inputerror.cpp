#include <cstdint>
#include <cstddef>

enum class InputError : int8_t {
    Ok = 0,
    InvalidParam = -1,
    OutOfBounds = -2,
    CalibrationInvalid = -3,
    NvmReadWrite = -4,
    CrcMismatch = -5
};

struct AxisConfig {
    uint16_t adc_min;
    uint16_t adc_center;
    uint16_t adc_max;
    float deadzone_inner;
    float deadzone_outer;
};

struct InputProfile {
    AxisConfig axis_x;
    AxisConfig axis_y;
    bool use_radial_deadzone;
    uint16_t crc16;
};

struct InputVector {
    float x;
    float y;
};

class InputDriver {
public:
    static InputError init(const InputProfile &profile) {
        if (profile.axis_x.adc_min >= profile.axis_x.adc_max ||
            profile.axis_y.adc_min >= profile.axis_y.adc_max) {
            return InputError::CalibrationInvalid;
        }
        return InputError::Ok;
    }
};
