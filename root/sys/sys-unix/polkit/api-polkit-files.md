# 📋 Формати й інтерфейси полкіта

Усе, що полкіт читає й відповідає, зводиться до чотирьох контрактів: XML-файл, у якому служба **оголошує** дію; файл `.rules`, у якому адміністратор **вирішує**; метод на шині, яким механізм **питає**; і чотири програми, якими те саме питання ставлять руками. Нижче — точні шляхи, поля, сигнатури й коди повернення, з позначками, де поведінка залежить від випуску.

## Файл дії: `/usr/share/polkit-1/actions/*.policy`

Файл належить пакетові служби; адміністратор його не редагує — його слово записують у правилах. Вміст — XML із декларацією типу:

```xml
<!DOCTYPE policyconfig PUBLIC "-//freedesktop//DTD polkit Policy Configuration 1.0//EN"
 "http://www.freedesktop.org/software/polkit/policyconfig-1.dtd">
```

| Елемент | Де | Що це |
|---|---|---|
| `policyconfig` | корінь, рівно раз | вміщує все інше |
| `vendor`, `vendor_url`, `icon_name` | у корені або в `action` | хто автор і яку піктограму показати; у `action` перекриває загальне |
| `action id="…"` | 0…n | оголошення дії; в `id` дозволені `[A-Za-z0-9]`, крапка й дефіс |
| `description` | в `action` | коротка назва дії для людини («Mount a filesystem») |
| `message` | в `action` | речення, яке побачить людина у вікні пароля |
| `defaults` | в `action` | типові відповіді для трьох кошиків обставин |
| `annotate key="…"` | в `action`, 0…n | іменована пара ключ-значення для тих, хто вміє її читати |

`description` і `message` повторюють з атрибутом `xml:lang` для кожного перекладу.

```xml
<action id="org.freedesktop.policykit.exec">
  <description>Run a program as another user</description>
  <message>Authentication is required to run $(program) as $(user)</message>
  <defaults>
    <allow_any>auth_admin</allow_any>
    <allow_inactive>auth_admin</allow_inactive>
    <allow_active>auth_admin_keep</allow_active>
  </defaults>
  <annotate key="org.freedesktop.policykit.imply">org.example.frobnicate</annotate>
</action>
```

**Підстановки.** Входження `$(ключ)` у `description` і `message` замінюються значенням однойменної подробиці з запиту; якщо такої подробиці немає, полкіт лишає в журналі скаргу про невдалу підстановку. `pkexec` завжди передає `user`, `user.gecos`, `user.display`, `program` і `command_line`; решту ключів вигадує сам механізм і документує у себе (наприклад, UDisks передає `device`, `drive`, `id.type`, `id.label`, `partition.number`). Дві подробиці мають особливий сенс для самого полкіта: `polkit.message` заміняє текст із файлу дії цілком, `polkit.gettext_domain` каже, у якому домені його перекладати.

**Відомі анотації:**

| Ключ | Дія |
|---|---|
| `org.freedesktop.policykit.exec.path` | повний шлях програми, для якої `pkexec` вживає саме цю дію замість типової `org.freedesktop.policykit.exec` |
| `org.freedesktop.policykit.exec.allow_gui` | непорожнє значення — `pkexec` лишає `$DISPLAY` і `$XAUTHORITY`; документація радить так не робити |
| `org.freedesktop.policykit.imply` | список дій, дозвіл на які випливає з дозволу на цю |
| `org.freedesktop.policykit.owner` | список осіб (`unix-user:`, `unix-group:`), яким вільно **питати**, чи авторизований хтось інший на цю дію |

**Шість значень** у `allow_any` / `allow_inactive` / `allow_active`:

| Значення | Що робить |
|---|---|
| `no` | відмовити мовчки |
| `yes` | дозволити мовчки |
| `auth_self` | спитати пароль самого прохача |
| `auth_admin` | спитати пароль адміністратора |
| `auth_self_keep` | те саме, що `auth_self`, і запамʼятати відповідь (типово ≈5 хв) |
| `auth_admin_keep` | те саме, що `auth_admin`, із запамʼятовуванням |

## Файли правил: `*.rules`

Теки обходу — чотири, у такому порядку:

