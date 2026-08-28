struct VarTerm;
struct AbsTerm;
struct AppTerm;

using Term = std::variant<VarTerm, std::shared_ptr<AbsTerm>, std::shared_ptr<AppTerm>>;

struct VarTerm {
    std::string name;
};

struct AbsTerm {
    std::string paramName;
    Type paramType;
    Term body;
};

struct AppTerm {
    Term func;
    Term arg;
};
