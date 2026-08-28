#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sshd-audit.py — утиліта аудиту конфігурації OpenSSH.
Зчитує нормалізований вивід 'sshd -T' та зіставляє параметри
із затвердженим базовим профілем загартування.
"""

import subprocess
import sys

# Очікувані безпечні параметри
SECURITY_BASELINE = {
    "passwordauthentication": {
        "expected": "no",
        "severity": "CRITICAL",
        "desc": "Парольна автентифікація дозволяє підбір паролів (brute-force)",
    },
    "kbdinteractiveauthentication": {
        "expected": "no",
        "severity": "HIGH",
        "desc": "Клавіатурно-інтерактивний вхід може пропускати паролі через PAM",
    },
    "permitemptypasswords": {
        "expected": "no",
        "severity": "CRITICAL",
        "desc": "Дозвіл входу без пароля",
    },
    "permitrootlogin": {
        "expected": ["no", "prohibit-password"],
        "severity": "CRITICAL",
        "desc": "Прямий вхід суперкористувача за паролем має бути заборонений",
    },
    "strictmodes": {
        "expected": "yes",
        "severity": "HIGH",
        "desc": "Перевірка прав доступу до ~/.ssh та authorized_keys",
    },
    "maxauthtries": {
        "expected": lambda v: int(v) <= 3,
        "expected_str": "<= 3",
        "severity": "MEDIUM",
        "desc": "Ліміт спроб автентифікації на з'єднання",
    },
    "logingracetime": {
        "expected": lambda v: int(v) <= 30,
        "expected_str": "<= 30s",
        "severity": "MEDIUM",
        "desc": "Таймаут неавтентифікованого з'єднання",
    },
    "x11forwarding": {
        "expected": "no",
        "severity": "LOW",
        "desc": "Прокидання X11 несе ризик перехоплення віконних подій",
    },
}

# Небезпечні криптографічні алгоритми, присутність яких неприпустима
WEAK_CRYPTO = {
    "ciphers": ["cbc", "3des", "arcfour", "cast128", "blowfish"],
    "kexalgorithms": ["diffie-hellman-group1-sha1", "diffie-hellman-group14-sha1", "group-exchange-sha1"],
    "macs": ["md5", "sha1", "96"],
}


def get_sshd_config():
    """Викликає 'sshd -T' та повертає словник параметрів."""
    try:
        res = subprocess.run(["sshd", "-T"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
    except FileNotFoundError:
        print("[!] Помилка: утиліту 'sshd' не знайдено в системі.", file=sys.stderr)
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"[!] Помилка виконання 'sshd -T': {e.stderr}", file=sys.stderr)
        sys.exit(1)

    cfg = {}
    for line in res.stdout.splitlines():
        line = line.strip()
        if not line or " " not in line:
            continue
        key, val = line.split(" ", 1)
        cfg[key.lower()] = val.strip()
    return cfg


def audit_config(cfg):
    """Звіряє налаштування з профілем безпеки."""
    issues = []

    # 1. Базові параметри
    for key, rule in SECURITY_BASELINE.items():
        val = cfg.get(key)
        if val is None:
            issues.append(("UNKNOWN", f"Параметр '{key}' відсутній у конфігурації", rule["severity"]))
            continue

        exp = rule["expected"]
        matched = False
        if callable(exp):
            try:
                matched = exp(val)
            except ValueError:
                matched = False
            exp_display = rule["expected_str"]
        elif isinstance(exp, list):
            matched = val in exp
            exp_display = " | ".join(exp)
        else:
            matched = val == exp
            exp_display = exp

        if not matched:
            issues.append((rule["severity"], f"{key}: поточне '{val}' != очікуване '{exp_display}' ({rule['desc']})"))

    # 2. Криптографічний аудит
    for category, forbidden_patterns in WEAK_CRYPTO.items():
        actual_val = cfg.get(category, "")
        elements = [x.strip() for x in actual_val.split(",") if x.strip()]
        for elem in elements:
            for bad in forbidden_patterns:
                if bad in elem.lower():
                    issues.append(("HIGH", f"Слабкий криптографічний алгоритм у '{category}': {elem}"))

    return issues


def main():
    print("=== Аудит конфігурації OpenSSH Daemon (sshd -T) ===")
    cfg = get_sshd_config()
    issues = audit_config(cfg)

    if not issues:
        print("[✓] Конфігурація sshd відповідає суворому профілю безпеки. Дефектів не виявлено.")
        sys.exit(0)

    print(f"[!] Знайдено зауважень: {len(issues)}\n")
    for sev, msg in issues:
        print(f"  [{sev:8s}] {msg}")

    print("\nРекомендація: додайте безпечний профіль у /etc/ssh/sshd_config.d/99-hardening.conf")
    sys.exit(1)


if __name__ == "__main__":
    main()
