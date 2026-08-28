#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <string_view>
#include <optional>
#include <format>
#include <span>

namespace dfm_importer {

/* Опис технологічного профілю виробника друкованих плат */
struct FactoryProfile {
    std::string_view factory_name;
    std::string_view tier_name;
    double copper_oz{1.0};           // 0.5, 1.0, 2.0 oz
    double min_track_width{0.150};    // мм
    double min_track_space{0.150};    // мм
    double min_drill_dia{0.300};      // мм
    double min_annular_ring{0.150};   // мм
    double mask_expansion{0.050};     // мм
    double min_mask_dam{0.100};       // мм
    double min_edge_milling{0.300};   // мм
    double min_edge_vcut{0.500};      // мм
    double min_hole_to_hole{0.500};   // мм
    double min_silk_width{0.150};     // мм
    double min_silk_clearance{0.150}; // мм
    double fiducial_edge_clear{5.000};// мм
    double max_aspect_ratio{8.0};
};

/* Набір еталонних профілів фабрик */
inline constexpr FactoryProfile PRESET_PROFILES[] = {
    {
        .factory_name = "JLCPCB",
        .tier_name = "Standard 1-2 Layer (1 oz)",
        .copper_oz = 1.0,
        .min_track_width = 0.150,
        .min_track_space = 0.150,
        .min_drill_dia = 0.300,
        .min_annular_ring = 0.150,
        .mask_expansion = 0.050,
        .min_mask_dam = 0.100,
        .min_edge_milling = 0.300,
        .min_edge_vcut = 0.500,
        .min_hole_to_hole = 0.500,
        .min_silk_width = 0.150,
        .min_silk_clearance = 0.150,
        .fiducial_edge_clear = 5.000,
        .max_aspect_ratio = 8.0
    },
    {
        .factory_name = "JLCPCB",
        .tier_name = "Advanced 4-6 Layer (0.5 oz)",
        .copper_oz = 0.5,
        .min_track_width = 0.090,
        .min_track_space = 0.090,
        .min_drill_dia = 0.150,
        .min_annular_ring = 0.100,
        .mask_expansion = 0.030,
        .min_mask_dam = 0.080,
        .min_edge_milling = 0.200,
        .min_edge_vcut = 0.400,
        .min_hole_to_hole = 0.400,
        .min_silk_width = 0.120,
        .min_silk_clearance = 0.120,
        .fiducial_edge_clear = 4.000,
        .max_aspect_ratio = 10.0
    },
    {
        .factory_name = "PCBWay",
        .tier_name = "Standard Production (1 oz)",
        .copper_oz = 1.0,
        .min_track_width = 0.150,
        .min_track_space = 0.150,
        .min_drill_dia = 0.300,
        .min_annular_ring = 0.150,
        .mask_expansion = 0.050,
        .min_mask_dam = 0.100,
        .min_edge_milling = 0.250,
        .min_edge_vcut = 0.500,
        .min_hole_to_hole = 0.500,
        .min_silk_width = 0.150,
        .min_silk_clearance = 0.150,
        .fiducial_edge_clear = 5.000,
        .max_aspect_ratio = 8.0
    },
    {
        .factory_name = "Eurocircuits",
        .tier_name = "Standard Pool (1 oz)",
        .copper_oz = 1.0,
        .min_track_width = 0.150,
        .min_track_space = 0.150,
        .min_drill_dia = 0.250,
        .min_annular_ring = 0.125,
        .mask_expansion = 0.040,
        .min_mask_dam = 0.100,
        .min_edge_milling = 0.250,
        .min_edge_vcut = 0.450,
        .min_hole_to_hole = 0.450,
        .min_silk_width = 0.150,
        .min_silk_clearance = 0.125,
        .fiducial_edge_clear = 5.000,
        .max_aspect_ratio = 8.5
    }
};

class KiCadRulesGenerator {
public:
    explicit constexpr KiCadRulesGenerator(const FactoryProfile& profile) noexcept
        : profile_(profile) {}

