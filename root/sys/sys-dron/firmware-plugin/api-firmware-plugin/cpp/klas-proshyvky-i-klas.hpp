static bool isMultiRotor (MAV_TYPE mavType);
static bool isFixedWing  (MAV_TYPE mavType);
static bool isVTOL       (MAV_TYPE mavType);
static bool isRoverBoat  (MAV_TYPE mavType);   // ⚠ не isRover
static bool isSub        (MAV_TYPE mavType);
static bool isAirship    (MAV_TYPE mavType);
static bool isPX4FirmwareClass       (MAV_AUTOPILOT autopilot);
static bool isArduPilotFirmwareClass (MAV_AUTOPILOT autopilot);
static bool isGenericFirmwareClass   (MAV_AUTOPILOT autopilot);
static QList<FirmwareClass_t> allFirmwareClasses();
static QList<VehicleClass_t>  allVehicleClasses(void);
static QString firmwareClassToString(FirmwareClass_t firmwareClass);
static QString vehicleClassToUserVisibleString(VehicleClass_t vehicleClass);
