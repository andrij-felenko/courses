#include <opencv2/core.hpp>
#include <cstdio>
#include <vector>

static void describe(const char* name, const cv::Mat& m)
{
    cv::Size whole(0, 0);
    cv::Point ofs(0, 0);
    if (m.dims == 2 && m.data)
        m.locateROI(whole, ofs);

    std::printf("%-6s rows=%-4d cols=%-4d flags=0x%08x elemSize=%zu step[0]=%zu\n",
                name, m.rows, m.cols, (unsigned)m.flags, m.elemSize(), m.step[0]);
    std::printf("       isContinuous=%d isSubmatrix=%d u=%s refcount=%d\n",
                (int)m.isContinuous(), (int)m.isSubmatrix(),
                m.u ? "є" : "нема", m.u ? m.u->refcount : 0);
    std::printf("       whole=%dx%d ofs=(%d,%d) корисних байтів у рядку=%zu\n\n",
                whole.width, whole.height, ofs.x, ofs.y,
                m.cols * m.elemSize());
}

int main()
{
    const int W = 1366, H = 768, STRIDE = 4160;    // 1366·3 = 4098, вирівняно на 64
    std::vector<uchar> pool((size_t)STRIDE * H);   // «чужий» буфер

    cv::Mat frame(H, W, CV_8UC3, pool.data(), STRIDE);   // володіння немає
    cv::Mat roi   = frame(cv::Rect(100, 100, 64, 64));   // вид на вид
    cv::Mat owned = roi.clone();                         // власний блок

    describe("frame", frame);
    describe("roi",   roi);
    describe("owned", owned);
    return 0;
}
