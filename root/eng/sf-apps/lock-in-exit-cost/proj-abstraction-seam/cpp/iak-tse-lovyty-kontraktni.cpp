#include <cassert>
#include <functional>

using StoreFactory = std::function<std::unique_ptr<ObjectStore>()>;

// Один контракт — проти будь-якої реалізації порту.
void run_contract(const StoreFactory& make) {
    // 1) get неіснуючого ключа — це nullopt, а НЕ виняток.
    {
        auto s = make();
        assert(!s->get("nope/missing").has_value());   // контракт: nullopt
    }

    // 2) Читання-після-запису: поклав — і ОДРАЗУ читаєш те саме.
    //    Саме тут провалиться зрештою-консистентний вендор — і добре,
    //    бо провал у тесті дешевший за провал у проді.
    {
        auto s = make();
        s->put("k/1", "hello");
        auto back = s->get("k/1");
        assert(back.has_value() && *back == "hello");   // контракт RAW
    }

    // 3) list за префіксом бачить щойно покладене.
    {
        auto s = make();
        s->put("p/a", "1");
        s->put("p/b", "2");
        auto keys = s->list("p/");
        assert(keys.size() == 2);                       // контракт: обидва видно
    }

    // 4) Ідемпотентність повтору put тим самим вмістом.
    {
        auto s = make();
        s->put("k/2", "v");
        s->put("k/2", "v");                             // повтор
        assert(*s->get("k/2") == "v");                  // не подвоїлось/зіпсувалось
    }
}

int main() {
    run_contract([]{ return make_store(Vendor::A, "test-bucket"); });
    run_contract([]{ return make_store(Vendor::B, "test-container"); });
    run_contract([]{ return std::make_unique<FakeStore>(); });   // фейк
    // Якщо на B впав крок 2 — ми ЩОЙНО спіймали дірявість
    // «читання-після-запису», поки вона в тесті, а не в бою.
}
