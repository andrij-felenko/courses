struct QGCTileSet
{
    QGCTileSet &operator+=(const QGCTileSet &other);   // додає tileCount і tileSize
    void clear();

    int     tileX0 = 0,  tileX1 = 0;
    int     tileY0 = 0,  tileY1 = 0;
    quint64 tileCount = 0;
    quint64 tileSize  = 0;
};
