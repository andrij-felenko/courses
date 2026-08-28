__kernel void localRange(__global const uchar* srcptr, int src_step, int src_offset,
                         __global uchar* dstptr, int dst_step, int dst_offset,
                         int dst_rows, int dst_cols
#ifdef HAVE_MASK
                       , __global const uchar* mskptr, int msk_step, int msk_offset
#endif
                        )
{
    const int x = get_global_id(0);
    const int y = get_global_id(1);
    if (x >= dst_cols || y >= dst_rows)
        return;

    const int di = mad24(y, dst_step, x + dst_offset);

#ifdef HAVE_MASK
    if (mskptr[mad24(y, msk_step, x + msk_offset)] == 0) {
        dstptr[di] = 0;
        return;
    }
#endif

    const int r = KSIZE / 2;
    int lo = 255, hi = 0;
    for (int dy = -r; dy <= r; ++dy) {
        const int yy = clamp(y + dy, 0, dst_rows - 1);
        for (int dx = -r; dx <= r; ++dx) {
            const int xx = clamp(x + dx, 0, dst_cols - 1);
            const int v = srcptr[mad24(yy, src_step, xx + src_offset)];
            lo = min(lo, v);
            hi = max(hi, v);
        }
    }
    dstptr[di] = convert_uchar(hi - lo);
}
