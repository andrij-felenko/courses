const MatAllocator* prevAllocator;
const MatAllocator* currAllocator;
int urefcount;      // скільки UMat-заголовків
int refcount;       // скільки Mat-заголовків
uchar* data;        // адреса для процесора (може бути NULL)
uchar* origdata;    // початок виділеного блоку
size_t size;
int flags;
void* handle;       // дескриптор буфера пристрою
void* userdata;
int allocatorFlags_;
