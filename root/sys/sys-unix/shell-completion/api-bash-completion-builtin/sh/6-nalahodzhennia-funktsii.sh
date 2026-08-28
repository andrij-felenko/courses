_debug_completion() {
    local log_file="/tmp/bash_completion_debug.log"
    {
        echo "=== $(date) ==="
        echo "COMP_LINE:  '$COMP_LINE'"
        echo "COMP_POINT: $COMP_POINT"
        echo "COMP_CWORD: $COMP_CWORD"
        echo "COMP_WORDS: ${COMP_WORDS[*]}"
        echo "cur:        '$cur'"
        echo "prev:       '$prev'"
    } >> "$log_file"
}
