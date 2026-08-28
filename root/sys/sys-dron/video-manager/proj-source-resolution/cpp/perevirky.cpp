// ─── ПЕРЕВІРКИ ────────────────────────────────────────────────────────────
static int failures = 0;
#define CHECK(cond) do { if (!(cond)) { ++failures; \
    std::printf("  ✗ %s (рядок %d)\n", #cond, __LINE__); } } while (0)

// 1. Повторний виклик із тими самими входами не змінює нічого.
static void test_idempotent()
{
    Settings st;
    st.source = Source::UdpH264;
    st.udpUrl = "0.0.0.0:5600";
    ReceiverState rx;                                  // приймач іще порожній

    const Decision first = resolve(st, std::nullopt, rx);
    CHECK(first.uri == "udp://0.0.0.0:5600");
    CHECK(first.changed);
    CHECK(apply(first, rx, st) == Action::Restart);

    const Decision again = resolve(st, std::nullopt, rx);
    CHECK(again.uri == first.uri);
    CHECK(!again.changed);                             // ← ціна перезапуску не платиться
    CHECK(apply(again, rx, st) == Action::Nothing);
}

// 2. Періодичне повідомлення камери не веде до перезапуску.
static void test_camera_repeats()
{
    Settings st;                                       // джерело ще «немає відео»
    ReceiverState rx;
    const StreamInfo info{StreamType::RtpUdp, Encoding::H264, "5600"};

    const Decision first = resolve(st, info, rx);
    CHECK(first.uri == "udp://0.0.0.0:5600");          // самий порт добудовано
    CHECK(first.writeBackSource == Source::UdpH264);
    CHECK(apply(first, rx, st) == Action::Restart);
    CHECK(st.source == Source::UdpH264);               // вибір апарата ліг у налаштування

    for (int i = 0; i < 10; ++i) {                     // камера повторює те саме
        const Decision echo = resolve(st, info, rx);
        CHECK(!echo.changed);
        CHECK(apply(echo, rx, st) == Action::Nothing);
    }
}

// 3. Порожнє поле адреси дає «не налаштовано».
static void test_empty_field()
{
    Settings st;
    st.source  = Source::Rtsp;
    st.rtspUrl = "";
    ReceiverState rx;

    const Decision blank = resolve(st, std::nullopt, rx);
    CHECK(!blank.hasVideo);
    CHECK(apply(blank, rx, st) == Action::Stop);       // зупинити, а не запускати

    st.rtspUrl = "rtsp://192.168.0.10:8554/H264Video";
    const Decision filled = resolve(st, std::nullopt, rx);
    CHECK(filled.hasVideo);
    CHECK(apply(filled, rx, st) == Action::Restart);
}

// 4. Жива величина доходить до приймача, але перезапуску не спричиняє.
static void test_live_setting()
{
    Settings st;
    st.source  = Source::Rtsp;
    st.rtspUrl = "rtsp://10.0.0.7:8554/live";
    ReceiverState rx;
    apply(resolve(st, std::nullopt, rx), rx, st);
    CHECK(rx.autoReconnect);

    st.autoReconnect = false;                          // користувач зняв галочку
    const Decision d = resolve(st, std::nullopt, rx);
    CHECK(!d.changed);
    CHECK(apply(d, rx, st) == Action::Nothing);
    CHECK(!rx.autoReconnect);                          // значення все одно дійшло

    st.lowLatency = true;                              // а це вже в конвеєр
    const Decision hard = resolve(st, std::nullopt, rx);
    CHECK(hard.changed);
    CHECK(apply(hard, rx, st) == Action::Restart);
}

// 5. Апарат сильніший за людину; той самий порт з іншим кодеком — інший потік.
static void test_priority_and_scheme()
{
    Settings st;
    st.source  = Source::Rtsp;
    st.rtspUrl = "rtsp://ручна.адреса/live";
    ReceiverState rx;
    const StreamInfo info{StreamType::Rtsp, Encoding::H264, "rtsp://10.0.0.7:8554/live"};
    CHECK(resolve(st, info, rx).uri == "rtsp://10.0.0.7:8554/live");

    Settings us;
    us.source = Source::UdpH264;
    us.udpUrl = "0.0.0.0:5600";
    ReceiverState ur;
    apply(resolve(us, std::nullopt, ur), ur, us);
    us.source = Source::UdpH265;                       // та сама адреса, інший кодек
    const Decision d = resolve(us, std::nullopt, ur);
    CHECK(d.uri == "udp265://0.0.0.0:5600");
    CHECK(d.changed);                                  // ← схема несе тип, тому зміну видно
}

int main()
{
    test_idempotent();
    test_camera_repeats();
    test_empty_field();
    test_live_setting();
    test_priority_and_scheme();

    if (failures > 0) {
        std::printf("провалено перевірок: %d\n", failures);
        return 1;
    }
    std::printf("усі перевірки пройдено\n");
    return 0;
}
