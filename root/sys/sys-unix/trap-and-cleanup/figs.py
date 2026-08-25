#!/usr/bin/env python3
"""
Генерація SVG-діаграм для теми trap-and-cleanup.
Всі діаграми мають чіткі viewBox, гармонійну палітру та адаптовані розміри без накладання тексту.
"""

import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_signal_flow():
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 940 500" width="100%" height="100%" style="background:#0f172a; font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, sans-serif;">
  <defs>
    <linearGradient id="headerGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#38bdf8" />
      <stop offset="100%" stop-color="#818cf8" />
    </linearGradient>
    <linearGradient id="boxGrad1" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#1e293b" />
      <stop offset="100%" stop-color="#334155" />
    </linearGradient>
    <linearGradient id="alertGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#7f1d1d" />
      <stop offset="100%" stop-color="#991b1b" />
    </linearGradient>
    <linearGradient id="actionGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#065f46" />
      <stop offset="100%" stop-color="#047857" />
    </linearGradient>
    <linearGradient id="kernelGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#312e81" />
      <stop offset="100%" stop-color="#4338ca" />
    </linearGradient>
    <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#38bdf8" />
    </marker>
    <marker id="arrowRed" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#f87171" />
    </marker>
    <marker id="arrowGreen" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#34d399" />
    </marker>
    <filter id="shadow" x="-5%" y="-5%" width="110%" height="115%" filterUnits="userSpaceOnUse">
      <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#000000" flood-opacity="0.4" />
    </filter>
  </defs>

  <!-- Заголовок діаграми -->
  <text x="470" y="32" fill="url(#headerGrad)" font-size="20" font-weight="700" text-anchor="middle">Життєвий цикл сигналу: перехоплення, очищення та Proper Re-raising</text>

  <!-- Шкала часу зверху -->
  <line x1="60" y1="65" x2="880" y2="65" stroke="#475569" stroke-width="2" stroke-dasharray="6 4" />
  <text x="70" y="58" fill="#94a3b8" font-size="12" font-weight="600">t = 0 (Старт)</text>
  <text x="470" y="58" fill="#94a3b8" font-size="12" font-weight="600" text-anchor="middle">Зовнішній сигнал</text>
  <text x="870" y="58" fill="#94a3b8" font-size="12" font-weight="600" text-anchor="end">t = кінець (128+N)</text>

  <!-- Блок 1: Нормальне виконання -->
  <g filter="url(#shadow)">
    <rect x="50" y="90" width="180" height="120" rx="10" fill="url(#boxGrad1)" stroke="#38bdf8" stroke-width="1.5" />
    <text x="140" y="118" fill="#38bdf8" font-size="14" font-weight="700" text-anchor="middle">1. Виконання коду</text>
    <text x="140" y="142" fill="#e2e8f0" font-size="12" text-anchor="middle">Створення $TMPDIR</text>
    <text x="140" y="162" fill="#e2e8f0" font-size="12" text-anchor="middle">Захоплення flock</text>
    <text x="140" y="184" fill="#94a3b8" font-size="11" text-anchor="middle">trap cleanup EXIT</text>
  </g>

  <!-- Стрілка 1 -> Сигнал -->
  <path d="M 230 150 L 290 150" stroke="#38bdf8" stroke-width="2" marker-end="url(#arrow)" />

  <!-- Блок 2: Прибуття сигналу -->
  <g filter="url(#shadow)">
    <rect x="300" y="90" width="180" height="120" rx="10" fill="url(#alertGrad)" stroke="#f87171" stroke-width="1.5" />
    <text x="390" y="118" fill="#fca5a5" font-size="14" font-weight="700" text-anchor="middle">2. Прибуття SIGINT</text>
    <text x="390" y="142" fill="#fef2f2" font-size="12" text-anchor="middle">Ctrl+C / kill -2 $$</text>
    <text x="390" y="164" fill="#fca5a5" font-size="12" text-anchor="middle">Ядро шле сигнал</text>
    <text x="390" y="186" fill="#cbd5e1" font-size="11" text-anchor="middle">Shell виявляє прапорець</text>
  </g>

  <!-- Стрілка 2 -> Пастка -->
  <path d="M 480 150 L 540 150" stroke="#f87171" stroke-width="2" marker-end="url(#arrowRed)" />

  <!-- Блок 3: Обробник пастки -->
  <g filter="url(#shadow)">
    <rect x="550" y="90" width="180" height="120" rx="10" fill="url(#boxGrad1)" stroke="#a855f7" stroke-width="1.5" />
    <text x="640" y="118" fill="#c084fc" font-size="14" font-weight="700" text-anchor="middle">3. Скидання пастки</text>
    <text x="640" y="142" fill="#f3e8ff" font-size="12" text-anchor="middle">trap - INT</text>
    <text x="640" y="164" fill="#e2e8f0" font-size="12" text-anchor="middle">Відновлення SIG_DFL</text>
    <text x="640" y="186" fill="#cbd5e1" font-size="11" text-anchor="middle">kill -s INT $$</text>
  </g>

  <!-- Стрілка 3 -> Re-raise вниз -->
  <path d="M 640 210 L 640 255" stroke="#c084fc" stroke-width="2" marker-end="url(#arrow)" />

  <!-- Блок 4: EXIT Trap -->
  <g filter="url(#shadow)">
    <rect x="550" y="265" width="180" height="130" rx="10" fill="url(#actionGrad)" stroke="#34d399" stroke-width="1.5" />
    <text x="640" y="293" fill="#6ee7b7" font-size="14" font-weight="700" text-anchor="middle">4. Хук trap EXIT</text>
    <text x="640" y="317" fill="#ecfdf5" font-size="12" text-anchor="middle">Гарантований виклик</text>
    <text x="640" y="339" fill="#a7f3d0" font-size="12" text-anchor="middle">rm -rf "$TEMP_DIR"</text>
    <text x="640" y="361" fill="#a7f3d0" font-size="12" text-anchor="middle">kill background jobs</text>
    <text x="640" y="383" fill="#cbd5e1" font-size="11" text-anchor="middle">unlock &amp; cleanup</text>
  </g>

  <!-- Стрілка 4 -> Батьківський процес -->
  <path d="M 550 330 L 290 330" stroke="#34d399" stroke-width="2" marker-end="url(#arrowGreen)" />

  <!-- Блок 5: Смерть від сигналу та реакція батька -->
  <g filter="url(#shadow)">
    <rect x="50" y="265" width="230" height="130" rx="10" fill="url(#kernelGrad)" stroke="#818cf8" stroke-width="1.5" />
    <text x="165" y="293" fill="#a5b4fc" font-size="14" font-weight="700" text-anchor="middle">5. Статус ядра: 128+SIG</text>
    <text x="165" y="317" fill="#ffffff" font-size="12" text-anchor="middle">Смерть від SIGINT (130)</text>
    <text x="165" y="339" fill="#c7d2fe" font-size="12" text-anchor="middle">WIFSIGNALED = true</text>
    <text x="165" y="361" fill="#c7d2fe" font-size="12" text-anchor="middle">WTERMSIG = SIGINT</text>
    <text x="165" y="383" fill="#38bdf8" font-size="11" font-weight="600" text-anchor="middle">Батько коректно зупиняє цикл</text>
  </g>

  <!-- Порівняльна плашка внизу: два окремі рядки без накладання -->
  <rect x="50" y="415" width="840" height="65" rx="8" fill="#1e293b" stroke="#334155" />
  
  <!-- Рядок 1: Хибний підхід -->
  <text x="70" y="438" fill="#f87171" font-size="12" font-weight="700">✖ Хибний exit 1:</text>
  <text x="180" y="438" fill="#94a3b8" font-size="12">WIFEXITED=true, маскує сигнал; зовнішній цикл for/while продовжує роботу.</text>

  <!-- Рядок 2: Правильний підхід -->
  <text x="70" y="462" fill="#34d399" font-size="12" font-weight="700">✓ Re-raising:</text>
  <text x="180" y="462" fill="#38bdf8" font-size="12">WIFSIGNALED=true, код 130/143; зовнішній оркестратор або shell зупиняє конвеєр.</text>
