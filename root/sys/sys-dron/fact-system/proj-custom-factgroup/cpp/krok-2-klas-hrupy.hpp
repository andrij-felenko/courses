// custom/src/FuelCellFactGroup.h
#pragma once

#include "FactGroup.h"
#include "QGCMAVLink.h"

class FuelCellFactGroup : public FactGroup
{
    Q_OBJECT
    Q_PROPERTY(Fact *pressure    READ pressure    CONSTANT)
    Q_PROPERTY(Fact *temperature READ temperature CONSTANT)
    Q_PROPERTY(Fact *power       READ power       CONSTANT)
    Q_PROPERTY(Fact *remaining   READ remaining   CONSTANT)
    Q_PROPERTY(Fact *state       READ state       CONSTANT)
    Q_PROPERTY(Fact *faults      READ faults      CONSTANT)

public:
    explicit FuelCellFactGroup(QObject *parent = nullptr);

    Fact *pressure()    { return &_pressureFact;    }
    Fact *temperature() { return &_temperatureFact; }
    Fact *power()       { return &_powerFact;       }
    Fact *remaining()   { return &_remainingFact;   }
    Fact *state()       { return &_stateFact;       }
    Fact *faults()      { return &_faultsFact;      }

    void handleMessage(Vehicle *vehicle, const mavlink_message_t &message) override;

private:
    Fact _pressureFact    = Fact(0, QStringLiteral("pressure"),    FactMetaData::valueTypeDouble);
    Fact _temperatureFact = Fact(0, QStringLiteral("temperature"), FactMetaData::valueTypeDouble);
    Fact _powerFact       = Fact(0, QStringLiteral("power"),       FactMetaData::valueTypeDouble);
    Fact _remainingFact   = Fact(0, QStringLiteral("remaining"),   FactMetaData::valueTypeDouble);
    Fact _stateFact       = Fact(0, QStringLiteral("state"),       FactMetaData::valueTypeUint8);
    Fact _faultsFact      = Fact(0, QStringLiteral("faults"),      FactMetaData::valueTypeUint32);
};
