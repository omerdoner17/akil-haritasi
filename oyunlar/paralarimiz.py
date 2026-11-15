import streamlit as st
import json
import os
import streamlit.components.v1 as components

def paralarimiz_oyunu_render(aktif_ogretmen, aktif_sube, ogrenciler_listesi):
    if not ogrenciler_listesi:
        st.warning(f"⚠️ **{aktif_sube}** sınıfında henüz kayıtlı öğrenci yok! Lütfen sol menüden '🏫 Sınıf Öğrenci Listesi' sekmesine geçip öğrencilerinizi ekleyin.")
        return

    etiketler = [f"{o['maskot']} {o['ad']}" for o in ogrenciler_listesi]
    temiz_isimler = [o['ad'].strip() for o in ogrenciler_listesi]
    
    json_etiketler = json.dumps(etiketler, ensure_ascii=False)
    json_temiz_isimler = json.dumps(temiz_isimler, ensure_ascii=False)

    mevcut_dizin = os.path.dirname(os.path.abspath(__file__))
    olasi_yollar = [
        os.path.join(mevcut_dizin, "paralarimiz.html"),
        os.path.join(mevcut_dizin, "paralarimiz (1).html"),
        os.path.expanduser(r"~\Downloads\paralarimiz (1).html"),
        os.path.expanduser(r"~\Downloads\paralarimiz.html"),
        r"C:\Users\ATLM\Downloads\paralarimiz (1).html",
        r"C:\Users\ATLM\Downloads\paralarimiz.html"
    ]

    html_yolu = None
    for yol in olasi_yollar:
        if os.path.exists(yol):
            html_yolu = yol
            break

    if not html_yolu:
        st.error("❌ 'paralarimiz.html' dosyası bulunamadı!")
        return

    try:
        with open(html_yolu, "r", encoding="utf-8") as f:
            html_icerik = f.read()
    except Exception:
        with open(html_yolu, "r", encoding="cp1254", errors="ignore") as f:
            html_icerik = f.read()

    # Demir paraları ve alt kısmı yukarı çeken kompakt stil
    kompakt_stil = """
    <style>
      body { padding: 4px !important; }
      .container { gap: 6px !important; }
      .target-panel { padding: 8px 14px !important; border-radius: 12px !important; gap: 10px !important; }
      .target-preview img { height: 48px !important; }
      .layout { gap: 8px !important; }
      .panel { padding: 8px !important; border-radius: 10px !important; }
      .panel-header { margin-bottom: 4px !important; }
      .banknotes-grid { gap: 6px !important; }
      .coins-grid { gap: 5px !important; margin-top: 4px !important; }
      .source-card.note img { height: 46px !important; }
      .source-card.coin img { height: 40px !important; }
      .source-card b { margin-top: 2px !important; font-size: 11px !important; }
      .board-dropzone { min-height: 170px !important; max-height: 230px !important; padding: 6px !important; }
      .desk-card img { height: 32px !important; }
      .status-card { padding: 6px 12px !important; margin-bottom: 6px !important; }
      .status-total { font-size: 19px !important; }
      .history-card { margin-top: 6px !important; padding-top: 6px !important; }
      .history-list { max-height: 90px !important; }
    </style>
    """

    ust_bar = f"""
    <div style="background:#ffffff; border-radius:12px; padding:8px 16px; margin-bottom:6px; display:flex; justify-content:space-between; align-items:center; border:2px solid #cbd5e1; box-shadow:0 2px 6px rgba(0,0,0,0.03);">
        <div style="font-size:15px; font-weight:800; color:#0f172a;">🪙 Paralarımız — Değer Denkliği</div>
        <div style="display:flex; align-items:center; gap:10px;">
            <span id="activeStudentLabel" style="font-size:16px; font-weight:900; color:#0284c7; background:#e0f2fe; padding:4px 14px; border-radius:14px; border:1px solid #bae6fd;">⭐ Tahtada: {etiketler[0]}</span>
            <button id="btnNextStudent" style="background:#ef4444; color:#ffffff; border:none; border-radius:8px; padding:6px 12px; font-weight:800; cursor:pointer;">🎯 Sıradaki Öğrenci</button>
        </div>
    </div>
    """

    entegrasyon_kodu = f"""
    <script>
    (function() {{
        let allLabels = {json_etiketler};
        let allPureNames = {json_temiz_isimler};
        let curIdx = 0;

        let btnNext = document.getElementById('btnNextStudent');
        let lblStudent = document.getElementById('activeStudentLabel');
        if (btnNext && lblStudent) {{
            btnNext.onclick = function() {{
                curIdx = (curIdx + 1) % allLabels.length;
                lblStudent.textContent = "⭐ Tahtada: " + allLabels[curIdx];
                if (typeof clearDesk === 'function') clearDesk(false);
            }};
        }}

        let btnSave = document.getElementById('btnSaveCombo');
        if (btnSave) {{
            btnSave.addEventListener('click', function() {{
                setTimeout(function() {{
                    let ogr = allPureNames[curIdx];
                    let hedefPara = (typeof currentTarget !== 'undefined' && currentTarget) ? currentTarget.name : "Para";
                    let url = "http://127.0.0.1:8765/cark_kaydet?ogr=" + encodeURIComponent(ogr) +
                              "&durum=" + encodeURIComponent("Yetkin Düzey") +
                              "&gorev=" + encodeURIComponent(hedefPara + " Değer Denkliği") +
                              "&model=" + encodeURIComponent("Para Kasası Manipülatifi") +
                              "&yanilgi=" + encodeURIComponent("Yok (Hedef paranın değer denkliğini başarıyla modelledi)") +
                              "&oneri=" + encodeURIComponent("Kuruş ve Lira dönüşümlerinde somut modellerle problem çözme becerisi zenginleştirilebilir.") +
                              "&guclu=" + encodeURIComponent(hedefPara + " değerini oluşturan paraları başarıyla ayrıştırdı.") +
                              "&ogretmen=" + encodeURIComponent("{aktif_ogretmen}") +
                              "&sube=" + encodeURIComponent("{aktif_sube}") +
                              "&t=" + Date.now();
                    let ping = new Image();
                    ping.src = url;
                }}, 300);
            }});
        }}
    }})();
    </script>
    """

    if '</head>' in html_icerik:
        html_icerik = html_icerik.replace('</head>', kompakt_stil + '</head>')
    else:
        html_icerik = kompakt_stil + html_icerik

    if '<div class="container">' in html_icerik:
        html_icerik = html_icerik.replace('<div class="container">', '<div class="container">' + ust_bar, 1)
    else:
        html_icerik = html_icerik.replace('<body>', '<body>' + ust_bar, 1)

    html_icerik = html_icerik.replace('</body>', entegrasyon_kodu + '</body>')

    # Yüksekliği 1150 yaparak demir paraların ve alt butonların tam görünmesini sağlıyoruz
    components.html(html_icerik, height=1150, scrolling=True)