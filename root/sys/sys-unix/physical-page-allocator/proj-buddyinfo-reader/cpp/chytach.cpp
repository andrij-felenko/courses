static std::string human(unsigned long bytes)
{
    static const char *u[] = { "Б", "КіБ", "МіБ", "ГіБ", "ТіБ" };
    int i = 0;
    double v = static_cast<double>(bytes);
    while (v >= 1024.0 && i < 4) { v /= 1024.0; i++; }
    char buf[64];
    snprintf(buf, sizeof buf, "%.1f %s", v, u[i]);
    return std::string(buf);
}

static unsigned long pcp_hidden(std::string_view zi, int node, std::string_view zone)
{
    char hdr[64];
    snprintf(hdr, sizeof hdr, "Node %d, zone %8s", node, std::string(zone).c_str());
    auto pos = zi.find(hdr);
    if (pos == std::string_view::npos) return 0;
    auto stop = zi.find("\nNode ", pos + 1);
    auto q = zi.find("\n  pagesets", pos);
    if (q == std::string_view::npos || (stop != std::string_view::npos && q > stop)) return 0;

    unsigned long sum = 0;
    while ((q = zi.find("count:", q + 1)) != std::string_view::npos) {
        if (stop != std::string_view::npos && q > stop) break;
        unsigned long val = 0;
        auto sub = zi.substr(q + 6);
        std::from_chars(sub.data(), sub.data() + sub.size(), val);
        sum += val;
    }
    return sum;
}
