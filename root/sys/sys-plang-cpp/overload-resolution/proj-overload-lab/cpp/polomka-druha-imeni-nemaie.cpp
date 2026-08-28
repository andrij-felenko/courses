struct Device {
    void send(int code)        { std::puts("Device::send(int)"); }
    void send(const char* msg) { std::puts("Device::send(const char*)"); }
};
struct Radio : Device {
    void send(double hz)       { std::puts("Radio::send(double)"); }
};

Radio r;
r.send("ping");
