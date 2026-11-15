import streamlit as st
import streamlit.components.v1 as components
import json
from urllib.parse import quote

def kesir_zari_oyunu_render(ogretmen_adi, sube_adi, ogrenciler):
    ogrenci_listesi_js = ogrenciler if ogrenciler else [{"ad": "Örnek Öğrenci", "maskot": "🦁"}]
    ogrenciler_json = json.dumps(ogrenci_listesi_js, ensure_ascii=False)
    ogretmen_enc = quote(str(ogretmen_adi))
    sube_enc = quote(str(sube_adi))

    html_code = f"""
<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>3. Sınıf Kesir Zarı</title>
<style>
  :root {{ --dice-size: 145px; }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', sans-serif; }}
  html, body {{ width: 100%; height: 100%; overflow: hidden; background: #f8fafc; color: #1E293B; user-select: none; }}
  #fitRoot {{ width: 100%; transform-origin: top center; padding: 6px; display: flex; flex-direction: column; align-items: center; }}
  .top-bar{{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;background:#fff;border:2px solid #cbd5e1;border-radius:14px;padding:6px 14px;width:100%;max-width:780px;margin-bottom:8px}}
  .student-box{{display:flex;align-items:center;gap:8px;font-weight:800;font-size:.95rem;color:#0284c7}}
  select.ogr-sel{{font:inherit;font-weight:700;padding:4px 10px;border-radius:8px;border:2px solid #0284c7;background:#f0f9ff;color:#0f172a;cursor:pointer}}
  .btn-spin{{background:#f59e0b;color:#fff;border:none;padding:6px 12px;border-radius:8px;font-weight:800;cursor:pointer}}
  .btn-save{{background:#10b981;color:#fff;border:none;padding:6px 14px;border-radius:8px;font-weight:800;cursor:pointer}}
  .btn-fs{{background:#475569;color:#fff;border:none;padding:6px 10px;border-radius:8px;font-weight:700;cursor:pointer}}
  .save-toast{{font-size:0.82rem;font-weight:700;color:#059669;display:none}}

  .scene-container {{ display: flex; flex-direction: column; align-items: center; justify-content: center; perspective: 1100px; width: 100%; padding: 14px 0 4px 0; }}
  .dice-stage {{ width: var(--dice-size); height: var(--dice-size); position: relative; transform-style: preserve-3d; transition: transform 1.2s cubic-bezier(0.18, 0.9, 0.22, 1.15); cursor: pointer; }}
  .face {{ position: absolute; width: var(--dice-size); height: var(--dice-size); background: #FFF; border: 5px solid #3B82F6; border-radius: 28px; box-shadow: inset 0 0 12px rgba(59, 130, 246, 0.15), 0 8px 20px rgba(30, 58, 138, 0.16); display: flex; flex-direction: column; justify-content: center; align-items: center; }}
  .face-front  {{ transform: rotateY(0deg) translateZ(calc(var(--dice-size) / 2)); }}
  .face-back   {{ transform: rotateY(180deg) translateZ(calc(var(--dice-size) / 2)); }}
  .face-right  {{ transform: rotateY(90deg) translateZ(calc(var(--dice-size) / 2)); }}
  .face-left   {{ transform: rotateY(-90deg) translateZ(calc(var(--dice-size) / 2)); }}
  .face-top    {{ transform: rotateX(90deg) translateZ(calc(var(--dice-size) / 2)); }}
  .face-bottom {{ transform: rotateX(-90deg) translateZ(calc(var(--dice-size) / 2)); }}
  .frac-num {{ font-size: 40px; color: #1D4ED8; font-weight: 950; line-height: 0.95; }}
  .frac-bar {{ width: 74px; height: 7px; background: #0F172A; margin: 7px 0; border-radius: 5px; }}
  .frac-den {{ font-size: 40px; color: #DC2626; font-weight: 950; line-height: 0.95; }}
  .dice-shadow {{ width: 125px; height: 16px; background: radial-gradient(ellipse at center, rgba(30, 58, 138, 0.3) 0%, transparent 70%); margin-top: 22px; border-radius: 50%; }}
  .btn-roll {{ background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%); color: #FFF; border: none; padding: 11px 24px; border-radius: 14px; font-size: 16px; font-weight: 900; cursor: pointer; box-shadow: 0 4px 14px rgba(37, 99, 235, 0.3); margin-top: 6px; }}
  .result-card {{ background: #FFF; border: 2px solid #93C5FD; border-radius: 16px; padding: 10px 18px; max-width: 480px; width: 100%; margin-top: 10px; text-align: center; }}
  .res-badge {{ display: inline-block; background: #EFF6FF; color: #2563EB; border: 1px solid #BFDBFE; font-size: 11.5px; font-weight: 800; padding: 2px 10px; border-radius: 999px; margin-bottom: 3px; }}
  .res-title {{ font-size: 19px; color: #1E3A8A; font-weight: 900; margin-bottom: 3px; }}
  .res-mission {{ font-size: 13.5px; color: #334155; }}
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
        <select id="rubrikSel" class="ogr-sel" style="border-color:#10b981;background:#ecfdf5">
            <option value="İleri Düzey">🌟 İleri Düzey</option>
            <option value="Yetkin Düzey" selected>✅ Yetkin Düzey</option>
            <option value="Gelişmekte Olan">⚠️ Gelişmekte Olan</option>
            <option value="Başlangıç Düzeyi">❌ Başlangıç Düzeyi</option>
        </select>
        <button class="btn-save" id="btnSaveResult">💾 Kaydet</button>
        <button class="btn-fs" onclick="toggleFS()">⛶</button>
    </div>
</div>
<div class="scene-container">
  <div class="dice-stage" id="dice" onclick="rollDice()">
    <div class="face face-front" id="f-front"></div>
    <div class="face face-back" id="f-back"></div>
    <div class="face face-right" id="f-right"></div>
    <div class="face face-left" id="f-left"></div>
    <div class="face face-top" id="f-top"></div>
    <div class="face-bottom face" id="f-bottom"></div>
  </div>
  <div class="dice-shadow" id="diceShadow"></div>
</div>
<button class="btn-roll" onclick="rollDice()">🎲 ZARI YUVARLA!</button>
<div class="result-card">
  <div class="res-badge" id="resBadge">GELEN KESİR: 2 / 3</div>
  <div class="res-title" id="resTitle">Üçte İki</div>
  <div class="res-mission" id="resMission">Çalışma kâğıdında <b>3 eş parçaya</b> bölünmüş bir şekil bulup <b>2 parçasını</b> boyayınız!</div>
</div>
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
var sel = document.getElementById("ogrSelect");
OGRENCILER.forEach(function(o) {{ var opt = document.createElement("option"); opt.value = o.ad; opt.textContent = (o.maskot || "🦁") + " " + o.ad; sel.appendChild(opt); }});
document.getElementById("btnRandom").onclick = function() {{
    if (OGRENCILER.length > 1) {{ var sayac = 0; var iv = setInterval(function() {{ sel.selectedIndex = Math.floor(Math.random() * OGRENCILER.length); if (++sayac > 12) clearInterval(iv); }}, 60); }}
}};
const fractionsPool = [
  {{ num: 1, den: 2, name: "Yarım (İkide Bir)" }}, {{ num: 1, den: 3, name: "Üçte Bir" }}, {{ num: 2, den: 3, name: "Üçte İki" }},
  {{ num: 1, den: 4, name: "Çeyrek (Dörtte Bir)" }}, {{ num: 2, den: 4, name: "Dörtte İki" }}, {{ num: 3, den: 4, name: "Dörtte Üç" }},
  {{ num: 1, den: 5, name: "Beşte Bir" }}, {{ num: 2, den: 5, name: "Beşte İki" }}, {{ num: 4, den: 5, name: "Beşte Dört" }},
  {{ num: 1, den: 6, name: "Altıda Bir" }}, {{ num: 5, den: 6, name: "Altıda Beş" }}, {{ num: 1, den: 7, name: "Yedide Bir" }},
  {{ num: 3, den: 7, name: "Yedide Üç" }}, {{ num: 5, den: 7, name: "Yedide Beş" }}, {{ num: 1, den: 8, name: "Sekizde Bir" }},
  {{ num: 3, den: 8, name: "Sekizde Üç" }}, {{ num: 5, den: 8, name: "Sekizde Beş" }}, {{ num: 7, den: 8, name: "Sekizde Yedi" }}
];
let currentFrac = fractionsPool[2], isRolling = false, baseRounds = 4;
const faceTargets = [{{ id: 'front', rx: 0, ry: 0 }}, {{ id: 'back', rx: 0, ry: 180 }}, {{ id: 'right', rx: 0, ry: -90 }}, {{ id: 'left', rx: 0, ry: 90 }}, {{ id: 'top', rx: -90, ry: 0 }}, {{ id: 'bottom', rx: 90, ry: 0 }}];
function buildFracHtml(num, den) {{ return `<div style="display:flex;flex-direction:column;align-items:center"><span class="frac-num">${{num}}</span><div class="frac-bar"></div><span class="frac-den">${{den}}</span></div>`; }}
faceTargets.forEach((f, idx) => {{ const frac = fractionsPool[idx % fractionsPool.length]; document.getElementById(`f-${{f.id}}`).innerHTML = buildFracHtml(frac.num, frac.den); }});
function rollDice() {{
  if (isRolling) return; isRolling = true;
  const dice = document.getElementById('dice'), targetFace = faceTargets[Math.floor(Math.random() * faceTargets.length)], selectedFrac = fractionsPool[Math.floor(Math.random() * fractionsPool.length)];
  currentFrac = selectedFrac; document.getElementById(`f-${{targetFace.id}}`).innerHTML = buildFracHtml(selectedFrac.num, selectedFrac.den);
  baseRounds += 3; const rx = targetFace.rx + (baseRounds * 360), ry = targetFace.ry + (baseRounds * 360);
  dice.style.transform = `rotateX(${{rx}}deg) rotateY(${{ry}}deg) scale(1.12)`;
  setTimeout(() => {{
    dice.style.transform = `rotateX(${{rx}}deg) rotateY(${{ry}}deg) scale(1)`;
    document.getElementById('resBadge').textContent = `GELEN KESİR: ${{currentFrac.num}} / ${{currentFrac.den}}`;
    document.getElementById('resTitle').textContent = currentFrac.name;
    document.getElementById('resMission').innerHTML = `Çalışma kâğıdında <b>${{currentFrac.den}} eş parçaya</b> bölünmüş bir şekil bulup <b>${{currentFrac.num}} parçasını</b> boyayınız!`;
    isRolling = false;
  }}, 1200);
}}
document.getElementById("btnSaveResult").onclick = function() {{
    var ogrAd = sel.value, durum = document.getElementById("rubrikSel").value, kesirStr = currentFrac.num + "/" + currentFrac.den + " (" + currentFrac.name + ")";
    var guclu = kesirStr + " kesrini pay ve payda anlamına uygun olarak modelledi.", yanilgi = durum.indexOf("Başlangıç") !== -1 ? "Pay ve payda yerlerini karıştırarak eş parça sayısını yanlış belirledi." : "Belirgin bir kavram yanılgısı tespit edilmedi.";
    new Image().src = "http://127.0.0.1:8765/cark_kaydet?ogr=" + encodeURIComponent(ogrAd) + "&durum=" + encodeURIComponent(durum) + "&gorev=" + encodeURIComponent("Kesir Zarı Modelleme: " + kesirStr) + "&model=" + encodeURIComponent("3D Kesir Zarı") + "&guclu=" + encodeURIComponent(guclu) + "&yanilgi=" + encodeURIComponent(yanilgi) + "&oneri=" + encodeURIComponent("Kesir şeritleri ve katlama kâğıtlarıyla birim kesir sayma etkinliği önerilir.") + "&ogretmen=" + OGRETMEN_ENC + "&sube=" + SUBE_ENC;
    var toast = document.getElementById("saveToast"); toast.style.display = "inline"; setTimeout(function() {{ toast.style.display = "none"; }}, 3000);
}};
setTimeout(autoFit, 100);
</script>
</body>
</html>
"""
    components.html(html_code, height=580, scrolling=False)