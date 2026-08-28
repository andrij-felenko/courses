// Профілювання конвеєра бортового зору поетапно.
// На Linux/одноплатнику — std::chrono (мікросекундна точність).
// Принцип: RAII-таймер міряє етап від конструктора до деструктора.
#include <chrono>
#include <cstdio>

struct Stage {
    const char* name;
    std::chrono::steady_clock::time_point t0{std::chrono::steady_clock::now()};
    explicit Stage(const char* n) : name(n) {}
    ~Stage() {
        auto dt = std::chrono::duration<double, std::milli>(
                      std::chrono::steady_clock::now() - t0).count();
        std::printf("%-12s %6.2f ms\n", name, dt);
    }
};

void process_frame() {
    Frame f; Roi r; Detections d; float angle;
    { Stage s("захоплення");  capture(&f); }         // камера → буфер
    { Stage s("ROI");         r = select_roi(&f); }  // звузити ділянку
    { Stage s("класика");     preprocess(&r); }      // поріг/фільтр/підготовка
    { Stage s("нейромережа"); d = infer(&r); }       // детектор (CPU або TPU)
    { Stage s("MAVLink");     angle = send_cmd(&d); }// кут → політний контролер
}
