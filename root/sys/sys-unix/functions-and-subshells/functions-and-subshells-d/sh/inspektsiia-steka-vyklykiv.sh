print_stack_trace() {
    local frame=0
    echo "=== Stack Traceback (most recent call first) ==="
    while [ $frame -lt ${#FUNCNAME[@]} ]; do
        local func="${FUNCNAME[$frame]}"
        local file="${BASH_SOURCE[$frame+1]}"
        local line="${BASH_LINENO[$frame]}"
        [ -z "$file" ] && file="${BASH_SOURCE[$frame]}"
        printf "  [%d] %s() at %s:%d\n" "$frame" "$func" "$file" "$line"
        frame=$((frame + 1))
    done
}
