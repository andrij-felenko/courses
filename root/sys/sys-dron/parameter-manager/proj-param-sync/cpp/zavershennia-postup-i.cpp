// Порожні карти очікування — ще НЕ все: параметри підвіса можуть приїхати
// першими, а головного компонента не бути взагалі.
bool ParamFetcher::complete() const
{
    for (const auto& entry : _comps)
        if (!entry.second.waiting.empty()) return false;
    return _comps.count(_defaultComp) != 0;
}

double ParamFetcher::progress() const
{
    uint32_t total = 0, left = 0;
    for (const auto& entry : _comps) {
        total += entry.second.total;
        left  += static_cast<uint32_t>(entry.second.waiting.size());
    }
    return total ? static_cast<double>(total - left) / static_cast<double>(total) : 0.0;
}
