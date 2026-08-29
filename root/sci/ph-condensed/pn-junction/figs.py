# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

def fig_meet():
    W, H = 760, 320
    f = []
    f.append(text(380, 30, 'Зустріч p- та n-областей до контакту', size=15, bold=True))
    f.append(rect(50, 60, 310, 220, fill='#fefce8', stroke='#eab308', rx=8))
    f.append(text(205, 90, 'p-область (акцептори Na)', size=14, bold=True, color='#854d0e'))
    f.append(text(205, 130, 'Багато дірок h+', size=12, color='#713f12'))
    f.append(text(205, 160, 'Нерухомі іони B-', size=12, color='#854d0e'))
    
    f.append(rect(400, 60, 310, 220, fill='#eff6ff', stroke='#3b82f6', rx=8))
    f.append(text(555, 90, 'n-область (донори Nd)', size=14, bold=True, color='#1e40af'))
    f.append(text(555, 130, 'Багато електронів e-', size=12, color='#1e3a8a'))
    f.append(text(555, 160, 'Нерухомі іони P+', size=12, color='#1e40af'))
    render(os.path.join(OUT, 'meet.svg'), W, H, '\n'.join(f))

def fig_diffuse_recombine():
    W, H = 760, 320
    f = []
    f.append(text(380, 30, 'Дифузія та рекомбінація на металургійній межі', size=15, bold=True))
    f.append(rect(40, 60, 680, 230, fill='#f8fafc', stroke=MUTED, rx=8))
    f.append(line(380, 60, 380, 290, color=MUTED, sw=1.5, dash='3 3'))
    f.append(text(210, 90, 'p-тип', size=14, bold=True, color='#854d0e'))
    f.append(text(550, 90, 'n-тип', size=14, bold=True, color='#1e40af'))
    f.append(line(240, 160, 360, 160, color='#f59e0b', sw=2))
    f.append(text(300, 145, 'Дифузія h+ →', size=12, color='#b45309'))
    f.append(line(520, 190, 400, 190, color='#3b82f6', sw=2))
    f.append(text(460, 215, '← Дифузія e-', size=12, color='#1d4ed8'))
    render(os.path.join(OUT, 'diffuse-recombine.svg'), W, H, '\n'.join(f))

def fig_depletion_region():
    W, H = 760, 320
    f = []
    f.append(text(380, 30, 'Область просторового заряду (ОПЗ / Depletion Region)', size=15, bold=True))
    f.append(rect(40, 60, 680, 230, fill='#f8fafc', stroke=MUTED, rx=8))
    f.append(rect(280, 60, 200, 230, fill='#fef2f2', stroke='#ef4444', sw=2))
    f.append(line(380, 60, 380, 290, color=MUTED, sw=1.5, dash='3 3'))
    f.append(text(160, 100, 'Нейтральна p-база', size=13, bold=True, color='#854d0e'))
    f.append(text(600, 100, 'Нейтральна n-база', size=13, bold=True, color='#1e40af'))
    f.append(text(330, 150, 'B-', size=16, bold=True, color='#dc2626'))
    f.append(text(430, 150, 'P+', size=16, bold=True, color='#2563eb'))
    f.append(text(380, 250, 'ОПЗ (збіднений шар W)', size=13, bold=True, color='#b91c1c'))
    render(os.path.join(OUT, 'depletion-region.svg'), W, H, '\n'.join(f))

def fig_builtin_field():
    W, H = 760, 320
    f = []
    f.append(text(380, 30, 'Вбудоване електричне поле та дрейфовий струм', size=15, bold=True))
    f.append(rect(40, 60, 680, 230, fill='#f8fafc', stroke=MUTED, rx=8))
    f.append(rect(280, 60, 200, 230, fill='#fef2f2', stroke='#ef4444', sw=1.5))
    f.append(line(450, 160, 310, 160, color='#dc2626', sw=3))
    f.append(text(380, 140, '← Вбудоване поле E_bi', size=13, bold=True, color='#dc2626'))
    f.append(text(380, 220, 'Дрейф протидіє дифузії', size=12, color=MUTED))
    render(os.path.join(OUT, 'builtin-field.svg'), W, H, '\n'.join(f))

def fig_barrier():
    W, H = 760, 340
    f = []
    f.append(text(380, 30, 'Вбудований потенційний бар\'єр V_bi', size=15, bold=True))
    f.append(rect(40, 60, 680, 250, fill='#f8fafc', stroke=MUTED, rx=8))
    f.append(line(80, 120, 280, 120, color='#3b82f6', sw=3))
    f.append(line(280, 120, 480, 220, color='#3b82f6', sw=3))
    f.append(line(480, 220, 680, 220, color='#3b82f6', sw=3))
    f.append(text(180, 100, 'Ec (p-сторона)', size=12, bold=True))
    f.append(text(580, 245, 'Ec (n-сторона)', size=12, bold=True))
    f.append(line(530, 120, 530, 220, color='#ef4444', sw=2))
    f.append(text(580, 170, 'q V_bi бар\'єр', size=12, bold=True, color='#dc2626'))
    render(os.path.join(OUT, 'barrier.svg'), W, H, '\n'.join(f))

def fig_equilibrium():
    W, H = 760, 320
    f = []
    f.append(text(380, 30, 'Динамічна рівновага струмів у PN-переході', size=15, bold=True))
    f.append(rect(40, 60, 680, 230, fill='#f8fafc', stroke=MUTED, rx=8))
    f.append(text(380, 110, 'J_diff (дифузія) = J_drift (дрейф)', size=15, bold=True, color='#1e3a8a'))
    f.append(text(380, 160, 'Сумарний струм у рівновазі: J_total = 0', size=14, bold=True, color='#047857'))
    f.append(text(380, 210, 'Рівень Фермі Ef = const по всій структурі', size=13, color=MUTED))
    render(os.path.join(OUT, 'equilibrium.svg'), W, H, '\n'.join(f))

if __name__ == '__main__':
    fig_meet()
    fig_diffuse_recombine()
    fig_depletion_region()
    fig_builtin_field()
    fig_barrier()
    fig_equilibrium()
