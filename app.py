# app.py
# Akıl Haritası — İlkokul Süreç & Beceri Kokpiti (Nihai Tam Sürüm - Turso & Bulut Oyun Kayıt Entegreli)

import streamlit as st
import sys
import os
import re
import importlib.util
import random
from urllib.parse import unquote

# Tam TYMM Müfredatını, Veli/Telafi Modülünü ve Çift Kulvarlı Bilişsel Pekiştirme Motorunu İçeri Aktar
from tymm_mufredat import mufredat_detayli
from veli_ve_telafi import veli_ve_telafi_bolumu_render
from gunluk_bilissel_pekistirme import (
    cift_kulvar_calisma_studyo_render,
    sabah_isinma_bilmecesi_render,
    dongu_ustalik_guncelle
)

# ----------------- PROJE VE OYUN MODÜLLERİ DİNAMİK YÜKLEYİCİ -----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
oyunlar_dizini = os.path.join(BASE_DIR, "oyunlar")

def modul_yukle(modul_adi_parcasi, fonksiyon_adi):
    if not os.path.exists(oyunlar_dizini):
        return None
    for f in os.listdir(oyunlar_dizini):
        if modul_adi_parcasi in f.lower() and not f.startswith("._") and (f.endswith(".py") or f.endswith(".py.py")):
            dosya_yolu = os.path.join(oyunlar_dizini, f)
            try:
                modul_tekil_ad = f"modul_{modul_adi_parcasi}"
                spec = importlib.util.spec_from_file_location(modul_tekil_ad, dosya_yolu)
                modul = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(modul)
                func = getattr(modul, fonksiyon_adi, None)
                if func is not None:
                    return func
                else:
                    return lambda *args, **kwargs: st.error(f"'{f}' dosyasında '{fonksiyon_adi}' fonksiyonu bulunamadı!")
            except Exception:
                import traceback
                hata_detayi = traceback.format_exc()
                return lambda *args, **kwargs: st.error(f"'{f}' yüklenirken hata oluştu:\n```\n{hata_detayi}\n```")
    return None

# Mevcut ve Yeni Oyun Modülleri (Toplam 11 Oyun)
kesirler_oyunu_render = modul_yukle("kesirler", "kesirler_oyunu_render")
paralarimiz_oyunu_render = modul_yukle("paralar", "paralarimiz_oyunu_render")
saatler_oyunu_render = modul_yukle("saatler", "saatler_oyunu_render")
beslenme_oyunu_render = modul_yukle("beslenme", "beslenme_oyunu_render")
es_anlam_oyunu_render = modul_yukle("es_anlam", "es_anlam_oyunu_render")
kesir_goleti_oyunu_render = modul_yukle("kesir_goleti", "kesir_goleti_oyunu_render")
kesir_zari_oyunu_render = modul_yukle("kesir_zari", "kesir_zari_oyunu_render")
kesir_seritleri_oyunu_render = modul_yukle("kesir_seritleri", "kesir_seritleri_oyunu_render")
buyuk_harf_oyunu_render = modul_yukle("buyuk_harf", "buyuk_harf_oyunu_render")
hak_avcisi_oyunu_render = modul_yukle("hak_avcisi", "hak_avcisi_oyunu_render")
haklar_ormani_oyunu_render = modul_yukle("haklar_ormani", "haklar_ormani_oyunu_render")

from google import genai
from google.genai import types
from PIL import Image
import json
import sqlite3
from datetime import datetime, timedelta
import pandas as pd
import time
import io

try:
    import libsql_client
except ImportError:
    libsql_client = None

# ReportLab Türkçe Font ve PDF Bileşenleri
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ----------------- TÜRKÇE FONT YÜKLEME -----------------
def turkce_font_yukle():
    adaylar = [
        # Linux (Streamlit Cloud) - packages.txt ile kurulur
        ("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
         "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"),
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
         "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
        # Windows (yerel bilgisayar)
        ("C:\\Windows\\Fonts\\arial.ttf", "C:\\Windows\\Fonts\\arialbd.ttf"),
        ("C:\\Windows\\Fonts\\tahoma.ttf", "C:\\Windows\\Fonts\\tahomabd.ttf"),
        ("C:\\Windows\\Fonts\\calibri.ttf", "C:\\Windows\\Fonts\\calibrib.ttf"),
    ]
    for normal, kalin in adaylar:
        if os.path.exists(normal) and os.path.exists(kalin):
            try:
                pdfmetrics.registerFont(TTFont('TRFont', normal))
                pdfmetrics.registerFont(TTFont('TRFont-Bold', kalin))
                return 'TRFont', 'TRFont-Bold'
            except Exception:
                continue
    return 'Helvetica', 'Helvetica-Bold'

FONT_NORMAL, FONT_BOLD = turkce_font_yukle()

# ----------------- HIZLANDIRILMIŞ MERKEZİ API HAVUZU -----------------
try:
    API_KEYS = list(st.secrets["GEMINI_API_KEYS"])
except Exception:
    API_KEYS = []

if "api_key_index" not in st.session_state:
    st.session_state.api_key_index = 0

def aktif_api_anahtari_al():
    return API_KEYS[st.session_state.api_key_index % len(API_KEYS)] if API_KEYS else None

def siradaki_anahtara_gec():
    st.session_state.api_key_index = (st.session_state.api_key_index + 1) % len(API_KEYS)

def dayanikli_rotasyonlu_cagri(model_adi, contents, config=None, max_toplam_deneme=3):
    for deneme in range(1, max_toplam_deneme + 1):
        mevcut_key = aktif_api_anahtari_al()
        if not mevcut_key:
            raise ValueError("Geçerli API anahtarı bulunamadı.")
        try:
            client = genai.Client(api_key=mevcut_key)
            res = client.models.generate_content(model=model_adi, contents=contents, config=config) if config else client.models.generate_content(model=model_adi, contents=contents)
            siradaki_anahtara_gec()
            return res
        except Exception as e:
            siradaki_anahtara_gec()
            if deneme == max_toplam_deneme:
                raise e
            time.sleep(0.2)

# ----------------- 20 STANDART ŞUBE LİSTESİ -----------------
STANDART_20_SUBE = []
for s_no in [1, 2, 3, 4]:
    for s_harf in ["A", "B", "C", "D", "E"]:
        STANDART_20_SUBE.append(f"{s_no}. Sınıf - {s_harf} Şubesi")

# ----------------- TURSO BULUT (libsql-client) & YEREL SQLİTE MOTORU -----------------
DB_PATH = os.path.join(BASE_DIR, "sinif_surec_takip.db")

try:
    _raw_url = str(st.secrets.get("TURSO_DATABASE_URL", "")).strip()
    TURSO_HTTP_URL = _raw_url.replace("libsql://", "https://") if _raw_url.startswith("libsql://") else _raw_url
    TURSO_TOKEN = str(st.secrets.get("TURSO_AUTH_TOKEN", "")).strip()
except Exception:
    TURSO_HTTP_URL = ""
    TURSO_TOKEN = ""

class TursoHttpCursor:
    """libsql_client sorgularını standart sqlite3 cursor yapısına uyarlar."""
    def __init__(self, client):
        self._client = client
        self._rows = []
        self.description = None

    def execute(self, sql, params=()):
        param_list = list(params) if params else []
        res = self._client.execute(sql, param_list)
        if getattr(res, "columns", None):
            self.description = [(col,) for col in res.columns]
        else:
            self.description = None
        self._rows = [tuple(r) for r in getattr(res, "rows", [])]
        return self

    def fetchall(self):
        return self._rows

    def fetchone(self):
        return self._rows[0] if self._rows else None

class TursoHttpConnection:
    """libsql_client bağlantısını sqlite3 connection arayüzüyle sunar."""
    def __init__(self, url, auth_token):
        self._client = libsql_client.create_client_sync(url=url, auth_token=auth_token)

    def cursor(self):
        return TursoHttpCursor(self._client)

    def execute(self, sql, params=()):
        cur = self.cursor()
        return cur.execute(sql, params)

    def commit(self):
        pass

    def close(self):
        try:
            self._client.close()
        except Exception:
            pass

def get_db_connection():
    if libsql_client is not None and TURSO_HTTP_URL and TURSO_TOKEN and "BURAYA_" not in TURSO_TOKEN:
        try:
            return TursoHttpConnection(TURSO_HTTP_URL, TURSO_TOKEN)
        except Exception:
            pass
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.execute("PRAGMA journal_mode = WAL")
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS degerlendirmeler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ogretmen_adi TEXT,
            sinif TEXT,
            ogrenci_adi TEXT,
            ders TEXT,
            kazanim TEXT,
            tarih DATE,
            rubrik_duzeyi TEXT,
            dusunme_sureci TEXT,
            guclu_yonler TEXT,
            kavram_yanilgisi TEXT,
            eylem_onerisi TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS ogrenciler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ogretmen_adi TEXT,
            sinif TEXT,
            ogrenci_adi TEXT,
            maskot TEXT,
            UNIQUE(ogretmen_adi, sinif, ogrenci_adi)
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS ayarlar (
            anahtar TEXT PRIMARY KEY,
            deger TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

SON_KAYIT_ZAMANI = {}

def veri_kaydet(ogretmen, sinif, ogrenci, ders, kazanim, rubrik, dusunme, guclu, yanilgi, oneri):
    global SON_KAYIT_ZAMANI
    anahtar = f"{ogretmen}_{sinif}_{ogrenci}_{kazanim}"
    simdi = time.time()
    
    if anahtar in SON_KAYIT_ZAMANI and (simdi - SON_KAYIT_ZAMANI[anahtar]) < 1.5:
        return

    SON_KAYIT_ZAMANI[anahtar] = simdi

    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO degerlendirmeler 
        (ogretmen_adi, sinif, ogrenci_adi, ders, kazanim, tarih, rubrik_duzeyi, dusunme_sureci, guclu_yonler, kavram_yanilgisi, eylem_onerisi)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        str(ogretmen).strip(),
        str(sinif).strip(),
        str(ogrenci).strip(),
        str(ders).strip(),
        str(kazanim).strip(),
        datetime.now().strftime("%Y-%m-%d %H:%M"),
        str(rubrik).strip(),
        str(dusunme).strip(),
        str(guclu).strip(),
        str(yanilgi).strip(),
        str(oneri).strip()
    ))
    c.execute("INSERT OR REPLACE INTO ayarlar (anahtar, deger) VALUES ('son_yarisan_ogrenci', ?)", (str(ogrenci).strip(),))
    conn.commit()
    conn.close()

