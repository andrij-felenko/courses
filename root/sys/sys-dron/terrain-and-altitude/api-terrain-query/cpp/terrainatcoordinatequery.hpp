explicit TerrainAtCoordinateQuery(bool autoDelete, QObject *parent = nullptr);

void requestData(const QList<QGeoCoordinate> &coordinates);

static bool getAltitudesForCoordinates(const QList<QGeoCoordinate> &coordinates,
                                       QList<double> &altitudes,
                                       bool &error);

void signalTerrainData(bool success, const QList<double> &heights);

signals:
    void terrainDataReceived(bool success, const QList<double> &heights);
