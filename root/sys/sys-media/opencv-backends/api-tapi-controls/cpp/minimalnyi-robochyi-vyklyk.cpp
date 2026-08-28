#include <opencv2/core.hpp>
#include <opencv2/core/ocl.hpp>
#include <opencv2/imgproc.hpp>
#include <opencv2/videoio.hpp>
#include <cstdio>

int main()
{
    if (!cv::ocl::haveOpenCL())
        std::printf("бібліотеки драйвера немає — усе піде процесором\n");

    const cv::ocl::Device& d = cv::ocl::Device::getDefault();
    std::printf("%s | %s | спільна памʼять: %d | один буфер до %zu МБ\n",
                d.name().c_str(), d.OpenCLVersion().c_str(),
                (int)d.hostUnifiedMemory(), d.maxMemAllocSize() >> 20);

    cv::VideoCapture cap("in.mp4", cv::CAP_FFMPEG, {
        cv::CAP_PROP_HW_ACCELERATION,            cv::VIDEO_ACCELERATION_ANY,
        cv::CAP_PROP_HW_DEVICE,                  0,
        cv::CAP_PROP_HW_ACCELERATION_USE_OPENCL, 1
    });
    if (!cap.isOpened())
        return 1;
    std::printf("дісталося прискорення: %d\n",
                (int)cap.get(cv::CAP_PROP_HW_ACCELERATION));

    cv::UMat frame, gray, blurred;
    for (int i = 0; cap.read(frame); ++i)
    {
        cv::cvtColor(frame, gray, cv::COLOR_BGR2GRAY);
        cv::GaussianBlur(gray, blurred, {5, 5}, 1.5);

        if (i == 10)                       // перші кадри платять за компіляцію ядер
        {
            cv::ocl::finish();
            int64 t0 = cv::getTickCount();
            cv::GaussianBlur(gray, blurred, {5, 5}, 1.5);
            cv::ocl::finish();
            std::printf("розмиття: %.2f мс\n",
                        (cv::getTickCount() - t0) * 1000.0 / cv::getTickFrequency());
        }
    }
    return 0;
}