```
/etc/polkit-1/rules.d/
/run/polkit-1/rules.d/
/usr/local/share/polkit-1/rules.d/
/usr/share/polkit-1/rules.d/
```

Порядок виконання — **лексикографічний за базовою назвою файлу наскрізно по всіх чотирьох теках разом**, і лише за однакової назви виграє тека, що вище в списку. Тобто `10-щось.rules` із `/usr/share` виконається раніше за `49-моє.rules` з `/etc`, а `/etc/…/49-моє.rules` перекриє однойменний файл з `/usr/share`. Звідси й звичка починати власні файли з двоцифрового номера.

Мова — JavaScript рівня ECMA-262 edition 5; жодного вводу-виводу, крім наведених нижче двох функцій, у скрипта немає.

```js
void     polkit.addRule(polkit.Result function(action, subject) { … });
void     polkit.addAdminRule(string[]     function(action, subject) { … });
void     polkit.log(string message);
string   polkit.spawn(string[] argv);
```

Функції викликаються в порядку додавання, доки одна не поверне значення. Повернення `polkit.Result.NOT_HANDLED`, `null`, `undefined` або відсутність `return` означає «я не про це» — беруть наступну функцію, а коли скінчилися всі — `<defaults>` із файлу дії.

| `polkit.Result` | Наслідок |
|---|---|
| `NO` | відмова, остаточно |
| `YES` | дозвіл без запитань |
| `AUTH_SELF` / `AUTH_SELF_KEEP` | пароль прохача, без / із запамʼятовуванням |
| `AUTH_ADMIN` / `AUTH_ADMIN_KEEP` | пароль адміністратора, без / із запамʼятовуванням |
| `NOT_HANDLED` | передати рішення далі |

`addAdminRule` відповідає на інше питання — **хто тут адміністратор** для цієї конкретної дії — і повертає масив рядків виду `"unix-group:wheel"`, `"unix-user:ivan"`, `"unix-netgroup:admins"`.

**Обʼєкт `action`:** `string id` і `string lookup(string key)` — той самий словник подробиць, що живить підстановки в повідомленні.

**Обʼєкт `subject`:**

| Поле | Тип | Значення |
|---|---|---|
| `pid`, `uid` | int | номер процесу й числовий ідентифікатор власника |
| `user` | string | імʼя користувача |
| `groups` | string[] | усі його групи |
| `seat`, `session` | string | ідентифікатори [місця й сеансу за logind](root:sys-unix/logind-sessions-seats) |
| `local` | boolean | `true`, лише якщо місце локальне |
| `active` | boolean | `true`, лише якщо сеанс зараз активний |
| `system_unit` | string | [юніт systemd](root:sys-unix/systemd-model), у якому живе процес; лише системний — процес із користувацького сеансу віддасть тут `user@1000.service` |
| `no_new_privileges` | boolean | заповнене, лише якщо `system_unit` непорожнє: `true`, коли в юніті ввімкнено `NoNewPrivileges=` |
| `isInGroup(name)` | boolean | членство у групі |
| `isInNetGroup(name)` | boolean | членство в мережевій групі [через NSS](root:sys-unix/user-database-nss) |

> 🔧 **Навіщо це.** Пара `system_unit` + `no_new_privileges` — єдиний спосіб написати правило про **службу**, а не про людину: імʼя користувацького юніта може вигадати будь-хто без прав, тому полкіт свідомо звужується до системних, а `no_new_privileges` дає гарантію, що всередині того юніта ніхто не підніметься setuid-двійником уже після перевірки.

**Час.** Скрипт, що виконується довше за 15 секунд, вбивають без винятку. `polkit.spawn()` чекає на помічника не довше за 10 секунд, повертає його стандартний вивід рядком і кидає виняток, якщо той завершився не нулем.

```js
polkit.addRule(function (action, subject) {
    if (action.id.indexOf("org.freedesktop.udisks2.") === 0 &&
        action.lookup("drive.removable") === "true" &&
        subject.isInGroup("storage") && subject.local && subject.active) {
        polkit.log("udisks дозволено для " + subject.user);
        return polkit.Result.YES;
    }
});
polkit.addAdminRule(function (action, subject) {
    return ["unix-group:wheel"];
});
```

## Шина: `CheckAuthorization`

Механізм не читає нічого з наведеного вище — він ставить одне питання на [системній шині](root:sys-unix/dbus).

