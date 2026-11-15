import streamlit as st
import streamlit.components.v1 as components
import json
from urllib.parse import quote

def kesir_goleti_oyunu_render(ogretmen_adi, sube_adi, ogrenciler):
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
<title>Süper Kesir Göleti</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', sans-serif; }}
  html, body {{ width: 100%; height: 100%; overflow: hidden; background: #f8fafc; color: #0F172A; user-select: none; }}
  #fitRoot {{ width: 100%; transform-origin: top center; padding: 6px; display: flex; flex-direction: column; align-items: center; }}
  .top-bar{{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;background:#fff;border:2px solid #cbd5e1;border-radius:14px;padding:6px 14px;width:100%;max-width:980px;margin-bottom:6px}}
  .student-box{{display:flex;align-items:center;gap:8px;font-weight:800;font-size:.95rem;color:#0284c7}}
  select.ogr-sel{{font:inherit;font-weight:700;padding:4px 10px;border-radius:8px;border:2px solid #0284c7;background:#f0f9ff;color:#0f172a;cursor:pointer}}
  .btn-spin{{background:#f59e0b;color:#fff;border:none;padding:6px 12px;border-radius:8px;font-weight:800;cursor:pointer}}
  .btn-save{{background:#10b981;color:#fff;border:none;padding:6px 14px;border-radius:8px;font-weight:800;cursor:pointer}}
  .btn-fs{{background:#475569;color:#fff;border:none;padding:6px 10px;border-radius:8px;font-weight:700;cursor:pointer}}
  .save-toast{{font-size:0.82rem;font-weight:700;color:#059669;display:none}}

  header {{ width: 100%; max-width: 980px; display: flex; justify-content: space-between; align-items: center; background: #fff; padding: 6px 16px; border-radius: 14px; border: 2px solid #BAE6FD; margin-bottom: 4px; }}
  .game-title {{ font-size: 16px; font-weight: 900; color: #0369A1; }}
  .stat-badge {{ background: #EFF6FF; border: 1.5px solid #BFDBFE; padding: 3px 9px; border-radius: 10px; font-size: 12.5px; font-weight: 800; color: #1D4ED8; }}
  .btn-char-select {{ background: linear-gradient(135deg, #F59E0B, #D97706); color: white; border: none; padding: 5px 10px; border-radius: 8px; font-size: 12px; font-weight: 800; cursor: pointer; }}

  .speech-bubble {{ background: #FFF; border: 3px solid #22C55E; border-radius: 16px; padding: 5px 20px; text-align: center; margin-bottom: 4px; }}
  .bubble-target {{ font-size: 22px; font-weight: 950; color: #1E3A8A; }}
  .bubble-hint {{ font-size: 11.5px; color: #64748B; font-weight: 600; }}

  .pond-area {{ width: 100%; max-width: 980px; height: 310px; background: radial-gradient(ellipse at center, #38BDF8 0%, #0284C7 100%); border: 4px solid #FCD34D; border-radius: 26px; position: relative; overflow: hidden; margin: 2px 0; }}
  .start-island {{ position: absolute; bottom: 10px; left: 50%; transform: translateX(-50%); width: 150px; height: 48px; background: radial-gradient(ellipse at center, #94A3B8 0%, #475569 100%); border-radius: 50%; border: 3px solid #CBD5E1; z-index: 5; }}
  .lilypads-container {{ position: absolute; top: 14px; left: 0; right: 0; display: flex; justify-content: space-around; padding: 0 16px; z-index: 10; }}
  .lilypad-card {{ display: flex; flex-direction: column; align-items: center; cursor: pointer; transition: transform 0.2s; width: 160px; }}
  .lilypad-card:hover {{ transform: translateY(-5px) scale(1.04); }}
  .lily-leaf {{ width: 148px; height: 116px; background: radial-gradient(circle at 40% 40%, #4ADE80 0%, #16A34A 70%, #14532D 100%); border-radius: 50%; position: relative; border: 4px solid #86EFAC; display: flex; align-items: center; justify-content: center; }}
  .fraction-model-box {{ width: 82px; height: 82px; display: flex; align-items: center; justify-content: center; background: #FFF; border-radius: 12px; border: 2.5px solid #0F172A; padding: 5px; }}
  .model-svg {{ width: 100%; height: 100%; display: block; }}
  .player-character {{ position: absolute; width: 82px; height: 82px; z-index: 25; pointer-events: none; transition: transform 0.6s, left 0.6s ease, top 0.6s ease, opacity 0.3s; }}
  .feedback-bar {{ width: 100%; max-width: 760px; background: #FFF; border-radius: 12px; padding: 6px 16px; display: flex; justify-content: space-between; align-items: center; border: 2px solid #E2E8F0; margin-top: 4px; }}
  .feedback-msg {{ font-size: 13px; font-weight: 800; color: #0369A1; }}
  .char-select-modal, .game-modal {{ position: fixed; inset: 0; background: rgba(15, 23, 42, 0.75); display: none; align-items: center; justify-content: center; z-index: 100; }}
  .char-modal-box, .modal-card {{ background: #FFF; border-radius: 20px; padding: 20px; text-align: center; max-width: 420px; width: 90%; }}
  .char-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; margin: 12px 0; }}
  .char-card {{ background: #F8FAFC; border: 2px solid #E2E8F0; border-radius: 14px; padding: 8px; cursor: pointer; }}
  .char-card.selected {{ border-color: #10B981; background: #ECFDF5; }}
  .btn-close-char, .btn-modal {{ background: #2563EB; color: white; border: none; padding: 8px 18px; border-radius: 10px; font-weight: 800; cursor: pointer; }}
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
<header>
  <div class="game-title" id="gameHeaderTitle">🐸 Zıpzıp ile Kesir Göleti</div>
  <div style="display:flex;gap:8px;align-items:center;">
    <div class="stat-badge">⭐ Puan: <span id="scoreVal">0</span></div>
    <div class="stat-badge">🎯 Soru: <span id="qNumVal">1/16</span></div>
    <div id="livesContainer" style="font-size:15px;"><span>❤️</span><span>❤️</span><span>❤️</span></div>
    <button class="btn-char-select" onclick="document.getElementById('charModal').style.display='flex'">🐾 Canlı Seç</button>
  </div>
</header>
<div class="speech-bubble">
  <div class="bubble-target" id="targetPrompt">YARIM</div>
  <div class="bubble-hint" id="targetHint">Bütünün 2 eş parçasından 1'ini gösteren yaprağı bul!</div>
</div>
<div class="pond-area" id="pondArea">
  <div class="lilypads-container" id="lilypadsBox"></div>
  <div class="start-island" id="startIsland"></div>
  <div class="player-character" id="playerChar"></div>
</div>
<div class="feedback-bar">
  <div class="feedback-msg" id="feedbackMsg">Doğru nilüfer yaprağına tıkla!</div>
  <div style="font-weight:800;color:#B45309;font-size:13px" id="streakBadge">🔥 Seri: 0</div>
</div>
</div>
<div class="char-select-modal" id="charModal">
  <div class="char-modal-box">
    <h3>🐾 Karakterini Seç!</h3>
    <div class="char-grid">
      <div class="char-card selected" id="cCard-frog" onclick="selectCharacter('frog')"><div style="font-size:32px">🐸</div><b>Kurbağa</b></div>
      <div class="char-card" id="cCard-duck" onclick="selectCharacter('duck')"><div style="font-size:32px">🦆</div><b>Ördek</b></div>
      <div class="char-card" id="cCard-turtle" onclick="selectCharacter('turtle')"><div style="font-size:32px">🐢</div><b>Kaplumbağa</b></div>
      <div class="char-card" id="cCard-bunny" onclick="selectCharacter('bunny')"><div style="font-size:32px">🐰</div><b>Tavşan</b></div>
    </div>
    <button class="btn-close-char" onclick="document.getElementById('charModal').style.display='none'">Tamam 👍</button>
  </div>
</div>
<div class="game-modal" id="gameModal">
  <div class="modal-card">
    <h2 id="modalTitle">Harika!</h2>
    <p id="modalDesc" style="margin:8px 0 14px 0"></p>
    <button class="btn-modal" onclick="restartGame()">Yeniden Oyna 🔄</button>
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
var dogruAtlayis = 0, yanlisAtlayis = 0;
var sel = document.getElementById("ogrSelect");
OGRENCILER.forEach(function(o) {{ var opt = document.createElement("option"); opt.value = o.ad; opt.textContent = (o.maskot || "🦁") + " " + o.ad; sel.appendChild(opt); }});
document.getElementById("btnRandom").onclick = function() {{
    if (OGRENCILER.length > 1) {{ var sayac = 0; var iv = setInterval(function() {{ sel.selectedIndex = Math.floor(Math.random() * OGRENCILER.length); if (++sayac > 12) clearInterval(iv); }}, 60); }}
    dogruAtlayis = 0; yanlisAtlayis = 0; restartGame();
}};
document.getElementById("btnSaveResult").onclick = function() {{
    var ogrAd = sel.value, durum = "Gelişmekte Olan", guclu = "Birim ve basit kesir modellerini tanımaya başladı.", yanilgi = "Belirgin bir kavram yanılgısı tespit edilmedi.";
    if (dogruAtlayis >= 4 && yanlisAtlayis === 0) {{ durum = "İleri Düzey"; guclu = "Bütün, yarım, çeyrek ve basit kesir modellerini hatasız eşleştirdi (" + dogruAtlayis + " doğru)."; }}
    else if (dogruAtlayis > yanlisAtlayis && dogruAtlayis >= 2) {{ durum = "Yetkin Düzey"; guclu = "Kesir modellerini çoğunlukla doğru okudu (" + dogruAtlayis + " doğru, " + yanlisAtlayis + " yanlış)."; }}
    else if (yanlisAtlayis >= dogruAtlayis) {{ durum = "Başlangıç Düzeyi"; yanilgi = "Eş parça sayısını (payda) veya boyalı parça sayısını (pay) sayarken karıştırma gözlendi."; }}
    new Image().src = "http://127.0.0.1:8765/cark_kaydet?ogr=" + encodeURIComponent(ogrAd) + "&durum=" + encodeURIComponent(durum) + "&gorev=" + encodeURIComponent("Kesir Göleti (" + dogruAtlayis + " Doğru, " + yanlisAtlayis + " Yanlış)") + "&model=" + encodeURIComponent("Süper Kesir Göleti") + "&guclu=" + encodeURIComponent(guclu) + "&yanilgi=" + encodeURIComponent(yanilgi) + "&oneri=" + encodeURIComponent("Kesir kartlarıyla pay ve payda eşleştirme alıştırması yapılabilir.") + "&ogretmen=" + OGRETMEN_ENC + "&sube=" + SUBE_ENC;
    var toast = document.getElementById("saveToast"); toast.style.display = "inline"; setTimeout(function() {{ toast.style.display = "none"; }}, 3000);
}};
const characters = {{
  frog: {{ title: "🐸 Zıpzıp ile Kesir Göleti", svg: `<svg viewBox="0 0 100 100" width="100%" height="100%"><ellipse cx="50" cy="60" rx="38" ry="28" fill="#22C55E"/><ellipse cx="50" cy="65" rx="25" ry="18" fill="#FEF08A"/><ellipse cx="50" cy="38" rx="34" ry="25" fill="#22C55E"/><circle cx="32" cy="20" r="14" fill="#22C55E"/><circle cx="68" cy="20" r="14" fill="#22C55E"/><circle cx="32" cy="20" r="10" fill="#FFF"/><circle cx="68" cy="20" r="10" fill="#FFF"/><circle cx="33" cy="20" r="5" fill="#0F172A"/><circle cx="67" cy="20" r="5" fill="#0F172A"/><path d="M 34 44 Q 50 58 66 44" fill="none" stroke="#0F172A" stroke-width="3.5" stroke-linecap="round"/></svg>` }},
  duck: {{ title: "🦆 Paytak ile Kesir Göleti", svg: `<svg viewBox="0 0 100 100" width="100%" height="100%"><ellipse cx="50" cy="58" rx="36" ry="27" fill="#FACC15"/><circle cx="50" cy="34" r="24" fill="#FACC15"/><circle cx="39" cy="27" r="5" fill="#0F172A"/><circle cx="61" cy="27" r="5" fill="#0F172A"/><ellipse cx="50" cy="42" rx="16" ry="9" fill="#EA580C"/></svg>` }},
  turtle: {{ title: "🐢 Tosbik ile Kesir Göleti", svg: `<svg viewBox="0 0 100 100" width="100%" height="100%"><ellipse cx="50" cy="58" rx="36" ry="30" fill="#16A34A" stroke="#14532D" stroke-width="3"/><ellipse cx="50" cy="26" rx="20" ry="17" fill="#4ADE80"/><circle cx="42" cy="22" r="4" fill="#0F172A"/><circle cx="58" cy="22" r="4" fill="#0F172A"/></svg>` }},
  bunny: {{ title: "🐰 Pofuduk ile Kesir Göleti", svg: `<svg viewBox="0 0 100 100" width="100%" height="100%"><ellipse cx="34" cy="14" rx="9" ry="20" fill="#FFF" stroke="#CBD5E1" stroke-width="2"/><ellipse cx="66" cy="14" rx="9" ry="20" fill="#FFF" stroke="#CBD5E1" stroke-width="2"/><ellipse cx="50" cy="64" rx="34" ry="26" fill="#FFF"/><circle cx="50" cy="38" r="23" fill="#FFF"/><circle cx="40" cy="34" r="5" fill="#0F172A"/><circle cx="60" cy="34" r="5" fill="#0F172A"/></svg>` }}
}};
const questionsBank = [
  {{ prompt: "YARIM", hint: "Bütünün 2 eş parçasından 1'ini gösteren yaprağı seç!", targetKey: "1_2", options: [{{ key: "1_2", type: "circle", parts: 2, shaded: 1 }}, {{ key: "1_4", type: "circle", parts: 4, shaded: 1 }}, {{ key: "1_1", type: "circle", parts: 1, shaded: 1 }}] }},
  {{ prompt: "ÇEYREK", hint: "Bütünün 4 eş parçasından 1'ini temsil eden modeli seç!", targetKey: "1_4", options: [{{ key: "1_2", type: "square", parts: 2, shaded: 1 }}, {{ key: "1_4", type: "square", parts: 4, shaded: 1 }}, {{ key: "3_4", type: "square", parts: 4, shaded: 3 }}] }},
  {{ prompt: "TAM (1 BÜTÜN)", hint: "Hiç parçalanmamış, eksiksiz tam 1 bütünü bul!", targetKey: "1_1", options: [{{ key: "1_4", type: "square", parts: 4, shaded: 1 }}, {{ key: "1_1", type: "circle", parts: 1, shaded: 1 }}, {{ key: "1_2", type: "rect", parts: 2, shaded: 1 }}] }},
  {{ prompt: "DÖRTTE ÜÇ (3/4)", hint: "4 eş parçaya bölünmüş ve 3 parçası boyanmış yaprağı bul!", targetKey: "3_4", options: [{{ key: "1_4", type: "circle", parts: 4, shaded: 1 }}, {{ key: "3_4", type: "circle", parts: 4, shaded: 3 }}, {{ key: "2_4", type: "circle", parts: 4, shaded: 2 }}] }},
  {{ prompt: "ÜÇTE BİR (1/3)", hint: "3 eş dilimden 1'inin boyandığı nilüfer yaprağını seç!", targetKey: "1_3", options: [{{ key: "1_3", type: "circle", parts: 3, shaded: 1 }}, {{ key: "1_4", type: "circle", parts: 4, shaded: 1 }}, {{ key: "2_3", type: "circle", parts: 3, shaded: 2 }}] }},
  {{ prompt: "ÜÇTE İKİ (2/3)", hint: "3 eş parçadan 2'sinin boyandığı basit kesir modeli!", targetKey: "2_3", options: [{{ key: "1_3", type: "rect", parts: 3, shaded: 1 }}, {{ key: "2_3", type: "rect", parts: 3, shaded: 2 }}, {{ key: "1_2", type: "rect", parts: 2, shaded: 1 }}] }},
  {{ prompt: "BEŞTE İKİ (2/5)", hint: "5 eş parçalı şeridin 2 parçasının boyalı olduğu yaprak!", targetKey: "2_5", options: [{{ key: "1_5", type: "rect", parts: 5, shaded: 1 }}, {{ key: "2_5", type: "rect", parts: 5, shaded: 2 }}, {{ key: "4_5", type: "rect", parts: 5, shaded: 4 }}] }},
  {{ prompt: "ALTIDA BİR (1/6)", hint: "6 eş dilimden tam 1 tanesinin boyandığı birim kesri bul!", targetKey: "1_6", options: [{{ key: "1_6", type: "circle", parts: 6, shaded: 1 }}, {{ key: "3_6", type: "circle", parts: 6, shaded: 3 }}, {{ key: "5_6", type: "circle", parts: 6, shaded: 5 }}] }},
  {{ prompt: "SEKİZDE BİR (1/8)", hint: "8 eş parçaya ayrılmış modelin birim kesrini seç!", targetKey: "1_8", options: [{{ key: "1_4", type: "circle", parts: 4, shaded: 1 }}, {{ key: "1_8", type: "circle", parts: 8, shaded: 1 }}, {{ key: "3_8", type: "circle", parts: 8, shaded: 3 }}] }},
  {{ prompt: "SEKİZDE ÜÇ (3/8)", hint: "8 eş dilimli dairenin tam 3 diliminin boyalı olduğu yaprak!", targetKey: "3_8", options: [{{ key: "1_8", type: "circle", parts: 8, shaded: 1 }}, {{ key: "3_8", type: "circle", parts: 8, shaded: 3 }}, {{ key: "5_8", type: "circle", parts: 8, shaded: 5 }}] }}
];
let currentQIndex = 0, score = 0, lives = 3, streak = 0, isJumping = false;
function selectCharacter(key) {{ document.getElementById('gameHeaderTitle').textContent = characters[key].title; document.getElementById('playerChar').innerHTML = characters[key].svg; document.querySelectorAll('.char-card').forEach(c => c.classList.remove('selected')); document.getElementById('cCard-' + key).classList.add('selected'); }}
function resetPlayerPosition() {{
  const pond = document.getElementById('pondArea'), pChar = document.getElementById('playerChar'), startIsland = document.getElementById('startIsland');
  const islandRect = startIsland.getBoundingClientRect(), pondRect = pond.getBoundingClientRect();
  pChar.style.left = `${{(islandRect.left - pondRect.left) + (islandRect.width / 2) - 41}}px`;
  pChar.style.top = `${{(islandRect.top - pondRect.top) - 36}}px`;
  pChar.style.opacity = "1";
}}
function getPieSlicePath(cx, cy, r, startDeg, endDeg) {{
  const rad1 = startDeg * Math.PI / 180.0, rad2 = endDeg * Math.PI / 180.0;
  const x1 = cx + r * Math.sin(rad1), y1 = cy - r * Math.cos(rad1), x2 = cx + r * Math.sin(rad2), y2 = cy - r * Math.cos(rad2);
  return `M ${{cx}} ${{cy}} L ${{x1.toFixed(2)}} ${{y1.toFixed(2)}} A ${{r}} ${{r}} 0 ${{(endDeg - startDeg > 180) ? 1 : 0}} 1 ${{x2.toFixed(2)}} ${{y2.toFixed(2)}} Z`;
}}
function generateModelSvg(type, parts, shaded) {{
  const strokeColor = "#0F172A", fillColor = "#2563EB", emptyColor = "#FFF";
  if (type === "circle") {{
    if (parts === 1) return `<svg viewBox="0 0 80 80" class="model-svg"><circle cx="40" cy="40" r="36" fill="${{fillColor}}" stroke="${{strokeColor}}" stroke-width="2.4"/></svg>`;
    let slices = '', sliceAngle = 360 / parts;
    for (let i = 0; i < parts; i++) slices += `<path d="${{getPieSlicePath(40, 40, 36, i * sliceAngle, (i + 1) * sliceAngle)}}" fill="${{i < shaded ? fillColor : emptyColor}}" stroke="${{strokeColor}}" stroke-width="2.4"/>`;
    return `<svg viewBox="0 0 80 80" class="model-svg">${{slices}}</svg>`;
  }}
  if (type === "square") {{
    if (parts === 2) return `<svg viewBox="0 0 80 80" class="model-svg"><rect x="4" y="4" width="36" height="72" fill="${{fillColor}}" stroke="${{strokeColor}}" stroke-width="2.4"/><rect x="40" y="4" width="36" height="72" fill="${{emptyColor}}" stroke="${{strokeColor}}" stroke-width="2.4"/></svg>`;
    return `<svg viewBox="0 0 80 80" class="model-svg"><rect x="4" y="4" width="36" height="36" fill="${{shaded>=1?fillColor:emptyColor}}" stroke="${{strokeColor}}" stroke-width="2.4"/><rect x="40" y="4" width="36" height="36" fill="${{shaded>=2?fillColor:emptyColor}}" stroke="${{strokeColor}}" stroke-width="2.4"/><rect x="4" y="40" width="36" height="36" fill="${{shaded>=3?fillColor:emptyColor}}" stroke="${{strokeColor}}" stroke-width="2.4"/><rect x="40" y="40" width="36" height="36" fill="${{shaded>=4?fillColor:emptyColor}}" stroke="${{strokeColor}}" stroke-width="2.4"/></svg>`;
  }}
  let colW = 72 / parts, bars = '';
  for (let i = 0; i < parts; i++) bars += `<rect x="${{4 + i * colW}}" y="13" width="${{colW}}" height="54" fill="${{i < shaded ? fillColor : emptyColor}}" stroke="${{strokeColor}}" stroke-width="2.4"/>`;
  return `<svg viewBox="0 0 80 80" class="model-svg">${{bars}}</svg>`;
}}
function loadQuestion() {{
  isJumping = false; resetPlayerPosition();
  const q = questionsBank[currentQIndex % questionsBank.length];
  document.getElementById('targetPrompt').textContent = q.prompt;
  document.getElementById('targetHint').textContent = q.hint;
  document.getElementById('qNumVal').textContent = `${{currentQIndex + 1}}/${{questionsBank.length}}`;
  const box = document.getElementById('lilypadsBox'); box.innerHTML = '';
  [...q.options].sort(() => Math.random() - 0.5).forEach((opt) => {{
    const isCorrect = (opt.key === q.targetKey);
    const card = document.createElement('div'); card.className = 'lilypad-card';
    card.innerHTML = `<div class="lily-leaf"><div class="fraction-model-box">${{generateModelSvg(opt.type, opt.parts, opt.shaded)}}</div></div>`;
    card.onclick = () => handleLeafClick(card, isCorrect);
    box.appendChild(card);
  }});
  setTimeout(autoFit, 60);
}}
function handleLeafClick(leafEl, isCorrect) {{
  if (isJumping) return; isJumping = true;
  const pChar = document.getElementById('playerChar'), pondRect = document.getElementById('pondArea').getBoundingClientRect(), leafRect = leafEl.getBoundingClientRect();
  pChar.style.left = `${{(leafRect.left - pondRect.left) + (leafRect.width / 2) - 41}}px`;
  pChar.style.top = `${{(leafRect.top - pondRect.top) + 14}}px`;
  setTimeout(() => {{
    if (isCorrect) {{
      dogruAtlayis++; score += 25; streak += 1;
      document.getElementById('scoreVal').textContent = score;
      document.getElementById('streakBadge').textContent = `🔥 Seri: ${{streak}}`;
      document.getElementById('feedbackMsg').innerHTML = `🎉 <b>Harika!</b> Doğru yaprağa kondu!`;
      setTimeout(() => {{ currentQIndex++; if (currentQIndex >= questionsBank.length) {{ document.getElementById('modalTitle').textContent = "Tebrikler!"; document.getElementById('modalDesc').textContent = "Skorun: " + score; document.getElementById('gameModal').style.display = 'flex'; }} else loadQuestion(); }}, 900);
    }} else {{
      yanlisAtlayis++; streak = 0; lives -= 1; pChar.style.opacity = "0";
      document.getElementById('streakBadge').textContent = `🔥 Seri: 0`;
      document.getElementById('feedbackMsg').innerHTML = `💦 <b>CUMBURLOP!</b> Yanlış yaprak!`;
      let hearts = ''; for (let i = 0; i < 3; i++) hearts += (i < lives) ? '<span>❤️</span>' : '<span style="opacity:0.3">🖤</span>';
      document.getElementById('livesContainer').innerHTML = hearts;
      if (lives <= 0) setTimeout(() => {{ document.getElementById('modalTitle').textContent = "Canlar Bitti!"; document.getElementById('modalDesc').textContent = "Skorun: " + score; document.getElementById('gameModal').style.display = 'flex'; }}, 750);
      else setTimeout(() => {{ resetPlayerPosition(); isJumping = false; }}, 850);
    }}
  }}, 600);
}}
function restartGame() {{ document.getElementById('gameModal').style.display = 'none'; score = 0; lives = 3; streak = 0; currentQIndex = 0; document.getElementById('scoreVal').textContent = "0"; document.getElementById('livesContainer').innerHTML = '<span>❤️</span><span>❤️</span><span>❤️</span>'; loadQuestion(); }}
window.onload = () => {{ selectCharacter('frog'); loadQuestion(); }};
</script>
</body>
</html>
"""
    components.html(html_code, height=580, scrolling=False)