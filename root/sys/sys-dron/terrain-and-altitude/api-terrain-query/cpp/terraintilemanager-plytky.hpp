static TerrainTileManager *instance();

bool getAltitudesForCoordinates(const QList<QGeoCoordinate> &coordinates,
                                QList<double> &altitudes, bool &error);

void addCoordinateQuery(TerrainQueryInterface *iface, const QList<QGeoCoordinate> &coordinates);
void addPathQuery      (TerrainQueryInterface *iface, const QGeoCoordinate &startPoint,
                                                      const QGeoCoordinate &endPoint);
void addCarpetQuery    (TerrainQueryInterface *iface, const QGeoCoordinate &swCoord,
                                                      const QGeoCoordinate &neCoord, bool statsOnly);
