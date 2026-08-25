# ⚙️ Розробка комплішена для CLI-утиліти з підкомандами

Утиліти керування інфраструктурою та хмарними середовищами (`kubectl`, `docker`, `git`, `systemctl`) використовують багаторівневу ієрархію підкоманд, позиційних параметрів та прапорців із фіксованими або динамічними значеннями. Створення якісного сценарію автодоповнення для такої утиліти вимагає коректного розбору контексту, відстеження стану попередніх аргументів і динамічного запиту системних об'єктів без блокування інтерфейсу термінала.

## 1. Архітектура та синтаксичне дерево утиліти

Розглянемо практичну розробку сценарію автодоповнення для консольної утиліти керування мікросервісним кластером `clusterctl`. Синтаксичне дерево команд має наступну структуру:

```text
clusterctl
├── nodes
│   ├── list       [--format=table|json|yaml] [--status=ready|notready]
│   └── drain      <node-name> [--force] [--timeout=<seconds>]
├── service
│   ├── deploy     <service-name> --env=prod|stage|dev [--tag=<image-tag>]
│   ├── logs       <service-name> [-f] [--tail=<lines>]
│   └── restart    <service-name> [--grace-period=<seconds>]
└── global flags:  --kubeconfig=<path>, --verbose, --help, -v, -h
```

Сценарій автодоповнення повинен розв'язувати чотири фундаментальні інженерні задачі:
1. **Ізоляція глобальних прапорців**: Визначати головну команду та підкоманду незалежно від того, скільки глобальних прапорців користувач ввів перед ними (наприклад, `clusterctl --verbose --kubeconfig=/etc/k8s/conf nodes list`).
2. **Обробка параметрів із роздільниками**: Пропонувати значення прапорців виду `--key=value` без руйнування буфера введення через розрив рядка символом рівності `=`.
3. **Кешування динамічних даних**: Отримувати списки імен вузлів (`node-name`) та сервісів (`service-name`) безпосередньо з локального кешу, виключаючи затримки мережевих викликів під час набору тексту.
4. **Контекстна фільтрація шляхів**: Викликати генератор файлової системи лише для тих опцій, які дійсно приймають шлях до конфігураційного файлу (`--kubeconfig`).

## 2. Реалізація повного сценарію доповнення

Нижче наведено виробничий сценарій автодоповнення для утиліти `clusterctl`, спроєктований для розміщення у системному каталозі `/usr/share/bash-completion/completions/clusterctl`.

