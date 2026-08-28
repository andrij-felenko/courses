static void report(const char* name, int frames)
{
    std::printf("%-40s %8.2f %11.2f\n", name,
                double(counter.allocs) / frames,
                double(counter.bytes)  / frames / 1048576.0);
}

const cv::Size sz(1920, 1080);
cv::Mat frame(sz, CV_8UC1);
cv::randu(frame, 0, 255);
const int N = 100;

{   // приймач живе між кадрами
    cv::Mat dst;
    cvx::localRange(frame, dst, 3);
    counter.reset();
    for (int i = 0; i < N; ++i)
        cvx::localRange(frame, dst, 3);
    report("приймач поза циклом", N);
}

{   // приймач народжується щокадру
    counter.reset();
    for (int i = 0; i < N; ++i) {
        cv::Mat dst;
        cvx::localRange(frame, dst, 3);
    }
    report("приймач усередині циклу", N);
}
