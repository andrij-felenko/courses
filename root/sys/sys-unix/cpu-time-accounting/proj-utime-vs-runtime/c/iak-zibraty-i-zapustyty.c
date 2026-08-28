int main(int argc, char **argv)
{
    const char *mode = argc > 1 ? argv[1] : "mix";
    double a2 = argc > 2 ? atof(argv[2]) : 0.0;
    double a3 = argc > 3 ? atof(argv[3]) : 0.0;
    double a4 = argc > 4 ? atof(argv[4]) : 0.0;

    setvbuf(stdout, NULL, _IOLBF, 0);

    if (!strcmp(mode, "mix"))
        return mode_mix(a2 > 0 ? a2 : 3.0, argc > 3 ? a3 : 0.35,
                        (a4 > 0 ? a4 : 1.0) / 1000.0);
    if (!strcmp(mode, "spread"))
        return mode_spread(argc > 2 ? (int)a2 : 8, a3 > 0 ? a3 : 1.0,
                           argc > 4 ? a4 : 0.35, 0.001);
    if (!strcmp(mode, "short"))
        return mode_short(a2 > 0 ? a2 : 3.0);
    if (!strcmp(mode, "phase"))
        return mode_phase(a2 > 0 ? a2 : 1.0, argc > 3 ? a3 : 0.35);
    if (!strcmp(mode, "threads"))
        return mode_threads(argc > 2 ? (int)a2 : 4, a3 > 0 ? a3 : 1.0,
                            argc > 4 ? a4 : 0.35);

    fprintf(stderr,
        "usage: cpulab mix     [с] [частка] [скибка_мс]\n"
        "              spread  [прогонів] [с] [частка]\n"
        "              short   [мс]\n"
        "              phase   [с] [частка]\n"
        "              threads [потоків] [с] [частка]\n");
    return 2;
}
