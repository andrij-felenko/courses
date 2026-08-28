void ParamFetcher::onParamValue(uint8_t compId, const mavlink_param_value_t& pv,
                                Clock::time_point now)
{
    // ArduPilot ллє незапитані значення ще ДО відповіді на запит списку, і номера
    // в них немає — поле дорівнює 65535. Будувати на них чеклист не можна.
    if (pv.param_index == UINT16_MAX && _awaitingList) return;

    Comp& c = _comps[compId];              // компонент міг з'явитися щойно
    if (!c.seen) {                         // перше значення від нього — будуємо чеклист
        c.seen  = true;
        c.total = pv.param_count;
        for (uint16_t i = 0; i < c.total; ++i) c.waiting[i] = 0;
    }

    // param_id — рівно 16 байтів і БЕЗ завершального нуля, якщо ім'я займає всі 16.
    char name[17] = {};
    std::memcpy(name, pv.param_id, 16);
    c.got[name] = { pv.param_value, pv.param_type };

    _awaitingList    = false;
    _silenceDeadline = now + Ms(kStreamSilenceMs);   // таймер тиші — з нуля

    if (pv.param_index < c.total) {                  // викреслюємо комірку
        c.waiting.erase(pv.param_index);
        _inFlight.erase(Key{compId, pv.param_index});
    }
    if (_batchOn) _refill(now);   // місце звільнилося — одразу беремо наступну діру
}
