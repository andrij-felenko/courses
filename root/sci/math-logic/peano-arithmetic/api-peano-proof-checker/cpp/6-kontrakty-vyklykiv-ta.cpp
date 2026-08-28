#include <iostream>
#include <vector>

int main() {
    using namespace peano::verifier;

    std::cout << "=== Перевірка формального доведення через PA Proof Checker API (C++20) ===\n";

    ProofContext ctx;
    ctx.steps.push_back(ProofStep{
        .step_id = 1,
        .formula_ast = reinterpret_cast<const void*>(0x1000),
        .rule = RuleType::AxiomAddBase,
        .ref_step_1 = 0,
        .ref_step_2 = 0
    });

    ctx.steps.push_back(ProofStep{
        .step_id = 2,
        .formula_ast = reinterpret_cast<const void*>(0x2000),
        .rule = RuleType::Generalization,
        .ref_step_1 = 1,
        .ref_step_2 = 0
    });

    auto result = verify_proof(ctx);

    if (result.has_value()) {
        std::cout << "Результат: Формальне доведення УСПІШНО ВЕРИФІКОВАНО (Success)\n";
    } else {
        auto [failed_step, status] = result.error();
        std::cout << "Результат: ПОМИЛКА ВЕРИФІКАЦІЇ у кроці " << failed_step 
                  << " (Код помилки: " << static_cast<uint32_t>(status) << ")\n";
    }

    return 0;
}
