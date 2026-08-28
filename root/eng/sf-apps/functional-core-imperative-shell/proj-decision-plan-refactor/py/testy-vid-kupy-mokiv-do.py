# ── ДО: тест мусить обставити всі дотики до світу ──
async def test_over_limit_flags_and_notifies():
    # 1. підробка бази з потрібним рахунком і шпигунами на записах
    db = Mock()
    db.load_account = AsyncMock(return_value=Account(
        id="a1", user_id="u1", balance=500, daily_limit=100))
    db.flag_transaction = AsyncMock()
    db.freeze_account   = AsyncMock()
    db.set_balance      = AsyncMock()
    # 2. підробка сповіщувача
    notifier = Mock(); notifier.push = AsyncMock()
    # 3. підробка журналу
    audit = Mock(); audit.log = AsyncMock()
    # 4. підмінити глобальні залежності на підробки
    inject(db=db, notifier=notifier, audit=audit)

    await handle_transaction("a1", Transaction(id="t1", amount=150))

    # 5. і тепер — допит шпигунів: покликали правильно?
    db.flag_transaction.assert_awaited_with("t1", "over-limit")
    notifier.push.assert_awaited_with("u1", "Транзакцію відкладено на перевірку")
