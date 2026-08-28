# Поведінка у Bash та Dash
helper() {
    echo "helper reads x: $x"  # Бачить 'parent_val', якщо викликана з parent!
}

parent() {
    local x="parent_val"
    helper
}

x="global_val"
parent
