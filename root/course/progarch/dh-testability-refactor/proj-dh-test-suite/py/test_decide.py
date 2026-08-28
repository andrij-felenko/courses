# test_decide.py
import pytest
from home import Reading, Config, Command, decide

CFG = Config(threshold=20.0)

@pytest.mark.parametrize("r, expected", [
    pytest.param(Reading(5.0),            Command.HEAT, id="глибокий-холод→HEAT"),
    pytest.param(Reading(19.0),           Command.HEAT, id="нижче-порога→HEAT"),
    pytest.param(Reading(19.999),         Command.HEAT, id="на-волосину-нижче→HEAT"),
    pytest.param(Reading(20.0),           Command.IDLE, id="рівно-на-порозі→IDLE"),
    pytest.param(Reading(20.001),         Command.IDLE, id="на-волосину-вище→IDLE"),
    pytest.param(Reading(25.0),           Command.IDLE, id="тепло→IDLE"),
    pytest.param(Reading(5.0,  ok=False), Command.IDLE, id="холод+мовчить→IDLE"),
    pytest.param(Reading(25.0, ok=False), Command.IDLE, id="тепло+мовчить→IDLE"),
])
def test_decide_covers_every_branch(r, expected):
    assert decide(r, CFG) == expected
