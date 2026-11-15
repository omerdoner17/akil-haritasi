# veli_ve_telafi.py
# Akıl Haritası — Veli Bilgilendirme Mektubu & WhatsApp Mesaj Üreticisi

import streamlit as st
import streamlit.components.v1 as components
import io
import re
from datetime import datetime
from google.genai import types
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def metni_tdk_ve_duz_metne_cevir(metin):
    if not metin:
        return ""
    metin = re.sub(r'\$?\\frac\{(\d+)\}\{(\d+)\}\$?', r'\1/\2', str(metin))
    metin = metin.replace("$", "").replace("\\times", "x").replace("\\div", "÷")
    return metin.strip()

def veli_mektubu_pdf_olustur(ogretmen_adi, sube_adi, ogrenci_adi, veli_metni, font_normal="Helvetica", font_bold="Helvetica-Bold"):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=42, leftMargin=42, topMargin=42, bottomMargin=42)
    
    temiz_ogrenci = ogrenci_adi.strip().title()
    temiz_ogretmen = ogretmen_adi.strip().title()

    def veli_sablon(canvas_obj, doc_obj):
        canvas_obj.saveState()
        canvas_obj.setStrokeColor(colors.HexColor("#10b981"))
        canvas_obj.setLineWidth(2)
        canvas_obj.roundRect(22, 22, 551, 798, 10, stroke=1, fill=0)
        canvas_obj.setFillColor(colors.HexColor("#065f46"))
        canvas_obj.setFont(font_bold, 16)
        canvas_obj.drawString(42, 782, "VELİ ÖĞRENME & GELİŞİM BİLGİLENDİRME NOTU")
        canvas_obj.setFont(font_normal, 9.5)
        canvas_obj.setFillColor(colors.HexColor("#047857"))
        canvas_obj.drawString(42, 766, f"Sınıf: {sube_adi}  |  Öğrenci: {temiz_ogrenci}  |  Tarih: {datetime.now().strftime('%d.%m.%Y')}")
        canvas_obj.setStrokeColor(colors.HexColor("#a7f3d0"))
        canvas_obj.line(42, 754, 553, 754)
        canvas_obj.setFont(font_normal, 8.5)
        canvas_obj.setFillColor(colors.HexColor("#64748b"))
        canvas_obj.drawString(42, 34, f"Sınıf Öğretmeni: {temiz_ogretmen} — Akıl Haritası Süreç Takip Sistemi")
        canvas_obj.restoreState()

    styles = getSampleStyleSheet()
    govde_stil = ParagraphStyle(
        'VeliGovde',
        parent=styles['Normal'],
        fontName=font_normal,
        textColor=colors.HexColor("#1e293b"),
        fontSize=11,
        leading=17,
        spaceAfter=10
    )

    hikaye = [Spacer(1, 45)]
    temiz_metin = metni_tdk_ve_duz_metne_cevir(veli_metni)
    for paragraf in temiz_metin.split("\n"):
        temiz_p = paragraf.strip()
        if temiz_p:
            temiz_p = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', temiz_p)
            hikaye.append(Paragraph(temiz_p, govde_stil))
            
    doc.build(hikaye, onFirstPage=veli_sablon, onLaterPages=veli_sablon)
    buffer.seek(0)
    return buffer

