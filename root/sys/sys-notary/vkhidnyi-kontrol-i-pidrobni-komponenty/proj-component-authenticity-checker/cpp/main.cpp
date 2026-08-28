#include <iostream>
#include <vector>
#include <array>
#include <span>
#include <string>
#include <string_view>
#include <memory>
#include <cmath>
#include <algorithm>
#include <numeric>
#include <expected>
#include <iomanip>

namespace SysNotary::CurveTracer {

constexpr size_t MaxSamplesPerCurve = 256;
constexpr float SignatureVoltageRef = 5.0f;
constexpr float SignatureCurrentRef = 0.010f; // 10 мА

enum class PinElectricalType {
    Unknown,
    IoDigital,
    IoAnalog,
    PowerVdd,
    PowerGnd,
    Reset,
    Clock
};

enum class InspectionVerdict {
    Pass,
    SuspectClone,
    SuspectRemark,
    DamagedEsd,
    OpenCircuit,
    ShortCircuit
};

struct Point2D {
    float voltage{0.0f};
    float current{0.0f};
};

struct ExtractedJunctionParams {
    float v_forward_v{0.0f};
    float r_dynamic_ohm{0.0f};
    float i_leak_ua{0.0f};
    float cap_pf{0.0f};
};

class CurveSignature {
public:
    std::vector<Point2D> samples;
    float test_freq_hz{100.0f};
    float source_resistor_ohm{1000.0f};

    CurveSignature() = default;
    CurveSignature(std::vector<Point2D> pts, float freq, float r_src)
        : samples(std::move(pts)), test_freq_hz(freq), source_resistor_ohm(r_src) {}

    [[nodiscard]] CurveSignature filterSavitzkyGolay() const {
        if (samples.size() < 5) return *this;

        std::vector<Point2D> filtered(samples.size());
        filtered[0] = samples[0];
        filtered[1] = samples[1];
        filtered[samples.size() - 2] = samples[samples.size() - 2];
        filtered[samples.size() - 1] = samples[samples.size() - 1];

        // Зважений фільтр 2-го порядку: (-3, 12, 17, 12, -3) / 35
        for (size_t k = 2; k < samples.size() - 2; ++k) {
            filtered[k].voltage = (-3.0f * samples[k - 2].voltage + 12.0f * samples[k - 1].voltage +
                                   17.0f * samples[k].voltage + 12.0f * samples[k + 1].voltage -
                                   3.0f * samples[k + 2].voltage) / 35.0f;

            filtered[k].current = (-3.0f * samples[k - 2].current + 12.0f * samples[k - 1].current +
                                   17.0f * samples[k].current + 12.0f * samples[k + 1].current -
                                   3.0f * samples[k + 2].current) / 35.0f;
        }

        return CurveSignature(std::move(filtered), test_freq_hz, source_resistor_ohm);
    }

