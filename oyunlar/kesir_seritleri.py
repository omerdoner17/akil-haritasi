import streamlit as st
import streamlit.components.v1 as components
import json
from urllib.parse import quote

def kesir_seritleri_oyunu_render(ogretmen_adi, sube_adi, ogrenciler):
    ogrenci_listesi_js = ogrenciler if ogrenciler else [{"ad": "Örnek Öğrenci", "maskot": "🦁"}]
    ogrenciler_json = json.dumps(ogrenci_listesi_js, ensure_ascii=False)

    html_code = f"""
<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>İnteraktif Kesir Şeritleri</title>
<style>
  :root {{ --c-1:#EF4444; --c-2:#F97316; --c-3:#EC4899; --c-4:#10B981; --c-5:#06B6D4; --c-6:#3B82F6; --c-8:#8B5CF6; }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', sans-serif; }}
  html, body {{ width: 100%; height: 100%; overflow: hidden; background: #f8fafc; color: #1E293B; user-select: none; }}
  #fitRoot {{ width: 100%; transform-origin: top center; padding: 6px; display: flex; flex-direction: column; align-items: center; }}
  .top-bar{{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;background:#fff;border:2px solid #cbd5e1;border-radius:14px;padding:6px 14px;width:100%;max-width:1000px;margin-bottom:6px}}
  .student-box{{display:flex;align-items:center;gap:8px;font-weight:800;font-size:.95rem;color:#0284c7}}
  select.ogr-sel{{font:inherit;font-weight:700;padding:4px 10px;border-radius:8px;border:2px solid #0284c7;background:#f0f9ff;color:#0f172a;cursor:pointer}}
  .btn-spin{{background:#f59e0b;color:#fff;border:none;padding:6px 12px;border-radius:8px;font-weight:800;cursor:pointer}}
  .btn-save{{background:#10b981;color:#fff;border:none;padding:6px 14px;border-radius:8px;font-weight:800;cursor:pointer}}
  .btn-fs{{background:#475569;color:#fff;border:none;padding:6px 10px;border-radius:8px;font-weight:700;cursor:pointer}}
  .save-toast{{font-size:0.82rem;font-weight:700;color:#059669;display:none}}

  .mode-tabs {{ display: flex; background: #FFF; padding: 3px; border-radius: 12px; border: 2px solid #E2E8F0; gap: 4px; margin-bottom: 6px; }}
  .tab-btn {{ border: none; background: transparent; padding: 5px 12px; border-radius: 8px; font-size: 12.5px; font-weight: 800; color: #64748B; cursor: pointer; }}
  .tab-btn.active {{ background: #2563EB; color: white; }}
  .main-wrapper {{ display: flex; flex-direction: column; width: 100%; max-width: 1000px; gap: 8px; }}
  .workspace-card, .palette-card {{ background: #FFF; border-radius: 14px; padding: 10px 14px; border: 2px solid #E2E8F0; }}
  .workspace-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }}
  .btn-tool {{ background: #F1F5F9; border: 1px solid #CBD5E1; color: #334155; padding: 4px 9px; border-radius: 7px; font-size: 11.5px; font-weight: 700; cursor: pointer; }}
  .whole-reference-bar {{ width: 100%; height: 32px; background: var(--c-1); color: white; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 14px; font-weight: 900; margin-bottom: 6px; }}
  .strip-drop-rows {{ display: flex; flex-direction: column; gap: 6px; min-height: 85px; }}
  .strip-row {{ width: 100%; height: 36px; background: #F8FAFC; border: 2px dashed #CBD5E1; border-radius: 10px; display: flex; align-items: center; padding: 2px; position: relative; overflow: hidden; }}
  .strip-row.highlight {{ background: #EFF6FF; border-color: #3B82F6; }}
  .strip-row.overflow {{ border-color: #EF4444; background: #FEF2F2; }}
  .strip-row.completed-whole {{ border-color: #10B981; background: #ECFDF5; }}
  .row-label {{ position: absolute; left: 10px; font-size: 11px; color: #94A3B8; font-weight: 700; pointer-events: none; }}
  .placed-strip-piece {{ height: 100%; border-radius: 6px; display: flex; align-items: center; justify-content: center; color: white; font-weight: 900; font-size: 12px; cursor: pointer; border: 1.5px solid rgba(255,255,255,0.4); flex-shrink: 0; }}
  .total-indicator-bar {{ display: flex; justify-content: space-between; align-items: center; margin-top: 6px; padding: 5px 10px; background: #F1F5F9; border-radius: 8px; font-size: 12px; font-weight: 800; }}
  .palette-grid {{ display: flex; flex-direction: column; gap: 4px; }}
  .palette-row {{ display: flex; gap: 4px; align-items: center; }}
  .palette-name {{ width: 68px; font-size: 11px; font-weight: 800; color: #64748B; text-align: right; padding-right: 5px; }}
  .strip-button {{ height: 28px; border-radius: 6px; color: white; font-weight: 900; font-size: 11.5px; display: flex; align-items: center; justify-content: center; cursor: pointer; border: 1px solid rgba(255,255,255,0.4); }}
  .bg-2 {{ background: var(--c-2); }} .bg-3 {{ background: var(--c-3); }} .bg-4 {{ background: var(--c-4); }} .bg-5 {{ background: var(--c-5); }} .bg-6 {{ background: var(--c-6); }} .bg-8 {{ background: var(--c-8); }}
  .challenge-box {{ background: linear-gradient(135deg, #1E3A8A 0%, #0F172A 100%); color: white; border-radius: 12px; padding: 8px 14px; display: none; justify-content: space-between; align-items: center; }}
  .compare-guide {{ display: none; background: #EFF6FF; border: 1.5px solid #BFDBFE; padding: 6px 10px; border-radius: 8px; font-size: 12px; color: #1E40AF; }}
  .celebration-overlay {{ position: fixed; inset: 0; background: rgba(15, 23, 42, 0.7); display: none; align-items: center; justify-content: center; z-index: 999; }}
  .celebration-modal {{ background: #FFF; border-radius: 18px; padding: 20px; text-align: center; max-width: 340px; }}
  .btn-next-level {{ background: #10B981; color: white; border: none; padding: 8px 18px; border-radius: 10px; font-weight: 800; cursor: pointer; margin-top: 10px; }}
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
<div class="mode-tabs">
  <button class="tab-btn active" id="tabFree" onclick="switchMode('free')">🔬 Serbest Keşif</button>
  <button class="tab-btn" id="tabChallenge" onclick="switchMode('challenge')">🏆 1 Bütünü Tamamla!</button>
  <button class="tab-btn" id="tabCompare" onclick="switchMode('compare')">⚖️ Karşılaştırma</button>
</div>
<div class="main-wrapper">
  <div class="challenge-box" id="challengeBox">
    <div><h4 id="chTitle" style="color:#FBBF24;font-size:14px">🎯 Görev 1</h4><p id="chDesc" style="font-size:12px"></p></div>
    <div style="text-align:center"><div id="scoreVal" style="font-size:18px;font-weight:900;color:#38BDF8">0</div><div style="font-size:9px">PUAN</div></div>
  </div>
  <div class="compare-guide" id="compareGuide">💡 <b>Pedagojik İpucu:</b> 1/2, 1/4 ve 1/8 şeritlerini alt alta koyarak payda büyüdükçe parçanın küçüldüğünü gözlemleyin.</div>
  <div class="workspace-card">
    <div class="workspace-header">
      <div style="font-weight:800;font-size:13.5px">Çalışma Masası <small style="color:#64748B">(Parçaya tıklayarak çıkarabilirsiniz)</small></div>
      <div style="display:flex;gap:5px"><button class="btn-tool" onclick="addNewRow()">➕ Satır</button><button class="btn-tool" onclick="clearActiveRow()">🗑️ Temizle</button><button class="btn-tool" onclick="resetAll()">🔄 Sıfırla</button></div>
    </div>
    <div class="whole-reference-bar">1 TAM (1 BÜTÜN)</div>
    <div class="strip-drop-rows" id="dropRowsContainer"></div>
    <div class="total-indicator-bar">
      <div>Aktif Satır Toplamı: <span style="color:#2563EB" id="activeTotalText">0.00 / 1 Tam</span></div>
      <div id="statusBadge">Satır Boş</div>
    </div>
  </div>
  <div class="palette-card">
    <div class="palette-grid">
      <div class="palette-row"><span class="palette-name">Yarım (1/2)</span><button class="strip-button bg-2" style="width:50%" onclick="addFraction(1,2,'bg-2')">1/2</button><button class="strip-button bg-2" style="width:50%" onclick="addFraction(1,2,'bg-2')">1/2</button></div>
      <div class="palette-row"><span class="palette-name">Üçte Bir</span><button class="strip-button bg-3" style="width:33.33%" onclick="addFraction(1,3,'bg-3')">1/3</button><button class="strip-button bg-3" style="width:33.33%" onclick="addFraction(1,3,'bg-3')">1/3</button><button class="strip-button bg-3" style="width:33.33%" onclick="addFraction(1,3,'bg-3')">1/3</button></div>
      <div class="palette-row"><span class="palette-name">Çeyrek (1/4)</span><button class="strip-button bg-4" style="width:25%" onclick="addFraction(1,4,'bg-4')">1/4</button><button class="strip-button bg-4" style="width:25%" onclick="addFraction(1,4,'bg-4')">1/4</button><button class="strip-button bg-4" style="width:25%" onclick="addFraction(1,4,'bg-4')">1/4</button><button class="strip-button bg-4" style="width:25%" onclick="addFraction(1,4,'bg-4')">1/4</button></div>
      <div class="palette-row"><span class="palette-name">Beşte Bir</span><button class="strip-button bg-5" style="width:20%" onclick="addFraction(1,5,'bg-5')">1/5</button><button class="strip-button bg-5" style="width:20%" onclick="addFraction(1,5,'bg-5')">1/5</button><button class="strip-button bg-5" style="width:20%" onclick="addFraction(1,5,'bg-5')">1/5</button><button class="strip-button bg-5" style="width:20%" onclick="addFraction(1,5,'bg-5')">1/5</button><button class="strip-button bg-5" style="width:20%" onclick="addFraction(1,5,'bg-5')">1/5</button></div>
      <div class="palette-row"><span class="palette-name">Altıda Bir</span><button class="strip-button bg-6" style="width:16.66%" onclick="addFraction(1,6,'bg-6')">1/6</button><button class="strip-button bg-6" style="width:16.66%" onclick="addFraction(1,6,'bg-6')">1/6</button><button class="strip-button bg-6" style="width:16.66%" onclick="addFraction(1,6,'bg-6')">1/6</button><button class="strip-button bg-6" style="width:16.66%" onclick="addFraction(1,6,'bg-6')">1/6</button><button class="strip-button bg-6" style="width:16.66%" onclick="addFraction(1,6,'bg-6')">1/6</button><button class="strip-button bg-6" style="width:16.66%" onclick="addFraction(1,6,'bg-6')">1/6</button></div>
      <div class="palette-row"><span class="palette-name">Sekizde Bir</span><button class="strip-button bg-8" style="width:12.5%" onclick="addFraction(1,8,'bg-8')">1/8</button><button class="strip-button bg-8" style="width:12.5%" onclick="addFraction(1,8,'bg-8')">1/8</button><button class="strip-button bg-8" style="width:12.5%" onclick="addFraction(1,8,'bg-8')">1/8</button><button class="strip-button bg-8" style="width:12.5%" onclick="addFraction(1,8,'bg-8')">1/8</button><button class="strip-button bg-8" style="width:12.5%" onclick="addFraction(1,8,'bg-8')">1/8</button><button class="strip-button bg-8" style="width:12.5%" onclick="addFraction(1,8,'bg-8')">1/8</button><button class="strip-button bg-8" style="width:12.5%" onclick="addFraction(1,8,'bg-8')">1/8</button><button class="strip-button bg-8" style="width:12.5%" onclick="addFraction(1,8,'bg-8')">1/8</button></div>
    </div>
  </div>
</div>
</div>
<div class="celebration-overlay" id="celebModal"><div class="celebration-modal"><h3>🎉 Tam 1 Bütün!</h3><p id="celebText"></p><button class="btn-next-level" onclick="nextChallenge()">Sıradaki Görev ➡️</button></div></div>
<script>
function autoFit(){{
  var r=document.getElementById('fitRoot'); r.style.transform='none';
  var h=r.scrollHeight, wh=window.innerHeight;
  if(h>wh && wh>100){{ var sc=(wh-8)/h; r.style.transform='scale('+sc+')'; }}
}}
window.addEventListener('resize',autoFit);
function toggleFS(){{if(!document.fullscreenElement)document.documentElement.requestFullscreen().catch(()=>{{}});else document.exitFullscreen();}}

var OGRENCILER = {ogrenciler_json};
var tamamlananButunSayisi = 0;
var sel = document.getElementById("ogrSelect");
OGRENCILER.forEach(function(o) {{ var opt = document.createElement("option"); opt.value = o.ad; opt.textContent = (o.maskot || "🦁") + " " + o.ad; sel.appendChild(opt); }});
document.getElementById("btnRandom").onclick = function() {{
    if (OGRENCILER.length > 1) {{ var sayac = 0; var iv = setInterval(function() {{ sel.selectedIndex = Math.floor(Math.random() * OGRENCILER.length); if (++sayac > 12) clearInterval(iv); }}, 60); }}
    tamamlananButunSayisi = 0; resetAll();
}};
document.getElementById("btnSaveResult").onclick = function() {{
    var ogrAd = sel.value, durum = tamamlananButunSayisi >= 2 ? "İleri Düzey" : (tamamlananButunSayisi === 1 ? "Yetkin Düzey" : "Gelişmekte Olan");
    var guclu = "Birim kesir şeritlerini birleştirerek parça-bütün ilişkisini ve denk kesirleri modelledi (" + tamamlananButunSayisi + " bütün tamamlandı).";

    var params = new URLSearchParams({{
        cark_kaydet: "1",
        ogr: ogrAd,
        durum: durum,
        gorev: "Kesir Şeritleri Laboratuvarı",
        model: "İnteraktif Kesir Şeritleri",
        guclu: guclu,
        yanilgi: "Belirgin bir kavram yanılgısı tespit edilmedi.",
        oneri: "Farklı paydalı birim kesirlerle 1 bütün oluşturma çalışmaları sürdürülebilir.",
        ogretmen: "{ogretmen_adi}",
        sube: "{sube_adi}",
        t: Date.now().toString()
    }});
    try {{
        var targetWin = window.parent || window;
        var baseUrl = targetWin.location.href.split("?")[0];
        targetWin.history.replaceState(null, "", baseUrl + "?" + params.toString());
        fetch(baseUrl + "?" + params.toString(), {{ mode: "no-cors", cache: "no-store" }}).catch(function() {{}});
    }} catch (e) {{}}

    var toast = document.getElementById("saveToast"); toast.style.display = "inline";
    setTimeout(function() {{
        toast.style.display = "none";
        try {{
            var targetWin = window.parent || window;
            targetWin.location.reload();
        }} catch (e) {{}}
    }}, 900);
}};
let currentMode = 'free', activeRowIndex = 0, rowsData = [ [] ], score = 0, currentChallengeLevel = 0;
const challengeLevels = [
  {{ title: "Görev 1: Yarımı Tamamla!", desc: "Satırda <b>1/2</b> var. Yanına hangi parçaları eklersen <b>tam 1 bütün</b> olur?", initial: [ {{num: 1, den: 2, colorClass: 'bg-2'}} ] }},
  {{ title: "Görev 2: Çeyrekleri Tamamla!", desc: "Satırda <b>1/4</b> var. 1 bütüne tamamlamak için kaç parça daha eklemelisin?", initial: [ {{num: 1, den: 4, colorClass: 'bg-4'}} ] }},
  {{ title: "Görev 3: Renkli Karışım!", desc: "Satırda <b>1/2 + 1/4</b> duruyor. Tam 1 bütün yapmak için son eksik parça nedir?", initial: [ {{num: 1, den: 2, colorClass: 'bg-2'}}, {{num: 1, den: 4, colorClass: 'bg-4'}} ] }},
  {{ title: "Görev 4: Sekizde Birlerin Gücü!", desc: "Satırda <b>1/2</b> var. Sadece <b>1/8 (mor)</b> parçalarıyla 1 bütünü tamamla!", initial: [ {{num: 1, den: 2, colorClass: 'bg-2'}} ] }}
];
function switchMode(mode) {{
  currentMode = mode;
  document.getElementById('tabFree').className = mode === 'free' ? 'tab-btn active' : 'tab-btn';
  document.getElementById('tabChallenge').className = mode === 'challenge' ? 'tab-btn active' : 'tab-btn';
  document.getElementById('tabCompare').className = mode === 'compare' ? 'tab-btn active' : 'tab-btn';
  document.getElementById('challengeBox').style.display = mode === 'challenge' ? 'flex' : 'none';
  document.getElementById('compareGuide').style.display = mode === 'compare' ? 'block' : 'none';
  if (mode === 'challenge') setupChallenge(0);
  else if (mode === 'compare') {{ rowsData = [ [{{num:1,den:2,colorClass:'bg-2'}}], [{{num:1,den:4,colorClass:'bg-4'}}], [{{num:1,den:8,colorClass:'bg-8'}}] ]; activeRowIndex = 0; renderRows(); }}
  else resetAll();
  setTimeout(autoFit, 50);
}}
function setupChallenge(lvlIdx) {{ currentChallengeLevel = lvlIdx % challengeLevels.length; const lvl = challengeLevels[currentChallengeLevel]; document.getElementById('chTitle').innerHTML = `🎯 ${{lvl.title}}`; document.getElementById('chDesc').innerHTML = lvl.desc; rowsData = [ JSON.parse(JSON.stringify(lvl.initial)) ]; activeRowIndex = 0; renderRows(); }}
function nextChallenge() {{ document.getElementById('celebModal').style.display = 'none'; setupChallenge(currentChallengeLevel + 1); }}
function addFraction(num, den, colorClass) {{ if (!rowsData[activeRowIndex]) rowsData[activeRowIndex] = []; rowsData[activeRowIndex].push({{ num, den, colorClass }}); renderRows(); checkRowTotal(activeRowIndex); }}
function removeFraction(rIdx, pIdx) {{ rowsData[rIdx].splice(pIdx, 1); renderRows(); checkRowTotal(rIdx); }}
function addNewRow() {{ if (rowsData.length < 4) {{ rowsData.push([]); activeRowIndex = rowsData.length - 1; renderRows(); setTimeout(autoFit, 40); }} }}
function clearActiveRow() {{ rowsData[activeRowIndex] = []; renderRows(); checkRowTotal(activeRowIndex); }}
function resetAll() {{ rowsData = [ [] ]; activeRowIndex = 0; renderRows(); checkRowTotal(0); setTimeout(autoFit, 40); }}
function renderRows() {{
  const container = document.getElementById('dropRowsContainer'); container.innerHTML = '';
  rowsData.forEach((row, rIdx) => {{
    const rowEl = document.createElement('div'); rowEl.className = 'strip-row' + (rIdx === activeRowIndex ? ' highlight' : '');
    rowEl.onclick = () => {{ activeRowIndex = rIdx; renderRows(); checkRowTotal(rIdx); }};
    if (row.length === 0) rowEl.innerHTML = `<div class="row-label">Satır ${{rIdx + 1}} (Paletten parça ekleyin)</div>`;
    row.forEach((p, pIdx) => {{
      const pEl = document.createElement('div'); pEl.className = `placed-strip-piece ${{p.colorClass}}`;
      pEl.style.width = `${{(p.num / p.den) * 100}}%`; pEl.textContent = `${{p.num}}/${{p.den}}`;
      pEl.onclick = (e) => {{ e.stopPropagation(); removeFraction(rIdx, pIdx); }};
      rowEl.appendChild(pEl);
    }});
    container.appendChild(rowEl);
  }});
}}
function checkRowTotal(rowIdx) {{
  const row = rowsData[rowIdx] || [], total = row.reduce((s, i) => s + (i.num / i.den), 0);
  const rowEl = document.querySelectorAll('.strip-row')[rowIdx];
  document.getElementById('activeTotalText').textContent = `${{total.toFixed(2)}} / 1 Tam`;
  const isWhole = Math.abs(total - 1.0) < 0.0001;
  if (rowEl) {{ rowEl.classList.remove('completed-whole', 'overflow'); if (isWhole) rowEl.classList.add('completed-whole'); else if (total > 1.0001) rowEl.classList.add('overflow'); }}
  if (isWhole) {{
    tamamlananButunSayisi++; document.getElementById('statusBadge').textContent = '⭐ TAM 1 BÜTÜN! ⭐';
    if (currentMode === 'challenge') {{ score += 100; document.getElementById('scoreVal').textContent = score; document.getElementById('celebText').innerHTML = 'Parçalar tam <b>1 Bütüne</b> eşit oldu!'; document.getElementById('celebModal').style.display = 'flex'; }}
  }} else if (total > 1.0001) document.getElementById('statusBadge').textContent = '⚠️ 1 Bütünü Aştı!';
  else document.getElementById('statusBadge').textContent = total === 0 ? 'Satır Boş' : '1 Bütünden Az';
}}
renderRows(); setTimeout(autoFit, 80);
</script>
</body>
</html>
"""
    components.html(html_code, height=580, scrolling=False)