def son_yarisan_ogrenciyi_getir():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT deger FROM ayarlar WHERE anahtar = 'son_yarisan_ogrenci'")
    row = c.fetchone()
    conn.close()
    return row[0].strip() if row and row[0] else None

def veri_getir(ogretmen=None, sinif=None, ogrenci=None, gun_sayisi=None):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM degerlendirmeler ORDER BY id DESC")
    rows = c.fetchall()
    cols = [desc[0] for desc in c.description] if c.description else []
    conn.close()

    df = pd.DataFrame(rows, columns=cols) if cols else pd.DataFrame()
    
    if df.empty:
        return df
        
    if ogretmen and ogretmen != "Tüm Öğretmenler":
        df = df[df["ogretmen_adi"].astype(str).str.strip().str.lower() == str(ogretmen).strip().lower()]
    if sinif and sinif != "Tüm Kademeler" and sinif != "Tüm Şubeler":
        df = df[df["sinif"].astype(str).str.strip().str.lower() == str(sinif).strip().lower()]
    if ogrenci and ogrenci != "Tüm Sınıf":
        df = df[df["ogrenci_adi"].astype(str).str.strip().str.lower() == str(ogrenci).strip().lower()]
    if gun_sayisi:
        baslangic = (datetime.now() - timedelta(days=gun_sayisi)).strftime("%Y-%m-%d")
        df = df[df["tarih"].astype(str).str[:10] >= baslangic]
        
    return df

# ----------------- BULUT UYUMLU OYUN KAYIT YAKALAYICISI -----------------
def bulut_oyun_kayit_yakala():
    qp = st.query_params
    if "cark_kaydet" in qp or "ogr" in qp:
        try:
            ogr = unquote(str(qp.get("ogr", ""))).strip()
            durum = unquote(str(qp.get("durum", "Gelişmekte Olan"))).strip()
            gorev = unquote(str(qp.get("gorev", ""))).strip()
            model = unquote(str(qp.get("model", ""))).strip()
            yanilgi = unquote(str(qp.get("yanilgi", ""))).strip()
            oneri = unquote(str(qp.get("oneri", ""))).strip()
            guclu = unquote(str(qp.get("guclu", ""))).strip()
            ogretmen = unquote(str(qp.get("ogretmen", st.session_state.get("aktif_ogretmen", "")))).strip()
            sube = unquote(str(qp.get("sube", st.session_state.get("aktif_sube", "")))).strip()

            if ogr and ogretmen and sube:
                st.session_state.aktif_ogretmen = ogretmen
                st.session_state.aktif_sube = sube

                ders_adi = "Matematik"
                if "Besle" in model or "Beslenme" in model:
                    ders_adi = "Hayat Bilgisi"
                    kazanim_adi = "HB.3.2.1. Kişisel sağlığını koruma bilinci geliştirebilme ve bilinçli tüketici davranışı sergileyebilme"
                elif "Haklar Ormanı" in model or "Hak Avcısı" in model or "Çocuk Hakları" in model:
                    if "4." in sube:
                        ders_adi = "Sosyal Bilgiler"
                        kazanim_adi = "SB.4.4.1. Çocuk haklarını, sorumluluklarını ve aktif vatandaşlık bilincini uygulayabilme"
                    else:
                        ders_adi = "Hayat Bilgisi"
                        kazanim_adi = "HB.3.1.2. Okul kültürüne katkıda bulunabilme ve demokratik katılım gösterebilme"
                elif "Gizemli Kutu" in model or "Eş Anlam" in model:
                    ders_adi = "Türkçe"
                    kazanim_adi = "T.O.3.2. Söz varlığını geliştirebilme ve kelimeler arası anlam ilişkilerini çözümleyebilme"
                elif "Büyük Harf" in model or "TDK" in model:
                    ders_adi = "Türkçe"
                    kazanim_adi = "T.Y.3.1. Yazım ve noktalama kurallarına uyarak okunaklı metinler yazabilme"
                elif "Saat" in model or "Para" in model:
                    ders_adi = "Matematik"
                    kazanim_adi = "MAT.3.4.2. Kütle, sıvı ölçme, zaman ve paralarımızla ilgili problemleri çözebilme"
                else:
                    ders_adi = "Matematik"
                    kazanim_adi = "MAT.3.1.4. Birim kesirleri modelleyebilme ve kesirlerin pay-payda anlamını açıklayabilme"

                veri_kaydet(
                    ogretmen,
                    sube,
                    ogr,
                    ders_adi,
                    kazanim_adi,
                    durum,
                    f"Akıllı tahtada canlı {gorev} görevini {model} üzerinde uyguladı.",
                    guclu,
                    yanilgi,
                    oneri
                )
                st.toast(f"✅ {ogr} adlı öğrencinin oyun sonucu kaydedildi!", icon="🎯")
        except Exception:
            pass
        finally:
            st.query_params.clear()

bulut_oyun_kayit_yakala()

# ----------------- ÖĞRENCİ YÖNETİMİ -----------------
SEVIMLI_MASKOTLAR = [
    "🦁 Aslan", "🐼 Panda", "🦊 Tilki", "🐨 Koala", "🐰 Tavşan", 
    "🐻 Ayıcık", "🐯 Kaplan", "🐸 Kurbağa", "🐵 Maymun", "🐧 Penguen", 
    "🐬 Yunus", "🐙 Ahtapot", "🦄 Tekboynuz", "🦖 Dinozor", "🦉 Baykuş"
]

def sinif_ogrencilerini_getir(ogretmen, sinif):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT ogrenci_adi, maskot FROM ogrenciler WHERE LOWER(TRIM(ogretmen_adi)) = LOWER(TRIM(?)) AND LOWER(TRIM(sinif)) = LOWER(TRIM(?)) ORDER BY id ASC", (ogretmen, sinif))
    rows = c.fetchall()
    conn.close()
    if rows:
        return [{"ad": r[0].strip(), "maskot": r[1]} for r in rows]
    return []

def sinif_ogrencisi_ekle(ogretmen, sinif, ogrenci_adi, maskot="🦁"):
    conn = get_db_connection()
    c = conn.cursor()
    try:
        c.execute("INSERT OR REPLACE INTO ogrenciler (ogretmen_adi, sinif, ogrenci_adi, maskot) VALUES (?, ?, ?, ?)", (ogretmen.strip(), sinif.strip(), ogrenci_adi.strip(), maskot))
        conn.commit()
    except Exception:
        pass
    conn.close()

def sinif_ogrencisi_toplu_ekle(ogretmen, sinif, ogrenci_listesi):
    conn = get_db_connection()
    c = conn.cursor()
    eklenen = 0
    for idx, item in enumerate(ogrenci_listesi):
        ad = str(item.get("Ad Soyad", "")).strip()
        if ad:
            maskot_secimi = SEVIMLI_MASKOTLAR[idx % len(SEVIMLI_MASKOTLAR)].split()[0]
            try:
                c.execute(
                    "INSERT OR REPLACE INTO ogrenciler (ogretmen_adi, sinif, ogrenci_adi, maskot) VALUES (?, ?, ?, ?)",
                    (ogretmen.strip(), sinif.strip(), ad, maskot_secimi)
                )
                eklenen += 1
            except Exception:
                pass
    conn.commit()
    conn.close()
    return eklenen

def sinif_ogrencisi_sil(ogretmen, sinif, ogrenci_adi):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM ogrenciler WHERE LOWER(TRIM(ogretmen_adi)) = LOWER(TRIM(?)) AND LOWER(TRIM(sinif)) = LOWER(TRIM(?)) AND LOWER(TRIM(ogrenci_adi)) = LOWER(TRIM(?))", (ogretmen, sinif, ogrenci_adi))
    conn.commit()
    conn.close()

def tum_ogrenci_adlari_getir(ogretmen, sinif):
    kayitli = sinif_ogrencilerini_getir(ogretmen, sinif)
    adlar = [o["ad"].strip() for o in kayitli]
    
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT DISTINCT ogrenci_adi FROM degerlendirmeler WHERE LOWER(TRIM(ogretmen_adi)) = LOWER(TRIM(?)) AND LOWER(TRIM(sinif)) = LOWER(TRIM(?))", (ogretmen, sinif))
    for r in c.fetchall():
        if r[0] and r[0].strip() not in adlar:
            adlar.append(r[0].strip())
    conn.close()
    return adlar

def veritabani_sifirla(ogretmen, sinif):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM degerlendirmeler WHERE LOWER(TRIM(ogretmen_adi)) = LOWER(TRIM(?)) AND LOWER(TRIM(sinif)) = LOWER(TRIM(?))", (ogretmen, sinif))
    conn.commit()
    conn.close()

# Düz müfredat listesi oluşturucu
mufredat = {}
for sinif_k, dersler_dict in mufredat_detayli.items():
    mufredat[sinif_k] = {}
    for ders_k, kazanim_dict in dersler_dict.items():
        mufredat[sinif_k][ders_k] = list(kazanim_dict.keys())

# ----------------- AKILLI TAHTA OYUN EŞLEŞMELERİ -----------------
KESIRLER_PAKETI = {
    "oyun_adi": "🎯 Kesirler Oyun Paketi (4 Etkileşimli Oyun)",
    "durum": "hazir",
    "modul": "kesirler_paketi",
    "aciklama": "Kesirler Çarkı, Süper Kesir Göleti, 3D Kesir Zarı ve İnteraktif Kesir Şeritleri Laboratuvarı.",
    "materyal": "Kesir Çubuğu, Daire Modeli, 3D Zar ve Nilüfer Göleti"
}

