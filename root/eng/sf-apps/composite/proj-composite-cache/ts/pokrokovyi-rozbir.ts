const root = new Group();
const inner = new Group();
root.add(inner);
const r1 = new Rectangle(0, 0, 10, 10);
inner.add(r1);
inner.add(new Rectangle(20, 0, 10, 10));
root.add(new Rectangle(100, 100, 5, 5));

console.log(root.bounds());   // { minX:0, minY:0, maxX:105, maxY:105 } — ПЕРШИЙ запит: повний перерахунок
root.bounds();                // усе чисте → O(1), не рахує НІЧОГО
r1.moveTo(-50, -50);          // листок поїхав → inner і root стали брудними, сусід — ні
console.log(root.bounds());   // { minX:-50, minY:-50, maxX:105, maxY:105 } — перерахунок ЛИШЕ брудного шляху