```bash
#!/usr/bin/env bash
# /usr/share/bash-completion/completions/clusterctl
# Сценарій автодоповнення для утиліти clusterctl

_clusterctl_get_nodes() {
    # Кешування списку вузлів на 30 секунд для усунення мережевих затримок
    local cache_file="/tmp/.clusterctl_nodes_cache_${UID}"
    local now
    now=$(date +%s)

    if [[ -f "$cache_file" ]]; then
        local mtime
        mtime=$(stat -c %Y "$cache_file" 2>/dev/null || stat -f %m "$cache_file" 2>/dev/null)
        if (( now - mtime < 30 )); then
            cat "$cache_file"
            return 0
        fi
    fi

    # Якщо кеш застарів або відсутній, виконуємо швидкий системний запит
    local nodes
    if nodes=$(clusterctl nodes list --format=names 2>/dev/null); then
        echo "$nodes" > "$cache_file"
        echo "$nodes"
    fi
}

_clusterctl_get_services() {
    local cache_file="/tmp/.clusterctl_services_cache_${UID}"
    local now
    now=$(date +%s)

    if [[ -f "$cache_file" ]]; then
        local mtime
        mtime=$(stat -c %Y "$cache_file" 2>/dev/null || stat -f %m "$cache_file" 2>/dev/null)
        if (( now - mtime < 30 )); then
            cat "$cache_file"
            return 0
        fi
    fi

    local svrs
    if svrs=$(clusterctl service list --format=names 2>/dev/null); then
        echo "$svrs" > "$cache_file"
        echo "$svrs"
    fi
}

_clusterctl() {
    local cur prev words cword
    # Ініціалізація стандартизованого контексту з усуненням розриву по '=' та ':'
    if declare -F _init_completion >/dev/null 2>&1; then
        _init_completion -n "=:" || return
    else
        # Резервна ініціалізація для чистих середовищ без bash-completion
        COMPREPLY=()
        cur="${COMP_WORDS[COMP_CWORD]}"
        prev="${COMP_WORDS[COMP_CWORD-1]}"
        words=("${COMP_WORDS[@]}")
        cword=$COMP_CWORD
    fi

    local global_opts="--kubeconfig= --verbose --help -v -h"
    local top_commands="nodes service help"

    # Обробка аргументів, якщо поточне слово починається зі знака рівності
    if [[ "$cur" == --kubeconfig=* ]]; then
        local file_prefix="${cur#--kubeconfig=}"
        compopt -o filenames -o nospace
        COMPREPLY=( $(compgen -f -- "$file_prefix") )
        return 0
    fi

    if [[ "$cur" == --format=* ]]; then
        local format_val="${cur#--format=}"
        COMPREPLY=( $(compgen -W "table json yaml names" -- "$format_val") )
        return 0
    fi

    if [[ "$cur" == --status=* ]]; then
        local status_val="${cur#--status=}"
        COMPREPLY=( $(compgen -W "ready notready" -- "$status_val") )
        return 0
    fi

    if [[ "$cur" == --env=* ]]; then
        local env_val="${cur#--env=}"
        COMPREPLY=( $(compgen -W "prod stage dev" -- "$env_val") )
        return 0
    fi

    # Визначення позиції головної команди та підкоманди
    local cmd=""
    local subcmd=""
    local i

    for (( i=1; i < cword; i++ )); do
        local w="${words[i]}"
        # Пропускаємо глобальні опції та їхні значення
        if [[ "$w" == --kubeconfig=* || "$w" == -v || "$w" == --verbose || "$w" == -h || "$w" == --help ]]; then
            continue
        fi
        if [[ "$w" == --kubeconfig ]]; then
            (( i++ )) # Пропускаємо наступний аргумент як значення опції
            continue
        fi

        if [[ -z "$cmd" ]]; then
            cmd="$w"
        elif [[ -z "$subcmd" ]]; then
            subcmd="$w"
            break
        fi
    done

    # 1. Рівень кореня: доповнення команд першого рівня та глобальних опцій
    if [[ -z "$cmd" ]]; then
        if [[ "$cur" == -* ]]; then
            COMPREPLY=( $(compgen -W "$global_opts" -- "$cur") )
            [[ ${#COMPREPLY[@]} -eq 1 && "${COMPREPLY[0]}" == *= ]] && compopt -o nospace
        else
            COMPREPLY=( $(compgen -W "$top_commands" -- "$cur") )
        fi
        return 0
    fi

    # 2. Рівень підкоманд: розгалуження за головною командою
    case "$cmd" in
        nodes)
            if [[ -z "$subcmd" ]]; then
                local node_subcmds="list drain"
                if [[ "$cur" == -* ]]; then
                    COMPREPLY=( $(compgen -W "$global_opts" -- "$cur") )
                else
                    COMPREPLY=( $(compgen -W "$node_subcmds" -- "$cur") )
                fi
                return 0
            fi

            case "$subcmd" in
                list)
                    local list_opts="--format= --status="
                    COMPREPLY=( $(compgen -W "$list_opts" -- "$cur") )
                    [[ ${#COMPREPLY[@]} -eq 1 && "${COMPREPLY[0]}" == *= ]] && compopt -o nospace
                    ;;
                drain)
                    if [[ "$cur" == -* ]]; then
                        local drain_opts="--force --timeout="
                        COMPREPLY=( $(compgen -W "$drain_opts" -- "$cur") )
                        [[ ${#COMPREPLY[@]} -eq 1 && "${COMPREPLY[0]}" == *= ]] && compopt -o nospace
                    else
                        # Доповнення імені вузла
                        local nodes
                        nodes=$(_clusterctl_get_nodes)
                        COMPREPLY=( $(compgen -W "$nodes" -- "$cur") )
                    fi
                    ;;
            esac
            ;;

        service)
            if [[ -z "$subcmd" ]]; then
                local srv_subcmds="deploy logs restart"
                if [[ "$cur" == -* ]]; then
                    COMPREPLY=( $(compgen -W "$global_opts" -- "$cur") )
                else
                    COMPREPLY=( $(compgen -W "$srv_subcmds" -- "$cur") )
                fi
                return 0
            fi

            case "$subcmd" in
                deploy)
                    if [[ "$cur" == -* ]]; then
                        local deploy_opts="--env= --tag="
                        COMPREPLY=( $(compgen -W "$deploy_opts" -- "$cur") )
                        [[ ${#COMPREPLY[@]} -eq 1 && "${COMPREPLY[0]}" == *= ]] && compopt -o nospace
                    else
                        # Перший позиційний аргумент після deploy — ім'я сервісу
                        local services
                        services=$(_clusterctl_get_services)
                        COMPREPLY=( $(compgen -W "$services" -- "$cur") )
                    fi
                    ;;
                logs)
                    if [[ "$cur" == -* ]]; then
                        local logs_opts="-f --tail="
                        COMPREPLY=( $(compgen -W "$logs_opts" -- "$cur") )
                        [[ ${#COMPREPLY[@]} -eq 1 && "${COMPREPLY[0]}" == *= ]] && compopt -o nospace
                    else
                        local services
                        services=$(_clusterctl_get_services)
                        COMPREPLY=( $(compgen -W "$services" -- "$cur") )
                    fi
                    ;;
                restart)
                    if [[ "$cur" == -* ]]; then
                        local restart_opts="--grace-period="
                        COMPREPLY=( $(compgen -W "$restart_opts" -- "$cur") )
                        [[ ${#COMPREPLY[@]} -eq 1 && "${COMPREPLY[0]}" == *= ]] && compopt -o nospace
                    else
                        local services
                        services=$(_clusterctl_get_services)
                        COMPREPLY=( $(compgen -W "$services" -- "$cur") )
                    fi
                    ;;
            esac
            ;;

        help)
            COMPREPLY=( $(compgen -W "$top_commands" -- "$cur") )
            ;;
    esac
}

# Реєстрація точки входу комплішена
complete -F _clusterctl clusterctl
```

