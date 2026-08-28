// у класі-замовнику
QPointer<TerrainAtCoordinateQuery> _query;

void MyItem::_requestTerrain()
{
    // 1. Попередній запит НЕ видаляємо — лише відчіпляємо його від себе.
    if (_query) {
        disconnect(_query, &TerrainAtCoordinateQuery::terrainDataReceived,
                   this,   &MyItem::_terrainDataReceived);
        _query = nullptr;
    }

    // 2. autoDelete = true: об'єкт знищить себе сам після того, як просигналить.
    _query = new TerrainAtCoordinateQuery(true /* autoDelete */);
    connect(_query, &TerrainAtCoordinateQuery::terrainDataReceived,
            this,   &MyItem::_terrainDataReceived);

    // 3. Запит завжди списком — навіть коли координата одна.
    _query->requestData({ _coordinate });
}

void MyItem::_terrainDataReceived(bool success, QList<double> heights)
{
    _terrainAltitude = (success && !heights.isEmpty()) ? heights[0] : qQNaN();
    _query = nullptr;                  // об'єкт уже приречений на deleteLater()
    emit terrainAltitudeChanged(_terrainAltitude);
}
