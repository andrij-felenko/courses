// C++20 Заголовок модульного інтерфейсу NozzleEvaluator.hpp
#pragma once
#include <expected>
#include <span>
#include <vector>

namespace NozzleLib {

class NozzleEvaluator {
public:
    explicit NozzleEvaluator(GasProperties gas_props) noexcept : gas_(gas_props) {}

    [[nodiscard]] std::expected<double, NozzleError> 
    getMachFromAreaRatio(double area_ratio, bool supersonic) const noexcept;

    [[nodiscard]] std::expected<double, NozzleError> 
    getChokedMassFlow(double A_throat) const noexcept;

    [[nodiscard]] std::expected<RegimeAnalysisResult, NozzleError> 
    determineRegime(const NozzleGeometry& geom) const noexcept;

    [[nodiscard]] std::expected<std::vector<FlowPointState>, NozzleError> 
    evaluateMesh(const NozzleGeometry& geom, std::span<const double> x_mesh, std::span<const double> area_mesh) const;

private:
    GasProperties gas_;
};

} // namespace NozzleLib
