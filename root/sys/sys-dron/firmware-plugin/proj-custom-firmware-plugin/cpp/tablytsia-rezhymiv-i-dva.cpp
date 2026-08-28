// SokilFirmwarePlugin.cc
enum SokilMode : uint32_t {
    ModeManual = 0, ModeStabilize = 1, ModeAltitude = 2, ModePosition = 3,
    ModeGuided = 4, ModeMission = 5, ModeReturn = 6, ModeLand = 7,
    ModeTakeoff = 8, ModeFailsafe = 9, ModeAcro = 10,
};

SokilCopterFirmwarePlugin::SokilCopterFirmwarePlugin(QObject *parent)
    : SokilFirmwarePlugin(parent)
{
    //                    ім'я           номер          canBeSet  advanced
    FlightModeList modes = {
        { "Manual",       ModeManual,    true,  false },
        { "Stabilize",    ModeStabilize, true,  false },
        { "Altitude",     ModeAltitude,  true,  false },
        { "Position",     ModePosition,  true,  false },
        { "Guided",       ModeGuided,    true,  false },
        { "Mission",      ModeMission,   true,  false },
        { "Return",       ModeReturn,    true,  false },
        { "Land",         ModeLand,      true,  false },
        { "Takeoff",      ModeTakeoff,   false, false },   // входить сама за командою зльоту
        { "Failsafe",     ModeFailsafe,  false, false },   // тільки показ
        { "Acro",         ModeAcro,      true,  true  },   // за перемикачем «розширено»
    };

    updateAvailableFlightModes(modes);   // заповнює _flightModeList і _modeEnumToString
}
