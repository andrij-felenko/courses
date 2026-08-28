case QGroundControlQmlGlobal::AltitudeFrameRelative:
case QGroundControlQmlGlobal::AltitudeFrameAbsolute:
    // No additional work needed
    return;
case QGroundControlQmlGlobal::AltitudeFrameCalcAboveTerrain:
    _buildFlightPathCoordInfoFromPathHeightInfoForCalcAboveTerrain();
    _adjustForMaxRates();
    _adjustForTolerance();
    _minAMSLAltitude = qQNaN();
    _maxAMSLAltitude = qQNaN();
    for (const CoordInfo_t& coordInfo: _rgFlightPathCoordInfo) {
        _minAMSLAltitude = std::fmin(_minAMSLAltitude, coordInfo.coord.altitude());
        _maxAMSLAltitude = std::fmax(_maxAMSLAltitude, coordInfo.coord.altitude());
    }
    emit lastSequenceNumberChanged(lastSequenceNumber());
    break;
