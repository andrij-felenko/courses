import pytest

# Контрактний тест як параметризована фабрика: той самий тест
# прогоняється на КОЖНІЙ реалізації ReadableList.
def make_arraylist(init):
    l = ArrayList()
    for x in init:
        l.add(x)
    return l

def make_immutable(init):
    return ImmutableList(init)

@pytest.mark.parametrize("make", [make_arraylist, make_immutable])
def test_readable_contract(make):
    lst = make([10, 20, 30])
    assert lst.size() == 3                # постумова size
    assert lst.get(0) == 10               # постумова get
    assert lst.get(2) == 30
