import os

def render():
    fig_dir = os.path.dirname(os.path.abspath(__file__))
    img_dir = os.path.join(fig_dir, 'img')
    os.makedirs(img_dir, exist_ok=True)
    
    # 1. Architecture diagram
    svg_arch = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 540">
    <rect width="100%" height="100%" fill="#ffffff" />
    <defs>
        <marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
            <path d="M0,0 L0,6 L9,3 z" fill="#333" />
        </marker>
    </defs>
    <g font-family="sans-serif" font-size="13">
        <!-- Hardware / Firmware Box -->
        <rect x="30" y="20" width="740" height="100" fill="#f8f9fa" stroke="#495057" stroke-width="2" rx="8"/>
        <text x="50" y="45" font-weight="bold" fill="#212529">Апаратне забезпечення та прошивка (BIOS / ACPI AML)</text>
        
        <rect x="50" y="60" width="210" height="46" fill="#e9ecef" stroke="#6c757d" stroke-width="1.5" rx="4"/>
        <text x="155" y="88" text-anchor="middle" font-weight="bold" fill="#343a40">ACPI пристрій PNP0C14</text>
        
        <rect x="290" y="60" width="220" height="46" fill="#e9ecef" stroke="#6c757d" stroke-width="1.5" rx="4"/>
        <text x="400" y="79" text-anchor="middle" font-weight="bold" fill="#343a40">Таблиця _WDG (GUID Guidance)</text>
        <text x="400" y="96" text-anchor="middle" font-size="11" fill="#495057">20-байтові блоки mapping-у</text>
        
        <rect x="540" y="60" width="210" height="46" fill="#e9ecef" stroke="#6c757d" stroke-width="1.5" rx="4"/>
        <text x="645" y="79" text-anchor="middle" font-weight="bold" fill="#343a40">AML методи (WMxx, WQxx)</text>
        <text x="645" y="96" text-anchor="middle" font-size="11" fill="#495057">та події (_WED)</text>

        <!-- Kernel Space Box -->
        <rect x="30" y="160" width="740" height="200" fill="#f0f4f8" stroke="#1864ab" stroke-width="2" rx="8"/>
        <text x="50" y="185" font-weight="bold" fill="#0b7285">Простір ядра Linux (Linux Kernel Space)</text>
        
        <rect x="50" y="198" width="700" height="50" fill="#d0ebff" stroke="#1c7ed6" stroke-width="1.5" rx="4"/>
        <text x="400" y="220" text-anchor="middle" font-weight="bold" fill="#1864ab">Підсистема WMI Core (drivers/platform/x86/wmi.c)</text>
        <text x="400" y="238" text-anchor="middle" font-size="11" fill="#1c7ed6">Реєстрація wmi_bus_type, парсинг _WDG, створення wmi_device для кожного GUID</text>
        
        <!-- Vendor WMI Drivers -->
        <rect x="50" y="265" width="210" height="85" fill="#e6fcf5" stroke="#0ca678" stroke-width="1.5" rx="4"/>
        <text x="155" y="285" text-anchor="middle" font-weight="bold" fill="#087f5b">dell-wmi / hp-wmi</text>
        <text x="155" y="303" text-anchor="middle" font-size="11" fill="#0ca678">Гарячі клавіші Fn</text>
        <text x="155" y="320" text-anchor="middle" font-size="11" fill="#0ca678">firmware_attributes</text>
        <text x="155" y="337" text-anchor="middle" font-size="11" fill="#0ca678">rfkill hw switch</text>

        <rect x="295" y="265" width="210" height="85" fill="#e6fcf5" stroke="#0ca678" stroke-width="1.5" rx="4"/>
        <text x="400" y="285" text-anchor="middle" font-weight="bold" fill="#087f5b">asus-wmi / lenovo-wmi</text>
        <text x="400" y="303" text-anchor="middle" font-size="11" fill="#0ca678">Профілі вентиляторів</text>
        <text x="400" y="320" text-anchor="middle" font-size="11" fill="#0ca678">Поріг заряду АКБ</text>
        <text x="400" y="337" text-anchor="middle" font-size="11" fill="#0ca678">RGB/LED підсвічування</text>

        <rect x="540" y="265" width="210" height="85" fill="#e6fcf5" stroke="#0ca678" stroke-width="1.5" rx="4"/>
        <text x="645" y="285" text-anchor="middle" font-weight="bold" fill="#087f5b">wmi-sysfs / bmof</text>
        <text x="645" y="303" text-anchor="middle" font-size="11" fill="#0ca678">Експорт BMOF буферів</text>
        <text x="645" y="320" text-anchor="middle" font-size="11" fill="#0ca678">Прямий доступ до data block</text>
        <text x="645" y="337" text-anchor="middle" font-size="11" fill="#0ca678">через sysfs атрибути</text>

        <!-- User Space Box -->
        <rect x="30" y="390" width="740" height="135" fill="#fff9db" stroke="#f59f00" stroke-width="2" rx="8"/>
        <text x="400" y="415" text-anchor="middle" font-weight="bold" fill="#f59f00">Простір користувача (User Space)</text>
        
        <rect x="50" y="440" width="210" height="60" fill="#fff3bf" stroke="#f59f00" stroke-width="1.5" rx="4"/>
        <text x="155" y="468" text-anchor="middle" font-weight="bold" fill="#e67700">Subsystem Input (/dev/input)</text>
        <text x="155" y="486" text-anchor="middle" font-size="11" fill="#e67700">evdev події клавіш</text>

        <rect x="295" y="440" width="210" height="60" fill="#fff3bf" stroke="#f59f00" stroke-width="1.5" rx="4"/>
        <text x="400" y="468" text-anchor="middle" font-weight="bold" fill="#e67700">Sysfs Nodes (/sys/bus/wmi/...)</text>
        <text x="400" y="486" text-anchor="middle" font-size="11" fill="#e67700">атрибути керування</text>

        <rect x="540" y="440" width="210" height="60" fill="#fff3bf" stroke="#f59f00" stroke-width="1.5" rx="4"/>
        <text x="645" y="468" text-anchor="middle" font-weight="bold" fill="#e67700">Утиліти bmfdec / fwts</text>
        <text x="645" y="486" text-anchor="middle" font-size="11" fill="#e67700">декомпіляція BMOF</text>

        <!-- Arrows (Connecting Hardware to Kernel, and Kernel to User Space) -->
        <path d="M 400 120 L 400 198" stroke="#333" stroke-width="2" marker-end="url(#arrow)"/>
        <path d="M 155 248 L 155 265" stroke="#333" stroke-width="1.5" marker-end="url(#arrow)"/>
        <path d="M 400 248 L 400 265" stroke="#333" stroke-width="1.5" marker-end="url(#arrow)"/>
        <path d="M 645 248 L 645 265" stroke="#333" stroke-width="1.5" marker-end="url(#arrow)"/>
        
        <path d="M 155 350 L 155 440" stroke="#333" stroke-width="1.5" stroke-dasharray="4,4" marker-end="url(#arrow)"/>
        <path d="M 645 350 L 645 440" stroke="#333" stroke-width="1.5" stroke-dasharray="4,4" marker-end="url(#arrow)"/>
    </g>
