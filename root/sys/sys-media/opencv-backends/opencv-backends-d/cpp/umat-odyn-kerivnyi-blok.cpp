struct CV_EXPORTS UMatData {
    int urefcount;      // скільки заголовків UMat
    int refcount;       // скільки заголовків Mat
    uchar* data;        // байти в системній пам'яті (може бути 0)
    uchar* origdata;
    size_t size;
    UMatData::MemoryFlag flags;
    void* handle;       // буфер прискорювача, cl_mem (може бути 0)
    void* userdata;
    int allocatorFlags_;
    int mapcount;
    UMatData* originalUMatData;
};
