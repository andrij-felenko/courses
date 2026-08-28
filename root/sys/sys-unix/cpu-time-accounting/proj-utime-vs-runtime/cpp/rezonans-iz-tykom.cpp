// Ті самі умови, різна довжина скибки. Одне зі значень збігається з періодом
// тику ядра — і саме на ньому поділ перестає бути схожим на сусідів.
static int mode_phase(double seconds, double kfrac)
{
    constexpr std::array<double, 6> slices_ms = { 0.2, 1.0, 2.0, 4.0, 8.0, 10.0 };

    std::cout << "скибка    частка sys    точна сума\n";
    for (double slice : slices_ms) {
        snap a{}, b{};
        take(a);
        burn_mix(seconds, kfrac, slice / 1000.0);
        take(b);
        snap d = diff(a, b);

        double tot = d.ru_self_u + d.ru_self_s;
        double share = tot > 0.0 ? 100.0 * d.ru_self_s / tot : 0.0;
        std::cout << std::fixed << std::setprecision(1) << std::setw(5) << slice << " мс     "
                  << std::setprecision(2) << std::setw(6) << share << " %     "
                  << std::setprecision(6) << std::setw(10) << d.clk_proc << "\n";
    }
    return 0;
}
