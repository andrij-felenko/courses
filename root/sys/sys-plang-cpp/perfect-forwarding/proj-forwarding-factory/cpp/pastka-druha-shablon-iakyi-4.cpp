void demoGuard() {
    std::puts("\n   із запобіжником requires — шаблон більше не претендує на свій тип:");

    std::puts("   Guest g1{\"Леся\"};");
    Guest g1{"Леся"};
    std::puts("   Guest g2{g1};");
    Guest g2{g1};
    std::puts("   Guest g3{std::move(g2)};");
    Guest g3{std::move(g2)};
    std::puts("   Vip vip;");
    Vip vip;
    std::puts("   Guest g4{vip};");
    Guest g4{vip};

    std::printf("      цілі: %s, %s, %s\n",
                g1.name().c_str(), g3.name().c_str(), g4.name().c_str());

    GuestCpp17 old{"той самий запобіжник через enable_if"};
    GuestCpp17 copy{old};
    std::printf("      C++17-версія: %s\n", copy.name().c_str());
}

int main() {
    demoWrappers();
    demoFactory();
    demoEmplace();
    demoLoop();
    demoGreedy();
    demoGuard();
}
