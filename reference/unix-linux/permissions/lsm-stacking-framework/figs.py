import sys
import os

def render():
    out_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(out_dir, exist_ok=True)
    
    # Figure 1: LSM Architecture (DAC vs LSM hook interception)
    doc1 = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 480" width="800" height="480">
    <rect width="100%" height="100%" fill="#ffffff" />
    
    <!-- User Space -->
    <rect x="40" y="25" width="720" height="105" fill="#e8f0fe" stroke="#1a73e8" stroke-width="2" rx="8" />
    <text x="60" y="58" font-family="sans-serif" font-size="16" font-weight="bold" fill="#1a73e8">User Space (Простір користувача)</text>
    
    <rect x="250" y="72" width="300" height="45" fill="#ffffff" stroke="#1a73e8" stroke-width="1.5" rx="5" />
    <text x="400" y="100" font-family="sans-serif" font-size="14" text-anchor="middle" fill="#202124">Процес користувача (open, execve)</text>
    
    <!-- Syscall Boundary -->
    <text x="60" y="146" font-family="sans-serif" font-size="12" font-weight="bold" fill="#d93025">Системний виклик (Syscall Boundary)</text>
    <line x1="40" y1="158" x2="760" y2="158" stroke="#d93025" stroke-width="2" stroke-dasharray="6,4" />
    
    <!-- Kernel Space -->
    <rect x="40" y="170" width="720" height="290" fill="#f8f9fa" stroke="#5f6368" stroke-width="2" rx="8" />
    <text x="60" y="200" font-family="sans-serif" font-size="16" font-weight="bold" fill="#3c4043">Kernel Space (Простір ядра)</text>
    
    <!-- VFS DAC Check -->
    <rect x="80" y="240" width="220" height="70" fill="#e6f4ea" stroke="#137333" stroke-width="1.5" rx="6" />
    <text x="190" y="268" font-family="sans-serif" font-size="14" font-weight="bold" text-anchor="middle" fill="#137333">VFS / DAC Перевірка</text>
    <text x="190" y="290" font-family="sans-serif" font-size="12" text-anchor="middle" fill="#3c4043">(UID, GID, POSIX mode bits)</text>
    
    <!-- DAC Decision -->
    <rect x="110" y="345" width="160" height="40" fill="#fce8e6" stroke="#c5221f" stroke-width="1.5" rx="5" />
    <text x="190" y="370" font-family="sans-serif" font-size="12" text-anchor="middle" fill="#c5221f">DAC Відмова (-EACCES)</text>
    
    <!-- Arrow Syscall -> DAC -->
    <path d="M 400 117 L 400 215 L 190 215 L 190 240" fill="none" stroke="#202124" stroke-width="2" marker-end="url(#arrow)" />
    
    <!-- Arrow DAC fail -->
    <path d="M 190 310 L 190 345" fill="none" stroke="#c5221f" stroke-width="2" marker-end="url(#arrow-red)" />
    
    <!-- Arrow DAC pass -> LSM Hook -->
    <path d="M 300 275 L 380 275" fill="none" stroke="#137333" stroke-width="2" marker-end="url(#arrow-green)" />
    <text x="340" y="265" font-family="sans-serif" font-size="11" font-weight="bold" text-anchor="middle" fill="#137333">Дозволено</text>
    
    <!-- LSM Hook Infrastructure -->
    <rect x="380" y="240" width="340" height="70" fill="#fef7e0" stroke="#b06000" stroke-width="1.5" rx="6" />
    <text x="550" y="268" font-family="sans-serif" font-size="14" font-weight="bold" text-anchor="middle" fill="#b06000">LSM Hooks Framework</text>
    <text x="550" y="290" font-family="sans-serif" font-size="12" text-anchor="middle" fill="#3c4043">security_file_open(), security_inode_permission()</text>
    
    <!-- Active LSM Modules -->
    <rect x="380" y="345" width="340" height="85" fill="#f3e8fd" stroke="#7627bb" stroke-width="1.5" rx="6" />
    <text x="550" y="370" font-family="sans-serif" font-size="13" font-weight="bold" text-anchor="middle" fill="#7627bb">Активні модулі безпеки (Stacked Modules)</text>
    <text x="550" y="392" font-family="sans-serif" font-size="12" text-anchor="middle" fill="#3c4043">Yama → AppArmor → SELinux → BPF-LSM → Landlock</text>
    <text x="550" y="412" font-family="sans-serif" font-size="11" font-style="italic" text-anchor="middle" fill="#5f6368">(Логічне "І": кожен модуль має дозволити)</text>
    
    <!-- Arrow LSM Hook -> Modules -->
    <path d="M 550 310 L 550 345" fill="none" stroke="#b06000" stroke-width="2" marker-end="url(#arrow)" />
    
    <defs>
        <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#202124" />
        </marker>
        <marker id="arrow-red" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#c5221f" />
        </marker>
        <marker id="arrow-green" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#137333" />
        </marker>
    </defs>
    </svg>"""
    
    with open(os.path.join(out_dir, "lsm-architecture.svg"), 'w', encoding='utf-8') as f:
        f.write(doc1)
        
    # Figure 2: LSM Stacking Call Chain (Short-circuit execution)
    doc2 = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 940 380" width="940" height="380">
    <rect width="100%" height="100%" fill="#ffffff" />
    
    <text x="470" y="35" font-family="sans-serif" font-size="18" font-weight="bold" text-anchor="middle" fill="#202124">Ланцюг викликів LSM Stacking (Short-Circuit Semantics)</text>
    
    <!-- Entrance -->
    <rect x="30" y="80" width="140" height="60" fill="#e8f0fe" stroke="#1a73e8" stroke-width="2" rx="6" />
    <text x="100" y="107" font-family="sans-serif" font-size="13" font-weight="bold" text-anchor="middle" fill="#1a73e8">LSM Hook</text>
    <text x="100" y="125" font-family="sans-serif" font-size="11" text-anchor="middle" fill="#3c4043">security_file_open()</text>
    
    <!-- Arrow to M1 -->
    <path d="M 170 110 L 210 110" fill="none" stroke="#202124" stroke-width="2" marker-end="url(#arrow)" />
    
    <!-- Module 1: Yama -->
    <rect x="210" y="70" width="140" height="180" fill="#e6f4ea" stroke="#137333" stroke-width="2" rx="6" />
    <text x="280" y="98" font-family="sans-serif" font-size="14" font-weight="bold" text-anchor="middle" fill="#137333">1. Yama LSM</text>
    <line x1="220" y1="110" x2="340" y2="110" stroke="#137333" stroke-width="1" />
    <text x="280" y="140" font-family="sans-serif" font-size="12" text-anchor="middle" fill="#202124">Перевірка ptrace</text>
    <rect x="230" y="180" width="100" height="35" fill="#ffffff" stroke="#137333" stroke-width="1.5" rx="4" />
    <text x="280" y="202" font-family="sans-serif" font-size="12" font-weight="bold" text-anchor="middle" fill="#137333">ret = 0 (OK)</text>
    
    <!-- Arrow M1 -> M2 -->
    <path d="M 350 110 L 390 110" fill="none" stroke="#137333" stroke-width="2" marker-end="url(#arrow-green)" />
    
    <!-- Module 2: AppArmor -->
    <rect x="390" y="70" width="140" height="180" fill="#e6f4ea" stroke="#137333" stroke-width="2" rx="6" />
    <text x="460" y="98" font-family="sans-serif" font-size="14" font-weight="bold" text-anchor="middle" fill="#137333">2. AppArmor</text>
    <line x1="400" y1="110" x2="520" y2="110" stroke="#137333" stroke-width="1" />
    <text x="460" y="140" font-family="sans-serif" font-size="12" text-anchor="middle" fill="#202124">Перевірка шляху</text>
    <rect x="410" y="180" width="100" height="35" fill="#ffffff" stroke="#137333" stroke-width="1.5" rx="4" />
    <text x="460" y="202" font-family="sans-serif" font-size="12" font-weight="bold" text-anchor="middle" fill="#137333">ret = 0 (OK)</text>
    
    <!-- Arrow M2 -> M3 -->
    <path d="M 530 110 L 570 110" fill="none" stroke="#137333" stroke-width="2" marker-end="url(#arrow-green)" />
    
    <!-- Module 3: BPF-LSM (Denies) -->
    <rect x="570" y="70" width="140" height="180" fill="#fce8e6" stroke="#c5221f" stroke-width="2" rx="6" />
    <text x="640" y="98" font-family="sans-serif" font-size="14" font-weight="bold" text-anchor="middle" fill="#c5221f">3. BPF-LSM</text>
    <line x1="580" y1="110" x2="700" y2="110" stroke="#c5221f" stroke-width="1" />
    <text x="640" y="140" font-family="sans-serif" font-size="12" text-anchor="middle" fill="#202124">Кастомне правило</text>
    <rect x="585" y="180" width="110" height="35" fill="#ffffff" stroke="#c5221f" stroke-width="1.5" rx="4" />
    <text x="640" y="202" font-family="sans-serif" font-size="11" font-weight="bold" text-anchor="middle" fill="#c5221f">ret = -EACCES</text>
    
    <!-- Arrow M3 (blocked before Landlock) -->
    <line x1="710" y1="110" x2="750" y2="110" stroke="#dadce0" stroke-width="2" stroke-dasharray="4,4" />
    <text x="835" y="114" font-family="sans-serif" font-size="11" text-anchor="middle" fill="#70757a">(Landlock пропущено)</text>
    
    <!-- Return Arrow / Short Circuit -->
    <path d="M 640 250 L 640 350 L 100 350 L 100 140" fill="none" stroke="#c5221f" stroke-width="2" stroke-dasharray="5,4" marker-end="url(#arrow-red)" />
    <rect x="320" y="280" width="310" height="28" fill="#ffffff" stroke="#c5221f" stroke-width="1" rx="4" />
    <text x="475" y="299" font-family="sans-serif" font-size="12" font-weight="bold" text-anchor="middle" fill="#c5221f">Раннє завершення (Short-circuit): -EACCES</text>

    <defs>
        <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#202124" />
        </marker>
        <marker id="arrow-green" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#137333" />
        </marker>
        <marker id="arrow-red" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#c5221f" />
        </marker>
    </defs>
    </svg>"""
    
    with open(os.path.join(out_dir, "lsm-stacking.svg"), 'w', encoding='utf-8') as f:
        f.write(doc2)
        
    # Figure 3: Security Blob Memory Layout
    doc3 = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 360" width="800" height="360">
    <rect width="100%" height="100%" fill="#ffffff" />
    
    <text x="400" y="35" font-family="sans-serif" font-size="18" font-weight="bold" text-anchor="middle" fill="#202124">Розподіл пам'яті Security Blob (void *security)</text>
    
    <!-- Parent Struct: task_struct / inode -->
    <rect x="40" y="70" width="220" height="230" fill="#f8f9fa" stroke="#5f6368" stroke-width="2" rx="6" />
    <text x="150" y="98" font-family="sans-serif" font-size="14" font-weight="bold" text-anchor="middle" fill="#202124">struct inode / task_struct</text>
    <line x1="50" y1="110" x2="250" y2="110" stroke="#5f6368" stroke-width="1" />
    
    <text x="60" y="135" font-family="sans-serif" font-size="12" fill="#5f6368">unsigned long i_ino;</text>
    <text x="60" y="160" font-family="sans-serif" font-size="12" fill="#5f6368">umode_t i_mode;</text>
    <text x="60" y="185" font-family="sans-serif" font-size="12" fill="#5f6368">kuid_t i_uid;</text>
    
    <!-- The Security Pointer -->
    <rect x="55" y="210" width="190" height="45" fill="#e8f0fe" stroke="#1a73e8" stroke-width="2" rx="4" />
    <text x="150" y="238" font-family="sans-serif" font-size="13" font-weight="bold" text-anchor="middle" fill="#1a73e8">void *security;</text>
    
    <!-- Arrow pointer -> Blob -->
    <path d="M 245 232 L 320 232" fill="none" stroke="#1a73e8" stroke-width="2.5" marker-end="url(#arrow-blue)" />
    
    <!-- Continuous Memory Blob -->
    <rect x="320" y="70" width="440" height="230" fill="#fef7e0" stroke="#b06000" stroke-width="2" rx="6" />
    <text x="540" y="98" font-family="sans-serif" font-size="14" font-weight="bold" text-anchor="middle" fill="#b06000">Спільний блок пам'яті (Cumulative Security Blob)</text>
    <line x1="330" y1="110" x2="750" y2="110" stroke="#b06000" stroke-width="1" />
    
    <!-- SELinux Slot -->
    <rect x="340" y="130" width="90" height="130" fill="#e6f4ea" stroke="#137333" stroke-width="1.5" rx="4" />
    <text x="385" y="160" font-family="sans-serif" font-size="12" font-weight="bold" text-anchor="middle" fill="#137333">SELinux</text>
    <text x="385" y="185" font-family="sans-serif" font-size="11" text-anchor="middle" fill="#3c4043">Offset: 0</text>
    <text x="385" y="210" font-family="sans-serif" font-size="11" text-anchor="middle" fill="#5f6368">u32 sid</text>
    
    <!-- AppArmor Slot -->
    <rect x="440" y="130" width="100" height="130" fill="#e8f0fe" stroke="#1a73e8" stroke-width="1.5" rx="4" />
    <text x="490" y="160" font-family="sans-serif" font-size="12" font-weight="bold" text-anchor="middle" fill="#1a73e8">AppArmor</text>
    <text x="490" y="185" font-family="sans-serif" font-size="11" text-anchor="middle" fill="#3c4043">Offset: 4</text>
    <text x="490" y="210" font-family="sans-serif" font-size="11" text-anchor="middle" fill="#5f6368">label ptr</text>
    
    <!-- Landlock Slot -->
    <rect x="550" y="130" width="95" height="130" fill="#f3e8fd" stroke="#7627bb" stroke-width="1.5" rx="4" />
    <text x="597" y="160" font-family="sans-serif" font-size="12" font-weight="bold" text-anchor="middle" fill="#7627bb">Landlock</text>
    <text x="597" y="185" font-family="sans-serif" font-size="11" text-anchor="middle" fill="#3c4043">Offset: 12</text>
    <text x="597" y="210" font-family="sans-serif" font-size="11" text-anchor="middle" fill="#5f6368">domain ptr</text>
    
    <!-- BPF-LSM Slot -->
    <rect x="655" y="130" width="85" height="130" fill="#fce8e6" stroke="#c5221f" stroke-width="1.5" rx="4" />
    <text x="697" y="160" font-family="sans-serif" font-size="12" font-weight="bold" text-anchor="middle" fill="#c5221f">BPF-LSM</text>
    <text x="697" y="185" font-family="sans-serif" font-size="11" text-anchor="middle" fill="#3c4043">Offset: 20</text>
    <text x="697" y="210" font-family="sans-serif" font-size="11" text-anchor="middle" fill="#5f6368">storage</text>
    
    <text x="540" y="282" font-family="sans-serif" font-size="11" font-style="italic" text-anchor="middle" fill="#5f6368">Загальний розмір вираховується при старті ядра через struct lsm_blob_sizes</text>

    <defs>
        <marker id="arrow-blue" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#1a73e8" />
        </marker>
    </defs>
    </svg>"""
    
    with open(os.path.join(out_dir, "lsm-blob-layout.svg"), 'w', encoding='utf-8') as f:
        f.write(doc3)

if __name__ == "__main__":
    render()
