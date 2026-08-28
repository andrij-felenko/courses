// SokilFirmwarePluginFactory.cc
#include "SokilFirmwarePluginFactory.h"
#include "SokilFirmwarePlugin.h"
#include "SokilMAVLink.h"

// Глобальний об'єкт: створюється до main(), і саме його конструктор
// вписує фабрику в реєстр. Нікого іншого викликати не треба.
SokilFirmwarePluginFactory SokilFirmwarePluginFactory_instance(nullptr);

SokilFirmwarePluginFactory::SokilFirmwarePluginFactory(QObject *parent)
    : FirmwarePluginFactory(parent)
{
    // Порожньо. Свідомо.
}

QList<QGCMAVLink::FirmwareClass_t> SokilFirmwarePluginFactory::supportedFirmwareClasses() const
{
    return { static_cast<QGCMAVLink::FirmwareClass_t>(MAV_AUTOPILOT_SOKIL) };
}

QList<QGCMAVLink::VehicleClass_t> SokilFirmwarePluginFactory::supportedVehicleClasses() const
{
    return { QGCMAVLink::VehicleClassMultiRotor, QGCMAVLink::VehicleClassRoverBoat };
}

FirmwarePlugin *SokilFirmwarePluginFactory::firmwarePluginForAutopilot(MAV_AUTOPILOT autopilotType,
                                                                      MAV_TYPE vehicleType)
{
    if (autopilotType != MAV_AUTOPILOT_SOKIL) {
        return nullptr;                    // не наш апарат — хай іде до загального плагіна
    }

    switch (vehicleType) {
    case MAV_TYPE_QUADROTOR:
    case MAV_TYPE_HEXAROTOR:
        if (!_copterPluginInstance) {
            _copterPluginInstance = new SokilCopterFirmwarePlugin(this);
        }
        return _copterPluginInstance;
    case MAV_TYPE_GROUND_ROVER:
        if (!_roverPluginInstance) {
            _roverPluginInstance = new SokilRoverFirmwarePlugin(this);
        }
        return _roverPluginInstance;
    default:
        return nullptr;
    }
}
