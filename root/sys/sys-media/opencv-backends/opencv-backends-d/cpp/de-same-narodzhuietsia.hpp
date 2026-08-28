UMat Mat::getUMat(AccessFlag accessFlags, UMatUsageFlags usageFlags) const
{
    ...
    if (data != datastart)          // це виріз усередині більшого буфера
    {
        ...
        src.adjustROI(dtop, dbottom, dleft, dright);   // розтягнути до цілого
        return src.getUMat(accessFlags, usageFlags)(cv::Rect(ofs.x, ofs.y, sz.width, sz.height));
    }
    CV_Assert(data == datastart);
    ...
}
