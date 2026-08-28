void SimpleMissionItem::_terrainAltChanged(void)
{
    if (_altitudeFrame == AltitudeFrameCalcAboveTerrain || _altitudeFrame == AltitudeFrameTerrain) {
        if (qIsNaN(terrainAltitude())) {
            // NaN — ознака того, що рельєф ще не приїхав
            if (_altitudeFrame == AltitudeFrameCalcAboveTerrain) {
                _missionItem._param7Fact.setRawValue(qQNaN());
            }
            _amslAltAboveTerrainFact.setRawValue(qQNaN());
        } else {
            double newAboveTerrain = terrainAltitude() + _altitudeFact.rawValue().toDouble();
            ...
        }
    }
}
