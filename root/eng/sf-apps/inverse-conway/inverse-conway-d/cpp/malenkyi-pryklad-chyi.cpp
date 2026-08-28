// Одна команда володіє обома підсистемами — межі немає,
// тож найдешевше просто ділити внутрішній стан під спільним замком.
struct Cache {
    std::mutex                    mu;
    std::map<Key, Value>         data;   // усе назовні, будь-хто чіпає напряму
};

// billing.cpp і catalog.cpp обидва роблять так:
{
    std::lock_guard<std::mutex> lk(cache.mu);
    cache.data[k] = v;                    // прямий доступ до нутра
}
