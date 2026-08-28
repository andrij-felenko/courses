// --- Файл client.cpp ---
import transaction_engine;

void run_client() {
    // TransactionContext ctx; // ❌ ПОМИЛКА: ідентифікатор TransactionContext невидимий (Not Visible)

    auto ctx = begin_transaction(1001); // ✅ ДОЗВОЛЕНО: тип TransactionContext досяжний (Reachable)
    ctx.commit();                       // ✅ ДОЗВОЛЕНО: компілятор знає макет класу та зміщення методу commit
    
    constexpr size_t ctx_sz = sizeof(ctx); // ✅ ДОЗВОЛЕНО: повний розмір структури відомий із BMI
}