BESLENME_PAKETI = {
    "oyun_adi": "🥗 Ali'yi Besle! — Sağlıklı Beslenme Simülasyonu",
    "durum": "hazir",
    "modul": "beslenme",
    "aciklama": "Sağlıklı ve zararlı besinlerin vücut sağlığı, büyüme-gelişme ve enerji üzerindeki etkisini gösteren simülasyon.",
    "materyal": "İnteraktif Besin Sepeti + Dinamik Karakter Simülatörü"
}

ES_ANLAM_PAKETI = {
    "oyun_adi": "📦 Eş Kardeşlerin Gizemli Kutusu (Eş Anlamlı Kelimeler)",
    "durum": "hazir",
    "modul": "es_anlam",
    "aciklama": "Cümle bağlamında kelimelerin eş anlamlılarını keşfettiren sürükle-bırak kelime makinesi.",
    "materyal": "Gizemli Kelime Makinesi + Cümle Kartları"
}

BUYUK_HARF_PAKETI = {
    "oyun_adi": "🔍 TDK Büyük Harf Avcısı (28 Cümlelik Gezi Hikâyesi)",
    "durum": "hazir",
    "modul": "buyuk_harf",
    "aciklama": "Öyküleyici metin içerisindeki büyük/küçük harf yazım hatalarını TDK kurallarıyla bulma etkinliği.",
    "materyal": "İnteraktif Hikâye Metni + Anlık TDK Kural Rehberi"
}

COCUK_HAKLARI_PAKETI = {
    "oyun_adi": "🧭 Çocuk Hakları Oyun Paketi (2 Etkileşimli Oyun)",
    "durum": "hazir",
    "modul": "cocuk_haklari_paketi",
    "aciklama": "Haklar Ormanı (15 Duraklı Yolculuk) ve Dedektif Hak Avcısı: Mahalle Macerası oyunları.",
    "materyal": "İnteraktif Orman Haritası + Mahalle İstasyonları Haritası"
}

KAZANIM_OYUNLARI = {
    "MAT.3.1.4. Birim kesirleri modelleyebilme ve kesirlerin pay-payda anlamını açıklayabilme": KESIRLER_PAKETI,
    "MAT.3.4.2. Kütle, sıvı ölçme, zaman ve paralarımızla ilgili problemleri çözebilme": {
        "oyun_adi": "⏰ İnteraktif Saat Ustası & 🪙 Paralarımız Kasası",
        "durum": "hazir",
        "modul": "zaman_ve_para",
        "aciklama": "Analog-dijital saat kadranı ile kâğıt banknot ve madeni kuruş kasa manipülatifleri.",
        "materyal": "Etkileşimli Analog Saat + Kâğıt/Madeni Para Kasası"
    },
    "HB.3.2.1. Kişisel sağlığını koruma bilinci geliştirebilme ve bilinçli tüketici davranışı sergileyebilme": BESLENME_PAKETI,
    "HB.3.1.2. Okul kültürüne katkıda bulunabilme ve demokratik katılım gösterebilme": COCUK_HAKLARI_PAKETI,
    "T.O.3.2. Söz varlığını geliştirebilme ve kelimeler arası anlam ilişkilerini çözümleyebilme": ES_ANLAM_PAKETI,
    "T.Y.3.1. Yazım ve noktalama kurallarına uyarak okunaklı metinler yazabilme": BUYUK_HARF_PAKETI,
    "SB.4.4.1. Çocuk haklarını, sorumluluklarını ve aktif vatandaşlık bilincini uygulayabilme": COCUK_HAKLARI_PAKETI,
    "MAT.1.1.5. Bütün ve yarım arasındaki ilişkiyi açıklayabilme": KESIRLER_PAKETI,
    "MAT.2.1.4. Bütün, yarım ve çeyrek arasındaki ilişkileri açıklayabilme": KESIRLER_PAKETI,
    "MAT.4.1.2. Kesirleri sınıflandırabilme, karşılaştırabilme ve kesirlerle işlem yapabilme": KESIRLER_PAKETI,
    "HB.1.2.2. Sağlıklı büyüme ve gelişme için dengeli beslenme alışkanlığı edinebilme": BESLENME_PAKETI,
    "HB.2.2.1. Sağlıklı yaşam alışkanlıklarını sürdürebilme ve sağlık çalışanlarını tanıyabilme": BESLENME_PAKETI,
    "FB.4.2.1. Besin içeriklerini ve dengeli beslenmenin insan sağlığına etkilerini değerlendirebilme": BESLENME_PAKETI,
    "T.O.2.2. Kelime dağarcığını geliştirebilme ve sözlük kullanabilme": ES_ANLAM_PAKETI,
    "T.O.4.2. Söz varlığını geliştirebilme ve kelimeler arası anlam ilişkilerini çözümleyebilme": ES_ANLAM_PAKETI,
    "T.Y.2.1. Yazım ve noktalama kurallarına uygun metinler yazabilme": BUYUK_HARF_PAKETI,
    "T.Y.4.1. Yazım ve noktalama kurallarına uyarak okunaklı ve düzenli metinler yazabilme": BUYUK_HARF_PAKETI
}

# ----------------- REPORTLAB BİREYSEL PDF MOTORU -----------------
def pdf_olustur(ogrenci_adi, veri_listesi):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    
    def pdf_sablon(canvas_obj, doc_obj):
        canvas_obj.saveState()
        canvas_obj.setStrokeColor(colors.HexColor("#0284c7"))
        canvas_obj.setLineWidth(1.5)
        canvas_obj.roundRect(20, 20, 555, 802, 6, stroke=1, fill=0)
        canvas_obj.setFillColor(colors.HexColor("#0f172a"))
        canvas_obj.setFont(FONT_BOLD, 18)
        canvas_obj.drawString(38, 785, "AKIL HARİTASI")
        canvas_obj.setFont(FONT_NORMAL, 9)
        canvas_obj.setFillColor(colors.HexColor("#0284c7"))
        canvas_obj.drawString(38, 771, "İLKOKUL SÜREÇ & BECERİ GELİŞİM PORTFOLYOSU")
        canvas_obj.setFillColor(colors.HexColor("#f8fafc"))
        canvas_obj.setStrokeColor(colors.HexColor("#cbd5e1"))
        canvas_obj.roundRect(390, 762, 165, 34, 4, stroke=1, fill=1)
        canvas_obj.setFont(FONT_BOLD, 9)
        canvas_obj.setFillColor(colors.HexColor("#0f172a"))
        canvas_obj.drawString(398, 782, f"Öğrenci: {ogrenci_adi}")
        canvas_obj.setFont(FONT_NORMAL, 8)
        canvas_obj.setFillColor(colors.HexColor("#64748b"))
        canvas_obj.drawString(398, 769, f"Tarih: {datetime.now().strftime('%d.%m.%Y')}")
        canvas_obj.setStrokeColor(colors.HexColor("#e2e8f0"))
        canvas_obj.line(38, 752, 555, 752)
        canvas_obj.setFont(FONT_NORMAL, 8)
        canvas_obj.setFillColor(colors.HexColor("#94a3b8"))
        canvas_obj.drawString(38, 30, "Bu rapor; öğrencinin akıl yürütme ve somut modelleme basamaklarına göre hazırlanmıştır.")
        canvas_obj.drawRightString(555, 30, f"Sayfa {canvas_obj._pageNumber}")
        canvas_obj.restoreState()

    styles = getSampleStyleSheet()
    baslik_stil = ParagraphStyle('RaporBaslik', parent=styles['Heading2'], fontName=FONT_BOLD, textColor=colors.HexColor("#0f172a"), fontSize=15, spaceAfter=14, alignment=1)
    kart_baslik_stil = ParagraphStyle('KartBaslik', parent=styles['Heading4'], fontName=FONT_BOLD, textColor=colors.HexColor("#0369a1"), fontSize=10.5, spaceAfter=2)
    etiket_stil = ParagraphStyle('Etiket', parent=styles['Normal'], fontName=FONT_BOLD, textColor=colors.HexColor("#334155"), fontSize=8.5, leading=12)
    metin_stil = ParagraphStyle('Metin', parent=styles['Normal'], fontName=FONT_NORMAL, textColor=colors.HexColor("#0f172a"), fontSize=8.5, leading=12.5)

    hikaye = [Spacer(1, 35)]
    hikaye.append(Paragraph(f"BİREYSEL ÖĞRENME & SÜREÇ GELİŞİM RAPORU<br/><font size='11' color='#0284c7'>Öğrenci: {ogrenci_adi}</font>", baslik_stil))
    hikaye.append(Spacer(1, 6))

    if not veri_listesi:
        hikaye.append(Paragraph("Öğrenciye ait henüz kayıtlı süreç verisi bulunmamaktadır.", metin_stil))
    else:
        for v in veri_listesi:
            rubrik_val = str(v[7])
            rubrik_rengi = "#059669" if ("Yetkin" in rubrik_val or "İleri" in rubrik_val) else ("#d97706" if "Gelişmekte" in rubrik_val else "#dc2626")
            kart = [
                [Paragraph(f"<b>{v[6]}</b> — {v[2]} | {v[4]}: <i>{v[5]}</i>", kart_baslik_stil), ""],
                [Paragraph("<b>Rubrik Seviyesi:</b>", etiket_stil), Paragraph(f"<font color='{rubrik_rengi}'><b>{rubrik_val}</b></font>", etiket_stil)],
                [Paragraph("<b>Düşünme Süreci:</b>", etiket_stil), Paragraph(str(v[8]), metin_stil)],
                [Paragraph("<b>Güçlü Yönler:</b>", etiket_stil), Paragraph(str(v[9]), metin_stil)],
                [Paragraph("<b>Tespit Edilen Yanılgı:</b>", etiket_stil), Paragraph(str(v[10]), metin_stil)],
                [Paragraph("<b>Gelişim Rehberliği:</b>", etiket_stil), Paragraph(str(v[11]), metin_stil)]
            ]
            t = Table(kart, colWidths=[115, 405])
            t.setStyle(TableStyle([
                ('SPAN', (0, 0), (1, 0)),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f8fafc")),
                ('PADDING', (0, 0), (-1, -1), 5),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('BOX', (0, 0), (-1, -1), 0.8, colors.HexColor("#cbd5e1")),
                ('INNERGRID', (0, 0), (-1, -1), 0.4, colors.HexColor("#f1f5f9")),
            ]))
            hikaye.append(t)
            hikaye.append(Spacer(1, 10))
            
    doc.build(hikaye, onFirstPage=pdf_sablon, onLaterPages=pdf_sablon)
    buffer.seek(0)
    return buffer

