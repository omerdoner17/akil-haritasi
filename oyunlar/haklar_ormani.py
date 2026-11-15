import streamlit as st
import streamlit.components.v1 as components
import os
import json
from urllib.parse import quote

def haklar_ormani_oyunu_render(ogretmen_adi, sube_adi, ogrenciler):
    html_yolu = os.path.join(os.path.dirname(__file__), "haklar_ormani.html")
    if not os.path.exists(html_yolu):
        st.error("⚠️ Lütfen 'haklar_ormani.html' dosyasını 'oyunlar' klasörünün içine kaydedin!")
        return

    with open(html_yolu, "r", encoding="utf-8") as f:
        html_icerik = f.read()

    ogrenci_listesi_js = ogrenciler if ogrenciler else [{"ad": "Örnek Öğrenci", "maskot": "🦁"}]
    ogrenciler_json = json.dumps(ogrenci_listesi_js, ensure_ascii=False)
    ogretmen_enc = quote(str(ogretmen_adi))
    sube_enc = quote(str(sube_adi))

    # Mevcut HTML'nin içine öğrenci çarkı ve süreç karnesi kayıt çubuğunu enjekte et
    ust_cubuk_html = f"""
    <div id="akilHaritasiBar" style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;background:#ffffff;border-bottom:2px solid #cbd5e1;padding:6px 14px;font-family:'Segoe UI',sans-serif;z-index:9999;position:relative;">
        <div style="display:flex;align-items:center;gap:8px;font-weight:800;font-size:14px;color:#0284c7;">
            <span>🎯 Tahtadaki Öğrenci:</span>
            <select id="ogrSelect" style="font:inherit;font-weight:700;padding:4px 10px;border-radius:8px;border:2px solid #0284c7;background:#f0f9ff;color:#0f172a;cursor:pointer;"></select>
            <button id="btnRandom" style="background:#f59e0b;color:#fff;border:none;padding:5px 11px;border-radius:8px;font-weight:800;cursor:pointer;">🎲 Çark</button>
        </div>
        <div style="display:flex;align-items:center;gap:8px;">
            <span id="saveToast" style="font-size:13px;font-weight:700;color:#059669;display:none;">✅ Süreç Karnesine Kaydedildi!</span>
            <button id="btnSaveResult" style="background:#10b981;color:#fff;border:none;padding:6px 13px;border-radius:8px;font-weight:800;cursor:pointer;">💾 Sürece Kaydet</button>
            <button onclick="if(!document.fullscreenElement)document.documentElement.requestFullscreen().catch(()=>{{}});else document.exitFullscreen();" style="background:#475569;color:#fff;border:none;padding:6px 10px;border-radius:8px;font-weight:700;cursor:pointer;">⛶ Tam Ekran</button>
        </div>
    </div>
    <script>
        var OGRENCILER = {ogrenciler_json};
        var OGRETMEN_ENC = "{ogretmen_enc}";
        var SUBE_ENC = "{sube_enc}";
        var sel = document.getElementById("ogrSelect");
        OGRENCILER.forEach(function(o) {{
            var opt = document.createElement("option");
            opt.value = o.ad;
            opt.textContent = (o.maskot || "🦁") + " " + o.ad;
            sel.appendChild(opt);
        }});
        document.getElementById("btnRandom").onclick = function() {{
            if (OGRENCILER.length > 1) {{
                var sayac = 0;
                var iv = setInterval(function() {{
                    sel.selectedIndex = Math.floor(Math.random() * OGRENCILER.length);
                    if (++sayac > 12) clearInterval(iv);
                }}, 60);
            }}
        }};
        document.getElementById("btnSaveResult").onclick = function() {{
            var ogrAd = sel.value;
            var durakNo = (typeof currentStationIndex !== 'undefined') ? (currentStationIndex + 1) : 1;
            var yildiz = (typeof stars !== 'undefined') ? stars : 0;
            var puan = (typeof score !== 'undefined') ? score : 0;
            var durum = yildiz >= 4 ? "İleri Düzey" : (yildiz >= 2 ? "Yetkin Düzey" : "Gelişmekte Olan");
            var guclu = "Haklar Ormanı yolculuğunda " + durakNo + ". durağa ulaştı ve " + yildiz + " yıldız (" + puan + " puan) topladı.";
            var url = "http://127.0.0.1:8765/cark_kaydet?ogr=" + encodeURIComponent(ogrAd) +
                      "&durum=" + encodeURIComponent(durum) +
                      "&gorev=" + encodeURIComponent("Haklar Ormanı (" + durakNo + "/15 Durak)") +
                      "&model=" + encodeURIComponent("Haklar Ormanı Çocuk Hakları Oyunu") +
                      "&guclu=" + encodeURIComponent(guclu) +
                      "&yanilgi=" + encodeURIComponent("Belirgin bir kavram yanılgısı tespit edilmedi.") +
                      "&oneri=" + encodeURIComponent("Günlük yaşam durumları ile temel çocuk haklarını eşleştirme çalışmaları sürdürülebilir.") +
                      "&ogretmen=" + OGRETMEN_ENC + "&sube=" + SUBE_ENC;
            new Image().src = url;
            var toast = document.getElementById("saveToast");
            toast.style.display = "inline";
            setTimeout(function() {{ toast.style.display = "none"; }}, 3000);
        }};
    </script>
    """

    # Harita yüksekliğini üst çubuğa göre ayarla ve üst çubuğu <body> etiketinin hemen altına yerleştir
    html_icerik = html_icerik.replace("height: calc(100vh - 80px);", "height: calc(100vh - 125px);")
    html_icerik = html_icerik.replace("min-height: 600px;", "min-height: 450px;")
    html_icerik = re.sub(r'(<body[^>]*>)', r'\1' + ust_cubuk_html, html_icerik, count=1) if 'import re' in globals() else html_icerik.replace('<body class="min-h-screen flex flex-col justify-between text-slate-800">', '<body class="min-h-screen flex flex-col justify-between text-slate-800">' + ust_cubuk_html)

    components.html(html_icerik, height=620, scrolling=False)