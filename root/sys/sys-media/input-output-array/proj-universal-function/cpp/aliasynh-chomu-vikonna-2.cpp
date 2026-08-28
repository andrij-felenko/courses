    cv::Mat scratch, tmp, out = dst;
    if (overlaps(src, dst)) {
        tmp.create(src.size(), CV_8UC1);
        out = tmp;
    }

    localRangeBody(src, out, mask, ksize, scratch);

    if (!tmp.empty())
        tmp.copyTo(dst);
