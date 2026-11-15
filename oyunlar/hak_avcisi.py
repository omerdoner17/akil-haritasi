import streamlit as st
import streamlit.components.v1 as components
import os

def hak_avcisi_oyunu_render(ogretmen_adi, sube_adi, ogrenciler):
    html_yolu = os.path.join(os.path.dirname(__file__), "hak_avcisi.html")
    if os.path.exists(html_yolu):
        with open(html_yolu, "r", encoding="utf-8") as f:
            html_icerik = f.read()
        components.html(html_icerik, height=620, scrolling=True)
    else:
        st.error("Lütfen 'hak_avcisi.html' dosyasını 'oyunlar' klasörünün içine kaydedin!")