VehicleGPSFactGroup::VehicleGPSFactGroup(QObject *parent)
    : FactGroup(1000, ":/json/Vehicle/GPSFact.json", parent)
{
    _addFact(&_latFact);
    _addFact(&_lonFact);
    _addFact(&_hdopFact);
    _addFact(&_lockFact);
    _addFact(&_countFact);

    _latFact.setRawValue(std::numeric_limits<float>::quiet_NaN());
    _hdopFact.setRawValue(std::numeric_limits<float>::quiet_NaN());
    _lockFact.setRawValue(0);
}
