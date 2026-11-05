class BitBangDriver {
public:
    BitBangDriver(void* data_port, uint16_t data_pin, 
                  void* clock_port, uint16_t clock_pin, 
                  uint32_t delay_us);

    int Init();
    int WriteByte(uint8_t byte);
    int ReadBuffer(uint8_t* buffer, size_t length);

private:
    void* m_data_port;
    uint16_t m_data_pin;
    void* m_clock_port;
    uint16_t m_clock_pin;
    uint32_t m_delay_us;

    void DelayHalfPeriod();
    void SetDataLine(bool state);
    void ToggleClock();
};
