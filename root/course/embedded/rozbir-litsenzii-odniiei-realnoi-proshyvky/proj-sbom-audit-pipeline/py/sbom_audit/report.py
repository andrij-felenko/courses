# -*- coding: utf-8 -*-
"""Два артефакти аудиту: машинний паспорт CycloneDX і людський файл атрибуції."""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

from . import TOOL_NAME, TOOL_VERSION
from .catalog import Catalog, Detection

# Простір імен для детермінованого serialNumber: та сама прошивка — той самий UUID.
_SBOM_NAMESPACE = uuid.UUID("6f2c1f0e-6a4c-5a3d-9b1e-2f7a4c9d8e10")


def _timestamp() -> str:
    """Час випуску, дружній до відтворюваних збірок (SOURCE_DATE_EPOCH)."""

    epoch = os.environ.get("SOURCE_DATE_EPOCH")
    if epoch and epoch.isdigit():
        moment = datetime.fromtimestamp(int(epoch), tz=timezone.utc)
    else:
        moment = datetime.now(timezone.utc)
    return moment.strftime("%Y-%m-%dT%H:%M:%SZ")


def _license_node(license_obj: dict) -> dict:
    """CycloneDX розрізняє SPDX-ідентифікатор, вираз і довільну назву.

    Пхати «Proprietary — Vendor EULA» у поле ``id`` не можна: валідатор схеми
    відкине паспорт, бо ``id`` приймає лише значення зі списку SPDX.
    """

    if "expression" in license_obj:
        return {"expression": license_obj["expression"]}
    if "id" in license_obj:
        return {"license": {"id": license_obj["id"]}}
    return {"license": {"name": license_obj["name"]}}


def build_sbom(catalog: Catalog,
               detections: dict[str, Detection],
               binary_hash: str,
               binary_name: str) -> dict:
    """Зібрати документ CycloneDX 1.5 з графом залежностей."""

    product = catalog.product
    root_ref = f"{product['name']}@{product.get('version', '0.0.0')}"

    components = []
    dependencies = [{"ref": root_ref, "dependsOn": []}]

    for comp_id, det in sorted(detections.items(), key=lambda kv: kv[1].component.name):
        comp = det.component
        ref = comp.purl
        components.append({
            "type": "library",
            "bom-ref": ref,
            "name": comp.name,
            "version": comp.version,
            "purl": comp.purl,
            "supplier": {"name": comp.supplier},
            "licenses": [_license_node(comp.license)],
            "properties": [
                {"name": "embedded:linked-objects", "value": str(len(det.objects))},
                {"name": "embedded:flash-bytes", "value": str(det.size)},
                {"name": "embedded:evidence", "value": "linker-map"},
            ] + ([{"name": "embedded:generated-by", "value": comp.generated_by}]
                 if comp.generated_by else []),
        })
        dependencies[0]["dependsOn"].append(ref)
        linked_deps = [catalog.components[d].purl
                       for d in comp.depends_on if d in detections]
        dependencies.append({"ref": ref, "dependsOn": linked_deps})

    return {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "serialNumber": f"urn:uuid:{uuid.uuid5(_SBOM_NAMESPACE, binary_hash)}",
        "version": 1,
        "metadata": {
            "timestamp": _timestamp(),
            "tools": [{"vendor": product.get("supplier", ""),
                       "name": TOOL_NAME, "version": TOOL_VERSION}],
            "component": {
                "type": product.get("type", "firmware"),
                "bom-ref": root_ref,
                "name": product["name"],
                "version": product.get("version", "0.0.0"),
                "supplier": {"name": product.get("supplier", "")},
                # Саме цей хеш підписує метапакет OTA: підміна байтів у Flash
                # робить паспорт недійсним.
                "hashes": [{"alg": "SHA-256", "content": binary_hash}],
                "properties": [{"name": "embedded:image-file", "value": binary_name}],
            },
        },
        "components": components,
        "dependencies": dependencies,
    }


def write_sbom(path: str | Path, document: dict) -> Path:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return out


def write_notice(path: str | Path,
                 catalog: Catalog,
                 detections: dict[str, Detection],
                 binary_hash: str) -> Path:
    """THIRD_PARTY_LICENSES.txt — те, що кладуть в інструкцію користувача."""

    product = catalog.product
    bar = "=" * 78
    lines = [
        bar,
        "ВІДОМОСТІ ПРО ЛІЦЕНЗІЇ СТОРОННЬОГО ПРОГРАМНОГО ЗАБЕЗПЕЧЕННЯ",
        f"Виріб    : {product['name']} {product.get('version', '')}",
        f"Образ    : SHA-256 {binary_hash}",
        f"Складено : {_timestamp()} інструментом {TOOL_NAME} {TOOL_VERSION}",
        "Перелік побудовано за мапою компонувальника, тобто описує саме той код,",
        "який фізично присутній у Flash-пам'яті виробу.",
        bar,
        "",
    ]

    ordered = sorted(detections.values(), key=lambda d: d.component.name.lower())
    for det in ordered:
        comp = det.component
        lines.append(f"Компонент : {comp.name}")
        lines.append(f"Версія    : {comp.version}")
        lines.append(f"Ліцензія  : {comp.license_text}")
        lines.append(f"Автор     : {comp.supplier}")
        lines.append(f"Ідентифікатор пакета : {comp.purl}")
        lines.append(f"У образі  : {len(det.objects)} об'єктних модулів, {det.size} байт")
        if comp.generated_notice:
            lines.append(f"Застереження генератора: {comp.generated_notice}")
        if comp.notice_required:
            lines.append("Повний текст ліцензії надається разом із виробом і за письмовим запитом.")
        lines.append("-" * 78)
        lines.append("")

    if not ordered:
        lines.append("Сторонніх компонентів у образі не виявлено.")
        lines.append("")

    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    return out
