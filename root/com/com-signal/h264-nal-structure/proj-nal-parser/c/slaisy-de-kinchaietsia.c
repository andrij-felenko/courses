typedef struct {
    int      valid;
    unsigned id, sps_id;
    unsigned cabac;        /* entropy_coding_mode_flag */
    unsigned poc_bottom;   /* bottom_field_pic_order_in_frame_present_flag */
} pps_t;

static int parse_pps(const uint8_t *rbsp, long len, pps_t *p)
{
    bits_t br; bits_init(&br, rbsp, len);
    memset(p, 0, sizeof *p);
    p->id     = ue(&br);
    p->sps_id = ue(&br);
    if (br.bad || p->id > 255 || p->sps_id > 31) return 0;
    p->cabac      = u1(&br);
    p->poc_bottom = u1(&br);
    p->valid = !br.bad;
    return p->valid;
}
