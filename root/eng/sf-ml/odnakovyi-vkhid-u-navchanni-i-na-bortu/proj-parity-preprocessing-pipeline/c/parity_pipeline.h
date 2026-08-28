// parity_pipeline.h
#ifndef PARITY_PIPELINE_H
#define PARITY_PIPELINE_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    int32_t m0[3];       // Множники масштабу у форматі Q0.31 (R, G, B)
    int32_t shift[3];    // Зсуви (31)
    int32_t z_eff[3];    // Ефективні нульові точки (R, G, B)
} PipelineQuantConfig;

typedef struct {
    int in_width;
    int in_height;
    int out_width;
    int out_height;
    int32_t step_x_q16;
    int32_t step_y_q16;
    PipelineQuantConfig quant;
} ParityPipelineContext;

bool parity_pipeline_init(
    ParityPipelineContext *ctx,
    int in_w, int in_h,
    int out_w, int out_h,
    const PipelineQuantConfig *quant_cfg);

void parity_pipeline_process_row(
    const ParityPipelineContext *ctx,
    const uint16_t *row0_rgb565,
    const uint16_t *row1_rgb565,
    int out_row_idx,
    int8_t *out_tensor_row_nhwc);

void parity_pipeline_process_frame(
    const ParityPipelineContext *ctx,
    const uint16_t *src_frame_rgb565,
    int8_t *dst_tensor_nhwc);

#ifdef __cplusplus
}
#endif

#endif // PARITY_PIPELINE_H

// parity_pipeline.c
#include "parity_pipeline.h"

#define CLAMP_INT8(val) (((val) < -128) ? -128 : (((val) > 127) ? 127 : (val)))
#define CLAMP_COORD(val, max_val) (((val) < 0) ? 0 : (((val) > (max_val)) ? (max_val) : (val)))

static inline void unpack_rgb565(uint16_t raw, uint8_t *r, uint8_t *g, uint8_t *b) {
    uint32_t r5 = (raw >> 11) & 0x1F;
    uint32_t g6 = (raw >> 5) & 0x3F;
    uint32_t b5 = raw & 0x1F;
    *r = (uint8_t)((r5 << 3) | (r5 >> 2));
    *g = (uint8_t)((g6 << 2) | (g6 >> 4));
    *b = (uint8_t)((b5 << 3) | (b5 >> 2));
}

static inline int8_t quantize_channel(uint8_t val, int32_t m0, int32_t shift, int32_t z_eff) {
    int64_t prod = (int64_t)val * m0;
    int64_t rounded = (prod + (1LL << (shift - 1))) >> shift;
    int32_t res = (int32_t)rounded + z_eff;
    return (int8_t)CLAMP_INT8(res);
}

bool parity_pipeline_init(
    ParityPipelineContext *ctx,
    int in_w, int in_h,
    int out_w, int out_h,
    const PipelineQuantConfig *quant_cfg)
{
    if (!ctx || !quant_cfg || in_w <= 0 || in_h <= 0 || out_w <= 0 || out_h <= 0) {
        return false;
    }

    ctx->in_width = in_w;
    ctx->in_height = in_h;
    ctx->out_width = out_w;
    ctx->out_height = out_h;
    ctx->quant = *quant_cfg;

    ctx->step_x_q16 = (int32_t)(((int64_t)in_w << 16) / out_w);
    ctx->step_y_q16 = (int32_t)(((int64_t)in_h << 16) / out_h);

    return true;
}

void parity_pipeline_process_row(
    const ParityPipelineContext *ctx,
    const uint16_t *row0_rgb565,
    const uint16_t *row1_rgb565,
    int out_row_idx,
    int8_t *out_tensor_row_nhwc)
{
    int32_t v_y = (int32_t)(((int64_t)(out_row_idx * 2 + 1) * ctx->step_y_q16 - (1 << 16)) >> 1);
    int32_t v_clamped = CLAMP_COORD(v_y, (ctx->in_height - 1) << 16);
    int32_t frac_y = v_clamped & 0xFFFF;

    int32_t u_x = (ctx->step_x_q16 - (1 << 16)) >> 1;

    for (int ox = 0; ox < ctx->out_width; ++ox) {
        int32_t u_clamped = CLAMP_COORD(u_x, (ctx->in_width - 1) << 16);
        int x0 = u_clamped >> 16;
        int x1 = (x0 < ctx->in_width - 1) ? x0 + 1 : x0;
        int32_t frac_x = u_clamped & 0xFFFF;

        uint8_t r00, g00, b00, r10, g10, b10;
        uint8_t r01, g01, b01, r11, g11, b11;
        unpack_rgb565(row0_rgb565[x0], &r00, &g00, &b00);
        unpack_rgb565(row0_rgb565[x1], &r10, &g10, &b10);
        unpack_rgb565(row1_rgb565[x0], &r01, &g01, &b01);
        unpack_rgb565(row1_rgb565[x1], &r11, &g11, &b11);

        int32_t w00 = ((65536 - frac_x) * (65536 - frac_y)) >> 16;
        int32_t w10 = (frac_x * (65536 - frac_y)) >> 16;
        int32_t w01 = ((65536 - frac_x) * frac_y) >> 16;
        int32_t w11 = (frac_x * frac_y) >> 16;

        uint8_t r = (uint8_t)((r00 * w00 + r10 * w10 + r01 * w01 + r11 * w11 + 32768) >> 16);
        uint8_t g = (uint8_t)((g00 * w00 + g10 * w10 + g01 * w01 + g11 * w11 + 32768) >> 16);
        uint8_t b = (uint8_t)((b00 * w00 + b10 * w10 + b01 * w01 + b11 * w11 + 32768) >> 16);

        int dst_idx = ox * 3;
        out_tensor_row_nhwc[dst_idx + 0] = quantize_channel(r, ctx->quant.m0[0], ctx->quant.shift[0], ctx->quant.z_eff[0]);
        out_tensor_row_nhwc[dst_idx + 1] = quantize_channel(g, ctx->quant.m0[1], ctx->quant.shift[1], ctx->quant.z_eff[1]);
        out_tensor_row_nhwc[dst_idx + 2] = quantize_channel(b, ctx->quant.m0[2], ctx->quant.shift[2], ctx->quant.z_eff[2]);

        u_x += ctx->step_x_q16;
    }
}

void parity_pipeline_process_frame(
    const ParityPipelineContext *ctx,
    const uint16_t *src_frame_rgb565,
    int8_t *dst_tensor_nhwc)
{
    for (int oy = 0; oy < ctx->out_height; ++oy) {
        int32_t v_y = (int32_t)(((int64_t)(oy * 2 + 1) * ctx->step_y_q16 - (1 << 16)) >> 1);
        int32_t v_clamped = CLAMP_COORD(v_y, (ctx->in_height - 1) << 16);
        int y0 = v_clamped >> 16;
        int y1 = (y0 < ctx->in_height - 1) ? y0 + 1 : y0;

        const uint16_t *row0 = &src_frame_rgb565[y0 * ctx->in_width];
        const uint16_t *row1 = &src_frame_rgb565[y1 * ctx->in_width];
        int8_t *out_row = &dst_tensor_nhwc[oy * ctx->out_width * 3];

        parity_pipeline_process_row(ctx, row0, row1, oy, out_row);
    }
}
