# -*- coding: utf-8 -*-
"""Пост-лінкерний ліцензійний аудит прошивки мікроконтролера.

Пакет складається з чотирьох частин, і кожна відповідає одному кроку конвеєра:

* :mod:`sbom_audit.linkmap`  — читає мапу компонувальника й каже, ЩО справді у Flash;
* :mod:`sbom_audit.catalog`  — зіставляє об'єктні модулі з базою компонентів і судить політику;
* :mod:`sbom_audit.symbols`  — перехресна звірка через ``arm-none-eabi-nm``;
* :mod:`sbom_audit.report`   — CycloneDX-паспорт і файл атрибуції.

Точка входу для CI — скрипт ``firmware_sbom_scanner.py`` поруч із пакетом.
"""

TOOL_NAME = "firmware-sbom-scanner"
TOOL_VERSION = "1.4.0"

__all__ = ["TOOL_NAME", "TOOL_VERSION"]