</svg>
'''
    with open(os.path.join(OUTPUT_DIR, "trap-signal-flow-and-re-raise.svg"), "w", encoding="utf-8") as f:
        f.write(svg.strip())

def generate_cleanup_stack():
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 920 460" width="100%" height="100%" style="background:#0f172a; font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, sans-serif;">
  <defs>
    <linearGradient id="titleGrad2" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#6ee7b7" />
      <stop offset="100%" stop-color="#38bdf8" />
    </linearGradient>
    <linearGradient id="cardGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#1e293b" />
      <stop offset="100%" stop-color="#334155" />
    </linearGradient>
    <linearGradient id="stackGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#1e1b4b" />
      <stop offset="100%" stop-color="#312e81" />
    </linearGradient>
    <marker id="arrowBlue2" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#38bdf8" />
    </marker>
    <marker id="arrowGreen2" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#34d399" />
    </marker>
    <marker id="arrowOrange" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#fb923c" />
    </marker>
    <filter id="shadow2" x="-5%" y="-5%" width="110%" height="115%" filterUnits="userSpaceOnUse">
      <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#000000" flood-opacity="0.4" />
    </filter>
  </defs>

  <!-- Заголовок -->
  <text x="460" y="32" fill="url(#titleGrad2)" font-size="20" font-weight="700" text-anchor="middle">Архітектура LIFO-стека очищення ресурсів (динамічний defer)</text>

  <!-- Ліва колонка: Прогрес скрипту (Push) -->
  <g filter="url(#shadow2)">
    <rect x="40" y="65" width="370" height="365" rx="10" fill="url(#cardGrad)" stroke="#38bdf8" stroke-width="1.5" />
    <text x="225" y="95" fill="#38bdf8" font-size="16" font-weight="700" text-anchor="middle">Фаза ініціалізації: Реєстрація (Push)</text>
    
    <!-- Крок 1 -->
    <rect x="60" y="115" width="330" height="60" rx="6" fill="#0f172a" stroke="#475569" />
    <text x="75" y="138" fill="#93c5fd" font-size="13" font-weight="600">1. Створення каталогу</text>
    <text x="75" y="158" fill="#e2e8f0" font-size="12">DIR=$(mktemp -d); defer_add "rm -rf $DIR"</text>

    <!-- Крок 2 -->
    <rect x="60" y="190" width="330" height="60" rx="6" fill="#0f172a" stroke="#475569" />
    <text x="75" y="213" fill="#93c5fd" font-size="13" font-weight="600">2. Блокування процесу</text>
    <text x="75" y="233" fill="#e2e8f0" font-size="12">exec 200&gt;app.lock; defer_add "exec 200&gt;&amp;-"</text>

    <!-- Крок 3 -->
    <rect x="60" y="265" width="330" height="60" rx="6" fill="#0f172a" stroke="#475569" />
    <text x="75" y="288" fill="#93c5fd" font-size="13" font-weight="600">3. Монтування сховища</text>
    <text x="75" y="308" fill="#e2e8f0" font-size="12">mount /dev/sdb1 /mnt; defer_add "umount /mnt"</text>

    <!-- Крок 4 -->
    <rect x="60" y="340" width="330" height="60" rx="6" fill="#0f172a" stroke="#475569" />
    <text x="75" y="363" fill="#93c5fd" font-size="13" font-weight="600">4. Запуск фонового демона</text>
    <text x="75" y="383" fill="#e2e8f0" font-size="12">daemon &amp; PID=$!; defer_add "kill $PID"</text>
  </g>

  <!-- Центральна стрілка виклику EXIT / сигналів -->
  <path d="M 420 240 L 500 240" stroke="#fb923c" stroke-width="3" marker-end="url(#arrowOrange)" />
  <text x="460" y="225" fill="#fb923c" font-size="13" font-weight="700" text-anchor="middle">EXIT</text>
  <text x="460" y="260" fill="#fed7aa" font-size="11" text-anchor="middle">або сигнал</text>

  <!-- Права колонка: LIFO Розгортання (Pop & Execute) -->
  <g filter="url(#shadow2)">
    <rect x="510" y="65" width="370" height="365" rx="10" fill="url(#stackGrad)" stroke="#a855f7" stroke-width="1.5" />
    <text x="695" y="95" fill="#c084fc" font-size="16" font-weight="700" text-anchor="middle">Фаза очищення: Зворотний порядок (LIFO)</text>

    <!-- Стек 1 (Останній доданий - перший виконаний) -->
    <rect x="530" y="115" width="330" height="60" rx="6" fill="#0f172a" stroke="#c084fc" />
    <text x="545" y="138" fill="#f43f5e" font-size="13" font-weight="700">[Виклик 1] Зупинка демона</text>
    <text x="545" y="158" fill="#a7f3d0" font-size="12">kill $PID &amp;&amp; wait $PID 2&gt;/dev/null</text>

    <!-- Стек 2 -->
    <rect x="530" y="190" width="330" height="60" rx="6" fill="#0f172a" stroke="#a855f7" />
    <text x="545" y="213" fill="#fb923c" font-size="13" font-weight="700">[Виклик 2] Демонтування</text>
    <text x="545" y="233" fill="#a7f3d0" font-size="12">umount -l /mnt</text>

    <!-- Стек 3 -->
    <rect x="530" y="265" width="330" height="60" rx="6" fill="#0f172a" stroke="#818cf8" />
    <text x="545" y="288" fill="#facc15" font-size="13" font-weight="700">[Виклик 3] Закриття дескриптора</text>
    <text x="545" y="308" fill="#a7f3d0" font-size="12">exec 200&gt;&amp;- (звільнення замка)</text>

    <!-- Стек 4 (Перший доданий - останній виконаний) -->
    <rect x="530" y="340" width="330" height="60" rx="6" fill="#0f172a" stroke="#38bdf8" />
    <text x="545" y="363" fill="#38bdf8" font-size="13" font-weight="700">[Виклик 4] Видалення каталогу</text>
    <text x="545" y="383" fill="#a7f3d0" font-size="12">rm -rf "$DIR"</text>
  </g>
</svg>
'''
    with open(os.path.join(OUTPUT_DIR, "cleanup-stack-architecture.svg"), "w", encoding="utf-8") as f:
        f.write(svg.strip())