    [[nodiscard]] ExtractedJunctionParams extractParameters() const {
        ExtractedJunctionParams p{};
        if (samples.empty()) return p;

        // Пошук V_F при 1.0 мА
        float min_diff = 1e9f;
        constexpr float TargetCurrent = 0.001f;
        for (const auto& pt : samples) {
            float diff = std::abs(pt.current - TargetCurrent);
            if (diff < min_diff && pt.voltage > 0.1f) {
                min_diff = diff;
                p.v_forward_v = pt.voltage;
            }
        }

        // Диференційний опір r_d між 2 мА та 5 мА
        float v1 = 0.0f, v2 = 0.0f;
        float d1 = 1e9f, d2 = 1e9f;
        for (const auto& pt : samples) {
            if (std::abs(pt.current - 0.002f) < d1) { d1 = std::abs(pt.current - 0.002f); v1 = pt.voltage; }
            if (std::abs(pt.current - 0.005f) < d2) { d2 = std::abs(pt.current - 0.005f); v2 = pt.voltage; }
        }
        if (std::abs(v2 - v1) > 1e-4f) {
            p.r_dynamic_ohm = (v2 - v1) / 0.003f;
        } else {
            p.r_dynamic_ohm = 15.0f;
        }

        // Зворотний витік при -4.0 В
        float d_rev = 1e9f;
        float leak_i = 0.0f;
        for (const auto& pt : samples) {
            if (std::abs(pt.voltage - (-4.0f)) < d_rev) {
                d_rev = std::abs(pt.voltage - (-4.0f));
                leak_i = std::abs(pt.current);
            }
        }
        p.i_leak_ua = leak_i * 1e6f;

        // Ємність через площу петлі
        float loop_area = 0.0f;
        for (size_t k = 0; k < samples.size() - 1; ++k) {
            float dv = samples[k + 1].voltage - samples[k].voltage;
            float avg_i = (samples[k].current + samples[k + 1].current) * 0.5f;
            loop_area += avg_i * dv;
        }
        loop_area = std::abs(loop_area);
        float omega = 2.0f * 3.14159265f * (test_freq_hz > 1.0f ? test_freq_hz : 100.0f);
        float v_pk_sq = SignatureVoltageRef * SignatureVoltageRef;
        p.cap_pf = (loop_area / (3.14159265f * omega * v_pk_sq)) * 1e12f;

        return p;
    }
};

struct PinGoldenProfile {
    uint16_t pin_number{0};
    std::string pin_name;
    PinElectricalType pin_type{PinElectricalType::Unknown};
    CurveSignature signature;
    ExtractedJunctionParams params;
};

struct PinInspectionResult {
    uint16_t pin_number{0};
    std::string pin_name;
    float euclidean_discrepancy{0.0f};
    float dtw_distance{0.0f};
    ExtractedJunctionParams uut_params;
    InspectionVerdict verdict{InspectionVerdict::Pass};
    std::string defect_description;
};

struct DeviceInspectionReport {
    std::string device_part_number;
    std::string manufacturer;
    std::string lot_serial_number;
    size_t total_tested_pins{0};
    size_t passed_pins{0};
    size_t failed_pins{0};
    float max_pin_discrepancy{0.0f};
    InspectionVerdict overall_verdict{InspectionVerdict::Pass};
    std::vector<PinInspectionResult> pin_results;
};

class SignatureComparator {
public:
    static float computeEuclideanDiscrepancy(const CurveSignature& gold, const CurveSignature& uut) {
        if (gold.samples.empty() || uut.samples.empty()) return 1.0f;

        size_t n = std::min(gold.samples.size(), uut.samples.size());
        float sum_sq = 0.0f;

        for (size_t k = 0; k < n; ++k) {
            float dv = (uut.samples[k].voltage - gold.samples[k].voltage) / SignatureVoltageRef;
            float di = (uut.samples[k].current - gold.samples[k].current) / SignatureCurrentRef;
            sum_sq += (dv * dv + di * di);
        }

        return std::sqrt(sum_sq / static_cast<float>(n));
    }

    static float computeDtwDistance(const CurveSignature& gold, const CurveSignature& uut) {
        size_t n = std::min<size_t>(gold.samples.size(), 64);
        size_t m = std::min<size_t>(uut.samples.size(), 64);
        if (n == 0 || m == 0) return 1.0f;

        std::vector<std::vector<float>> dtw(n, std::vector<float>(m, 0.0f));

        for (size_t i = 0; i < n; ++i) {
            for (size_t j = 0; j < m; ++j) {
                float dv = (uut.samples[j].voltage - gold.samples[i].voltage) / SignatureVoltageRef;
                float di = (uut.samples[j].current - gold.samples[i].current) / SignatureCurrentRef;
                float cost = std::sqrt(dv * dv + di * di);

                if (i == 0 && j == 0) {
                    dtw[i][j] = cost;
                } else if (i == 0) {
                    dtw[i][j] = cost + dtw[i][j - 1];
                } else if (j == 0) {
                    dtw[i][j] = cost + dtw[i - 1][j];
                } else {
                    float min_prev = std::min({dtw[i - 1][j], dtw[i][j - 1], dtw[i - 1][j - 1]});
                    dtw[i][j] = cost + min_prev;
                }
            }
        }

        return dtw[n - 1][m - 1] / static_cast<float>(n + m);
    }
};

class ComponentAuthenticityChecker {
private:
    std::string device_pn_;
    std::string manufacturer_;
    std::vector<PinGoldenProfile> golden_pins_;

public:
    ComponentAuthenticityChecker(std::string_view pn, std::string_view mfg)
        : device_pn_(pn), manufacturer_(mfg) {}

