class CV_EXPORTS MatAllocator
{
public:
    virtual UMatData* allocate(int dims, const int* sizes, int type,
                               void* data, size_t* step,
                               AccessFlag flags, UMatUsageFlags usageFlags) const = 0;
    virtual bool allocate(UMatData* data, AccessFlag accessflags,
                          UMatUsageFlags usageFlags) const = 0;
    virtual void deallocate(UMatData* data) const = 0;
    virtual void map(UMatData* data, AccessFlag accessflags) const;
    virtual void unmap(UMatData* data) const;
    virtual void download(UMatData* data, void* dst, int dims, const size_t sz[],
                          const size_t srcofs[], const size_t srcstep[],
                          const size_t dststep[]) const;
    virtual void upload(UMatData* data, const void* src, int dims, const size_t sz[],
                        const size_t dstofs[], const size_t dststep[],
                        const size_t srcstep[]) const;
    virtual void copy(UMatData* srcdata, UMatData* dstdata, int dims, const size_t sz[],
                      const size_t srcofs[], const size_t srcstep[],
                      const size_t dstofs[], const size_t dststep[], bool sync) const;
    virtual BufferPoolController* getBufferPoolController(const char* id = NULL) const;
};
