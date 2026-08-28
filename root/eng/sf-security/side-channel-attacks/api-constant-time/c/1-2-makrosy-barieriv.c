#if defined(__GNUC__) || defined(__clang__)
#define CT_BARRIER_32(x) do { __asm__ volatile ("" : "+r" (x)); } while(0)
#define CT_BARRIER_64(x) do { __asm__ volatile ("" : "+r" (x)); } while(0)
#define CT_BARRIER_PTR(p) do { __asm__ volatile ("" : "+r" (p)); } while(0)
#elif defined(_MSC_VER)
#define CT_BARRIER_32(x) do { _ReadWriteBarrier(); } while(0)
#define CT_BARRIER_64(x) do { _ReadWriteBarrier(); } while(0)
#define CT_BARRIER_PTR(p) do { _ReadWriteBarrier(); } while(0)
#else
#define CT_BARRIER_32(x) ((void)0)
#define CT_BARRIER_64(x) ((void)0)
#define CT_BARRIER_PTR(p) ((void)0)
#endif
