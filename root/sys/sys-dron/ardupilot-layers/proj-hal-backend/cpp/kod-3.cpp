// Бекенд SITL: те саме обличчя, але байти течуть у мережеву трубу, не в регістр.
class UARTDriver_SITL : public AP_HAL::UARTDriver {
    int fd;                           // сокет до моделі апарата
public:
    UARTDriver_SITL(int socket) : fd(socket) {}

    void begin(uint32_t) override {}              // швидкість для сокета не потрібна
    size_t write(uint8_t b) override {
        return ::send(fd, &b, 1, 0);              // байт → сокет
    }
    int16_t read() override {
        uint8_t b;
        return (::recv(fd, &b, 1, MSG_DONTWAIT) == 1) ? b : -1;
    }
    uint32_t available() override { /* опитати сокет */ return 0; }
};
