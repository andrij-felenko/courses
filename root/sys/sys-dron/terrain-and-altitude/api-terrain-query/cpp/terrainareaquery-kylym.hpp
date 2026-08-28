explicit TerrainAreaQuery(bool autoDelete, QObject *parent = nullptr);
void requestData(const QGeoCoordinate &swCoord, const QGeoCoordinate &neCoord);

struct CarpetHeightInfo_t {
    double                minHeight;
    double                maxHeight;
    QList<QList<double>>  carpet;
};

signals:
    void terrainDataReceived(bool success,
                             const TerrainAreaQuery::CarpetHeightInfo_t &carpetHeightInfo);
