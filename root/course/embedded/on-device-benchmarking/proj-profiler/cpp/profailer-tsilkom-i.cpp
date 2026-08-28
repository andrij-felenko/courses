// Головний цикл: ПРОГРІВ у смітник, тоді ВИМІР — потоком РІЗНИХ кадрів.
int main() {
    Camera   cam;
    Preproc  pre;
    Model    net("detector.bin");
    Parser   post;

    // Профайлер: вікно 512, теплова зона 0, ядро 0, лог у файл.
    VisionProfiler prof(/*win=*/512, /*zone=*/0, /*cpu=*/0, "bench.csv");

    // 1) ПРОГРІВ — кілька кадрів у смітник: розганяємо чіп, гріємо кеш коду.
    for (int i = 0; i < 30; ++i) {
        Image img = cam.grab();
        Output out = net.infer(pre.process(img));
        net.synchronize();
        post.decode(out);
    }

    // 2) ДОВГИЙ вимір — десятки секунд, щоб упіймати троттлінг.
    //    Кожна ітерація бере НОВИЙ кадр із камери: кеш не "вивчить" картинку.
    const int N = 3000;                  // ~2 хвилини при 25 FPS
    for (int n = 0; n < N; ++n) {
        prof.run_frame(n, cam, pre, net, post);

        // Раз на секунду — коротке зведення в консоль (видно троттлінг наживо).
        if (n % 25 == 0) {
            auto fs = prof.frame.snapshot();
            double tc = read_temp_c(0).value_or(-1.0);
            std::printf("[%4d]  кадр p99 %.1f мс  (%.1f FPS)  t=%.1f°C\n",
                        n, fs.p99, fs.p99 > 0 ? 1000.0 / fs.p99 : 0.0, tc);
        }
    }

    std::printf("\n=== ПІДСУМОК (перцентилі за останнє вікно) ===\n");
    prof.report();
    return 0;
}
