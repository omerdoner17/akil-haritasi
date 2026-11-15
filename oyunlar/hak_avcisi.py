import streamlit as st
import streamlit.components.v1 as components
import os
import json

def hak_avcisi_oyunu_render(ogretmen_adi, sube_adi, ogrenciler):
    html_yolu = os.path.join(os.path.dirname(__file__), "hak_avcisi.html")
    if os.path.exists(html_yolu):
        with open(html_yolu, "r", encoding="utf-8") as f:
            html_icerik = f.read()

        ogrenciler_json = json.dumps(ogrenciler or [], ensure_ascii=False)
        bulut_kopru_js = f"""
        <script>
        (function() {{
            const OGR_LIST = {ogrenciler_json};
            const OGRETMEN = {json.dumps(str(ogretmen_adi), ensure_ascii=False)};
            const SUBE = {json.dumps(str(sube_adi), ensure_ascii=False)};

            function bulutaGonder(rawUrl) {{
                try {{
                    const u = new URL(rawUrl, window.location.origin);
                    const p = new URLSearchParams(u.search);
                    p.set("cark_kaydet", "1");
                    if (!p.get("ogretmen")) p.set("ogretmen", OGRETMEN);
                    if (!p.get("sube")) p.set("sube", SUBE);
                    if (!p.get("ogr") && OGR_LIST.length > 0) p.set("ogr", OGR_LIST[0].ad);
                    p.set("t", Date.now().toString());

                    const targetWin = window.parent || window;
                    const baseUrl = targetWin.location.href.split("?")[0];
                    targetWin.history.replaceState(null, "", baseUrl + "?" + p.toString());
                    fetch(baseUrl + "?" + p.toString(), {{ mode: "no-cors", cache: "no-store" }}).catch(() => {{}});
                    setTimeout(() => {{
                        try {{ targetWin.location.reload(); }} catch(e) {{}}
                    }}, 800);
                }} catch (e) {{}}
            }}

            const origFetch = window.fetch;
            window.fetch = function(input, init) {{
                const urlStr = typeof input === "string" ? input : (input && input.url ? input.url : "");
                if (urlStr.includes("cark_kaydet")) {{
                    bulutaGonder(urlStr);
                    return Promise.resolve(new Response("ok"));
                }}
                return origFetch.apply(this, arguments);
            }};

            const origImgSrc = Object.getOwnPropertyDescriptor(Image.prototype, "src");
            if (origImgSrc && origImgSrc.set) {{
                Object.defineProperty(Image.prototype, "src", {{
                    set: function(val) {{
                        if (typeof val === "string" && val.includes("cark_kaydet")) {{
                            bulutaGonder(val);
                            return;
                        }}
                        origImgSrc.set.call(this, val);
                    }}
                }});
            }}
        }})();
        </script>
        """
        if "</body>" in html_icerik:
            html_icerik = html_icerik.replace("</body>", bulut_kopru_js + "\n</body>")
        else:
            html_icerik += bulut_kopru_js

        components.html(html_icerik, height=620, scrolling=True)
    else:
        st.error("Lütfen 'hak_avcisi.html' dosyasını 'oyunlar' klasörünün içine kaydedin!")
