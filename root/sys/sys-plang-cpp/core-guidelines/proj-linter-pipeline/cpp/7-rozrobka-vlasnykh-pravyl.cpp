#include "clang/ASTMatchers/ASTMatchFinder.h"
#include "clang/ASTMatchers/ASTMatchers.h"
#include "clang/StaticAnalyzer/Checkers/BuiltinCheckerRegistration.h"
#include "clang/Tidy/ClangTidyCheck.h"

using namespace clang::ast_matchers;

namespace custom_guidelines {

class FactoryReturnCheck : public clang::tidy::ClangTidyCheck {
public:
    FactoryReturnCheck(llvm::StringRef Name, clang::tidy::ClangTidyContext *Context)
        : ClangTidyCheck(Name, Context) {}

    void registerMatchers(MatchFinder *Finder) override {
        // Шукаємо оголошення функцій, назва яких починається з "create" або "make",
        // які повертають сирий вказівник замість розумного
        Finder->addMatcher(
            functionDecl(
                hasName("create"),
                returns(pointerType(pointee(hasDeclaration(recordDecl()))))
            ).bind("faulty_factory"),
            this
        );
    }

    void check(const MatchFinder::MatchResult &Result) override {
        const auto *MatchedDecl = Result.Nodes.getNodeAs<clang::FunctionDecl>("faulty_factory");
        if (!MatchedDecl) return;

        diag(MatchedDecl->getLocation(),
             "Фабрична функція %0 повертає сирий вказівник; за правилом R.3 слід повертати std::unique_ptr")
            << MatchedDecl;
    }
};

} // namespace custom_guidelines
