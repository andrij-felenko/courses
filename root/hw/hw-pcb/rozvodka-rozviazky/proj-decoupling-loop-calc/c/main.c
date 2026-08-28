#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>
#include <string.h>

#define SPEED_OF_LIGHT_M_S 299792458.0
#define VACUUM_PERMEABILITY_H_M (4.0 * M_PI * 1e-7)

typedef enum {
    TOPOLOGY_FAR_TRACE = 0,
    TOPOLOGY_END_VIA,
    TOPOLOGY_SIDE_VIA,
    TOPOLOGY_DOUBLE_SIDE_VIA,
    TOPOLOGY_VIA_IN_PAD_TOP,
    TOPOLOGY_BGA_BOTTOM_VIPPO,
    TOPOLOGY_COUNT
} DecouplingTopology;

static const char *TOPOLOGY_DESCRIPTIONS[TOPOLOGY_COUNT] = {
    "1. Far Traces (Віддалений монтаж, довгі траси l=4.0мм, s=3.5мм)",
    "2. End Vias (Торцеві перехідні отвори за контактними падами)",
    "3. Side Vias (Бічні перехідні отвори з мінімальним зазором)",
    "4. Double Side Vias (Подвійні симетричні бічні вії, 4 отвори)",
    "5. Via-in-Pad Top (Технологія VIPPO на верхньому шарі L1)",
    "6. BGA Bottom VIPPO (Монтаж на звороті плати прямо під чіпом)"
};

typedef struct {
    const char *part_name;
    double capacitance_f;
    double esr_ohms;
    double esl_henries;
    double length_m;
    double width_m;
    double pad_len_m;
    double pad_width_m;
} MlccCapacitorModel;

typedef struct {
    double dielectric_er;
    double h_to_gnd_plane_m;
    double h_to_pwr_plane_m;
    double total_board_thickness_m;
    double via_drill_diameter_m;
    double copper_thickness_m;
} PcbStackupModel;

typedef struct {
    double l_esl_nh;
    double l_pads_nh;
    double l_traces_nh;
    double l_vias_nh;
    double l_spread_nh;
    double l_total_mount_nh;
    double srf_frequency_mhz;
    double z_at_srf_mohms;
    double r_eff_100mhz_mm;
    double r_eff_500mhz_mm;
    double r_eff_1ghz_mm;
} DetailedAnalysisResult;

static double calc_partial_rect_inductance(double length_m, double width_m, double thickness_m) {
    if (length_m <= 0.0 || width_m <= 0.0) return 0.0;
    double wt = width_m + thickness_m;
    double ratio = 2.0 * length_m / wt;
    if (ratio <= 0.0) return 0.0;
    double term = log(ratio) + 0.5 + 0.2235 * (wt / length_m);
    return (VACUUM_PERMEABILITY_H_M * length_m / (2.0 * M_PI)) * term;
}

static double calc_via_self_inductance(double height_m, double radius_m) {
    if (height_m <= 0.0 || radius_m <= 0.0) return 0.0;
    double ratio = 2.0 * height_m / radius_m;
    double term = log(ratio + sqrt(1.0 + ratio * ratio)) - sqrt(1.0 + 1.0 / (ratio * ratio)) + (radius_m / (2.0 * height_m)) + 0.25;
    return (VACUUM_PERMEABILITY_H_M * height_m / (2.0 * M_PI)) * term;
}

static double calc_via_mutual_inductance(double height_m, double pitch_m) {
    if (height_m <= 0.0 || pitch_m <= 0.0) return 0.0;
    double hs = height_m / pitch_m;
    double sh = pitch_m / height_m;
    double term = log(hs + sqrt(1.0 + hs * hs)) - sqrt(1.0 + sh * sh) + sh;
    return (VACUUM_PERMEABILITY_H_M * height_m / (2.0 * M_PI)) * term;
}

static double calc_plane_spreading_inductance(double plane_gap_m, double via_radius_m, double pitch_m) {
    if (plane_gap_m <= 0.0 || via_radius_m <= 0.0 || pitch_m <= 2.0 * via_radius_m) return 0.0;
    return (VACUUM_PERMEABILITY_H_M * plane_gap_m / M_PI) * log(pitch_m / (2.0 * via_radius_m));
}

static double calc_effective_decoupling_radius(double frequency_hz, double er, double safety_factor) {
    if (frequency_hz <= 0.0 || er <= 0.0 || safety_factor <= 0.0) return 0.0;
    double v_propagation = SPEED_OF_LIGHT_M_S / sqrt(er);
    return v_propagation / (2.0 * M_PI * frequency_hz * safety_factor);
}

