// Обмежений реєстр пулів: стеля розміру + LRU + ЗАКРИТТЯ пулу при евікції.
public final class PoolRegistry implements AutoCloseable {
    private static final int MAX = 64;
    private final Map<String, ConnectionPool> pools;

    public PoolRegistry() {
        // accessOrder=true → LinkedHashMap тримає порядок за останнім доступом (LRU)
        this.pools = new LinkedHashMap<>(16, 0.75f, true) {
            @Override
            protected boolean removeEldestEntry(Map.Entry<String, ConnectionPool> eldest) {
                if (size() > MAX) {
                    eldest.getValue().close();   // ← закрити з'єднання, не лише кинути посилання
                    return true;                 // ← і аж тоді видалити запис
                }
                return false;
            }
        };
    }

    public synchronized ConnectionPool get(String url) {  // LinkedHashMap не потокобезпечний
        ConnectionPool p = pools.get(url);                // get теж оновлює «свіжість» (LRU)
        if (p == null) {
            p = new ConnectionPool(url);
            pools.put(url, p);                            // put запускає removeEldestEntry
        }
        return p;
    }

    @Override
    public synchronized void close() {
        pools.values().forEach(ConnectionPool::close);    // при зупинці — закрити всі
        pools.clear();
    }
}