def generate_mktemp_security():
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 920 440" width="100%" height="100%" style="background:#0f172a; font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, sans-serif;">
  <defs>
    <linearGradient id="titleGrad3" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#f87171" />
      <stop offset="100%" stop-color="#fbbf24" />
    </linearGradient>
    <linearGradient id="vulnGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#450a0a" />
      <stop offset="100%" stop-color="#7f1d1d" />
    </linearGradient>
    <linearGradient id="safeGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#064e3b" />
      <stop offset="100%" stop-color="#065f46" />
    </linearGradient>
    <marker id="arrowRed3" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#f87171" />
    </marker>
    <marker id="arrowGreen3" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#34d399" />
    </marker>
    <filter id="shadow3" x="-5%" y="-5%" width="110%" height="115%" filterUnits="userSpaceOnUse">
      <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#000000" flood-opacity="0.4" />
    </filter>
  </defs>

  <text x="460" y="32" fill="url(#titleGrad3)" font-size="20" font-weight="700" text-anchor="middle">Безпека у /tmp: Вразливість фіксованих шляхів проти атомарного mktemp -d</text>

  <!-- Лівий блок: Вразливий підхід -->
  <g filter="url(#shadow3)">
    <rect x="40" y="65" width="400" height="345" rx="10" fill="url(#vulnGrad)" stroke="#f87171" stroke-width="1.5" />
    <text x="240" y="95" fill="#fca5a5" font-size="16" font-weight="700" text-anchor="middle">Вразливо: Передбачуваний шлях у /tmp</text>

    <!-- Схема атаки -->
    <rect x="60" y="115" width="360" height="70" rx="6" fill="#1e293b" stroke="#64748b" />
    <text x="75" y="138" fill="#f87171" font-size="13" font-weight="600">Код: echo "data" &gt; /tmp/job.$$.tmp</text>
    <text x="75" y="162" fill="#cbd5e1" font-size="12">PID передбачуваний; файл створюється без O_EXCL</text>

    <rect x="60" y="200" width="360" height="85" rx="6" fill="#1e293b" stroke="#f87171" />
    <text x="75" y="223" fill="#fca5a5" font-size="13" font-weight="600">Атака Symlink Race (TOCTOU):</text>
    <text x="75" y="245" fill="#e2e8f0" font-size="12">Зловмисник створює лінк:</text>
    <text x="75" y="267" fill="#fbbf24" font-family="monospace" font-size="12">ln -s /etc/shadow /tmp/job.1234.tmp</text>

    <rect x="60" y="300" width="360" height="90" rx="6" fill="#2d0606" stroke="#ef4444" />
    <text x="75" y="323" fill="#f87171" font-size="13" font-weight="700">Наслідки:</text>
    <text x="75" y="345" fill="#fecaca" font-size="12">• Перезапис системних критичних файлів</text>
    <text x="75" y="367" fill="#fecaca" font-size="12">• Підвищення привілеїв або відмова у доступі</text>
  </g>

  <!-- Правий блок: Безпечний підхід -->
  <g filter="url(#shadow3)">
    <rect x="480" y="65" width="400" height="345" rx="10" fill="url(#safeGrad)" stroke="#34d399" stroke-width="1.5" />
    <text x="680" y="95" fill="#86efac" font-size="16" font-weight="700" text-anchor="middle">Безпечно: Приватний каталог mktemp -d</text>

    <!-- Безпечна схема -->
    <rect x="500" y="115" width="360" height="70" rx="6" fill="#1e293b" stroke="#64748b" />
    <text x="515" y="138" fill="#34d399" font-size="13" font-weight="600">Код: WORK_DIR=$(mktemp -d)</text>
    <text x="515" y="162" fill="#cbd5e1" font-size="12">Атомарний mkdir() з маскою прав 0700</text>

    <rect x="500" y="200" width="360" height="85" rx="6" fill="#1e293b" stroke="#34d399" />
    <text x="515" y="223" fill="#86efac" font-size="13" font-weight="600">Бар'єр захисту ядра:</text>
    <text x="515" y="245" fill="#e2e8f0" font-size="12">Тільки власник процесу має права rwx.</text>
    <text x="515" y="267" fill="#a7f3d0" font-size="12">Чужі користувачі не можуть навіть прочитати вміст.</text>

    <rect x="500" y="300" width="360" height="90" rx="6" fill="#063828" stroke="#10b981" />
    <text x="515" y="323" fill="#6ee7b7" font-size="13" font-weight="700">Гарантії:</text>
    <text x="515" y="345" fill="#d1fae5" font-size="12">• Повна ізоляція від symlink-атак</text>
    <text x="515" y="367" fill="#d1fae5" font-size="12">• Одне просте прибирання: rm -rf "$WORK_DIR"</text>
  </g>
</svg>
'''
    with open(os.path.join(OUTPUT_DIR, "tmp-symlink-race-attack.svg"), "w", encoding="utf-8") as f:
        f.write(svg.strip())

if __name__ == "__main__":
    generate_signal_flow()
    generate_cleanup_stack()
    generate_mktemp_security()
    print("Усі фігури успішно згенеровано.")
