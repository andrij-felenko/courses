#include <opencv2/core.hpp>
#include <functional>
#include <utility>

// Заголовок над ЧУЖИМИ байтами, але під лічильником Mat.
// release_ спрацює на останньому release() — не раніше й не пізніше.
class BorrowedAllocator final : public cv::MatAllocator {
public:
    BorrowedAllocator(uchar* bytes, size_t nbytes, size_t rowStep,
                      std::function<void()> release)
        : bytes_(bytes), nbytes_(nbytes), rowStep_(rowStep), release_(std::move(release)) {}

    cv::UMatData* allocate(int dims, const int* sizes, int type,
                           void* data0, size_t* step,
                           cv::AccessFlag, cv::UMatUsageFlags) const override
    {
        CV_Assert(data0 == nullptr && dims == 2 && step != nullptr);

        const size_t esz = CV_ELEM_SIZE(type);
        step[1] = esz;                                   // create() перевіряє саме цей крок
        step[0] = rowStep_ ? rowStep_ : sizes[1] * esz;  // крок рядка джерела, а не ширина
        CV_Assert(step[0] >= sizes[1] * esz);
        CV_Assert(step[0] * sizes[0] <= nbytes_);

        cv::UMatData* u = new cv::UMatData(this);
        u->data = u->origdata = bytes_;
        u->size = step[0] * sizes[0];
        u->flags |= cv::UMatData::USER_ALLOCATED;        // байти не наші: fastFree не чіпати
        return u;
    }

    bool allocate(cv::UMatData* u, cv::AccessFlag, cv::UMatUsageFlags) const override
    {
        return u != nullptr;
    }

    void deallocate(cv::UMatData* u) const override
    {
        if (!u) return;
        CV_Assert(u->refcount == 0 && u->urefcount == 0);
        if (release_) release_();   // ось де відпускається чужий буфер
        delete u;                   // керівний блок завжди наш
    }

private:
    uchar* bytes_;
    size_t nbytes_;
    size_t rowStep_;
    std::function<void()> release_;
};
