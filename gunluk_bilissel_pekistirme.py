# gunluk_bilissel_pekistirme.py
# Akıl Haritası — Tam Otomatik Bireysel Çalışma Kâğıdı Motoru (Genel Rehber Notlu & Bölünmez Sorulu)

import streamlit as st
import io
import re
import json
import math
import sqlite3
from datetime import datetime, timedelta
from google.genai import types
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Flowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# ----------------- METİN & TDK TEMİZLEYİCİ -----------------
def metin_temizle(metin):
    if not metin:
        return ""
    metin = str(metin)
    metin = re.sub(r'\$?\\frac\{(\d+)\}\{(\d+)\}\$?', r'\1/\2', metin)
    metin = metin.replace("$", "").replace("\\times", "x").replace("\\div", "÷")
    metin = re.sub(r'\[.*?\]', '', metin)
    metin = re.sub(r'[^\w\s.,;:!?()/\-\'\"’“”%+=<>@&*°çğıöşüÇĞİÖŞÜâîûÂÎÛ]', '', metin)
    metin = re.sub(r'\s{2,}', ' ', metin)
    return metin.strip()

# ----------------- VERİTABANI ARALIKLI TEKRAR & GÖREV TAKİP DÖNGÜSÜ -----------------
def dongu_db_init(db_path):
    conn = sqlite3.connect(db_path, timeout=30)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS bilissel_dongu (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gorev_kodu TEXT UNIQUE,
            ogretmen_adi TEXT,
            sinif TEXT,
            ogrenci_adi TEXT,
            kulvar TEXT,
            ders TEXT,
            konu_ozeti TEXT,
            hata_turu TEXT,
            tekrar_asamasi TEXT,
            durum TEXT,
            olusturma_tarihi DATE,
            sonraki_kontrol_tarihi DATE
        )
    """)
    conn.commit()
    conn.close()

def dongu_kaydet(db_path, gorev_kodu, ogretmen, sinif, ogrenci, kulvar, ders, konu_ozeti, hata_turu, tekrar_asamasi):
    dongu_db_init(db_path)
    conn = sqlite3.connect(db_path, timeout=30)
    c = conn.cursor()
    bugun = datetime.now().strftime("%Y-%m-%d")
    sonraki = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
    try:
        c.execute("""
            INSERT OR REPLACE INTO bilissel_dongu
            (gorev_kodu, ogretmen_adi, sinif, ogrenci_adi, kulvar, ders, konu_ozeti, hata_turu, tekrar_asamasi, durum, olusturma_tarihi, sonraki_kontrol_tarihi)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Aktif', ?, ?)
        """, (gorev_kodu, ogretmen, sinif, ogrenci, kulvar, ders, konu_ozeti, hata_turu, tekrar_asamasi, bugun, sonraki))
        conn.commit()
    except Exception:
        pass
    conn.close()

def ogrenci_dongu_gecmisi(db_path, ogretmen, sinif, ogrenci):
    dongu_db_init(db_path)
    conn = sqlite3.connect(db_path, timeout=30)
    c = conn.cursor()
    c.execute("""
        SELECT gorev_kodu, kulvar, ders, konu_ozeti, hata_turu, tekrar_asamasi, durum, olusturma_tarihi, sonraki_kontrol_tarihi
        FROM bilissel_dongu
        WHERE LOWER(TRIM(ogretmen_adi)) = LOWER(TRIM(?))
          AND LOWER(TRIM(sinif)) = LOWER(TRIM(?))
          AND LOWER(TRIM(ogrenci_adi)) = LOWER(TRIM(?))
        ORDER BY id DESC LIMIT 10
    """, (ogretmen, sinif, ogrenci))
    rows = c.fetchall()
    conn.close()
    return rows

def dongu_ustalik_guncelle(db_path, gorev_kodu):
    dongu_db_init(db_path)
    conn = sqlite3.connect(db_path, timeout=30)
    c = conn.cursor()
    c.execute("UPDATE bilissel_dongu SET durum = 'Ustalık Kazanıldı' WHERE UPPER(TRIM(gorev_kodu)) = UPPER(TRIM(?))", (gorev_kodu,))
    etkilenen = c.rowcount
    conn.commit()
    conn.close()
    return etkilenen > 0

# ----------------- REPORTLAB TÜRKÇE FONT DESTEKLİ ÇİZİM MOTORU -----------------
class EtkinlikCizimAlani(Flowable):
    def __init__(self, cizim_tipi="yok", parametre=4, font_normal="Helvetica", font_bold="Helvetica-Bold", width=490, height=62):
        super().__init__()
        self.cizim_tipi = str(cizim_tipi).lower()
        self.font_normal = font_normal
        self.font_bold = font_bold
        try:
            self.param = max(2, min(12, int(parametre)))
        except Exception:
            self.param = 4
        self.width = width
        self.height = height

    def draw(self):
        c = self.canv
        c.saveState()
        if "kesir_cubuk" in self.cizim_tipi:
            bar_w = 340
            bar_h = 25
            start_x = (self.width - bar_w) / 2
            start_y = 21
            parca_w = bar_w / self.param
            c.setStrokeColor(colors.HexColor("#1e3a8a"))
            c.setLineWidth(1.5)
            for i in range(self.param):
                c.rect(start_x + i * parca_w, start_y, parca_w, bar_h, stroke=1, fill=0)
            c.setFont(self.font_normal, 8.5)
            c.setFillColor(colors.HexColor("#334155"))
            c.drawCentredString(self.width / 2, 6, f"Yukarıdaki {self.param} eş parçalı kesir çubuğunu istenen miktara göre boyayınız.")

        elif "kesir_daire" in self.cizim_tipi:
            cx, cy, r = self.width / 2, 35, 22
            c.setStrokeColor(colors.HexColor("#0369a1"))
            c.setLineWidth(1.4)
            c.circle(cx, cy, r, stroke=1, fill=0)
            for i in range(self.param):
                aci = (2 * math.pi * i) / self.param
                c.line(cx, cy, cx + r * math.cos(aci), cy + r * math.sin(aci))
            c.setFont(self.font_normal, 8.5)
            c.setFillColor(colors.HexColor("#334155"))
            c.drawCentredString(self.width / 2, 3, f"{self.param} eş dilime ayrılmış bütün üzerinde istenen kesri boyayınız.")

        elif "saat" in self.cizim_tipi:
            for offset in [-95, 95]:
                cx, cy, r = (self.width / 2) + offset, 34, 23
                c.setStrokeColor(colors.HexColor("#0f172a"))
                c.setLineWidth(1.5)
                c.circle(cx, cy, r, stroke=1, fill=0)
                c.circle(cx, cy, 1.8, stroke=1, fill=1)
                c.setFont(self.font_bold, 6.5)
                for saat in range(1, 13):
                    ang = math.radians(90 - saat * 30)
                    tx = cx + (r - 6.5) * math.cos(ang)
                    ty = cy + (r - 6.5) * math.sin(ang) - 2
                    c.drawCentredString(tx, ty, str(saat))
            c.setFont(self.font_normal, 8.5)
            c.setFillColor(colors.HexColor("#334155"))
            c.drawCentredString(self.width / 2, 2, "Saat kadranları üzerine akrep (kısa) ve yelkovanı (uzun) çizerek gösteriniz.")

        elif "buyutec" in self.cizim_tipi:
            c.setStrokeColor(colors.HexColor("#d97706"))
            c.setDash(3, 3)
            c.roundRect(16, 6, self.width - 32, 46, 6, stroke=1, fill=0)
            c.setDash()
            c.setFont(self.font_bold, 8.5)
            c.setFillColor(colors.HexColor("#92400e"))
            c.drawString(26, 40, "Not ve Çizim Alanı:")
        c.restoreState()

# ----------------- ÖĞRENCİYE ÖZEL TEMİZ PDF MOTORU -----------------
def bilissel_calisma_kagidi_pdf(ogretmen_adi, sube_adi, ogrenci_adi, kulvar, gorev_kodu, tekrar_asamasi, icerik_json, font_normal="Helvetica", font_bold="Helvetica-Bold"):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=34, leftMargin=34, topMargin=98, bottomMargin=42)

    temiz_ogr = metin_temizle(ogrenci_adi).title()
    temiz_ogrt = metin_temizle(ogretmen_adi).title()
    zenginlestirme_mi = ("Zenginleştirme" in kulvar)

    ana_renk = colors.HexColor("#6d28d9") if zenginlestirme_mi else colors.HexColor("#0284c7")
    acik_bg = colors.HexColor("#f5f3ff") if zenginlestirme_mi else colors.HexColor("#eff6ff")
    baslik_metni = "BİREYSEL ZENGİNLEŞTİRME & DERİNLEŞTİRME ÇALIŞMA KÂĞIDI" if zenginlestirme_mi else "BİREYSEL DESTEKLEME & PEKİŞTİRME ÇALIŞMA KÂĞIDI"

    def sablon(canvas_obj, doc_obj):
        canvas_obj.saveState()
        canvas_obj.setStrokeColor(ana_renk)
        canvas_obj.setLineWidth(1.8)
        canvas_obj.roundRect(18, 18, 559, 806, 8, stroke=1, fill=0)

        canvas_obj.setFillColor(acik_bg)
        canvas_obj.roundRect(26, 760, 543, 54, 6, stroke=0, fill=1)

        canvas_obj.setFillColor(ana_renk)
        canvas_obj.setFont(font_bold, 13.5)
        canvas_obj.drawString(38, 795, baslik_metni)

        canvas_obj.setFont(font_normal, 9)
        canvas_obj.setFillColor(colors.HexColor("#1e293b"))
        canvas_obj.drawString(38, 779, f"Öğrenci Adı Soyadı: {temiz_ogr}     |     Sınıf: {sube_adi}     |     Tarih: {datetime.now().strftime('%d.%m.%Y')}")
        
        canvas_obj.setFont(font_bold, 8.2)
        canvas_obj.setFillColor(colors.HexColor("#475569"))
        canvas_obj.drawString(38, 765, f"Çalışma Aşaması: {metin_temizle(tekrar_asamasi)}")
        canvas_obj.drawRightString(556, 765, "Değerlendirme: [   ] Tamamlandı")

        canvas_obj.setFont(font_normal, 8)
        canvas_obj.setFillColor(colors.HexColor("#64748b"))
        canvas_obj.drawString(34, 28, f"Sınıf Öğretmeni: {temiz_ogrt}  |  Akıl Haritası Bireysel Öğrenme Kâğıdı")
        canvas_obj.drawRightString(558, 28, f"Sayfa {canvas_obj._pageNumber}")
        canvas_obj.restoreState()

    styles = getSampleStyleSheet()
    giris_baslik = ParagraphStyle('GBaslik', parent=styles['Heading4'], fontName=font_bold, textColor=colors.HexColor("#92400e") if not zenginlestirme_mi else colors.HexColor("#5b21b6"), fontSize=10, spaceAfter=2)
    giris_metin = ParagraphStyle('GMetin', parent=styles['Normal'], fontName=font_normal, textColor=colors.HexColor("#1e293b"), fontSize=9.3, leading=14)
    soru_baslik = ParagraphStyle('SBaslik', parent=styles['Normal'], fontName=font_bold, textColor=colors.HexColor("#0f172a"), fontSize=10, leading=13, spaceAfter=3)
    soru_metin = ParagraphStyle('SMetin', parent=styles['Normal'], fontName=font_normal, textColor=colors.HexColor("#1e293b"), fontSize=9.5, leading=14)

    hikaye = []

    giris_notu = metin_temizle(icerik_json.get("giris_notu", ""))
    if giris_notu:
        kutu_etiket = "Kâşif İpucu & Bilgi Notu" if zenginlestirme_mi else "Küçük Bir Hatırlatma"
        t_giris = Table([[Paragraph(kutu_etiket, giris_baslik)], [Paragraph(giris_notu, giris_metin)]], colWidths=[526], splitByRow=0)
        t_giris.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#ede9fe") if zenginlestirme_mi else colors.HexColor("#fef3c7")),
            ('BOX', (0, 0), (-1, -1), 1.2, ana_renk if zenginlestirme_mi else colors.HexColor("#f59e0b")),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        hikaye.append(t_giris)
        hikaye.append(Spacer(1, 10))

    sorular = icerik_json.get("sorular", [])
    for idx, s in enumerate(sorular, 1):
        s_metni = metin_temizle(s.get("soru_metni", ""))
        secenekler = [metin_temizle(sec) for sec in s.get("secenekler", [])]
        cizim_tipi = str(s.get("cizim_tipi", "yok"))
        cizim_param = s.get("cizim_param", 4)

        soru_blok = [
            [Paragraph(f"<b>Soru {idx}</b>", soru_baslik)],
            [Paragraph(s_metni, soru_metin)]
        ]

        if cizim_tipi not in ["yok", "", "None"]:
            soru_blok.append([EtkinlikCizimAlani(
                cizim_tipi=cizim_tipi,
                parametre=cizim_param,
                font_normal=font_normal,
                font_bold=font_bold,
                width=500,
                height=60
            )])

        if secenekler:
            sec_str = "      ".join(secenekler)
            soru_blok.append([Paragraph(f"<b>Seçenekler:</b>  {sec_str}", soru_metin)])
        else:
            soru_blok.append([Paragraph("<font color='#94a3b8'>Çözüm / Açıklama / Çizim Alanı:<br/><br/>..........................................................................................................................................<br/>..........................................................................................................................................</font>", soru_metin)])

        t_soru = Table(soru_blok, colWidths=[526], splitByRow=0)
        t_soru.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f8fafc")),
            ('BOX', (0, 0), (-1, -1), 0.8, colors.HexColor("#cbd5e1")),
            ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.HexColor("#e2e8f0")),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        hikaye.append(t_soru)
        hikaye.append(Spacer(1, 10))

    doc.build(hikaye, onFirstPage=sablon, onLaterPages=sablon)
    buffer.seek(0)
    return buffer

# ----------------- SINIF GENELİ "SABAH ISINMA BİLMECESİ" ÜRETİCİSİ -----------------
def sabah_isinma_bilmecesi_render(aktif_ogretmen, aktif_sube, df_sinif, yapay_zeka_cagri_fonksiyonu):
    if df_sinif.empty:
        return

    bugun_str = datetime.now().strftime("%Y-%m-%d")
    df_son = df_sinif[df_sinif["tarih"].astype(str).str.startswith(bugun_str)]
    if df_son.empty:
        df_son = df_sinif.head(15)

    hatali_df = df_son[
        ~df_son["kavram_yanilgisi"].astype(str).str.contains("Belirgin bir kavram yanılgısı tespit edilmedi", case=False, na=False)
    ]

    with st.expander("☀️ Akıllı Tahta İçin 'Sabah Isınma Bilmecesi & Ortak Yanılgı Özeti'", expanded=False):
        c_o1, c_o2 = st.columns([2, 1])
        with c_o1:
            if not hatali_df.empty:
                st.info(f"📊 Son kayıtlarda **{hatali_df['ogrenci_adi'].nunique()}** öğrencide pekiştirme gerektiren bulgular saptandı.")
            else:
                st.success("🌟 Sınıf genelinde belirgin bir kavram yanılgısı yok; üst düzey zenginleştirme bilmecesi hazırlanabilir!")
        with c_o2:
            if st.button("✨ Tahta İçin 3 Dakikalık Isınma Sorusu Üret", use_container_width=True, key="btn_sabah_bilmece"):
                with st.spinner("Sınıfın ortak düzeyine uygun akıllı tahta ısınma kartı hazırlanıyor..."):
                    ozet_veriler = [
                        f"Ders: {r['ders']} | Kazanım: {r['kazanim']} | Düzey: {r['rubrik_duzeyi']} | Bulgu: {r['kavram_yanilgisi']}"
                        for _, r in df_son.head(10).iterrows()
                    ]
                    prompt_bilmece = f"""
