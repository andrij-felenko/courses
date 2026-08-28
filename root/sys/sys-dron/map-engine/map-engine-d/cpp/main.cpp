class OpenStreetMapProvider : public MapProvider
{
public:
    OpenStreetMapProvider()
        : MapProvider(QStringLiteral("Street Map"),
                      QStringLiteral("https://www.openstreetmap.org"),
                      QStringLiteral("png"),
                      QGC_AVERAGE_TILE_SIZE,
                      MapProvider::StreetMap) {}
private:
    QString _getURL(int x, int y, int zoom) const final
    {
        return _mapUrl.arg(zoom).arg(x).arg(y);
    }
    const QString _mapUrl =
        QStringLiteral("http://tile.openstreetmap.org/%1/%2/%3.png");
};