    void addGoldenPin(PinGoldenProfile pin) {
        golden_pins_.push_back(std::move(pin));
    }

    [[nodiscard]] DeviceInspectionReport inspectLot(
        std::string_view lot_number,
        std::span<const CurveSignature> uut_signatures
    ) const {
        DeviceInspectionReport report;
        report.device_part_number = device_pn_;
        report.manufacturer = manufacturer_;
        report.lot_serial_number = std::string(lot_number);
        report.total_tested_pins = std::min(golden_pins_.size(), uut_signatures.size());
        report.overall_verdict = InspectionVerdict::Pass;

        for (size_t i = 0; i < report.total_tested_pins; ++i) {
            const auto& gold = golden_pins_[i];
            CurveSignature filtered_uut = uut_signatures[i].filterSavitzkyGolay();

            PinInspectionResult res;
            res.pin_number = gold.pin_number;
            res.pin_name = gold.pin_name;
            res.uut_params = filtered_uut.extractParameters();
            res.euclidean_discrepancy = SignatureComparator::computeEuclideanDiscrepancy(gold.signature, filtered_uut);
            res.dtw_distance = SignatureComparator::computeDtwDistance(gold.signature, filtered_uut);

            // Критерії класифікації браку
            if (res.uut_params.v_forward_v < 0.1f && res.uut_params.r_dynamic_ohm < 2.0f) {
                res.verdict = InspectionVerdict::ShortCircuit;
                res.defect_description = "Коротке замикання на GND";
            } else if (res.uut_params.v_forward_v > 4.5f) {
                res.verdict = InspectionVerdict::OpenCircuit;
                res.defect_description = "Обрив виводу (без ESD)";
            } else if (res.uut_params.i_leak_ua > 50.0f) {
                res.verdict = InspectionVerdict::SuspectRemark;
                res.defect_description = "Аномальний витік (I_leak > 50 uA)";
            } else if (res.euclidean_discrepancy > 0.08f || res.dtw_distance > 0.06f) {
                res.verdict = InspectionVerdict::SuspectClone;
                res.defect_description = "Кристал-клон (відхилення > 8%)";
            } else {
                res.verdict = InspectionVerdict::Pass;
                res.defect_description = "Автентичний";
            }

            if (res.euclidean_discrepancy > report.max_pin_discrepancy) {
                report.max_pin_discrepancy = res.euclidean_discrepancy;
            }

            if (res.verdict == InspectionVerdict::Pass) {
                report.passed_pins++;
            } else {
                report.failed_pins++;
                if (report.overall_verdict == InspectionVerdict::Pass) {
                    report.overall_verdict = res.verdict;
                }
            }

            report.pin_results.push_back(std::move(res));
        }

        return report;
    }

