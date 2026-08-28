void ParamFetcher::tick(Clock::time_point now)
{
    if (_awaitingList) {                        // борт ще не озвався жодного разу
        if (now < _listDeadline) return;
        if (_listAttempts > kListRetries) { _giveUp = true; return; }
        _sendRequestList();
        ++_listAttempts;
        _listDeadline = now + Ms(kListSilenceMs);
        return;
    }

    if (!_batchOn) {
        if (now < _silenceDeadline) return;     // потік іде — таймер тиші відсунуто
        _batchOn = true;                        // замовк: вмикаємо добір
    }

    // Прострочені запити: місце в пачці звільняється, номер іде на нову спробу.
    // _ask дописує в _inFlight, але вставка в std::map не псує чинних ітераторів,
    // а новий запис має дедлайн у майбутньому — цей самий обхід його не зачепить.
    for (auto it = _inFlight.begin(); it != _inFlight.end(); ) {
        if (now < it->second) { ++it; continue; }
        const Key key = it->first;
        it = _inFlight.erase(it);
        _ask(key.first, key.second, now);
    }
    _refill(now);
}

// Спробувати номер ще раз — або здатися на ньому назавжди.
void ParamFetcher::_ask(uint8_t compId, uint16_t idx, Clock::time_point now)
{
    Comp& c  = _comps.at(compId);
    auto  it = c.waiting.find(idx);
    if (it == c.waiting.end()) return;          // уже приїхав, поки ми чекали

    if (++it->second > kTriesPerIndex) {        // шоста спроба — досить
        c.failed.insert(idx);
        c.waiting.erase(it);
        return;
    }
    _sendRequestRead(compId, idx);
    _inFlight[Key{compId, idx}] = now + Ms(kReadAckMs);
}

// Дотягти пачку до десяти запитів у польоті, беручи діри в порядку номерів.
void ParamFetcher::_refill(Clock::time_point now)
{
    for (auto& entry : _comps) {
        const uint8_t compId = entry.first;
        Comp&         c      = entry.second;
        for (auto it = c.waiting.begin(); it != c.waiting.end(); ) {
            if (_inFlight.size() >= kBatchSize) return;       // пачка повна
            const uint16_t idx = it->first;
            ++it;                                            // _ask може стерти запис
            if (_inFlight.count(Key{compId, idx})) continue;  // уже в польоті
            _ask(compId, idx, now);
        }
    }
}

void ParamFetcher::_sendRequestList()
{
    mavlink_message_t msg;
    mavlink_msg_param_request_list_pack(kGcsSysId, kGcsCompId, &msg,
                                        _sysId, MAV_COMP_ID_ALL);
    _out.send(msg);
}

void ParamFetcher::_sendRequestRead(uint8_t compId, uint16_t idx)
{
    // param_index тут int16_t: −1 означає «шукай за іменем», тож за номером
    // доступні лише перші 32768 параметрів.
    mavlink_message_t msg;
    mavlink_msg_param_request_read_pack(kGcsSysId, kGcsCompId, &msg,
                                        _sysId, compId, "", static_cast<int16_t>(idx));
    _out.send(msg);
}
