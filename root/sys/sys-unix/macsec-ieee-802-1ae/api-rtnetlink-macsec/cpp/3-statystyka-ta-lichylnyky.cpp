// Об'єктно-орієнтовані структури статистики в C++20
#include <cstdint>

struct MacsecDevStats {
    std::uint64_t out_pkts_untagged{0};
    std::uint64_t in_pkts_untagged{0};
    std::uint64_t in_pkts_bad_tag{0};
    std::uint64_t in_pkts_unknown_sci{0};
    std::uint64_t in_pkts_no_sci{0};
    std::uint64_t in_pkts_overrun{0};
};

struct MacsecRxScStats {
    std::uint64_t in_pkts_ok{0};
    std::uint64_t in_pkts_unchecked{0};
    std::uint64_t in_pkts_delayed{0};
    std::uint64_t in_pkts_late{0};
    std::uint64_t in_pkts_invalid{0};
    std::uint64_t in_pkts_not_valid{0};
};
