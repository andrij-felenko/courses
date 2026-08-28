auto x = trs::make_variable("x");
auto y = trs::make_variable("y");
auto z = trs::make_variable("z");
auto e = trs::make_function("e", {});
auto inv = [](trs::TermPtr a) { return trs::make_function("i", {a}); };
auto mul = [](trs::TermPtr a, trs::TermPtr b) { return trs::make_function("*", {a, b}); };

std::vector<std::pair<trs::TermPtr, trs::TermPtr>> axioms = {
    { mul(e, x), x },
    { mul(inv(x), x), e },
    { mul(mul(x, y), z), mul(x, mul(y, z)) }
};
