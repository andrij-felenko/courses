    if (_hist.needed()) {
        _hist.create(1, 256, CV_32SC1);
        cv::Mat hist = _hist.getMat();
        hist.setTo(0);
        int* h = hist.ptr<int>();
        for (int y = 0; y < out.rows; ++y) {
            const uchar* d = out.ptr<uchar>(y);
            for (int x = 0; x < out.cols; ++x)
                ++h[d[x]];
        }
    }
