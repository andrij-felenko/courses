safe_format_file() {
    local i
    local filename="$1"
    local timestamp
    timestamp=$(date +%s)
    
    for i in 1 2 3; do
        printf "."
    done
}
