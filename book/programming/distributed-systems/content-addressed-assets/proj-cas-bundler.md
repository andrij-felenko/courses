# ⚙️ Контентно-адресований репозиторій блобів та пайплайн збирання асетів

Практична реалізація контентної адресації вимагає двох взаємопов'язаних системних компонентів: низькорівневого атомарного сховища блобів (CAS Store) із самоверифікацією цілісності та високорівневого конвеєра збирання, який виконує топологічний обхід графа залежностей, підстановку хешів, розрахунок підписів безпеки SRI та генерацію маніфесту.

---

### 1. Ядро сховища CAS: атомарний запис та самоперевірка

Ключовий системний контракт сховища CAS базується на фундаментальному інваріанті: **адреса блобу завжди дорівнює криптографічному дайджесту його вмісту**.

Запис блобу в сховище виконується у три строго детерміновані кроки:
1. **Обчислення дайджесту:** потік вхідних байтів хешується за алгоритмом SHA-256 (256 біт, 64 шістнадцяткових символи). Це гарантує математичну однозначність ідентифікатора.
2. **Ізольований запис:** дані записуються у тимчасовий файл у службовому підкаталозі `tmp/` у межах тієї самої точки монтування файлової системи. Це виключає затримки на копіювання між дисковими розділами під час перейменування.
3. **Атомарне перейменування (*atomic rename*):** системний виклик `rename()` (POSIX `rename` або Win32 `MoveFileEx` з прапорцем заміни) переміщує файл у фінальний шлях виду `store/8f/4a1c9b...` (де перші 2 символи виділяються в підкаталог, щоб уникнути деградації продуктивності файлових систем через ліміти на кількість записів в одному каталозі).

Завдяки атомарності системного виклику паралельні читачі або фонові процеси ніколи не натраплять на частково записаний або заблокований файл. Якщо файл із таким хешем уже існує на диску, запис миттєво пропускається, забезпечуючи автоматичну дедуплікацію нульової вартості.

Під час читання даних сховище реалізує принцип активної самоперевірки (*Self-Verification*). Кожен прочитаний блок повторно хешується перед віддачею викликаючому коду. Якщо внаслідок апаратного збою диска (*silent bit rot*), збою контролера або втручання зловмисника байти на диску змінилися, сховище не віддає скомпрометовані дані, а негайно повертає помилку цілісності.

:::tabs
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <filesystem>
#include <fstream>
#include <sstream>
#include <iomanip>
#include <optional>
#include <openssl/sha.h>

namespace fs = std::filesystem;

class ContentAddressableStore {
public:
    explicit ContentAddressableStore(fs::path root_dir) 
        : root_dir_(std::move(root_dir)) {
        fs::create_directories(root_dir_ / "tmp");
    }

    // Обчислення SHA-256 у шістнадцятковий рядок
    static std::string compute_sha256(std::string_view data) {
        unsigned char hash[SHA256_DIGEST_LENGTH];
        SHA256(reinterpret_cast<const unsigned char*>(data.data()), data.size(), hash);
        
        std::ostringstream oss;
        for (unsigned char byte : hash) {
            oss << std::hex << std::setw(2) << std::setfill('0') << static_cast<int>(byte);
        }
        return oss.str();
    }

    // Отримання відносного шляху блобу за префіксом (2 символи на підкаталог)
    [[nodiscard]] fs::path blob_path(std::string_view digest) const {
        return root_dir_ / digest.substr(0, 2) / digest.substr(2);
    }

    // Збереження блобу з гарантією атомарності та дедуплікації
    std::string put(std::string_view data) {
        const std::string digest = compute_sha256(data);
        const fs::path target = blob_path(digest);

        if (fs::exists(target)) {
            return digest; // Уже збережено — дедуплікація
        }

        fs::create_directories(target.parent_path());

        // Атомарний запис через тимчасовий файл у тій самій файловій системі
        const fs::path temp_file = root_dir_ / "tmp" / (digest + ".tmp." + std::to_string(rand()));
        {
            std::ofstream out(temp_file, std::ios::binary | std::ios::trunc);
            out.write(data.data(), static_cast<std::streamsize>(data.size()));
            out.flush();
        }

        fs::rename(temp_file, target);
        return digest;
    }