    static void printReport(const DeviceInspectionReport& rep) {
        std::cout << "====================================================================\n";
        std::cout << " ЗВІТ ВХІДНОГО СИГНАТУРНОГО КОНТРОЛЮ АВТЕНТИЧНОСТІ КОМПОНЕНТА      \n";
        std::cout << "====================================================================\n";
        std::cout << " Компонент:       " << rep.device_part_number << " (" << rep.manufacturer << ")\n";
        std::cout << " Партія / Лот:    " << rep.lot_serial_number << "\n";
        std::cout << " Перевірено пінів: " << rep.total_tested_pins 
                  << " (Успішно: " << rep.passed_pins << ", Дефектних: " << rep.failed_pins << ")\n";
        std::cout << " Макс. відхилення: " << std::fixed << std::setprecision(2) 
                  << (rep.max_pin_discrepancy * 100.0f) << "%\n";
        std::cout << " ПІДСУМКОВИЙ ВЕРДИКТ: " 
                  << (rep.overall_verdict == InspectionVerdict::Pass 
                      ? "[✓ ПРИДАТНО / ОРИГІНАЛ]" 
                      : "[✗ КОНТРАФАКТ / КАРАНТИН]") << "\n";
        std::cout << "--------------------------------------------------------------------\n";
        std::cout << " Пін | Назва   | V_F (В) | r_d (Ом) | I_leak (uA) | C_j (пФ) | Статус\n";
        std::cout << "-----+---------+---------+----------+-------------+----------+------\n";

        for (const auto& r : rep.pin_results) {
            std::cout << " " << std::setw(3) << r.pin_number << " | "
                      << std::setw(7) << std::left << r.pin_name << " |  "
                      << std::setw(5) << std::right << std::fixed << std::setprecision(3) << r.uut_params.v_forward_v << "  |  "
                      << std::setw(6) << std::fixed << std::setprecision(1) << r.uut_params.r_dynamic_ohm << "  |   "
                      << std::setw(7) << std::fixed << std::setprecision(2) << r.uut_params.i_leak_ua << "   |  "
                      << std::setw(5) << std::fixed << std::setprecision(1) << r.uut_params.cap_pf << "   | "
                      << r.defect_description << "\n";
        }
        std::cout << "====================================================================\n";
    }
};

class DiscretesSignatureGenerator {
public:
    static CurveSignature generateBjtBeSignature(float v_be_on, float r_bulk, float i_sat, bool is_damaged_leak) {
        std::vector<Point2D> pts(128);
        constexpr float Rsrc = 1000.0f;

        for (size_t k = 0; k < pts.size(); ++k) {
            float phase = (2.0f * 3.14159265f * static_cast<float>(k)) / static_cast<float>(pts.size());
            float v_gen = SignatureVoltageRef * std::sin(phase);
            float v_dut = 0.0f;
            float i_dut = 0.0f;

            if (v_gen > v_be_on) {
                float v_diff = v_gen - v_be_on;
                v_dut = v_be_on + v_diff * (r_bulk / (r_bulk + Rsrc));
                i_dut = (v_gen - v_dut) / Rsrc;
            } else if (v_gen < -6.0f) {
                v_dut = -6.0f;
                i_dut = (v_gen - v_dut) / Rsrc;
            } else {
                float leak = is_damaged_leak ? (v_gen / 80000.0f) : (v_gen < 0.0f ? -i_sat : 0.0f);
                i_dut = leak;
                v_dut = v_gen - i_dut * Rsrc;
            }
            pts[k] = Point2D{ .voltage = v_dut, .current = i_dut };
        }
        return CurveSignature(std::move(pts), 100.0f, Rsrc);
    }

    static CurveSignature generateMosfetGsSignature(float cap_nF, float r_leak_ohm) {
        std::vector<Point2D> pts(128);
        constexpr float Freq = 1000.0f;
        constexpr float Rsrc = 10000.0f;
        float omega = 2.0f * 3.14159265f * Freq;
        float cap_f = cap_nF * 1e-9f;

        for (size_t k = 0; k < pts.size(); ++k) {
            float phase = (2.0f * 3.14159265f * static_cast<float>(k)) / static_cast<float>(pts.size());
            float v_gen = SignatureVoltageRef * std::sin(phase);

            float i_cap = v_gen * omega * cap_f * std::cos(phase);
            float i_res = v_gen / r_leak_ohm;
            float i_total = i_cap + i_res;
            float v_dut = v_gen - i_total * Rsrc;

            pts[k] = Point2D{ .voltage = v_dut, .current = i_total };
        }
        return CurveSignature(std::move(pts), Freq, Rsrc);
    }

