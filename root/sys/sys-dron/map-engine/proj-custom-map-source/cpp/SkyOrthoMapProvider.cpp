// src/QtLocationPlugin/Providers/SkyOrthoMapProvider.cpp
#include "SkyOrthoMapProvider.h"

#include "SettingsManager.h"
#include "SkyOrthoSettings.h"

QString SkyOrthoMapProvider::_getURL(int x, int y, int zoom) const
{
    if ((zoom < kMinZoom) || (zoom > kMaxZoom)) {
        return QString();          // порожньо = «не проси»; наслідки — у граблях
    }
    return _mapUrl.arg(zoom).arg(x).arg(y);
}

QByteArray SkyOrthoMapProvider::getToken() const
{
    return SettingsManager::instance()->skyOrthoSettings()
        ->apiKey()->rawValue().toString().toUtf8();
}

QGCTileSet SkyOrthoMapProvider::getTileCount(int zoom,
                                             double topleftLon, double topleftLat,
                                             double bottomRightLon, double bottomRightLat) const
{
    if ((zoom < kMinZoom) || (zoom > kMaxZoom)) {
        return QGCTileSet();       // нуль клітинок, нуль байтів
    }
    return MapProvider::getTileCount(zoom, topleftLon, topleftLat,
                                     bottomRightLon, bottomRightLat);
}
