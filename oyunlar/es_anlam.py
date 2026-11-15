import streamlit as st
import streamlit.components.v1 as components
import json
from urllib.parse import quote

def es_anlam_oyunu_render(ogretmen_adi, sube_adi, ogrenciler):
    ogrenci_listesi_js = ogrenciler if ogrenciler else [{"ad": "Örnek Öğrenci", "maskot": "🦁"}]
    ogrenciler_json = json.dumps(ogrenci_listesi_js, ensure_ascii=False)
    ogretmen_enc = quote(str(ogretmen_adi))
    sube_enc = quote(str(sube_adi))

    html_code = f"""
<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Eş Kardeşlerin Gizemli Kutusu</title>
<style>
:root{{--bg:#e9f1ff;--panel:#fff;--ink:#1d2a44;--muted:#5b6b8c;--accent:#3b6df0;--box2:#5f7399;--card:#fff8dc;--cardb:#e0c870;--line:#c9d6f0;--ok:#1f9d63;--bad:#d9534f}}
*{{box-sizing:border-box}}
html,body{{margin:0;padding:0;width:100%;height:100%;overflow:hidden;background:#f8fafc;color:var(--ink);font-family:"Trebuchet MS","Segoe UI",Arial,sans-serif}}
#fitRoot{{width:100%;transform-origin:top center;padding:6px}}
.top-bar{{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;background:#fff;border:2px solid #cbd5e1;border-radius:14px;padding:6px 14px;max-width:1100px;margin:0 auto 6px auto}}
.student-box{{display:flex;align-items:center;gap:8px;font-weight:800;font-size:.95rem;color:#0284c7}}
select.ogr-sel{{font:inherit;font-weight:700;padding:4px 10px;border-radius:8px;border:2px solid #0284c7;background:#f0f9ff;color:#0f172a;cursor:pointer}}
.btn-spin{{background:#f59e0b;color:#fff;border:none;padding:6px 12px;border-radius:8px;font-weight:800;cursor:pointer}}
.btn-save{{background:#10b981;color:#fff;border:none;padding:6px 14px;border-radius:8px;font-weight:800;cursor:pointer}}
.btn-fs{{background:#475569;color:#fff;border:none;padding:6px 10px;border-radius:8px;font-weight:700;cursor:pointer}}
.save-toast{{font-size:0.82rem;font-weight:700;color:#059669;display:none}}
main{{max-width:1100px;margin:0 auto;display:flex;flex-direction:column;gap:6px}}
.wrap{{display:grid;grid-template-columns:minmax(0,1fr) 250px;gap:8px;align-items:stretch}}
.scene{{position:relative;container-type:inline-size;background:var(--panel);border:2px solid var(--line);border-radius:16px;overflow:hidden;max-height:310px;aspect-ratio:7/4;justify-self:center;width:100%}}
svg{{display:block;width:100%;height:100%;object-fit:contain}}
#screen{{position:absolute;left:26.4%;top:21%;width:47.1%;height:24%;display:flex;align-items:center;justify-content:center;text-align:center;font-size:2.8cqw;font-weight:800;line-height:1.2;color:var(--ink)}}
#screen.q{{font-size:7cqw;color:var(--box2)}}
#screen.nm{{font-size:3.2cqw}}
#out{{position:absolute;left:15%;width:70%;top:72%;height:24%;display:flex;align-items:center;justify-content:center}}
.sent{{font-size:2.8cqw;font-weight:800;text-align:center;background:var(--card);border:.5cqw solid var(--ok);border-radius:1.6cqw;padding:.8cqw 1.6cqw}}
.sent.bad{{border-color:var(--bad);color:var(--bad)}}
.hint{{font-size:2.2cqw;color:var(--muted);font-weight:700}}
.hl,.hl2{{display:inline-block;margin:0 .18em;background:#ffe066;color:#1d2a44;border-radius:4px;padding:0 4px}}
.machine-help{{display:flex;justify-content:center}}
.machine-help button{{font:inherit;font-weight:800;font-size:.9rem;padding:6px 14px;border-radius:10px;border:2px solid #7c5cf0;background:#fff;color:#44318e;cursor:pointer}}
.dialog{{display:none;position:fixed;inset:0;z-index:100;background:rgba(15,25,48,.62);align-items:center;justify-content:center}}
.dialog.show{{display:flex}}
.dialog-card{{width:min(480px,92vw);background:var(--panel);border:3px solid var(--line);border-radius:20px;padding:20px;text-align:center}}
.dialog-actions{{display:flex;justify-content:center;gap:8px;margin-top:12px}}
.dialog-actions button{{font:inherit;font-weight:800;padding:8px 14px;border:0;border-radius:8px;background:var(--accent);color:white;cursor:pointer}}
.dialog-actions .secondary{{background:transparent;color:var(--muted);border:2px solid var(--line)}}
.blank-input{{width:70px;padding:5px;font-weight:900;font-size:1.2rem;border:3px dashed #7c5cf0;background:#f1edff;color:#44318e;text-align:center;border-radius:8px}}
.tray{{display:flex;flex-wrap:wrap;gap:5px;justify-content:center}}
.card{{font:inherit;font-size:.82rem;line-height:1.25;font-weight:700;text-align:left;color:var(--ink);background:var(--card);border:2px solid var(--cardb);border-radius:10px;padding:5px 8px;max-width:205px;cursor:grab;user-select:none}}
.card.used{{opacity:.3;pointer-events:none}}
.card.drag{{position:fixed;z-index:50;margin:0;cursor:grabbing;transform:rotate(-4deg) scale(1.08)}}
.card.drag.fly{{transition:all .45s ease-in;transform:scale(.15);opacity:0}}
.card.drag.back{{transition:all .25s}}
.side{{background:var(--panel);border:2px solid var(--line);border-radius:16px;padding:8px;display:flex;flex-direction:column;max-height:310px}}
.side h2{{font-size:.9rem;margin:0 0 6px;text-align:center;color:var(--muted)}}
#log{{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:4px;overflow:auto;flex:1}}
#log li{{background:var(--card);border:1.5px solid var(--cardb);border-radius:8px;padding:4px 6px;font-weight:700;font-size:.78rem}}
#log li .n::before{{content:"↓ ";color:var(--accent)}}
#log li.ph{{background:none;border:0;color:var(--muted);font-weight:400;text-align:center}}
.ctl{{display:flex;gap:4px;margin-top:6px}}
button.act{{flex:1;font:inherit;font-weight:700;font-size:.78rem;padding:6px;border-radius:8px;border:1.5px solid var(--line);background:transparent;color:var(--muted);cursor:pointer}}
.hole{{fill:#0b1224}}.light{{fill:#2a3550}}#hit{{stroke:#1f6f7c;stroke-width:5}}#hit.hot{{stroke:#ffd23f;stroke-width:8}}
</style>
</head>
<body>
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
<main>
<div class="wrap">
<div class="scene">
<svg viewBox="0 0 700 400">
<defs>
<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#6fd6cf"/><stop offset="1" stop-color="#2f8f9d"/></linearGradient>
<g id="robot">
<path d="M82 205 Q52 240 60 278" stroke="var(--rd)" stroke-width="16" stroke-linecap="round" fill="none"/><circle cx="60" cy="282" r="11" fill="var(--rc)"/>
<rect x="92" y="290" width="22" height="64" rx="8" fill="var(--rd)"/><rect x="128" y="290" width="22" height="64" rx="8" fill="var(--rd)"/>
<rect x="84" y="348" width="38" height="16" rx="8" fill="var(--rd)"/><rect x="120" y="348" width="38" height="16" rx="8" fill="var(--rd)"/>
<rect x="80" y="176" width="82" height="118" rx="18" fill="var(--rc)"/><circle cx="121" cy="215" r="11" fill="#ffd23f"/>
<path d="M158 205 Q205 238 247 212" stroke="var(--rd)" stroke-width="16" stroke-linecap="round" fill="none"/><circle cx="250" cy="212" r="13" fill="var(--rc)"/>
<line x1="121" y1="96" x2="121" y2="74" stroke="var(--rd)" stroke-width="5"/><circle cx="121" cy="70" r="8" fill="#ffd23f"/>
<rect x="76" y="96" width="90" height="76" rx="22" fill="var(--rc)"/>
<circle cx="102" cy="130" r="14" fill="#fff"/><circle cx="140" cy="130" r="14" fill="#fff"/>
<circle cx="105" cy="132" r="6" fill="#111"/><circle cx="143" cy="132" r="6" fill="#111"/>
<path d="M104 154 Q121 166 138 154" stroke="#111" stroke-width="4" fill="none" stroke-linecap="round"/>
</g>
</defs>
<g id="all">
<g transform="translate(-27.5,31) scale(.75)"><use href="#robot" style="--rc:#4a86f5;--rd:#2f5cc0"/></g>
<g transform="translate(700,0) scale(-1,1)"><g transform="translate(-27.5,31) scale(.75)"><use href="#robot" style="--rc:#4a86f5;--rd:#2f5cc0"/></g></g>
<rect x="150" y="38" width="400" height="30" rx="9" fill="#7c5cf0"/><rect x="290" y="48" width="120" height="10" rx="5" class="hole"/>
<rect id="hit" x="160" y="66" width="380" height="200" rx="16" fill="url(#bg)"/>
<rect x="185" y="84" width="330" height="96" rx="12" fill="var(--panel)"/>
<circle class="light" cx="310" cy="205" r="10"/><circle class="light" cx="350" cy="205" r="10"/><circle class="light" cx="390" cy="205" r="10"/>
<rect x="305" y="252" width="90" height="12" rx="6" class="hole"/>
</g>
</svg>
<div id="screen" class="q">?</div>
<div id="out"><div class="hint">Bir kartı kutunun içine sürükle ve bırak!</div></div>
</div>
<aside class="side">
<h2>Kutudan çıkanlar</h2>
<ul id="log"><li class="ph">Henüz bir şey çıkmadı</li></ul>
<div class="ctl"><button class="act" id="reveal">Adını göster</button><button class="act" id="reset">Baştan başla</button></div>
</aside>
</div>
<div class="machine-help"><button id="askMachine" type="button">Makinenin sorusu: “Ben ne işe yarıyorum?”</button></div>
<div class="dialog" id="dialog"><div class="dialog-card"><h2 id="dialogTitle"></h2><div id="dialogBody"></div></div></div>
<div class="tray" id="tray"></div>
</main>
</div>
<script>
function autoFit(){{
  var r=document.getElementById('fitRoot'); r.style.transform='none';
  var h=r.scrollHeight, wh=window.innerHeight;
  if(h>wh && wh>100){{ var sc=(wh-8)/h; r.style.transform='scale('+sc+')'; }}
}}
window.addEventListener('resize',autoFit);
function toggleFS(){{if(!document.fullscreenElement)document.documentElement.requestFullscreen().catch(()=>{{}});else document.exitFullscreen();}}

var OGRENCILER = {ogrenciler_json}, OGRETMEN_ENC = "{ogretmen_enc}", SUBE_ENC = "{sube_enc}";
var bulunanEsAnlamSayisi = 0, hataliKartDenemesi = 0, kuraliKesfettiMi = false;
var sel = document.getElementById("ogrSelect");
OGRENCILER.forEach(function(o) {{ var opt = document.createElement("option"); opt.value = o.ad; opt.textContent = (o.maskot || "🦁") + " " + o.ad; sel.appendChild(opt); }});
document.getElementById("btnRandom").onclick = function() {{
    if (OGRENCILER.length > 1) {{ var sayac = 0; var iv = setInterval(function() {{ sel.selectedIndex = Math.floor(Math.random() * OGRENCILER.length); if (++sayac > 12) clearInterval(iv); }}, 60); }}
    bulunanEsAnlamSayisi = 0; hataliKartDenemesi = 0; kuraliKesfettiMi = false; document.getElementById("reset").click();
}};
document.getElementById("btnSaveResult").onclick = function() {{
    var ogrAd = sel.value, durum = "Gelişmekte Olan", guclu = "Eş anlamlı kelimeleri cümle bağlamında deniyor.", yanilgi = "Belirgin bir kavram yanılgısı tespit edilmedi.";
    if (kuraliKesfettiMi && bulunanEsAnlamSayisi >= 4 && hataliKartDenemesi === 0) {{ durum = "İleri Düzey"; guclu = "Eş anlamlı kelimeleri eksiksiz ayırt etti ve 'Eş Anlam' kuralını keşfetti."; }}
    else if (bulunanEsAnlamSayisi >= 3) {{ durum = "Yetkin Düzey"; guclu = bulunanEsAnlamSayisi + " adet eş anlamlı kelime dönüşümünü tamamladı."; }}
    else {{ durum = "Başlangıç Düzeyi"; if (hataliKartDenemesi > 0) yanilgi = "Eş anlamlısı olmayan kelimeleri eş anlamlı sanarak kutuya attı."; }}
    new Image().src = "http://127.0.0.1:8765/cark_kaydet?ogr=" + encodeURIComponent(ogrAd) + "&durum=" + encodeURIComponent(durum) + "&gorev=" + encodeURIComponent("Eş Anlamlı Kelimeler (" + bulunanEsAnlamSayisi + " Eşleşme)") + "&model=" + encodeURIComponent("Eş Kardeşlerin Gizemli Kutusu") + "&guclu=" + encodeURIComponent(guclu) + "&yanilgi=" + encodeURIComponent(yanilgi) + "&oneri=" + encodeURIComponent("Eş anlamlı kelime kartlarıyla cümle kurma etkinliği yapılabilir.") + "&ogretmen=" + OGRETMEN_ENC + "&sube=" + SUBE_ENC;
    var toast = document.getElementById("saveToast"); toast.style.display = "inline"; setTimeout(function() {{ toast.style.display = "none"; }}, 3000);
}};
const D=[["Annem bana bir ","hediye"," aldı.","armağan"],["Evimize ","misafir"," geldi.","konuk"],["Sorunun ","cevabını"," söyledim.","yanıtını"],["Bu ","yıl"," çok kitap okudum.","sene"],["Yaşadığım ","şehir"," çok güzel.","kent"],["Bir ","öykü"," okudum.","hikâye"],["Bu ","kelimenin"," anlamını öğrendim.","sözcüğün"],["Geçen gün güzel bir ","anı"," yaşadım.","hatıra"],["Masanın üstünde bir ","kitap"," var.",null],["Çantamda yeni bir ","defter"," var.",null]];
const $=id=>document.getElementById(id), tray=$("tray"),all=$("all"),screen=$("screen"),out=$("out"),hit=$("hit"),log=$("log"), HINT='<div class="hint">Bir kartı kutunun içine sürükle ve bırak!</div>';
let busy=false; const old=d=>d[0]+'<span class="hl">'+d[1]+'</span>'+d[2], neu=d=>d[0]+'<span class="hl2">'+d[3]+'</span>'+d[2];
function setScreen(html,cls){{screen.className=cls||"";screen.innerHTML=html;}}
function inBox(x,y){{const r=hit.getBoundingClientRect();return x>=r.left-30&&x<=r.right+30&&y>=r.top-50&&y<=r.bottom+10;}}
function build(){{tray.innerHTML="";D.forEach((d,i)=>{{const b=document.createElement("button");b.className="card";b.innerHTML=old(d);b.addEventListener("pointerdown",e=>startDrag(e,b,i));tray.appendChild(b);}});setTimeout(autoFit,50);}}
function startDrag(e,b,i){{if(busy)return;e.preventDefault();const r=b.getBoundingClientRect(),dx=e.clientX-r.left,dy=e.clientY-r.top,c=b.cloneNode(true);c.className="card drag";c.style.width=r.width+"px";c.style.left=r.left+"px";c.style.top=r.top+"px";document.body.appendChild(c);b.style.opacity=".3";c.setPointerCapture(e.pointerId);c.addEventListener("pointermove",m=>{{c.style.left=(m.clientX-dx)+"px";c.style.top=(m.clientY-dy)+"px";hit.classList.toggle("hot",inBox(m.clientX,m.clientY));}});const end=m=>{{hit.classList.remove("hot");if(inBox(m.clientX,m.clientY)){{busy=true;b.classList.add("used");b.style.opacity="";const s=document.querySelector(".hole").getBoundingClientRect();c.classList.add("fly");c.style.left=(s.left+s.width/2-r.width/2)+"px";c.style.top=(s.top-10)+"px";setTimeout(()=>{{c.remove();work(i);}},450);}}else{{c.classList.add("back");c.style.left=r.left+"px";c.style.top=r.top+"px";setTimeout(()=>{{c.remove();b.style.opacity="";}},250);}}}};c.addEventListener("pointerup",end);c.addEventListener("pointercancel",end);}}
function work(i){{const d=D[i];busy=true;out.innerHTML="";setScreen(old(d));setTimeout(()=>{{const o=document.createElement("div");if(d[3]){{o.className="sent";o.innerHTML=neu(d);const ph=log.querySelector(".ph");if(ph)ph.remove();const li=document.createElement("li");li.innerHTML='<div>'+old(d)+'</div><div class="n">'+neu(d)+'</div>';log.prepend(li);bulunanEsAnlamSayisi++;}}else{{o.className="sent bad";o.textContent="? Kutu şaşırdı. Sence neden çalışmadı?";hataliKartDenemesi++;}}out.appendChild(o);busy=false;}},700);}}
const dialog=$("dialog"),dialogTitle=$("dialogTitle"),dialogBody=$("dialogBody");
$("askMachine").onclick=()=>{{dialogTitle.textContent="Ben ne işe yarıyorum?";dialogBody.innerHTML=`<p style="font-size:1.2rem"><input id="answerInput" class="blank-input" type="text" maxlength="3" placeholder="..."> <strong>anlamlı kelimeleri değiştiriyorum.</strong></p><div class="dialog-actions"><button id="checkAnswer" type="button">Gönder</button><button id="closeDialog" class="secondary" type="button">Kapat</button></div><p id="answerFeedback"></p>`;dialog.classList.add("show");$("answerInput").focus();$("checkAnswer").onclick=()=>{{if($("answerInput").value.trim().toLocaleLowerCase("tr-TR")==="eş"){{kuraliKesfettiMi=true;dialogTitle.textContent="Tebrikler!";dialogBody.innerHTML=`<p><strong>Harika! Eş anlamlı kelimeleri keşfettin.</strong></p><div class="dialog-actions"><button id="closeOk" type="button">Devam Et</button></div>`;$("closeOk").onclick=()=>dialog.classList.remove("show");}}else $("answerFeedback").textContent="Biraz daha düşün!";}};$("closeDialog").onclick=()=>dialog.classList.remove("show");}};
$("reveal").onclick=()=>{{if(!busy)setScreen("EŞ ANLAM<br>MAKİNESİ","nm");}};
$("reset").onclick=()=>{{out.innerHTML=HINT;setScreen("?","q");log.innerHTML='<li class="ph">Henüz bir şey çıkmadı</li>';busy=false;build();}};
build();
</script>
</body>
</html>
"""
    components.html(html_code, height=580, scrolling=False)