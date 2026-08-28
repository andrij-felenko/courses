static std::uint32_t rng_state = 2463534242u;
static std::uint32_t rnd() {
    std::uint32_t x = rng_state;
    x ^= x << 13; x ^= x >> 17; x ^= x << 5;
    return rng_state = x;
}

static void step() {
    ensure_free();
    std::int32_t ino = 0;
    if (rnd() % 100 < 90) {
        ino = static_cast<std::int32_t>(rnd() % static_cast<std::uint32_t>(state.nhot));
    } else {
        ino = state.nhot + static_cast<std::int32_t>(rnd() % static_cast<std::uint32_t>(state.nfiles - state.nhot));
    }
    std::int32_t off = static_cast<std::int32_t>(rnd() % FILE_BLOCKS);
    file_write(ino, off);
}

static void run_simulation(Policy pol, bool sep, double rho) {
    state.policy = pol;
    state.sep_head = sep;
    state.nfiles = static_cast<std::int32_t>(rho * NSEGS);
    state.nhot = std::max(1, state.nfiles / 10);
    state.free_segs = static_cast<std::int32_t>(NSEGS);
    state.head = {-1, -1};
    state.now_ = 0;
    rng_state = 2463534242u;

    for (auto& s : state.seg) {
        s.is_free = true;
        s.written = 0;
        s.live = 0;
        s.sealed = 0;
    }
    state.inode.assign(state.nfiles, std::array<std::int32_t, FILE_BLOCKS>{});
    for (auto& fn : state.inode) fn.fill(-1);

    for (std::size_t off = 0; off < FILE_BLOCKS; ++off) {
        for (std::int32_t ino = 0; ino < state.nfiles; ++ino) {
            ensure_free();
            file_write(ino, static_cast<std::int32_t>(off));
        }
    }

    for (std::int64_t k = 0; k < WARMUP; ++k) step();

    state.user_writes = state.clean_writes = state.clean_reads = 0;
    state.victims = state.stalls = 0;
    state.u_sum = 0.0;

    for (std::size_t k = 0; k < MEASURE; ++k) step();
}

int main() {
    constexpr double rhos[] = { 0.50, 0.70, 0.80, 0.90, 0.95 };
    struct Variant { Policy pol; bool sep; const char* name; };
    constexpr Variant vars[] = {
        { Policy::Greedy,      true,  "greedy" },
        { Policy::CostBenefit, true,  "cost-benefit" },
        { Policy::CostBenefit, false, "cost-ben 1head" }
    };

    std::cout << "  rho  policy           u_vict  WA_write  WA_total  2/(1-u)  stall\n";
    for (double rho : rhos) {
        for (const auto& v : vars) {
            run_simulation(v.pol, v.sep, rho);
            if (state.user_writes == 0) {
                std::cout << " " << std::fixed << std::setprecision(2) << rho 
                          << "  " << std::left << std::setw(15) << v.name 
                          << "   том став: прибирачеві нема куди писати\n";
                continue;
            }
            double ub = state.victims ? state.u_sum / static_cast<double>(state.victims) : 0.0;
            double wa_w = static_cast<double>(state.user_writes + state.clean_writes) / static_cast<double>(state.user_writes);
            double wa_t = static_cast<double>(state.user_writes + state.clean_writes + state.clean_reads) / static_cast<double>(state.user_writes);
            
            std::cout << " " << std::fixed << std::setprecision(2) << rho 
                      << "  " << std::left << std::setw(15) << v.name 
                      << "  " << std::setw(6) << std::setprecision(3) << ub 
                      << "  " << std::setw(8) << std::setprecision(2) << wa_w 
                      << "  " << std::setw(8) << std::setprecision(2) << wa_t 
                      << "  " << std::setw(7) << std::setprecision(2) << (2.0 / (1.0 - ub)) 
                      << "  " << std::setw(5) << state.stalls << '\n';
        }
    }
    return 0;
}
