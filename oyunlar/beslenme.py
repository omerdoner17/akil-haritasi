import streamlit as st
import streamlit.components.v1 as components
import json
from urllib.parse import quote

def beslenme_oyunu_render(ogretmen_adi, sube_adi, ogrenciler):
    ogrenci_listesi_js = ogrenciler if ogrenciler else [{"ad": "Örnek Öğrenci", "maskot": "🦁"}]
    ogrenciler_json = json.dumps(ogrenci_listesi_js, ensure_ascii=False)
    ogretmen_enc = quote(str(ogretmen_adi))
    sube_enc = quote(str(sube_adi))

    html_code = f"""
<!DOCTYPE html>
<html lang="tr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Ali'yi Besle!</title>
<style>
:root{{--bg:#eef7ff;--card:#fff;--tx:#1f2d3d;--mut:#5b6b7b;--bd:#d5e3f0;--ok:#2e9e5b;--bad:#e0523f}}
*{{box-sizing:border-box}}
html,body{{margin:0;padding:0;width:100%;height:100%;overflow:hidden;background:#f8fafc;color:var(--tx);font-family:system-ui,-apple-system,"Segoe UI",sans-serif}}
#fitRoot{{width:100%;transform-origin:top center;padding:6px}}
.top-bar{{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;background:#fff;border:2px solid #cbd5e1;border-radius:14px;padding:6px 14px;max-width:960px;margin:0 auto 8px auto}}
.student-box{{display:flex;align-items:center;gap:8px;font-weight:800;font-size:.95rem;color:#0284c7}}
select.ogr-sel{{font:inherit;font-weight:700;padding:4px 10px;border-radius:8px;border:2px solid #0284c7;background:#f0f9ff;color:#0f172a;cursor:pointer}}
.btn-spin{{background:#f59e0b;color:#fff;border:none;padding:6px 12px;border-radius:8px;font-weight:800;cursor:pointer}}
.btn-save{{background:#10b981;color:#fff;border:none;padding:6px 14px;border-radius:8px;font-weight:800;cursor:pointer}}
.btn-fs{{background:#475569;color:#fff;border:none;padding:6px 10px;border-radius:8px;font-weight:700;cursor:pointer}}
.save-toast{{font-size:0.82rem;font-weight:700;color:#059669;display:none}}
.game{{display:flex;gap:10px;max-width:960px;margin:0 auto;align-items:stretch}}
.panel{{background:var(--card);border:1px solid var(--bd);border-radius:14px;padding:8px}}
.stage{{flex:1.8;text-align:center}}
.foods{{flex:1.1}}
.foods h2{{font-size:.95rem;margin:0 0 6px}}
.grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:6px}}
.food{{font-size:1.65rem;background:var(--bg);border:2px solid var(--bd);border-radius:12px;padding:5px 0 3px;cursor:grab;user-select:none;line-height:1.05;text-align:center}}
.food small{{display:block;font-size:.58rem;color:var(--mut);margin-top:1px;font-weight:700}}
.food:hover{{transform:scale(1.06);border-color:#0284c7}}
.bar{{height:16px;border-radius:10px;background:linear-gradient(90deg,var(--bad),#f2c14e,var(--ok));position:relative;margin:2px 4px;border:1px solid var(--bd)}}
.bar i{{position:absolute;top:-4px;width:6px;height:22px;background:var(--tx);border-radius:4px;left:50%;transform:translateX(-50%);transition:left .6s}}
.lab{{display:flex;justify-content:space-between;font-size:.7rem;font-weight:700;color:var(--mut);margin:0 4px 2px}}
#sv{{width:100%;max-height:290px;display:block;border-radius:10px}}
.quake{{animation:q .5s}}
@keyframes q{{0%,100%{{transform:translate(0)}}20%{{transform:translate(-7px,5px)}}40%{{transform:translate(6px,-5px)}}60%{{transform:translate(-5px,3px)}}80%{{transform:translate(4px,-2px)}}}}
@keyframes spin{{to{{transform:rotate(360deg)}}}}
@keyframes drift{{from{{transform:translateX(-220px)}}to{{transform:translateX(720px)}}}}
#rays{{transform-box:fill-box;transform-origin:center;animation:spin 30s linear infinite}}
.cl{{animation:drift linear infinite}}
.sn{{--k1:#6cc3ff;--k2:#dff4ff;--h1:#7bd389;--h2:#5cbf72;--gr:#4fae5f;--cl:#fff;--su:1}}
.sf{{--k1:#38aaff;--k2:#c9f2ff;--h1:#6fe08a;--h2:#4fd073;--gr:#3fc25a;--cl:#fff;--su:1}}
.so{{--k1:#78858f;--k2:#b4bec7;--h1:#8aa58f;--h2:#78947e;--gr:#6b8a72;--cl:#9aa3ab;--su:0}}
#k1{{stop-color:var(--k1);transition:stop-color 1.6s}}#k2{{stop-color:var(--k2);transition:stop-color 1.6s}}
.h1{{fill:var(--h1)}}.h2{{fill:var(--h2)}}.gr{{fill:var(--gr)}}.cc{{fill:var(--cl)}}
#sun{{opacity:var(--su);transition:opacity 1.6s}}
.status{{font-weight:800;font-size:.95rem;margin:4px 0 0}}
.msg{{min-height:1.4em;color:#334155;font-weight:600;font-size:.85rem;margin:2px 4px}}
.btns{{display:flex;gap:6px;justify-content:center;margin-top:4px}}
button.b{{font:inherit;font-weight:700;font-size:.82rem;padding:6px 12px;border-radius:10px;border:2px solid var(--bd);background:var(--bg);color:var(--tx);cursor:pointer}}
.ghost{{position:fixed;font-size:2.2rem;pointer-events:none;z-index:99;transform:translate(-50%,-50%)}}
.cnt{{display:flex;justify-content:center;gap:16px;font-size:.85rem;margin-top:4px;font-weight:700}}
.cnt b.g{{color:var(--ok)}}.cnt b.r{{color:var(--bad)}}
</style></head><body>
<div id="fitRoot">
<div class="top-bar">
    <div class="student-box">
        <span>🎯 Öğrenci:</span>
        <select id="ogrSelect" class="ogr-sel"></select>
        <button class="btn-spin" id="btnRandom">🎲 Çark</button>
    </div>
    <div style="display:flex;align-items:center;gap:8px;">
        <span class="save-toast" id="saveToast">✅ Kaydedildi!</span>
        <button class="btn-save" id="btnSaveResult">💾 Sürece Kaydet</button>
        <button class="btn-fs" onclick="toggleFS()">⛶ Tam Ekran</button>
    </div>
</div>
<div class="game">
<div class="panel stage" id="stage">
 <div class="bar"><i id="ptr"></i></div>
 <div class="lab"><span>Obez 😟</span><span>Normal</span><span>Fit 💪</span></div>
 <svg id="sv" class="sn" viewBox="0 0 600 440">
  <defs><linearGradient id="sk" x1="0" y1="0" x2="0" y2="1"><stop id="k1" offset="0"/><stop id="k2" offset="1"/></linearGradient></defs>
  <rect width="600" height="440" fill="url(#sk)"/>
  <g id="sun"><g id="rays" stroke="#ffd34d" stroke-width="6" stroke-linecap="round"></g><circle cx="520" cy="75" r="34" fill="#ffd34d"/></g>
  <g class="cl" style="animation-duration:55s"><g class="cc"><ellipse cx="0" cy="70" rx="48" ry="16"/><ellipse cx="26" cy="57" rx="28" ry="18"/><ellipse cx="-24" cy="60" rx="24" ry="14"/></g></g>
  <path class="h1" d="M0 330 Q120 250 260 320 T520 300 T600 320 V440H0Z"/>
  <path class="h2" d="M0 365 Q150 305 300 355 T600 345 V440H0Z"/>
  <rect class="gr" y="382" width="600" height="58"/>
  <ellipse id="sh" fill="#000" opacity=".25"/>
  <g id="ch">
   <line id="l1" stroke="#ffcf8a" stroke-linecap="round"/><line id="l2" stroke="#ffcf8a" stroke-linecap="round"/>
   <ellipse id="s1" fill="#e8453c"/><ellipse id="s2" fill="#e8453c"/>
   <ellipse id="body" fill="#3b9cff" stroke="#1f6fcf" stroke-width="3"/>
   <ellipse id="belly" fill="#ffcf8a"/><circle id="nv" r="3" fill="#d79a4a"/>
   <line id="a1" stroke="#ffcf8a" stroke-linecap="round"/><line id="a2" stroke="#ffcf8a" stroke-linecap="round"/>
   <circle id="bi1" r="11" fill="#ffcf8a" stroke="#d79a4a" stroke-width="2"/><circle id="bi2" r="11" fill="#ffcf8a" stroke="#d79a4a" stroke-width="2"/>
   <circle id="h1" fill="#ffcf8a"/><circle id="h2" fill="#ffcf8a"/>
   <g id="face">
    <ellipse id="chin" cx="0" fill="#f2bf75"/>
    <circle id="head" fill="#ffcf8a" stroke="#d79a4a" stroke-width="3"/>
    <rect id="band" x="-31" y="-28" width="62" height="9" rx="3" fill="#e8453c"/>
    <circle id="c1" r="7" fill="#ff8f8f" opacity=".55"/><circle id="c2" r="7" fill="#ff8f8f" opacity=".55"/>
    <ellipse id="e1" fill="#fff"/><ellipse id="e2" fill="#fff"/>
    <ellipse id="p1" fill="#222"/><ellipse id="p2" fill="#222"/>
    <line id="b1" stroke="#5a3a1a" stroke-width="4" stroke-linecap="round"/><line id="b2" stroke="#5a3a1a" stroke-width="4" stroke-linecap="round"/>
    <path id="mc" fill="none" stroke="#222" stroke-width="4" stroke-linecap="round"/>
    <ellipse id="mo" cx="0" fill="#7a1f2b"/><ellipse id="tg" cx="0" fill="#ff7b8a"/>
    <circle id="mp" cx="0" r="1" fill="none"/>
   </g>
  </g>
  <g id="pg" text-anchor="middle"></g>
 </svg>
 <div class="status" id="st"></div>
 <div class="msg" id="msg">Ali çok acıkmış. Ona ne yedireceksin?</div>
 <div class="btns"><button class="b" id="jb">⬆️ Zıpla!</button><button class="b" id="wb">🚶 Yürü!</button><button class="b" id="rb">🔄 Yeniden</button></div>
 <div class="cnt"><span>Sağlıklı: <b class="g" id="cg">0</b></span><span>Sağlıksız: <b class="r" id="cb">0</b></span></div>
</div>
<div class="panel foods"><h2>🥗 Besin Sepeti</h2><div class="grid" id="grid"></div></div>
</div>
</div>
<script>
function autoFit(){{
  var r=document.getElementById('fitRoot');
  r.style.transform='none';
  var h=r.scrollHeight, wh=window.innerHeight;
  if(h>wh && wh>100){{ var sc=(wh-8)/h; r.style.transform='scale('+sc+')'; }}
}}
window.addEventListener('resize',autoFit);
function toggleFS(){{if(!document.fullscreenElement)document.documentElement.requestFullscreen().catch(()=>{{}});else document.exitFullscreen();}}

var OGRENCILER = {ogrenciler_json};
var OGRETMEN_ENC = "{ogretmen_enc}";
var SUBE_ENC = "{sube_enc}";
var secilenZararliBesinler = [];
var sel = document.getElementById("ogrSelect");
OGRENCILER.forEach(function(o) {{ var opt = document.createElement("option"); opt.value = o.ad; opt.textContent = (o.maskot || "🦁") + " " + o.ad; sel.appendChild(opt); }});
document.getElementById("btnRandom").onclick = function() {{
    if (OGRENCILER.length > 1) {{ var sayac = 0; var interval = setInterval(function() {{ sel.selectedIndex = Math.floor(Math.random() * OGRENCILER.length); if (++sayac > 12) clearInterval(interval); }}, 60); }}
    s=0; cg=0; cb=0; prev="normal"; secilenZararliBesinler=[]; S.tx=S.x=300; S.walk=0; S.y=0; S.air=0;
    document.getElementById("msg").textContent = "Yeni öğrenci tahtada! Ali'yi sağlıklı besleyelim."; draw();
}};
document.getElementById("btnSaveResult").onclick = function() {{
    var ogrAd = sel.value;
    var durum = "Gelişmekte Olan", guclu = "Sağlıklı ve zararlı besinleri ayırt etmeye çalışıyor.", yanilgi = "Belirgin bir kavram yanılgısı tespit edilmedi.", oneri = "Besin gruplarını günlük öğün tabağı üzerinde eşleştirme çalışması yapılabilir.";
    if (cg >= 3 && cb === 0) {{ durum = "İleri Düzey"; guclu = "Tüm seçimlerinde dengeli ve sağlıklı besinleri tercih etti (" + cg + " sağlıklı seçim)."; }}
    else if (cg > cb && cg >= 2) {{ durum = "Yetkin Düzey"; guclu = "Sağlıklı besinleri çoğunlukla doğru seçti (" + cg + " sağlıklı, " + cb + " sağlıksız)."; }}
    else if (cb >= cg && (cg + cb) > 0) {{ durum = "Başlangıç Düzeyi"; yanilgi = "Şekerli ve paketli gıdaları (" + (secilenZararliBesinler.join(", ") || "abur cubur") + ") tercih etme eğilimi görüldü."; }}
    var url = "http://127.0.0.1:8765/cark_kaydet?ogr=" + encodeURIComponent(ogrAd) + "&durum=" + encodeURIComponent(durum) + "&gorev=" + encodeURIComponent("Sağlıklı Beslenme (" + cg + " Doğru, " + cb + " Yanlış)") + "&model=" + encodeURIComponent("Aliyi Besle Beslenme Oyunu") + "&guclu=" + encodeURIComponent(guclu) + "&yanilgi=" + encodeURIComponent(yanilgi) + "&oneri=" + encodeURIComponent(oneri) + "&ogretmen=" + OGRETMEN_ENC + "&sube=" + SUBE_ENC;
    new Image().src = url;
    var toast = document.getElementById("saveToast"); toast.style.display = "inline";
    setTimeout(function() {{ toast.style.display = "none"; }}, 3000);
}};
var NS="http://www.w3.org/2000/svg",$=function(i){{return document.getElementById(i)}},rnd=function(a,b){{return a+Math.random()*(b-a)}},cl=function(v,a,b){{return Math.max(a,Math.min(b,v))}};
var FD=[["🍎","Elma",1,"Elma vitamin ve lif içerir."],["🥦","Brokoli",1,"Sebzeler vücudumuzu güçlendirir."],["🥕","Havuç",1,"Havuç gözlerimiz için faydalıdır."],["🥛","Süt",1,"Süt kemiklerimizi güçlendirir."],["🐟","Balık",1,"Balık kaslarımızı geliştirir."],["🍌","Muz",1,"Muz sağlıklı enerji verir."],["🥗","Salata",1,"Taze sebzelerle dolu."],["💧","Su",1,"Su içmek çok önemlidir."],
["🍔","Hamburger",-1,"Hamburger çok yağlıdır."],["🍟","Patates",-1,"Kızartmalar çok yağlıdır."],["🍕","Pizza",-1,"Çok yağ ve tuz içerir."],["🍩","Donut",-1,"Çok şekerlidir."],["🥤","Kola",-1,"Gazlı içeceklerde çok şeker var."],["🍫","Çikolata",-1,"Fazla şeker zararlıdır."],["🍭","Şeker",-1,"Besin değeri yoktur."],["🍦","Dondurma",-1,"Çok şekerlidir."],["🥚","Yumurta",1,"Yumurta büyümeye yardım eder."],["🍗","Tavuk",1,"Tavuk protein kaynağıdır."]];
var sh_=function(a){{return a.sort(function(){{return Math.random()-.5}})}};
FD=sh_(sh_(FD.filter(function(x){{return x[2]>0}})).slice(0,9).concat(sh_(FD.filter(function(x){{return x[2]<0}})).slice(0,9)));
var ids="ch sh l1 l2 s1 s2 body belly nv a1 a2 bi1 bi2 h1 h2 face chin head band c1 c2 e1 e2 p1 p2 b1 b2 mc mo tg mp pg sv stage".split(" "),E={{}};ids.forEach(function(i){{E[i]=$(i)}});
function A(e,o){{for(var k in o)e.setAttribute(k,o[k])}}
var rh="";for(var i=0;i<8;i++)rh+='<line x1="520" y1="24" x2="520" y2="8" transform="rotate('+i*45+' 520 75)"/>';$("rays").innerHTML=rh;
var GY=390,s=0,cg=0,cb=0,prev="normal",ps=[],drag=null;
var S={{x:300,y:0,vy:0,air:0,flip:0,rot:0,sqz:0,f:0,g:0,tx:300,walk:0,ph:0,wa:0,open:0,openT:0,chewE:0,burpE:0,fl:0,near:0,ax:20,ay:62,ex:0,ey:0,bk:0,nb:2,wob:0,mb:0,sh:0,t:0,px:0,py:0,hp:0,sp:0,hyA:150}};
function state(){{return s<=-3?"obez":s>=3?"fit":"normal"}}
function P(txt,x,y,vx,vy,o){{o=o||{{}};var e=document.createElementNS(NS,"text");e.textContent=txt;e.setAttribute("font-size",o.sz||22);if(o.fill)e.setAttribute("fill",o.fill);if(o.bold)e.setAttribute("font-weight","700");E.pg.appendChild(e);ps.push({{e:e,x:x,y:y,vx:vx,vy:vy,g:o.g||0,ttl:o.ttl||1,a:0,sp:o.sp||0,r:0}})}}
function dust(n){{for(var i=0;i<n;i++)P("●",S.x+rnd(-60,60),GY-4,rnd(-90,90),rnd(-50,-10),{{sz:12,fill:"#d9cdb4",ttl:.5}})}}
function confetti(){{for(var i=0;i<35;i++)P("■",rnd(30,570),rnd(-20,40),rnd(-40,40),rnd(60,170),{{sz:14,fill:"hsl("+Math.floor(rnd(0,360))+",90%,60%)",g:120,ttl:2.2,sp:rnd(-300,300)}})}}
function frame(ts){{
 var dt=Math.min(.05,(ts-(frame.l||ts))/1000);frame.l=ts;S.t+=dt;var t=S.t,st=state(),k=Math.min(1,dt*3);
 S.f+=(Math.max(0,-s)/6-S.f)*k;S.g+=(Math.max(0,s)/6-S.g)*k;var f=S.f,g=S.g;
 if(S.air){{S.vy+=1900*dt;S.y+=S.vy*dt;if(S.flip)S.rot=Math.min(360,S.rot+640*dt);if(S.y>=0){{S.y=0;S.air=0;S.flip=0;S.rot=0;S.sqz=st=="obez"?.25:.2;dust(10);if(st=="obez")S.sh=.6}}}}
 S.sqz*=Math.max(0,1-dt*8);var sq=S.sqz;
 var sp=st=="fit"?230:st=="normal"?95:0;if(!sp)S.walk=0;
 if(S.walk){{var d=S.tx-S.x;if(Math.abs(d)<5)S.walk=0;else{{S.x+=Math.sign(d)*Math.min(Math.abs(d),sp*dt);S.ph+=dt*sp/11}}}}
 S.wa+=((S.walk&&!S.air?1:0)-S.wa)*Math.min(1,dt*8);
 S.sh=Math.max(0,S.sh-dt*1.6);S.wob=Math.max(0,S.wob-dt*1.2);S.mb*=Math.max(0,1-dt*.8);
 var rx=50+f*85-g*8,ry=72+f*10,ll=46-f*22,bcy=-(ll+ry-5),hr=40+f*8,hy=bcy-ry-hr*.7+f*14;
 var bob=S.air?0:(S.walk?-Math.abs(Math.sin(S.ph))*5:-Math.abs(Math.sin(t*3))*5*g),shx=Math.sin(t*70)*5*S.sh;
 A(E.ch,{{transform:"translate("+(S.x+shx)+","+(GY+S.y+bob)+") scale("+(1+sq)+","+(1-sq)+") rotate("+S.rot+" 0 "+bcy+")"}});
 A(E.sh,{{cx:S.x,cy:GY+3,rx:rx+22,ry:8,opacity:.25}});
 function sw(sd){{return Math.sin(S.ph+(sd>0?0:Math.PI))}}
 [1,-1].forEach(function(sd,i){{var hx=sd*rx*.42,lf=Math.max(0,sw(sd))*10*S.wa,fx=hx+sd*f*14+sw(sd)*20*S.wa,n=i+1;A(E["l"+n],{{x1:hx,y1:bcy+ry-10,x2:fx,y2:-lf,"stroke-width":15+f*9}});A(E["s"+n],{{cx:fx,cy:-lf-3,rx:19+f*6,ry:9}});}});
 A(E.body,{{cx:0,cy:bcy,rx:rx,ry:ry}});A(E.belly,{{cx:0,cy:bcy+ry*.6,rx:rx*.6,ry:ry*.28,opacity:cl(f*2.2-.5,0,1)}});A(E.nv,{{cx:0,cy:bcy+ry*.64,opacity:cl(f*2.2-.5,0,1)}});
 var T=st=="fit"?[34,-58]:st=="normal"?[20,62]:[12,48],ak=Math.min(1,dt*6);S.ax+=(T[0]-S.ax)*ak;S.ay+=(T[1]-S.ay)*ak;var bo=st=="fit"?cl(S.g*3,0,1):0;
 [1,-1].forEach(function(sd,i){{var n=i+1,sx=sd*(rx-8),sy=bcy-ry*.4,ex2=sd*(rx-8+S.ax),ey2=sy+S.ay+sw(-sd)*16*S.wa;A(E["a"+n],{{x1:sx,y1:sy,x2:ex2,y2:ey2,"stroke-width":13+f*5}});A(E["h"+n],{{cx:ex2,cy:ey2,r:9+f*2}});A(E["bi"+n],{{cx:(sx+ex2)/2,cy:(sy+ey2)/2,opacity:bo}});}});
 var m=cl(s/3+S.mb,-1,1),my=hr*.45;A(E.face,{{transform:"translate(0,"+hy+")"}});S.hyA=GY+S.y+hy;
 A(E.chin,{{cy:hr*.65,rx:hr*.85,ry:hr*.5,opacity:cl(f*1.5,0,1)}});A(E.head,{{r:hr}});A(E.band,{{opacity:cl((g-.3)*4,0,1)}});
 A(E.c1,{{cx:-hr*.65,cy:hr*.25}});A(E.c2,{{cx:hr*.65,cy:hr*.25}});
 var er=Math.max(.6,8*(1-f*.45)),ey=-hr*.1;
 [1,-1].forEach(function(sd,i){{var n=i+1;A(E["e"+n],{{cx:sd*hr*.37,cy:ey,rx:8,ry:er}});A(E["p"+n],{{cx:sd*hr*.37,cy:ey,rx:4,ry:er*.5}})}});
 var bi=-hr*.5+(m<0?m*6:-m*4),bu=-hr*.5+(m<0?-m*3:-m*4);A(E.b1,{{x1:-hr*.62,y1:bu,x2:-hr*.12,y2:bi}});A(E.b2,{{x1:hr*.12,y1:bi,x2:hr*.62,y2:bu}});
 if(t<S.chewE)S.openT=.28+.22*Math.sin(t*24);else if(S.near||S.fl>0)S.openT=.95;else S.openT=0;
 S.open+=(S.openT-S.open)*Math.min(1,dt*16);var o=S.open,mr=2+o*14;
 A(E.mc,{{d:"M-16 "+my+" Q0 "+(my+m*16+2)+" 16 "+my,opacity:o<.12?1:0}});A(E.mo,{{cy:my,rx:9+o*5,ry:mr,opacity:o<.12?0:1}});A(E.tg,{{cy:my+mr*.5,rx:6,ry:mr*.4,opacity:o<.12?0:1}});A(E.mp,{{cy:my}});
 for(var i=ps.length;i--;){{var p=ps[i];p.a+=dt;if(p.a>=p.ttl){{p.e.remove();ps.splice(i,1);continue}}p.vy+=p.g*dt;p.x+=p.vx*dt;p.y+=p.vy*dt;p.r+=p.sp*dt;p.e.setAttribute("transform","translate("+p.x+" "+p.y+") rotate("+p.r+")");p.e.setAttribute("opacity",Math.min(1,(p.ttl-p.a)*3))}}
 requestAnimationFrame(frame)}}
function feed(f,x,y){{var gh=document.createElement("div");gh.className="ghost";gh.textContent=f[0];document.body.appendChild(gh);S.fl++;var t0=performance.now();(function step(n){{var p=Math.min(1,(n-t0)/400),e=p*p,r=E.mp.getBoundingClientRect();gh.style.left=(x+(r.left-x)*e)+"px";gh.style.top=(y+(r.top-y)*e-Math.sin(Math.PI*p)*60)+"px";if(p<1)requestAnimationFrame(step);else{{gh.remove();S.fl--;eat(f)}}}})(t0);}}
function eat(f){{var good=f[2]>0;s=cl(s+f[2],-6,6);good?cg++:cb++;if(!good && secilenZararliBesinler.indexOf(f[1])===-1)secilenZararliBesinler.push(f[1]);S.chewE=S.t+1;S.mb=good?.6:-.3;P(good?"Sağlıklı! 💪":"Sağlıksız! 🤢",S.x,S.hyA-75,0,-35,{{sz:20,fill:good?"#2e9e5b":"#e0523f",bold:1,ttl:1.3}});$("msg").textContent=(good?"✅ ":"⚠️ ")+f[3];var st=state();if(st!=prev){{if(st=="fit"){{confetti();S.air=1;S.vy=-620;S.flip=1}}prev=st}}draw()}}
function draw(){{var st=state();$("ptr").style.left=(50+s/6*46)+"%";$("cg").textContent=cg;$("cb").textContent=cb;E.sv.setAttribute("class",st=="fit"?"sf":st=="obez"?"so":"sn");$("st").textContent=st=="fit"?"💪 Ali sağlıklı ve fit!":st=="obez"?"😟 Ali obez oldu!":"🙂 Ali iyi durumda.";$("st").style.color=st=="fit"?"var(--ok)":st=="obez"?"var(--bad)":"var(--tx)"}}
$("jb").onclick=function(){{if(S.air)return;var st=state();S.air=1;S.vy=st=="fit"?-640:-360;S.flip=st=="fit"?1:0;dust(6)}};
$("wb").onclick=function(){{S.tx=S.x<300?rnd(360,500):rnd(100,240);S.walk=1}};
$("rb").onclick=function(){{s=0;cg=0;cb=0;prev="normal";secilenZararliBesinler=[];S.tx=S.x=300;S.walk=0;S.y=0;S.air=0;draw()}};
var g=$("grid");
FD.forEach(function(f){{var d=document.createElement("div");d.className="food";d.innerHTML=f[0]+"<small>"+f[1]+"</small>";
 d.onpointerdown=function(e){{d.setPointerCapture(e.pointerId);drag={{f:f,sx:e.clientX,sy:e.clientY,m:0,gh:null}}}};
 d.onpointermove=function(e){{if(!drag)return;if(!drag.m&&Math.hypot(e.clientX-drag.sx,e.clientY-drag.sy)>8){{drag.m=1;drag.gh=document.createElement("div");drag.gh.className="ghost";drag.gh.textContent=f[0];document.body.appendChild(drag.gh)}}if(drag.m){{drag.gh.style.left=e.clientX+"px";drag.gh.style.top=e.clientY+"px";var r=E.mp.getBoundingClientRect();S.near=Math.hypot(e.clientX-r.left,e.clientY-r.top)<120?1:0}}}};
 d.onpointerup=function(e){{if(!drag)return;var q=drag;drag=null;S.near=0;if(!q.m){{var r=d.getBoundingClientRect();feed(q.f,r.left+r.width/2,r.top+r.height/2)}}else{{var r2=E.mp.getBoundingClientRect(),ok=Math.hypot(e.clientX-r2.left,e.clientY-r2.top)<120;q.gh.remove();if(ok)feed(q.f,e.clientX,e.clientY)}}}};
 g.appendChild(d)}});
draw();requestAnimationFrame(frame);setTimeout(autoFit,100);
</script></body></html>
"""
    components.html(html_code, height=580, scrolling=False)