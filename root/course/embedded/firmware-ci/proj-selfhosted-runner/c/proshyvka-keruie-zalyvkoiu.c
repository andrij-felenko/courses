// Стан, який ми виловлюємо з потоку рядків від плати.
struct verdict {
    int alive;    // побачили банер?
    int done;     // побачили RESULT: ...?
    int failed;   // скільки тестів провалено (валідне лише коли done)
};

// Колбек на кожен рядок: шукаємо спершу банер, потім вердикт.
static int on_line(const char *line, void *ctx) {
    struct verdict *v = (struct verdict *)ctx;
    if (!v->alive && strncmp(line, BANNER, strlen(BANNER)) == 0) {
        v->alive = 1;
        return 1;   // банер знайдено — вертаємось, далі шукатимемо вердикт окремо
    }
    if (v->alive) {
        if (strncmp(line, PASS, strlen(PASS)) == 0) { v->done = 1; v->failed = 0; return 1; }
        if (strncmp(line, FAILPFX, strlen(FAILPFX)) == 0) {
            v->done = 1;
            v->failed = atoi(line + strlen(FAILPFX));   // число після префікса
            return 1;
        }
    }
    return 0;   // звичайний рядок логу тесту — пропускаємо далі
}

int main(int argc, char **argv) {
    // argv: <port> <firmware.elf>
    if (argc != 3) { fprintf(stderr, "usage: %s <port> <fw.elf>\n", argv[0]); return 3; }
    const char *port = argv[1];
    const char *fw   = argv[2];

    // 1. Відновити чіп у відомий стан ПЕРЕД заливкою.
    hil_pulse_reset(port, 50);

    // 2. Залити прошивку зовнішнім прошивальником (openocd/st-flash/probe-rs).
    //    Тут — st-flash як приклад; ненульовий код заливки = стенд-проблема.
    char cmd[512];
    snprintf(cmd, sizeof(cmd),
             "st-flash --reset write %s 0x08000000", fw);
    if (system(cmd) != 0) {
        fprintf(stderr, "HIL: заливка провалилась (прошивальник)\n");
        return 2;   // не «тест червоний», а стенд-проблема → карантин
    }

    // 3. Відкрити порт і чекати БАНЕР — доказ, що чіп ожив після заливки.
    int fd = open_serial(port);
    if (fd < 0) { fprintf(stderr, "HIL: не відкрити %s\n", port); return 3; }

    struct verdict v = {0, 0, 0};
    // На старт даємо 3 секунди: заливка + перезапуск + перший рядок.
    if (read_lines_until(fd, now_ms() + 3000, on_line, &v) != 0 || !v.alive) {
        fprintf(stderr, "HIL: чіп НЕ ожив — банер не прийшов за 3 с (карантин)\n");
        hil_pulse_reset(port, 50);   // остання спроба привести в тямі
        close(fd);
        return 2;   // мертвий стенд — код 2, окремий від «тести впали»
    }
    fprintf(stderr, "HIL: чіп ожив (банер прийнято), чекаю вердикт...\n");

    // 4. Чіп живий — тепер чекаємо ВЕРДИКТ. Тестам даємо до 30 с.
    if (read_lines_until(fd, now_ms() + 30000, on_line, &v) != 0 || !v.done) {
        fprintf(stderr, "HIL: вердикт не прийшов за 30 с — тести зависли (карантин)\n");
        close(fd);
        return 2;   // ожив, але завис у тестах — теж стенд-проблема, не «FAIL»
    }

    // 5. Прибрати за собою: лишити чіп у скиді для наступного прогону.
    hil_pulse_reset(port, 50);
    close(fd);

    if (v.failed == 0) {
        fprintf(stderr, "HIL: PASS — усі on-target тести зелені\n");
        return 0;
    }
    fprintf(stderr, "HIL: FAIL — провалено тестів: %d\n", v.failed);
    return 1;   // тести червоні → крок червоний → ворота замкнено
}
