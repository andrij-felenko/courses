/// Set of optional capabilites which firmware may support
enum FirmwareCapabilities {
    SetFlightModeCapability =   1 << 0,   ///< метод setFlightMode підтримано
    PauseVehicleCapability =    1 << 1,   ///< апарат уміє зупинитися на місці
    GuidedModeCapability =      1 << 2,   ///< апарат приймає команди керованого режиму
    OrbitModeCapability =       1 << 3,   ///< апарат уміє облітати точку по колу
    TakeoffVehicleCapability =  1 << 4,   ///< апарат уміє злітати
    ROIModeCapability =         1 << 5,   ///< точка інтересу — і в польоті, і в плані
    ChangeHeadingCapability =   1 << 6,   ///< апарат уміє змінити курс на місці
    GuidedTakeoffCapability =   1 << 7,   ///< зліт саме з керованого режиму
};
