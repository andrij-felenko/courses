static int mode_short(double ms)
{
    snap a{}, b{};
    take(a);
    burn_user(ms / 1000.0);
    take(b);
    snap d = diff(a, b);
    std::cout << std::fixed << std::setprecision(0)
              << "спалено ~" << ms << " мс самого лише власного коду\n";
    report(d);
    return 0;
}
