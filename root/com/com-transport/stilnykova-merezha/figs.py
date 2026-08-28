# -*- coding: utf-8 -*-
"""Генератор векторних діаграм (SVG) для теми stilnykova-merezha."""
import os
import math

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def fig_cellular_topology():
    """Фігура 1: Топологія стільникової мережі, секторизація та повторне використання частот."""
    w, h = 960, 500
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="100%" height="100%">',
        '<style>',
        '  .bg { fill: #0f172a; }',
        '  .card { fill: #1e293b; stroke: #334155; stroke-width: 1.5; rx: 8px; }',
        '  .hex { stroke-width: 2; fill-opacity: 0.15; }',
        '  .hex-f1 { stroke: #38bdf8; fill: #38bdf8; }',
        '  .hex-f2 { stroke: #4ade80; fill: #4ade80; }',
        '  .hex-f3 { stroke: #f43f5e; fill: #f43f5e; }',
        '  .sec-line { stroke: #94a3b8; stroke-width: 1.5; stroke-dasharray: 4,3; }',
        '  .tower-beam { fill-opacity: 0.25; stroke-width: 1; }',
        '  .beam-s1 { fill: #38bdf8; stroke: #38bdf8; }',
        '  .beam-s2 { fill: #4ade80; stroke: #4ade80; }',
        '  .beam-s3 { fill: #fbbf24; stroke: #fbbf24; }',
        '  .txt-title { font-family: sans-serif; font-size: 14px; font-weight: 700; fill: #f8fafc; }',
        '  .txt-sub { font-family: sans-serif; font-size: 11px; fill: #94a3b8; }',
        '  .txt-bold { font-family: sans-serif; font-size: 12px; font-weight: 700; fill: #f1f5f9; }',
        '  .txt-sec { font-family: sans-serif; font-size: 10px; font-weight: 600; fill: #cbd5e1; }',
        '  .legend-box { fill: #1e293b; stroke: #475569; stroke-width: 1; rx: 4px; }',
        '  .badge { fill: #0f172a; stroke-width: 1; rx: 4px; }',
        '</style>',
        f'<rect class="bg" width="{w}" height="{h}" />',
    ]

    # Panel 1: Hexagonal grid and frequency reuse (Left side)
    svg.append('<rect class="card" x="20" y="20" width="450" height="460" />')
    svg.append('<text class="txt-title" font-size="14" x="40" y="48">Повторне використання частот (Reuse N=3 vs N=1)</text>')
    svg.append('<text class="txt-sub" font-size="11" x="40" y="68">Мінімізація міжсотової інтерференції (ICI) на межах сот</text>')

    def hex_pts(cx, cy, r):
        pts = []
        for i in range(6):
            ang = math.radians(60 * i + 30)
            pts.append(f"{cx + r * math.cos(ang):.1f},{cy + r * math.sin(ang):.1f}")
        return " ".join(pts)

    r_hex = 52
    cells = [
        (140, 160, "hex-f1", "f₁", "Сота A"),
        (230, 160, "hex-f2", "f₂", "Сота B"),
        (320, 160, "hex-f3", "f₃", "Сота C"),
        (95, 238, "hex-f2", "f₂", "Сота D"),
        (185, 238, "hex-f3", "f₃", "Сота E"),
        (275, 238, "hex-f1", "f₁", "Сота F"),
        (365, 238, "hex-f2", "f₂", "Сота G"),
        (140, 316, "hex-f1", "f₁", "Сота H"),
        (230, 316, "hex-f2", "f₂", "Сота I"),
        (320, 316, "hex-f3", "f₃", "Сота J"),
    ]

    for cx, cy, cls, freq, name in cells:
        svg.append(f'<polygon class="hex {cls}" points="{hex_pts(cx, cy, r_hex)}" />')
        svg.append(f'<circle cx="{cx}" cy="{cy}" r="3" fill="#ffffff" />')
        svg.append(f'<text class="txt-bold" font-size="12" x="{cx}" y="{cy - 8}" text-anchor="middle">{freq}</text>')
        svg.append(f'<text class="txt-sub" font-size="11" x="{cx}" y="{cy + 18}" text-anchor="middle">{name}</text>')

    svg.append('<rect class="legend-box" x="40" y="390" width="410" height="70" />')
    svg.append('<circle cx="58" cy="412" r="6" class="hex-f1" fill-opacity="1" />')
    svg.append('<text class="txt-sub" font-size="11" x="75" y="416">Канал f₁: смуга A (наприклад, EARFCN 1300)</text>')
    svg.append('<circle cx="58" cy="438" r="6" class="hex-f2" fill-opacity="1" />')
    svg.append('<text class="txt-sub" font-size="11" x="75" y="442">Канали f₂, f₃: суміжні піддіапазони без накладання</text>')

    # Panel 2: 3-Sector Base Station (Right side)
    svg.append('<rect class="card" x="490" y="20" width="450" height="460" />')
    svg.append('<text class="txt-title" font-size="14" x="510" y="48">Трьохсекторна базова станція (eNodeB / gNodeB)</text>')
    svg.append('<text class="txt-sub" font-size="11" x="510" y="68">Секторизація по 120° спрямованими панелями (PCI = 3·Group + Sec)</text>')

    tcx, tcy = 715, 230
    # Beams
    svg.append(f'<path class="tower-beam beam-s1" d="M {tcx} {tcy} L {tcx - 55} {tcy - 100} A 120 120 0 0 1 {tcx + 55} {tcy - 100} Z" />')
    svg.append(f'<path class="tower-beam beam-s2" d="M {tcx} {tcy} L {tcx + 115} {tcy - 5} A 120 120 0 0 1 {tcx + 20} {tcy + 115} Z" />')
    svg.append(f'<path class="tower-beam beam-s3" d="M {tcx} {tcy} L {tcx - 20} {tcy + 115} A 120 120 0 0 1 {tcx - 115} {tcy - 5} Z" />')

    # Sector dividing lines
    svg.append(f'<line class="sec-line" x1="{tcx}" y1="{tcy - 15}" x2="{tcx}" y2="{tcy - 120}" />')
    svg.append(f'<line class="sec-line" x1="{tcx + 15}" y1="{tcy + 10}" x2="{tcx + 105}" y2="{tcy + 60}" />')
    svg.append(f'<line class="sec-line" x1="{tcx - 15}" y1="{tcy + 10}" x2="{tcx - 105}" y2="{tcy + 60}" />')

    # Tower icon
    svg.append(f'<circle cx="{tcx}" cy="{tcy}" r="12" fill="#334155" stroke="#64748b" stroke-width="2" />')
    svg.append(f'<polygon points="{tcx},{tcy-7} {tcx+5},{tcy+3} {tcx-5},{tcy+3}" fill="#f8fafc" />')

    # Badges for sector descriptions
    svg.append(f'<rect class="badge" x="{tcx + 65}" y="{tcy - 110}" width="125" height="42" stroke="#38bdf8" />')
    svg.append(f'<text class="txt-bold" font-size="12" x="{tcx + 75}" y="{tcy - 92}" fill="#38bdf8">Сектор 0 (0°)</text>')
    svg.append(f'<text class="txt-sec" font-size="10" x="{tcx + 75}" y="{tcy - 76}">Cell ID = 3k+0</text>')

    svg.append(f'<rect class="badge" x="{tcx + 65}" y="{tcy + 85}" width="125" height="42" stroke="#4ade80" />')
    svg.append(f'<text class="txt-bold" font-size="12" x="{tcx + 75}" y="{tcy + 103}" fill="#4ade80">Сектор 1 (120°)</text>')
    svg.append(f'<text class="txt-sec" font-size="10" x="{tcx + 75}" y="{tcy + 119}">Cell ID = 3k+1</text>')

    svg.append(f'<rect class="badge" x="{tcx - 190}" y="{tcy + 85}" width="125" height="42" stroke="#fbbf24" />')
    svg.append(f'<text class="txt-bold" font-size="12" x="{tcx - 180}" y="{tcy + 103}" fill="#fbbf24">Сектор 2 (240°)</text>')
    svg.append(f'<text class="txt-sec" font-size="10" x="{tcx - 180}" y="{tcy + 119}">Cell ID = 3k+2</text>')

    svg.append('<rect class="legend-box" x="510" y="390" width="410" height="70" />')
    svg.append('<text class="txt-sub" font-size="11" x="525" y="416">• Секторизація зменшує взаємну інтерференцію в 3 рази</text>')
    svg.append('<text class="txt-sub" font-size="11" x="525" y="442">• Окремий RF-тракт на кожен сектор (MIMO 2x2/4x4/Massive)</text>')

    svg.append('</svg>')
    out_path = os.path.join(IMG_DIR, "cellular-topology-sectorization.svg")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print(f"Generated: {out_path}")


