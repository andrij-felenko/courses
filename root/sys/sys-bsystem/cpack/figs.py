# -*- coding: utf-8 -*-
"""Генерація SVG-діаграм для теми cpack (CPack: збірка дистрибутива)."""

import os
import sys

# Підключення svgkit із кореневої папки scripts
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def fig_cpack_architecture():
    """Архітектура конвеєра CPack: етапи, проміжні каталоги та генератори."""
    w, h = 940, 360
    f = []

    # Колонка 1: Вихідні дані та генерація
    f.append(fitbox(20, 50, 200, 75, "CMakeLists.txt\ninstall() правила\ninclude(CPack)", size=13, fill="#eaf2f8", stroke="#2980b9", bold=True))
    f.append(arrow(220, 87, 260, 87))

    f.append(fitbox(260, 50, 190, 75, "Фаза генерації CMake\nГенерація CPackConfig.cmake\nта CPackSourceConfig.cmake", size=12, fill="#fdfefe", stroke=LINE))
    f.append(arrow(450, 87, 490, 87))

    f.append(fitbox(490, 50, 180, 75, "Виклик утиліти cpack\n(CLI або target package)\nЧитання конфігурації", size=12, fill="#fdfefe", stroke=LINE))
    f.append(arrow(670, 87, 710, 87))

    # Колонка 2: Staging дерево
    f.append(fitbox(710, 30, 210, 115, "Staging Directory\n_CPack_Packages/<Plat>/<Gen>/\n• Виклик cmake_install.cmake\n• Монтування DESTDIR\n• Структурування каталогів", size=12, fill="#fef9e7", stroke="#f39c12", bold=True))

    # Перехід до генераторів униз
    f.append(arrow(815, 145, 815, 185))

    # Блок розподілу генераторів
    f.append(fitbox(50, 185, 840, 45, "Двигун генераторів CPack (CPACK_GENERATOR / -G <Generator>)", size=14, fill="#eaeded", stroke=LINE, bold=True))

    # Стрілки від двигуна до конкретних форматів
    f.append(arrow(140, 230, 140, 265))
    f.append(arrow(340, 230, 340, 265))
    f.append(arrow(580, 230, 580, 265))
    f.append(arrow(800, 230, 800, 265))

    # Формати результатів
    f.append(fitbox(30, 265, 200, 75, "Архіви\nTGZ / TXZ / ZIP\nАвтономні тарболи\nБез зовнішніх утиліт", size=12, fill="#e8f8f5", stroke=FIELD))
    f.append(fitbox(250, 265, 200, 75, "Пакети Linux\nDEB (dpkg-deb / shlibs)\nRPM (rpmbuild / spec)\nСистемні менеджери", size=12, fill="#e8f8f5", stroke=FIELD))
    f.append(fitbox(480, 265, 200, 75, "Інсталятори Windows\nNSIS (.exe майстер)\nWIX (.msi база даних)\nРеєстр та ярлики", size=12, fill="#e8f8f5", stroke=FIELD))
    f.append(fitbox(700, 265, 210, 75, "Пакети macOS\nDragNDrop (.dmg образ)\nproductbuild (.pkg)\nBundle застосунки", size=12, fill="#e8f8f5", stroke=FIELD))

    render(os.path.join(IMG_DIR, "cpack-architecture.svg"), w, h, *f, title="Архітектура конвеєра збірки пакетів CPack")


