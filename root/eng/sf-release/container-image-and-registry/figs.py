# -*- coding: utf-8 -*-
import sys, os

# Додаємо шлях до scripts/ у корені репозиторію (4 рівні вгору)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── Фіг. 1: Ієрархія сутностей OCI Image Format ─────────────────────────────
def fig_oci_image_hierarchy():
    W, H = 1040, 580
    p = []
    
    # Загальне тло
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    p.append(text(W / 2, 38, "Ієрархія сутностей OCI Image Format Specification", size=16, color="#0f172a", bold=True))
    p.append(text(W / 2, 58, "Дерево дескрипторів: від мультиархітектурного індексу до криптографічних блобів шарів", size=11, color="#64748b"))
    
    # Блок 1: Image Index (Fat Manifest)
    idx_x, idx_y, idx_w, idx_h = 30, 85, 260, 465
    p.append(rect(idx_x, idx_y, idx_w, idx_h, fill="#f8fafc", stroke="#6366f1", sw=1.6, rx=6))
    p.append(text(idx_x + idx_w / 2, idx_y + 24, "OCI Image Index", size=13.5, color="#4338ca", bold=True))
    p.append(text(idx_x + idx_w / 2, idx_y + 42, "application/vnd.oci.image.index.v1+json", size=9.5, color="#64748b"))
    
    p.append(rect(idx_x + 15, idx_y + 60, idx_w - 30, 120, fill="#ffffff", stroke="#818cf8", sw=1.2, rx=4))
    p.append(text(idx_x + idx_w / 2, idx_y + 78, "Дескриптор: Linux / amd64", size=11, color="#3730a3", bold=True))
    p.append(text(idx_x + idx_w / 2, idx_y + 96, "mediaType: image.manifest.v1+json", size=9.5, color="#334155"))
    p.append(text(idx_x + idx_w / 2, idx_y + 114, "digest: sha256:7f3b1a9...", size=9.5, color="#4338ca"))
    p.append(text(idx_x + idx_w / 2, idx_y + 132, "platform: { os: linux, arch: amd64 }", size=9.5, color="#64748b"))
    p.append(text(idx_x + idx_w / 2, idx_y + 150, "size: 7122 bytes", size=9.5, color="#64748b"))
    p.append(text(idx_x + idx_w / 2, idx_y + 168, "Цільовий маніфест x86_64", size=9.5, color="#059669"))
    
    p.append(rect(idx_x + 15, idx_y + 195, idx_w - 30, 120, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=4))
    p.append(text(idx_x + idx_w / 2, idx_y + 213, "Дескриптор: Linux / arm64", size=11, color="#475569", bold=True))
    p.append(text(idx_x + idx_w / 2, idx_y + 231, "mediaType: image.manifest.v1+json", size=9.5, color="#64748b"))
    p.append(text(idx_x + idx_w / 2, idx_y + 249, "digest: sha256:c94d2e8...", size=9.5, color="#64748b"))
    p.append(text(idx_x + idx_w / 2, idx_y + 267, "platform: { os: linux, arch: arm64 }", size=9.5, color="#64748b"))
    p.append(text(idx_x + idx_w / 2, idx_y + 285, "size: 7118 bytes", size=9.5, color="#64748b"))
    p.append(text(idx_x + idx_w / 2, idx_y + 303, "Маніфест для Apple Silicon/Graviton", size=9.5, color="#64748b"))
    
    p.append(rect(idx_x + 15, idx_y + 330, idx_w - 30, 110, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=4))
    p.append(text(idx_x + idx_w / 2, idx_y + 348, "Дескриптор: Windows / amd64", size=11, color="#475569", bold=True))
    p.append(text(idx_x + idx_w / 2, idx_y + 366, "mediaType: image.manifest.v1+json", size=9.5, color="#64748b"))
    p.append(text(idx_x + idx_w / 2, idx_y + 384, "digest: sha256:4a19fe3...", size=9.5, color="#64748b"))
    p.append(text(idx_x + idx_w / 2, idx_y + 402, "platform: { os: windows, arch: amd64 }", size=9.5, color="#64748b"))
    p.append(text(idx_x + idx_w / 2, idx_y + 422, "size: 8940 bytes", size=9.5, color="#64748b"))
    
    p.append(text(idx_x + idx_w / 2, idx_y + 454, "Єдине ім'я: myapp:v1.2.0", size=10, color="#1e293b", bold=True))
    
    # Блок 2: Image Manifest
    man_x, man_y, man_w, man_h = 330, 85, 300, 465
    p.append(rect(man_x, man_y, man_w, man_h, fill="#eff6ff", stroke="#2563eb", sw=1.6, rx=6))
    p.append(text(man_x + man_w / 2, man_y + 24, "OCI Image Manifest (linux/amd64)", size=13.5, color="#1d4ed8", bold=True))
    p.append(text(man_x + man_w / 2, man_y + 42, "application/vnd.oci.image.manifest.v1+json", size=9.5, color="#64748b"))
    
    # Config Descriptor
    p.append(rect(man_x + 15, man_y + 60, man_w - 30, 80, fill="#fef3c7", stroke="#d97706", sw=1.3, rx=4))
    p.append(text(man_x + man_w / 2, man_y + 80, "Config Descriptor (Метадані)", size=11, color="#b45309", bold=True))
    p.append(text(man_x + man_w / 2, man_y + 98, "mediaType: image.config.v1+json", size=9.5, color="#78350f"))
    p.append(text(man_x + man_w / 2, man_y + 116, "digest: sha256:5a8d9f4...", size=9.5, color="#b45309"))
    p.append(text(man_x + man_w / 2, man_y + 132, "size: 3450 bytes", size=9.5, color="#64748b"))
    
    # Layers Array
    p.append(rect(man_x + 15, man_y + 155, man_w - 30, 290, fill="#ffffff", stroke="#3b82f6", sw=1.2, rx=4))
    p.append(text(man_x + man_w / 2, man_y + 175, "Впорядкований масив шарів (layers)", size=11, color="#1e40af", bold=True))
    
    layers_data = [
        ("Шар 0: Базова ОС (Rootfs Base)", "sha256:e3b0c44...", "28.5 MB", "#059669"),
        ("Шар 1: Системні пакунки / libc", "sha256:1a84f09...", "14.2 MB", "#0284c7"),
        ("Шар 2: Залежності застосунку", "sha256:9c78d12...", "8.4 MB", "#7c3aed"),
        ("Шар 3: Бінарний файл сервісу", "sha256:3d4f56a...", "2.1 MB", "#db2777")
    ]
    for idx, (title, dig, sz, col) in enumerate(layers_data):
        ly = man_y + 195 + idx * 60
        p.append(rect(man_x + 25, ly, man_w - 50, 52, fill="#f8fafc", stroke=col, sw=1.1, rx=4))
        p.append(text(man_x + man_w / 2, ly + 16, title, size=10, color=col, bold=True))
        p.append(text(man_x + man_w / 2, ly + 32, f"digest: {dig}", size=9.5, color="#334155"))
        p.append(text(man_x + man_w / 2, ly + 46, f"layer.v1.tar+gzip | {sz}", size=9.5, color="#64748b"))
    
    p.append(text(man_x + man_w / 2, man_y + 454, "Фіксований порядок накладання 0 → 3", size=10, color="#1e293b", bold=True))
    
    # Блок 3: Image Config JSON
    cfg_x, cfg_y, cfg_w, cfg_h = 670, 85, 340, 220
    p.append(rect(cfg_x, cfg_y, cfg_w, cfg_h, fill="#fffbeb", stroke="#d97706", sw=1.6, rx=6))
    p.append(text(cfg_x + cfg_w / 2, cfg_y + 24, "Image Config JSON (Параметри рантайму)", size=13, color="#b45309", bold=True))
    p.append(text(cfg_x + cfg_w / 2, cfg_y + 42, "digest: sha256:5a8d9f4...", size=9.5, color="#78350f"))
    
    cfg_lines = [
        "architecture: 'amd64', os: 'linux'",
        "config: {",
        "  Env: ['PATH=/usr/local/bin:...', 'PORT=8080'],",
        "  Entrypoint: ['/app/server'],",
        "  WorkingDir: '/app', ExposedPorts: {'8080/tcp': {}}",
        "}",
        "rootfs: {",
        "  type: 'layers',",
        "  diff_ids: [sha256:u0..., sha256:u1..., sha256:u2..., sha256:u3...]",
        "}"
    ]
    p.append(rect(cfg_x + 15, cfg_y + 55, cfg_w - 30, 150, fill="#ffffff", stroke="#f59e0b", sw=1.0, rx=4))
    for idx, l in enumerate(cfg_lines):
        p.append(text(cfg_x + 25, cfg_y + 72 + idx * 14, l, size=9.5, color="#1e293b", anchor="start"))
    
    # Блок 4: Layer Blobs (Сховище блобів)
    blobs_x, blobs_y, blobs_w, blobs_h = 670, 320, 340, 230
    p.append(rect(blobs_x, blobs_y, blobs_w, blobs_h, fill="#ecfdf5", stroke="#059669", sw=1.6, rx=6))
    p.append(text(blobs_x + blobs_w / 2, blobs_y + 24, "Layer Tarball Blobs (CAS Сховище)", size=13, color="#047857", bold=True))
    p.append(text(blobs_x + blobs_w / 2, blobs_y + 42, "Стиснуті архіви відмінностей файлової системи", size=9.5, color="#64748b"))
    
    blob_boxes = [
        ("Layer 0 Blob (sha256:e3b0c44...)", "Alpine Rootfs: /bin, /etc, /lib, /usr", "#059669"),
        ("Layer 1 Blob (sha256:1a84f09...)", "Пакетні оновлення: libssl3, ca-certificates", "#0284c7"),
        ("Layer 2 Blob (sha256:9c78d12...)", "Залежності: node_modules або venv", "#7c3aed"),
        ("Layer 3 Blob (sha256:3d4f56a...)", "Виконуваний файл: /app/server", "#db2777")
    ]
    for idx, (head, desc, clr) in enumerate(blob_boxes):
        by = blobs_y + 58 + idx * 40
        p.append(rect(blobs_x + 15, by, blobs_w - 30, 34, fill="#ffffff", stroke=clr, sw=1.1, rx=4))
        p.append(text(blobs_x + 25, by + 14, head, size=9.5, color=clr, bold=True, anchor="start"))
        p.append(text(blobs_x + 25, by + 27, desc, size=9.5, color="#475569", anchor="start"))
    
    # Стрілки зв'язку
    p.append(arrow(idx_x + idx_w, idx_y + 120, man_x - 3, man_y + 120, color="#6366f1", sw=2.0))
    p.append(arrow(man_x + man_w, man_y + 100, cfg_x - 3, cfg_y + 100, color="#d97706", sw=2.0))
    p.append(arrow(man_x + man_w, man_y + 300, blobs_x - 3, blobs_y + 115, color="#059669", sw=2.0))
    
    render(os.path.join(OUT, "oci-image-hierarchy.svg"), W, H, *p)
    
    # Стрілки зв'язку
    p.append(arrow(idx_x + idx_w, idx_y + 120, man_x - 3, man_y + 120, color="#6366f1", sw=2.0))
    p.append(arrow(man_x + man_w, man_y + 100, cfg_x - 3, cfg_y + 100, color="#d97706", sw=2.0))
    p.append(arrow(man_x + man_w, man_y + 300, blobs_x - 3, blobs_y + 115, color="#059669", sw=2.0))
    
    render(os.path.join(OUT, "oci-image-hierarchy.svg"), W, H, *p)


