while (!_requestQueue.isEmpty()) {
    const QueuedRequestInfo_t requestInfo = _requestQueue.dequeue();
    const SentRequestInfo_t sentRequestInfo = { requestInfo.terrainAtCoordinateQuery,
                                                requestInfo.coordinates.count() };
    _sentRequests.append(sentRequestInfo);
    coords += requestInfo.coordinates;
    if (coords.count() > 50) {
        break;
    }
}
