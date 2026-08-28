void cvx::localRange(cv::InputArray _src, cv::OutputArray _dst, int ksize,
                     cv::InputArray _mask, cv::OutputArray _hist)
{
    CV_Assert(ksize >= 3 && ksize % 2 == 1);
    CV_Assert(_src.dims() <= 2 && _src.type() == CV_8UC1);
    CV_Assert(_mask.empty() || _mask.type() == CV_8UC1);
    CV_Assert(!_dst.fixedType() || _dst.type() == CV_8UC1);

    CVX_OCL_RUN(_dst.isUMat(), ocl_localRange(_src, _dst, ksize, _mask, _hist));

    cv::Mat src  = _src.getMat();          // ← до create, і це не стиль
    cv::Mat mask = _mask.getMat();         // порожній Mat, якщо маски немає

    CV_Assert(mask.empty() || mask.size() == src.size());

    _dst.create(src.size(), CV_8UC1);
    cv::Mat dst = _dst.getMat();
    // ...
}
