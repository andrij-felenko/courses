#!/bin/bash
# /usr/lib/initcpio/hooks/keycheck — виконавець хука в рантаймі mkinitcpio

run_hook() {
    # Зчитати параметр keycheck.path із командного рядка
    for arg in $CMDLINE; do
        case "$arg" in
            keycheck.path=*)
                KEY_PATH="${arg#*=}"
                ;;
        esac
    done

    if [ -n "$KEY_PATH" ]; then
        echo "mkinitcpio: Verifying key at $KEY_PATH..."
        if ! initramfs-keycheck "$KEY_PATH"; then
            echo "mkinitcpio: Key check failed! Falling back to rescue shell."
            launch_interactive_shell
        fi
    fi
}
