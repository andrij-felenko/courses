/* Чи не бреше маніфест: статус каже «написано», а файлу немає або він порожній.
   Локально, 0 токенів. Критично перед міграцією — батч довіряє маніфесту. */
const fs = require("fs"), path = require("path");
const R = path.resolve(__dirname, "../..");
const KINDS = { book: ["physics","math","electronics","programming","communications","algorithms","philosophy"],
  catalog: ["boards","connect","sensors","power","actuators","instruments","components"],
  reference: ["unix-linux","cpp-standards","build-systems","media-vision","qgroundcontrol"] };
const READABLE = new Set(["done","update","deeper","recheck"]);
/* книги, що вже переїхали в root/: їхні СТАРІ маніфести навмисно застарілі — не судимо їх,
   натомість судимо нові. Список — з реєстру, а не з хардкоду. */
const shelf = JSON.parse(fs.readFileSync(path.join(R, "root/shelf.json"), "utf8"));
const MOVED = new Set();
const NEWBOOKS = [];
for (const K of shelf.kinds) for (const b of K.books) { MOVED.add(b); NEWBOOKS.push(["root/" + K.dir, b]); }
function ld(f,k){const w={__BOOKS__:[],__GUIDES__:[]};try{new Function("window",fs.readFileSync(f,"utf8"))(w)}catch(e){return null}return (w[k]||[])[0]}
function size(f){try{return fs.statSync(f).size}catch(e){return -1}}
const lies=[],ghosts=[];
function judge(dir, base, ver, status, where, mf, slug){
  if(!READABLE.has(status)) return;
  const f = path.join(dir, base);
  const s = size(f);
  const rec = { manifest: mf, slug: slug, ver: ver, status: status, file: base, where: where, size: s };
  if (s < 0) ghosts.push(rec);
  else if (s < 200) lies.push(rec);
}
for (const [kind, slugs] of Object.entries(KINDS)) for (const s of slugs) {
  if (MOVED.has(s)) continue;
  const m = ld(path.join(R,kind,s,"manifest.js"),"__BOOKS__"); if(!m) continue;
  for (const sec of m.sections||[]) for (const t of sec.topics||[]) {
    const dir = path.join(R,kind,s,sec.slug,t.slug), where = kind+"/"+s+"/"+sec.slug+"/"+t.slug;
    const mf = kind+"/"+s+"/manifest.js";
    judge(dir, t.slug+".md",  "basic",    (t.basic||{}).status,    where, mf, t.slug);
    judge(dir, t.slug+"-d.md","detailed", (t.detailed||{}).status, where, mf, t.slug);
    for (const k of ["hist","comp","math","proj","api"]) for (const ins of t[k]||[])
      judge(dir, ins.file, k, ins.status, where, mf, t.slug);
  }
}
for (const g of ["embedded","embedded-ultra","progarch","unix"]) {
  if (MOVED.has(g)) continue;
  const m = ld(path.join(R,"guide",g,"manifest.js"),"__GUIDES__"); if(!m) continue;
  for (const mo of m.modules||[]) for (const c of mo.chapters||[]) for (const st of c.steps||[]) {
    if(!st.slug) continue;
    const dir = path.join(R,"guide",g,mo.slug,st.slug), where = "guide/"+g+"/"+mo.slug+"/"+st.slug;
    const mf = "guide/"+g+"/manifest.js";
    judge(dir, st.slug+".md",  "basic",    (st.basic||{}).status,    where, mf, st.slug);
    judge(dir, st.slug+"-d.md","detailed", (st.detailed||{}).status, where, mf, st.slug);
    for (const k of ["hist","comp","math","proj","api"]) for (const ins of st[k]||[])
      judge(dir, ins.file, k, ins.status, where, mf, st.slug);
  }
}
/* нові маніфести root/: groups -> chapters -> topics */
for (const [dir, b] of NEWBOOKS) {
  const f = path.join(R, dir, b, "manifest.json");
  if (!fs.existsSync(f)) continue;
  const m = JSON.parse(fs.readFileSync(f, "utf8"));
  for (const g of m.groups || []) for (const c of g.chapters || []) for (const t of c.topics || []) {
    if (!t.slug) continue;                       // крок-ref: файлу не має за визначенням
    const d = path.join(R, dir, b, t.slug), where = dir + "/" + b + "/" + t.slug, mf = dir + "/" + b + "/manifest.json";
    judge(d, t.slug + ".md",   "basic",    (t.basic||{}).status,    where, mf, t.slug);
    judge(d, t.slug + "-d.md", "detailed", (t.detailed||{}).status, where, mf, t.slug);
    for (const k of ["hist","comp","math","proj","api"]) for (const ins of t[k]||[])
      judge(d, ins.file, k, ins.status, where, mf, t.slug);
  }
}
fs.writeFileSync(path.join(__dirname,"manifest-lies.json"), JSON.stringify({ghosts,lies},null,2)+"\n","utf8");
console.log("СТАТУС «написано», а файлу НЕМА:      " + ghosts.length);
console.log("СТАТУС «написано», а файл ПОРОЖНІЙ:  " + lies.length);
[...ghosts.slice(0,6), ...lies.slice(0,4)].forEach(x=>console.log("   "+x.where+"  "+x.ver+"="+x.status+"  "+x.file));
console.log("повний список — scripts/migrate/manifest-lies.json");
