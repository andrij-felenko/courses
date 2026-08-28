class UrlFactory
{
public:
    static QString getImageFormat(QStringView type, QByteArrayView image);
    static QString getImageFormat(int qtMapId,      QByteArrayView image);

    static QUrl getTileURL(QStringView type, int x, int y, int zoom);
    static QUrl getTileURL(int qtMapId,      int x, int y, int zoom);

    static quint32 averageSizeForType(QStringView type);
    static bool    isElevation(int qtMapId);

    static int long2tileX(QStringView mapType, double lon, int z);
    static int lat2tileY(QStringView mapType, double lat, int z);

    static QGCTileSet getTileCount(int zoom, double topleftLon, double topleftLat,
                                   double bottomRightLon, double bottomRightLat,
                                   QStringView mapType);

    static const QList<SharedMapProvider> &getProviders();
    static QStringList getProviderTypes();
    static QStringList getElevationProviderTypes();

    static int     getQtMapIdFromProviderType(QStringView type);
    static QString getProviderTypeFromQtMapId(int qtMapId);
    static SharedMapProvider getMapProviderFromQtMapId(int qtMapId);
    static SharedMapProvider getMapProviderFromProviderType(QStringView type);

    static int     hashFromProviderType(QStringView type);
    static QString providerTypeFromHash(int hash);
    static QString tileHashToType(QStringView tileHash);
    static QString getTileHash(QStringView type, int x, int y, int z);

private:
    static const QList<SharedMapProvider> _providers;
};
