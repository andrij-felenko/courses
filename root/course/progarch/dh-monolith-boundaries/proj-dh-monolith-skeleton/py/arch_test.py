# arch_test.py — ФІТНЕС-ФУНКЦІЯ: три червоні умови валять збірку
from arch.graph import import_graph
from arch.rules import forbidden_edges
from arch.cycles import find_cycle
from arch.schema_rule import cross_schema

def test_no_forbidden_import():
    bad = forbidden_edges(import_graph())
    assert not bad, f"заборонені ребра імпорту: {bad}"        # напр. [('billing', 'control')]

def test_graph_is_acyclic():
    cycle = find_cycle(import_graph())
    assert cycle is None, f"цикл у графі залежностей: {' → '.join(cycle)}"

def test_schema_isolation():
    bad = cross_schema()
    assert not bad, f"звертання в чужу схему: {bad}"          # напр. [('telemetry','control','schema.sql')]
