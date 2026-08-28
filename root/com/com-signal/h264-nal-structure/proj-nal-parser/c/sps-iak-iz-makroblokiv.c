typedef struct {
    int      valid;
    unsigned id, profile_idc, level_idc;
    unsigned chroma_format_idc, separate_colour_plane_flag;
    unsigned log2_max_frame_num;      /* уже з доданою четвіркою */
    unsigned poc_type, log2_max_poc_lsb, poc_always_zero;
    unsigned frame_mbs_only_flag;
    unsigned coded_w, coded_h;        /* пікселі до обрізання */
    unsigned width, height;           /* справжні пікселі картинки */
} sps_t;

/* Матриці квантування нас не цікавлять, але пропустити їх, не прочитавши,
   неможливо — довжина кожного значення залежить від самого значення. */
static void skip_scaling_list(bits_t *br, int n)
{
    int last = 8, next = 8;
    for (int j = 0; j < n && !br->bad; j++) {
        if (next != 0) next = (last + se(br) + 256) % 256;
        if (next != 0) last = next;
    }
}

static int parse_sps(const uint8_t *rbsp, long len, sps_t *s)
{
    bits_t br; bits_init(&br, rbsp, len);
    memset(s, 0, sizeof *s);

    s->profile_idc = un(&br, 8);
    un(&br, 8);                     /* прапорці обмежень + резерв */
    s->level_idc   = un(&br, 8);
    s->id          = ue(&br);
    if (s->id > 31) return 0;

    s->chroma_format_idc = 1;       /* 4:2:0 — значення за замовчуванням */
    switch (s->profile_idc) {
    case 100: case 110: case 122: case 244: case  44:
    case  83: case  86: case 118: case 128: case 138:
    case 139: case 134: case 135: case 144:
        s->chroma_format_idc = ue(&br);
        if (s->chroma_format_idc > 3) return 0;
        if (s->chroma_format_idc == 3) s->separate_colour_plane_flag = u1(&br);
        ue(&br);                    /* bit_depth_luma_minus8   */
        ue(&br);                    /* bit_depth_chroma_minus8 */
        u1(&br);                    /* qpprime_y_zero_transform_bypass_flag */
        if (u1(&br)) {              /* seq_scaling_matrix_present_flag */
            int lists = (s->chroma_format_idc != 3) ? 8 : 12;
            for (int i = 0; i < lists; i++)
                if (u1(&br)) skip_scaling_list(&br, (i < 6) ? 16 : 64);
        }
        break;
    default: break;
    }

    s->log2_max_frame_num = ue(&br) + 4;
    if (s->log2_max_frame_num > 16) return 0;

    s->poc_type = ue(&br);
    if (s->poc_type == 0) {
        s->log2_max_poc_lsb = ue(&br) + 4;
        if (s->log2_max_poc_lsb > 16) return 0;
    } else if (s->poc_type == 1) {
        s->poc_always_zero = u1(&br);
        se(&br); se(&br);           /* зсуви для неопорних кадрів і полів */
        uint32_t cycle = ue(&br);
        if (cycle > 255) return 0;
        for (uint32_t i = 0; i < cycle && !br.bad; i++) se(&br);
    } else if (s->poc_type > 2) return 0;

    ue(&br);                        /* max_num_ref_frames */
    u1(&br);                        /* gaps_in_frame_num_value_allowed_flag */

    uint32_t mbs_w = ue(&br) + 1;
    uint32_t map_h = ue(&br) + 1;
    if (mbs_w > 4096 || map_h > 4096) return 0;

    s->frame_mbs_only_flag = u1(&br);
    if (!s->frame_mbs_only_flag) u1(&br);   /* mb_adaptive_frame_field_flag */
    u1(&br);                                /* direct_8x8_inference_flag    */

    uint32_t cl = 0, cr = 0, ct = 0, cb = 0;
    if (u1(&br)) {                          /* frame_cropping_flag */
        cl = ue(&br); cr = ue(&br); ct = ue(&br); cb = ue(&br);
        if (cl > 4096 || cr > 4096 || ct > 4096 || cb > 4096) return 0;
    }
    if (br.bad) return 0;

    s->coded_w = mbs_w * 16;
    s->coded_h = map_h * (2u - s->frame_mbs_only_flag) * 16;

    /* Одиниця обрізання — не піксель. По горизонталі це SubWidthC,
       по вертикалі SubHeightC, ще й подвоєне, коли кадр може бути полями. */
    unsigned ux = 1, uy = 2 - s->frame_mbs_only_flag;
    if (s->chroma_format_idc != 0 && !s->separate_colour_plane_flag) {
        unsigned sub_w = (s->chroma_format_idc == 3) ? 1 : 2;
        unsigned sub_h = (s->chroma_format_idc == 1) ? 2 : 1;
        ux = sub_w;
        uy = sub_h * (2 - s->frame_mbs_only_flag);
    }

    uint32_t cut_x = (cl + cr) * ux, cut_y = (ct + cb) * uy;
    if (cut_x >= s->coded_w || cut_y >= s->coded_h) return 0;
    s->width  = s->coded_w - cut_x;
    s->height = s->coded_h - cut_y;
    s->valid  = 1;
    return 1;
}
