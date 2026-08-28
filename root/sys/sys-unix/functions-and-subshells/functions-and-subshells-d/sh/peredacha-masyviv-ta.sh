# Передача масиву за посиланням
append_timestamp() {
    local -n target_array="$1" # target_array стає аліасом змінної, переданої першим аргументом
    target_array+=("$(date +%T)")
}

my_log_entries=("Server started" "Port 8080 open")
append_timestamp my_log_entries

# Масив my_log_entries містить три елементи!
printf "Entry: %s\n" "${my_log_entries[@]}"
