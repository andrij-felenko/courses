import os
import math

def create_svg(filename, width, height, content):
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
<style>
    .bg {{ fill: #1e1e2e; }}
    .title {{ font-family: system-ui, sans-serif; font-size: 16px; font-weight: bold; fill: #cdd6f4; text-anchor: middle; }}
    .subtitle {{ font-family: system-ui, sans-serif; font-size: 13px; fill: #bac2de; text-anchor: middle; }}
    .label {{ font-family: system-ui, sans-serif; font-size: 13px; fill: #cdd6f4; }}
    .label-center {{ font-family: system-ui, sans-serif; font-size: 13px; fill: #cdd6f4; text-anchor: middle; }}
    .label-muted {{ font-family: system-ui, sans-serif; font-size: 12px; fill: #a6adc8; text-anchor: middle; }}
    .formula {{ font-family: "Courier New", monospace; font-size: 14px; font-weight: bold; fill: #f9e2af; text-anchor: middle; }}
    .wire {{ stroke: #89b4fa; stroke-width: 3; fill: none; stroke-linecap: round; stroke-linejoin: round; }}
    .wire-dash {{ stroke: #89b4fa; stroke-width: 2; stroke-dasharray: 5,5; fill: none; }}
    .field-line {{ stroke: #f38ba8; stroke-width: 2; fill: none; }}
    .ext-line {{ stroke: #a6e3a1; stroke-width: 2.5; fill: none; }}
    .box {{ fill: #313244; stroke: #45475a; stroke-width: 2; rx: 8; ry: 8; }}
    .source-box {{ fill: #181825; stroke: #a6e3a1; stroke-width: 2; stroke-dasharray: 4,4; rx: 8; ry: 8; }}
    .charge-pos {{ fill: #f38ba8; stroke: #11111b; stroke-width: 1.5; }}
    .charge-neg {{ fill: #89b4fa; stroke: #11111b; stroke-width: 1.5; }}
    .text-pos {{ font-family: system-ui, sans-serif; font-size: 13px; font-weight: bold; fill: #11111b; text-anchor: middle; dominant-baseline: central; }}
    .text-neg {{ font-family: system-ui, sans-serif; font-size: 15px; font-weight: bold; fill: #11111b; text-anchor: middle; dominant-baseline: central; }}
    .arrow {{ fill: #f38ba8; }}
    .arrow-ext {{ fill: #a6e3a1; }}
    .arrow-b {{ fill: #fab387; }}
    .arrow-v {{ fill: #cba6f7; }}
    .resistor {{ stroke: #f9e2af; stroke-width: 3; fill: none; stroke-linejoin: round; }}
</style>
<rect width="100%" height="100%" class="bg" />
{content}
</svg>'''
    filepath = os.path.join(os.path.dirname(__file__), 'img', filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(svg)
    print(f"Generated {filepath}")

# 1. loop-circulation.svg
def gen_loop_circulation():
    content = '''
    <defs>
        <marker id="arr-red" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 1 L 10 5 L 0 9 z" fill="#f38ba8" />
        </marker>
        <marker id="arr-green" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 1 L 10 5 L 0 9 z" fill="#a6e3a1" />
        </marker>
        <marker id="arr-blue" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 1 L 10 5 L 0 9 z" fill="#89b4fa" />
        </marker>
    </defs>

    <g transform="translate(10, 10)">
        <rect x="0" y="0" width="370" height="340" class="box" />
        <text x="185" y="30" class="title">Консервативне поле E_es</text>
        <text x="185" y="50" class="label-muted">Без сторонніх сил струм згасає</text>

        <circle cx="100" cy="180" r="22" class="charge-pos" />
        <text x="100" y="180" class="text-pos">+</text>
        <circle cx="270" cy="180" r="22" class="charge-neg" />
        <text x="270" y="180" class="text-neg">−</text>

        <path d="M 122 170 Q 185 130 248 170" class="field-line" marker-end="url(#arr-red)" />
        <path d="M 122 180 Q 185 150 248 180" class="field-line" marker-end="url(#arr-red)" />
        <path d="M 122 190 Q 185 230 248 190" class="field-line" marker-end="url(#arr-red)" />
        <text x="185" y="120" class="label-center" fill="#f38ba8">E_es (від + до -)</text>

        <text x="185" y="270" class="formula">∮ E_es · dl = 0</text>
        <text x="185" y="300" class="label-muted">Робота за замкненим контуром дорівнює 0</text>
    </g>

    <g transform="translate(400, 10)">
        <rect x="0" y="0" width="370" height="340" class="box" />
        <text x="185" y="30" class="title">Контур із джерелом ЕРС</text>
        <text x="185" y="50" class="label-muted">Сторонні сили F_ext долають кулонівське поле</text>

        <rect x="50" y="90" width="270" height="180" rx="15" ry="15" class="wire" />

        <rect x="120" y="245" width="130" height="50" class="box" stroke="#a6e3a1" stroke-width="2" />
        <text x="185" y="267" class="label-center" fill="#a6e3a1">Джерело ЕРС</text>
        <text x="185" y="284" class="label-muted">F_ext всередині</text>

        <text x="135" y="270" class="label" fill="#f38ba8" font-weight="bold">+</text>
        <text x="230" y="270" class="label" fill="#89b4fa" font-weight="bold">−</text>

        <path d="M 120 90 L 250 90" class="field-line" stroke="#89b4fa" stroke-width="3" marker-end="url(#arr-blue)" />
        <text x="185" y="80" class="label-center" fill="#89b4fa">Струм I у зовнішньому колі</text>

        <path d="M 220 255 L 150 255" class="ext-line" marker-end="url(#arr-green)" />
        <text x="185" y="240" class="label-center" fill="#a6e3a1">E_ext (від - до +)</text>

        <text x="185" y="315" class="formula">E = ∮ E_ext · dl &gt; 0</text>
    </g>
    '''
    create_svg('loop-circulation.svg', 780, 360, content)

# 2. source-internal-resistance.svg
def gen_source_internal_resistance():
    content = '''
    <defs>
        <marker id="arr-blue2" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 1 L 10 5 L 0 9 z" fill="#89b4fa" />
        </marker>
    </defs>

    <g transform="translate(10, 10)">
        <rect x="0" y="0" width="370" height="340" class="box" />
        <text x="185" y="30" class="title">Модель реального джерела</text>

        <rect x="30" y="70" width="150" height="200" class="source-box" />
        <text x="105" y="90" class="label-center" fill="#a6e3a1">Реальне джерело</text>

        <circle cx="70" cy="170" r="18" fill="none" stroke="#a6e3a1" stroke-width="2" />
        <text x="70" y="174" class="label-center" fill="#a6e3a1" font-weight="bold">E</text>

        <path d="M 70 152 L 70 130 L 130 130" class="wire" />
        <path d="M 130 130 L 133 123 L 139 137 L 145 123 L 151 137 L 157 123 L 160 130" class="resistor" stroke="#f38ba8" />
        <text x="145" y="115" class="label-center" fill="#f38ba8">r</text>

        <circle cx="170" cy="130" r="4" fill="#cdd6f4" />
        <text x="170" y="115" class="label-center">A (+)</text>
        <circle cx="70" cy="230" r="4" fill="#cdd6f4" />
        <text x="70" y="250" class="label-center">B (−)</text>

        <path d="M 170 130 L 290 130 L 290 150" class="wire" />
        <path d="M 290 150 L 283 154 L 297 162 L 283 170 L 297 178 L 283 186 L 290 190" class="resistor" />
        <text x="315" y="174" class="label" fill="#f9e2af">R (навантаження)</text>
        <path d="M 290 190 L 290 230 L 70 230 L 70 188" class="wire" />

        <path d="M 200 130 L 250 130" class="wire" marker-end="url(#arr-blue2)" />
        <text x="225" y="120" class="label-center" fill="#89b4fa">I</text>

        <text x="185" y="295" class="formula">V_term = E − I · r</text>
        <text x="185" y="320" class="label-muted">V_term = I · R (напруга на клемах)</text>
    </g>

    <g transform="translate(400, 10)">
        <rect x="0" y="0" width="370" height="340" class="box" />
        <text x="185" y="30" class="title">Навантажувальна характеристика</text>

        <path d="M 60 260 L 330 260" stroke="#a6adc8" stroke-width="2" marker-end="url(#arr-blue2)" />
        <text x="330" y="280" class="label-center" fill="#a6adc8">I (струм)</text>
        <path d="M 60 260 L 60 70" stroke="#a6adc8" stroke-width="2" marker-end="url(#arr-blue2)" />
        <text x="50" y="65" class="label-center" fill="#a6adc8">V</text>

        <line x1="60" y1="90" x2="300" y2="260" stroke="#f38ba8" stroke-width="3" />

        <circle cx="60" cy="90" r="5" fill="#a6e3a1" />
        <text x="45" y="95" class="label" fill="#a6e3a1" font-weight="bold">E</text>
        <text x="140" y="85" class="label" fill="#a6e3a1">Холостий хід (I = 0)</text>

        <circle cx="300" cy="260" r="5" fill="#f38ba8" />
        <text x="300" y="285" class="label-center" fill="#f38ba8" font-weight="bold">I_sc = E/r</text>
        <text x="240" y="240" class="label-center" fill="#f38ba8">Коротке замикання</text>

        <circle cx="180" cy="175" r="5" fill="#f9e2af" />
        <line x1="180" y1="175" x2="60" y2="175" stroke="#f9e2af" stroke-dasharray="3,3" />
        <line x1="180" y1="175" x2="180" y2="260" stroke="#f9e2af" stroke-dasharray="3,3" />
        <text x="40" y="180" class="label" fill="#f9e2af">V_term</text>
        <text x="180" y="280" class="label-center" fill="#f9e2af">I_робочий</text>

        <text x="185" y="320" class="label-muted">Спад напруги ΔV = I · r залежить від струму</text>
    </g>
    '''
    create_svg('source-internal-resistance.svg', 780, 360, content)

# 3. emf-mechanisms.svg
def gen_emf_mechanisms():
    extra_def = '''<defs><marker id="arr-yellow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1 L 10 5 L 0 9 z" fill="#f9e2af" /></marker></defs>'''
    content = extra_def + '''
    <g transform="translate(10, 10)">
        <rect x="0" y="0" width="175" height="340" class="box" />
        <text x="87" y="30" class="title" font-size="14">1. Хімічна</text>
        <text x="87" y="50" class="label-muted">(Акумулятор)</text>

        <rect x="30" y="120" width="115" height="130" fill="#181825" stroke="#89b4fa" stroke-width="2" rx="4" />
        <rect x="35" y="150" width="105" height="95" fill="#313244" opacity="0.7" />

        <rect x="45" y="90" width="15" height="120" fill="#f38ba8" rx="2" />
        <text x="52" y="80" class="label-center" fill="#f38ba8">+</text>
        <rect x="115" y="90" width="15" height="120" fill="#89b4fa" rx="2" />
        <text x="122" y="80" class="label-center" fill="#89b4fa">−</text>

        <text x="87" y="275" class="label-center" fill="#a6e3a1">Окисно-відновні</text>
        <text x="87" y="295" class="label-center" fill="#a6e3a1">реакції</text>
        <text x="87" y="320" class="label-muted">Розділення іонів</text>
    </g>

    <g transform="translate(200, 10)">
        <rect x="0" y="0" width="175" height="340" class="box" />
        <text x="87" y="30" class="title" font-size="14">2. Індукційна</text>
        <text x="87" y="50" class="label-muted">(Генератор)</text>

        <rect x="30" y="100" width="50" height="40" fill="#f38ba8" rx="4" />
        <text x="55" y="125" class="label-center" fill="#11111b" font-weight="bold">N</text>
        <rect x="30" y="140" width="50" height="40" fill="#89b4fa" rx="4" />
        <text x="55" y="165" class="label-center" fill="#11111b" font-weight="bold">S</text>

        <ellipse cx="120" cy="140" rx="25" ry="40" class="wire" stroke="#f9e2af" stroke-width="3" />
        <path d="M 30 115 C 80 110, 100 120, 150 115" class="field-line" stroke-dasharray="3,3" />
        <path d="M 30 165 C 80 160, 100 170, 150 165" class="field-line" stroke-dasharray="3,3" />

        <text x="87" y="275" class="label-center" fill="#f9e2af">Зміна поля B(t)</text>
        <text x="87" y="295" class="formula" font-size="12">E = −dΦ/dt</text>
        <text x="87" y="320" class="label-muted">Сила Лоренца</text>
    </g>

    <g transform="translate(390, 10)">
        <rect x="0" y="0" width="175" height="340" class="box" />
        <text x="87" y="30" class="title" font-size="14">3. Термоелектрична</text>
        <text x="87" y="50" class="label-muted">(Термопара)</text>

        <path d="M 30 180 L 87 120 L 145 180" stroke="#fab387" stroke-width="4" fill="none" />
        <path d="M 30 200 L 87 140 L 145 200" stroke="#cba6f7" stroke-width="4" fill="none" />
        <circle cx="87" cy="130" r="10" fill="#f38ba8" />
        <text x="87" y="95" class="label-center" fill="#f38ba8">Гарячий T1</text>
        <text x="40" y="225" class="label-center" fill="#89b4fa">T2</text>
        <text x="135" y="225" class="label-center" fill="#89b4fa">T2</text>

        <text x="87" y="275" class="label-center" fill="#fab387">Градієнт T</text>
        <text x="87" y="295" class="formula" font-size="12">E = α · ΔT</text>
        <text x="87" y="320" class="label-muted">Ефект Зеєбека</text>
    </g>

    <g transform="translate(580, 10)">
        <rect x="0" y="0" width="180" height="340" class="box" />
        <text x="90" y="30" class="title" font-size="14">4. Фотоелектрична</text>
        <text x="90" y="50" class="label-muted">(Сонячна панель)</text>

        <rect x="30" y="110" width="120" height="40" fill="#89b4fa" opacity="0.8" rx="2" />
        <text x="90" y="134" class="label-center" fill="#11111b" font-weight="bold">n-шар</text>
        <rect x="30" y="150" width="120" height="50" fill="#f38ba8" opacity="0.8" rx="2" />
        <text x="90" y="180" class="label-center" fill="#11111b" font-weight="bold">p-шар</text>

        <path d="M 40 70 L 60 105" stroke="#f9e2af" stroke-width="2" marker-end="url(#arr-yellow)" />
        <path d="M 80 65 L 100 105" stroke="#f9e2af" stroke-width="2" marker-end="url(#arr-yellow)" />
        <path d="M 120 70 L 140 105" stroke="#f9e2af" stroke-width="2" marker-end="url(#arr-yellow)" />
        <text x="90" y="60" class="label-center" fill="#f9e2af">Фотони (hν)</text>

        <text x="90" y="275" class="label-center" fill="#f9e2af">Поглинання світла</text>
        <text x="90" y="295" class="label-center" fill="#a6e3a1">Розділення e-/h+</text>
        <text x="90" y="320" class="label-muted">Внутрішнє поле p-n</text>
    </g>
    '''
    create_svg('emf-mechanisms.svg', 770, 360, content)

# 4. motional-emf-conductor.svg
def gen_motional_emf():
    crosses = []
    for x in range(40, 640, 70):
        for y in range(30, 200, 50):
            crosses.append(f'<g transform="translate({x}, {y})"><circle cx="0" cy="0" r="10" fill="none" stroke="#fab387" stroke-width="1.5"/><line x1="-6" y1="-6" x2="6" y2="6" stroke="#fab387" stroke-width="1.5"/><line x1="6" y1="-6" x2="-6" y2="6" stroke="#fab387" stroke-width="1.5"/></g>')
    crosses_svg = '\n'.join(crosses)

    content = f'''
    <defs>
        <marker id="arr-purple" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 1 L 10 5 L 0 9 z" fill="#cba6f7" />
        </marker>
        <marker id="arr-green2" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 1 L 10 5 L 0 9 z" fill="#a6e3a1" />
        </marker>
    </defs>

    <rect x="10" y="10" width="740" height="340" class="box" />
    <text x="380" y="35" class="title">ЕРС руху в провіднику (Сила Лоренца)</text>

    <g transform="translate(60, 70)">
        {crosses_svg}
    </g>
    <text x="680" y="80" class="label-center" fill="#fab387">B (напрямлене у сторінку ⊗)</text>

    <rect x="340" y="90" width="30" height="180" fill="#89b4fa" stroke="#cdd6f4" stroke-width="2" rx="4" />
    <text x="355" y="110" class="label-center" fill="#f38ba8" font-weight="bold">+</text>
    <text x="355" y="255" class="label-center" fill="#89b4fa" font-weight="bold">−</text>
    <text x="390" y="180" class="label" fill="#cdd6f4">Довжина L</text>

    <path d="M 370 180 L 470 180" stroke="#cba6f7" stroke-width="4" marker-end="url(#arr-purple)" />
    <text x="420" y="165" class="label-center" fill="#cba6f7" font-weight="bold">Швидкість v</text>

    <path d="M 355 180 L 355 130" stroke="#a6e3a1" stroke-width="3" marker-end="url(#arr-green2)" />
    <text x="300" y="150" class="label" fill="#a6e3a1">F_L = q(v × B)</text>

    <rect x="180" y="285" width="400" height="50" class="box" stroke="#f9e2af" stroke-width="1.5" />
    <text x="380" y="315" class="formula">E = v · B · L · sin(θ)</text>
    '''
    create_svg('motional-emf-conductor.svg', 760, 360, content)

if __name__ == '__main__':
    gen_loop_circulation()
    gen_source_internal_resistance()
    gen_emf_mechanisms()
    gen_motional_emf()
