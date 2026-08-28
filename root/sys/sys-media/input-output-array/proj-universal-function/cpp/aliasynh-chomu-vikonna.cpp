static bool overlaps(const cv::Mat& a, const cv::Mat& b)
{
    if (!a.datastart || !b.datastart)
        return false;
    if (a.u && b.u && a.u != b.u)
        return false;                 // різні керівні блоки — точно різні буфери

    std::less<const uchar*> before;    // повний порядок; звичайне «<» на покажчиках
    return before(a.datastart, b.dataend) &&   // з різних об'єктів не визначене
           before(b.datastart, a.dataend);
}