    [[nodiscard]] std::string generate_dru_content() const {
        std::string out;
        out.reserve(4096);

        out += ";; ===================================================================\n";
        out += std::format(";; KiCad 8/9 Custom DRC Rules\n");
        out += std::format(";; Factory Profile: {} - {}\n", profile_.factory_name, profile_.tier_name);
        out += std::format(";; Copper Weight: {:.1f} oz | Max Aspect Ratio: {:.1f}:1\n",
                           profile_.copper_oz, profile_.max_aspect_ratio);
        out += ";; Generated automatically by C++20 DFM Rules Importer\n";
        out += ";; ===================================================================\n\n";
        out += "(version 1)\n\n";

        // 1. Мінімальна ширина провідників
        out += "(rule \"Factory_Min_Track_Width\"\n";
        out += "  (priority 100)\n";
        out += std::format("  (constraint track_width (min {:.3f}mm))\n", profile_.min_track_width);
        out += "  (condition \"A.Type == 'Track'\"))\n\n";

        // 2. Мінімальний ізоляційний зазор
        out += "(rule \"Factory_Min_Clearance\"\n";
        out += "  (priority 100)\n";
        out += std::format("  (constraint clearance (min {:.3f}mm))\n", profile_.min_track_space);
        out += "  (condition \"A.NetClass != B.NetClass\"))\n\n";

        // 3. Мінімальний діаметр свердла
        out += "(rule \"Factory_Min_Drill\"\n";
        out += "  (priority 110)\n";
        out += std::format("  (constraint hole_size (min {:.3f}mm))\n", profile_.min_drill_dia);
        out += "  (condition \"A.Type == 'Via' || A.Type == 'Pad'\"))\n\n";

        // 4. Мінімальний поясок металізації
        out += "(rule \"Factory_Min_Annular_Ring\"\n";
        out += "  (priority 110)\n";
        out += std::format("  (constraint annular_width (min {:.3f}mm))\n", profile_.min_annular_ring);
        out += "  (condition \"A.Type == 'Via'\"))\n\n";

        // 5. Відступ міді до контуру плати при фрезеруванні
        out += "(rule \"Factory_Edge_Milling_Clearance\"\n";
        out += "  (priority 120)\n";
        out += std::format("  (constraint edge_clearance (min {:.3f}mm))\n", profile_.min_edge_milling);
        out += "  (condition \"A.Type == 'Track' || A.Type == 'Zone' || A.Type == 'Pad'\"))\n\n";

        // 6. Відступ полігонів живлення до осі V-cut
        out += "(rule \"Factory_VCut_Scoring_Clearance\"\n";
        out += "  (priority 130)\n";
        out += std::format("  (constraint edge_clearance (min {:.3f}mm))\n", profile_.min_edge_vcut);
        out += "  (condition \"A.Type == 'Zone' && A.NetClass == 'Power'\"))\n\n";

        // 7. Зазор між отворами (Hole-to-Hole)
        out += "(rule \"Factory_Hole_To_Hole\"\n";
        out += "  (priority 105)\n";
        out += std::format("  (constraint hole_clearance (min {:.3f}mm))\n", profile_.min_hole_to_hole);
        out += "  (condition \"A.Type == 'Via' || A.Type == 'Pad'\"))\n\n";

        // 8. Відступ шовкографії від паяльних майданчиків
        out += "(rule \"Factory_Silk_To_Mask_Clearance\"\n";
        out += "  (priority 90)\n";
        out += std::format("  (constraint silk_clearance (min {:.3f}mm))\n", profile_.min_silk_clearance);
        out += "  (condition \"A.Type == 'Graphic' && A.Layer == 'F.SilkS'\"))\n\n";

        // 9. Відступ оптичних реперів від краю плати
        out += "(rule \"Factory_Fiducial_Edge_Clearance\"\n";
        out += "  (priority 140)\n";
        out += std::format("  (constraint edge_clearance (min {:.3f}mm))\n", profile_.fiducial_edge_clear);
        out += "  (condition \"A.Type == 'Footprint' && A.Reference == 'FID*'\"))\n\n";

        return out;
    }

    bool write_to_file(std::string_view filepath) const {
        std::ofstream ofs(std::string(filepath));
        if (!ofs.is_open()) {
            return false;
        }
        ofs << generate_dru_content();
        return ofs.good();
    }

private:
    FactoryProfile profile_;
};

} // namespace dfm_importer

int main(int argc, char* argv[]) {
    using namespace dfm_importer;

    std::cout << "=== DFM Rules Importer CLI (C++20) ===\n\n";

    constexpr std::span<const FactoryProfile> presets(PRESET_PROFILES);

    if (argc < 2) {
        std::cout << std::format("Використання: {} <індекс_профілю> [вихідний_файл.kicad_dru]\n", argv[0]);
        std::cout << "Доступні профілі фабрик:\n";
        for (size_t i = 0; i < presets.size(); ++i) {
            const auto& p = presets[i];
            std::cout << std::format("  [{}] {} — {} (Мідь: {:.1f} oz, Min W/S: {:.2f}/{:.2f} мм)\n",
                                     i, p.factory_name, p.tier_name, p.copper_oz,
                                     p.min_track_width, p.min_track_space);
        }
        return 1;
    }

    const size_t idx = static_cast<size_t>(std::stoi(argv[1]));
    if (idx >= presets.size()) {
        std::cerr << std::format("Помилка: некоректний індекс профілю {} (доступно 0..{})\n",
                                 idx, presets.size() - 1);
        return 1;
    }

    const std::string_view outfile = (argc >= 3) ? argv[2] : "factory_rules.kicad_dru";
    const auto& profile = presets[idx];

    std::cout << std::format("Генерація правил для '{} ({})' у файл '{}'...\n",
                             profile.factory_name, profile.tier_name, outfile);

    const KiCadRulesGenerator generator(profile);
    if (generator.write_to_file(outfile)) {
        std::cout << "Файл правил успішно згенеровано!\n";
        return 0;
    } else {
        std::cerr << "Помилка запису файлу!\n";
        return 1;
    }
}
