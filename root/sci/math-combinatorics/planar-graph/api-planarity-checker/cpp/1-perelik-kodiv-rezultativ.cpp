#include <system_error>
#include <string_view>

enum class PlanarStatus {
    Ok = 0,
    NonPlanar,
    NullPointer,
    InvalidVertex,
    EdgeCapacityExceeded,
    NotEmbedded,
    NoCertificate
};

[[nodiscard]] constexpr std::string_view to_string(PlanarStatus status) noexcept {
    switch (status) {
        case PlanarStatus::Ok: return "OK (Planar)";
        case PlanarStatus::NonPlanar: return "Non-Planar Graph";
        case PlanarStatus::NullPointer: return "Null Pointer Error";
        case PlanarStatus::InvalidVertex: return "Invalid Vertex Index";
        case PlanarStatus::EdgeCapacityExceeded: return "Edge Capacity Exceeded";
        case PlanarStatus::NotEmbedded: return "Graph Not Embedded";
        case PlanarStatus::NoCertificate: return "No Kuratowski Certificate Available";
    }
    return "Unknown Error";
}
