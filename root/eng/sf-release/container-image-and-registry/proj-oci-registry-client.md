# ⚙️ Реалізація клієнта OCI реєстру та монтажу rootfs

Взаємодія з віддаленим OCI-реєстром та підготовка ізольованої файлової системи контейнера вимагає від системного рушія послідовного виконання чотирьох задач:
1. Виконання мережевих HTTP REST API викликів з обробкою Bearer-автентифікації.
2. Парсинг структури маніфесту OCI Image Manifest v1.
3. Потокове викачування бінарних блобів шарів із безперервною перевіркою контрольних сум SHA-256 (Streaming Hash Verification) на льоту.
4. Розпакування tarball-архівів із трансляцією спецфайлів видалення, захистом від атак обходу шляхів (Directory Traversal) та фінальна композиція кореневої файлової системи (rootfs) через системні виклики OverlayFS.

Нижче наведено практичну системну реалізацію базового OCI-клієнта мовами C та C++.

---

## 1. Потокова перевірка SHA-256 під час завантаження

При роботі з розподіленими реєстрами бінарні архіви шарів завантажуються через ненадійні публічні канали зв'язку або сторонні CDN-мережі. Зберігати терабайтний архів на локальний диск без перевірки або зчитувати його в пам'ять повторно після завантаження є неприпустимим: це призводить до подвійного навантаження на підсистему введення-виведення (I/O) хоста та створює ризик запису скомпрометованих даних.

Правильним інженерним рішенням є **потоковий розрахунок хешу (Streaming SHA-256)**: кожен отриманий із сокета мережевий буфер розміром 64 КБ одночасно записується у тимчасовий файл і передається до криптографічного контексту OpenSSL.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <openssl/sha.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>

#define BUFFER_SIZE 65536

typedef struct {
    SHA256_CTX ctx;
    unsigned char hash[SHA256_DIGEST_LENGTH];
    char hex_digest[SHA256_DIGEST_LENGTH * 2 + 1];
    size_t total_bytes;
} LayerVerifier;

/* Ініціалізація криптографічного контексту */
void verifier_init(LayerVerifier *v) {
    SHA256_Init(&v->ctx);
    v->total_bytes = 0;
    memset(v->hex_digest, 0, sizeof(v->hex_digest));
}

/* Оновлення контексту при отриманні чергового мережевого чанка */
void verifier_update(LayerVerifier *v, const void *data, size_t len) {
    SHA256_Update(&v->ctx, data, len);
    v->total_bytes += len;
}

