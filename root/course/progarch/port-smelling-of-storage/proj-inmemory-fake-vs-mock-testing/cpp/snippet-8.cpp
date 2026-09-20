#include <gtest/gtest.h>

TEST(ToggleDeviceUseCaseTest, SwitchesOffAndPersistsState) {
    // Arrangetabs ::: У такому модульному тесті (англ. :: У такому модульному тесті (англ. @@en|unit test@@) немає декларацій очікувань, шпигунів чи перевірок черговості звернень до бази даних. автономний пам'яттєвий двійник
    InMemoryDeviceRepository repo;
    DeviceId id{"dev-1"};
    repo.save(Device{id, "Кліматичний клапан", true});
    ToggleDeviceUseCase useCase(repo);

    // Acttabs ::: У такому модульному тесті (англ. :: У такому модульному тесті (англ. @@en|unit test@@) немає декларацій очікувань, шпигунів чи перевірок черговості звернень до бази даних. запуск бізнес-сценарію
    bool ok = useCase.execute(id, false);

    // Asserttabs ::: У такому модульному тесті (англ. :: У такому модульному тесті (англ. @@en|unit test@@) немає декларацій очікувань, шпигунів чи перевірок черговості звернень до бази даних. перевірка стану замість підрахунку викликів моків
    EXPECT_TRUE(ok);
    auto updated = repo.find_by_id(id);
    ASSERT_TRUE(updated.has_value());
    EXPECT_FALSE(updated->is_on);
}
