// MyOrthoMapProvider.h
class MyOrthoMapProvider : public MapProvider
{
public:
    MyOrthoMapProvider()
        : MapProvider(QStringLiteral("Ortho Rescue"),          // ім'я → налаштування й ключ
                      QStringLiteral("https://gis.example.org"),
                      QStringLiteral("jpg"),
                      42000,                                    // виміряний середній тайл
                      MapProvider::SatelliteMapDay) {}
private:
    QString _getURL(int x, int y, int zoom) const final { return _mapUrl.arg(zoom).arg(x).arg(y); }

    const QString _mapUrl = QStringLiteral("https://gis.example.org/tiles/%1/%2/%3.jpg");
};