# ── Фіг. 2: Content-Addressable Storage та дедуплікація ────────────────────────
def fig_content_addressable_storage():
    W, H = 1000, 520
    p = []
    
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    p.append(text(W / 2, 38, "Адресація за вмістом (CAS) та дедуплікація шарів", size=16, color="#0f172a", bold=True))
    p.append(text(W / 2, 58, "Спільні шари між різними образами зберігаються на диску та передаються мережею рівно один раз", size=11, color="#64748b"))
    
    # Лівий образ: auth-service:v2
    img1_x, img1_y, img1_w, img1_h = 30, 85, 260, 400
    p.append(rect(img1_x, img1_y, img1_w, img1_h, fill="#eff6ff", stroke="#2563eb", sw=1.6, rx=6))
    p.append(text(img1_x + img1_w / 2, img1_y + 24, "Образ: auth-service:v2", size=13, color="#1d4ed8", bold=True))
    p.append(text(img1_x + img1_w / 2, img1_y + 42, "Маніфест: sha256:aa11...", size=9.5, color="#64748b"))
    
    p.append(rect(img1_x + 15, img1_y + 65, img1_w - 30, 70, fill="#ecfdf5", stroke="#059669", sw=1.4, rx=4))
    p.append(text(img1_x + img1_w / 2, img1_y + 88, "Шар 1: Ubuntu 22.04 Base", size=11, color="#047857", bold=True))
    p.append(text(img1_x + img1_w / 2, img1_y + 106, "sha256:7b29a... (29.2 MB)", size=9.5, color="#334155"))
    p.append(text(img1_x + img1_w / 2, img1_y + 122, "Спільний базовий шар", size=9, color="#059669"))
    
    p.append(rect(img1_x + 15, img1_y + 145, img1_w - 30, 70, fill="#fffbeb", stroke="#d97706", sw=1.4, rx=4))
    p.append(text(img1_x + img1_w / 2, img1_y + 168, "Шар 2: OpenSSL + Curl", size=11, color="#b45309", bold=True))
    p.append(text(img1_x + img1_w / 2, img1_y + 186, "sha256:3f48c... (12.1 MB)", size=9.5, color="#334155"))
    p.append(text(img1_x + img1_w / 2, img1_y + 202, "Спільні утиліти безпеки", size=9, color="#b45309"))
    
    p.append(rect(img1_x + 15, img1_y + 225, img1_w - 30, 70, fill="#fdf2f8", stroke="#db2777", sw=1.4, rx=4))
    p.append(text(img1_x + img1_w / 2, img1_y + 248, "Шар 3: Go Runtime & Auth", size=11, color="#be185d", bold=True))
    p.append(text(img1_x + img1_w / 2, img1_y + 266, "sha256:1198a... (18.4 MB)", size=9.5, color="#334155"))
    p.append(text(img1_x + img1_w / 2, img1_y + 282, "Унікальний для auth", size=9, color="#be185d"))
    
    p.append(text(img1_x + img1_w / 2, img1_y + 335, "Сумарний віртуальний розмір:", size=10, color="#475569"))
    p.append(text(img1_x + img1_w / 2, img1_y + 355, "29.2 + 12.1 + 18.4 = 59.7 MB", size=11, color="#1e293b", bold=True))
    
    # Правий образ: payment-api:v4
    img2_x, img2_y, img2_w, img2_h = 710, 85, 260, 400
    p.append(rect(img2_x, img2_y, img2_w, img2_h, fill="#eff6ff", stroke="#2563eb", sw=1.6, rx=6))
    p.append(text(img2_x + img2_w / 2, img2_y + 24, "Образ: payment-api:v4", size=13, color="#1d4ed8", bold=True))
    p.append(text(img2_x + img2_w / 2, img2_y + 42, "Маніфест: sha256:bb22...", size=9.5, color="#64748b"))
    
    p.append(rect(img2_x + 15, img2_y + 65, img2_w - 30, 70, fill="#ecfdf5", stroke="#059669", sw=1.4, rx=4))
    p.append(text(img2_x + img2_w / 2, img2_y + 88, "Шар 1: Ubuntu 22.04 Base", size=11, color="#047857", bold=True))
    p.append(text(img2_x + img2_w / 2, img2_y + 106, "sha256:7b29a... (29.2 MB)", size=9.5, color="#334155"))
    p.append(text(img2_x + img2_w / 2, img2_y + 122, "Спільний базовий шар", size=9, color="#059669"))
    
    p.append(rect(img2_x + 15, img2_y + 145, img2_w - 30, 70, fill="#fffbeb", stroke="#d97706", sw=1.4, rx=4))
    p.append(text(img2_x + img2_w / 2, img2_y + 168, "Шар 2: OpenSSL + Curl", size=11, color="#b45309", bold=True))
    p.append(text(img2_x + img2_w / 2, img2_y + 186, "sha256:3f48c... (12.1 MB)", size=9.5, color="#334155"))
    p.append(text(img2_x + img2_w / 2, img2_y + 202, "Спільні утиліти безпеки", size=9, color="#b45309"))
    
    p.append(rect(img2_x + 15, img2_y + 225, img2_w - 30, 70, fill="#f5f3ff", stroke="#7c3aed", sw=1.4, rx=4))
    p.append(text(img2_x + img2_w / 2, img2_y + 248, "Шар 3: Node.js & Payment", size=11, color="#6d28d9", bold=True))
    p.append(text(img2_x + img2_w / 2, img2_y + 266, "sha256:8823f... (42.6 MB)", size=9.5, color="#334155"))
    p.append(text(img2_x + img2_w / 2, img2_y + 282, "Унікальний для payment", size=9, color="#6d28d9"))
    
    p.append(text(img2_x + img2_w / 2, img2_y + 335, "Сумарний віртуальний розмір:", size=10, color="#475569"))
    p.append(text(img2_x + img2_w / 2, img2_y + 355, "29.2 + 12.1 + 42.6 = 83.9 MB", size=11, color="#1e293b", bold=True))
    
    # Центр: Content-Addressable Storage Хоста (/var/lib/containerd/io.containerd.content.v1.content/blobs/sha256/)
    cas_x, cas_y, cas_w, cas_h = 320, 85, 360, 400
    p.append(rect(cas_x, cas_y, cas_w, cas_h, fill="#f8fafc", stroke="#475569", sw=1.8, rx=6))
    p.append(text(cas_x + cas_w / 2, cas_y + 24, "Локальне сховище блобів (CAS Pool)", size=13.5, color="#0f172a", bold=True))
    p.append(text(cas_x + cas_w / 2, cas_y + 42, "Ідентифікатор = Ключ = SHA256(Вміст)", size=10, color="#64748b"))
    
    cas_blobs = [
        ("Blob sha256:7b29a...", "Ubuntu 22.04 Rootfs (29.2 MB)", "Ref count: 2 (auth + payment)", "#059669", "#ecfdf5"),
        ("Blob sha256:3f48c...", "OpenSSL + Curl Layer (12.1 MB)", "Ref count: 2 (auth + payment)", "#d97706", "#fffbeb"),
        ("Blob sha256:1198a...", "Auth Go Service (18.4 MB)", "Ref count: 1 (тільки auth)", "#db2777", "#fdf2f8"),
        ("Blob sha256:8823f...", "Payment Node.js App (42.6 MB)", "Ref count: 1 (тільки payment)", "#7c3aed", "#f5f3ff")
    ]
    for idx, (bname, bdesc, bref, bstrk, bbg) in enumerate(cas_blobs):
        by = cas_y + 65 + idx * 72
        p.append(rect(cas_x + 15, by, cas_w - 30, 62, fill=bbg, stroke=bstrk, sw=1.3, rx=4))
        p.append(text(cas_x + 25, by + 18, bname, size=10.5, color=bstrk, bold=True, anchor="start"))
        p.append(text(cas_x + 25, by + 34, bdesc, size=9.5, color="#334155", anchor="start"))
        p.append(text(cas_x + 25, by + 50, bref, size=9, color="#64748b", anchor="start"))
    
    p.append(text(cas_x + cas_w / 2, cas_y + 365, "Фактичний обсяг на диску хоста:", size=10.5, color="#1e293b", bold=True))
    p.append(text(cas_x + cas_w / 2, cas_y + 383, "29.2 + 12.1 + 18.4 + 42.6 = 102.3 MB (замість 143.6 MB)", size=10.5, color="#059669", bold=True))
    
    # Стрілки посилань
    p.append(arrow(img1_x + img1_w, img1_y + 100, cas_x + 12, cas_y + 96, color="#059669", sw=1.8))
    p.append(arrow(img1_x + img1_w, img1_y + 180, cas_x + 12, cas_y + 168, color="#d97706", sw=1.8))
    p.append(arrow(img1_x + img1_w, img1_y + 260, cas_x + 12, cas_y + 240, color="#db2777", sw=1.8))
    
    p.append(arrow(img2_x, img2_y + 100, cas_x + cas_w - 12, cas_y + 96, color="#059669", sw=1.8))
    p.append(arrow(img2_x, img2_y + 180, cas_x + cas_w - 12, cas_y + 168, color="#d97706", sw=1.8))
    p.append(arrow(img2_x, img2_y + 260, cas_x + cas_w - 12, cas_y + 312, color="#7c3aed", sw=1.8))
    
    render(os.path.join(OUT, "content-addressable-storage.svg"), W, H, *p)


