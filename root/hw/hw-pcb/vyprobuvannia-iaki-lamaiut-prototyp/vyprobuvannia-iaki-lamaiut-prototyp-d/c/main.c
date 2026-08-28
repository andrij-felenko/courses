#include <stdio.h>
#include <math.h>
#include <stdbool.h>

#define MAX_PSD_POINTS 16

typedef struct {
    double freq_hz;
    double psd_g2_hz;
} PsdBreakpoint;

typedef struct {
    double spec_low;
    double spec_high;
    double measured_lol;
    double measured_uol;
    double measured_ldl;
    double measured_udl;
} StressLimits;

typedef struct {
    double op_margin_low;
    double op_margin_high;
    double destruct_margin_low;
    double destruct_margin_high;
    bool is_qualified;
} MarginReport;

double calculate_g_rms(const PsdBreakpoint *pts, size_t count) {
    if (count < 2) return 0.0;
    double total_area = 0.0;

    for (size_t i = 0; i < count - 1; ++i) {
        double f1 = pts[i].freq_hz;
        double f2 = pts[i + 1].freq_hz;
        double p1 = pts[i].psd_g2_hz;
        double p2 = pts[i + 1].psd_g2_hz;

        if (f1 <= 0.0 || f2 <= f1) continue;

        if (fabs(p1 - p2) < 1e-9) {
            total_area += p1 * (f2 - f1);
        } else {
            double slope_db_oct = 10.0 * log10(p2 / p1) / (log2(f2 / f1));
            double m = slope_db_oct / (10.0 * log10(2.0));

            if (fabs(m + 1.0) < 1e-6) {
                total_area += p1 * f1 * log(f2 / f1);
            } else {
                total_area += (p2 * f2 - p1 * f1) / (m + 1.0);
            }
        }
    }
    return (total_area > 0.0) ? sqrt(total_area) : 0.0;
}

MarginReport evaluate_stress_margins(const StressLimits *limits, double min_op_margin_pct, double min_des_margin_pct) {
    MarginReport report;
    double spec_span = limits->spec_high - limits->spec_low;

    report.op_margin_low = (limits->spec_low - limits->measured_lol) / spec_span * 100.0;
    report.op_margin_high = (limits->measured_uol - limits->spec_high) / spec_span * 100.0;
    report.destruct_margin_low = (limits->spec_low - limits->measured_ldl) / spec_span * 100.0;
    report.destruct_margin_high = (limits->measured_udl - limits->spec_high) / spec_span * 100.0;

    report.is_qualified = (report.op_margin_low >= min_op_margin_pct) &&
                          (report.op_margin_high >= min_op_margin_pct) &&
                          (report.destruct_margin_low >= min_des_margin_pct) &&
                          (report.destruct_margin_high >= min_des_margin_pct);
    return report;
}
