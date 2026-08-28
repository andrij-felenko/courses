/* Зібрати один стабілізований кадр. src — знятий кадр (W×H), dst — вихідний.
   Колір беремо білінійно; за межами знятого кадру лишаємо чорне (це і є запас). */
void render_frame(const uint8_t *src, int W, int H, uint8_t *dst, int DW, int DH,
                  const att *att_k, const att *att_k1,
                  const cam_geom *c, const rs_geom *rs, double dt_frame)
{
    for (int yd = 0; yd < DH; ++yd) {
        for (int xd = 0; xd < DW; ++xd) {
            double sx, sy;
            sample_src_rs(att_k, att_k1, c, rs, dt_frame, xd, yd, &sx, &sy);
            dst[yd*DW + xd] = bilinear(src, W, H, sx, sy);  /* домішування сусідів */
        }
    }
}
