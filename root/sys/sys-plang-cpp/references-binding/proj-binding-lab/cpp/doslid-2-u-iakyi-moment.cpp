static Loud make(std::string name) { return Loud(std::move(name)); }

static void part_lifetime() {
    head("2. Коли саме гине тимчасовий");

    std::cout << "    (а) тимчасовий ні з чим не зв'язаний:\n";
    {
        make("миттєвий");
        std::cout << "        наступний рядок блоку\n";
    }

    std::cout << "    (б) тимчасовий зв'язаний із const Loud&:\n";
    {
        const Loud& kept = make("подовжений");
        std::cout << "        наступний рядок блоку; #" << kept.id() << " живий\n";
    }

    std::cout << "    (в) те саме через Loud&&:\n";
    {
        Loud&& kept = make("подовжений-rvalue");
        std::cout << "        наступний рядок блоку; #" << kept.id() << " живий\n";
    }
}
