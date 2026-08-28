type DataSet = {
  name: string;
  bornManyPlaces: boolean;         // G1: той самий ключ народжується в кількох місцях одразу?
  availPartitionNonneg: boolean;   // G2: доступність запису під розривом — незаперечна?
  naturalHome: boolean;            // G3: чи є природний «дім» на запис?
};

function decide(ds: DataSet): { model: string; price: string } {
  const pressures: string[] = [];
  if (ds.bornManyPlaces)       pressures.push("гео/офлайн");
  if (ds.availPartitionNonneg) pressures.push("доступність-під-розривом");
  if (pressures.length === 0)                          // жоден тиск не назвався
    return { model: "один лідер + читальні репліки", price: "пауза на failover" };
  if (!ds.naturalHome)                                 // тиск є, природного дому нема
    return { model: "безлідерна (кворум W+R>N)", price: "конфлікти + тюнинг кворуму" };
  return { model: "мультилідер (лідер на дім/регіон)", price: "конфлікти на спільних ключах" };
}

const DH: DataSet[] = [
  { name: "Твін дому",          bornManyPlaces: false, availPartitionNonneg: false, naturalHome: true },
  { name: "Реєстр",             bornManyPlaces: false, availPartitionNonneg: false, naturalHome: true },
  { name: "Телеметрія",         bornManyPlaces: false, availPartitionNonneg: false, naturalHome: true },
  { name: "Крос-регіон (гіп.)", bornManyPlaces: false, availPartitionNonneg: false, naturalHome: true },
];

for (const ds of DH) {
  const { model, price } = decide(ds);
  console.log(`${ds.name.padEnd(18)} → ${model}  ·  ціна: ${price}`);
}
