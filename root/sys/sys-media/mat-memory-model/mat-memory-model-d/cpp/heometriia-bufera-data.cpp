void addOffset(cv::Mat& m, int delta) {
    CV_Assert(m.type() == CV_8UC1);
    int rowsToScan = m.rows, colsToScan = m.cols;
    if (m.isContinuous()) {           // рядки стикаються —
        colsToScan *= rowsToScan;     // обходимо все одним циклом
        rowsToScan = 1;
    }
    for (int y = 0; y < rowsToScan; ++y) {
        uchar* p = m.ptr<uchar>(y);
        for (int x = 0; x < colsToScan; ++x)
            p[x] = cv::saturate_cast<uchar>(p[x] + delta);
    }
}
