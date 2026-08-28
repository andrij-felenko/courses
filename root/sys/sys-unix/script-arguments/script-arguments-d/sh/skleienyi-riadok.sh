join_by_comma() {
    old_ifs="$IFS"
    IFS=","
    result="$*"
    IFS="$old_ifs"
    printf "%s\n" "$result"
}

# Виклик: join_by_comma "Київ" "Львів" "Одеса"
# Виведе: Київ,Львів,Одеса
