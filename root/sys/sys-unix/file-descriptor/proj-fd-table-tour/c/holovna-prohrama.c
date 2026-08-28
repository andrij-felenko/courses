int main(int argc, char **argv)
{
    setvbuf(stdout, NULL, _IOLBF, 0);   /* порядок рядків = порядок подій */

    const char *child = (argc > 1) ? argv[1] : "./fdchild";

    demo_lowest();
    demo_two_levels();
    demo_manual_redirect();
    demo_exec(child);
    demo_reuse();
    demo_leak();
    return 0;
}
