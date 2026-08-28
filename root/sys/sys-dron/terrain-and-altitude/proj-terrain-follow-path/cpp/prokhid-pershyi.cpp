void TransectStyleComplexItem::_buildFlightPathCoordInfoFromPathHeightInfoForCalcAboveTerrain(void)
{
    double distanceToSurface = _cameraCalc.distanceToSurface()->rawValue().toDouble();

    _rgFlightPathCoordInfo.clear();
    int pathHeightIndex = 0;
    for (int transectIndex=0; transectIndex<_transects.count(); transectIndex++) {
        const QList<CoordInfo_t>& transect = _transects[transectIndex];

        // Build flight path for transect
        for (int transectCoordIndex=0; transectCoordIndex<transect.count() - 1; transectCoordIndex++) {
            CoordInfo_t fromCoordInfo   = transect[transectCoordIndex];
            CoordInfo_t toCoordInfo     = transect[transectCoordIndex+1];

            const auto& pathHeightInfo = _rgPathHeightInfo[pathHeightIndex++];

            fromCoordInfo.coord.setAltitude(distanceToSurface + pathHeightInfo.heights.first());
            toCoordInfo.coord.setAltitude(distanceToSurface + pathHeightInfo.heights.last());

            if (transectCoordIndex == 0) {
                _rgFlightPathCoordInfo.append(fromCoordInfo);
            }

            // Add interstitial points at max resolution of our terrain data
            int cHeights = pathHeightInfo.heights.count();

            double azimuth  = fromCoordInfo.coord.azimuthTo(toCoordInfo.coord);
            double distance = fromCoordInfo.coord.distanceTo(toCoordInfo.coord);

            for (int interstitialIndex=1; interstitialIndex<cHeights - 1; interstitialIndex++) {
                double interstitialTerrainHeight = pathHeightInfo.heights[interstitialIndex];
                double percentTowardsTo = (1.0 / (cHeights - 1)) * interstitialIndex;

                CoordInfo_t interstitialCoordInfo;
                interstitialCoordInfo.coordType = CoordTypeInteriorTerrainAdded;
                interstitialCoordInfo.coord     = fromCoordInfo.coord.atDistanceAndAzimuth(distance * percentTowardsTo, azimuth);
                interstitialCoordInfo.coord.setAltitude(interstitialTerrainHeight + distanceToSurface);

                _rgFlightPathCoordInfo.append(interstitialCoordInfo);
            }

            _rgFlightPathCoordInfo.append(toCoordInfo);
        }
        ...
    }
}
