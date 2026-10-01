struct Adxl345Data {
    float x{0.0f};
    float y{0.0f};
    float z{0.0f};
};

Adxl345Status read_accel(Adxl345Dev &dev, Adxl345Data &data) {
    uint8_t buf[6];
    if (dev.hal.read(dev.hal.handle, 0x32, buf, 6) != 0) {
        return Adxl345Status::ErrBus;
    }
    int16_t raw_x = static_cast<int16_t>((buf[1] << 8) | buf[0]);
    int16_t raw_y = static_cast<int16_t>((buf[3] << 8) | buf[2]);
    int16_t raw_z = static_cast<int16_t>((buf[5] << 8) | buf[4]);

    data.x = raw_x * 0.0039f;
    data.y = raw_y * 0.0039f;
    data.z = raw_z * 0.0039f;
    return Adxl345Status::Ok;
}
