struct AS5048_Diagnostics {
    bool compLow;
    bool compHigh;
    bool cof;
    bool ocf;
    uint8_t agc;
};

class AS5048_HealthMonitor {
private:
    uint8_t csPin;

    uint16_t spiTransfer(uint16_t cmd) {
        digitalWrite(csPin, LOW);
        uint16_t val = SPI.transfer16(cmd);
        digitalWrite(csPin, HIGH);
        return val;
    }

public:
    AS5048_HealthMonitor(uint8_t cs) : csPin(cs) {}

    bool checkHealth(AS5048_Diagnostics &diag) {
        SPI.beginTransaction(SPISettings(1000000, MSBFIRST, SPI_MODE1));
        spiTransfer(0x7FFD); // Запит регістру 0x3FFD
        uint16_t res = spiTransfer(0x0000); // Виштовхування відповіді NOP
        SPI.endTransaction();

        diag.agc      = res & 0xFF;
        diag.ocf      = (res & 0x0400) != 0;
        diag.cof      = (res & 0x0800) != 0;
        diag.compLow  = (res & 0x1000) != 0;
        diag.compHigh = (res & 0x2000) != 0;

        if (diag.compLow || diag.compHigh || diag.cof || !diag.ocf) {
            return false; // Стан неефективного чи аварійного магнітного поля
        }
        return true;
    }
};
