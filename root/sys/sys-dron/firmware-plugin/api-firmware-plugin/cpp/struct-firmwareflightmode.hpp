struct FirmwareFlightMode
{
    FirmwareFlightMode(const QString &mName, uint32_t cMode,
                       bool cbs = false, bool adv = false);

    FirmwareFlightMode(const QString &mName, uint8_t sMode, uint32_t cMode,
                       bool cbs = false, bool adv = false,
                       bool fWing = false, bool mRotor = true);

    QString  mode_name    = "Unknown";
    uint8_t  standard_mode = 0;
    uint32_t custom_mode  = UINT32_MAX;
    bool     canBeSet     = false;
    bool     advanced     = false;
    bool     fixedWing    = false;
    bool     multiRotor   = true;
};
