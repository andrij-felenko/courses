// EsriMapProvider.cpp
QByteArray EsriMapProvider::getToken() const
{
    return SettingsManager::instance()->appSettings()->esriToken()->rawValue().toString().toUtf8();
}

// QGeoTileFetcherQGC.cpp
const QByteArray token = mapProvider->getToken();
if (!token.isEmpty()) {
    request.setRawHeader(QByteArrayLiteral("User-Token"), token);
}
