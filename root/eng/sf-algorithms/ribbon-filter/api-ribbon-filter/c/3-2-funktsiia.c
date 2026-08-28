#include <stddef.h>

typedef struct {
    const void *data;
    size_t length;
} RibbonSlice;

RibbonStatus ribbon_build_bytes(const RibbonOptions *opts,
                                const RibbonSlice *slices,
                                size_t num_slices,
                                RibbonFilter **out_filter);
