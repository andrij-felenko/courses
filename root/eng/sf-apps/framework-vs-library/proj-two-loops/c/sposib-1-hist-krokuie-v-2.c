#define CAP_MS 16                          // стеля затримки: один кадр 60 Гц

static int gen = 0;                        // мітка покоління таймера
static void tick(int my_gen);

static void arm(void) {
    long ms = -1;
    curl_multi_timeout(multi, &ms);        // −1 → свого дедлайну в libcurl зараз нема
    if (ms < 0 || ms > CAP_MS) ms = CAP_MS;
    glutTimerFunc((unsigned)ms, tick, ++gen);
}

static void tick(int my_gen) {
    if (my_gen != gen) return;             // цей таймер уже скасовано новішим
    int running;
    curl_multi_perform(multi, &running);
    reap_finished();
    if (running > 0) arm();                // нема переносів — нема й таймера
}
