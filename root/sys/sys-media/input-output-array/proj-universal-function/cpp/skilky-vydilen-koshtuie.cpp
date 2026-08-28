class CountingAllocator : public cv::MatAllocator
{
public:
    explicit CountingAllocator(cv::MatAllocator* base) : base_(base) {}

    cv::UMatData* allocate(int dims, const int* sizes, int type, void* data,
                           size_t* step, cv::AccessFlag flags,
                           cv::UMatUsageFlags usage) const override
    {
        cv::UMatData* u = base_->allocate(dims, sizes, type, data, step, flags, usage);
        if (u) {
            ++allocs;
            size_t n = CV_ELEM_SIZE(type);
            for (int i = 0; i < dims; ++i) n *= (size_t)sizes[i];
            bytes += n;
        }
        return u;
    }

    bool allocate(cv::UMatData* u, cv::AccessFlag f, cv::UMatUsageFlags g) const override
    { return base_->allocate(u, f, g); }

    void deallocate(cv::UMatData* u) const override
    { if (u) ++frees; base_->deallocate(u); }

    void map(cv::UMatData* u, cv::AccessFlag f)  const override { base_->map(u, f); }
    void unmap(cv::UMatData* u)                  const override { base_->unmap(u); }

    // download / upload / copy / getBufferPoolController — так само наскрізь у base_.

    void reset() { allocs = 0; frees = 0; bytes = 0; }

    // Внутрішні тимчасові буфери OpenCV народжуються й у робочих потоках,
    // тож лічильники мусять бути атомарними.
    mutable std::atomic<long long> allocs{0}, frees{0}, bytes{0};
private:
    cv::MatAllocator* base_;
};
