void TransectStyleComplexItem::_adjustForMaxRates(void)
{
    double maxClimbRate     = _terrainAdjustMaxClimbRateFact.rawValue().toDouble();
    double maxDescentRate   = _terrainAdjustMaxDescentRateFact.rawValue().toDouble();
    double flightSpeed      = _vehicleSpeed;

    if (qIsNaN(flightSpeed) || (maxClimbRate == 0 && maxDescentRate == 0)) {
        if (qIsNaN(flightSpeed)) {
            qWarning() << "TransectStyleComplexItem::_adjustForMaxRates called with flightSpeed = NaN";
        }
        return;
    }
    if (maxClimbRate <= 0 && maxDescentRate <= 0) {
        return;
    }

    if (maxClimbRate > 0) {
        bool climbRateAdjusted;
        do {
            climbRateAdjusted = false;
            for (int i=0; i<_rgFlightPathCoordInfo.count() - 1; i++) {
                QGeoCoordinate& fromCoord   = _rgFlightPathCoordInfo[i].coord;
                QGeoCoordinate& toCoord     = _rgFlightPathCoordInfo[i+1].coord;

                double altDifference    = toCoord.altitude() - fromCoord.altitude();
                double distance         = fromCoord.distanceTo(toCoord);
                double seconds          = distance / flightSpeed;
                double climbRate        = altDifference / seconds;

                if (climbRate > 0 && climbRate - maxClimbRate > 0.1) {
                    double maxAltitudeDelta = maxClimbRate * seconds;
                    fromCoord.setAltitude(toCoord.altitude() - maxAltitudeDelta);
                    climbRateAdjusted = true;
                }
            }
        } while (climbRateAdjusted);
    }

    if (maxDescentRate > 0) {
        bool descentRateAdjusted;
        maxDescentRate = -maxDescentRate;
        do {
            descentRateAdjusted = false;
            for (int i=0; i<_rgFlightPathCoordInfo.count() - 1; i++) {
                QGeoCoordinate& fromCoord   = _rgFlightPathCoordInfo[i].coord;
                QGeoCoordinate& toCoord     = _rgFlightPathCoordInfo[i+1].coord;

                double altDifference    = toCoord.altitude() - fromCoord.altitude();
                double distance         = fromCoord.distanceTo(toCoord);
                double seconds          = distance / flightSpeed;
                double descentRate      = altDifference / seconds;

                if (descentRate < 0 && descentRate - maxDescentRate < -0.1) {
                    double maxAltitudeDelta = maxDescentRate * seconds;
                    toCoord.setAltitude(fromCoord.altitude() + maxAltitudeDelta);
                    descentRateAdjusted = true;
                }
            }
        } while (descentRateAdjusted);
    }
}
