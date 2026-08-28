/* плоскість 31 → FB_ID=27, SRC_W=1920.0, CRTC_ID=42
   CRTC     42 → ACTIVE=1, MODE_ID=блоб 88
   роз'єм   55 → CRTC_ID=42                                        */

__u32 objs[]   = {  31,  42,  55 };            /* count_objs = 3   */
__u32 nprops[] = {   3,   2,   1 };            /* сума = 6         */

__u32 props[]  = { p_fb, p_srcw, p_crtc,       /*   об'єкта 31     */
                   p_active, p_modeid,         /*   об'єкта 42     */
                   p_conn_crtc };              /*   об'єкта 55     */
__u64 values[] = {   27, 1920ull << 16, 42,
                      1, 88,
                     42 };
