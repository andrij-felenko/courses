#include <intrin.h>

/* Скалярні інтринсики MSVC для архітектур x86 / x64 / ARM / ARM64 */
unsigned int __popcnt(unsigned int value);
unsigned short __popcnt16(unsigned short value);
unsigned __int64 __popcnt64(unsigned __int64 value);

/* Векторні інтринсики SSE4.2 */
unsigned int _mm_popcnt_u32(unsigned int a);
unsigned __int64 _mm_popcnt_u64(unsigned __int64 a);
