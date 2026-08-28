QString UrlFactory::getTileHash(QStringView type, int x, int y, int z)
{
    const int hash = hashFromProviderType(type);
    return QString::asprintf("%010d%08d%08d%03d", hash, x, y, z);
}

QString UrlFactory::tileHashToType(QStringView tileHash)
{
    return providerTypeFromHash(tileHash.mid(0, 10).toInt());
}
