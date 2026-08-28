// Усе, що мусить пережити кадр і померти разом із ним.
struct MappedSample {
    GstSample* sample = nullptr;   // НАШЕ посилання на зразок
    GstBuffer* buffer = nullptr;   // позичений у зразка
    GstMapInfo map{};
};

class GstMatAllocator final : public cv::MatAllocator
{
public:
    // Цей перевантажений allocate ми кличемо самі, передавши відображені байти.
    cv::UMatData* allocate(int dims, const int* sizes, int type,
                           void* data0, size_t* step,
                           cv::AccessFlag, cv::UMatUsageFlags) const override
    {
        CV_Assert(data0 != nullptr);        // ми загортаємо чуже, а не виділяємо своє

        size_t total = CV_ELEM_SIZE(type);
        for (int i = dims - 1; i >= 0; --i) {
            if (step) {
                if (step[i] != CV_AUTOSTEP) { CV_Assert(total <= step[i]); total = step[i]; }
                else                        { step[i] = total; }
            }
            total *= sizes[i];
        }

        cv::UMatData* u = new cv::UMatData(this);   // → currAllocator = this, refcount = 0
        u->data = u->origdata = static_cast<uchar*>(data0);
        u->size = total;
        u->flags |= cv::UMatData::USER_ALLOCATED;   // ← без цього буде fastFree чужого вказівника
        return u;
    }

    bool allocate(cv::UMatData* u, cv::AccessFlag, cv::UMatUsageFlags) const override
    {
        return u != nullptr;                        // шлях UMat нам не потрібен
    }

    void deallocate(cv::UMatData* u) const override
    {
        if (!u) return;
        CV_Assert(u->urefcount == 0 && u->refcount == 0);

        auto* hold = static_cast<MappedSample*>(u->userdata);
        if (hold) {
            gst_buffer_unmap(hold->buffer, &hold->map);   // спершу закрити відображення…
            gst_sample_unref(hold->sample);               // …і аж потім відпустити зразок
            delete hold;
        }
        delete u;                                          // fastFree не кличемо — пам'ять чужа
    }
};

// Алокатор без стану — отже, один на процес.
static const GstMatAllocator& gstAllocator()
{
    static const GstMatAllocator instance;
    return instance;
}
