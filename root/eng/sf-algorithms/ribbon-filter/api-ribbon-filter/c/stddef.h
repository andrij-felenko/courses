#include <stddef.h>

RibbonStatus ribbon_serialize(const RibbonFilter *filter,
                              void *buffer,
                              size_t buffer_size,
                              size_t *out_written_bytes);

RibbonStatus ribbon_open_zerocopy(const void *mapped_buffer,
                                  size_t buffer_size,
                                  RibbonFilter *out_filter);
