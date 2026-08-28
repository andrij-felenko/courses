int main(int argc, char **argv)
{
    int only = (argc > 1) ? atoi(argv[1]) : 0;

    setvbuf(stdout, out_buf, _IOFBF, sizeof out_buf);

    if (!only || only == 1) probe_ladder();
    if (!only || only == 2) probe_two_doors();
    if (!only || only == 3) probe_moving_threshold();
    if (!only || only == 4) probe_trapped();
    if (!only || only == 5) probe_calloc();
    return 0;
}
