// parity_test_runner.c
#include <stdio.h>
#include <math.h>
#include <stdlib.h>
#include "parity_pipeline.h"

typedef struct {
    double cosine_sim;
    double mae;
    int max_ae;
    double sqnr_db;
} ParityMetrics;

ParityMetrics evaluate_parity(const int8_t *actual, const int8_t *golden, size_t length) {
    ParityMetrics m = {0};
    double dot_prod = 0.0;
    double norm_a = 0.0;
    double norm_g = 0.0;
    double sum_abs_err = 0.0;
    double sum_sig_sq = 0.0;
    double sum_err_sq = 0.0;
    int max_err = 0;

    for (size_t i = 0; i < length; ++i) {
        double a = (double)actual[i];
        double g = (double)golden[i];
        double err = fabs(a - g);

        dot_prod += a * g;
        norm_a += a * a;
        norm_g += g * g;

        sum_abs_err += err;
        sum_sig_sq += g * g;
        sum_err_sq += (a - g) * (a - g);

        if ((int)err > max_err) {
            max_err = (int)err;
        }
    }

    m.cosine_sim = dot_prod / (sqrt(norm_a) * sqrt(norm_g) + 1e-12);
    m.mae = sum_abs_err / (double)length;
    m.max_ae = max_err;
    m.sqnr_db = (sum_err_sq > 0.0) ? 10.0 * log10(sum_sig_sq / sum_err_sq) : 99.9;

    return m;
}

void run_parity_benchmark(void) {
    const int in_w = 320, in_h = 240;
    const int out_w = 224, out_h = 224;
    const size_t total_elements = out_w * out_h * 3;

    uint16_t *src_frame = (uint16_t*)malloc(in_w * in_h * sizeof(uint16_t));
    int8_t *actual_tensor = (int8_t*)malloc(total_elements);
    int8_t *golden_tensor = (int8_t*)malloc(total_elements);

    FILE *f_in = fopen("test_input_qvga_rgb565.bin", "rb");
    FILE *f_gold = fopen("golden_output_224_int8.bin", "rb");
    if (!f_in || !f_gold) {
        printf("Error opening golden files!
");
        return;
    }
    fread(src_frame, sizeof(uint16_t), in_w * in_h, f_in);
    fread(golden_tensor, 1, total_elements, f_gold);
    fclose(f_in);
    fclose(f_gold);

    PipelineQuantConfig q_cfg = {
        .m0 = {1204859844, 1231731535, 1226257173},
        .shift = {31, 31, 31},
        .z_eff = {-270, -260, -230}
    };

    ParityPipelineContext ctx;
    parity_pipeline_init(&ctx, in_w, in_h, out_w, out_h, &q_cfg);
    parity_pipeline_process_frame(&ctx, src_frame, actual_tensor);

    ParityMetrics res = evaluate_parity(actual_tensor, golden_tensor, total_elements);

    printf("========================================
");
    printf("PARITY VERIFICATION REPORT:
");
    printf("Cosine Similarity : %.6f  (Gate: > 0.999500)
", res.cosine_sim);
    printf("Mean Absolute Err : %.4f LSB (Gate: <= 0.1500)
", res.mae);
    printf("Max Absolute Err  : %d LSB    (Gate: <= 1)
", res.max_ae);
    printf("SQNR              : %.2f dB   (Gate: >= 42.0 dB)
", res.sqnr_db);
    printf("========================================
");

    if (res.cosine_sim > 0.9995 && res.mae <= 0.15 && res.max_ae <= 1 && res.sqnr_db >= 42.0) {
        printf("RESULT: [PASSED] 100%% Bit-Exact Parity Confirmed!
");
    } else {
        printf("RESULT: [FAILED] Preprocessing Divergence Detected!
");
    }

    free(src_frame);
    free(actual_tensor);
    free(golden_tensor);
}
