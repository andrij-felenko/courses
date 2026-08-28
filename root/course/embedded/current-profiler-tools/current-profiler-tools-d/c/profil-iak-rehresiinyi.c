// Псевдо-API приладу (реальні виклики залежать від моделі):
//   profiler_set_voltage(V)        — виставити живлення DUT
//   profiler_capture(sec)          — захопити вікно довжиною sec секунд
//   profiler_charge_uas()          — інтеграл струму за вікно, у мкА·с

// Міряємо заряд ОДНОГО активного сплеску (boot → вимір → TX → знову сон):
// він короткий, тож тест швидкий. Поріг — із розрахунку робочого циклу.
#define WINDOW_S          3.0       // вікно довше за активну фазу (~1.7 с)
#define Q_BUDGET_UAS   203000.0     // бюджет заряду активної фази, мкА·с (=203 мА·с)
#define Q_TOLERANCE       1.10      // допуск +10 % на розкид між вимірами

int energy_regression_test(void) {
    profiler_set_voltage(3.3);
    profiler_capture(WINDOW_S);                 // охопити весь активний сплеск

    double q = profiler_charge_uas();           // заряд за вікно, мкА·с
    double i_avg_ua = q / WINDOW_S;             // мкА·с / с = мкА (середнє за вікно)

    printf("burst charge = %.0f uA*s,  I_avg(window) = %.0f uA\n", q, i_avg_ua);

    if (q > Q_BUDGET_UAS * Q_TOLERANCE) {       // порівнюємо саме заряд, не середнє
        printf("FAIL: charge %.0f > budget %.0f (+%.0f%%)\n",
               q, Q_BUDGET_UAS, (Q_TOLERANCE - 1.0) * 100);
        return 1;                               // ненульовий код → CI валить білд
    }
    printf("PASS: within energy budget\n");
    return 0;
}
