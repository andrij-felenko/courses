struct Person { std::string name; };
struct Student : Person {};

const char* pick(const Person&)          { return "нешаблон  (const Person&)"; }
template <class S> const char* pick(S&&) { return "ШАБЛОН    (S&&)"; }

void demoGreedy() {
    std::puts("\n=== 5. Ненажерливий шаблон: хто виграє відбір ===");

    Person p{"Леся"};
    const Person cp{"Леся"};
    Student st{};
    const Student cst{};

    std::printf("   %s%s\n", pad("Person, неконстантний lvalue", 32).c_str(),  pick(p));
    std::printf("   %s%s\n", pad("Person, константний lvalue", 32).c_str(),    pick(cp));
    std::printf("   %s%s\n", pad("Person, тимчасовий об'єкт", 32).c_str(),     pick(Person{"Леся"}));
    std::printf("   %s%s\n", pad("Student, неконстантний lvalue", 32).c_str(), pick(st));
    std::printf("   %s%s\n", pad("Student, константний lvalue", 32).c_str(),   pick(cst));
}
