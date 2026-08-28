#!/usr/bin/env python3
import sys
import pexpect

def change_user_password(username: str, new_password: str) -> bool:
    # spawn створює пару PTY через openpty/forkpty
    child = pexpect.spawn(f"passwd {username}", encoding="utf-8", timeout=5)

    try:
        # Список очікуваних підказок
        index = child.expect([
            r"[Nn]ew password:",
            r"[Cc]urrent password:",
            pexpect.EOF,
            pexpect.TIMEOUT
        ])

        if index == 0:
            # Програма запитує новий пароль
            child.sendline(new_password)
        elif index == 1:
            print("Помилка: утиліта вимагає поточний пароль", file=sys.stderr)
            child.close(force=True)
            return False
        else:
            print("Помилка: несподіване завершення або таймаут", file=sys.stderr)
            return False

        # Очікуємо повторного введення для підтвердження
        child.expect(r"[Rr]etype.*password:")
        child.sendline(new_password)

        # Очікуємо підсумку виконання
        child.expect(pexpect.EOF)
        child.close()

        return child.exitstatus == 0

    except pexpect.ExceptionPexpect as e:
        print(f"Збій автоматизації PTY: {e}", file=sys.stderr)
        return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f"Використання: {sys.argv[0]} <користувач> <новий_пароль>")
        sys.exit(1)
    success = change_user_password(sys.argv[1], sys.argv[2])
    sys.exit(0 if success else 1)
