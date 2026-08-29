# -*- coding: utf-8 -*-
"""База відомих компонентів, зіставлення з модулями з мапи й політика ліцензій."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from .linkmap import LinkedObject, MapReport


class CatalogError(RuntimeError):
    """Конфіг компонентів зламаний — конвеєр зупиняємо, а не вгадуємо."""


@dataclass
class Finding:
    code: str
    message: str
    severity: str = "warning"        # "warning" | "info"


@dataclass
class Component:
    id: str
    name: str
    version: str
    supplier: str
    purl: str
    license: dict                    # {"id"|"name"|"expression": ...}
    patterns: list[re.Pattern]
    symbol_prefixes: list[str] = field(default_factory=list)
    depends_on: list[str] = field(default_factory=list)
    notice_required: bool = True
    generated_by: str | None = None
    generated_notice: str | None = None

    @property
    def license_text(self) -> str:
        return (self.license.get("id")
                or self.license.get("expression")
                or self.license.get("name", "UNKNOWN"))


@dataclass
class Detection:
    component: Component
    objects: list[LinkedObject] = field(default_factory=list)

    @property
    def size(self) -> int:
        return sum(o.size for o in self.objects)


class Catalog:
    """Конфіг компонентів у пам'яті: компоненти, політика, зіставлення."""

    def __init__(self, data: dict, source: Path) -> None:
        self.source = source
        self.product = data.get("product") or {}
        if not self.product.get("name"):
            raise CatalogError(f"{source}: у блоці product немає name")

        policy = data.get("policy") or {}
        self.banned_ids: set[str] = set(policy.get("banned_license_ids", []))
        self.allowed_exceptions: set[str] = set(policy.get("allowed_exceptions", []))
        self.watch_prefixes: dict[str, str] = dict(policy.get("watch_symbol_prefixes", {}))
        self.first_party: list[re.Pattern] = [
            _compile(p, source, "policy.first_party_patterns")
            for p in policy.get("first_party_patterns", [])
        ]

        raw_components = data.get("components") or {}
        if not raw_components:
            raise CatalogError(f"{source}: порожній список компонентів")

        self.components: dict[str, Component] = {}
        for comp_id, raw in raw_components.items():
            self.components[comp_id] = _build_component(comp_id, raw, source)

        for comp in self.components.values():
            for dep in comp.depends_on:
                if dep not in self.components:
                    raise CatalogError(
                        f"{source}: компонент '{comp.id}' залежить від невідомого '{dep}'"
                    )

    # ---------------------------------------------------------------- завантаження

    @classmethod
    def load(cls, path: str | Path) -> "Catalog":
        p = Path(path)
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except FileNotFoundError as exc:
            raise CatalogError(f"конфіга компонентів немає: {p}") from exc
        except json.JSONDecodeError as exc:
            raise CatalogError(f"{p}: не JSON (рядок {exc.lineno}, {exc.msg})") from exc
        return cls(data, p)

    # ---------------------------------------------------------------- зіставлення

    def attribute(self, report: MapReport) -> tuple[dict[str, Detection], list[Finding]]:
        """Розкласти модулі з мапи по компонентах; повернути ще й зауваження."""

        detections: dict[str, Detection] = {}
        findings: list[Finding] = []

        for obj in report.objects_sorted():
            hits = [c for c in self.components.values() if _matches(c, obj)]

            if not hits:
                if not any(p.search(obj.display) for p in self.first_party):
                    findings.append(Finding(
                        "UNATTRIBUTED_OBJECT",
                        f"модуль {obj.display} ({obj.size} Б) не належить ані нашому коду, "
                        f"ані жодному задекларованому компоненту",
                    ))
                continue

            if len(hits) > 1:
                findings.append(Finding(
                    "AMBIGUOUS_OBJECT",
                    f"модуль {obj.display} підпадає під шаблони кількох компонентів "
                    f"({', '.join(h.id for h in hits)}); зараховано до '{hits[0].id}' — "
                    f"уточніть object_patterns у {self.source.name}",
                ))

            detections.setdefault(hits[0].id, Detection(hits[0])).objects.append(obj)

        findings.extend(self._check_dependencies(detections))
        findings.extend(self._notes(detections))
        findings.extend(_override_notes(report, detections))
        return detections, findings

    def _check_dependencies(self, detections: dict[str, Detection]) -> list[Finding]:
        """Транзитивні рівні: жоден проміжний компонент не має випасти з паспорта."""

        out: list[Finding] = []
        for det in list(detections.values()):
            for dep_id in det.component.depends_on:
                if dep_id in detections:
                    continue
                dep = self.components[dep_id]
                out.append(Finding(
                    "TRANSITIVE_DEPENDENCY_NOT_LINKED",
                    f"'{det.component.name}' задекларовано як споживача '{dep.name}', "
                    f"але жодного модуля '{dep_id}' у мапі немає: або шаблони застаріли, "
                    f"або компонент зібрано з іншою конфігурацією",
                ))
        return out

    def _notes(self, detections: dict[str, Detection]) -> list[Finding]:
        out: list[Finding] = []
        for det in detections.values():
            if det.component.generated_by:
                out.append(Finding(
                    "GENERATED_CODE_NOTICE",
                    f"{det.component.name}: код від {det.component.generated_by} — "
                    f"ліцензійні шапки в згенерованих файлах зберігати обов'язково",
                    severity="info",
                ))
        return out

    # ---------------------------------------------------------------- політика

    def violations(self, detections: dict[str, Detection]) -> list[str]:
        """Заборонені ліцензії серед РЕАЛЬНО злінкованих компонентів."""

        out: list[str] = []
        for det in detections.values():
            banned = self._banned_reason(det.component.license)
            if banned:
                out.append(
                    f"{det.component.name} {det.component.version} — {banned} "
                    f"({det.size} Б у Flash, {len(det.objects)} модулів)"
                )
        return out

    def _banned_reason(self, license_obj: dict) -> str | None:
        """Розібрати SPDX-вираз: виняток runtime-бібліотеки знімає заборону."""

        expression = license_obj.get("expression")
        single = license_obj.get("id")

        if single and single in self.banned_ids:
            return f"заборонена ліцензія {single}"

        if expression:
            tokens = re.split(r"[()\s]+", expression)
            exceptions = {t for t in tokens if t in self.allowed_exceptions}
            hit = next((t for t in tokens if t in self.banned_ids), None)
            if hit and not exceptions:
                return f"заборонена ліцензія {hit} у виразі «{expression}»"
        return None

    # ---------------------------------------------------------------- символи

    def declared_prefixes(self) -> dict[str, str]:
        """Префікс символу -> ідентифікатор компонента, який його декларує."""

        out: dict[str, str] = {}
        for comp in self.components.values():
            for prefix in comp.symbol_prefixes:
                out[prefix] = comp.id
        return out


