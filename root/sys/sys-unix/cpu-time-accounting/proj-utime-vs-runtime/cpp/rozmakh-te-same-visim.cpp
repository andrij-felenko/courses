static int mode_spread(int runs, double seconds, double kfrac, double slice)
{
    runs = std::clamp(runs, 2, 64);

    double rt_min = 1e30, rt_max = -1e30, sh_min = 1e30, sh_max = -1e30;

    std::cout << "прогін   точна сума        user           sys      частка sys\n";
    for (int i = 1; i <= runs; i++) {
        snap a{}, b{};
        take(a);
        burn_mix(seconds, kfrac, slice);
        take(b);
        snap d = diff(a, b);

        double tot = d.ru_self_u + d.ru_self_s;
        double share = tot > 0.0 ? d.ru_self_s / tot : 0.0;
        std::cout << std::fixed << std::setprecision(6)
                  << "  " << std::setw(2) << i
                  << "    " << std::setw(10) << d.clk_proc
                  << "   " << std::setw(10) << d.ru_self_u
                  << "   " << std::setw(10) << d.ru_self_s
                  << "     " << std::setprecision(2) << std::setw(6) << (100.0 * share) << " %\n";

        rt_min = std::min(rt_min, d.clk_proc);
        rt_max = std::max(rt_max, d.clk_proc);
        sh_min = std::min(sh_min, share);
        sh_max = std::max(sh_max, share);
    }
    std::cout << "\nточна сума: розмах " << std::setprecision(6) << (rt_max - rt_min)
              << " с  (" << std::setprecision(3) << (100.0 * (rt_max - rt_min) / rt_min)
              << " % від " << std::setprecision(3) << rt_min << " с)\n"
              << "частка sys: розмах " << std::setprecision(2) << (100.0 * (sh_max - sh_min))
              << " відсоткового пункту (від " << (100.0 * sh_min)
              << " до " << (100.0 * sh_max) << ")\n";
    return 0;
}