# ----------------- 1-4 DERECELİ SÜREÇ BİLEŞENİ GÖZLEM ÇİZELGESİ PDF MOTORU -----------------
def olcutlu_gozlem_cizelgesi_pdf(ogretmen_adi, sube_adi, ders_adi, ana_kazanim, alt_basamaklar, tablo_satirlari):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), rightMargin=22, leftMargin=22, topMargin=26, bottomMargin=22)
    styles = getSampleStyleSheet()
    
    baslik_stil = ParagraphStyle('OlcutBaslik', parent=styles['Heading2'], fontName=FONT_BOLD, textColor=colors.HexColor("#0f172a"), fontSize=13, spaceAfter=3, alignment=1)
    aciklama_stil = ParagraphStyle('OlcutAciklama', parent=styles['Normal'], fontName=FONT_NORMAL, textColor=colors.HexColor("#334155"), fontSize=8.5, spaceAfter=10, alignment=1)
    hucre_baslik = ParagraphStyle('HucreBaslik', parent=styles['Normal'], fontName=FONT_BOLD, textColor=colors.white, fontSize=7.5, leading=9.5, alignment=1)
    hucre_metin = ParagraphStyle('HucreMetin', parent=styles['Normal'], fontName=FONT_NORMAL, textColor=colors.HexColor("#0f172a"), fontSize=8.5, leading=10.5, alignment=1)
    ad_metin = ParagraphStyle('AdMetin', parent=styles['Normal'], fontName=FONT_BOLD, textColor=colors.HexColor("#0f172a"), fontSize=8.5, leading=10.5, alignment=0)

    hikaye = []
    hikaye.append(Paragraph(f"{ders_adi.upper()} — ÖĞRENME ÇIKTISI & SÜREÇ BİLEŞENİ GÖZLEM ÇİZELGESİ ({sube_adi})", baslik_stil))
    
    max_puan = len(alt_basamaklar) * 4
    olcek_aciklama = f"<b>Öğrenme Çıktısı:</b> {ana_kazanim}<br/>Derecelendirme Ölçeği (1–4): <b>1: Başlangıç | 2: Gelişmekte Olan | 3: Yetkin | 4: İleri Düzey</b> — Öğretmen: <b>{ogretmen_adi}</b> | Tarih: {datetime.now().strftime('%d.%m.%Y')}"
    hikaye.append(Paragraph(olcek_aciklama, aciklama_stil))

    ust_baslik = [
        Paragraph("Sıra", hucre_baslik),
        Paragraph("ÖĞRENCİNİN<br/>ADI-SOYADI", hucre_baslik)
    ]
    for i, basamak in enumerate(alt_basamaklar, 1):
        ust_baslik.append(Paragraph(f"Süreç Bileşeni {i}<br/>{basamak}<br/>(1 - 4)", hucre_baslik))
    ust_baslik.append(Paragraph(f"TOPLAM<br/>(Max {max_puan})", hucre_baslik))
    ust_baslik.append(Paragraph("GENEL DÜZEY<br/>(TYMM)", hucre_baslik))

    tablo_verisi = [ust_baslik]

    for idx, satir in enumerate(tablo_satirlari, 1):
        row_cells = [
            Paragraph(str(idx), hucre_metin),
            Paragraph(satir["Öğrenci Adı"], ad_metin)
        ]
        for i in range(1, len(alt_basamaklar) + 1):
            row_cells.append(Paragraph(f"<b>{satir[f'Bileşen {i}']}</b>", hucre_metin))
        row_cells.append(Paragraph(f"<b>{satir['TOPLAM']}</b>", hucre_metin))
        row_cells.append(Paragraph(f"<b>{satir['GENEL DÜZEY']}</b>", hucre_metin))
        tablo_verisi.append(row_cells)

    olcut_genislik = 470 / max(1, len(alt_basamaklar))
    col_widths = [26, 120] + [olcut_genislik]*len(alt_basamaklar) + [52, 88]

    t = Table(tablo_verisi, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0369a1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f1f5f9")]),
        ('GRID', (0, 0), (-1, -1), 0.6, colors.HexColor("#64748b")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    hikaye.append(t)
    doc.build(hikaye)
    buffer.seek(0)
    return buffer

# ----------------- MODERN ARAYÜZ VE EKRANA SIĞDIRMA STİLİ -----------------
st.set_page_config(page_title="Akıl Haritası — İlkokul Süreç Asistanı", layout="wide", page_icon="🧭")

st.markdown("""
<style>
    .block-container {
        padding-top: 1.2rem !important;
        padding-bottom: 0.5rem !important;
        max-width: 98% !important;
    }
    header[data-testid="stHeader"] {
        background: transparent !important;
        height: 2rem !important;
    }
    iframe {
        width: 100% !important;
        border-radius: 16px !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.06) !important;
    }
    .stApp {
        background: radial-gradient(circle at 10% 10%, #f1f5f9 0%, #e2e8f0 100%);
        color: #0f172a;
        font-family: 'Segoe UI', system-ui, sans-serif;
    }
    div[data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #cbd5e1;
        box-shadow: 4px 0 24px rgba(0, 0, 0, 0.05);
    }
    .stButton>button {
        border-radius: 12px;
        font-weight: 700;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(2, 132, 199, 0.15);
    }
    div[data-testid="stMetricValue"] {
        font-weight: 900;
        color: #0284c7;
    }
    .game-card {
        background: #ffffff;
        border: 2px solid #e2e8f0;
        border-radius: 14px;
        padding: 12px 18px;
        margin-bottom: 10px;
        box-shadow: 0 4px 14px rgba(15,23,42,0.03);
        transition: all 0.2s ease;
    }
    .game-card:hover {
        border-color: #0284c7;
        box-shadow: 0 6px 20px rgba(2,132,199,0.1);
    }
    .step-card {
        background: #ffffff;
        border-left: 5px solid #0284c7;
        border-top: 1px solid #e2e8f0;
        border-right: 1px solid #e2e8f0;
        border-bottom: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 10px 14px;
        margin-bottom: 8px;
        font-size: 13.5px;
        color: #1e293b;
        box-shadow: 0 2px 6px rgba(0,0,0,0.02);
    }
    .badge-ready {
        background: #dcfce7;
        color: #15803d;
        border: 1px solid #86efac;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 800;
    }
    .badge-wip {
        background: #fef9c3;
        color: #854d0e;
        border: 1px solid #fde047;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 800;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- OTURUM YÖNETİMİ -----------------
if "aktif_ogretmen" not in st.session_state:
    st.session_state.aktif_ogretmen = None
if "aktif_sube" not in st.session_state:
    st.session_state.aktif_sube = None
if "secili_oyun_kazanimi" not in st.session_state:
    st.session_state.secili_oyun_kazanimi = "MAT.3.1.4. Birim kesirleri modelleyebilme ve kesirlerin pay-payda anlamını açıklayabilme"
if "olcutlu_cizelge_sonuc" not in st.session_state:
    st.session_state.olcutlu_cizelge_sonuc = None

if not st.session_state.aktif_ogretmen:
    c_b1, c_giris, c_b2 = st.columns([1, 2, 1])
    with c_giris:
        st.markdown("<br/>", unsafe_allow_html=True)
        st.markdown("""
        <div style="background: #ffffff; padding: 36px 30px; border-radius: 24px; border: 1px solid #cbd5e1; box-shadow: 0 20px 50px rgba(2, 132, 199, 0.12); text-align: center; margin-bottom: 20px;">
            <div style="font-size: 54px; margin-bottom: 6px;">🧭</div>
            <h1 style="color: #0284c7; margin: 0; font-size: 32px; font-weight: 900;">AKIL HARİTASI</h1>
            <div style="display: inline-block; background: #e0f2fe; color: #0284c7; padding: 4px 14px; border-radius: 20px; font-size: 13px; font-weight: 800; margin-top: 8px;">
                İlkokul Süreç & Beceri Kokpiti
            </div>
            <p style="color: #64748b; font-size: 14px; margin-top: 14px;">Öğretmen adınızı yazın ve bağlanmak istediğiniz sınıfı seçin:</p>
        </div>
        """, unsafe_allow_html=True)
        
        girilen_ogretmen = st.text_input("👤 Öğretmen Adı Soyadı:", value="Ahmet Öğretmen")
        secilen_sube = st.selectbox("🏫 Bağlanılacak Sınıfınız / Şubeniz:", STANDART_20_SUBE, index=STANDART_20_SUBE.index("3. Sınıf - E Şubesi"))
        
        st.markdown("<br/>", unsafe_allow_html=True)
        if st.button("🚀 Sınıfıma Bağlan ve Başlat", type="primary", use_container_width=True):
            if girilen_ogretmen.strip():
                st.session_state.aktif_ogretmen = girilen_ogretmen.strip()
                st.session_state.aktif_sube = secilen_sube
                st.rerun()
    st.stop()

# ----------------- SOL PANEL -----------------
aktif_ogretmen = st.session_state.aktif_ogretmen
aktif_sube = st.session_state.aktif_sube

st.sidebar.markdown(f"""
<div style="background: linear-gradient(135deg, #0284c7, #0369a1); padding: 18px 14px; border-radius: 16px; color: #ffffff; text-align: center; margin-bottom: 15px; box-shadow: 0 4px 14px rgba(2, 132, 199, 0.25);">
    <div style="font-size: 36px;">🧭</div>
    <div style="font-size: 19px; font-weight: 900;">AKIL HARİTASI</div>
    <div style="background: rgba(255,255,255,0.18); padding: 8px 10px; border-radius: 10px; font-size: 12.5px; margin-top: 10px; border: 1px solid rgba(255,255,255,0.25);">
        👤 <b>{aktif_ogretmen}</b><br/>
        🏫 <span style="color:#fef08a; font-weight:800;">{aktif_sube}</span>
    </div>
</div>
""", unsafe_allow_html=True)

if st.sidebar.button("🚪 Şube Değiştir / Çıkış Yap", use_container_width=True):
    st.session_state.aktif_ogretmen = None
    st.session_state.aktif_sube = None
    st.rerun()

st.sidebar.markdown("---")

sayfa = st.sidebar.radio("Modüller:", [
    "🎮 Akıllı Tahta & Eğitsel Oyunlar",
    "📋 Süreç Bileşeni Gözlem Çizelgesi",
    "📸 Kâğıt / Süreç Analizi",
    "📇 Bireysel Gelişim Kartı",
    "📊 Sınıf Gelişim & Zümre Kokpiti",
    "🏫 Sınıf Öğrenci Listesi"
])

st.sidebar.markdown("---")
if st.sidebar.button("⚠️ Bu Sınıfın Kayıtlarını Sıfırla"):
    veritabani_sifirla(aktif_ogretmen, aktif_sube)
    st.sidebar.success(f"{aktif_sube} kayıtları temizlendi!")
    time.sleep(0.5)
    st.rerun()

# ----------------- MODÜL: SINIF ÖĞRENCİ LİSTESİ -----------------
if sayfa == "🏫 Sınıf Öğrenci Listesi":
    st.title("🏫 Sınıf Öğrenci Kadrosu")
    st.caption(f"Öğretmen: **{aktif_ogretmen}** | Şube: **{aktif_sube}**")
    
    mevcut = sinif_ogrencilerini_getir(aktif_ogretmen, aktif_sube)
    
    c_manuel, c_foto, c_liste = st.columns([1, 1.25, 1])
    
    with c_manuel:
        with st.container(border=True):
            st.markdown("### ➕ Elle Ekle")
            st.caption("Öğrenci adını ve karakterini seçip tek tek ekleyin.")
            yeni_ad = st.text_input("Öğrenci Adı Soyadı:", placeholder="Örn: Zeynep Kaya")
            yeni_mas = st.selectbox("Sevimli Karakteri:", SEVIMLI_MASKOTLAR)
            if st.button("Öğrenciyi Sınıfa Kaydet", type="primary", use_container_width=True) and yeni_ad.strip():
                sinif_ogrencisi_ekle(aktif_ogretmen, aktif_sube, yeni_ad.strip(), yeni_mas.split()[0])
                st.success(f"{yeni_ad} eklendi!")
                time.sleep(0.4)
                st.rerun()

    with c_foto:
        with st.container(border=True):
            st.markdown("### 📸 Fotoğraftan Aktar")
            st.caption("Sınıf defteri fotoğrafını galeriden seçin; isimler otomatik okunur.")
            
            liste_foto = st.file_uploader(
                "Sınıf listesi görseli (JPG/PNG):",
                type=["jpg", "jpeg", "png"],
                key="sinif_listesi_uploader"
            )
            
            if liste_foto is not None:
                dosya_kimligi = f"{liste_foto.name}_{liste_foto.size}"
                if st.session_state.get("son_okunan_liste_dosyasi") != dosya_kimligi:
                    with st.spinner("Liste taranıyor..."):
                        try:
                            img = Image.open(liste_foto)
                            img.thumbnail((1200, 1200))
                            
                            prompt_liste = """
Bu görsel bir okul sınıf defteri veya öğrenci listesidir.
Görseldeki tüm öğrencilerin sıra/okul numaralarını ve Ad Soyad bilgilerini oku.
Sadece geçerli bir JSON listesi döndür, başka açıklama ekleme:
[
  {"Okul No": "145", "Ad Soyad": "Ahmet Yılmaz"},
  {"Okul No": "146", "Ad Soyad": "Ayşe Demir"}
]
Not: Başlıkları (Sıra No, Adı Soyadı, Sınıf vb.) alma. İsimlerin baş harflerini büyük yaz (Title Case).
"""
                            res = dayanikli_rotasyonlu_cagri(
                                model_adi='gemini-3.5-flash-lite',
                                contents=[img, prompt_liste],
                                config=types.GenerateContentConfig(
                                    response_mime_type="application/json",
                                    thinking_config=types.ThinkingConfig(thinking_level="LOW")
                                )
                            )
                            temiz_json = res.text.replace("```json", "").replace("```", "").strip()
                            okunan_liste = json.loads(temiz_json)
                            
                            if isinstance(okunan_liste, list) and len(okunan_liste) > 0:
                                st.session_state["gecici_sinif_df"] = pd.DataFrame(okunan_liste)
                            else:
                                st.warning("İsim okunamadı. Tablodan ekleyebilirsiniz.")
                                st.session_state["gecici_sinif_df"] = pd.DataFrame([{"Okul No": "", "Ad Soyad": ""}])
                            
                            st.session_state["son_okunan_liste_dosyasi"] = dosya_kimligi
                        except Exception as e:
                            st.error(f"Hata: {str(e)}")

            if "gecici_sinif_df" in st.session_state:
                st.caption("Hatalı harf varsa çift tıklayıp düzeltebilirsiniz:")
                duzenlenmis_liste_df = st.data_editor(
                    st.session_state["gecici_sinif_df"],
                    num_rows="dynamic",
                    use_container_width=True,
                    hide_index=True
                )
                
                if st.button(f"💾 Listeyi {aktif_sube} Sınıfına Kaydet", type="primary", use_container_width=True):
                    kayitlar = duzenlenmis_liste_df.to_dict(orient="records")
                    eklenen_sayi = sinif_ogrencisi_toplu_ekle(aktif_ogretmen, aktif_sube, kayitlar)
                    if eklenen_sayi > 0:
                        del st.session_state["gecici_sinif_df"]
                        st.session_state["son_okunan_liste_dosyasi"] = None
                        st.success(f"✅ {eklenen_sayi} öğrenci eklendi!")
                        time.sleep(0.6)
                        st.rerun()
                    else:
                        st.warning("Geçerli bir öğrenci adı bulunamadı.")

    with c_liste:
        with st.container(border=True):
            st.markdown(f"### 📋 Mevcut ({len(mevcut)})")
            if not mevcut:
                st.info("Henüz kayıtlı öğrenci yok.")
            else:
                for ogr in mevcut:
                    co1, co2 = st.columns([3, 1.2])
                    with co1:
                        st.markdown(f"**{ogr['maskot']} {ogr['ad']}**")
                    with co2:
                        if st.button("Sil", key=f"sil_{ogr['ad']}", use_container_width=True):
                            sinif_ogrencisi_sil(aktif_ogretmen, aktif_sube, ogr['ad'])
                            st.rerun()

# ----------------- MODÜL: AKILLI TAHTA & EĞİTSEL OYUN KOKPİTİ -----------------
elif sayfa == "🎮 Akıllı Tahta & Eğitsel Oyunlar":
    kademe_kodu = aktif_sube.split(".")[0] + ". Sınıf"
    if kademe_kodu not in mufredat:
        kademe_kodu = "3. Sınıf"

    st.markdown(f"""
    <div style="background: #ffffff; padding: 10px 18px; border-radius: 12px; border: 1px solid #cbd5e1; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center;">
        <div>
            <span style="font-size:18px; font-weight:900; color:#0f172a;">🎮 Akıllı Tahta & Eğitsel Oyun Kokpiti</span>
        </div>
        <div style="font-size:13px;">🏫 <b>Sınıf:</b> <span style="color:#0284c7; font-weight:800;">{aktif_sube}</span> &nbsp;|&nbsp; 👤 <b>Öğretmen:</b> <span style="color:#0284c7; font-weight:800;">{aktif_ogretmen}</span></div>
    </div>
    """, unsafe_allow_html=True)

    c_d1, c_d2 = st.columns([1, 2.5])
    with c_d1:
        dersler = list(mufredat[kademe_kodu].keys())
        varsayilan_ders_idx = dersler.index("Matematik") if "Matematik" in dersler else 0
        secilen_ders = st.selectbox("📚 Ders Seçiniz:", dersler, index=varsayilan_ders_idx)

    with c_d2:
        kazanimlar = mufredat[kademe_kodu][secilen_ders]
        varsayilan_kaz_idx = 0
        if st.session_state.secili_oyun_kazanimi in kazanimlar:
            varsayilan_kaz_idx = kazanimlar.index(st.session_state.secili_oyun_kazanimi)
        secilen_kazanim = st.selectbox("🎯 Öğrenme Çıktısı Seçiniz:", kazanimlar, index=varsayilan_kaz_idx)
        st.session_state.secili_oyun_kazanimi = secilen_kazanim

    alt_basamaklar_oyun = mufredat_detayli[kademe_kodu][secilen_ders].get(secilen_kazanim, [])
    if alt_basamaklar_oyun:
        with st.expander("📌 Bu Öğrenme Çıktısının Süreç Bileşenleri (Alt Basamaklar)", expanded=False):
            for basamak in alt_basamaklar_oyun:
                st.markdown(f"- {basamak}")

    ogrenciler = sinif_ogrencilerini_getir(aktif_ogretmen, aktif_sube)

    if secilen_kazanim in KAZANIM_OYUNLARI:
        oyun_bilgi = KAZANIM_OYUNLARI[secilen_kazanim]
        
        st.markdown(f"""
        <div class="game-card">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <h4 style="margin:0; color:#0284c7; font-size:16px;">{oyun_bilgi['oyun_adi']}</h4>
                <span class="badge-ready">🟢 Oynamaya Hazır</span>
            </div>
            <div style="font-size:12.5px; color:#475569; margin-top:4px;">{oyun_bilgi['aciklama']}</div>
        </div>
        """, unsafe_allow_html=True)

        if oyun_bilgi["modul"] == "kesirler_paketi":
            t_cark, t_golet, t_zar, t_serit = st.tabs([
                "🎯 Kesirler Çarkı", 
                "🐸 Süper Kesir Göleti", 
                "🎲 3D Kesir Zarı", 
                "📏 İnteraktif Kesir Şeritleri"
            ])
            with t_cark:
                if kesirler_oyunu_render:
                    kesirler_oyunu_render(aktif_ogretmen, aktif_sube, ogrenciler)
                else:
                    st.error("oyunlar/kesirler.py modülü bulunamadı.")
            with t_golet:
                if kesir_goleti_oyunu_render:
                    kesir_goleti_oyunu_render(aktif_ogretmen, aktif_sube, ogrenciler)
                else:
                    st.error("oyunlar/kesir_goleti.py modülü bulunamadı.")
            with t_zar:
                if kesir_zari_oyunu_render:
                    kesir_zari_oyunu_render(aktif_ogretmen, aktif_sube, ogrenciler)
                else:
                    st.error("oyunlar/kesir_zari.py modülü bulunamadı.")
            with t_serit:
                if kesir_seritleri_oyunu_render:
                    kesir_seritleri_oyunu_render(aktif_ogretmen, aktif_sube, ogrenciler)
                else:
                    st.error("oyunlar/kesir_seritleri.py modülü bulunamadı.")

        elif oyun_bilgi["modul"] == "zaman_ve_para":
            tab_saat, tab_para = st.tabs(["⏰ İnteraktif Saat Ustası", "🪙 Paralarımız Kasası"])
            with tab_saat:
                if saatler_oyunu_render:
                    saatler_oyunu_render(aktif_ogretmen, aktif_sube, ogrenciler)
                else:
                    st.error("oyunlar/saatler.py modülü bulunamadı.")
            with tab_para:
                if paralarimiz_oyunu_render:
                    paralarimiz_oyunu_render(aktif_ogretmen, aktif_sube, ogrenciler)
                else:
                    st.error("oyunlar/paralarimiz.py modülü bulunamadı.")

        elif oyun_bilgi["modul"] == "beslenme":
            if beslenme_oyunu_render:
                beslenme_oyunu_render(aktif_ogretmen, aktif_sube, ogrenciler)
            else:
                st.error("oyunlar/beslenme.py modülü bulunamadı.")

        elif oyun_bilgi["modul"] == "es_anlam":
            if es_anlam_oyunu_render:
                es_anlam_oyunu_render(aktif_ogretmen, aktif_sube, ogrenciler)
            else:
                st.error("oyunlar/es_anlam.py modülü bulunamadı.")

        elif oyun_bilgi["modul"] == "buyuk_harf":
            if buyuk_harf_oyunu_render:
                buyuk_harf_oyunu_render(aktif_ogretmen, aktif_sube, ogrenciler)
            else:
                st.error("oyunlar/buyuk_harf.py modülü bulunamadı.")

        elif oyun_bilgi["modul"] == "cocuk_haklari_paketi":
            tab_orman, tab_mahalle = st.tabs([
                "🌲 Haklar Ormanı (15 Duraklı Yolculuk)",
                "🔍 Dedektif Hak Avcısı: Mahalle Macerası"
            ])
            with tab_orman:
                if haklar_ormani_oyunu_render:
                    haklar_ormani_oyunu_render(aktif_ogretmen, aktif_sube, ogrenciler)
                else:
                    st.error("oyunlar/haklar_ormani.py modülü bulunamadı.")
            with tab_mahalle:
                if hak_avcisi_oyunu_render:
                    hak_avcisi_oyunu_render(aktif_ogretmen, aktif_sube, ogrenciler)
                else:
                    st.error("oyunlar/hak_avcisi.py modülü bulunamadı.")

    else:
        st.markdown(f"""
        <div class="game-card" style="border-left: 5px solid #f59e0b;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <h3 style="margin:0; color:#0f172a; font-size:17px;">🎯 {secilen_kazanim}</h3>
                <span class="badge-wip">📋 Yeni Oyun Tasarımı Bekleniyor</span>
            </div>
            <p style="margin:8px 0 0 0; color:#64748b; font-size:13.5px;">
                Bu öğrenme çıktısı için henüz özel bir akıllı tahta oyunu kodlanmadı. 
                Ancak sol menüdeki <b>📋 Süreç Bileşeni Gözlem Çizelgesi</b> ve <b>📸 Kâğıt / Süreç Analizi</b> modüllerinde tüm süreç bileşenleriyle birlikte değerlendirme yapabilirsiniz.
            </p>
        </div>
        """, unsafe_allow_html=True)

# ----------------- MODÜL: 1-4 ÖLÇEKLİ SÜREÇ BİLEŞENİ GÖZLEM ÇİZELGESİ -----------------
elif sayfa == "📋 Süreç Bileşeni Gözlem Çizelgesi":
    st.title("📋 TYMM Öğrenme Çıktısı & Süreç Bileşeni Gözlem Çizelgesi")
    st.markdown(f"**Sınıf:** `{aktif_sube}` | **Öğretmen:** `{aktif_ogretmen}` | **Derecelendirme Ölçeği:** `1 – 4 (1: Başlangıç, 2: Gelişmekte Olan, 3: Yetkin, 4: İleri Düzey)`")

    kademe_kodu = aktif_sube.split(".")[0] + ". Sınıf"
    if kademe_kodu not in mufredat_detayli:
        kademe_kodu = "3. Sınıf"

    with st.container(border=True):
        c_s1, c_s2 = st.columns([1, 2.2])
        with c_s1:
            dersler = list(mufredat_detayli[kademe_kodu].keys())
            varsayilan_d_idx = dersler.index("Matematik") if "Matematik" in dersler else 0
            secili_ders_olcut = st.selectbox("📚 Ders Seçiniz:", dersler, index=varsayilan_d_idx, key="olcut_ders")
        with c_s2:
            kazanim_listesi = list(mufredat_detayli[kademe_kodu][secili_ders_olcut].keys())
            secili_ana_kazanim = st.selectbox("🎯 Ana Öğrenme Çıktısı:", kazanim_listesi, key="olcut_ana_kazanim")

        tum_alt_basamaklar = mufredat_detayli[kademe_kodu][secili_ders_olcut][secili_ana_kazanim]
        
        st.markdown("#### 🧩 Değerlendirilecek Süreç Bileşenleri (Alt Basamaklar)")
        secilen_alt_basamaklar = []
        cols_check = st.columns(2)
        for i, basamak in enumerate(tum_alt_basamaklar):
            with cols_check[i % 2]:
                if st.checkbox(f"**{basamak}**", value=True, key=f"chk_{secili_ana_kazanim}_{i}"):
                    secilen_alt_basamaklar.append(basamak)

    sinif_ogrencileri = sinif_ogrencilerini_getir(aktif_ogretmen, aktif_sube)

    if not sinif_ogrencileri:
        st.warning(f"⚠️ **{aktif_sube}** sınıfında kayıtlı öğrenci bulunmuyor. Lütfen önce **🏫 Sınıf Öğrenci Listesi** sekmesinden öğrencilerinizi ekleyin.")
    elif not secilen_alt_basamaklar:
        st.warning("⚠️ Lütfen çizelgede değerlendirilecek en az 1 süreç bileşeni seçiniz.")
    else:
        if st.button("🚀 Tüm Sınıfı Seçili Süreç Bileşenlerine Göre (1–4) Değerlendir ve Çizelgeyi Doldur", type="primary", use_container_width=True):
            with st.spinner("Öğrencilerin oyun ve çalışma kâğıdı verileri inceleniyor, süreç bileşeni çizelgesi hazırlanıyor..."):
                df_sinif_gecmisi = veri_getir(ogretmen=aktif_ogretmen, sinif=aktif_sube)
                
                verisi_olanlar = []
                verisi_olmayanlar_satir = []
                
                for ogr in sinif_ogrencileri:
                    ogr_ad = ogr["ad"]
                    if not df_sinif_gecmisi.empty:
                        ogr_kayitlari = df_sinif_gecmisi[df_sinif_gecmisi["ogrenci_adi"].astype(str).str.strip().str.lower() == ogr_ad.lower()]
                    else:
                        ogr_kayitlari = pd.DataFrame()
                        
                    if not ogr_kayitlari.empty:
                        ozet_gecmis = " | ".join([
                            f"{r['kazanim']} -> {r['rubrik_duzeyi']} ({r['kavram_yanilgisi']})"
                            for _, r in ogr_kayitlari.head(4).iterrows()
                        ])
                        verisi_olanlar.append({
                            "ogrenci_adi": ogr_ad,
                            "gecmis": ozet_gecmis
                        })
                    else:
                        bos_satir = {"Öğrenci Adı": ogr_ad}
                        for i in range(1, len(secilen_alt_basamaklar) + 1):
                            bos_satir[f"Bileşen {i}"] = "-"
                        bos_satir["TOPLAM"] = "-"
                        bos_satir["GENEL DÜZEY"] = "Veri Bekleniyor"
                        verisi_olmayanlar_satir.append(bos_satir)

                dolu_satirlar = []
                if verisi_olanlar:
                    prompt_olcut = f"""
TYMM uzmanısın. Aşağıdaki öğrencilerin geçmiş oyun ve çalışma kâğıdı verilerine göre '{secili_ana_kazanim}' öğrenme çıktısının her bir süreç bileşeni için 1 ile 4 arasında tam sayı puan ver (1: Başlangıç, 2: Gelişmekte Olan, 3: Yetkin, 4: İleri Düzey).
Süreç Bileşenleri ({len(secilen_alt_basamaklar)} adet): {json.dumps(secilen_alt_basamaklar, ensure_ascii=False)}
Öğrenciler: {json.dumps(verisi_olanlar, ensure_ascii=False)}

Sadece geçerli JSON listesi döndür:
[
  {{"ogrenci_adi": "Ad", "puanlar": [3, 4, 2, 3]}}
]
(puanlar listesi tam olarak {len(secilen_alt_basamaklar)} elemanlı olmalı ve her eleman 1 ile 4 arasında tam sayı olmalıdır.)
"""
                    try:
                        response = dayanikli_rotasyonlu_cagri(
                            model_adi='gemini-3.5-flash-lite',
                            contents=[prompt_olcut],
                            config=types.GenerateContentConfig(
                                response_mime_type="application/json",
                                thinking_config=types.ThinkingConfig(thinking_level="LOW")
                            )
                        )
                        temiz_json = response.text.replace("```json", "").replace("```", "").strip()
                        yz_sonuc_listesi = json.loads(temiz_json)
                        
                        for item in yz_sonuc_listesi:
                            o_ad = item.get("ogrenci_adi", "")
                            puanlar = item.get("puanlar", [2]*len(secilen_alt_basamaklar))
                            
                            temiz_puanlar = []
                            for p in puanlar[:len(secilen_alt_basamaklar)]:
                                val = max(1, min(4, int(p)))
                                temiz_puanlar.append(val)
                            while len(temiz_puanlar) < len(secilen_alt_basamaklar):
                                temiz_puanlar.append(2)
                                
                            toplam_puan = sum(temiz_puanlar)
                            ortalama_puan = toplam_puan / len(secilen_alt_basamaklar)
                            
                            if ortalama_puan < 1.75:
                                genel_durum = "Başlangıç Düzeyi"
                            elif ortalama_puan < 2.50:
                                genel_durum = "Gelişmekte Olan"
                            elif ortalama_puan < 3.40:
                                genel_durum = "Yetkin Düzey"
                            else:
                                genel_durum = "İleri Düzey"

                            satir = {"Öğrenci Adı": o_ad}
                            for idx_o, puan_val in enumerate(temiz_puanlar, 1):
                                satir[f"Bileşen {idx_o}"] = puan_val
                            satir["TOPLAM"] = toplam_puan
                            satir["GENEL DÜZEY"] = genel_durum
                            dolu_satirlar.append(satir)
                            
                    except Exception as e:
                        st.error(f"Değerlendirme sırasında hata oluştu: {str(e)}")

                tum_cizelge = dolu_satirlar + verisi_olmayanlar_satir
                if tum_cizelge:
                    st.session_state.olcutlu_cizelge_sonuc = {
                        "ders": secili_ders_olcut,
                        "ana_kazanim": secili_ana_kazanim,
                        "alt_basamaklar": secilen_alt_basamaklar,
                        "tablo": tum_cizelge
                    }
                    st.success("✅ Tüm sınıfın 1–4 dereceli süreç bileşeni gözlem çizelgesi başarıyla dolduruldu!")

        if st.session_state.olcutlu_cizelge_sonuc:
            paket = st.session_state.olcutlu_cizelge_sonuc
            st.markdown("---")
            st.markdown(f"### 📝 {aktif_sube} — {paket['ders']} Süreç Bileşeni Gözlem Çizelgesi")
            st.caption(f"**Öğrenme Çıktısı:** {paket['ana_kazanim']}")
            
            for idx_b, b_metin in enumerate(paket["alt_basamaklar"], 1):
                st.markdown(f'<div class="step-card"><b>Bileşen {idx_b}:</b> {b_metin}</div>', unsafe_allow_html=True)
            
            df_cizelge = pd.DataFrame(paket["tablo"])
            duzenlenmis_df = st.data_editor(df_cizelge, use_container_width=True, hide_index=True)
            
            pdf_cizelge_bytes = olcutlu_gozlem_cizelgesi_pdf(
                ogretmen_adi=aktif_ogretmen,
                sube_adi=aktif_sube,
                ders_adi=paket["ders"],
                ana_kazanim=paket["ana_kazanim"],
                alt_basamaklar=paket["alt_basamaklar"],
                tablo_satirlari=duzenlenmis_df.to_dict(orient="records")
            )
            st.download_button(
                label="📥 Doldurulmuş Süreç Bileşeni Gözlem Çizelgesini PDF İndir",
                data=pdf_cizelge_bytes,
                file_name=f"{aktif_sube}_{paket['ders']}_Surec_Bileseni_Cizelgesi.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True
            )

# ----------------- MODÜL: BİREYSEL GELİŞİM KARTI (ÇİFT KULVAR + VELİ/TELAFİ) -----------------
elif sayfa == "📇 Bireysel Gelişim Kartı":
    st.title("📇 Bireysel Gelişim & Diferansiyel Çalışma Stüdyosu")
    st.markdown(f"**Sınıf:** `{aktif_sube}` | **Öğretmen:** `{aktif_ogretmen}`")
    
    ogrenci_listesi = tum_ogrenci_adlari_getir(aktif_ogretmen, aktif_sube)
    
    if not ogrenci_listesi:
        st.info(f"ℹ️ **{aktif_sube}** sınıfında henüz kayıtlı bir öğrenci veya süreç verisi bulunmuyor.")
    else:
        son_ogr = son_yarisan_ogrenciyi_getir()
        varsayilan_ogr_idx = 0
        if son_ogr and son_ogr in ogrenci_listesi:
            varsayilan_ogr_idx = ogrenci_listesi.index(son_ogr)
            
        c_sec, c_ind = st.columns([3, 1])
        with c_sec:
            secilen = st.selectbox("👤 İncelenecek Öğrenciyi Seçiniz (En son yarışan otomatik seçilir):", ogrenci_listesi, index=varsayilan_ogr_idx)
            
        df_tum = veri_getir(ogretmen=aktif_ogretmen, sinif=aktif_sube, ogrenci=secilen)
        
        with c_ind:
            st.markdown("<br/>", unsafe_allow_html=True)
            if not df_tum.empty:
                pdf_bytes = pdf_olustur(secilen, df_tum.values.tolist())
                st.download_button(
                    label="💾 Portfolyo PDF İndir",
                    data=pdf_bytes,
                    file_name=f"{secilen}_{aktif_sube}_gelisim_raporu.pdf",
                    mime="application/pdf",
                    type="primary",
                    use_container_width=True
                )
            else:
                st.button("💾 Portfolyo PDF", disabled=True, use_container_width=True)
                
        st.markdown(f"""
        <div style="padding: 16px 22px; border-radius: 16px; background: #ffffff; border: 2px solid #0284c7; box-shadow: 0 4px 15px rgba(0,0,0,0.04); margin-bottom: 16px;">
            <h2 style="margin: 0; color: #0284c7; font-size: 24px;">👤 {secilen}</h2>
            <p style="margin: 4px 0 0 0; color: #64748b; font-weight: 600;">Sınıf/Şube: <b>{aktif_sube}</b> | Toplam Süreç Kaydı: <b style="color:#0284c7;">{len(df_tum)}</b></p>
        </div>
        """, unsafe_allow_html=True)
        
        if df_tum.empty:
            st.info(f"ℹ️ **{secilen}** için henüz sistemde kayıtlı bir süreç verisi bulunmuyor.")
        else:
            # Öğrencinin kayıtlı maskotunu bul
            kayitli_list = sinif_ogrencilerini_getir(aktif_ogretmen, aktif_sube)
            ogr_maskot = next((x["maskot"] for x in kayitli_list if x["ad"].lower() == secilen.lower()), "🦁")

            # 1. Çift Kulvarlı (Destekleme & Zenginleştirme) Bilişsel Pekiştirme Atölyesi
            cift_kulvar_calisma_studyo_render(
                DB_PATH,
                aktif_ogretmen,
                aktif_sube,
                secilen,
                ogr_maskot,
                df_tum,
                dayanikli_rotasyonlu_cagri,
                FONT_NORMAL,
                FONT_BOLD
            )
            st.markdown("---")

            # 2. Veli Bilgilendirme ve Konu Bazlı Telafi Modülü
            veli_ve_telafi_bolumu_render(
                aktif_ogretmen,
                aktif_sube,
                secilen,
                df_tum,
                dayanikli_rotasyonlu_cagri,
                FONT_NORMAL,
                FONT_BOLD
            )

            st.markdown("---")
            st.markdown("### 📜 Öğrencinin Tüm Süreç & Gözlem Kayıtları")
            for idx, row in df_tum.iterrows():
                with st.container():
                    st.markdown(f"""
                    <div style="background:#ffffff; padding:16px; border-radius:14px; border:1px solid #e2e8f0; margin-bottom:12px; box-shadow:0 2px 8px rgba(0,0,0,0.02);">
                        <div style="font-size:15.5px; font-weight:800; color:#0f172a;">
                            📅 {row['tarih']} — 👤 <b>{row['ogrenci_adi']}</b> ({row['sinif']}) | {row['ders']}: <span style="color:#0284c7;">{row['kazanim']}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    c_a, c_b = st.columns([1, 2])
                    with c_a:
                        st.metric("Rubrik Seviyesi", row['rubrik_duzeyi'])
                    with c_b:
                        st.markdown(f"**Düşünme Süreci:** {row['dusunme_sureci']}")
                        
                    col_g, col_y = st.columns(2)
                    with col_g:
                        st.success(f"**⭐ Güçlü Yönler:**\n\n{row['guclu_yonler']}")
                    with col_y:
                        st.warning(f"**⚠️ Bilişsel Engel / Yanılgı:**\n\n{row['kavram_yanilgisi']}")
                        
                    st.info(f"**💡 Öğretmen Destek Önerisi:**\n\n{row['eylem_onerisi']}")
                    st.markdown("---")

# ----------------- MODÜL: SINIF KOKPİTİ -----------------
elif sayfa == "📊 Sınıf Gelişim & Zümre Kokpiti":
    st.title("📊 Akıl Haritası — Sınıf Gelişim & Zümre Kokpiti")
    
    # Sınıf geneli Sabah Isınma Bilmecesi ve Ortak Yanılgı Özeti
    df_sinif_genel = veri_getir(ogretmen=aktif_ogretmen, sinif=aktif_sube)
    sabah_isinma_bilmecesi_render(aktif_ogretmen, aktif_sube, df_sinif_genel, dayanikli_rotasyonlu_cagri)

    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        f_kapsam = st.selectbox("🏫 İnceleme Kapsamı:", [f"Kendi Sınıfım ({aktif_sube})", "Tüm Şubeler (Zümre Geneli)"])
    with col_f2:
        zaman_filtresi = st.selectbox("📅 Zaman Aralığı:", ["Son 1 Hafta (7 Gün)", "Son 1 Ay (30 Gün)", "Tüm Dönem / Yıl"])
        
    gun_haritasi = {"Son 1 Hafta (7 Gün)": 7, "Son 1 Ay (30 Gün)": 30, "Tüm Dönem / Yıl": None}
    
    filtre_ogretmen = aktif_ogretmen if "Kendi Sınıfım" in f_kapsam else None
    filtre_sinif = aktif_sube if "Kendi Sınıfım" in f_kapsam else None
    
    tum_adlar = tum_ogrenci_adlari_getir(aktif_ogretmen, aktif_sube)
    with col_f3:
        secilen_ogrenci = st.selectbox("👤 Öğrenci Filtresi:", ["Tüm Sınıf"] + tum_adlar)

    df = veri_getir(ogretmen=filtre_ogretmen, sinif=filtre_sinif, ogrenci=secilen_ogrenci, gun_sayisi=gun_haritasi[zaman_filtresi])

    if df.empty:
        st.info("ℹ️ Seçilen filtrede henüz kayıtlı bir değerlendirme verisi bulunamadı.")
    else:
        df_goster = df
        c_kpi1, c_kpi2, c_kpi3 = st.columns(3)
        c_kpi1.metric("Toplam Süreç Kaydı", len(df_goster))
        yetkin_sayisi = len(df_goster[df_goster["rubrik_duzeyi"].str.contains("Yetkin|İleri", na=False)])
        c_kpi2.metric("Yetkin ve İleri Düzey", yetkin_sayisi)
        destek_sayisi = len(df_goster[df_goster["rubrik_duzeyi"].str.contains("Gelişmekte|Başlangıç", na=False)])
        c_kpi3.metric("Destek / Yanılgı Tespiti", destek_sayisi)

        st.bar_chart(df_goster["rubrik_duzeyi"].value_counts())
        
        st.markdown("---")
        st.markdown("### 📜 Detaylı Gözlem ve Süreç Tablosu (Tüm Öğrenciler)")
        st.dataframe(
            df_goster[["tarih", "ogrenci_adi", "sinif", "ders", "kazanim", "rubrik_duzeyi", "dusunme_sureci", "kavram_yanilgisi", "eylem_onerisi"]],
            use_container_width=True
        )
        
        csv_data = df_goster.to_csv(index=False, sep=';').encode('utf-8-sig')
        st.download_button(
            label="📥 Bu Tabloyu İndir (Excel CSV)",
            data=csv_data,
            file_name=f"{aktif_sube}_surec_raporu.csv",
            mime="text/csv"
        )

# ----------------- MODÜL: KÂĞIT / SÜREÇ ANALİZİ (ÇOKLU FOTOĞRAF + KAPALI DEVRE GÖREV KODU) -----------------
elif sayfa == "📸 Kâğıt / Süreç Analizi":
    st.title("🌱 Akıl Haritası — Beceri & Süreç Analizi")
    st.markdown(f"**Sınıf:** `{aktif_sube}` | **Öğretmen:** `{aktif_ogretmen}`")
    
    col_input, col_result = st.columns([1, 1])
    with col_input:
        st.subheader("📋 Öğrenci ve Öğrenme Çıktısı Bilgisi")
        
        varsayilan_kademe_index = 2
        for ki, kademe_adi in enumerate(list(mufredat.keys())):
            if kademe_adi[:2] in aktif_sube:
                varsayilan_kademe_index = ki
                break
                
        secilen_kademe = st.selectbox("🏫 Kademe Seçiniz:", list(mufredat.keys()), index=varsayilan_kademe_index)
        
        ogrenciler = [o["ad"] for o in sinif_ogrencilerini_getir(aktif_ogretmen, aktif_sube)]
        if ogrenciler:
            ogrenci_adi = st.selectbox("👤 Öğrenci Seçiniz:", ogrenciler)
        else:
            ogrenci_adi = st.text_input("👤 Öğrenci Adı Soyadı:", value="Öğrenci")
            
        secilen_ders = st.selectbox("📚 Ders Seçiniz:", list(mufredat[secilen_kademe].keys()), index=1)
        secilen_kazanim = st.selectbox("🎯 Öğrenme Çıktısı:", mufredat[secilen_kademe][secilen_ders])
        
        alt_basamaklar_kagit = mufredat_detayli[secilen_kademe][secilen_ders].get(secilen_kazanim, [])
        if alt_basamaklar_kagit:
            with st.expander("🧩 Bu Öğrenme Çıktısının Süreç Bileşenleri", expanded=False):
                for basamak_k in alt_basamaklar_kagit:
                    st.markdown(f"- {basamak_k}")

        uploaded_files = st.file_uploader(
            "📷 Kâğıt / Defter Fotoğraflarını Yükleyin (Birden fazla seçebilirsiniz):", 
            type=["jpg", "png", "jpeg"],
            accept_multiple_files=True
        )
        
        if uploaded_files:
            st.caption(f"Toplam **{len(uploaded_files)}** adet çalışma sayfası yüklendi:")
            onizleme_cols = st.columns(min(3, len(uploaded_files)))
            for idx, dosya in enumerate(uploaded_files):
                with onizleme_cols[idx % 3]:
                    st.image(dosya, caption=f"Sayfa {idx + 1}", use_container_width=True)
            
    with col_result:
        st.subheader("🔍 Yapay Zekâ Süreç Değerlendirmesi")
        if uploaded_files and st.button(f"Kâğıtları Analiz Et ({len(uploaded_files)} Sayfa) ve Sürece Kaydet", type="primary", use_container_width=True):
            try:
                with st.spinner(f"Öğrencinin {len(uploaded_files)} sayfalık akıl yürütme adımları bütüncül olarak inceleniyor..."):
                    gorsel_listesi = []
                    for dosya in uploaded_files:
                        img = Image.open(dosya)
                        img.thumbnail((800, 800))
                        gorsel_listesi.append(img)
                    
                    prompt = f"""
TYMM uzmanısın. Sana sunulan {len(gorsel_listesi)} adet görseldeki {secilen_kademe} {secilen_ders} ({secilen_kazanim}) öğrenci çalışmasının tüm sayfalarını bütüncül olarak ve süreç bileşenlerini ({json.dumps(alt_basamaklar_kagit, ensure_ascii=False)}) dikkate alarak incele.
Eğer kâğıdın sağ üst köşesinde 'GRV-...' şeklinde bir Görev Takip Kodu görünüyorsa onu da tespit et ve 'tespit_edilen_gorev_kodu' alanına yaz (yoksa boş string "" bırak).
Sadece geçerli JSON döndür:
{{
  "tespit_edilen_gorev_kodu": "",
  "rubrik_duzeyi": "Başlangıç Düzeyi | Gelişmekte Olan | Yetkin Düzey | İleri Düzey",
  "dusunme_sureci_ozeti": "Tüm sayfaları kapsayan 2-3 kısa pedagojik cümle",
  "guclu_yonler": "1 kısa cümle",
  "kavram_yanilgisi_veya_hata": "Varsa tüm sayfalardaki yanılgılar yoksa 'Belirgin bir kavram yanılgısı tespit edilmedi'",
  "ogretmene_eylem_onerisi": "1 kısa CPA önerisi"
}}
"""
                    icerik_paketi = gorsel_listesi + [prompt]
                    
                    response = dayanikli_rotasyonlu_cagri(
                        model_adi='gemini-3.5-flash-lite', 
                        contents=icerik_paketi, 
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                            thinking_config=types.ThinkingConfig(thinking_level="LOW")
                        )
                    )
                    temiz_json = response.text.replace("```json", "").replace("```", "").strip()
                    result = json.loads(temiz_json)
                    veri_kaydet(
                        aktif_ogretmen, 
                        aktif_sube, 
                        ogrenci_adi, 
                        secilen_ders, 
                        secilen_kazanim, 
                        result.get("rubrik_duzeyi", "Belirsiz"), 
                        result.get("dusunme_sureci_ozeti", ""), 
                        result.get("guclu_yonler", ""), 
                        result.get("kavram_yanilgisi_veya_hata", ""), 
                        result.get("ogretmene_eylem_onerisi", "")
                    )
                    st.success(f"✅ {len(gorsel_listesi)} sayfalık TYMM Süreç Analizi tamamlandı ve {ogrenci_adi} adına kaydedildi!")
                    
                    # Kapalı Devre Görev Kodu Kontrolü
                    gorev_kodu_bulunan = str(result.get("tespit_edilen_gorev_kodu", "")).strip()
                    if not gorev_kodu_bulunan:
                        eslesme = re.search(r'GRV-[A-Z0-9]+-\d+', str(result))
                        if eslesme:
                            gorev_kodu_bulunan = eslesme.group(0)
                            
                    if gorev_kodu_bulunan and dongu_ustalik_guncelle(DB_PATH, gorev_kodu_bulunan):
                        st.balloons()
                        st.success(f"🏆 Kâğıt üzerindeki `{gorev_kodu_bulunan}` görev kodu tanındı ve öğrencinin Aralıklı Tekrar Döngüsünde **Ustalık Kazanıldı** olarak işaretlendi!")

                    st.markdown(f"**Rubrik Seviyesi:** `{result.get('rubrik_duzeyi')}`")
                    st.info(result.get("dusunme_sureci_ozeti"))
                    st.markdown(f"> **Öğretmen Destek Önerisi:** {result.get('ogretmene_eylem_onerisi')}")
            except Exception as e:
                st.error(f"Hata oluştu: {str(e)}")
