// custom/src/CustomPlugin.cc
#include <QtQml/QQmlEngine>

#include "MultiVehicleManager.h"

void CustomPlugin::init()
{
    QGCCorePlugin::init();

    qmlRegisterSingletonInstance("Custom.Beacon", 1, 0, "Beacon", &_beacon);

    (void) connect(MultiVehicleManager::instance(), &MultiVehicleManager::vehicleAdded,
                   this, [this](Vehicle *vehicle) { _beacon.requestRate(vehicle, 2); });
}
