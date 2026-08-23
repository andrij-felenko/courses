/* збирає кандидатів у НОВІ теми з усіх джерел: toc/, toc2/ і фінальних варіантів final/<курс>-{A,B}.md */
const fs=require("fs"), path=require("path");
const NL=String.fromCharCode(10);
const courses=["embedded","progarch","unix"];
function norm(s){return s.toLowerCase().replace(/[«»"'`\u2019\u02bc()]/g," ").replace(/[^a-zа-яіїєґ0-9 ]/gi," ").replace(/\s+/g," ").trim();}
function titleOf(line){
 const q=line.match(/[«"]([^»"]{3,90})[»"]/);
 if(q) return q[1].trim();
 let s=line.replace(/^[-*\d.\s]+/,"");
 s=s.split(" → ")[0].split(" · ")[0].split(" — ")[0];
 return s.replace(/\*\*/g,"").trim().slice(0,90);
}
function harvest(file,out,tag){
 if(!fs.existsSync(file)) return;
 const L=fs.readFileSync(file,"utf8").split(/\r?\n/);
 let on=false, lvl=0;
 for(const ln of L){
  const h=ln.match(/^(#{1,6})\s+(.*)$/);
  if(h){
   const t=h[2].toUpperCase();
   if(/НОВ/.test(t)&&!/НОВОГО/.test(t)){on=true;lvl=h[1].length;continue;}
   if(on&&h[1].length<=lvl){on=false;}
   continue;
  }
  if(!on) continue;
  if(!/^\s*[-*]|^\s*\d+\./.test(ln)) continue;
  const t=titleOf(ln);
  if(t.length<6) continue;
  const k=norm(t);
  if(!k) continue;
  if(!out[k]) out[k]={title:t,votes:0,src:{},line:ln.trim()};
  out[k].votes++; out[k].src[tag]=1;
 }
}
for(const c of courses){
 const out={};
 for(let i=1;i<=5;i++){harvest(path.join(__dirname,"toc",c+"-"+i+".md"),out,"A"+i);
                       harvest(path.join(__dirname,"toc2",c+"-"+i+".md"),out,"B"+i);}
 for(const v of ["A","B"]) harvest(path.join(__dirname,"final",c+"-"+v+".md"),out,"F"+v);
 const arr=Object.keys(out).map(k=>out[k]).sort((a,b)=>b.votes-a.votes);
 let o="# Теми, запропоновані сьогодні — курс «"+c+"»"+NL+NL;
 o+="Зібрано з 10 незалежних пропозицій і 2 зведень. Число — скільки джерел назвали тему самостійно."+NL;
 o+="Це **кандидати, а не рішення**. Формулювання чужі — переназви як треба."+NL+NL;
 let cur=null;
 for(const it of arr){
  if(it.votes!==cur){cur=it.votes;o+=NL+"## Назвали джерел: "+cur+NL+NL;}
  o+="- **"+it.title+"** — "+it.line.replace(/^[-*\d.\s]+/,"").slice(0,220)+NL;
 }
 fs.writeFileSync(path.join(__dirname,"final","newtopics-"+c+".md"),o);
 console.log(c+": кандидатів "+arr.length+" (з них ≥2 джерел: "+arr.filter(x=>x.votes>=2).length+")");
}
