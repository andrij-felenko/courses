#include <cstdint>
#include <cstddef>
#include <span>

/* C++ відображення вендорського Platform Abstraction Layer */
extern "C" {
    using SensorReadFn = int8_t (*)(uint8_t reg_addr, uint8_t *read_data, uint32_t len, void *intf_ptr);
    using SensorWriteFn = int8_t (*)(uint8_t reg_addr, const uint8_t *write_data, uint32_t len, void *intf_ptr);
    using SensorDelayUsFn = void (*)(uint32_t period_us, void *intf_ptr);

    struct VendorSensorCalib {
        uint16_t dig_t1;
        int16_t  dig_t2;
        int16_t  dig_t3;
    };

    struct VendorSensorDev {
        uint8_t chip_id;
        void *intf_ptr;
        SensorReadFn read;
        SensorWriteFn write;
        SensorDelayUsFn delay_us;
        VendorSensorCalib calib_data;
    };
}
