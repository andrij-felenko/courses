"""
Модуль агрегації результатів митного аудиту та публікації звіту в Git-платформу.
Формує структурований Markdown-звіт і виконує виклик REST API GitHub / GitLab.
"""

import json
import os
import urllib.error
import urllib.request
from typing import Optional

from models import CheckResult, Severity


class GitPRReporter:
    """
    Генератор звітів та інтеграційний агент для публікації статусу приймання в пул-реквесті.
    """

    def __init__(self, api_token: Optional[str] = None, pr_comments_url: Optional[str] = None):
        self.api_token = api_token or os.environ.get("GITHUB_TOKEN") or os.environ.get("GITLAB_TOKEN")
        self.pr_comments_url = pr_comments_url or os.environ.get("PR_COMMENTS_URL")

    def generate_markdown_report(self, results: list[CheckResult], commit_sha: str = "HEAD") -> str:
        """
        Складає наочний підсумковий звіт у форматі Markdown для автоматичного коментування в PR.
        """
        total_errors = sum(r.error_count for r in results)
        total_warnings = sum(r.warning_count for r in results)
        overall_passed = total_errors == 0

        status_banner = (
            "## 🛡️ Митний контур приймання: ✅ СХВАЛЕНО ДО ЗЛИТТЯ\n\n"
            "> Усі архітектурні, ліцензійні та тестові інваріанти замовника успішно виконано."
            if overall_passed
            else
            "## 🛡️ Митний контур приймання: ❌ ЗЛИТТЯ ЗАБЛОКОВАНО\n\n"
            f"> Виявлено **{total_errors}** критичних порушень критеріїв Definition of Done. "
            "Пул-реквест підрядника не може бути прийнятий до усунення наведених дефектів."
        )

        md = [status_banner, f"\n**Коміт:** `{commit_sha}`\n"]
        md.append("### 📊 Зведена таблиця перевірок якості\n")
        md.append("| Інспектор якості | Статус | Критичні помилки | Застереження | Короткий підсумок |")
        md.append("| :--- | :---: | :---: | :---: | :--- |")

        for r in results:
            icon = "✅ PASS" if r.passed else "❌ FAIL"
            md.append(f"| **{r.check_name}** | {icon} | {r.error_count} | {r.warning_count} | {r.summary} |")

        all_violations = [v for r in results for v in r.violations]
        if all_violations:
            md.append("\n### 🔍 Деталізований реєстр виявлених порушень\n")
            md.append("| Рівень | Правило | Файл : Рядок | Опис розходження |")
            md.append("| :---: | :--- | :--- | :--- |")
            for v in all_violations:
                sev_badge = "🔴 ERROR" if v.severity == Severity.ERROR else "🟡 WARN"
                loc = f"`{v.file_path}:{v.line_number}`"
                md.append(f"| {sev_badge} | `{v.rule_name}` | {loc} | {v.message} |")

            md.append("\n> **Вказівка підряднику:** Виправте порушення у своїй локальній гілці "
                      "та оновіть пул-реквест. Повторний аудит запуститься автоматично.")

        return "\n".join(md)

    def post_comment_to_pr(self, report_markdown: str) -> bool:
        """
        Відправляє звіт через REST API Git-платформи (GitHub / GitLab / Gitea).
        """
        if not self.pr_comments_url:
            print("[INFO] PR_COMMENTS_URL не задано. Публікація в мережу пропущена.")
            return False

        if not self.api_token:
            print("[WARN] API токен відсутній. Неможливо автентифікувати запит до Git-сервісу.")
            return False

        payload = json.dumps({"body": report_markdown}).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_token}",
            "User-Agent": "Customs-Gate-CI/1.0",
        }

        req = urllib.request.Request(self.pr_comments_url, data=payload, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                status = resp.status
                if status in {200, 201}:
                    print(f"[SUCCESS] Звіт успішно опубліковано у коментарях PR (HTTP {status}).")
                    return True
                print(f"[WARN] Сервер повернув статус {status} при публікації звіту.")
                return False
        except urllib.error.URLError as err:
            print(f"[ERROR] Збій відправки коментаря в Git API: {err}")
            return False

    def save_report(self, report_markdown: str, output_path: str = "customs_report.md") -> None:
        """Зберігає згенерований звіт у локальний Markdown-файл артефакту CI."""
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report_markdown)
        print(f"[INFO] Звіт збережено локально: {output_path}")
