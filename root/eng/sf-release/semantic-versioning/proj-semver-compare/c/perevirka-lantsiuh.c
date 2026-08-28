#include <assert.h>
#include <stdio.h>

static int cmp_str(const char *a, const char *b) {
    semver_t va, vb;
    assert(semver_parse(a, &va) == SEMVER_OK);
    assert(semver_parse(b, &vb) == SEMVER_OK);
    return semver_compare(&va, &vb);
}

int main(void) {
    // Числами, не рядками — класична пастка саморобних порівнянь:
    assert(cmp_str("1.2.0", "1.10.0") < 0);          // 2 < 10 як числа
    assert(cmp_str("1.10.0", "1.2.0") > 0);

    // Канонічний ланцюг зростання зі специфікації — кожен строго менший за наступний:
    const char *chain[] = {
        "1.0.0-alpha", "1.0.0-alpha.1", "1.0.0-alpha.beta",
        "1.0.0-beta",  "1.0.0-beta.2",  "1.0.0-beta.11",
        "1.0.0-rc.1",  "1.0.0",
    };
    for (int i = 0; i + 1 < (int)(sizeof chain / sizeof *chain); ++i)
        assert(cmp_str(chain[i], chain[i + 1]) < 0);

    // Окремо — три місця, де саморобні порівнювачі найчастіше брешуть:
    assert(cmp_str("1.0.0-beta.2",  "1.0.0-beta.11")   < 0);  // числове: 2 < 11, не "11" < "2"
    assert(cmp_str("1.0.0-alpha.1", "1.0.0-alpha.beta") < 0);  // числовий нижчий за буквений
    assert(cmp_str("1.0.0-rc.1",    "1.0.0")            < 0);  // передвипуск нижчий за випуск

    // Метадані збірки ігноруються — це та сама версія за старшинством:
    assert(cmp_str("1.0.0+build.9", "1.0.0+build.5")       == 0);
    assert(cmp_str("1.0.0+exp.sha.5114f85", "1.0.0")       == 0);

    puts("усі перевірки пройдено");
    return 0;
}
