#!/usr/bin/env bash
# fast_prompt.sh — високоефективний генератор запрошення для GNU Bash

__prompt_get_git_branch() {
    local git_dir=""
    local cur_dir="$PWD"

    # Шукаємо каталог .git вгору по дереву без виклику команди git
    while [[ -n "$cur_dir" ]]; do
        if [[ -d "${cur_dir}/.git" ]]; then
            git_dir="${cur_dir}/.git"
            break
        elif [[ -f "${cur_dir}/.git" ]]; then
            # Підтримка git-worktree або submodules (файл gitdir: ...)
            local gitdir_content
            if read -r gitdir_content < "${cur_dir}/.git"; then
                if [[ "$gitdir_content" =~ ^gitdir:\ (.*)$ ]]; then
                    git_dir="${cur_dir}/${BASH_REMATCH[1]}"
                    break
                fi
            fi
        fi
        cur_dir="${cur_dir%/*}"
    done

    [[ -z "$git_dir" ]] && return 0

    local head_file="${git_dir}/HEAD"
    [[ ! -r "$head_file" ]] && return 0

    local head_content
    read -r head_content < "$head_file"

    if [[ "$head_content" =~ ^ref:\ refs/heads/(.*)$ ]]; then
        # Звичайна гілка
        echo -n " (git:${BASH_REMATCH[1]})"
    elif [[ -n "$head_content" ]]; then
        # Стан Detached HEAD — виводимо перші 7 символів SHA-1
        echo -n " (git:${head_content:0:7})"
    fi
}

__prompt_format_path() {
    local raw_path="${PWD/#$HOME/\~}"
    local max_depth=3

    # Розбиваємо шлях на сегменти за допомогою масиву
    IFS='/' read -r -a segments <<< "$raw_path"
    local total=${#segments[@]}

    if (( total > max_depth + 1 )); then
        local first="${segments[0]}"
        local last_parts=("${segments[@]:total-max_depth:max_depth}")
        local joined
        joined=$(IFS='/'; echo "${last_parts[*]}")
        echo "${first}/.../${joined}"
    else
        echo "$raw_path"
    fi
}

fast_prompt_command() {
    # КРОК 1: Зберігаємо код повернення ПЕРШИМ рядком функції
    local last_status=$?
    local pipestatus=("${PIPESTATUS[@]}")

    # КРОК 2: Визначення колірної індикації статусу завершення
    local status_color="\[\e[32m\]" # Зелений
    local status_symbol="✓"
    if (( last_status != 0 )); then
        status_color="\[\e[1;31m\]" # Жирний червоний
        status_symbol="✗ [${last_status}]"
    fi

    # КРОК 3: Віртуальні середовища Python / Conda
    local venv_info=""
    if [[ -n "${VIRTUAL_ENV:-}" ]]; then
        venv_info="\[\e[36m\](${VIRTUAL_ENV##*/}) "
    elif [[ -n "${CONDA_DEFAULT_ENV:-}" ]]; then
        venv_info="\[\e[36m\](${CONDA_DEFAULT_ENV}) "
    fi

    # КРОК 4: Отримання інформації про шлях та Git
    local formatted_path
    formatted_path="$(__prompt_format_path)"
    local git_info
    git_info="$(__prompt_get_git_branch)"

    # КРОК 5: Конструювання фінального PS1
    local reset="\[\e[0m\]"
    local user_host="\[\e[1;34m\]\u@\h${reset}"
    local path_str="\[\e[1;33m\]${formatted_path}${reset}"
    local git_str="\[\e[35m\]${git_info}${reset}"
    local prompt_char="\[\e[1m\]\\\$${reset}"

    PS1="${venv_info}${user_host}:${path_str}${git_str} ${status_color}${status_symbol}${reset}\n${prompt_char} "
}

# Встановлюємо хук перед відображенням запрошення
PROMPT_COMMAND=fast_prompt_command
