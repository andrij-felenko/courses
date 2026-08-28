// profiler.cpp — бортовий профайлер зору: стадії, перцентилі, залізо, CSV.
#include "stage_timer.h"
#include "hw_counters.h"
#include <cstdio>
#include <vector>

// Чотири стадії конвеєра зору — кожна зі своїм кільцевим буфером.
struct VisionProfiler {
    StageTimer capture, prep, model, parse, frame;  // frame = повний кадр
    FILE* csv = nullptr;
    int   temp_zone, cpu_id;

    VisionProfiler(size_t win, int zone, int cpu, const char* csv_path)
        : capture(win), prep(win), model(win), parse(win), frame(win),
          temp_zone(zone), cpu_id(cpu) {
        csv = std::fopen(csv_path, "w");
        if (csv)  // заголовок: окремі стадії + повний кадр + залізо
            std::fprintf(csv, "n,capture_ms,prep_ms,model_ms,parse_ms,"
                              "frame_ms,temp_c,cpu_mhz\n");
    }
    ~VisionProfiler() { if (csv) std::fclose(csv); }

    // Один кадр: міряємо кожну стадію, пишемо рядок CSV, повертаємо час кадру.
    double run_frame(int n, Camera& cam, Preproc& pre, Model& net,
                     Parser& post) {
        frame.start();                       // повний кадр — наскрізь

        capture.start();
        Image img = cam.grab();              // взяти кадр із камери
        capture.stop();

        prep.start();
        Tensor in = pre.process(img);        // масштаб, формат, нормування
        prep.stop();

        model.start();
        Output out = net.infer(in);          // сама мережа
        net.synchronize();                   // БАР'ЄР: дочекатися прискорювача!
        model.stop();                        // інакше міряємо чергу, не роботу

        parse.start();
        post.decode(out);                    // розбір виходу мережі
        parse.stop();

        double ft = frame.stop();

        // Залізо тієї ж миті: температура й частота поряд із часом кадру.
        double tc = read_temp_c(temp_zone).value_or(-1.0);
        double fr = read_cpu_mhz(cpu_id).value_or(-1.0);

        if (csv)
            std::fprintf(csv, "%d,%.2f,%.2f,%.2f,%.2f,%.2f,%.1f,%.0f\n",
                         n,
                         last_ms(capture),
                         last_ms(prep), last_ms(model), last_ms(parse),
                         ft, tc, fr);
        return ft;
    }

    // Надрукувати зведення по стадіях (перцентилі за поточним вікном).
    void report() const {
        print_row("захоплення", capture.snapshot());
        print_row("підготовка", prep.snapshot());
        print_row("модель    ", model.snapshot());
        print_row("розбір    ", parse.snapshot());
        print_row("КАДР      ", frame.snapshot());
    }

private:
    // Останній записаний час стадії (для рядка CSV беремо саме його, не перцентиль).
    static double last_ms(const StageTimer&) ; // (реалізація — нижче в нотатці)

    static void print_row(const char* name, const Stats& s) {
        std::printf("%s  сер %.1f | p50 %.1f | p95 %.1f | p99 %.1f | "
                    "max %.1f мс  (%.1f FPS за p99)\n",
                    name, s.mean, s.p50, s.p95, s.p99, s.max,
                    s.p99 > 0 ? 1000.0 / s.p99 : 0.0);
    }
};
