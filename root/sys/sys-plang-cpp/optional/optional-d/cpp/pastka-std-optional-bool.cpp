std::optional<bool> opt_flag = false;

// ПАСТКА! Неявне зведення до bool перевіряє has_value(), а не значення усередині!
if (opt_flag) {
    // Цей блок ВИКОНАЄТЬСЯ, тому що opt_flag МІСТИТЬ значення (нехай і false!)
}

// Коректна перевірка значення усередині optional<bool>:
if (opt_flag.value_or(false)) {
    // Виконається лише тоді, коли opt_flag заповнений І дорівнює true
}
