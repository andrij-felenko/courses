static long rpc(std::string_view req) {
    if (send_line(req) < 0) {
        std::cerr << "керувальний канал обірвався\n";
        std::exit(2);
    }
    std::string resp;
    if (recv_line(resp) < 0) {
        std::cerr << "помилка читання відповіді\n";
        std::exit(2);
    }
    long v = 0;
    int e = 0;
    if (::sscanf(resp.c_str(), "OK %ld", &v) == 1) return v;
    if (::sscanf(resp.c_str(), "ERR %d", &e) == 1) return -static_cast<long>(e);
    std::cerr << "незрозуміла відповідь: " << resp << "\n";
    std::exit(2);
}
