request.setUrl(mapProvider->getTileURL(x, y, zoom));       // → наш _getURL
request.setTransferTimeout(10000);
request.setRawHeader("Accept", "*/*");
request.setHeader(QNetworkRequest::UserAgentHeader, s_userAgent);

const QByteArray referrer = mapProvider->getReferrer().toUtf8();
if (!referrer.isEmpty()) {
    request.setRawHeader("Referer", referrer);             // → наш конструктор
}
const QByteArray token = mapProvider->getToken();
if (!token.isEmpty()) {
    request.setRawHeader("User-Token", token);             // → наш getToken
}
