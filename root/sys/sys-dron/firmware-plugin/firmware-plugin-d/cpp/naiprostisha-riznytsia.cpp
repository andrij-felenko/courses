struct FirmwareFlightMode
{
    QString  mode_name    = "Unknown";
    uint8_t  standard_mode = 0;
    uint32_t custom_mode  = UINT32_MAX;
    bool     canBeSet     = false;
    bool     advanced     = false;
    bool     fixedWing    = false;
    bool     multiRotor   = true;
};
