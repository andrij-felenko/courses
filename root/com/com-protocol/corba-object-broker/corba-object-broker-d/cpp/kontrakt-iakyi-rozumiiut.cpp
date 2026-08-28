// C++: посилання приходить нетипізованим, тому його треба звузити до інтерфейсу
CORBA::Object_var obj = orb->string_to_object(ior_string);
bank::Account_var acc = bank::Account::_narrow(obj);
if (CORBA::is_nil(acc)) { /* за цим посиланням не рахунок */ }

try {
    acc->withdraw(50);
    CORBA::Long left = acc->balance();
} catch (const bank::InsufficientFunds& e) {
    // помилка, оголошена в IDL: не вистачило e.shortfall
} catch (const CORBA::SystemException& e) {
    // помилка, якої в IDL немає: зламався сам виклик
}
