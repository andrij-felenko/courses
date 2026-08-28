static uchar    g_curve[256];
static cv::UMat g_curveU;              // та сама таблиця для гілки на пристрої

static void buildCurve()
{
    for (int i = 0; i < 256; ++i) {
        double x = i / 255.0;
        double y = x * x * (3.0 - 2.0 * x);        // м'яка S-подібна крива
        g_curve[i] = cv::saturate_cast<uchar>(y * 255.0);
    }
    cv::Mat(1, 256, CV_8UC1, g_curve).copyTo(g_curveU);
}

// Крок, у якого гілки на прискорювачі немає за визначенням: наш власний цикл.
static void curveOnHost(const cv::Mat& src, cv::Mat& dst)
{
    CV_Assert(src.type() == CV_8UC1);
    dst.create(src.size(), src.type());
    for (int y = 0; y < src.rows; ++y) {
        const uchar* s = src.ptr<uchar>(y);
        uchar*       d = dst.ptr<uchar>(y);
        for (int x = 0; x < src.cols; ++x)
            d[x] = g_curve[s[x]];
    }
}