def veli_ve_telafi_bolumu_render(aktif_ogretmen, aktif_sube, secilen_ogrenci, df_tum, yapay_zeka_cagri_fonksiyonu, font_normal, font_bold):
    st.markdown("""
    <style>
        textarea, .stTextArea textarea, div[data-baseweb="textarea"], div[data-baseweb="base-input"] {
            background-color: #ffffff !important;
            color: #0f172a !important;
            -webkit-text-fill-color: #0f172a !important;
            caret-color: #0284c7 !important;
        }
        div[data-baseweb="textarea"] {
            border: 2px solid #0284c7 !important;
            border-radius: 12px !important;
        }
    </style>
    """, unsafe_allow_html=True)

    temiz_ogrenci_adi = secilen_ogrenci.strip().title()
    temiz_ogretmen_adi = aktif_ogretmen.strip().title()

    with st.container(border=True):
        st.markdown("### 💌 Veli Bilgilendirme Notu (WhatsApp & PDF)")
        st.caption("Öğrencinin sınıf içi performansını ve evde yapılabilecek destekleyici etkinlikleri velinin anlayacağı sıcak bir dille hazırlar.")
        
        if st.button(f"✨ {temiz_ogrenci_adi} İçin Veli Bilgilendirme Metni Hazırla", type="primary", key=f"btn_veli_{secilen_ogrenci}"):
            with st.spinner("TDK yazım kurallarına uygun veli bilgilendirme mektubu hazırlanıyor..."):
                ozet_satirlar = [
                    f"- Ders: {r['ders']} | Konu: {r['kazanim']} | Düzey: {r['rubrik_duzeyi']} | Güçlü Yön: {r['guclu_yonler']} | Gelişim Alanı: {r['kavram_yanilgisi']} | Öneri: {r['eylem_onerisi']}"
                    for _, r in df_tum.head(8).iterrows()
                ]
                prompt_veli = f"""
Sen deneyimli, empatik ve Türkçeyi kusursuz kullanan bir ilkokul sınıf öğretmenisin. Adın: {temiz_ogretmen_adi}.
Aşağıdaki sınıf içi gözlem ve oyun verilerine dayanarak '{temiz_ogrenci_adi}' adlı öğrencinin velisine gönderilmek üzere samimi, motive edici ve anlaşılır bir bilgilendirme mesajı yaz.

Öğrenci Verileri:
{chr(10).join(ozet_satirlar)}

KESİN YAZIM VE ÜSLUP KURALLARI (TDK):
1. Kesinlikle LaTeX veya matematiksel kod kullanma (Örneğin asla $\\frac{{1}}{{2}}$ yazma; bunun yerine "1/2 (yarım)" veya "1/4 (çeyrek)" yaz).
2. TDK Yazım Kılavuzu kurallarına eksiksiz uy: Özel isimlerin ilk harfini büyük yaz ve gelen çekim eklerini kesme işaretiyle ayır (Örn: "{temiz_ogrenci_adi}'nun", "{temiz_ogrenci_adi}'ya", "{temiz_ogrenci_adi}'yı").
3. "Sayın Velimiz," diye sıcak bir giriş yap.
4. Önce öğrencinin sınıftaki güçlü yönlerini ve başardığı konuları somut örneklerle öv.
5. Ardından gelişime açık olduğu noktaları yargılamadan, "birlikte destekleyebileceğimiz alanlar" diliyle sade Türkçeyle açıkla.
6. Velinin evde çocukla oyunlaştırarak yapabileceği 2-3 pratik, masrafsız etkinlik önerisi ver.
7. "Sevgilerimle, {temiz_ogretmen_adi}" şeklinde bitir.
"""
                try:
                    res_veli = yapay_zeka_cagri_fonksiyonu(
                        model_adi='gemini-3.5-flash-lite',
                        contents=[prompt_veli],
                        config=types.GenerateContentConfig(thinking_config=types.ThinkingConfig(thinking_level="LOW"))
                    )
                    st.session_state[f"veli_notu_{secilen_ogrenci}"] = metni_tdk_ve_duz_metne_cevir(res_veli.text)
                except Exception as e:
                    st.error(f"Metin oluşturulurken hata oluştu: {str(e)}")

        if f"veli_notu_{secilen_ogrenci}" in st.session_state:
            duzenlenen_veli_metni = st.text_area(
                "📝 Veli Mesajı Düzenleme Alanı:",
                value=st.session_state[f"veli_notu_{secilen_ogrenci}"],
                height=240,
                key=f"txt_veli_{secilen_ogrenci}"
            )
            
            whatsapp_temiz = duzenlenen_veli_metni.replace("**", "")
            
            c_v1, c_v2 = st.columns(2)
            with c_v1:
                veli_pdf_bytes = veli_mektubu_pdf_olustur(
                    ogretmen_adi=temiz_ogretmen_adi,
                    sube_adi=aktif_sube,
                    ogrenci_adi=temiz_ogrenci_adi,
                    veli_metni=duzenlenen_veli_metni,
                    font_normal=font_normal,
                    font_bold=font_bold
                )
                st.download_button(
                    label="📄 Veli Bilgilendirme Mektubunu PDF İndir",
                    data=veli_pdf_bytes,
                    file_name=f"{temiz_ogrenci_adi}_Veli_Bilgilendirme_Mektubu.pdf",
                    mime="application/pdf",
                    type="primary",
                    use_container_width=True
                )
            with c_v2:
                kopya_html = f"""
                <button id="copyBtn" onclick="copyText()" style="
                    width: 100%; padding: 9px 16px; border-radius: 12px; border: none;
                    background: #25d366; color: #ffffff; font-weight: 800; font-size: 14px;
                    cursor: pointer; font-family: 'Segoe UI', sans-serif; box-shadow: 0 3px 10px rgba(37,211,102,0.3);
                ">📲 WhatsApp Mesajını Panoya Kopyala</button>
                <textarea id="hiddenText" style="position:absolute; left:-9999px;">{whatsapp_temiz}</textarea>
                <script>
                    function copyText() {{
                        var copyText = document.getElementById("hiddenText");
                        copyText.select();
                        document.execCommand("copy");
                        var btn = document.getElementById("copyBtn");
                        btn.innerText = "✅ Kopyalandı! WhatsApp'a Yapıştırabilirsiniz";
                        btn.style.background = "#059669";
                        setTimeout(() => {{
                            btn.innerText = "📲 WhatsApp Mesajını Panoya Kopyala";
                            btn.style.background = "#25d366";
                        }}, 3000);
                    }}
                </script>
                """
                components.html(kopya_html, height=48)