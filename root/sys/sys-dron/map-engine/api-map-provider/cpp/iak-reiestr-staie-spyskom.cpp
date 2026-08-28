for (const SharedMapProvider &provider : UrlFactory::getProviders()) {
    mapList.append(QGeoMapType(static_cast<QGeoMapType::MapStyle>(provider->getMapStyle()),
                               provider->getMapName(),      // назва
                               provider->getMapName(),      // опис — той самий рядок
                               false, false,
                               provider->getMapId(),        // mapId фреймворку = _mapId
                               QByteArrayLiteral("QGroundControl"),
                               cameraCapabilities()));
}
setSupportedMapTypes(mapList);
