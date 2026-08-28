struct Screen { long long usd, eur; std::string note; };

static long long to_eur(long long cents, long long rate) {   // × rate/100
    return (cents * rate + 50) / 100;
}
static long long to_usd(long long cents, long long rate) {   // ÷ rate/100
    return (cents * 100 + rate / 2) / rate;
}

Screen view(const State& s) {
    if (s.entered == Field::Usd)
        return { s.amount, to_eur(s.amount, s.rate), s.note };
    return { to_usd(s.amount, s.rate), s.amount, s.note };
}