def fig_rach_and_attach():
    """Фігура 2: Послідовність підключення RACH (Msg1-Msg4) та реєстрація в ядрі (Attach/Auth)."""
    w, h = 960, 580
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="100%" height="100%">',
        '<style>',
        '  .bg { fill: #0f172a; }',
        '  .title { font-family: sans-serif; font-size: 15px; font-weight: 700; fill: #f8fafc; }',
        '  .subtitle { font-family: sans-serif; font-size: 11px; fill: #94a3b8; }',
        '  .node-box { fill: #1e293b; stroke: #475569; stroke-width: 1.5; rx: 6px; }',
        '  .node-title { font-family: sans-serif; font-size: 12px; font-weight: 700; fill: #f1f5f9; }',
        '  .node-sub { font-family: sans-serif; font-size: 10px; fill: #94a3b8; }',
        '  .lifeline { stroke: #334155; stroke-width: 1.5; stroke-dasharray: 4,4; }',
        '  .phase-box { fill: #1e293b; fill-opacity: 0.5; stroke: #3b82f6; stroke-width: 1; stroke-dasharray: 3,3; rx: 4px; }',
        '  .phase-title { font-family: sans-serif; font-size: 11px; font-weight: 700; fill: #60a5fa; }',
        '  .msg-line { stroke-width: 1.5; }',
        '  .msg-ul { stroke: #38bdf8; }',
        '  .msg-dl { stroke: #4ade80; }',
        '  .msg-core { stroke: #a78bfa; }',
        '  .msg-txt { font-family: sans-serif; font-size: 11px; font-weight: 600; fill: #e2e8f0; }',
        '  .msg-detail { font-family: sans-serif; font-size: 10px; fill: #94a3b8; }',
        '</style>',
        '<defs>',
        '  <marker id="arr-ul" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">',
        '    <polygon points="0 0, 8 3, 0 6" fill="#38bdf8" />',
        '  </marker>',
        '  <marker id="arr-dl" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">',
        '    <polygon points="0 0, 8 3, 0 6" fill="#4ade80" />',
        '  </marker>',
        '  <marker id="arr-core" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">',
        '    <polygon points="0 0, 8 3, 0 6" fill="#a78bfa" />',
        '  </marker>',
        '</defs>',
        f'<rect class="bg" width="{w}" height="{h}" />',
        '<text class="title" font-size="15" x="30" y="32">Процедура підключення: Випадковий доступ (RACH) та реєстрація в ядрі (Attach)</text>',
        '<text class="subtitle" font-size="11" x="30" y="48">Від фізичної синхронізації до виділення радіоносіїв (Default EPS Bearer / PDU Session)</text>',
    ]

    ue_x = 120
    enb_x = 380
    mme_x = 640
    hss_x = 860

    nodes = [
        (ue_x, "UE (Модем)", "SIM / RRC / NAS"),
        (enb_x, "eNodeB / gNodeB", "PHY / MAC / RRC"),
        (mme_x, "MME / AMF", "Контролер ядра"),
        (hss_x, "HSS / UDM", "База абонентів"),
    ]

    for nx, title, sub in nodes:
        svg.append(f'<rect class="node-box" x="{nx - 60}" y="65" width="120" height="48" />')
        svg.append(f'<text class="node-title" font-size="12" x="{nx}" y="85" text-anchor="middle">{title}</text>')
        svg.append(f'<text class="node-sub" font-size="10" x="{nx}" y="101" text-anchor="middle">{sub}</text>')
        svg.append(f'<line class="lifeline" x1="{nx}" y1="115" x2="{nx}" y2="{h - 25}" />')

    # Phase 1: MIB/SIB System Info
    y = 140
    svg.append(f'<line class="msg-line msg-dl" x1="{enb_x}" y1="{y}" x2="{ue_x}" y2="{y}" marker-end="url(#arr-dl)" />')
    svg.append(f'<text class="msg-txt" font-size="11" x="{ue_x + 15}" y="{y - 6}">1. PBCH / PDSCH: MIB + SIB1 + SIB2</text>')
    svg.append(f'<text class="msg-detail" font-size="10" x="{ue_x + 15}" y="{y + 14}">Синхронізація (PSS/SSS), смуга DL, параметри PRACH, TAC, PLMN</text>')

    # Phase 2: RACH 4-step
    y = 190
    svg.append(f'<rect class="phase-box" x="40" y="{y - 14}" width="420" height="150" />')
    svg.append(f'<text class="phase-title" font-size="11" x="50" y="{y + 2}">ФАЗА ВИПАДКОВОГО ДОСТУПУ (4-Step CBRA RACH)</text>')

    y1 = y + 25
    svg.append(f'<line class="msg-line msg-ul" x1="{ue_x}" y1="{y1}" x2="{enb_x}" y2="{y1}" marker-end="url(#arr-ul)" />')
    svg.append(f'<text class="msg-txt" font-size="11" x="{ue_x + 15}" y="{y1 - 6}">Msg1: PRACH Preamble (Zadoff-Chu seq)</text>')

    y2 = y1 + 35
    svg.append(f'<line class="msg-line msg-dl" x1="{enb_x}" y1="{y2}" x2="{ue_x}" y2="{y2}" marker-end="url(#arr-dl)" />')
    svg.append(f'<text class="msg-txt" font-size="11" x="{ue_x + 15}" y="{y2 - 6}">Msg2: RAR (Timing Advance, UL Grant, TC-RNTI)</text>')

    y3 = y2 + 35
    svg.append(f'<line class="msg-line msg-ul" x1="{ue_x}" y1="{y3}" x2="{enb_x}" y2="{y3}" marker-end="url(#arr-ul)" />')
    svg.append(f'<text class="msg-txt" font-size="11" x="{ue_x + 15}" y="{y3 - 6}">Msg3: RRCSetupRequest (UE-ID: S-TMSI / Random)</text>')

    y4 = y3 + 35
    svg.append(f'<line class="msg-line msg-dl" x1="{enb_x}" y1="{y4}" x2="{ue_x}" y2="{y4}" marker-end="url(#arr-dl)" />')
    svg.append(f'<text class="msg-txt" font-size="11" x="{ue_x + 15}" y="{y4 - 6}">Msg4: RRCSetup (Contention Resolution, C-RNTI)</text>')

    # Phase 3: RRC & NAS Attach / Registration
    y = 365
    svg.append(f'<line class="msg-line msg-ul" x1="{ue_x}" y1="{y}" x2="{enb_x}" y2="{y}" marker-end="url(#arr-ul)" />')
    svg.append(f'<text class="msg-txt" font-size="11" x="{ue_x + 15}" y="{y - 6}">RRCSetupComplete + NAS: Attach Request (IMSI/GUTI)</text>')

    y += 32
    svg.append(f'<line class="msg-line msg-core" x1="{enb_x}" y1="{y}" x2="{mme_x}" y2="{y}" marker-end="url(#arr-core)" />')
    svg.append(f'<text class="msg-txt" font-size="11" x="{enb_x + 15}" y="{y - 6}">S1-AP: Initial UE Message (Attach Request)</text>')

    # Authentication & Security
    y += 36
    svg.append(f'<line class="msg-line msg-core" x1="{mme_x}" y1="{y}" x2="{hss_x}" y2="{y}" marker-end="url(#arr-core)" />')
    svg.append(f'<text class="msg-txt" font-size="11" x="{mme_x + 15}" y="{y - 6}">Authentication Information Request</text>')

    y += 32
    svg.append(f'<line class="msg-line msg-core" x1="{hss_x}" y1="{y}" x2="{mme_x}" y2="{y}" marker-end="url(#arr-core)" />')
    svg.append(f'<text class="msg-txt" font-size="11" x="{mme_x + 15}" y="{y - 6}">Auth Vectors (RAND, AUTN, XRES, K_ASME)</text>')

    y += 36
    svg.append(f'<line class="msg-line msg-dl" x1="{mme_x}" y1="{y}" x2="{ue_x}" y2="{y}" marker-end="url(#arr-dl)" />')
    svg.append(f'<text class="msg-txt" font-size="11" x="{ue_x + 15}" y="{y - 6}">NAS: Authentication Request (RAND, AUTN) - Security Activation</text>')

    y += 36
    svg.append(f'<line class="msg-line msg-dl" x1="{enb_x}" y1="{y}" x2="{ue_x}" y2="{y}" marker-end="url(#arr-dl)" />')
    svg.append(f'<text class="msg-txt" font-size="11" x="{ue_x + 15}" y="{y - 6}">RRC: SecurityModeCommand &amp; RRCReconfiguration (Default Bearer / IP)</text>')

    svg.append('</svg>')
    out_path = os.path.join(IMG_DIR, "rach-and-attach-sequence.svg")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print(f"Generated: {out_path}")


