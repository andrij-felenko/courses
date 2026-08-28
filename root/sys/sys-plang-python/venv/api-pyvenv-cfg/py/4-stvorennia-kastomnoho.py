import os
import subprocess
import venv
from pathlib import Path

class CorporateEnvBuilder(venv.EnvBuilder):
    """Спеціалізований конструктор venv для корпоративної інфраструктури."""
    
    def __init__(self, dev_tools=None, extra_index_url=None, **kwargs):
        super().__init__(**kwargs)
        self.dev_tools = dev_tools or ["pytest", "ruff", "mypy"]
        self.extra_index_url = extra_index_url

    def post_setup(self, context):
        """Хук розширення, що виконується після базового створення середовища."""
        # 1. Автоматична генерація файлу .gitignore
        gitignore = Path(context.env_dir) / ".gitignore"
        if not gitignore.exists():
            gitignore.write_text("*\n", encoding="utf-8")

        # 2. Налаштування корпоративного індексу пакетів pip.conf всередині venv
        if self.extra_index_url:
            pip_conf_dir = Path(context.env_dir)
            pip_conf = pip_conf_dir / "pip.conf"
            pip_conf.write_text(
                f"[global]\nextra-index-url = {self.extra_index_url}\n",
                encoding="utf-8"
            )

        # 3. Автоматичне встановлення базових інструментів тестування
        if self.with_pip and self.dev_tools:
            cmd = [context.executable, "-m", "pip", "install", "--quiet"] + self.dev_tools
            subprocess.run(cmd, check=True)
            print(f"Успішно встановлено корпоративний набір утиліт: {', '.join(self.dev_tools)}")

if __name__ == "__main__":
    builder = CorporateEnvBuilder(
        with_pip=True,
        prompt="corp-backend",
        extra_index_url="https://pypi.internal.corp/simple",
        dev_tools=["fastapi", "pytest", "ruff"]
    )
    builder.create("./.backend_env")
