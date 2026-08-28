// Три примітиви транспорту DNS — res_nquery з <resolv.h> плюс ns_parserr
// з <arpa/nameser.h>. Розбір пакета механічний, тому тут лише оголошення.
struct NaptrRec {
    uint16_t    order, preference;
    std::string flags, service, regexp, replacement;
};
std::vector<NaptrRec> query_naptr(const std::string& name);
std::vector<Target>   query_srv(const std::string& name);   // кидає Denied на ціль "."
std::vector<Addr>     query_addr(const std::string& host);  // A і AAAA

// Що цей клієнт узагалі вміє. Порядок домену (order, потім preference)
// головніший за наш смак: ми тільки викидаємо те, чого не потягнемо.
static const std::array<std::string_view, 3> kPrefer{"SIPS+D2T", "SIP+D2T", "SIP+D2U"};

// Крок 1: голий домен → імена, під якими лежать записи SRV.
std::vector<std::string> service_names(const std::string& domain) {
    std::vector<NaptrRec> recs;
    try { recs = query_naptr(domain); } catch (const DnsError&) {}

    // S-NAPTR: прапорець «S» (далі буде SRV), регулярні вирази заборонені.
    std::erase_if(recs, [](const NaptrRec& n) {
        return n.flags != "S" || !n.regexp.empty() ||
               std::find(kPrefer.begin(), kPrefer.end(), n.service) == kPrefer.end();
    });
    std::stable_sort(recs.begin(), recs.end(), [](const NaptrRec& a, const NaptrRec& b) {
        return std::tie(a.order, a.preference) < std::tie(b.order, b.preference);
    });

    std::vector<std::string> names;
    for (const auto& n : recs) names.push_back(n.replacement);
    if (names.empty())                       // NAPTR немає — транспорт припускаємо самі
        names.push_back("_sips._tcp." + domain + ".");
    return names;
}

// legacy — відкат на вшитий порт. Дозволений ЛИШЕ коли записів немає зовсім.
std::vector<Target> legacy(const std::string& domain) {
    return { Target{domain + ".", 5061, 0, 0, query_addr(domain)} };
}

// Увесь ланцюг. Викликається ОДИН раз на серію спроб.
std::vector<Target> resolve(const std::string& domain) {
    std::vector<Target> plan;
    bool denied = false;

    for (const auto& name : service_names(domain)) {          // крок 2
        std::vector<Target> ts;
        try { ts = query_srv(name); }
        catch (const Denied&)   { denied = true; continue; }  // ціль "." — і жодних обхідних шляхів
        catch (const DnsError&) { continue; }
        if (ts.empty()) continue;

        auto ordered = order_rfc2782(std::move(ts));
        plan.insert(plan.end(), std::make_move_iterator(ordered.begin()),
                                std::make_move_iterator(ordered.end()));
    }

    if (plan.empty()) {
        if (denied) throw Denied{domain};   // домен сказав «ні»: на вшитий порт іти НЕ можна
        return legacy(domain);              // записів просто немає — дозволений старий шлях
    }
    for (auto& t : plan) t.addrs = query_addr(t.host);        // крок 3
    return plan;
}
