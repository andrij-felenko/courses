void dumpOwnership(const cv::Mat& m, const char* name)
{
    std::printf("%s: %dx%d type=%d flags=0x%08X cont=%d sub=%d step0=%zu\n",
                name, m.rows, m.cols, m.type(), m.flags,
                (int)m.isContinuous(), (int)m.isSubmatrix(), m.step[0]);

    if (m.u)
        std::printf("   u=%p refcount=%d urefcount=%d size=%zu user_allocated=%d\n",
                    (void*)m.u, m.u->refcount, m.u->urefcount, m.u->size,
                    (int)((m.u->flags & cv::UMatData::USER_ALLOCATED) != 0));
    else
        std::printf("   u=nullptr — заголовок нічим не володіє\n");

    if (m.dims == 2 && m.step[0] > 0) {
        cv::Size whole; cv::Point ofs;
        m.locateROI(whole, ofs);
        std::printf("   вигляд %dx%d у буфері %dx%d зі зсувом (%d, %d)\n",
                    m.cols, m.rows, whole.width, whole.height, ofs.x, ofs.y);
    }
}
