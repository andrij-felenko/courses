#include <stdio.h>

#if defined(__has_include)
    #if __has_include(<stdfix.h>)
        #define HAS_FIXED_POINT 1
    #else
        #define HAS_FIXED_POINT 0
    #endif
#else
    #define HAS_FIXED_POINT 0
#endif

int main(void) {
    printf("Підтримка фіксованої коми: %d\n", HAS_FIXED_POINT);
    return 0;
}
