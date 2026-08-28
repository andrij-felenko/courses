// src/Vehicle/FactGroups/VehicleWinchFactGroup.h
#pragma once

#include "FactGroup.h"

class VehicleWinchFactGroup : public FactGroup
{
    Q_OBJECT
    Q_PROPERTY(Fact *lineLength READ lineLength CONSTANT)
    Q_PROPERTY(Fact *speed      READ speed      CONSTANT)
    Q_PROPERTY(Fact *tension    READ tension    CONSTANT)
    Q_PROPERTY(Fact *voltage    READ voltage    CONSTANT)
    Q_PROPERTY(Fact *current    READ current    CONSTANT)
    Q_PROPERTY(Fact *motorTemp  READ motorTemp  CONSTANT)
    Q_PROPERTY(bool  moving     READ moving     NOTIFY movingChanged)

public:
    explicit VehicleWinchFactGroup(QObject *parent = nullptr);

    Fact *lineLength() { return &_lineLengthFact; }
    Fact *speed()      { return &_speedFact; }
    Fact *tension()    { return &_tensionFact; }
    Fact *voltage()    { return &_voltageFact; }
    Fact *current()    { return &_currentFact; }
    Fact *motorTemp()  { return &_motorTempFact; }

    bool moving() const { return _moving; }

    // Перевизначення FactGroup
    void handleMessage(Vehicle *vehicle, const mavlink_message_t &message) final;

signals:
    void movingChanged(bool moving);

private:
    void _handleWinchStatus(const mavlink_message_t &message);

    Fact _lineLengthFact = Fact(0, QStringLiteral("lineLength"), FactMetaData::valueTypeDouble);
    Fact _speedFact      = Fact(0, QStringLiteral("speed"),      FactMetaData::valueTypeDouble);
    Fact _tensionFact    = Fact(0, QStringLiteral("tension"),    FactMetaData::valueTypeDouble);
    Fact _voltageFact    = Fact(0, QStringLiteral("voltage"),    FactMetaData::valueTypeDouble);
    Fact _currentFact    = Fact(0, QStringLiteral("current"),    FactMetaData::valueTypeDouble);
    Fact _motorTempFact  = Fact(0, QStringLiteral("motorTemp"),  FactMetaData::valueTypeDouble);

    bool _moving = false;
};
