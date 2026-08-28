void invert(cv::Mat& m)                      // CV_8UC3, на місці
{
    int rows = m.rows;
    int cols = m.cols * m.channels();        // байтів у рядку — корисних

    if (m.isContinuous()) {                  // весь блок — один довгий рядок
        cols *= rows;
        rows = 1;
    }

    for (int y = 0; y < rows; ++y) {
        uchar* p = m.ptr<uchar>(y);          // початок рядка y
        for (int i = 0; i < cols; ++i)
            p[i] = 255 - p[i];
    }
}
