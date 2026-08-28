// Кожен член шини мусить мати ≥2 пінів (джерело + приймач).
// Член з одним піном — оголошено, але нікуди не заведено: висячий.
static void warn_dangling(const Netlist& net, const BusName& bn) {
    for (const std::string& m : expand(bn)) {
        auto it = net.find(m);
        size_t n = (it == net.end()) ? 0 : it->second.size();
        if (n < 2)
            printf("ПОПЕРЕДЖЕННЯ: член %s шини %s[...] висить (пінів: %zu)\n",
                   m.c_str(), bn.prefix.c_str(), n);
    }
}
