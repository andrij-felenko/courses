# Варіант 1: Роздільне оголошення (якщо local підтримується системним sh)
my_func() {
    local data
    data=$(faulty_command) || return 1
    process "$data"
}

# Варіант 2: Повна ізоляція через субшел (100% POSIX)
# Круглі дужки замість фігурних виконують тіло у форкнутому субшелі
my_isolated_func() (
    data=$(faulty_command) || exit 1
    # Усі змінні автоматично знищаться при виході з субшела
    process "$data"
)