void analyze_decoupling_mounting(const MlccCapacitorModel *cap, const PcbStackupModel *pcb,
                                 DecouplingTopology topology, DetailedAnalysisResult *out_res) {
    double via_r = pcb->via_drill_diameter_m / 2.0;
    double l_pads = 0.0;
    double l_traces = 0.0;
    double l_vias = 0.0;
    double l_spread = 0.0;
    double h_gnd = pcb->h_to_gnd_plane_m;
    double h_pwr = pcb->h_to_pwr_plane_m;
    double d_planes = fabs(pcb->h_to_pwr_plane_m - pcb->h_to_gnd_plane_m);
    if (d_planes < 1e-5) d_planes = 0.0001;

    switch (topology) {
        case TOPOLOGY_FAR_TRACE: {
            double tr_len = 0.0040;
            double tr_w = 0.00025;
            double via_pitch = 0.0035;
            l_pads = 2.0 * calc_partial_rect_inductance(cap->pad_len_m, cap->pad_width_m, pcb->copper_thickness_m);
            l_traces = 2.0 * calc_partial_rect_inductance(tr_len, tr_w, pcb->copper_thickness_m);
            double l_vg = calc_via_self_inductance(h_gnd, via_r);
            double l_vp = calc_via_self_inductance(h_pwr, via_r);
            double m_v = calc_via_mutual_inductance((h_gnd + h_pwr) / 2.0, via_pitch);
            l_vias = l_vg + l_vp - 2.0 * m_v;
            l_spread = calc_plane_spreading_inductance(d_planes, via_r, via_pitch);
            break;
        }
        case TOPOLOGY_END_VIA: {
            double via_pitch = cap->length_m + 2.0 * via_r + 0.00020;
            l_pads = 2.0 * calc_partial_rect_inductance(cap->pad_len_m, cap->pad_width_m, pcb->copper_thickness_m);
            l_traces = 2.0 * calc_partial_rect_inductance(0.00030, cap->pad_width_m, pcb->copper_thickness_m);
            double l_vg = calc_via_self_inductance(h_gnd, via_r);
            double l_vp = calc_via_self_inductance(h_pwr, via_r);
            double m_v = calc_via_mutual_inductance((h_gnd + h_pwr) / 2.0, via_pitch);
            l_vias = l_vg + l_vp - 2.0 * m_v;
            l_spread = calc_plane_spreading_inductance(d_planes, via_r, via_pitch);
            break;
        }
        case TOPOLOGY_SIDE_VIA: {
            double via_pitch = cap->width_m + 2.0 * via_r + 0.00015;
            l_pads = 2.0 * calc_partial_rect_inductance(cap->pad_len_m, cap->pad_width_m, pcb->copper_thickness_m);
            l_traces = 2.0 * calc_partial_rect_inductance(0.00015, cap->pad_width_m, pcb->copper_thickness_m);
            double l_vg = calc_via_self_inductance(h_gnd, via_r);
            double l_vp = calc_via_self_inductance(h_pwr, via_r);
            double m_v = calc_via_mutual_inductance((h_gnd + h_pwr) / 2.0, via_pitch);
            l_vias = l_vg + l_vp - 2.0 * m_v;
            l_spread = calc_plane_spreading_inductance(d_planes, via_r, via_pitch);
            break;
        }
        case TOPOLOGY_DOUBLE_SIDE_VIA: {
            double via_pitch = cap->width_m + 2.0 * via_r + 0.00015;
            l_pads = 2.0 * calc_partial_rect_inductance(cap->pad_len_m, cap->pad_width_m, pcb->copper_thickness_m);
            l_traces = 0.5 * calc_partial_rect_inductance(0.00015, cap->pad_width_m, pcb->copper_thickness_m);
            double l_vg = calc_via_self_inductance(h_gnd, via_r);
            double l_vp = calc_via_self_inductance(h_pwr, via_r);
            double m_v = calc_via_mutual_inductance((h_gnd + h_pwr) / 2.0, via_pitch);
            l_vias = (l_vg + l_vp - 2.0 * m_v) * 0.52;
            l_spread = calc_plane_spreading_inductance(d_planes, via_r, via_pitch) * 0.5;
            break;
        }
        case TOPOLOGY_VIA_IN_PAD_TOP: {
            double via_pitch = cap->length_m - cap->pad_len_m;
            l_pads = 0.5 * calc_partial_rect_inductance(cap->pad_len_m, cap->pad_width_m, pcb->copper_thickness_m);
            l_traces = 0.0;
            double l_vg = calc_via_self_inductance(h_gnd, via_r);
            double l_vp = calc_via_self_inductance(h_pwr, via_r);
            double m_v = calc_via_mutual_inductance((h_gnd + h_pwr) / 2.0, via_pitch);
            l_vias = l_vg + l_vp - 2.0 * m_v;
            l_spread = calc_plane_spreading_inductance(d_planes, via_r, via_pitch);
            break;
        }
        case TOPOLOGY_BGA_BOTTOM_VIPPO: {
            double via_pitch = 0.00080;
            double h_bot_gnd = pcb->total_board_thickness_m - pcb->h_to_gnd_plane_m;
            double h_bot_pwr = pcb->total_board_thickness_m - pcb->h_to_pwr_plane_m;
            l_pads = 0.3 * calc_partial_rect_inductance(cap->pad_len_m, cap->pad_width_m, pcb->copper_thickness_m);
            l_traces = 0.0;
            double l_vg = calc_via_self_inductance(h_bot_gnd, via_r);
            double l_vp = calc_via_self_inductance(h_bot_pwr, via_r);
            double m_v = calc_via_mutual_inductance((h_bot_gnd + h_bot_pwr) / 2.0, via_pitch);
            l_vias = l_vg + l_vp - 2.0 * m_v;
            l_spread = calc_plane_spreading_inductance(d_planes, via_r, via_pitch);
            break;
        }
        default:
            break;
    }

    out_res->l_esl_nh = cap->esl_henries * 1e9;
    out_res->l_pads_nh = l_pads * 1e9;
    out_res->l_traces_nh = l_traces * 1e9;
    out_res->l_vias_nh = l_vias * 1e9;
    out_res->l_spread_nh = l_spread * 1e9;
    out_res->l_total_mount_nh = (cap->esl_henries + l_pads + l_traces + l_vias + l_spread) * 1e9;

    double l_total_h = out_res->l_total_mount_nh * 1e-9;
    if (l_total_h > 0.0 && cap->capacitance_f > 0.0) {
        out_res->srf_frequency_mhz = (1.0 / (2.0 * M_PI * sqrt(l_total_h * cap->capacitance_f))) / 1e6;
    } else {
        out_res->srf_frequency_mhz = 0.0;
    }

    out_res->z_at_srf_mohms = cap->esr_ohms * 1000.0;
    out_res->r_eff_100mhz_mm = calc_effective_decoupling_radius(100e6, pcb->dielectric_er, 4.0) * 1000.0;
    out_res->r_eff_500mhz_mm = calc_effective_decoupling_radius(500e6, pcb->dielectric_er, 4.0) * 1000.0;
    out_res->r_eff_1ghz_mm = calc_effective_decoupling_radius(1e9, pcb->dielectric_er, 4.0) * 1000.0;
}

