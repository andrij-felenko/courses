// umat_boundaries.cpp — один ланцюжок, чотири маршрути, чесний вимір.
//
//   g++ -O2 -std=c++17 umat_boundaries.cpp -o umat_boundaries \
//       $(pkg-config --cflags --libs opencv4)

#include <opencv2/core.hpp>
#include <opencv2/core/ocl.hpp>
#include <opencv2/imgproc.hpp>

#include <algorithm>
#include <cstdint>
#include <cstdio>
#include <string>
#include <vector>

// Мілісекунди між двома відліками. Переводимо саме різницю: лічильник тіків
// росте від старту машини, і множити його на 1000.0 — втрачати молодші розряди.
static double msBetween(int64_t a, int64_t b)
{
    return (b - a) * 1000.0 / cv::getTickFrequency();
}

// Закрити чергу пристрою. Без цього виклику будь-яке число нижче — вигадка.
static void syncDevice()
{
    if (cv::ocl::useOpenCL())
        cv::ocl::finish();
}

// Скільки байтів і скільки разів кадр перетнув межу за один прохід.
struct Wall {
    long long up = 0, down = 0;
    int crossings = 0;

    void toDevice(const cv::Mat& m)
    { up   += (long long)m.total() * m.elemSize(); ++crossings; }

    void toHost(const cv::UMat& u)
    { down += (long long)u.total() * u.elemSize(); ++crossings; }

    long long total() const { return up + down; }
};

// Єдині два місця в програмі, де межу перетинають свідомо.
static void upload(const cv::Mat& src, cv::UMat& dst, Wall& w)
{
    src.copyTo(dst);            // Mat::copyTo у UMat — це upload у буфер пристрою
    w.toDevice(src);
}

static void download(const cv::UMat& src, cv::Mat& dst, Wall& w)
{
    src.copyTo(dst);            // UMat::copyTo у Mat — це download із буфера
    w.toHost(src);
}