Sen ilkokul öğretmenisin. Sınıf: {aktif_sube}.
Sınıfın son etkinlik verileri:
{chr(10).join(ozet_veriler)}

Ertesi sabah dersin ilk 3 dakikasında akıllı tahtaya yansıtılacak, tüm sınıfın birlikte tartışıp çözebileceği eğlenceli, 1 soruluk "Günün Isınma Bilmecesi" hazırla.
Kesinlikle LaTeX kullanma (kesirleri 1/2 gibi yaz) ve TDK Yazım Kılavuzu kurallarına eksiksiz uy.
Sadece geçerli JSON döndür:
{{
  "baslik": "Kısa dikkat çekici başlık",
  "bilmece_metni": "Tahtada büyük puntoda okunacak eğlenceli soru/senaryo",
  "ipucu": "Öğretmenin öğrencilere vereceği minik ipucu",
  "cevap_ve_tartisma": "Doğru cevap ve sınıf içi tartışma sorusu"
}}
"""
                    try:
                        res = yapay_zeka_cagri_fonksiyonu(
                            model_adi='gemini-3.5-flash-lite',
                            contents=[prompt_bilmece],
                            config=types.GenerateContentConfig(
                                response_mime_type="application/json",
                                thinking_config=types.ThinkingConfig(thinking_level="LOW")
                            )
                        )
                        temiz = res.text.replace("```json", "").replace("```", "").strip()
                        st.session_state["sabah_bilmece_data"] = json.loads(temiz)
                    except Exception as e:
                        st.error(f"Hata: {str(e)}")

        if "sabah_bilmece_data" in st.session_state:
            b = st.session_state["sabah_bilmece_data"]
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #fefce8, #fef3c7); border: 2px solid #f59e0b; border-radius: 14px; padding: 16px; margin-top: 8px;">
                <h4 style="margin:0 0 6px 0; color:#92400e;">☀️ {metin_temizle(b.get('baslik', ''))}</h4>
                <p style="font-size:16px; font-weight:700; color:#0f172a; margin:0 0 8px 0;">{metin_temizle(b.get('bilmece_metni', ''))}</p>
                <div style="font-size:13px; color:#78350f;"><b>💡 İpucu:</b> {metin_temizle(b.get('ipucu', ''))}</div>
            </div>
            """, unsafe_allow_html=True)
            with st.expander("🔑 Cevabı ve Tartışma Sorusunu Göster"):
                st.write(metin_temizle(b.get("cevap_ve_tartisma", "")))

