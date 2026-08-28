// MyFirmwarePluginFactory.h
class MyFirmwarePluginFactory : public FirmwarePluginFactory
{
    Q_OBJECT
public:
    explicit MyFirmwarePluginFactory(QObject *parent = nullptr)
        : FirmwarePluginFactory(parent) {}        // реєстрація — у базовому конструкторі

    QList<QGCMAVLink::FirmwareClass_t> supportedFirmwareClasses() const override
        { return { QGCMAVLink::FirmwareClassPX4 }; }

    QList<QGCMAVLink::VehicleClass_t> supportedVehicleClasses() const override
        { return { QGCMAVLink::VehicleClassMultiRotor }; }

    FirmwarePlugin *firmwarePluginForAutopilot(MAV_AUTOPILOT autopilotType,
                                               MAV_TYPE vehicleType) override
    {
        if (autopilotType != MAV_AUTOPILOT_PX4) { return nullptr; }
        if (QGCMAVLink::vehicleClass(vehicleType) != QGCMAVLink::VehicleClassMultiRotor) {
            return nullptr;
        }
        if (!_pluginInstance) { _pluginInstance = new MyFirmwarePlugin(this); }
        return _pluginInstance;                   // ОДИН примірник на всі апарати класу
    }
private:
    MyFirmwarePlugin *_pluginInstance = nullptr;
};