    static CurveSignature generateSchottkySignature(float v_f_knee, float r_series, float i_rev_leak) {
        std::vector<Point2D> pts(128);
        constexpr float Rsrc = 1000.0f;

        for (size_t k = 0; k < pts.size(); ++k) {
            float phase = (2.0f * 3.14159265f * static_cast<float>(k)) / static_cast<float>(pts.size());
            float v_gen = SignatureVoltageRef * std::sin(phase);
            float v_dut = 0.0f;
            float i_dut = 0.0f;

            if (v_gen > v_f_knee) {
                float v_diff = v_gen - v_f_knee;
                v_dut = v_f_knee + v_diff * (r_series / (r_series + Rsrc));
                i_dut = (v_gen - v_dut) / Rsrc;
            } else {
                i_dut = (v_gen < 0.0f) ? (-i_rev_leak * std::abs(v_gen) / SignatureVoltageRef) : 0.0f;
                v_dut = v_gen - i_dut * Rsrc;
            }
            pts[k] = Point2D{ .voltage = v_dut, .current = i_dut };
        }
        return CurveSignature(std::move(pts), 100.0f, Rsrc);
    }
};

inline void runExtendedDiscreteInspectionDemo() {
    std::cout << "\n=== ТЕСТУВАННЯ ДИСКРЕТНИХ КОМПОНЕНТІВ (BJT, MOSFET, SCHOTTKY) ===\n";

    // 1. BJT 2N3904
    auto bjt_gold = DiscretesSignatureGenerator::generateBjtBeSignature(0.68f, 12.0f, 1e-8f, false);
    auto bjt_damaged = DiscretesSignatureGenerator::generateBjtBeSignature(0.68f, 12.0f, 1e-8f, true);
    PinGoldenProfile prof_bjt{ .pin_number = 1, .pin_name = "B-E", .signature = bjt_gold };
    ComponentAuthenticityChecker checker_bjt("2N3904", "ON Semi");
    checker_bjt.addGoldenPin(prof_bjt);
    std::array<CurveSignature, 1> uut_bjt{ bjt_damaged };
    auto rep_bjt = checker_bjt.inspectLot("LOT-BJT-991", uut_bjt);
    std::cout << " [BJT 2N3904] Вердикт: " 
              << (rep_bjt.overall_verdict == InspectionVerdict::Pass ? "PASS" : "FAIL / LEAKAGE")
              << " (Витік: " << rep_bjt.pin_results[0].uut_params.i_leak_ua << " uA)\n";

    // 2. MOSFET IRFP460
    auto mos_gold = DiscretesSignatureGenerator::generateMosfetGsSignature(4.2f, 1e8f);
    auto mos_recycled = DiscretesSignatureGenerator::generateMosfetGsSignature(4.2f, 8e4f);
    PinGoldenProfile prof_mos{ .pin_number = 2, .pin_name = "G-S", .signature = mos_gold };
    ComponentAuthenticityChecker checker_mos("IRFP460", "Vishay");
    checker_mos.addGoldenPin(prof_mos);
    std::array<CurveSignature, 1> uut_mos{ mos_recycled };
    auto rep_mos = checker_mos.inspectLot("LOT-MOS-402", uut_mos);
    std::cout << " [MOSFET IRFP460] Вердикт: " 
              << (rep_mos.overall_verdict == InspectionVerdict::Pass ? "PASS" : "FAIL / GATE BREAKDOWN")
              << " (" << rep_mos.pin_results[0].defect_description << ")\n";

    // 3. Schottky 1N5819
    auto sch_gold = DiscretesSignatureGenerator::generateSchottkySignature(0.28f, 8.0f, 2e-5f);
    auto sch_clone = DiscretesSignatureGenerator::generateSchottkySignature(0.55f, 22.0f, 1e-6f);
    PinGoldenProfile prof_sch{ .pin_number = 3, .pin_name = "Anode", .signature = sch_gold };
    ComponentAuthenticityChecker checker_sch("1N5819", "Diodes Inc");
    checker_sch.addGoldenPin(prof_sch);
    std::array<CurveSignature, 1> uut_sch{ sch_clone };
    auto rep_sch = checker_sch.inspectLot("LOT-SCH-118", uut_sch);
    std::cout << " [Schottky 1N5819] Вердикт: " 
              << (rep_sch.overall_verdict == InspectionVerdict::Pass ? "PASS" : "FAIL / WRONG JUNCTION")
              << " (V_F = " << rep_sch.pin_results[0].uut_params.v_forward_v << " В)\n";
}

} // namespace SysNotary::CurveTracer
