typedef struct {
    unsigned first_mb, slice_type, pps_id;
    unsigned frame_num, field_pic, bottom_field;
    unsigned idr_pic_id, poc_lsb;
    int32_t  delta_poc_bottom, delta_poc0, delta_poc1;
    unsigned ref_idc, type;          /* із байта заголовка NAL */
} slice_t;

static int parse_slice(const uint8_t *rbsp, long len,
                       unsigned ref_idc, unsigned type,
                       const sps_t *sps_tab, const pps_t *pps_tab,
                       slice_t *sh)
{
    bits_t br; bits_init(&br, rbsp, len);
    memset(sh, 0, sizeof *sh);
    sh->ref_idc = ref_idc;
    sh->type    = type;

    sh->first_mb   = ue(&br);
    sh->slice_type = ue(&br);
    sh->pps_id     = ue(&br);
    if (br.bad || sh->pps_id > 255) return 0;

    const pps_t *pps = &pps_tab[sh->pps_id];
    if (!pps->valid) return 0;                 /* цього PPS ще не бачили */
    const sps_t *sps = &sps_tab[pps->sps_id];
    if (!sps->valid) return 0;                 /* цього SPS ще не бачили */

    if (sps->separate_colour_plane_flag) un(&br, 2);   /* colour_plane_id */
    sh->frame_num = un(&br, sps->log2_max_frame_num);
    if (!sps->frame_mbs_only_flag) {
        sh->field_pic = u1(&br);
        if (sh->field_pic) sh->bottom_field = u1(&br);
    }
    if (type == 5) sh->idr_pic_id = ue(&br);

    if (sps->poc_type == 0) {
        sh->poc_lsb = un(&br, sps->log2_max_poc_lsb);
        if (pps->poc_bottom && !sh->field_pic) sh->delta_poc_bottom = se(&br);
    } else if (sps->poc_type == 1 && !sps->poc_always_zero) {
        sh->delta_poc0 = se(&br);
        if (pps->poc_bottom && !sh->field_pic) sh->delta_poc1 = se(&br);
    }
    return !br.bad;
}
