struct Node { std::string name; std::vector<Node> kids; };

int main() {
    Note n{"Список", "молоко, хліб"};
    n.with_tag("побут").print();          // Taggable віддав Note&, далі Printable
                                          // друкує: Список [побут]
    Note m{"Список", "інше"};
    std::cout << std::boolalpha << (n == m) << '\n';   // true: ключі збігаються

    // ОДНЕ тіло аксесора — чотири різні сигнатури
    static_assert(std::is_same_v<decltype(n.title()),                std::string&>);
    static_assert(std::is_same_v<decltype(std::as_const(n).title()), const std::string&>);
    static_assert(std::is_same_v<decltype(std::move(n).title()),     std::string&&>);
    static_assert(std::is_same_v<decltype(std::as_const(n).body()),  const std::string&>);
    static_assert(std::is_same_v<decltype(std::move(n).body()),      std::string&&>);
