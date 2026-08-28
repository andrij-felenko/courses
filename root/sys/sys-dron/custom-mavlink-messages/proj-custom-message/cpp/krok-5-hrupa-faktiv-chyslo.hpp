// custom/src/PerimeterFactGroup.h
#pragma once

#include "FactGroup.h"
#include "MAVLinkLib.h"

class Vehicle;

class PerimeterFactGroup : public FactGroup
{
    Q_OBJECT
    Q_PROPERTY(Fact *number  READ number  CONSTANT)
    Q_PROPERTY(Fact *range   READ range   CONSTANT)
    Q_PROPERTY(Fact *quality READ quality CONSTANT)

public:
    explicit PerimeterFactGroup(QObject *parent = nullptr);

    Fact *number()  { return &_numberFact;  }
    Fact *range()   { return &_rangeFact;   }
    Fact *quality() { return &_qualityFact; }

    void update(const mavlink_perimeter_beacon_status_t &status);

    Q_INVOKABLE void setMode(Vehicle *vehicle, int mode, double radiusM);
    Q_INVOKABLE void requestRate(Vehicle *vehicle, int hz);

private:
    Fact _numberFact  = Fact(0, QStringLiteral("number"),  FactMetaData::valueTypeUint16);
    Fact _rangeFact   = Fact(0, QStringLiteral("range"),   FactMetaData::valueTypeDouble);
    Fact _qualityFact = Fact(0, QStringLiteral("quality"), FactMetaData::valueTypeDouble);
};
