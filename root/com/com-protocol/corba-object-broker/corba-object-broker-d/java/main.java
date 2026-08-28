// Java: те саме IDL, те саме звуження, інші імена згенерованих класів
org.omg.CORBA.Object obj = orb.string_to_object(iorString);
bank.Account acc = bank.AccountHelper.narrow(obj);

try {
    acc.withdraw(50);
    int left = acc.balance();
} catch (bank.InsufficientFunds e) {
    // не вистачило e.shortfall
} catch (org.omg.CORBA.SystemException e) {
    // зламався сам виклик
}
