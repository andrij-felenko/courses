// Append all transects into a single PolyPath query
QList<QGeoCoordinate> transectPoints;
for (const QList<CoordInfo_t>& transect: _transects) {
    for (const CoordInfo_t& coordInfo: transect) {
        transectPoints.append(coordInfo.coord);
    }
}

if (transectPoints.count() > 1) {
    _currentTerrainPolyPathQuery = new TerrainPolyPathQuery(true /* autoDelete */);
    connect(_currentTerrainPolyPathQuery, &TerrainPolyPathQuery::terrainDataReceived,
            this, &TransectStyleComplexItem::_polyPathTerrainData);
    _currentTerrainPolyPathQuery->requestData(transectPoints);
}
