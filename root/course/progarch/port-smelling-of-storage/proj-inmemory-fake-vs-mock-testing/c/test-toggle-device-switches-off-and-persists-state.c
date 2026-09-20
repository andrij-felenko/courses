#include <assert.h>

void test_toggle_device_switches_off_and_persists_state(void) {
    // Arrangetabs ::: У такому модульному тесті (англ. :: У такому модульному тесті (англ. @@en|unit test@@) немає декларацій очікувань, шпигунів чи перевірок черговості звернень до бази даних. пам'яттєвий двійник із початковим станом
    in_memory_device_repo_t storage = { .count = 0 };
    device_repository_t repo = {
        .find_by_id = in_memory_find_by_id,
        .save = in_memory_save
    };
    device_t initial = { .id = "dev-1", .name = "Клапан", .is_on = true };
    in_memory_save(&storage, &initial);

    // Acttabs ::: У такому модульному тесті (англ. :: У такому модульному тесті (англ. @@en|unit test@@) немає декларацій очікувань, шпигунів чи перевірок черговості звернень до бази даних. виконання доменного сценарію
    bool ok = toggle_device_use_case(&repo, &storage, "dev-1", false);

    // Asserttabs ::: У такому модульному тесті (англ. :: У такому модульному тесті (англ. @@en|unit test@@) немає декларацій очікувань, шпигунів чи перевірок черговості звернень до бази даних. перевірка кінцевого стану агрегату
    assert(ok);
    device_t* updated = in_memory_find_by_id(&storage, "dev-1");
    assert(updated != NULL && updated->is_on == false);
    free(updated);
}
