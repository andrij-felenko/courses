void TransectStyleComplexItem::_adjustForTolerance(void)
{
    QList<CoordInfo_t>  adjustedFlightPath;
    double              tolerance           = _terrainAdjustToleranceFact.rawValue().toDouble();
    CoordInfo_t&        lastCoordInfo       = _rgFlightPathCoordInfo.first();

    adjustedFlightPath.append(lastCoordInfo);

    int coordIndex = 1;
    while (coordIndex < _rgFlightPathCoordInfo.count()) {
        // Walk forward until we fall out of tolerence. When we fall out of tolerance add that point.
        // We always add non-interstitial points no matter what.
        const CoordInfo_t& nextCoordInfo = _rgFlightPathCoordInfo[coordIndex];
        if (nextCoordInfo.coordType != CoordTypeInteriorTerrainAdded ||
                qAbs(lastCoordInfo.coord.altitude() - nextCoordInfo.coord.altitude()) > tolerance) {
            adjustedFlightPath.append(nextCoordInfo);
            lastCoordInfo = nextCoordInfo;
        }
        coordIndex++;
    }

    _rgFlightPathCoordInfo = adjustedFlightPath;
}
