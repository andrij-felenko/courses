__kernel void applyCurve(__global const uchar* srcptr, int src_step, int src_offset,
                         __global uchar* dstptr, int dst_step, int dst_offset,
                         int dst_rows, int dst_cols,
                         __global const uchar* curve)
{
    int x = get_global_id(0);
    int y = get_global_id(1);
    if (x < dst_cols && y < dst_rows)
        dstptr[mad24(y, dst_step, x + dst_offset)] =
            curve[srcptr[mad24(y, src_step, x + src_offset)]];
}
