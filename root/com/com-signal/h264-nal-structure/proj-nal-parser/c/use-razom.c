static const char *nal_name(unsigned t)
{
    switch (t) {
    case 1:  return "слайс";
    case 5:  return "слайс IDR";
    case 6:  return "SEI";
    case 7:  return "SPS";
    case 8:  return "PPS";
    case 9:  return "роздільник AU";
    case 12: return "наповнювач";
    default: return "інше";
    }
}

int main(int argc, char **argv)
{
    if (argc != 2) { fprintf(stderr, "вжиток: %s stream.h264\n", argv[0]); return 2; }

    FILE *f = fopen(argv[1], "rb");
    if (!f) { perror(argv[1]); return 1; }
    if (fseek(f, 0, SEEK_END) != 0) { fprintf(stderr, "потрібен звичайний файл\n"); return 1; }
    long size = ftell(f);
    if (size < 0) { perror("ftell"); return 1; }
    rewind(f);

    uint8_t *buf = malloc(size ? (size_t)size : 1);
    if (!buf || fread(buf, 1, (size_t)size, f) != (size_t)size) {
        fprintf(stderr, "не прочитав файл\n"); return 1;
    }
    fclose(f);

    static sps_t sps_tab[32];
    static pps_t pps_tab[256];
    slice_t prev = { 0 };
    int  have_prev = 0;
    long au = 0, idr = 0, first_idr = -1;

    annexb_t it = { buf, size, 0 };
    nal_t nal;

    while (annexb_next(&it, &nal)) {
        if (nal.len < 1) continue;
        if (nal.data[0] & 0x80) {                    /* forbidden_zero_bit */
            printf("%9ld  заголовок пошкоджено\n", nal.off);
            continue;
        }
        unsigned ref_idc = (nal.data[0] >> 5) & 3u;
        unsigned type    =  nal.data[0] & 0x1Fu;

        printf("%9ld  тип %2u  ref %u  %8ld Б  %s",
               nal.off, type, ref_idc, nal.len, nal_name(type));

        if (type == 7 || type == 8) {
            /* набори параметрів короткі — знімаємо захист повністю, на місці */
            long n = unescape(nal.data + 1, nal.len - 1, nal.data + 1, nal.len - 1);
            if (type == 7) {
                sps_t s;
                if (parse_sps(nal.data + 1, n, &s)) {
                    sps_tab[s.id] = s;
                    printf("  →  %ux%u (кодовано %ux%u), профіль %u, рівень %u.%u",
                           s.width, s.height, s.coded_w, s.coded_h,
                           s.profile_idc, s.level_idc / 10, s.level_idc % 10);
                } else printf("  →  розібрати не вдалося");
            } else {
                pps_t p;
                if (parse_pps(nal.data + 1, n, &p)) {
                    pps_tab[p.id] = p;
                    printf("  →  SPS %u, %s", p.sps_id, p.cabac ? "CABAC" : "CAVLC");
                } else printf("  →  розібрати не вдалося");
            }
        } else if (type == 1 || type == 5) {
            uint8_t hdr[64];        /* заголовка вистачає з головою */
            long n = unescape(hdr, sizeof hdr, nal.data + 1, nal.len - 1);
            slice_t sh;
            if (parse_slice(hdr, n, ref_idc, type, sps_tab, pps_tab, &sh)) {
                int fresh = !have_prev || new_picture(&sh, &prev);
                printf("   mb %u, frame_num %u", sh.first_mb, sh.frame_num);
                if (fresh) {
                    au++;
                    if (type == 5) { idr++; if (first_idr < 0) first_idr = nal.off; }
                    printf("   ← кадр %ld%s", au, type == 5 ? "  (IDR — точка входу)" : "");
                }
                prev = sh; have_prev = 1;
            } else printf("  →  наборів параметрів ще не було");
        }
        putchar('\n');
    }

    printf("\nкадрів: %ld, з них IDR: %ld", au, idr);
    if (first_idr >= 0) printf("; перша точка входу на зсуві %ld\n", first_idr);
    else                printf("; ЖОДНОЇ точки входу — потік нізвідки почати\n");

    free(buf);
    return 0;
}
