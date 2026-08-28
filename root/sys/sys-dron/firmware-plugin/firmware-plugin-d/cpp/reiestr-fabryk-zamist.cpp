class FirmwarePluginFactory : public QObject
{
public:
    virtual FirmwarePlugin *firmwarePluginForAutopilot(MAV_AUTOPILOT autopilotType,
                                                       MAV_TYPE vehicleType) = 0;
    virtual QList<QGCMAVLink::FirmwareClass_t> supportedFirmwareClasses() const = 0;
    virtual QList<QGCMAVLink::VehicleClass_t> supportedVehicleClasses() const
        { return QGCMAVLink::allVehicleClasses(); }
};

class FirmwarePluginFactoryRegister : public QObject
{
public:
    static FirmwarePluginFactoryRegister *instance();
    void registerPluginFactory(FirmwarePluginFactory *pluginFactory)
        { _factoryList.append(pluginFactory); }
    QList<FirmwarePluginFactory*> pluginFactories() const { return _factoryList; }
private:
    QList<FirmwarePluginFactory*> _factoryList;
};