    // Читання блобу із самоперевіркою цілісності на льоту
    std::optional<std::string> get(std::string_view digest) const {
        const fs::path path = blob_path(digest);
        if (!fs::exists(path)) {
            return std::nullopt;
        }

        std::ifstream in(path, std::ios::binary);
        std::stringstream buffer;
        buffer << in.rdbuf();
        std::string content = buffer.str();

        // Верифікація інваріанта: захист від апаратного пошкодження диска
        if (compute_sha256(content) != digest) {
            std::cerr << "[КРИТИЧНО] Пошкодження даних для блобу: " << digest << std::endl;
            return std::nullopt;
        }

        return content;
    }

private:
    fs::path root_dir_;
};

int main() {
    ContentAddressableStore store("./cas_repository");

    std::string payload = "console.log('Production static asset payload');";
    std::string digest = store.put(payload);

    std::cout << "Збережено блоб з відбитком: " << digest << std::endl;

    auto retrieved = store.get(digest);
    if (retrieved) {
        std::cout << "Успішно прочитано та верифіковано: " << *retrieved << std::endl;
    }
    return 0;
}
```
```ts
import * as fs from 'node:fs';
import * as path from 'node:path';
import * as crypto from 'node:crypto';

export class ContentAddressableStore {
  private readonly rootDir: string;
  private readonly tmpDir: string;

  constructor(rootDir: string) {
    this.rootDir = path.resolve(rootDir);
    this.tmpDir = path.join(this.rootDir, 'tmp');
    fs.mkdirSync(this.tmpDir, { recursive: true });
  }

  // Обчислення криптографічного дайджесту SHA-256
  public computeHash(content: Buffer | string): string {
    return crypto.createHash('sha256').update(content).digest('hex');
  }

  // Шлях до об'єкта зі структурою каталогів 2/62 символи
  public getBlobPath(digest: string): string {
    const prefix = digest.slice(0, 2);
    const remainder = digest.slice(2);
    return path.join(this.rootDir, prefix, remainder);
  }

  // Атомарний запис блобу
  public put(content: Buffer | string): string {
    const buffer = Buffer.isBuffer(content) ? content : Buffer.from(content, 'utf-8');
    const digest = this.computeHash(buffer);
    const targetPath = this.getBlobPath(digest);

    if (fs.existsSync(targetPath)) {
      return digest; // Повна дедуплікація
    }

    fs.mkdirSync(path.dirname(targetPath), { recursive: true });

    // Тимчасовий файл у межах того ж монтування для атомарного rename
    const tempFile = path.join(this.tmpDir, `${digest}.${Date.now()}.${Math.random().toString(36).slice(2)}.tmp`);
    fs.writeFileSync(tempFile, buffer);
    fs.renameSync(tempFile, targetPath);

    return digest;
  }

  // Читання з миттєвою верифікацією
  public get(digest: string): Buffer | null {
    const targetPath = this.getBlobPath(digest);
    if (!fs.existsSync(targetPath)) {
      return null;
    }

    const data = fs.readFileSync(targetPath);
    const actualHash = this.computeHash(data);

    if (actualHash !== digest) {
      throw new Error(`[Помилка цілісності CAS] Невідповідність хешу: очікувався ${digest}, отримано ${actualHash}`);
    }

    return data;
  }
}
```
:::

---

### 2. Конвеєр збирання: топологічне переписування графа залежностей

Головна складність збирання веб-асетів полягає у правильному порядку обчислення хешів. Якщо файл стилів `styles.css` містить посилання на шрифти `font.woff2` та зображення `logo.png`, його фінальний хеш неможливо обчислити, доки не будуть обчислені хеші всіх залежностей. Якщо ж виконати обчислення у довільному порядку, підстановка хешованого імені шрифту змінить вміст CSS-файлу, що зробить його попередньо обчислений хеш недійсним.

Конвеєр обробляє граф асетів у **зворотному топологічному порядку (Post-Order Traversal)**:
1. **Листки дерева залежностей:** спершу обробляються ресурси, які не мають власних підлеглих посилань (зображення WebP/PNG, шрифти WOFF2, бінарні модулі WASM, аудіофрагменти). Їхні байти хешуються і зберігаються у цільовій папці з відбитком у назві.
2. **Проміжні вузли (CSS/JS):** у тілі файлів стилів і скриптів виконується строга текстова заміна відносних шляхів на отримані хешовані адреси листків. Лише після повної підстановки оновлених адрес обчислюється фінальний хеш вмісту батьківського файлу.
3. **Коренева точка входу (`index.html`):** у кореневому документі замінюються всі посилання на стилі та скрипти, а також генеруються атрибути безпеки `integrity` за стандартом Subresource Integrity (SRI, SHA-384 Base64). Це захищає клієнта від підміни байтів на скомпрометованих CDN-вузлах.
4. **Генерація маніфесту:** створюється єдиний словник `manifest.json`, що зв'язує початкові логічні шляхи з кінцевими хешованими URL. Маніфест використовується бекенд-серверами під час SSR-генерації сторінок.

```ts
import * as fs from 'node:fs';
import * as path from 'node:path';
import * as crypto from 'node:crypto';

