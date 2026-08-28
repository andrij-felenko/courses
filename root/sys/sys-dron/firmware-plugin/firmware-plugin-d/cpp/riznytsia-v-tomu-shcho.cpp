enum FirmwareCapabilities {
    SetFlightModeCapability =   1 << 0,
    PauseVehicleCapability =    1 << 1,
    GuidedModeCapability =      1 << 2,
    OrbitModeCapability =       1 << 3,
    TakeoffVehicleCapability =  1 << 4,
    ROIModeCapability =         1 << 5,
    ChangeHeadingCapability =   1 << 6,
    GuidedTakeoffCapability =   1 << 7,
};

virtual bool isCapable(const Vehicle *vehicle, FirmwareCapabilities capabilities) const;
