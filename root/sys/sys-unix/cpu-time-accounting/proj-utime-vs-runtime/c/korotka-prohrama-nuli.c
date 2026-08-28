static int mode_short(double ms)
{
    snap a, b, d;
    take(&a);
    burn_user(ms / 1000.0);
    take(&b);
    diff(&a, &b, &d);
    printf("спалено ~%.0f мс самого лише власного коду\n", ms);
    report(&d);
    return 0;
}
