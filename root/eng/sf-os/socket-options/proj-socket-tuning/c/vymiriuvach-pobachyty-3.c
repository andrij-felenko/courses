int main(int argc, char **argv)
{
    int server = 0, nodelay = 0, port = 9099, iters = 1000;
    const char *host = "127.0.0.1";

    for (int i = 1; i < argc; i++) {
        if      (!strcmp(argv[i], "-s"))                 server  = 1;
        else if (!strcmp(argv[i], "-d"))                 nodelay = 1;
        else if (!strcmp(argv[i], "-c") && i + 1 < argc) host  = argv[++i];
        else if (!strcmp(argv[i], "-p") && i + 1 < argc) port  = atoi(argv[++i]);
        else if (!strcmp(argv[i], "-n") && i + 1 < argc) iters = atoi(argv[++i]);
        else {
            fprintf(stderr, "вжиток: %s -s | -c <адреса> [-d] [-p порт] [-n обмінів]\n",
                    argv[0]);
            return 2;
        }
    }
    if (server) run_server(port);
    else        run_client(host, port, nodelay, iters);
    return 0;
}