export interface AssetManifest {
  [originalPath: string]: {
    hashedPath: string;
    integrity: string; // SRI (Subresource Integrity)
    size: number;
  };
}

export class AssetPipeline {
  private readonly sourceDir: string;
  private readonly distDir: string;
  private readonly manifest: AssetManifest = {};

  constructor(sourceDir: string, distDir: string) {
    this.sourceDir = path.resolve(sourceDir);
    this.distDir = path.resolve(distDir);
    fs.mkdirSync(this.distDir, { recursive: true });
  }

  // Обчислення SRI-хешу за стандартом W3C (SHA-384 base64)
  private computeSri(content: Buffer): string {
    const hash = crypto.createHash('sha384').update(content).digest('base64');
    return `sha384-${hash}`;
  }

  // Генерація короткого хешу для назви файлу (перші 8 байтів / 16 символів hex)
  private computeFingerprint(content: Buffer): string {
    return crypto.createHash('sha256').update(content).digest('hex').slice(0, 16);
  }

  // Обробка одного файлу: збереження у dist з відбитком у назві
  public processAsset(relPath: string, content: Buffer | string): string {
    const buffer = Buffer.isBuffer(content) ? content : Buffer.from(content, 'utf-8');
    const fingerprint = this.computeFingerprint(buffer);
    const parsed = path.parse(relPath);

    const hashedFilename = `${parsed.name}.${fingerprint}${parsed.ext}`;
    const hashedRelPath = path.join(parsed.dir, hashedFilename).replace(/\\/g, '/');
    const targetPath = path.join(this.distDir, hashedRelPath);

    fs.mkdirSync(path.dirname(targetPath), { recursive: true });
    fs.writeFileSync(targetPath, buffer);

    this.manifest[relPath.replace(/\\/g, '/')] = {
      hashedPath: `/${hashedRelPath}`,
      integrity: this.computeSri(buffer),
      size: buffer.length,
    };

    return `/${hashedRelPath}`;
  }

