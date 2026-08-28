struct Walk {
    uint64_t n{0};                 // екстентів у карті
    uint64_t mapped{0};            // сума fe_length
    uint64_t longest{0};
    uint64_t holes{0}, hole_bytes{0};
    uint64_t unwritten{0}, delalloc{0}, shared{0}, encoded{0};
    uint64_t pairs{0}, glued{0};   // сусідніх пар / з них — упритул

    uint64_t seen_end{0};          // найбільший побачений логічний кінець
    bool have_prev{false};
    fiemap_extent prev{};

    void take(const fiemap_extent &e, bool verbose, uint64_t idx) {
        if (e.fe_logical + e.fe_length <= seen_end)
            return;                               // цей запис ми вже бачили

        if (e.fe_logical > seen_end) {            // між даними — діра
            holes++;
            hole_bytes += e.fe_logical - seen_end;
        }

        n++;
        mapped += e.fe_length;
        if (e.fe_length > longest)
            longest = e.fe_length;
        if (e.fe_flags & FIEMAP_EXTENT_UNWRITTEN) unwritten += e.fe_length;
        if (e.fe_flags & FIEMAP_EXTENT_DELALLOC)  delalloc  += e.fe_length;
        if (e.fe_flags & FIEMAP_EXTENT_SHARED)    shared    += e.fe_length;
        if (e.fe_flags & FIEMAP_EXTENT_ENCODED)   encoded   += e.fe_length;

        constexpr uint32_t VAGUE = FIEMAP_EXTENT_UNKNOWN | FIEMAP_EXTENT_DELALLOC |
                                   FIEMAP_EXTENT_NOT_ALIGNED | FIEMAP_EXTENT_ENCODED;

        if (have_prev && !((prev.fe_flags | e.fe_flags) & VAGUE)) {
            pairs++;
            if (prev.fe_physical + prev.fe_length == e.fe_physical &&
                prev.fe_logical  + prev.fe_length == e.fe_logical)
                glued++;                          // сусіди стик у стик
        }

        if (verbose) {
            std::string fs = flags_str(e.fe_flags);
            printf("%8" PRIu64 " %14" PRIu64 " %12" PRIu64 " %16" PRIu64 "  %s\n",
                   idx, static_cast<uint64_t>(e.fe_logical),
                   static_cast<uint64_t>(e.fe_length),
                   static_cast<uint64_t>(e.fe_physical), fs.c_str());
        }

        seen_end = e.fe_logical + e.fe_length;
        prev = e;
        have_prev = true;
    }
};