## 3. Покроковий розбір логіки та синтаксичних структур

### Позиційний аналіз та фільтрація глобальних прапорців

Головна складність розбору командного рядка полягає в тому, що користувач може передавати прапорці у довільному порядку. Наприклад:
- `clusterctl service deploy my-app --env=prod`
- `clusterctl --verbose service --kubeconfig /path deploy my-app --env=prod`

Цикл `for (( i=1; i < cword; i++ ))` послідовно сканує всі попередні токени від початку рядка до поточної позиції курсора. Якщо токен є відомим глобальним прапорцем (`--verbose`, `-v`), цикл пропускає його. Якщо прапорець приймає окремий аргумент (`--kubeconfig <path>`), лічильник циклу додатково збільшується на одиницю `(( i++ ))`, щоб пропустити сам шлях до конфігурації.

Перше знайдене слово, яке не є прапорцем, зберігається у змінній `cmd` (рівень 1). Друге таке слово зберігається у `subcmd` (рівень 2). Це дозволяє функції миттєво перейти до потрібної гілки оператора `case "$cmd" in` без повторного парсингу вже проаналізованого тексту.

### Обробка прапорців із суфіксом знака рівності

Коли скрипт пропонує опцію, яка вимагає обов'язкового значення (наприклад, `--format=`), додавання пропуску після підстановки є помилкою, оскільки користувач має одразу продовжити введення значення.
Для цього застосовується перевірка довжини сформованого результату:

```bash
[[ ${#COMPREPLY[@]} -eq 1 && "${COMPREPLY[0]}" == *= ]] && compopt -o nospace
```

