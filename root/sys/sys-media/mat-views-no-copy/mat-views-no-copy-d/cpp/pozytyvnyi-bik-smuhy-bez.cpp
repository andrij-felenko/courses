const int nBands = 4;

cv::parallel_for_(cv::Range(0, nBands), [&](const cv::Range& r) {
    for (int b = r.start; b < r.end; ++b) {
        int y0 =  b      * frame.rows / nBands;
        int y1 = (b + 1) * frame.rows / nBands;

        cv::Mat band = frame.rowRange(y0, y1);          // вид, не копія
        cv::threshold(band, band, 128, 255, cv::THRESH_BINARY);
    }
});
