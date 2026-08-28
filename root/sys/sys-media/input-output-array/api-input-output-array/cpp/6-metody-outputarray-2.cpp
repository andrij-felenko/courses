void _OutputArray::move(Mat& m) const
{
    if (fixedSize())
    {
        assign(m);          // ← заборона розміру мовчки перетворює переміщення на копію
        return;
    }
    int k = kind();
    if (k == UMAT)      { m.copyTo(*(UMat*)obj); m.release(); }
    else if (k == MAT)  { *(Mat*)obj = std::move(m); }
    else if (k == MATX) { m.copyTo(getMat()); m.release(); }
    else CV_Error(Error::StsNotImplemented, "");
}