def _build_component(comp_id: str, raw: dict, source: Path) -> Component:
    for required in ("name", "version", "license", "object_patterns"):
        if required not in raw:
            raise CatalogError(f"{source}: у компонента '{comp_id}' немає поля '{required}'")

    license_obj = raw["license"]
    if not isinstance(license_obj, dict) or not (
        {"id", "name", "expression"} & set(license_obj)
    ):
        raise CatalogError(
            f"{source}: license компонента '{comp_id}' має бути об'єктом "
            f"з полем id, name або expression"
        )

    return Component(
        id=comp_id,
        name=raw["name"],
        version=str(raw["version"]),
        supplier=raw.get("supplier", "невідомий постачальник"),
        purl=raw.get("purl", f"pkg:generic/{comp_id}@{raw['version']}"),
        license=license_obj,
        patterns=[_compile(p, source, f"{comp_id}.object_patterns")
                  for p in raw["object_patterns"]],
        symbol_prefixes=list(raw.get("symbol_prefixes", [])),
        depends_on=list(raw.get("depends_on", [])),
        notice_required=bool(raw.get("notice_required", True)),
        generated_by=raw.get("generated_by"),
        generated_notice=raw.get("generated_notice"),
    )


def _compile(pattern: str, source: Path, where: str) -> re.Pattern:
    try:
        return re.compile(pattern, re.IGNORECASE)
    except re.error as exc:
        raise CatalogError(f"{source}: битий регулярний вираз у {where}: {pattern} — {exc}") from exc


def _matches(comp: Component, obj: LinkedObject) -> bool:
    return any(p.search(obj.display) for p in comp.patterns)


def _override_notes(report: MapReport, detections: dict[str, Detection]) -> list[Finding]:
    """Слабкі символи: чия реалізація лишилася у Flash."""

    out: list[Finding] = []
    for override in report.overrides[:20]:            # у мапі їх бувають сотні
        out.append(Finding(
            "WEAK_SYMBOL_OVERRIDE",
            f"{override.section}: у Flash реалізація з {override.kept_by}, "
            f"версію з {', '.join(override.dropped_from)} викинуто",
            severity="info",
        ))
    if len(report.overrides) > 20:
        out.append(Finding(
            "WEAK_SYMBOL_OVERRIDE",
            f"…і ще {len(report.overrides) - 20} перевизначень слабких символів",
            severity="info",
        ))
    return out