def fig_rrc_state_machine():
    """Фігура 3: Автомат станів RRC (IDLE, CONNECTED, INACTIVE) з тригерами переходів."""
    w, h = 940, 450
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="100%" height="100%">',
        '<style>',
        '  .bg { fill: #0f172a; }',
        '  .title { font-family: sans-serif; font-size: 15px; font-weight: 700; fill: #f8fafc; }',
        '  .subtitle { font-family: sans-serif; font-size: 11px; fill: #94a3b8; }',
        '  .state-card { rx: 8px; stroke-width: 2; }',
        '  .st-idle { fill: #1e293b; stroke: #38bdf8; }',
        '  .st-conn { fill: #1e293b; stroke: #4ade80; }',
        '  .st-inact { fill: #1e293b; stroke: #f59e0b; }',
        '  .st-name { font-family: sans-serif; font-size: 13px; font-weight: 700; }',
        '  .st-desc { font-family: sans-serif; font-size: 10px; fill: #cbd5e1; }',
        '  .trans-line { stroke-width: 1.5; fill: none; }',
        '  .t-blue { stroke: #38bdf8; }',
        '  .t-green { stroke: #4ade80; }',
        '  .t-yellow { stroke: #f59e0b; }',
        '  .t-red { stroke: #f43f5e; }',
        '  .trans-txt { font-family: sans-serif; font-size: 10px; font-weight: 600; fill: #f1f5f9; }',
        '  .trans-sub { font-family: sans-serif; font-size: 9px; fill: #94a3b8; }',
        '</style>',
        '<defs>',
        '  <marker id="arr-b" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">',
        '    <polygon points="0 0, 8 3, 0 6" fill="#38bdf8" />',
        '  </marker>',
        '  <marker id="arr-g" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">',
        '    <polygon points="0 0, 8 3, 0 6" fill="#4ade80" />',
        '  </marker>',
        '  <marker id="arr-y" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">',
        '    <polygon points="0 0, 8 3, 0 6" fill="#f59e0b" />',
        '  </marker>',
        '  <marker id="arr-r" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">',
        '    <polygon points="0 0, 8 3, 0 6" fill="#f43f5e" />',
        '  </marker>',
        '</defs>',
        f'<rect class="bg" width="{w}" height="{h}" />',
        '<text class="title" font-size="15" x="30" y="32">Автомат станів керування радіоресурсами (RRC State Machine)</text>',
        '<text class="subtitle" font-size="11" x="30" y="48">Еволюція станів зв\'язку від класичного LTE (IDLE/CONNECTED) до 5G NR (RRC_INACTIVE)</text>',
    ]

    # State 1: RRC_IDLE (Left)
    svg.append('<rect class="state-card st-idle" x="35" y="85" width="240" height="280" />')
    svg.append('<text class="st-name" font-size="13" x="155" y="115" text-anchor="middle" fill="#38bdf8">RRC_IDLE</text>')
    svg.append('<text class="st-desc" font-size="10" x="50" y="145">• TX вимкнено (енергозбереження)</text>')
    svg.append('<text class="st-desc" font-size="10" x="50" y="168">• Періодичний DRX / eDRX цикл</text>')
    svg.append('<text class="st-desc" font-size="10" x="50" y="191">• Слухання Paging каналу</text>')
    svg.append('<text class="st-desc" font-size="10" x="50" y="214">• Вимірювання для переобрання</text>')
    svg.append('<text class="st-desc" font-size="10" x="50" y="235">  соти (Cell Reselection S-критерій)</text>')
    svg.append('<text class="st-desc" font-size="10" x="50" y="258">• Немає C-RNTI та RRC-контексту</text>')
    svg.append('<text class="st-desc" font-size="10" x="50" y="281">• Локація відома з точністю до TAC</text>')
    svg.append('<text class="st-desc" font-size="10" x="50" y="315" fill="#38bdf8">Час переходу: ~100–150 мс</text>')

    # State 2: RRC_CONNECTED (Right)
    svg.append('<rect class="state-card st-conn" x="665" y="85" width="240" height="280" />')
    svg.append('<text class="st-name" font-size="13" x="785" y="115" text-anchor="middle" fill="#4ade80">RRC_CONNECTED</text>')
    svg.append('<text class="st-desc" font-size="10" x="680" y="145">• Активний прийом і передача даних</text>')
    svg.append('<text class="st-desc" font-size="10" x="680" y="168">• Виділений ідентифікатор C-RNTI</text>')
    svg.append('<text class="st-desc" font-size="10" x="680" y="191">• Налаштовані радіоносії (DRB/SRB)</text>')
    svg.append('<text class="st-desc" font-size="10" x="680" y="214">• Контроль каналу (CQI, PMI, RI)</text>')
    svg.append('<text class="st-desc" font-size="10" x="680" y="237">• Звіти вимірювань для Handover</text>')
    svg.append('<text class="st-desc" font-size="10" x="680" y="260">• Керування потужністю (TPC)</text>')
    svg.append('<text class="st-desc" font-size="10" x="680" y="283">• Постійний моніторинг PDCCH</text>')
    svg.append('<text class="st-desc" font-size="10" x="680" y="315" fill="#4ade80">Затримка пакету: &lt; 1–4 мс</text>')

    # State 3: RRC_INACTIVE (Center bottom)
    svg.append('<rect class="state-card st-inact" x="350" y="240" width="240" height="185" />')
    svg.append('<text class="st-name" font-size="13" x="470" y="265" text-anchor="middle" fill="#f59e0b">RRC_INACTIVE (5G/LTE-A)</text>')
    svg.append('<text class="st-desc" font-size="10" x="365" y="290">• Контекст безпеки збережено в RAN</text>')
    svg.append('<text class="st-desc" font-size="10" x="365" y="310">• Зв\'язок Core (N2/N3) залишається</text>')
    svg.append('<text class="st-desc" font-size="10" x="365" y="330">• Пристрій спить як в IDLE</text>')
    svg.append('<text class="st-desc" font-size="10" x="365" y="350">• Швидке відновлення без ядра</text>')
    svg.append('<text class="st-desc" font-size="10" x="365" y="370">• Призначено I-RNTI і RNA</text>')
    svg.append('<text class="st-desc" font-size="10" x="365" y="395" fill="#f59e0b">Час відновлення: &lt; 10–15 мс</text>')

    # Transition Arrows
    # 1. IDLE -> CONNECTED (Top arc)
    svg.append('<path class="trans-line t-green" d="M 275 125 C 400 65, 540 65, 665 125" marker-end="url(#arr-g)" />')
    svg.append('<text class="trans-txt" font-size="10" x="470" y="85" text-anchor="middle">RRC Setup (RACH, MO Data / MT Paging)</text>')
    svg.append('<text class="trans-sub" font-size="9" x="470" y="100" text-anchor="middle">Повне встановлення RRC та носіїв ядра</text>')

    # 2. CONNECTED -> IDLE (Lower middle)
    svg.append('<path class="trans-line t-red" d="M 665 175 C 540 140, 400 140, 275 175" marker-end="url(#arr-r)" />')
    svg.append('<text class="trans-txt" font-size="10" x="470" y="152" text-anchor="middle">RRCRelease (Inactivity Timer / Detach)</text>')

    # 3. CONNECTED -> INACTIVE
    svg.append('<path class="trans-line t-yellow" d="M 685 365 C 655 400, 625 390, 590 375" marker-end="url(#arr-y)" />')
    svg.append('<text class="trans-txt" font-size="10" x="655" y="420" text-anchor="middle">RRCRelease (suspendConfig)</text>')

    # 4. INACTIVE -> CONNECTED
    svg.append('<path class="trans-line t-green" d="M 550 240 C 585 200, 625 195, 665 215" marker-end="url(#arr-g)" />')
    svg.append('<text class="trans-txt" font-size="10" x="575" y="200" text-anchor="middle">RRCResumeRequest</text>')

    # 5. INACTIVE -> IDLE
    svg.append('<path class="trans-line t-red" d="M 350 340 C 320 345, 300 345, 275 330" marker-end="url(#arr-r)" />')
    svg.append('<text class="trans-txt" font-size="10" x="290" y="370" text-anchor="middle">RNA fail / Core release</text>')

    svg.append('</svg>')
    out_path = os.path.join(IMG_DIR, "rrc-state-machine.svg")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print(f"Generated: {out_path}")


