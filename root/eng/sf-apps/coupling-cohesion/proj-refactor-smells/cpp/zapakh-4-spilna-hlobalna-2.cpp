class LinkStatus {
public:
    // Запис — лише звідси; інваріант linkUp ⟺ rssi>поріг тримається тут
    void updateRssi(int rssi) {
        CriticalSection cs;           // закрили переривання на час запису
        rssi_   = rssi;
        linkUp_ = (rssi > RSSI_THRESHOLD);
    }
    void reset() {
        CriticalSection cs;
        packetsLost_ = 0;
        linkUp_      = false;
        rssi_        = RSSI_FLOOR;    // і rssi узгоджуємо — не лишаємо брехати
    }
    // Читання — атомарний зліпок, щоб не вхопити півзначення
    struct Snapshot { int rssi; bool up; uint32_t lost; };
    Snapshot read() const {
        CriticalSection cs;
        return { rssi_, linkUp_, packetsLost_ };
    }
private:
    static constexpr int RSSI_THRESHOLD = -90;
    static constexpr int RSSI_FLOOR     = -128;
    volatile int      rssi_        = RSSI_FLOOR;
    volatile bool     linkUp_      = false;
    volatile uint32_t packetsLost_ = 0;
};

LinkStatus g_link;   // один екземпляр — але доступ лише через його методи