  // Конвеєр обробки графа: Листки (Fonts/Images) -> Стилі (CSS) -> Точка входу (HTML)
  public build(files: { [relPath: string]: string | Buffer }): AssetManifest {
    const paths = Object.keys(files);

    // 1. Обробка статичних листків (зображення, шрифти, WASM)
    const leafExtensions = new Set(['.png', '.jpg', '.svg', '.woff2', '.ttf', '.wasm']);
    for (const p of paths) {
      if (leafExtensions.has(path.extname(p))) {
        this.processAsset(p, files[p]);
      }
    }

    // 2. Обробка CSS з підстановкою оновлених адрес зображень і шрифтів
    for (const p of paths) {
      if (path.extname(p) === '.css') {
        let cssContent = files[p].toString('utf-8');
        for (const [orig, entry] of Object.entries(this.manifest)) {
          cssContent = cssContent.replaceAll(orig, entry.hashedPath);
          cssContent = cssContent.replaceAll(`/${orig}`, entry.hashedPath);
        }
        this.processAsset(p, cssContent);
      }
    }

    // 3. Обробка JS модулів
    for (const p of paths) {
      if (path.extname(p) === '.js') {
        let jsContent = files[p].toString('utf-8');
        for (const [orig, entry] of Object.entries(this.manifest)) {
          jsContent = jsContent.replaceAll(`"${orig}"`, `"${entry.hashedPath}"`);
          jsContent = jsContent.replaceAll(`'${orig}'`, `'${entry.hashedPath}'`);
        }
        this.processAsset(p, jsContent);
      }
    }

    // 4. Обробка HTML (вхідна точка: Cache-Control: no-cache)
    for (const p of paths) {
      if (path.extname(p) === '.html') {
        let htmlContent = files[p].toString('utf-8');
        for (const [orig, entry] of Object.entries(this.manifest)) {
          const regexScript = new RegExp(`<script([^>]*)src=["']/?${orig}["']([^>]*)>`, 'g');
          htmlContent = htmlContent.replace(regexScript, `<script$1src="${entry.hashedPath}" integrity="${entry.integrity}" crossorigin="anonymous"$2>`);

          const regexLink = new RegExp(`<link([^>]*)href=["']/?${orig}["']([^>]*)>`, 'g');
          htmlContent = htmlContent.replace(regexLink, `<link$1href="${entry.hashedPath}" integrity="${entry.integrity}" crossorigin="anonymous"$2>`);
        }
        // HTML зберігається БЕЗ хешу в імені (мутабельна точка входу)
        fs.writeFileSync(path.join(this.distDir, p), htmlContent, 'utf-8');
      }
    }

    // 5. Запис маніфесту
    fs.writeFileSync(
      path.join(this.distDir, 'manifest.json'),
      JSON.stringify(this.manifest, null, 2),
      'utf-8'
    );

    return this.manifest;
  }
}
```

---

### 3. Збирання сміття (Garbage Collection) за досяжністю

Оскільки кожен новий реліз додає нові контентно-адресовані файли до сховища, без механізму періодичної утилізації дисковий простір або бакет S3 неминуче вичерпається.

Видалення файлів за часом модифікації файлової системи (TTL / mtime) є класичною антипатерною практикою: незмінений файл бібліотеки вендора `vendor.9e3b.js`, створений кілька місяців тому, залишається активним і критично необхідним у найсвіжішому релізі. Його видалення призведе до глобальної аварії веб-сервісу.

Єдиним надійним алгоритмом утилізації є **Mark-and-Sweep на основі коренів досяжності**:
1. **Фаза розмітки (Mark Phase):** Збирач зчитує всі маніфести активних релізів за останні `N` днів (вікно збереження, наприклад 14 або 30 днів). Усі хеші асетів, зафіксовані в цих маніфестах, додаються до множини живих об'єктів (*Reachable Set*).
2. **Фаза очищення (Sweep Phase):** Сканується фізичний каталог сховища на диску або перелічуються об'єкти в S3-бакеті. Усі файли, чиїх хешів немає у *Reachable Set*, безпечно видаляються.

Крім того, під час виконання GC у високонавантажених кластерах застосовується захисний інтервал відтермінування (*Grace Period*): файли, створені менше ніж 1 годину тому, ніколи не видаляються, навіть якщо вони відсутні в наявних маніфестах. Це усуває стан гонитви (*race condition*), коли новий білд якраз завантажує свої асети, але ще не встиг опублікувати новий маніфест точки входу.

```ts
export class CasGarbageCollector {
  private readonly storeDir: string;

  constructor(storeDir: string) {
    this.storeDir = path.resolve(storeDir);
  }

  public runGc(activeManifests: AssetManifest[], dryRun = false): { deleted: number; retained: number } {
    // 1. Mark phase: збір усіх досяжних хешів з активних маніфестів
    const reachableHashes = new Set<string>();
    for (const manifest of activeManifests) {
      for (const entry of Object.values(manifest)) {
        const match = entry.hashedPath.match(/\.([a-f0-9]{16,64})\./);
        if (match) {
          reachableHashes.add(match[1]);
        }
      }
    }

    let deleted = 0;
    let retained = 0;

    // 2. Sweep phase: видалення недосяжних блобів
    const scanDir = (dir: string) => {
      const entries = fs.readdirSync(dir, { withFileTypes: true });
      for (const entry of entries) {
        const fullPath = path.join(dir, entry.name);
        if (entry.isDirectory()) {
          if (entry.name !== 'tmp') scanDir(fullPath);
        } else if (entry.isFile()) {
          const match = entry.name.match(/\.([a-f0-9]{16,64})\./);
          const hash = match ? match[1] : null;

          if (hash && !reachableHashes.has(hash)) {
            if (!dryRun) fs.unlinkSync(fullPath);
            deleted++;
          } else {
            retained++;
          }
        }
      }
    };

    scanDir(this.storeDir);
    return { deleted, retained };
  }
}
```

Така комбінована архітектура гарантує повну відсутність збоїв у рантаймі: клієнти отримують блискавичне завантаження з `Cache-Control: immutable`, застарілі файли очищаються без ризику помилок `ChunkLoadError`, а цілісність даних захищена криптографічними хешами.
