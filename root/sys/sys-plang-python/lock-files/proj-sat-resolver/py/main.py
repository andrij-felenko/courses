#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Симулятор CDCL / PubGrub резолвера залежностей з експортом у lock-файл.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple
import hashlib

@dataclass
class Version:
    major: int
    minor: int
    patch: int

    @classmethod
    def parse(cls, s: str) -> "Version":
        parts = [int(p) for p in s.split(".")]
        return cls(parts[0], parts[1], parts[2] if len(parts) > 2 else 0)

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    def __lt__(self, other: "Version") -> bool:
        return (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch)

    def __ge__(self, other: "Version") -> bool:
        return not (self < other)

@dataclass
class VersionConstraint:
    min_ver: Optional[Version] = None
    max_ver: Optional[Version] = None  # виключно (exclusive)

    def satisfied_by(self, v: Version) -> bool:
        if self.min_ver and v < self.min_ver:
            return False
        if self.max_ver and v >= self.max_ver:
            return False
        return True

@dataclass
class PackageRelease:
    name: str
    version: Version
    dependencies: Dict[str, VersionConstraint] = field(default_factory=dict)
    sha256: str = ""

    def __post_init__(self):
        if not self.sha256:
            raw = f"{self.name}-{self.version}".encode("utf-8")
            self.sha256 = hashlib.sha256(raw).hexdigest()

class PackageUniverse:
    def __init__(self):
        self.packages: Dict[str, List[PackageRelease]] = {}

    def add(self, pkg: PackageRelease):
        self.packages.setdefault(pkg.name, []).append(pkg)
        self.packages[pkg.name].sort(key=lambda x: x.version, reverse=True)

    def find(self, name: str, constraint: VersionConstraint) -> List[PackageRelease]:
        if name not in self.packages:
            return []
        return [p for p in self.packages[name] if constraint.satisfied_by(p.version)]

class CDCLResolver:
    def __init__(self, universe: PackageUniverse):
        self.universe = universe
        self.learned_clauses: List[Set[Tuple[str, str]]] = []

    def solve(self, root_reqs: Dict[str, VersionConstraint]) -> Optional[Dict[str, PackageRelease]]:
        decision_stack: List[PackageRelease] = []

        def backtrack_with_learning(failed_choice: PackageRelease):
            conflict_set = {(p.name, str(p.version)) for p in decision_stack}
            conflict_set.add((failed_choice.name, str(failed_choice.version)))
            self.learned_clauses.append(conflict_set)

        def is_clause_violated(assignment: Dict[str, PackageRelease]) -> bool:
            for clause in self.learned_clauses:
                matches = 0
                for pkg_name, ver_str in clause:
                    if pkg_name in assignment and str(assignment[pkg_name].version) == ver_str:
                        matches += 1
                if matches == len(clause):
                    return True
            return False

        def resolve_recursive(current: Dict[str, PackageRelease]) -> Optional[Dict[str, PackageRelease]]:
            if is_clause_violated(current):
                return None

            accumulated_reqs: Dict[str, VersionConstraint] = dict(root_reqs)
            for pkg in current.values():
                for dep_name, dep_constraint in pkg.dependencies.items():
                    if dep_name in accumulated_reqs:
                        prev = accumulated_reqs[dep_name]
                        new_min = max(prev.min_ver, dep_constraint.min_ver, key=lambda v: v or Version(0,0,0))
                        new_max = None
                        if prev.max_ver and dep_constraint.max_ver:
                            new_max = min(prev.max_ver, dep_constraint.max_ver)
                        else:
                            new_max = prev.max_ver or dep_constraint.max_ver
                        accumulated_reqs[dep_name] = VersionConstraint(new_min, new_max)
                    else:
                        accumulated_reqs[dep_name] = dep_constraint

            unresolved = [name for name in accumulated_reqs if name not in current]
            if not unresolved:
                return current

            target_pkg_name = unresolved[0]
            constraint = accumulated_reqs[target_pkg_name]
            candidates = self.universe.find(target_pkg_name, constraint)

            if not candidates:
                return None

            for candidate in candidates:
                next_assignment = dict(current)
                next_assignment[target_pkg_name] = candidate
                decision_stack.append(candidate)

                res = resolve_recursive(next_assignment)
                if res is not None:
                    return res

                decision_stack.pop()
                backtrack_with_learning(candidate)

            return None

        return resolve_recursive({})

    def export_lock(self, solution: Dict[str, PackageRelease]) -> str:
        lines = [
            "# Generated by Antigravity CDCL Lockfile Simulator",
            "version = 1",
            "revision = 0",
            ""
        ]
        for name in sorted(solution.keys()):
            pkg = solution[name]
            lines.append("[[package]]")
            lines.append(f'name = "{pkg.name}"')
            lines.append(f'version = "{pkg.version}"')
            lines.append(f'sha256 = "{pkg.sha256}"')
            if pkg.dependencies:
                lines.append("dependencies = [")
                for d_name in sorted(pkg.dependencies.keys()):
                    lines.append(f'  "{d_name}",')
                lines.append("]")
            lines.append("")
        return "\n".join(lines)

def main():
    u = PackageUniverse()
    u.add(PackageRelease("fastapi", Version(0, 110, 0), {
        "pydantic": VersionConstraint(Version(2, 0, 0), Version(3, 0, 0)),
        "starlette": VersionConstraint(Version(0, 37, 0), Version(0, 38, 0))
    }))
    u.add(PackageRelease("pydantic", Version(2, 6, 4), {
        "pydantic-core": VersionConstraint(Version(2, 16, 0), Version(2, 17, 0))
    }))
    u.add(PackageRelease("pydantic", Version(2, 7, 0), {
        "pydantic-core": VersionConstraint(Version(2, 18, 0), Version(2, 19, 0))
    }))
    u.add(PackageRelease("pydantic-core", Version(2, 16, 3)))
    u.add(PackageRelease("pydantic-core", Version(2, 18, 1)))
    u.add(PackageRelease("starlette", Version(0, 37, 2)))

    root_requirements = {
        "fastapi": VersionConstraint(Version(0, 110, 0), Version(0, 111, 0)),
        "pydantic-core": VersionConstraint(Version(2, 16, 0), Version(2, 17, 0))
    }

    resolver = CDCLResolver(u)
    solution = resolver.solve(root_requirements)

    if solution:
        print(resolver.export_lock(solution))
    else:
        print("Dependency resolution failed.")

if __name__ == "__main__":
    main()
