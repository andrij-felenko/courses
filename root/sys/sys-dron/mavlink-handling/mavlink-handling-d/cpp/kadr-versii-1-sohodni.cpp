void LinkInterface::reportMavlinkV1Traffic()
{
    if (_mavlinkV1TrafficReported || _mavlinkV2TrafficSeen) {
        return;
    }

    if (!_mavlinkV1FirstSeenTimer.isValid()) {
        _mavlinkV1FirstSeenTimer.start();
    }
    if (_mavlinkV1FirstSeenTimer.elapsed() < _mavlinkV1TrafficGraceMsecs) {
        return;
    }
    _mavlinkV1TrafficReported = true;
    ...
}