</svg>"""

    with open(os.path.join(img_dir, 'wmi-architecture.svg'), 'w', encoding='utf-8') as f:
        f.write(svg_arch)

    # 2. Event sequence diagram
    svg_seq = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 480">
    <rect width="100%" height="100%" fill="#ffffff" />
    <defs>
        <marker id="arrow2" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
            <path d="M0,0 L0,6 L9,3 z" fill="#1c7ed6" />
        </marker>
    </defs>
    <g font-family="sans-serif" font-size="12">
        <!-- Vertical lifelines -->
        <!-- 1. EC/HW -->
        <rect x="50" y="30" width="120" height="35" fill="#e9ecef" stroke="#495057" stroke-width="1.5" rx="4"/>
        <text x="110" y="52" text-anchor="middle" font-weight="bold" fill="#212529">EC / Hardware</text>
        <line x1="110" y1="65" x2="110" y2="440" stroke="#adb5bd" stroke-width="1.5" stroke-dasharray="4,4"/>

        <!-- 2. ACPI Core -->
        <rect x="230" y="30" width="120" height="35" fill="#d0ebff" stroke="#1c7ed6" stroke-width="1.5" rx="4"/>
        <text x="290" y="52" text-anchor="middle" font-weight="bold" fill="#1864ab">ACPI Core</text>
        <line x1="290" y1="65" x2="290" y2="440" stroke="#adb5bd" stroke-width="1.5" stroke-dasharray="4,4"/>

        <!-- 3. wmi.ko -->
        <rect x="410" y="30" width="120" height="35" fill="#d0ebff" stroke="#1c7ed6" stroke-width="1.5" rx="4"/>
        <text x="470" y="52" text-anchor="middle" font-weight="bold" fill="#1864ab">wmi.ko</text>
        <line x1="470" y1="65" x2="470" y2="440" stroke="#adb5bd" stroke-width="1.5" stroke-dasharray="4,4"/>

        <!-- 4. Vendor Driver -->
        <rect x="580" y="30" width="160" height="35" fill="#e6fcf5" stroke="#0ca678" stroke-width="1.5" rx="4"/>
        <text x="660" y="52" text-anchor="middle" font-weight="bold" fill="#087f5b">dell-wmi / asus-wmi</text>
        <line x1="660" y1="65" x2="660" y2="440" stroke="#adb5bd" stroke-width="1.5" stroke-dasharray="4,4"/>

        <!-- Sequence Steps -->
        <!-- Step 1 -->
        <path d="M 110 95 L 290 95" stroke="#1c7ed6" stroke-width="1.5" marker-end="url(#arrow2)"/>
        <text x="200" y="88" text-anchor="middle" font-weight="bold" fill="#1864ab">1. SCI Interrupt (Fn-key press)</text>

        <!-- Step 2 -->
        <path d="M 290 140 L 470 140" stroke="#1c7ed6" stroke-width="1.5" marker-end="url(#arrow2)"/>
        <text x="380" y="133" text-anchor="middle" font-weight="bold" fill="#1864ab">2. Notify(PNP0C14, 0x80)</text>

        <!-- Step 3 -->
        <path d="M 470 185 L 290 185" stroke="#1c7ed6" stroke-width="1.5" marker-end="url(#arrow2)"/>
        <text x="380" y="178" text-anchor="middle" font-weight="bold" fill="#1864ab">3. Виклик _WED(0x80)</text>

        <!-- Step 4 -->
        <path d="M 290 230 L 470 230" stroke="#1c7ed6" stroke-width="1.5" marker-end="url(#arrow2)"/>
        <text x="380" y="223" text-anchor="middle" font-weight="bold" fill="#1864ab">4. Повернення event_data (скан-код)</text>

        <!-- Step 5 -->
        <path d="M 470 275 L 660 275" stroke="#1c7ed6" stroke-width="1.5" marker-end="url(#arrow2)"/>
        <text x="565" y="268" text-anchor="middle" font-weight="bold" fill="#1864ab">5. driver->notify(wdev, obj)</text>

        <!-- Step 6 -->
        <rect x="590" y="305" width="140" height="40" fill="#fff3bf" stroke="#f59f00" stroke-width="1" rx="4"/>
        <text x="660" y="322" text-anchor="middle" font-size="11" fill="#e67700">sparse_keymap_entry</text>
        <text x="660" y="337" text-anchor="middle" font-size="11" fill="#e67700">WMI code -> KEY_BRIGHTNESS</text>

        <!-- Step 7 -->
        <path d="M 660 375 L 660 415" stroke="#0ca678" stroke-width="1.5" marker-end="url(#arrow2)"/>
        <text x="660" y="430" text-anchor="middle" font-weight="bold" fill="#087f5b">6. input_report_key() -> /dev/input/eventX</text>
    </g>
</svg>"""

    with open(os.path.join(img_dir, 'wmi-event-sequence.svg'), 'w', encoding='utf-8') as f:
        f.write(svg_seq)

if __name__ == '__main__':
    render()