# ── Фіг. 3: Хронологія та протокол OCI Distribution Spec Pull ─────────────────
def fig_distribution_pull_protocol():
    W, H = 1060, 560
    p = []
    
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    p.append(text(W / 2, 38, "Хронологія та протокол OCI Distribution Specification (Pull Workflow)", size=16, color="#0f172a", bold=True))
    p.append(text(W / 2, 58, "Послідовність викликів HTTP REST API v2, перевірка автентифікації, отримання маніфесту та блобів", size=11, color="#64748b"))
    
    # Лінії учасників
    client_x = 120
    auth_x = 400
    reg_x = 680
    cdn_x = 940
    
    top_y = 95
    bot_y = 525
    
    for x_pos, name, clr in [
        (client_x, "Клієнт (containerd / docker)", "#2563eb"),
        (auth_x, "Auth Service (Token Server)", "#7c3aed"),
        (reg_x, "OCI Registry (API V2)", "#059669"),
        (cdn_x, "Blob Storage / CDN (S3)", "#d97706")
    ]:
        p.append(rect(x_pos - 85, top_y - 25, 170, 36, fill="#f8fafc", stroke=clr, sw=1.4, rx=6))
        p.append(text(x_pos, top_y - 7, name, size=11, color=clr, bold=True))
        p.append(line(x_pos, top_y + 12, x_pos, bot_y, color="#cbd5e1", sw=1.2, dash="4,4"))
    
    # Кроки протоколу
    # 1. Запит без токену
    y1 = 135
    p.append(arrow(client_x, y1, reg_x, y1, color="#2563eb", sw=1.6))
    p.append(text((client_x + reg_x) / 2, y1 - 8, "1. GET /v2/myorg/app/manifests/v1.0 (Accept: oci.manifest.v1+json)", size=9.5, color="#1e293b"))
    
    # 2. Відповідь 401 Unauthorized
    y2 = 175
    p.append(arrow(reg_x, y2, client_x, y2, color="#dc2626", sw=1.6))
    p.append(text((client_x + reg_x) / 2, y2 - 8, "2. 401 Unauthorized (Www-Authenticate: Bearer realm=\"https://auth...\", service=\"registry\")", size=9.5, color="#dc2626"))
    
    # 3. Запит токену
    y3 = 215
    p.append(arrow(client_x, y3, auth_x, y3, color="#7c3aed", sw=1.6))
    p.append(text((client_x + auth_x) / 2, y3 - 8, "3. GET /token?service=registry&scope=repository:myorg/app:pull", size=9.5, color="#6d28d9"))
    
    # 4. Видача JWT токену
    y4 = 250
    p.append(arrow(auth_x, y4, client_x, y4, color="#7c3aed", sw=1.6))
    p.append(text((client_x + auth_x) / 2, y4 - 8, "4. 200 OK { token: \"eyJhbGciOi...\" }", size=9.5, color="#059669"))
    
    # 5. Повторний запит маніфесту з Bearer
    y5 = 290
    p.append(arrow(client_x, y5, reg_x, y5, color="#2563eb", sw=1.6))
    p.append(text((client_x + reg_x) / 2, y5 - 8, "5. GET /v2/myorg/app/manifests/v1.0 (Authorization: Bearer eyJ...)", size=9.5, color="#1e293b"))
    
    # 6. Відповідь з маніфестом
    y6 = 330
    p.append(arrow(reg_x, y6, client_x, y6, color="#059669", sw=1.6))
    p.append(text((client_x + reg_x) / 2, y6 - 8, "6. 200 OK (Docker-Content-Digest: sha256:7f3b..., JSON: {config, layers: [L1, L2]})", size=9.5, color="#047857", bold=True))
    
    # Локальний diff: перевірка наявності L1 в CAS
    y_local = 365
    p.append(rect(client_x - 70, y_local - 10, 140, 22, fill="#ecfdf5", stroke="#059669", sw=1.0, rx=4))
    p.append(text(client_x, y_local + 5, "L1 знайдено в кеші! (Skip)", size=9.5, color="#047857", bold=True))
    
    # 7. HEAD перевірка відсутнього блобу L2
    y7 = 395
    p.append(arrow(client_x, y7, reg_x, y7, color="#2563eb", sw=1.4))
    p.append(text((client_x + reg_x) / 2, y7 - 8, "7. HEAD /v2/myorg/app/blobs/sha256:3d4f56... (Перевірка розміру)", size=9.5, color="#1e293b"))
    
    # 8. Відповідь 200 OK Content-Length
    y8 = 425
    p.append(arrow(reg_x, y8, client_x, y8, color="#059669", sw=1.4))
    p.append(text((client_x + reg_x) / 2, y8 - 8, "8. 200 OK (Content-Length: 2150490, Content-Type: application/octet-stream)", size=9.5, color="#059669"))
    
    # 9. GET блобу (з редиректом)
    y9 = 455
    p.append(arrow(client_x, y9, reg_x, y9, color="#2563eb", sw=1.6))
    p.append(text((client_x + reg_x) / 2, y9 - 8, "9. GET /v2/myorg/app/blobs/sha256:3d4f56...", size=9.5, color="#1e293b"))
    
    # 10. 307 Temporary Redirect на S3/CDN
    y10 = 485
    p.append(arrow(reg_x, y10, client_x, y10, color="#d97706", sw=1.6))
    p.append(text((client_x + reg_x) / 2, y10 - 8, "10. 307 Temporary Redirect (Location: https://s3.amazonaws.com/registry-blobs/...)", size=9.5, color="#b45309"))
    
    # 11. Пряме завантаження з CDN
    y11 = 515
    p.append(arrow(client_x, y11, cdn_x, y11, color="#d97706", sw=1.8))
    p.append(text((client_x + cdn_x) / 2, y11 - 8, "11. GET https://s3... → 200 OK (Потокове завантаження тарболу + Streaming SHA256)", size=9.5, color="#b45309", bold=True))
    
    render(os.path.join(OUT, "distribution-pull-protocol.svg"), W, H, *p)