Якщо `COMPREPLY` містить рівно один елемент і цей елемент закінчується на знак `=`, команда `compopt -o nospace` інструктує Readline не додавати кінцевий пропуск. Користувач отримує рядок `--format=`, де наступне натискання Tab негайно розкриває список доступних форматів (`table json yaml names`).

## 4. Інженерний аналіз пасток та крайових випадків

### Пастка розриву слів символом знака рівності

Якщо опція має вигляд `--format=table`, за замовчуванням `COMP_WORDBREAKS` містить символ `=`. Без виклику `_init_completion -n "=:"` Readline розбиває введення на три окремих токени: `["--format", "=", "tab"]`. 
Якщо генератор поверне повний рядок `COMPREPLY=("--format=table")`, Readline здійснить підстановку від поточної позиції курсора (після знаку `=`), у результаті чого рядок перетвориться на сміття: `clusterctl nodes list --format=--format=table`.
Правильний підхід полягає у вилученні префікса через підстановку параметра `${cur#*=}` та застосуванні прапорця `compopt -o nospace`.

### Ціна виконання підоболонок усередині автодоповнення

Кожне натискання клавіші Tab повинно формувати відповідь із затримкою не більше 50 мілісекунд, інакше користувач відчуває затримку інтерфейсу введення. 
Прямий виклик `$(clusterctl nodes list)` породжує створення нового процесу через `fork()` та `execve()`, ініціалізує середовище виконання утиліти (наприклад, середовище виконання Go, Node.js чи Python) та виконує мережевий виклик до сервера API. Якщо сервер відповідає за 300–800 мс, термінал зависає на майже секунду.

Використання файлового кешу в каталозі `/tmp` з перевіркою часової мітки `mtime` через системний виклик `stat` гарантує, що важкий процес викликається лише один раз на 30 секунд, а всі наступні операції Tab читають текстовий список з кешу в пам'яті за частки мілісекунди. Застосування `stat -c %Y` для Linux та резервного `stat -f %m` для систем BSD/macOS забезпечує міжплатформну сумісність.

## 5. Розміщення та інсталяція у системних каталогах

Для коректної інтеграції сценарію у дистрибутивах Linux існують суворі правила розміщення файлів комплішена:

- `/usr/share/bash-completion/completions/clusterctl`: Основне стандартне місце для пакетних утиліт (FHS layout). Назва файлу повинна строго збігатися з іменем бінарника без суфікса `.sh` або `.bash`.
- `/etc/bash_completion.d/clusterctl`: Застарілий каталог для локальних адміністративних скриптів. Файли тут зчитуються монолітно під час старту сесії, тому розміщувати тут важкі сценарії не рекомендується.
- `~/.local/share/bash-completion/completions/clusterctl`: Стандартний каталог для локального користувача, коли права адміністратора `root` недоступні.

## 6. Методика тестування та валідації комплішена

Для перевірки коректності створеного сценарію слід виконати тестовий прогін у чистій сесії Bash:

1. **Тестування на рівні синтаксису Bash**: Перевірити відсутність синтаксичних помилок за допомогою `bash -n /usr/share/bash-completion/completions/clusterctl`.
2. **Ізоляція в чистому середовищі**: Запустити підсесію `env -i HOME="$HOME" PATH="$PATH" bash --noprofile --norc`, завантажити скрипт через `source` та перевірити роботу прапорців.
3. **Профілювання часу відгуку**: Виміряти час виконання генератора за допомогою вбудованої команди `time`:

```bash
COMP_WORDS=("clusterctl" "service" "deploy" "")
COMP_CWORD=3
COMP_LINE="clusterctl service deploy "
COMP_POINT=${#COMP_LINE}

time _clusterctl
echo "Згенеровано варіантів: ${#COMPREPLY[@]}"
```

Час виконання `real` для будь-якої комбінації аргументів не повинен перевищувати `0.050s` (50 мс), що гарантує плавний та миттєвий відгук термінала.
