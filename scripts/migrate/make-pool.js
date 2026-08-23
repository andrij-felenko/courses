const fs=require('fs'), path=require('path');
global.window={__BOOKS__:[],__GUIDES__:[]};
for(const d of ['book','reference','catalog'])
 for(const b of fs.readdirSync(d)){
  const p=path.resolve(d,b,'manifest.js');
  if(fs.existsSync(p)) try{require(p);}catch(e){}
 }
for(const c of ['embedded','progarch','unix']) try{require(path.resolve('guide',c,'manifest.js'));}catch(e){}
const W=s=>s==='done'||s==='recheck'||s==='update'||s==='deeper';
const ALL={};
for(const b of window.__BOOKS__)
 for(const s of b.sections||[])
  for(const t of s.topics||[]){
   const d=(t.detailed||{}).status, ba=(t.basic||{}).status;
   const written=W(d)||W(ba);
   const pending=(d==='pending')||(ba==='pending');
   if(!written&&!pending) continue;
   ALL[b.slug+'/'+s.slug+'/'+t.slug]={book:b.slug,type:b.type||'book',sec:s.slug,secT:s.title,
     slug:t.slug,title:t.title,st:written?'написана':'заведена, ще не написана'};
  }
const CAT=['sensors','power','connect','boards','actuators','instruments','components'];
const SRC={embedded:['physics','electronics','programming','math','communications','algorithms',
   'media-vision','qgroundcontrol','build-systems','python'].concat(CAT),
 progarch:['programming','algorithms','communications','math','python','build-systems','unix-linux','media-vision','cpp-standards','qgroundcontrol','electronics','physics'].concat(CAT),
 unix:['unix-linux','programming','build-systems','python','algorithms','communications','math','media-vision'].concat(CAT)};
for(const g of window.__GUIDES__){
 const used={};
 for(const m of g.modules||[]) for(const ch of m.chapters||[]) for(const st of ch.steps||[])
  if(st.ref) used[st.ref]=1;
 const bysec={}; let n=0,np=0;
 for(const k of Object.keys(ALL)){
  const a=ALL[k];
  if(SRC[g.slug].indexOf(a.book)<0) continue;
  if(used[k]) continue;
  const kind=a.type==='catalog'?'КАТАЛОГ':(a.type==='reference'?'ДОВІДНИК':'КНИГА');
  const key=kind+' · '+a.book+' / '+a.secT+'  ['+a.sec+']';
  (bysec[key]=bysec[key]||[]).push(a); n++;
  if(a.st!=='написана') np++;
 }
 let out='# Резерв корпусу для курсу «'+g.title+'»\n\n';
 out+='Статті корпусу ('+n+'), у які курс НЕ веде. Шлях у `ref` — рівно те, що в дужках.\n\n';
 out+='**Дві категорії, обидві придатні для `ref`:**\n\n';
 out+='- без позначки — **написана**, читач відкриє її одразу;\n';
 out+='- `[pending]` — **тему заведено в маніфесті, статтю ще не написано** ('+np+' таких).\n';
 out+='  Адреса вже існує, слуг і назва вже обрані: вести `ref` сюди можна й треба,\n';
 out+='  вигадувати нову тему на те саме — не можна.\n\n';
 out+='Тут є всі три види книг: **КНИГА** (закони й явища), **ДОВІДНИК** (мова, ОС, формат,\n';
 out+='протокол), **КАТАЛОГ** (конкретні плати, модулі, прилади, деталі).\n\n';
 for(const k of Object.keys(bysec).sort()){
  out+='## '+k+'  ('+bysec[k].length+')\n\n';
  for(const a of bysec[k]) out+='- `'+a.book+'/'+a.sec+'/'+a.slug+'` — '+a.title+(a.st!=='написана'?'  `[pending]`':'')+'\n';
  out+='\n';
 }
 fs.writeFileSync('scripts/migrate/final/pool-'+g.slug+'.md',out);
 console.log(g.slug+': '+n+' статей ('+np+' pending), розділів '+Object.keys(bysec).length);
}