int main(void) {
    MlccCapacitorModel cap0402 = {
        .part_name = "0402 100nF 6.3V X7R",
        .capacitance_f = 100e-9,
        .esr_ohms = 0.018,
        .esl_henries = 0.38e-9,
        .length_m = 0.0010,
        .width_m = 0.0005,
        .pad_len_m = 0.0005,
        .pad_width_m = 0.0006
    };

    PcbStackupModel stackup6layer = {
        .dielectric_er = 4.2,
        .h_to_gnd_plane_m = 0.00012,
        .h_to_pwr_plane_m = 0.00060,
        .total_board_thickness_m = 0.00160,
        .via_drill_diameter_m = 0.00025,
        .copper_thickness_m = 0.000035
    };

    printf("==================================================================================================\n");
    printf("  АНАЛІТИЧНИЙ КАЛЬКУЛЯТОР ІНДУКТИВНОСТІ МОНТАЖУ РОЗВ'ЯЗКИ (%s)\n", cap0402.part_name);
    printf("  Параметри стека: 6 шарів, L2 GND=%.2f мм, L3 PWR=%.2f мм, товщина=%.2f мм, Er=%.1f\n",
           stackup6layer.h_to_gnd_plane_m * 1000.0, stackup6layer.h_to_pwr_plane_m * 1000.0,
           stackup6layer.total_board_thickness_m * 1000.0, stackup6layer.dielectric_er);
    printf("==================================================================================================\n\n");

    printf("%-52s | %-6s | %-6s | %-6s | %-6s | %-8s | %-9s\n",
           "Топологія трасування", "L_pads", "L_trc", "L_vias", "L_sprd", "L_TOTAL", "SRF (MHz)");
    printf("-----------------------------------------------------+--------+--------+--------+--------+----------+-----------\n");

    for (int t = 0; t < TOPOLOGY_COUNT; ++t) {
        DetailedAnalysisResult res;
        analyze_decoupling_mounting(&cap0402, &stackup6layer, (DecouplingTopology)t, &res);
        printf("%-52s | %5.2f  | %5.2f  | %5.2f  | %5.2f  | %6.2f нГн| %6.1f МГц\n",
               TOPOLOGY_DESCRIPTIONS[t], res.l_pads_nh, res.l_traces_nh, res.l_vias_nh,
               res.l_spread_nh, res.l_total_mount_nh, res.srf_frequency_mhz);
    }

    DetailedAnalysisResult base_res;
    analyze_decoupling_mounting(&cap0402, &stackup6layer, TOPOLOGY_SIDE_VIA, &base_res);
    printf("\n--------------------------------------------------------------------------------------------------\n");
    printf("  Просторовий радіус ефективної дії конденсатора (r_eff, Er=%.1f, запас фази k=4):\n", stackup6layer.dielectric_er);
    printf("    • f = 100 МГц  -> r_eff = %.1f мм (конденсатор живить локальну зону в радіусі ~5.8 см)\n", base_res.r_eff_100mhz_mm);
    printf("    • f = 500 МГц  -> r_eff = %.1f мм (вимагає розміщення впритул до чіпа)\n", base_res.r_eff_500mhz_mm);
    printf("    • f = 1.0 ГГц  -> r_eff = %.1f мм (діє виключно під BGA або всередині корпусу чіпа)\n", base_res.r_eff_1ghz_mm);
    printf("==================================================================================================\n");

    return 0;
}
