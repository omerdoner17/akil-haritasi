import streamlit as st
import streamlit.components.v1 as components
import json
from urllib.parse import quote

def buyuk_harf_oyunu_render(ogretmen_adi, sube_adi, ogrenciler):
    ogrenci_listesi_js = ogrenciler if ogrenciler else [{"ad": "Örnek Öğrenci", "maskot": "🦁"}]
    ogrenciler_json = json.dumps(ogrenci_listesi_js, ensure_ascii=False)

    html_code = f"""
<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>TDK Büyük Harf Avcısı</title>
<style>
  * {{ box-sizing: border-box; user-select: none; font-family: 'Segoe UI', sans-serif; }}
  html, body {{ width: 100%; height: 100%; overflow: hidden; background: #f8fafc; color: #2c3e50; margin: 0; padding: 0; }}
  #fitRoot {{ width: 100%; transform-origin: top center; padding: 6px; display: flex; flex-direction: column; align-items: center; }}
  .top-bar{{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;background:#fff;border:2px solid #cbd5e1;border-radius:14px;padding:6px 14px;width:100%;max-width:1050px;margin-bottom:6px}}
  .student-box{{display:flex;align-items:center;gap:8px;font-weight:800;font-size:.95rem;color:#0284c7}}
  select.ogr-sel{{font:inherit;font-weight:700;padding:4px 10px;border-radius:8px;border:2px solid #0284c7;background:#f0f9ff;color:#0f172a;cursor:pointer}}
  .btn-spin{{background:#f59e0b;color:#fff;border:none;padding:6px 12px;border-radius:8px;font-weight:800;cursor:pointer}}
  .btn-save{{background:#10b981;color:#fff;border:none;padding:6px 14px;border-radius:8px;font-weight:800;cursor:pointer}}
  .btn-fs{{background:#475569;color:#fff;border:none;padding:6px 10px;border-radius:8px;font-weight:700;cursor:pointer}}
  .save-toast{{font-size:0.82rem;font-weight:700;color:#059669;display:none}}

  .control-panel {{ display: flex; justify-content: space-between; align-items: center; width: 100%; max-width: 1050px; background: #fff; padding: 8px 16px; border-radius: 12px; border: 1px solid #cbd5e1; margin-bottom: 8px; }}
  .score-badge {{ background: #e1f5fe; color: #0288d1; padding: 3px 10px; border-radius: 16px; font-weight: 800; }}
  .progress-bar-container {{ flex-grow: 1; max-width: 360px; height: 12px; background-color: #e2e8f0; border-radius: 8px; margin: 0 14px; overflow: hidden; }}
  .progress-bar {{ height: 100%; width: 0%; background: linear-gradient(90deg, #3498db, #2ecc71); transition: width 0.4s ease; }}
  .story-card {{ background: #fff; border-radius: 14px; padding: 14px 20px; width: 100%; max-width: 1050px; border: 1px solid #cbd5e1; line-height: 2.05; font-size: 1.05rem; margin-bottom: 8px; text-align: justify; height: 320px; overflow-y: auto; }}
  .word {{ display: inline-block; padding: 1px 4px; margin: 1px; border-radius: 5px; cursor: pointer; border: 1.5px solid transparent; background-color: #f8fafc; }}
  .word:hover {{ background-color: #e2e8f0; }}
  .word.found-error {{ background-color: #d4edda !important; border-color: #28a745 !important; color: #155724 !important; font-weight: 700; }}
  .word.wrong-click {{ background-color: #f8d7da !important; border-color: #dc3545 !important; }}
  .rule-box {{ width: 100%; max-width: 1050px; background: #fff9e6; border-left: 6px solid #f1c40f; padding: 10px 16px; border-radius: 10px; font-size: 0.95rem; color: #57606f; }}
  .rule-box.active-success {{ background: #e8f8f5; border-left-color: #2ecc71; color: #1e8449; font-weight: 600; }}
  .rule-box.active-error {{ background: #fdf2e9; border-left-color: #e67e22; color: #a04000; }}
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
<div class="control-panel">
  <div style="font-weight:800;color:#1e3799;font-size:14px">🔍 TDK Büyük Harf Avcısı — Bulunan Hata: <span class="score-badge"><span id="found-count">0</span> / 28</span></div>
  <div class="progress-bar-container"><div class="progress-bar" id="progress-bar"></div></div>
  <button style="background:#4b6584;color:#fff;border:none;padding:5px 10px;border-radius:8px;cursor:pointer;font-weight:700;font-size:12px" onclick="restartGame()">🔄 Sıfırla</button>
</div>
<div class="story-card" id="story-container"></div>
<div class="rule-box" id="rule-box">💡 İpucu: Metinde büyük/küçük harf yazımı yanlış olan kelimenin üzerine dokun!</div>
</div>
<script>
function autoFit(){{
  var r=document.getElementById('fitRoot'); r.style.transform='none';
  var h=r.scrollHeight, wh=window.innerHeight;
  if(h>wh && wh>100){{ var sc=(wh-8)/h; r.style.transform='scale('+sc+')'; }}
}}
window.addEventListener('resize',autoFit);
function toggleFS(){{if(!document.fullscreenElement)document.documentElement.requestFullscreen().catch(()=>{{}});else document.exitFullscreen();}}

var OGRENCILER = {ogrenciler_json};
var yanlisTiklamaSayisi = 0;
var sel = document.getElementById("ogrSelect");
OGRENCILER.forEach(function(o) {{ var opt = document.createElement("option"); opt.value = o.ad; opt.textContent = (o.maskot || "🦁") + " " + o.ad; sel.appendChild(opt); }});
document.getElementById("btnRandom").onclick = function() {{
    if (OGRENCILER.length > 1) {{ var sayac = 0; var iv = setInterval(function() {{ sel.selectedIndex = Math.floor(Math.random() * OGRENCILER.length); if (++sayac > 12) clearInterval(iv); }}, 60); }}
    yanlisTiklamaSayisi = 0;
}};

const storySentences = [
  [{{w:"Geçen"}},{{w:"yıl"}},{{id:1,w:"Ekim",correct:"ekim",isError:true,rule:"Belirli bir tarih belirtmeyen ay ve gün adları küçük harfle başlar."}},{{w:"ayının"}},{{w:"güneşli"}},{{w:"bir"}},{{w:"gününde"}},{{w:"Etili"}},{{w:"İlkokulu"}},{{w:"3-A"}},{{w:"sınıfında"}},{{w:"büyük"}},{{w:"bir"}},{{w:"heyecan"}},{{w:"vardı."}}],
  [{{w:"Öğretmenimiz"}},{{id:2,w:"ömer",correct:"Ömer",isError:true,rule:"İnsan isimleri (özel adlar) her zaman büyük harfle başlar."}},{{w:"Bey,"}},{{w:"sınıfa"}},{{w:"girer"}},{{w:"girmez"}},{{w:"hepimize"}},{{w:"güzel"}},{{w:"bir"}},{{w:"müjde"}},{{w:"verdi."}}],
  [{{w:"Yarın"}},{{w:"sabah"}},{{w:"Çanakkale"}},{{w:"ilimize"}},{{w:"bağlı"}},{{id:3,w:"çan",correct:"Çan",isError:true,rule:"İlçe, şehir ve il adları büyük harfle başlar."}},{{w:"ilçesine"}},{{w:"unutulmaz"}},{{w:"bir"}},{{w:"gezi"}},{{w:"düzenleyecektik."}}],
  [{{w:"Akşam"}},{{w:"eve"}},{{w:"vardığımda"}},{{w:"annem"}},{{id:4,w:"hanife",correct:"Hanife",isError:true,rule:"Kişi adları her zaman büyük harfle yazılır."}},{{w:"Hanım"}},{{w:"gezi"}},{{w:"çantamı"}},{{w:"özenle"}},{{w:"hazırladı."}}],
  [{{w:"Sabah"}},{{w:"erkenden"}},{{w:"okul"}},{{w:"bahçesinde"}},{{w:"toplandık"}},{{w:"ve"}},{{id:5,w:"Otobüsümüzü",correct:"otobüsümüzü",isError:true,rule:"Cümle ortasındaki cins isimler küçük harfle başlar."}},{{w:"beklemeye"}},{{w:"başladık."}}],
  [{{w:"Sınıf"}},{{w:"arkadaşım"}},{{id:6,w:"mehmet,",correct:"Mehmet,",isError:true,rule:"Özel şahıs isimleri büyük harfle başlar."}},{{w:"elinde"}},{{w:"tuttuğu"}},{{w:"gezi"}},{{w:"haritasını"}},{{w:"heyecanla"}},{{w:"inceliyordu."}}],
  [{{w:"Otobüsümüz"}},{{w:"hareket"}},{{w:"edince"}},{{w:"hep"}},{{w:"birlikte"}},{{w:"Türk"}},{{id:7,w:"Bayrağı",correct:"bayrağı",isError:true,rule:"Türk bayrağı tamlamasında 'bayrak' kelimesi küçük harfle yazılır."}},{{w:"sallayarak"}},{{w:"neşeyle"}},{{w:"el"}},{{w:"salladık."}}],
  [{{w:"Yolculuk"}},{{w:"sırasında"}},{{w:"öğretmenimiz"}},{{w:"bize"}},{{w:"Marmara"}},{{id:8,w:"bölgesi",correct:"Bölgesi",isError:true,rule:"Bölge adlarının her kelimesi büyük harfle başlar (Marmara Bölgesi)."}},{{w:"hakkında"}},{{w:"bilgiler"}},{{w:"verdi."}}],
  [{{w:"Yolun"}},{{w:"kenarında"}},{{w:"akmakta"}},{{w:"olan"}},{{id:9,w:"kazdağı",correct:"Kazdağı",isError:true,rule:"Dağ, dere, nehir ve göl gibi coğrafi isimler büyük harfle başlar."}},{{w:"Deresi"}},{{w:"manzarasını"}},{{w:"keyifle"}},{{w:"izledik."}}],
  [{{w:"Yolda"}},{{w:"kısa"}},{{w:"bir"}},{{w:"mola"}},{{w:"verdiğimizde"}},{{w:"minik"}},{{w:"bir"}},{{id:10,w:"Kedi",correct:"kedi",isError:true,rule:"Cümle içinde tür (cins) hayvan adları küçük harfle yazılır."}},{{w:"yanımıza"}},{{w:"sokuldu."}}],
  [{{w:"Tesisin"}},{{w:"bahçesindeki"}},{{id:11,w:"pamuk",correct:"Pamuk",isError:true,rule:"Hayvanlara verilen özel adlar büyük harfle başlar."}},{{w:"isimli"}},{{w:"sevimli"}},{{w:"köpeğe"}},{{w:"biraz"}},{{w:"yiyecek"}},{{w:"verdik."}}],
  [{{w:"İkinci"}},{{w:"durağımız"}},{{w:"olan"}},{{id:12,w:"Tarihi",correct:"tarihi",isError:true,rule:"Özel isim grubu oluşturmayan cins sıfatlar küçük harfle yazılır."}},{{w:"müze"}},{{w:"binasının"}},{{w:"önüne"}},{{w:"ulaştığımızda"}},{{w:"otobüsten"}},{{w:"indik."}}],
  [{{w:"Müzenin"}},{{w:"kapısında"}},{{w:"duran"}},{{id:13,w:"Görevliler",correct:"görevliler",isError:true,rule:"Cümle ortasındaki unvan olmayan tür isimleri küçük harfle başlar."}},{{w:"bizi"}},{{w:"çok"}},{{w:"sıcak"}},{{w:"bir"}},{{w:"şekilde"}},{{w:"karşıladılar."}}],
  [{{w:"Müzede"}},{{w:"sergilenen"}},{{id:14,w:"atatürk",correct:"Atatürk",isError:true,rule:"Tarihi şahsiyetlerin isimleri büyük harfle başlar."}},{{w:"görsellerini"}},{{w:"görünce"}},{{w:"hepimiz"}},{{w:"çok"}},{{w:"gururlandık."}}],
  [{{w:"Rehberimiz,"}},{{id:15,w:"türkiye",correct:"Türkiye",isError:true,rule:"Devlet ve ülke isimleri büyük harfle başlar (Türkiye Cumhuriyeti)."}},{{w:"Cumhuriyeti'nin"}},{{w:"kuruluş"}},{{w:"yıllarından"}},{{w:"önemli"}},{{w:"hikayeler"}},{{w:"anlattı."}}],
  [{{w:"Salondaki"}},{{w:"maketleri"}},{{w:"incelerken"}},{{w:"arkadaşım"}},{{w:"Zeynep"}},{{id:16,w:"De",correct:"de",isError:true,rule:"Ayrı yazılan 'de/da' bağlacı cümle ortasında küçük harfle yazılır."}},{{w:"not"}},{{w:"defterine"}},{{w:"yazılar"}},{{w:"yazıyordu."}}],
  [{{w:"Öğle"}},{{w:"yemeğinde"}},{{id:17,w:"çanakkale",correct:"Çanakkale",isError:true,rule:"Özel yer isimleri büyük harfle başlar."}},{{w:"seramiğinden"}},{{w:"yapılmış"}},{{w:"tabaklarda"}},{{w:"ikramlar"}},{{w:"sunuldu."}}],
  [{{w:"Yemekten"}},{{w:"sonra"}},{{id:18,w:"Öğretmenimiz",correct:"öğretmenimiz",isError:true,rule:"Cümle ortasında meslek belirten tür kelimeler küçük harfle başlar."}},{{w:"Ömer"}},{{w:"Bey"}},{{w:"bize"}},{{w:"rehberlik"}},{{w:"etmeye"}},{{w:"devam"}},{{w:"etti."}}],
  [{{w:"Gezi"}},{{w:"alanındaki"}},{{w:"büyük"}},{{w:"ağacın"}},{{w:"altında"}},{{id:19,w:"Oturup",correct:"oturup",isError:true,rule:"Cümle ortasındaki fiiller küçük harfle başlar."}},{{w:"biraz"}},{{w:"dinlendik."}}],
  [{{w:"Arkadaşımız"}},{{w:"Ali,"}},{{w:"yanında"}},{{w:"getirdiği"}},{{w:"kalimbalı"}},{{id:20,w:"Şarkı",correct:"şarkı",isError:true,rule:"Cins isimler cümle ortasında küçük harfle başlar."}},{{w:"kitabını"}},{{w:"açtı."}}],
  [{{w:"Öğretmenim"}},{{id:21,w:"canım",correct:"Canım",isError:true,rule:"Eser, şiir ve şarkı başlıklarının her kelimesi büyük harfle başlar."}},{{w:"Benim"}},{{w:"şarkısını"}},{{w:"hep"}},{{w:"birlikte"}},{{w:"neşeyle"}},{{w:"söyledik."}}],
  [{{w:"Dönüş"}},{{w:"yoluna"}},{{w:"geçmeden"}},{{w:"önce"}},{{w:"hatıra"}},{{id:22,w:"Fotoğrafı",correct:"fotoğrafı",isError:true,rule:"Cümle ortasında cins isimler küçük harfle yazılır."}},{{w:"çektirmek"}},{{w:"için"}},{{w:"toplandık."}}],
  [{{w:"Otobüse"}},{{w:"bindiğimizde"}},{{id:23,w:"Kasım",correct:"kasım",isError:true,rule:"Belirli bir sayısal tarih bildirmeyen ay adları küçük yazılır."}},{{w:"ayında"}},{{w:"yeni"}},{{w:"bir"}},{{w:"geziye"}},{{w:"gideceğimizi"}},{{w:"öğrendik."}}],
  [{{w:"Bütün"}},{{w:"yol"}},{{w:"boyunca"}},{{id:24,w:"istiklal",correct:"İstiklal",isError:true,rule:"Ulusal marş adlarının her kelimesi büyük harfle başlar (İstiklal Marşı)."}},{{w:"Marşı"}},{{w:"şiirimizi"}},{{w:"coşkuyla"}},{{w:"tekrarladık."}}],
  [{{w:"Akşamüstü"}},{{w:"okula"}},{{w:"ulaştığımızda"}},{{id:25,w:"Velilerimiz",correct:"velilerimiz",isError:true,rule:"Cümle ortasındaki cins isimler küçük harfle yazılır."}},{{w:"bizi"}},{{w:"kapıda"}},{{w:"bekliyordu."}}],
  [{{w:"Eve"}},{{w:"dönünce"}},{{w:"gezi"}},{{id:26,w:"Günlüğünü",correct:"günlüğünü",isError:true,rule:"Cümle ortasında cins isimler küçük harfle başlar."}},{{w:"anneme"}},{{w:"büyük"}},{{w:"bir"}},{{w:"heyecanla"}},{{w:"okudum."}}],
  [{{w:"Bu"}},{{w:"güzel"}},{{w:"gezide"}},{{id:27,w:"Vatan",correct:"vatan",isError:true,rule:"Cümle ortasındaki özel isim olmayan kavramlar küçük harfle yazılır."}},{{w:"sevgisini"}},{{w:"ve"}},{{w:"arkadaşlığı"}},{{w:"hissettik."}}],
  [{{w:"Unutulmaz"}},{{w:"anılarla"}},{{w:"dolu"}},{{w:"bu"}},{{w:"günü"}},{{id:28,w:"Hiçbir",correct:"hiçbir",isError:true,rule:"Cümle ortasında birleşik sıfatlar küçük harfle başlar."}},{{w:"zaman"}},{{w:"unutmayacağım."}}]
];
let foundErrors = new Set();
function renderStory() {{
  const container = document.getElementById('story-container'); container.innerHTML = '';
  storySentences.forEach((sentence) => {{
    const sSpan = document.createElement('span'); sSpan.style.marginRight = '5px';
    sentence.forEach((item) => {{
      const span = document.createElement('span'); span.className = 'word';
      span.textContent = (item.isError && foundErrors.has(item.id)) ? item.correct : item.w;
      if (item.isError && foundErrors.has(item.id)) span.classList.add('found-error');
      span.onclick = () => {{
        const ruleBox = document.getElementById('rule-box');
        if (item.isError) {{
          if (!foundErrors.has(item.id)) {{
            foundErrors.add(item.id); span.textContent = item.correct; span.classList.add('found-error');
            ruleBox.className = 'rule-box active-success';
            ruleBox.innerHTML = `✅ <b>Doğru!</b> (${{item.w}} ➔ <b>${{item.correct}}</b>) — ${{item.rule}}`;
            document.getElementById('found-count').textContent = foundErrors.size;
            document.getElementById('progress-bar').style.width = `${{(foundErrors.size / 28) * 100}}%`;
          }}
        }} else {{
          yanlisTiklamaSayisi++; span.classList.add('wrong-click');
          ruleBox.className = 'rule-box active-error';
          ruleBox.innerHTML = `❌ <b>"${{item.w}}"</b> kelimesinin yazımı doğru!`;
          setTimeout(() => span.classList.remove('wrong-click'), 400);
        }}
      }};
      sSpan.appendChild(span);
    }});
    container.appendChild(sSpan);
  }});
  setTimeout(autoFit, 60);
}}
function restartGame() {{ foundErrors.clear(); yanlisTiklamaSayisi = 0; document.getElementById('found-count').textContent = 0; document.getElementById('progress-bar').style.width = '0%'; renderStory(); }}
document.getElementById("btnSaveResult").onclick = function() {{
    var ogrAd = sel.value, bulunan = foundErrors.size;
    var durum = (bulunan >= 5 && yanlisTiklamaSayisi <= 1) ? "İleri Düzey" : (bulunan >= 3 ? "Yetkin Düzey" : "Gelişmekte Olan");
    var guclu = "TDK büyük/küçük harf yazım kurallarına göre " + bulunan + " adet yazım hatasını tespit etti.";
    var yanilgi = yanlisTiklamaSayisi > 2 ? "Doğru yazılmış özel isim veya cins isimleri hatalı sanarak işaretleme eğilimi görüldü." : "Belirgin bir kavram yanılgısı tespit edilmedi.";
    
    var params = new URLSearchParams({{
        cark_kaydet: "1",
        ogr: ogrAd,
        durum: durum,
        gorev: "TDK Büyük Harf Avcısı (" + bulunan + "/28 Hata)",
        model: "TDK Büyük Harf Avcısı",
        guclu: guclu,
        yanilgi: yanilgi,
        oneri: "Özel adlar, belirli tarihler ve eser adlarının yazımıyla ilgili kısa dikte çalışması yapılabilir.",
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
renderStory();
</script>
</body>
</html>
"""
    components.html(html_code, height=580, scrolling=False)
