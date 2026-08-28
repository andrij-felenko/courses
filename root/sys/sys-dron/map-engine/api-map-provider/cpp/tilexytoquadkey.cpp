QString MapProvider::_tileXYToQuadKey(int tileX, int tileY, int levelOfDetail) const
{
    QString quadKey;
    for (int i = levelOfDetail; i > 0; i--) {
        char digit = '0';
        const int mask = 1 << (i - 1);
        if ((tileX & mask) != 0) { digit++; }
        if ((tileY & mask) != 0) { digit += 2; }
        quadKey.append(digit);
    }
    return quadKey;
}
