_stateParameters = new SkippableAsyncState(
    QStringLiteral("RequestParameters"), this,
    [this]() {                                  // чи пропускати?
        if (_shouldSkipForFlying()) {
            if (vehicle()->px4Firmware()) {     // PX4 має дешеву звірку кешу за хешем
                return false;
            }
            _lastSkipReason = QStringLiteral("(vehicle is flying)");
            return true;
        }
        return false;
    },
    [this](SkippableAsyncState* state) { _requestParameters(state); },
    ...
