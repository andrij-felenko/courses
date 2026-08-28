class ElevationProvider : public MapProvider
{
protected:
    ElevationProvider(const QString &mapName, const QString &referrer, const QString &imageFormat,
                      quint32 averageSize, MapProvider::MapStyle mapType)
        : MapProvider(mapName, referrer, imageFormat, averageSize, mapType) {}

public:
    bool isElevationProvider() const final { return true; }
    virtual QByteArray serialize(const QByteArray &image) const = 0;
};