```
імʼя на шині   org.freedesktop.PolicyKit1
обʼєкт         /org/freedesktop/PolicyKit1/Authority
інтерфейс      org.freedesktop.PolicyKit1.Authority

CheckAuthorization(in (sa{sv}) subject,
                   in s        action_id,
                   in a{ss}    details,
                   in u        flags,
                   in s        cancellation_id,
                   out (bba{ss}) result)
```

Суб'єкт — пара «вид» плюс словник подробиць:

| Вид | Ключі подробиць |
|---|---|
| `system-bus-name` | `name` (`s`) — імʼя зʼєднання на кшталт `:1.42`; підробити неможливо, гонки немає |
| `unix-process` | `pidfd` (`h`) та `uid` (`i`) — з випуску 124 (2024); стара форма `pid` (`u`), `start-time` (`t`), `uid` (`i`) вважається застарілою |
| `unix-session` | `session-id` (`s`) — увесь сеанс, а не окремий процес |

`flags`: `0` — не питати нічого й відповісти тим, що є; `1` (`AllowUserInteraction`) — дозволити полкітові покликати агента автентифікації. `cancellation_id` — довільний рядок, яким той самий виклик потім скасовують методом `CancelCheckAuthorization`.

Результат `(bba{ss})` — це `is_authorized`, `is_challenge` і словник подробиць. Пара прапорців читається так: `true`/`false` — дозволено; `false`/`true` — потрібна автентифікація, але її не пробували (не було прапорця або агента); `false`/`false` — відмова.

Решта інтерфейсу: `EnumerateActions`, `RegisterAuthenticationAgent` (і `…WithOptions`), `UnregisterAuthenticationAgent`, `AuthenticationAgentResponse2`, `EnumerateTemporaryAuthorizations`, `RevokeTemporaryAuthorizations`, `RevokeTemporaryAuthorizationById`, сигнал `Changed`.

Мінімальний виклик руками:

```sh
busctl call org.freedesktop.PolicyKit1 /org/freedesktop/PolicyKit1/Authority \
  org.freedesktop.PolicyKit1.Authority CheckAuthorization \
  '(sa{sv})sa{ss}us' \
  system-bus-name 1 name s :1.42 \
  org.freedesktop.udisks2.filesystem-mount 0 1 ""
```

## Командний рядок

**`pkaction`** — читач файлів дій: без аргументів друкує всі відомі ідентифікатори, `--action-id <дія> --verbose` — опис, повідомлення, вендора, піктограму й три типові відповіді.

**`pkcheck`** ставить питання рівно так, як його ставив би механізм:

```
pkcheck --action-id ДІЯ
        { --process pid,pid-start-time,uid | --system-bus-name ІМʼЯ }
        [--detail КЛЮЧ ЗНАЧЕННЯ]… [--allow-user-interaction] [--enable-internal-agent]
pkcheck --list-temp | --revoke-temp
```

Довідка прямо забороняє короткі форми `--process pid` і `pid,start-time`: в обох є гонка. Відповідь читають з коду виходу:

| Код | Що сталося |
|---|---|
| 0 | авторизовано |
| 1 | не авторизовано |
| 2 | потрібна автентифікація, але агента немає або не передали `--allow-user-interaction` |
| 3 | людина закрила вікно запиту |
| 126 | помилка в самих аргументах |
| 127 | помилка під час перевірки |

**`pkexec [--user імʼя] [--keep-cwd] ПРОГРАМА [АРГУМЕНТИ…]`** запускає програму від імені іншого користувача (типово root). Оточення зачищається до мінімального безпечного, `PKEXEC_UID` ставиться в uid того, хто викликав. Код виходу — код програми; `127` — не авторизовано або сталася помилка, `126` — людина закрила вікно запиту.

**`pkttyagent [--process pid,pid-start-time | --system-bus-name імʼя] [--notify-fd fd] [--fallback]`** — агент автентифікації для терміналу: питає пароль просто в tty. Потрібен там, де графічного агента немає (ssh, консоль); `--notify-fd` закривається, щойно агента зареєстровано, `--fallback` не дає витіснити вже наявного агента. Типовий ужиток — запустити його у тлі поруч із `pkcheck --allow-user-interaction`.
