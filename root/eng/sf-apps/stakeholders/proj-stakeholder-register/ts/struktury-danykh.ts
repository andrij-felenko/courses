// Якісні атрибути, про які дбають стейкхолдери.
type Attribute = "доступність" | "змінюваність" | "швидкодія" | "безпека" | "вартість";

// Стейкхолдер = ім'я + три булеві осі вагомості + інтерес + його турбота.
interface Stakeholder {
  name: string;
  power: boolean;       // чи може ЗМУСИТИ?
  legitimacy: boolean;  // чи МАЄ ПРАВО вимагати?
  urgency: boolean;     // чи мусить бути ЗАРАЗ?
  interest: boolean;    // чи не байдуже, що буде із системою?
  concern: Attribute;   // головна турбота
  hard?: boolean;       // турбота — твердий поріг (закон), а не м'яке вподобання
}

// Архітектурне рішення свідомо закриває один атрибут.
interface Decision {
  name: string;
  closes: Attribute;
}

// Параметр устрою тягне атрибути в той чи інший бік: +1 краще, −1 гірше.
interface Parameter {
  name: string;
  pushes: { attr: Attribute; dir: 1 | -1 }[];
}

// В'ю обрамлює (показує) певні турботи-атрибути.
interface View {
  name: string;
  frames: Attribute[];
}
