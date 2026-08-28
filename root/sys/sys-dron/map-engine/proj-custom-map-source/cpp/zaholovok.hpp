// src/QtLocationPlugin/Providers/SkyOrthoMapProvider.h
#pragma once

#include "MapProvider.h"

/// Ортофотоплани власного сервера: сітка XYZ, jpeg, токен окремим заголовком.
class SkyOrthoMapProvider : public MapProvider
{
public:
    SkyOrthoMapProvider()
        : MapProvider(QStringLiteral("SkyOrtho Aerial"),            // «джерело тип»
                      QStringLiteral("https://tiles.skylark.example"),
                      QStringLiteral("jpg"),
                      41000,                                        // виміряний тайл
                      MapProvider::SatelliteMapDay) {}

    QByteArray getToken() const final;

    QGCTileSet getTileCount(int zoom,
                            double topleftLon, double topleftLat,
                            double bottomRightLon, double bottomRightLat) const final;

private:
    QString _getURL(int x, int y, int zoom) const final;

    static constexpr int kMinZoom = 10;
    static constexpr int kMaxZoom = 19;

    const QString _mapUrl = QStringLiteral(
        "https://tiles.skylark.example/ortho/%1/%2/%3.jpg");
};