def fig_cpack_component_mapping():
    """Модель компонентного пакування: правила install(), компоненти та вихідні пакети."""
    w, h = 920, 370
    f = []

    # Ліва колонка: Правила install()
    f.append(text(130, 55, "Правила install() у CMake", size=14, bold=True))
    f.append(fitbox(20, 75, 220, 50, "install(TARGETS app\n  COMPONENT Runtime)", size=12, fill="#fdfefe", stroke=LINE))
    f.append(fitbox(20, 135, 220, 50, "install(TARGETS lib\n  COMPONENT Runtime)", size=12, fill="#fdfefe", stroke=LINE))
    f.append(fitbox(20, 195, 220, 50, "install(FILES api.h\n  COMPONENT Development)", size=12, fill="#fdfefe", stroke=LINE))
    f.append(fitbox(20, 255, 220, 50, "install(DIRECTORY docs/\n  COMPONENT Documentation)", size=12, fill="#fdfefe", stroke=LINE))

    # Стрілки в центр
    f.append(arrow(240, 100, 310, 120))
    f.append(arrow(240, 160, 310, 130))
    f.append(arrow(240, 220, 310, 210))
    f.append(arrow(240, 280, 310, 290))

    # Центральна колонка: Граф компонентів CPack
    f.append(text(460, 55, "Декларація компонентів CPack", size=14, bold=True))
    f.append(fitbox(310, 85, 290, 70, "cpack_add_component(Runtime\n  DISPLAY_NAME \"Виконувані файли\"\n  REQUIRED)", size=12, fill="#eaf2f8", stroke="#2980b9", bold=True))
    f.append(fitbox(310, 175, 290, 70, "cpack_add_component(Development\n  DISPLAY_NAME \"Заголовки та CMake\"\n  DEPENDS Runtime)", size=12, fill="#fef9e7", stroke="#f39c12", bold=True))
    f.append(fitbox(310, 265, 290, 70, "cpack_add_component(Documentation\n  DISPLAY_NAME \"Документація API\"\n  GROUP Help)", size=12, fill="#f4f6f7", stroke=MUTED))

    # Залежність між компонентами
    f.append(line(455, 175, 455, 155, color=POS, sw=1.5, dash="4,3"))

    # Стрілки праворуч
    f.append(arrow(600, 120, 680, 110))
    f.append(arrow(600, 210, 680, 190))
    f.append(arrow(600, 300, 680, 280))

    # Права колонка: Вихідні пакети (Component Install)
    f.append(text(790, 55, "Згенеровані артефакти", size=14, bold=True))
    f.append(fitbox(680, 85, 220, 60, "app-1.0.0-Linux-Runtime.deb\n(або .rpm / .zip)\nВиконувані бінарники", size=12, fill="#e8f8f5", stroke=FIELD))
    f.append(fitbox(680, 165, 220, 65, "app-1.0.0-Linux-Development.deb\n(Depends: Runtime)\nЗаголовки, .cmake файли", size=12, fill="#e8f8f5", stroke=FIELD))
    f.append(fitbox(680, 255, 220, 60, "app-1.0.0-Linux-Docs.deb\n(Опційний пакет)\nHTML / man-сторінки", size=12, fill="#e8f8f5", stroke=FIELD))

    render(os.path.join(IMG_DIR, "cpack-component-mapping.svg"), w, h, *f, title="Відображення правил install() у незалежні пакети через компоненти")


def fig_cpack_package_lifecycle():
    """Життєвий цикл встановлення пакета та виконання скриптлетів DEB/RPM."""
    w, h = 920, 350
    f = []

    # Верхня доріжка: DEB (dpkg)
    f.append(fitbox(20, 60, 130, 45, "dpkg -i pkg.deb\nПочаток", size=12, fill="#fdfefe", stroke=LINE, bold=True))
    f.append(arrow(150, 82, 190, 82))

    f.append(fitbox(190, 55, 140, 55, "preinst\nЗупинка сервісу,\nперевірка версії", size=12, fill="#fdecea", stroke=POS, bold=True))
    f.append(arrow(330, 82, 370, 82))

    f.append(fitbox(370, 55, 150, 55, "Розпакування файлів\nЗапис файлів у /\n(FHS структура)", size=12, fill="#fef9e7", stroke="#f39c12"))
    f.append(arrow(520, 82, 560, 82))

    f.append(fitbox(560, 55, 150, 55, "postinst\nldconfig, systemctl\ndaemon-reload, старт", size=12, fill="#eaf2f8", stroke="#2980b9", bold=True))
    f.append(arrow(710, 82, 750, 82))

    f.append(fitbox(750, 55, 150, 55, "Тригери dpkg\nОновлення кешу\n(ldconfig, man-db)", size=12, fill="#e8f8f5", stroke=FIELD))

    # Розділювач
    f.append(line(20, 160, 900, 160, color=MUTED, sw=1, dash="5,5"))
    f.append(text(80, 150, "Формат DEB", size=13, color="#2980b9", bold=True))
    f.append(text(80, 200, "Формат RPM", size=13, color="#c0392b", bold=True))

    # Нижня доріжка: RPM (rpm / dnf)
    f.append(fitbox(20, 220, 130, 45, "rpm -ivh pkg.rpm\nПочаток", size=12, fill="#fdfefe", stroke=LINE, bold=True))
    f.append(arrow(150, 242, 190, 242))

    f.append(fitbox(190, 215, 140, 55, "%pre\nСтворення юзерів,\nперевірка конфліктів", size=12, fill="#fdecea", stroke=POS, bold=True))
    f.append(arrow(330, 242, 370, 242))

    f.append(fitbox(370, 215, 150, 55, "Розгортання файлів\nПеревірка хешів,\nзапис на диск", size=12, fill="#fef9e7", stroke="#f39c12"))
    f.append(arrow(520, 242, 560, 242))

    f.append(fitbox(560, 215, 150, 55, "%post\nЗапуск daemon-reload,\nстворення симлінків", size=12, fill="#eaf2f8", stroke="#2980b9", bold=True))
    f.append(arrow(710, 242, 750, 242))

    f.append(fitbox(750, 215, 150, 55, "%transfiletriggerin\nФайлові тригери\nдля спільних шляхів", size=12, fill="#e8f8f5", stroke=FIELD))

    render(os.path.join(IMG_DIR, "cpack-package-lifecycle.svg"), w, h, *f, title="Послідовність виконання скриптів життєвого циклу під час інсталяції пакетів")


if __name__ == "__main__":
    fig_cpack_architecture()
    fig_cpack_component_mapping()
    fig_cpack_package_lifecycle()
    print("Всі фігури згенеровано успішно.")
