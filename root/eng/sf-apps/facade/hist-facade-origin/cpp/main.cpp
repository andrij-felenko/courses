// Фасад параметризують складником підсистеми: який генератор коду вжити.
// Домен компіляторів — низькорівневий, тому взірець-мова тут C++ (як у GoF).
class Compiler {
public:
    void compile(std::istream& input, BytecodeStream& output) {
        Scanner scanner(input);
        ProgramNodeBuilder builder;
        Parser parser;
        parser.parse(scanner, builder);          // → будує дерево

        // ↓ ось параметризація: генератор задають ЗЗОВНІ
        RISCCodeGenerator generator(output);
        ProgramNode* parseTree = builder.rootNode();
        parseTree->traverse(generator);          // дерево → байт-код
    }
};

// Клієнтові — один рядок, уся підсистема схована:
Compiler compiler;
compiler.compile(source, target);
