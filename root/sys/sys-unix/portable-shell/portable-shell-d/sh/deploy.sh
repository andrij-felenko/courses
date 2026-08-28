$ shellcheck -s sh deploy.sh

In deploy.sh line 12:
    [[ -d "$target_dir" ]] || mkdir -p "$target_dir"
    ^--------------------^
SC3010 (warning): In POSIX sh, [[ ]] is undefined.

In deploy.sh line 19:
    local status="running"
    ^----------^
SC3043 (warning): In POSIX sh, 'local' is undefined.

In deploy.sh line 34:
    diff <(generate_old) <(generate_new)
         ^-------------^
SC3001 (warning): In POSIX sh, process substitution is undefined.
