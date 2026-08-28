// збираємо дерево
const root = new Folder();
const src = new Folder();
src.add(new File(1200));
src.add(new File(800));
root.add(src);
root.add(new File(500));

// а тепер — увага — клієнт НЕ знає й не питає, що перед ним
console.log(root.size());      // 2500
console.log(src.size());       // 2000
console.log(new File(42).size());  // 42 — той самий виклик
