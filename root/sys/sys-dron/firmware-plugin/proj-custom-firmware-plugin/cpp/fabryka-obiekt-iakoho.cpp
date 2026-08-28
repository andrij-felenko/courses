// SokilFirmwarePluginFactory.h
#include "FirmwarePluginFactory.h"

class SokilFirmwarePluginFactory : public FirmwarePluginFactory
{
    Q_OBJECT

public:
    explicit SokilFirmwarePluginFactory(QObject *parent = nullptr);

    QList<QGCMAVLink::FirmwareClass_t> supportedFirmwareClasses() const final;
    QList<QGCMAVLink::VehicleClass_t>  supportedVehicleClasses() const final;
    FirmwarePlugin *firmwarePluginForAutopilot(MAV_AUTOPILOT autopilotType,
                                               MAV_TYPE vehicleType) final;

private:
    FirmwarePlugin *_copterPluginInstance = nullptr;
    FirmwarePlugin *_roverPluginInstance  = nullptr;
};