def fig_handover_timeline():
    """Фігура 4: Часова діаграма хендоверу (Event A3, Hysteresis, Time-to-Trigger, виконання)."""
    w, h = 960, 500
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="100%" height="100%">',
        '<style>',
        '  .bg { fill: #0f172a; }',
        '  .title { font-family: sans-serif; font-size: 15px; font-weight: 700; fill: #f8fafc; }',
        '  .subtitle { font-family: sans-serif; font-size: 11px; fill: #94a3b8; }',
        '  .axis { stroke: #475569; stroke-width: 1.5; }',
        '  .grid { stroke: #334155; stroke-width: 1; stroke-dasharray: 4,4; }',
        '  .sig-srv { stroke: #38bdf8; stroke-width: 2.5; fill: none; }',
        '  .sig-tgt { stroke: #4ade80; stroke-width: 2.5; fill: none; }',
        '  .ttt-zone { fill: #38bdf8; fill-opacity: 0.12; stroke: #38bdf8; stroke-width: 1; stroke-dasharray: 2,2; }',
        '  .event-line { stroke: #f43f5e; stroke-width: 1.5; stroke-dasharray: 3,3; }',
        '  .txt-axis { font-family: sans-serif; font-size: 10px; fill: #94a3b8; }',
        '  .txt-lbl { font-family: sans-serif; font-size: 12px; font-weight: 700; fill: #f8fafc; }',
        '  .txt-note { font-family: sans-serif; font-size: 10px; fill: #cbd5e1; }',
        '  .box-note { fill: #1e293b; stroke: #475569; stroke-width: 1; rx: 4px; }',
        '</style>',
        '<defs>',
        '  <marker id="arr-axis" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">',
        '    <polygon points="0 0, 8 3, 0 6" fill="#475569" />',
        '  </marker>',
        '</defs>',
        f'<rect class="bg" width="{w}" height="{h}" />',
        '<text class="title" font-size="15" x="30" y="32">Процес естафетної передачі (Handover): Подія A3, Гістерезис та Time-to-Trigger</text>',
        '<text class="subtitle" font-size="11" x="30" y="48">Запобігання ефекту «пінг-понгу» при перетині меж суміжних сот</text>',
    ]

    ox, oy = 80, 420
    gw, gh = 820, 310

    # Axes
    svg.append(f'<line class="axis" x1="{ox}" y1="{oy}" x2="{ox + gw}" y2="{oy}" marker-end="url(#arr-axis)" />')
    svg.append(f'<line class="axis" x1="{ox}" y1="{oy}" x2="{ox}" y2="{oy - gh}" marker-end="url(#arr-axis)" />')
    svg.append(f'<text class="txt-axis" font-size="10" x="{ox + gw - 40}" y="{oy + 25}">Час (t)</text>')
    svg.append(f'<text class="txt-axis" font-size="10" x="{ox - 65}" y="{oy - gh + 15}">RSRP (dBm)</text>')

    # Signal curves stay within y = 200..400
    srv_d = f"M {ox} {oy - 200} C {ox + 220} {oy - 190}, {ox + 380} {oy - 130}, {ox + 550} {oy - 70} S {ox + 750} {oy - 35}, {ox + 800} {oy - 25}"
    tgt_d = f"M {ox} {oy - 25} C {ox + 220} {oy - 50}, {ox + 380} {oy - 110}, {ox + 550} {oy - 165} S {ox + 750} {oy - 210}, {ox + 800} {oy - 220}"

    svg.append(f'<path class="sig-srv" d="{srv_d}" />')
    svg.append(f'<path class="sig-tgt" d="{tgt_d}" />')

    # Top boxes stay strictly in y = 60..120
    # Legend box (top left)
    svg.append(f'<rect class="box-note" x="{ox + 20}" y="65" width="220" height="52" />')
    svg.append(f'<line x1="{ox + 30}" y1="82" x2="{ox + 55}" y2="82" stroke="#38bdf8" stroke-width="3" />')
    svg.append(f'<text class="txt-lbl" font-size="12" x="{ox + 65}" y="86" fill="#38bdf8">Serving Cell (Поточна)</text>')
    svg.append(f'<line x1="{ox + 30}" y1="102" x2="{ox + 55}" y2="102" stroke="#4ade80" stroke-width="3" />')
    svg.append(f'<text class="txt-lbl" font-size="12" x="{ox + 65}" y="106" fill="#4ade80">Target Cell (Сусідня)</text>')

    # Middle Note Box (A3 Condition)
    svg.append(f'<rect class="box-note" x="{ox + 260}" y="65" width="220" height="52" />')
    svg.append(f'<text class="txt-lbl" font-size="12" x="{ox + 270}" y="86" fill="#f59e0b">Умова події A3:</text>')
    svg.append(f'<text class="txt-note" font-size="10" x="{ox + 270}" y="104">RSRP_tgt &gt; RSRP_srv + Hys + Off</text>')

    # Right Note Box (Handover Execution)
    svg.append(f'<rect class="box-note" x="{ox + 500}" y="65" width="220" height="52" />')
    svg.append(f'<text class="txt-lbl" font-size="12" x="{ox + 512}" y="86" fill="#4ade80">Виконання естафети:</text>')
    svg.append(f'<text class="txt-note" font-size="10" x="{ox + 512}" y="104">• X2/Xn Handover Command</text>')

    t_eq = ox + 320     # Equal RSRP
    t_start = ox + 410  # A3 condition triggered
    t_report = ox + 570 # TTT expires
    t_ho = ox + 720     # Handover Execution

    # Event dashed lines start at y=135 and go down to y=oy
    svg.append(f'<line class="grid" x1="{t_eq}" y1="{oy}" x2="{t_eq}" y2="135" />')
    svg.append(f'<text class="txt-axis" font-size="10" x="{t_eq}" y="{oy + 18}" text-anchor="middle">RSRP₁ = RSRP₂</text>')

    svg.append(f'<line class="event-line" x1="{t_start}" y1="{oy}" x2="{t_start}" y2="135" />')
    svg.append(f'<text class="txt-axis" font-size="10" x="{t_start}" y="{oy + 18}" text-anchor="middle">A3 Вхід</text>')

    # Shaded TTT Zone
    svg.append(f'<rect class="ttt-zone" x="{t_start}" y="135" width="{t_report - t_start}" height="{oy - 135}" />')

    svg.append(f'<line class="event-line" x1="{t_report}" y1="{oy}" x2="{t_report}" y2="135" />')
    svg.append(f'<text class="txt-axis" font-size="10" x="{t_report}" y="{oy + 18}" text-anchor="middle">Звіт вимірювань</text>')

    svg.append(f'<line class="event-line" x1="{t_ho}" y1="{oy}" x2="{t_ho}" y2="135" />')
    svg.append(f'<text class="txt-axis" font-size="10" x="{t_ho}" y="{oy + 18}" text-anchor="middle">Перемикання (HO)</text>')

    svg.append('</svg>')
    out_path = os.path.join(IMG_DIR, "handover-a3-event-timeline.svg")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print(f"Generated: {out_path}")


def main():
    fig_cellular_topology()
    fig_rach_and_attach()
    fig_rrc_state_machine()
    fig_handover_timeline()


if __name__ == "__main__":
    main()
