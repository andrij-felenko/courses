import re
import subprocess

# Створення дочірнього процесу esptool з перенаправленням stdout
process = subprocess.Popen(
    ["esptool.py", "--port", "COM3", "write_flash", "0x0", "firmware.bin"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1
)

# Регулярний вираз для витягування відсотка виконання
progress_pattern = re.compile(r'\((\d+)\s*%\)')

# Порядковий розбір текстового потоку в реальному часі
for line in iter(process.stdout.readline, ''):
    match = progress_pattern.search(line)
    if match:
        percentage = int(match.group(1))
        # Оновлення віджета смуги прогресу у головному потоці GUI
        update_progress_bar(percentage)
