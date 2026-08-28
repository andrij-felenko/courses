class Pool;                                  // оголошення наперед

// Обгортка-оренда: тримає позичений Conn, повертає його в деструкторі.
class Lease {
public:
    Lease(Pool& pool, Conn* conn) : pool_(pool), conn_(conn) {}
    ~Lease() { if (conn_) pool_.release(conn_); }   // ← повернення тут

    Conn* operator->() { return conn_; }     // щоб писати lease->query(...)
    Conn& operator*()  { return *conn_; }

    // Оренду не можна копіювати (два власники одного Conn = зомбі),
    // але можна ПЕРЕДАВАТИ (move): старий власник знімає з себе conn_.
    Lease(const Lease&) = delete;
    Lease& operator=(const Lease&) = delete;
    Lease(Lease&& o) noexcept : pool_(o.pool_), conn_(o.conn_) { o.conn_ = nullptr; }

private:
    Pool& pool_;
    Conn* conn_;
};

// використання
void handle(Pool& pool) {
    Lease lease = pool.acquire();            // позичив
    auto rows = lease->query("select ...");  // працюємо крізь ->
    if (rows.empty())
        return;                              // ← деструктор Lease поверне Conn
    process(rows);
}                                            // ← або тут: у будь-якому разі release