# ── Фіг. 4: Монтаж шарів через OverlayFS ──────────────────────────────────────
def fig_overlayfs_layer_mounting():
    W, H = 1040, 540
    p = []
    
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    p.append(text(W / 2, 38, "Монтаж та композиція шарів у ядрі Linux через OverlayFS", size=16, color="#0f172a", bold=True))
    p.append(text(W / 2, 58, "Об'єднання незмінних стеків lowerdir, семантика Copy-Up та видалення через whiteouts", size=11, color="#64748b"))
    
    # Ліва колонка: Рівні файлової системи (OverlayFS Directories)
    col_x, col_y, col_w, col_h = 30, 85, 470, 430
    p.append(rect(col_x, col_y, col_w, col_h, fill="#f8fafc", stroke="#64748b", sw=1.6, rx=6))
    p.append(text(col_x + col_w / 2, col_y + 24, "Структура каталогів на хості (Storage Driver)", size=13.5, color="#1e293b", bold=True))
    
    # Upperdir
    p.append(rect(col_x + 15, col_y + 40, col_w - 30, 85, fill="#fef2f2", stroke="#dc2626", sw=1.4, rx=4))
    p.append(text(col_x + 25, col_y + 58, "upperdir (Контейнерний шар Read-Write)", size=11.5, color="#b91c1c", bold=True, anchor="start"))
    p.append(text(col_x + 25, col_y + 76, "• /etc/config.json (Створено новий файл конфігурації)", size=9.5, color="#334155", anchor="start"))
    p.append(text(col_x + 25, col_y + 92, "• /var/log/app.log (Запис логів процесу)", size=9.5, color="#334155", anchor="start"))
    p.append(text(col_x + 25, col_y + 108, "• /bin/.wh.old_tool (Whiteout: видалення утиліти з нижнього шару)", size=9.5, color="#dc2626", bold=True, anchor="start"))
    
    # Workdir
    p.append(rect(col_x + 15, col_y + 135, col_w - 30, 45, fill="#fffbeb", stroke="#d97706", sw=1.2, rx=4))
    p.append(text(col_x + 25, col_y + 154, "workdir (Службовий каталог ядра для атомарних операцій Copy-Up)", size=10.5, color="#b45309", bold=True, anchor="start"))
    p.append(text(col_x + 25, col_y + 170, "Порожній у стані спокою; гарантує транзакційність мутацій", size=9.5, color="#64748b", anchor="start"))
    
    # Lowerdir Stack
    p.append(rect(col_x + 15, col_y + 190, col_w - 30, 225, fill="#eff6ff", stroke="#2563eb", sw=1.4, rx=4))
    p.append(text(col_x + 25, col_y + 210, "lowerdir stack (Незмінні шари образу Read-Only)", size=11.5, color="#1d4ed8", bold=True, anchor="start"))
    
    lower_layers = [
        ("Layer 3: /app/server (Бінарник застосунку v1.0.0)", "sha256:3d4f56..."),
        ("Layer 2: /lib/libssl.so, /lib/libcrypto.so", "sha256:9c78d1..."),
        ("Layer 1: /bin/old_tool (Застаріла утиліта з базового шару)", "sha256:1a84f0..."),
        ("Layer 0: /bin/sh, /etc/passwd, /lib/ld-musl-x86_64.so", "sha256:e3b0c4...")
    ]
    for idx, (lname, ldigest) in enumerate(lower_layers):
        ly = col_y + 225 + idx * 46
        p.append(rect(col_x + 25, ly, col_w - 50, 40, fill="#ffffff", stroke="#93c5fd", sw=1.1, rx=4))
        p.append(text(col_x + 35, ly + 16, lname, size=9.5, color="#0f172a", bold=True, anchor="start"))
        p.append(text(col_x + 35, ly + 32, f"digest: {ldigest} (RO)", size=9.5, color="#64748b", anchor="start"))
    
    # Права колонка: Merged View (Результат монтування)
    mrg_x, mrg_y, mrg_w, mrg_h = 540, 85, 470, 430
    p.append(rect(mrg_x, mrg_y, mrg_w, mrg_h, fill="#ecfdf5", stroke="#059669", sw=1.6, rx=6))
    p.append(text(mrg_x + mrg_w / 2, mrg_y + 24, "merged dir — Єдина точка монтування rootfs контейнера", size=13.5, color="#047857", bold=True))
    p.append(text(mrg_x + mrg_w / 2, mrg_y + 42, "Те, що бачить процес контейнера після pivot_root()", size=10, color="#64748b"))
    
    merged_items = [
        ("/app/server", "Видно з Layer 3 (Read-Only)", "#1e40af", "#eff6ff"),
        ("/etc/config.json", "Створено в upperdir (Read-Write)", "#b91c1c", "#fef2f2"),
        ("/etc/passwd", "Видно з Layer 0 (Read-Only)", "#1e40af", "#eff6ff"),
        ("/lib/libssl.so", "Видно з Layer 2 (Read-Only)", "#1e40af", "#eff6ff"),
        ("/var/log/app.log", "Записується в upperdir (Read-Write)", "#b91c1c", "#fef2f2"),
        ("/bin/sh", "Видно з Layer 0 (Read-Only)", "#1e40af", "#eff6ff"),
        ("/bin/old_tool", "ПРИХОВАНО через .wh.old_tool у upperdir!", "#dc2626", "#fef2f2")
    ]
    for idx, (ipath, inote, iclr, ibg) in enumerate(merged_items):
        iy = mrg_y + 60 + idx * 46
        p.append(rect(mrg_x + 20, iy, mrg_w - 40, 38, fill=ibg, stroke=iclr, sw=1.2, rx=4))
        p.append(text(mrg_x + 35, iy + 16, ipath, size=10.5, color=iclr, bold=True, anchor="start"))
        p.append(text(mrg_x + 35, iy + 30, inote, size=9.5, color="#475569", anchor="start"))
    
    p.append(rect(mrg_x + 20, mrg_y + 385, mrg_w - 40, 32, fill="#ffffff", stroke="#059669", sw=1.2, rx=4))
    p.append(text(mrg_x + mrg_w / 2, mrg_y + 405, "mount -t overlay overlay -o lowerdir=L3:L2:L1:L0,upperdir=U,workdir=W merged", size=9.5, color="#047857", bold=True))
    
    # Стрілка злиття
    p.append(arrow(col_x + col_w + 3, col_y + 215, mrg_x - 3, mrg_y + 215, color="#059669", sw=2.2))
    p.append(text((col_x + col_w + mrg_x) / 2, col_y + 195, "VFS", size=11, color="#047857", bold=True))
    p.append(text((col_x + col_w + mrg_x) / 2, col_y + 235, "Композиція", size=9.5, color="#64748b"))
    
    render(os.path.join(OUT, "overlayfs-layer-mounting.svg"), W, H, *p)


def main():
    fig_oci_image_hierarchy()
    fig_content_addressable_storage()
    fig_distribution_pull_protocol()
    fig_overlayfs_layer_mounting()
    print("Generated 4 SVG figures successfully.")

if __name__ == "__main__":
    main()
