/*
 * Хостові тести RAII-вартового:
 *
 *   g++ -std=c++20 -Wall -Wextra -I. -o build/test_cs \
 *       cpp/test/test_critical_section.cpp && ./build/test_cs
 */

#include <cstdio>
#include <mutex>
#include <stdexcept>

#include "host_mock_policy.hpp"
#include "../navigation.hpp"

namespace {

int g_failures = 0;

void check(bool ok, const char* what, int line)
{
    if (!ok) {
        std::printf("ПРОВАЛ (рядок %d): %s\n", line, what);
        ++g_failures;
    }
}

#define CHECK(cond) check((cond), #cond, __LINE__)

using Mock  = embedded::test::MockLockPolicy;
using Guard = embedded::sync::CriticalSectionGuard<Mock>;

void test_enter_exit()
{
    Mock::reset();
    {
        const Guard lock;
        CHECK(Mock::locked());
    }
    CHECK(!Mock::locked());
    CHECK(Mock::enters == 1U);
    CHECK(Mock::exits == 1U);
}

void test_nesting()
{
    Mock::reset();
    {
        const Guard outer;
        {
            const Guard inner;
            CHECK(Mock::locked());
        }
        // Вкладений вартовий відновив стан, а не відкрив переривання.
        CHECK(Mock::locked());
    }
    CHECK(!Mock::locked());
    CHECK(Mock::max_depth == 2U);
    CHECK(Mock::depth == 0U);
}

bool lookup_with_early_return(bool found)
{
    const Guard lock;
    if (!found) {
        return false;
    }
    return true;
}

void test_early_return()
{
    Mock::reset();
    CHECK(!lookup_with_early_return(false));
    CHECK(!Mock::locked());
    CHECK(lookup_with_early_return(true));
    CHECK(!Mock::locked());
}

void test_exception_unwinds()
{
    Mock::reset();
    try {
        const Guard lock;
        throw std::runtime_error("збій розбору пакета");
    } catch (const std::runtime_error&) {
        // Розкрутка стека вже викликала деструктор вартового.
    }
    CHECK(!Mock::locked());
    CHECK(Mock::depth == 0U);
}

void test_lock_guard_adapter()
{
    using SpinLock = embedded::sync::InterruptSpinLock<Mock>;

    Mock::reset();
    SpinLock spin;
    {
        const std::lock_guard<SpinLock> lock{spin};
        CHECK(Mock::locked());
    }
    CHECK(!Mock::locked());
}

void test_with_critical_returns_value()
{
    Mock::reset();
    const int value = embedded::sync::with_critical<Mock>([] { return 42; });
    CHECK(value == 42);
    CHECK(!Mock::locked());
}

void test_navigation()
{
    Mock::reset();
    flight::NavigationManager<Mock> nav;

    CHECK(!nav.snapshot().has_value());   // фікса ще немає

    const flight::NavigationData fix{501234567, 306543210, 152300, 1724930000000000ULL};
    nav.update(fix);

    const auto snapshot = nav.snapshot();
    CHECK(snapshot.has_value());
    CHECK(snapshot->latitude == fix.latitude);
    CHECK(snapshot->longitude == fix.longitude);
    CHECK(snapshot->altitude_mm == fix.altitude_mm);
    CHECK(snapshot->timestamp_us == fix.timestamp_us);
    CHECK(nav.updates() == 1U);
    CHECK(!Mock::locked());

    nav.reset();
    CHECK(!nav.snapshot().has_value());
}

}  // namespace

int main()
{
    test_enter_exit();
    test_nesting();
    test_early_return();
    test_exception_unwinds();
    test_lock_guard_adapter();
    test_with_critical_returns_value();
    test_navigation();

    if (g_failures == 0) {
        std::puts("усі перевірки пройдено");
        return 0;
    }
    std::printf("провалено перевірок: %d\n", g_failures);
    return 1;
}