# ----------------- ANA BİREYSEL OTOMATİK ÇALIŞMA KÂĞIDI ARAYÜZÜ -----------------
def cift_kulvar_calisma_studyo_render(db_path, aktif_ogretmen, aktif_sube, secilen_ogrenci, maskot, df_tum, yapay_zeka_cagri_fonksiyonu, font_normal, font_bold):
    dongu_db_init(db_path)
    temiz_ogr = metin_temizle(secilen_ogrenci).title()
    temiz_ogrt = metin_temizle(aktif_ogretmen).title()

    bugun_str = datetime.now().strftime("%Y-%m-%d")
    df_bugun = df_tum[df_tum["tarih"].astype(str).str.startswith(bugun_str)]
    analiz_df = df_bugun if not df_bugun.empty else df_tum.head(6)

    hatali_df = analiz_df[
        ~analiz_df["kavram_yanilgisi"].astype(str).str.contains("Belirgin bir kavram yanılgısı tespit edilmedi", case=False, na=False)
    ]
    baslangic_gelismekte_df = analiz_df[
        analiz_df["rubrik_duzeyi"].astype(str).str.contains("Başlangıç|Gelişmekte", case=False, na=False)
    ]

    if not hatali_df.empty or not baslangic_gelismekte_df.empty:
        otomatik_kulvar = "Destekleme"
        durum_ozeti = f"Sistem değerlendirmesi: **{temiz_ogr}** için pekiştirme gerektiren bulgular saptandı; **Destekleme & Pekiştirme** çalışma kâğıdı otomatik hazırlanacak."
    else:
        otomatik_kulvar = "Zenginleştirme"
        durum_ozeti = f"Sistem değerlendirmesi: **{temiz_ogr}** tüm etkinliklerde Yetkin/İleri düzey performans gösterdi; **Zenginleştirme & Derinleştirme** çalışma kâğıdı otomatik hazırlanacak."

    gecmis_donguler = ogrenci_dongu_gecmisi(db_path, aktif_ogretmen, aktif_sube, secilen_ogrenci)
    aktif_tekrar = None
    for gd in gecmis_donguler:
        if gd[6] == "Aktif":
            aktif_tekrar = gd
            break

    otomatik_asama = "3. Gün - Aralıklı Kontrol" if aktif_tekrar else "1. Gün - İlk Hatırlatma ve Pekiştirme"

    with st.container(border=True):
        st.markdown("### 🧠 Akıllı Bireysel Çalışma Kâğıdı Üreticisi")
        st.info(durum_ozeti)

        if aktif_tekrar:
            st.warning(f"🔁 **Aralıklı Tekrar Takibi:** (**{aktif_tekrar[2]} — {aktif_tekrar[3]}**) aktif takip döngüsü otomatik algılandı ve son soruya kontrol sorusu eklendi.")

        # Prompt içinde öğrencinin ismi ve "geçen derste hata yaptı" ifadesi ASLA geçmemesi için sadece konu ve odak noktası çıkarılır
        odak_konular = []
        odak_df = hatali_df if (otomatik_kulvar == "Destekleme" and not hatali_df.empty) else analiz_df.head(5)
        for _, r in odak_df.iterrows():
            odak_konular.append(
                f"Ders: {r['ders']} | Kazanım: {r['kazanim']} | Odaklanılacak Kavram/Beceri: {r['kavram_yanilgisi']}"
            )

        if st.button(f"✨ {temiz_ogr} İçin Kişiselleştirilmiş Çalışma Kâğıdını Hazırla", type="primary", use_container_width=True, key=f"btn_oto_kagit_{secilen_ogrenci}"):
            with st.spinner("Öğrencinin verileri analiz ediliyor ve TDK kurallarına %100 uygun çalışma kâğıdı hazırlanıyor..."):
                zengin_mi = (otomatik_kulvar == "Zenginleştirme")
                eski_tekrar_notu = f"6. soruda şu konuyu da pekiştir: {aktif_tekrar[2]} - {aktif_tekrar[3]}." if aktif_tekrar else ""

                if zengin_mi:
                    kulvar_talimati = """
MOD: ZENGİNLEŞTİRME & DERİNLEŞTİRME (Üst Düzey Düşünme Etkinlikleri).
Basit alıştırma SORMA! Problem kurma, görsel ispat, mantık bilmecesi, hayali bir karakterin çözümündeki gizli hatayı yakalama ve gerçek yaşam tasarımı soruları hazırla.
"""
                else:
                    kulvar_talimati = """
MOD: DESTEKLEME & PEKİŞTİRME (Somutlaştırma ve Kavram Öğretimi).
- Soru 1: Hayali bir arkadaşının çözümündeki hatayı bulup ona doğrusunu öğreteceği soru (Soru metninin içinde asla köşeli parantez '[...]' veya 'Hata Yaptı' gibi etiketler YAZMA!).
- Soru 2: Kesir çubuğu boyama, kesir dairesi boyama veya boş analog saate akrep-yelkovan çizme etkinliği.
- Soru 3: Anahtar kelimeleri vurgulayan dikkat ve yönerge kontrolü sorusu.
- Soru 4: Günlük yaşamdan (oyun, okul, paylaşım) kurgulanmış somut problem.
- Soru 5 ve 6: Çoktan seçmeli pekiştirme soruları.
"""

                prompt_ana = f"""
Sen Türkiye Yüzyılı Maarif Modeli (TYMM) uzmanısın ve Türkçeyi TDK Yazım Kılavuzu kurallarına %100 uygun kullanan bir ilkokul öğretmenisin.
Sınıf Düzeyi: {aktif_sube}
{kulvar_talimati}
{eski_tekrar_notu}

Çalışma Kâğıdının Odaklanacağı Ders ve Kavramlar:
{chr(10).join(odak_konular)}

KESİN KURALLAR (ASLA İHLAL ETME):
1. "giris_notu" ALANI KURALI: Bu kutuda KESİNLİKLE hiçbir öğrenci ismi (Mehmet, Ayşe vb.) kullanma ve "geçen derste hata yapmıştın, eksik boyamıştın" gibi geçmiş hataları hatırlatan HİÇBİR cümle kurma! Sadece konunun kuralını ve püf noktasını somut bir örnekle anlatan, herkes için geçerli 2 cümlelik genel bir konu özeti yaz. (Örnek: "Bir kesri modellerken payda bütünün kaç eş parçaya bölündüğünü, pay ise bu eş parçalardan kaç tanesinin boyanacağını gösterir. Örneğin 3/5 kesrini göstermek için 5 eş parçadan 3 tanesini boyarız.")
2. TDK YAZIM KURALLARI: Tüm kelimeleri TDK Yazım Kılavuzu'na göre doğru yaz. Noktalama işaretlerini doğru kullan.
3. KÖŞELİ PARANTEZ YASAĞI: Soru metinlerinin başına "[Hata Yaptı]", "[Görsel Modelleme]" gibi köşeli parantezli etiketler YAZMA.
4. EMOJİ VE LATEX YASAĞI: Hiçbir metinde emoji veya LaTeX ($\\frac{{1}}{{2}}$) kullanma; kesirleri "1/2", "3/5" şeklinde düz yaz.
5. Tam olarak 6 adet soru üret.
6. Uygun sorularda "cizim_tipi" alanını kullanarak PDF'e vektörel şekil çizdir:
   - Kesir çubuğu gerekiyorsa: "kesir_cubuk" (ve "cizim_param" olarak payda sayısını örn: 5 yaz)
   - Kesir dairesi/pizzası gerekiyorsa: "kesir_daire" (ve "cizim_param" olarak dilim sayısını örn: 4 yaz)
   - Saat sorusuysa: "saat"
   - Not / çizim kutusu gerekiyorsa: "buyutec"
   - Ek çizim gerekmiyorsa: "yok"

Sadece geçerli bir JSON nesnesi döndür:
{{
  "hata_veya_duzey_turu": "Kavram Pekiştirme | Dikkat Becerisi | Problem Çözme | Üst Düzey Transfer",
  "odak_ders": "Matematik / Türkçe / Hayat Bilgisi vb.",
  "odak_konu_ozeti": "3-5 kelimelik kısa konu başlığı",
  "giris_notu": "Öğrenci ismi ve geçmiş hata geçmeyen, sadece konunun doğru kuralını somut bir örnekle açıklayan 2 cümlelik genel hatırlatma notu.",
  "sorular": [
    {{
      "soru_metni": "Etiketsiz, net ve TDK kurallarına tam uygun soru metni",
      "cizim_tipi": "kesir_cubuk | kesir_daire | saat | buyutec | yok",
      "cizim_param": 5,
      "secenekler": [],
      "dogru_cevap": "Beklenen doğru cevap ve kısa açıklama"
    }}
  ]
}}
"""
                try:
                    res = yapay_zeka_cagri_fonksiyonu(
                        model_adi='gemini-3.5-flash-lite',
                        contents=[prompt_ana],
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                            thinking_config=types.ThinkingConfig(thinking_level="LOW")
                        )
                    )
                    temiz_json = res.text.replace("```json", "").replace("```", "").strip()
                    icerik = json.loads(temiz_json)

                    kisa_ad = re.sub(r'[^A-Z0-9]', '', temiz_ogr.upper().replace("İ", "I").replace("Ş", "S").replace("Ğ", "G").replace("Ü", "U").replace("Ö", "O").replace("Ç", "C"))[:5]
                    gorev_kodu = f"GRV-{kisa_ad}-{datetime.now().strftime('%d%H%M')}"

                    dongu_kaydet(
                        db_path=db_path,
                        gorev_kodu=gorev_kodu,
                        ogretmen=aktif_ogretmen,
                        sinif=aktif_sube,
                        ogrenci=secilen_ogrenci,
                        kulvar=otomatik_kulvar,
                        ders=icerik.get("odak_ders", "Genel"),
                        konu_ozeti=icerik.get("odak_konu_ozeti", "Bilişsel Pekiştirme"),
                        hata_turu=icerik.get("hata_veya_duzey_turu", "Genel"),
                        tekrar_asamasi=otomatik_asama
                    )

                    st.session_state[f"cift_kulvar_paket_{secilen_ogrenci}"] = {
                        "kulvar": otomatik_kulvar,
                        "gorev_kodu": gorev_kodu,
                        "asama": otomatik_asama,
                        "icerik": icerik
                    }
                except Exception as e:
                    st.error(f"Çalışma kâğıdı hazırlanırken hata oluştu: {str(e)}")

        if f"cift_kulvar_paket_{secilen_ogrenci}" in st.session_state:
            pkt = st.session_state[f"cift_kulvar_paket_{secilen_ogrenci}"]
            ic = pkt["icerik"]

            st.success(f"✅ **{pkt['kulvar']}** çalışma kâğıdı hazır!")

            with st.expander("👀 Hazırlanan Soruları ve Öğretmen Cevap Anahtarını Önizle (PDF'te Cevap Anahtarı Yer Almaz)", expanded=True):
                st.markdown(f"> **Küçük Bir Hatırlatma:** {metin_temizle(ic.get('giris_notu', ''))}")
                for i, s in enumerate(ic.get("sorular", []), 1):
                    st.markdown(f"**Soru {i}:** {metin_temizle(s.get('soru_metni', ''))}")
                    if s.get("secenekler"):
                        st.caption("   ".join([metin_temizle(x) for x in s["secenekler"]]))
                    st.caption(f"🔑 *Öğretmen Cevap Anahtarı:* {metin_temizle(s.get('dogru_cevap', ''))}")

            pdf_bytes = bilissel_calisma_kagidi_pdf(
                ogretmen_adi=temiz_ogrt,
                sube_adi=aktif_sube,
                ogrenci_adi=temiz_ogr,
                kulvar=pkt["kulvar"],
                gorev_kodu=pkt["gorev_kodu"],
                tekrar_asamasi=pkt["asama"],
                icerik_json=ic,
                font_normal=font_normal,
                font_bold=font_bold
            )
            st.download_button(
                label=f"📥 {pkt['kulvar']} Öğrenci Çalışma Kâğıdını PDF İndir (Cevap Anahtarsız Temiz Baskı)",
                data=pdf_bytes,
                file_name=f"{temiz_ogr}_{pkt['kulvar']}_Calisma_Kagidi.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True
            )

        if gecmis_donguler:
            with st.expander(f"🔁 {temiz_ogr} — Aralıklı Tekrar & Görev Takip Döngüsü ({len(gecmis_donguler)} Görev)", expanded=False):
                for gd in gecmis_donguler:
                    g_kod, g_kulvar, g_ders, g_konu, g_tur, g_asama, g_durum, g_tar, g_sonraki = gd
                    c_d1, c_d2 = st.columns([3.5, 1])
                    with c_d1:
                        ikon = "✅" if g_durum == "Ustalık Kazanıldı" else "⏳"
                        st.markdown(f"{ikon} **{g_kulvar}** ({g_ders}: *{g_konu}*) — `{g_tur}` | {g_asama} | Sonraki Kontrol: `{g_sonraki}`")
                    with c_d2:
                        if g_durum != "Ustalık Kazanıldı":
                            if st.button("🏆 Ustalığı Onayla", key=f"ustalik_{g_kod}", use_container_width=True):
                                dongu_ustalik_guncelle(db_path, g_kod)
                                st.rerun()
                        else:
                            st.caption("Tamamlandı")