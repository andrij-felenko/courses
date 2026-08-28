// custom/src/PerimeterFactGroup.cc
#include "PerimeterFactGroup.h"

#include "CustomPlugin.h"   // звідси Q_DECLARE_LOGGING_CATEGORY(CustomLog)
#include "MAVLinkProtocol.h"
#include "Vehicle.h"
#include "VehicleLinkManager.h"

PerimeterFactGroup::PerimeterFactGroup(QObject *parent)
    : FactGroup(500, QStringLiteral(":/custom/json/PerimeterFact.json"), parent)
{
    _addFact(&_numberFact);
    _addFact(&_rangeFact);
    _addFact(&_qualityFact);

    // Доки апарат не озвався, показувати нема чого — і це не нуль.
    _rangeFact.setRawValue(qQNaN());
    _qualityFact.setRawValue(qQNaN());
}

void PerimeterFactGroup::update(const mavlink_perimeter_beacon_status_t &status)
{
    _numberFact.setRawValue(status.beacon_id);
    _rangeFact.setRawValue(status.range_m);
    _qualityFact.setRawValue(status.quality);
    _setTelemetryAvailable(true);
}
