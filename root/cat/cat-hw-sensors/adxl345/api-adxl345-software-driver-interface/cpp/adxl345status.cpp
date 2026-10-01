enum class Adxl345Status {
    Ok = 0,
    ErrBus = -1,
    ErrDevNotFound = -2
};

struct Adxl345Dev {
    Adxl345Hal hal;
    uint8_t    dev_id{0};

    Adxl345Status init(const Adxl345Hal &bus_hal) {
        if (!bus_hal.read || !bus_hal.write) return Adxl345Status::ErrBus;
        hal = bus_hal;
        uint8_t id = 0;
        if (hal.read(hal.handle, 0x00, &id, 1) != 0) {
            return Adxl345Status::ErrBus;
        }
        if (id != 0xE5) {
            return Adxl345Status::ErrDevNotFound;
        }
        dev_id = id;
        return Adxl345Status::Ok;
    }
};
