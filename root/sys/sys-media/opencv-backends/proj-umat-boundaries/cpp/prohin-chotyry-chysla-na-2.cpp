static std::vector<cv::Mat> makeFrames(cv::Size sz, int n)
{
    std::vector<cv::Mat> v;
    cv::RNG rng(42);
    for (int i = 0; i < n; ++i) {
        cv::Mat f(sz, CV_8UC3, cv::Scalar(30, 30, 30));
        cv::circle(f, {300 + 90 * i, 540}, 260, cv::Scalar(210, 200, 190), -1);
        cv::rectangle(f, cv::Rect(900, 200 + 30 * i, 700, 500),
                      cv::Scalar(160, 170, 180), -1);
        cv::Mat noise(sz, CV_8UC3);
        rng.fill(noise, cv::RNG::UNIFORM, 0, 12);
        f += noise;
        v.push_back(f);
    }
    return v;
}

int main()
{
    buildCurve();

    std::printf("OpenCL: %s", cv::ocl::haveOpenCL() ? "є" : "немає");
    if (cv::ocl::haveOpenCL()) {
        const cv::ocl::Device& d = cv::ocl::Device::getDefault();
        std::printf(", пристрій: %s, спільна пам'ять із хостом: %s",
                    d.name().c_str(), d.hostUnifiedMemory() ? "так" : "ні");
    }
    std::printf("\n\n");

    std::vector<cv::Mat> frames = makeFrames({1920, 1080}, 8);

    struct { const char* name; Route fn; bool onDevice; } routes[] = {
        { "усе на Mat",              routeHost,   false },
        { "усе на UMat",             routeDevice, true  },
        { "UMat + процесорний крок", routeSplit,  true  },
        { "UMat + власне ядро",      routeKernel, true  },
    };

    std::printf("%-26s %8s %8s %8s %8s   %s\n", "маршрут",
                "постан.", "рахунок", "доставка", "разом", "через шину");

    std::vector<Report> reps;
    for (const auto& r : routes)
        reps.push_back(bench(r.name, r.fn, r.onDevice, frames, 10, 60));

    for (const auto& r : reps)
        std::printf("%-26s %8.2f %8.2f %8.2f %8.2f   %6.2f МБ / %d\n",
                    r.name.c_str(), r.enqueue, r.compute, r.deliver, r.total,
                    r.wall.total() / 1048576.0, r.wall.crossings);

    // Маршрути мусять давати ту саму картинку — інакше вимір ні про що.
    for (size_t i = 1; i < reps.size(); ++i)
        std::printf("розбіжність з першим маршрутом: %d пікселів (%s)\n",
                    cv::countNonZero(reps[i].result != reps[0].result),
                    reps[i].name.c_str());
    return 0;
}
