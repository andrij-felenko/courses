QString CustomURLMapProvider::_getURL(int x, int y, int zoom) const
{
    QString url = SettingsManager::instance()->appSettings()
        ->customURL()->rawValue().toString();
    (void) url.replace("{x}", QString::number(x));
    (void) url.replace("{y}", QString::number(y));
    static const QRegularExpression zoomRegExp("\\{(z|zoom)\\}");
    (void) url.replace(zoomRegExp, QString::number(zoom));
    return url;
}