/* Фіналізація та звірка з очікуваним дайджестом із маніфесту */
int verifier_finalize_and_check(LayerVerifier *v, const char *expected_digest) {
    SHA256_Final(v->hash, &v->ctx);
    for (int i = 0; i < SHA256_DIGEST_LENGTH; i++) {
        sprintf(&v->hex_digest[i * 2], "%02x", v->hash[i]);
    }
    v->hex_digest[SHA256_DIGEST_LENGTH * 2] = '\0';

    const char *expected_hex = expected_digest;
    if (strncmp(expected_digest, "sha256:", 7) == 0) {
        expected_hex += 7;
    }

    if (strcmp(v->hex_digest, expected_hex) == 0) {
        return 1; /* Хеш валідний: цілісність підтверджено */
    }
    return 0; /* Невідповідність контрольної суми */
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <span>
#include <iomanip>
#include <sstream>
#include <openssl/sha.h>

class LayerVerifier {
public:
    LayerVerifier() {
        SHA256_Init(&ctx_);
    }

    void update(std::span<const uint8_t> data) noexcept {
        SHA256_Update(&ctx_, data.data(), data.size());
        total_bytes_ += data.size();
    }

    [[nodiscard]] bool verify(std::string_view expected_digest) {
        std::vector<uint8_t> hash(SHA256_DIGEST_LENGTH);
        SHA256_Final(hash.data(), &ctx_);

        std::ostringstream oss;
        for (uint8_t byte : hash) {
            oss << std::hex << std::setw(2) << std::setfill('0') << static_cast<int>(byte);
        }
        computed_hex_ = oss.str();

        std::string_view expected_hex = expected_digest;
        if (expected_hex.starts_with("sha256:")) {
            expected_hex.remove_prefix(7);
        }

        return computed_hex_ == expected_hex;
    }

    [[nodiscard]] std::string_view computed_hex() const noexcept {
        return computed_hex_;
    }

    [[nodiscard]] size_t total_bytes() const noexcept {
        return total_bytes_;
    }

private:
    SHA256_CTX ctx_{};
    size_t total_bytes_{0};
    std::string computed_hex_;
};
```
:::

---

## 2. Монтаж шарів через системний виклик `mount(2)` OverlayFS

Після розпакування всіх tarball-архівів у локальні каталоги сховища хоста (`/var/lib/containerd/io.containerd.snapshotter.v1.overlayfs/snapshots/<id>/fs`), рантайм формує системний рядок параметрів ядра для каскадного об'єднання файлових систем.

Особливості формування параметрів монтування:
- **`lowerdir`**: перелік каталогів незмінних шарів, розділених двокрапкою (`:`). Порядок переліку визначає пріоритет перекриття зверху вниз (найвищий шар вказується першим).
- **`upperdir`**: виділений каталог на хості, відкритий для запису для конкретного екземпляра контейнера.
- **`workdir`**: технічний каталог ядра на тій самій файловій системі, що й `upperdir`, необхідний для атомарних операцій копіювання при записі (Copy-Up).
- **`merged`**: цільова точка монтування, яка передається системному виклику `pivot_root(2)` як майбутній корінь контейнера.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mount.h>
#include <errno.h>

int mount_overlay_rootfs(const char **lower_dirs, size_t lower_count,
                         const char *upper_dir, const char *work_dir,
                         const char *merged_target) {
    /* Розрахунок необхідної довжини рядка опцій lowerdir */
    size_t opt_len = 512;
    for (size_t i = 0; i < lower_count; i++) {
        opt_len += strlen(lower_dirs[i]) + 1;
    }
    opt_len += strlen(upper_dir) + strlen(work_dir) + 64;

    char *options = (char *)malloc(opt_len);
    if (!options) {
        perror("Помилка виділення динамічної пам'яті");
        return -1;
    }

    strcpy(options, "lowerdir=");
    for (size_t i = 0; i < lower_count; i++) {
        strcat(options, lower_dirs[i]);
        if (i + 1 < lower_count) {
            strcat(options, ":");
        }
    }

    char buf[512];
    snprintf(buf, sizeof(buf), ",upperdir=%s,workdir=%s", upper_dir, work_dir);
    strcat(options, buf);

    /* Виклик системного монтування OverlayFS у ядрі */
    int ret = mount("overlay", merged_target, "overlay", 0, options);
    if (ret != 0) {
        fprintf(stderr, "Помилка системного виклику mount (%s): %s\n", merged_target, strerror(errno));
        free(options);
        return -1;
    }

    printf("Успішно змонтовано OverlayFS rootfs у %s (кількість нижніх шарів: %zu)\n", merged_target, lower_count);
    free(options);
    return 0;
}
```
```cpp
#include <iostream>
#include <string>
#include <vector>
#include <string_view>
#include <numeric>
#include <sys/mount.h>
#include <cerrno>
#include <cstring>
#include <stdexcept>
#include <filesystem>

namespace fs = std::filesystem;

class OverlayRootfsMount {
public:
    static void mount_layers(const std::vector<fs::path>& lower_dirs,
                             const fs::path& upper_dir,
                             const fs::path& work_dir,
                             const fs::path& merged_target) {
        if (lower_dirs.empty()) {
            throw std::invalid_argument("Масив lower_dirs не може бути порожнім");
        }

        // Формування рядка опцій lowerdir=dir1:dir2:dir3
        std::string lower_opt = "lowerdir=";
        for (size_t i = 0; i < lower_dirs.size(); ++i) {
            lower_opt += lower_dirs[i].string();
            if (i + 1 < lower_dirs.size()) {
                lower_opt += ":";
            }
        }

        std::string options = lower_opt + 
                              ",upperdir=" + upper_dir.string() + 
                              ",workdir=" + work_dir.string();

        // Створення цільової точки монтування
        fs::create_directories(merged_target);

        int res = ::mount("overlay", merged_target.c_str(), "overlay", 0, options.c_str());
        if (res != 0) {
            throw std::runtime_error("Системна помилка mount OverlayFS: " + 
                                     std::string(std::strerror(errno)));
        }

        std::cout << "[OK] OverlayFS змонтовано: " << merged_target 
                  << " (lowerdir count: " << lower_dirs.size() << ")\n";
    }

    static void unmount_rootfs(const fs::path& merged_target) {
        if (::umount2(merged_target.c_str(), MNT_DETACH) != 0) {
            throw std::runtime_error("Помилка розмонтування umount2: " + 
                                     std::string(std::strerror(errno)));
        }
        std::cout << "[OK] Розмонтовано rootfs: " << merged_target << "\n";
    }
};
```
:::

---

## 3. Обробка маркерів Whiteout при розпакуванні тарболів

Під час розпакування OCI tarball-архівів звичайна утиліта `tar` не розуміє специфіки накладання шарів і розпакує службові файли як звичайний текст на диск. Системний розпакувальник (tar unpacker) зобов'язаний перехоплювати записи з префіксом `.wh.` та транслювати їх у системні примітиви ядра Linux:

1. **Whiteout файлу (`.wh.<filename>`):** Створення символьного пристрою з мажорним та мінорним номером `0:0` через `mknod(2)`.
2. **Непрозорий каталог (`.wh..wh..opq`):** Встановлення розширеного атрибута `trusted.overlay.opaque="y"` (або `user.overlay.opaque="y"` у rootless-режимі) на батьківський каталог через системний виклик `setxattr(2)`.

:::tabs
```c
#include <stdio.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/sysmacros.h>
#include <sys/xattr.h>
#include <unistd.h>

int handle_oci_whiteout(const char *parent_dir, const char *entry_name) {
    /* Перевірка на маркер непрозорості каталогу */
    if (strcmp(entry_name, ".wh..wh..opq") == 0) {
        /* Спроба встановити системний атрибут trusted */
        if (setxattr(parent_dir, "trusted.overlay.opaque", "y", 1, 0) != 0) {
            /* Fallback для rootless просторів імен */
            setxattr(parent_dir, "user.overlay.opaque", "y", 1, 0);
        }
        return 1; /* Оброблено як спецмаркер */
    }

    /* Перевірка на видалення конкретного файлу */
    if (strncmp(entry_name, ".wh.", 4) == 0) {
        const char *target_filename = entry_name + 4;
        char whiteout_path[1024];
        snprintf(whiteout_path, sizeof(whiteout_path), "%s/%s", parent_dir, target_filename);

        /* Створення спеціального символьного пристрою ядра whiteout (0:0) */
        dev_t dev = makedev(0, 0);
        if (mknod(whiteout_path, S_IFCHR | 0600, dev) != 0) {
            perror("Помилка створення вузла whiteout через mknod");
            return -1;
        }
        return 1; /* Оброблено як спецмаркер */
    }

    return 0; /* Звичайний файл або каталог */
}
```
```cpp
#include <iostream>
#include <string_view>
#include <filesystem>
#include <sys/stat.h>
#include <sys/sysmacros.h>
#include <sys/xattr.h>
#include <cerrno>
#include <cstring>

namespace fs = std::filesystem;

class OciWhiteoutProcessor {
public:
    static bool process_tar_entry(const fs::path& parent_dir, std::string_view entry_name) {
        if (entry_name == ".wh..wh..opq") {
            // Маркер повної непрозорості каталогу
            int ret = ::setxattr(parent_dir.c_str(), "trusted.overlay.opaque", "y", 1, 0);
            if (ret != 0) {
                ::setxattr(parent_dir.c_str(), "user.overlay.opaque", "y", 1, 0);
            }
            return true;
        }

        if (entry_name.starts_with(".wh.")) {
            // Маркер видалення окремого файлу з нижчого шару
            std::string_view target_name = entry_name.substr(4);
            fs::path target_path = parent_dir / target_name;

            dev_t dev = makedev(0, 0);
            if (::mknod(target_path.c_str(), S_IFCHR | 0600, dev) != 0) {
                std::cerr << "[WARN] Помилка створення whiteout вузла mknod: " 
                          << target_path << " (" << std::strerror(errno) << ")\n";
                return false;
            }
            return true;
        }

        return false; // Звичайний файл
    }
};
```
:::

---

## 4. Безпека розпакування: захист від Directory Traversal (Zip Slip)

Під час обробки неперевірених tarball-архівів із публічних реєстрів зловмисник може сформувати архів, який містить відносні шляхи з виходом за межі кореня (наприклад, `../../../../etc/shadow` або символьне посилання `symlink -> /etc`, за яким слідує запис `symlink/passwd`).

Якщо розпакувальник наївно викличе системний виклик створення файлу без перевірки, шкідливий архів перезапише критичні системні файли хоста.

Для гарантування безпеки розпакувальник застосовує трирівневий захист:
1. **Канонізація шляху:** кожен запис у заголовку перевіряється на відсутність послідовностей `../` та префіксів `/`.
2. **Перевірка меж (Boundary Checking):** сформований абсолютний шлях файлу порівнюється з базовим каталогом шару, блокуючи будь-які спроби виходу назовні.
3. **Апаратна ізоляція VFS:** у сучасних ядрах Linux (версії 5.6+) використовується системний виклик `openat2(2)` із прапорцями `RESOLVE_BENEATH | RESOLVE_NO_SYMLINKS`, який апаратно забороняє перехід через символьні посилання за межі відкритого файлового дескриптора кореня шару.

---

## 5. Простеження системних викликів у Linux (Tracing & Debugging)

Для інспекції реальної поведінки ядра Linux під час монтування rootfs можна скористатися утилітою `strace`:

```bash
strace -f -e trace=mount,umount2,mknod,setxattr ./my_oci_runtime run my_container
```

Типовий журнал системних викликів демонструє точну послідовність дій рушія:
1. `setxattr("/layers/L2/etc", "trusted.overlay.opaque", "y", 1, 0) = 0` — ізоляція каталогу `/etc`.
2. `mknod("/layers/L2/bin/curl", S_IFCHR|0600, makedev(0x0, 0x0)) = 0` — встановлення whiteout для видаленого curl.
3. `mount("overlay", "/run/container/merged", "overlay", 0, "lowerdir=/layers/L2:/layers/L1,upperdir=/run/container/upper,workdir=/run/container/work") = 0` — фінальне монтування кореневої файлової системи.

---

## 6. Пастки та крайові випадки при конструюванні rootfs

1. **Міжшарові жорсткі посилання (Cross-layer Hard Links):** Якщо шар 2 намагається створити `link(2)` на файл із шару 1 під час розпакування, ядро поверне помилку `EXDEV` (Invalid cross-device link). Рантайм контейнерів повинен перехоплювати такі hard link записи в заголовках tar і розгортати їх як фізичне копіювання файлу.
2. **UID/GID мапінг у rootless-середовищах:** При запуску без суперкористувача (Rootless Podman / Docker) системний виклик `chown(2)` для файлів rootfs заборонений ядром. Необхідно використовувати простір імен користувача (`user namespace`) із відображенням суб-UID через утиліту `newuidmap(1)`.
3. **Обнулення міток mtime для білдових кешів:** Неоднакові часові мітки модифікації файлів у заголовках tar призводять до зміни SHA-256 хешу архіву при кожній повторній збірці. Для забезпечення детермінізму збирачі (BuildKit, Kaniko) примусово виставляють `mtime = 0` (1970-01-01 00:00:00 UTC) для незмінених файлів.
4. **Коректне розмонтування та очищення workdir:** При завершенні роботи контейнера точка монтування повинна звільнятися викликом `umount2(merged, MNT_DETACH)`. Якщо процес завершився аварійно і файли у `workdir` залишилися у проміжному стані, ядро може заблокувати наступне монтування OverlayFS з помилкою `EBUSY`. Рушій зобов'язаний повністю очищати вміст `workdir` перед кожним повторним стартом.
