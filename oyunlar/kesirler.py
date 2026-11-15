import streamlit as st
import json
import streamlit.components.v1 as components

def kesirler_oyunu_render(aktif_ogretmen, aktif_sube, ogrenciler_listesi):
    if not ogrenciler_listesi:
        st.warning(f"⚠️ **{aktif_sube}** sınıfında henüz kayıtlı öğrenci yok! Lütfen sol menüden '🏫 Sınıf Öğrenci Listesi' sekmesine geçip öğrencilerinizi ekleyin.")
        return

    etiketler = [f"{o['maskot']} {o['ad']}" for o in ogrenciler_listesi]
    temiz_isimler = [o['ad'].strip() for o in ogrenciler_listesi]
    
    json_etiketler = json.dumps(etiketler, ensure_ascii=False)
    json_temiz_isimler = json.dumps(temiz_isimler, ensure_ascii=False)

    html_kod = """
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>
        <style>
            body {
                margin: 0; padding: 10px 0; display: flex; flex-direction: column;
                align-items: center; justify-content: center; font-family: 'Segoe UI', Tahoma, sans-serif;
                background: transparent; user-select: none; color: #1e293b;
            }
            .top-bar {
                display: flex; align-items: center; justify-content: space-between;
                width: 520px; margin-bottom: 14px;
            }
            .badge {
                font-size: 16px; font-weight: 800; color: #0284c7; background: #ffffff;
                padding: 8px 20px; border-radius: 24px; border: 2px solid #bae6fd;
            }
            .reset-btn {
                background: #ffffff; color: #475569; border: 2px solid #cbd5e1;
                border-radius: 20px; padding: 8px 18px; font-size: 14px; font-weight: 700;
                cursor: pointer; transition: border-color 0.15s, color 0.15s;
            }
            .reset-btn:hover { border-color: #0284c7; color: #0284c7; }
            .wheel-container {
                position: relative; width: 480px; height: 480px;
                display: flex; align-items: center; justify-content: center;
            }
            canvas {
                border-radius: 50%; cursor: pointer;
                border: 6px solid #ffffff;
                box-shadow: 0 10px 25px rgba(15, 23, 42, 0.12);
                will-change: transform;
                transform: translateZ(0);
            }
            .center-btn {
                position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
                width: 108px; height: 108px; border-radius: 50%;
                background: radial-gradient(circle, #ef4444 30%, #dc2626 70%, #991b1b 100%);
                border: 5px solid #ffffff; box-shadow: 0 6px 18px rgba(220,38,38,0.4);
                display: flex; flex-direction: column; align-items: center; justify-content: center;
                cursor: pointer; z-index: 20; transition: transform 0.12s;
            }
            .center-btn:active { transform: translate(-50%, -50%) scale(0.94); }
            .pointer {
                position: absolute; top: 50%; right: -6px; transform: translateY(-50%);
                width: 0; height: 0; border-top: 20px solid transparent;
                border-bottom: 20px solid transparent; border-right: 38px solid #f59e0b;
                z-index: 10;
            }
            #questionModal {
                display: none; flex-direction: column; align-items: center; justify-content: center;
                width: 650px; background: #ffffff; border: 3px solid #0284c7;
                border-radius: 28px; padding: 26px; box-shadow: 0 12px 32px rgba(0,0,0,0.1);
            }
            .student-badge {
                font-size: 28px; font-weight: 900; color: #0284c7; margin: 0 0 8px 0;
            }
            .task-banner {
                background: #f0fdf4; border: 2px solid #10b981; padding: 10px 28px;
                border-radius: 16px; font-size: 26px; font-weight: 900; color: #047857;
                margin-bottom: 14px;
            }
            .model-switcher {
                display: flex; gap: 10px; margin-bottom: 12px;
            }
            .switch-btn {
                padding: 6px 16px; border-radius: 14px; border: 2px solid #cbd5e1;
                background: #f8fafc; font-weight: 700; cursor: pointer; font-size: 14px;
            }
            .switch-btn.active {
                border-color: #0284c7; background: #e0f2fe; color: #0284c7;
            }
            .fraction-bar {
                display: flex; width: 540px; height: 90px; border: 4px solid #0f172a;
                border-radius: 14px; overflow: hidden; margin: 10px 0; background: #f8fafc;
            }
            .fraction-slice {
                flex: 1; border-right: 2px dashed #94a3b8; cursor: pointer;
                display: flex; flex-direction: column; align-items: center; justify-content: center;
                font-size: 18px; font-weight: 800; color: #334155; transition: background 0.12s;
            }
            .fraction-slice:last-child { border-right: none; }
            .fraction-slice.selected { background: #0284c7 !important; color: #ffffff; }
            svg.pizza-svg { width: 220px; height: 220px; cursor: pointer; margin: 6px 0; }
            path.pizza-slice { fill: #f8fafc; stroke: #0f172a; stroke-width: 3; transition: fill 0.12s; }
            path.pizza-slice.selected { fill: #10b981 !important; }
            .btn-row {
                display: flex; gap: 12px; align-items: center; margin-top: 8px;
            }
            .submit-btn {
                padding: 13px 38px; font-size: 18px; font-weight: 900; color: #ffffff;
                background: linear-gradient(135deg, #10b981, #059669); border: none;
                border-radius: 30px; cursor: pointer;
            }
            .submit-btn:active { transform: scale(0.97); }
            .skip-btn {
                padding: 12px 22px; font-size: 15px; font-weight: 700; color: #475569;
                background: #f1f5f9; border: 2px solid #cbd5e1; border-radius: 30px; cursor: pointer;
            }
            .skip-btn:hover { border-color: #0284c7; color: #0284c7; }
            @keyframes shake {
                0%, 100% { transform: translateX(0); }
                25% { transform: translateX(-8px); }
                75% { transform: translateX(8px); }
            }
            .shake-anim { animation: shake 0.3s ease-in-out; }
        </style>
    </head>
    <body>
        <div id="wheelScreen">
            <div class="top-bar">
                <span class="badge" id="kalanSayac">Kalan Öğrenci: __SAYI__ / __SAYI__</span>
                <button class="reset-btn" id="turuSifirlaBtn">🔄 Turu Sıfırla</button>
            </div>
            <div class="wheel-container">
                <canvas id="wheelCanvas" width="460" height="460"></canvas>
                <div class="pointer"></div>
                <div class="center-btn" id="ortaCevirBtn">
                    <span style="font-size:26px;">🎯</span>
                    <span style="font-size:16px; font-weight:900; color:#ffffff; letter-spacing:0.5px;">ÇEVİR</span>
                </div>
            </div>
        </div>

        <div id="questionModal">
            <div class="student-badge" id="secilenOgrenciBaslik"></div>
            <div class="task-banner" id="gorevMetni"></div>
            
            <div class="model-switcher">
                <button class="switch-btn active" id="btnBarModel">📏 Kesir Çubuğu</button>
                <button class="switch-btn" id="btnPizzaModel">🍕 Daire (Pizza) Modeli</button>
            </div>

            <div class="fraction-bar" id="barContainer"></div>
            <div id="pizzaContainer" style="display:none;"></div>

            <div style="font-size:19px; font-weight:800; color:#0f172a; margin:8px 0;">
                Boyanan Parça: <span id="boyananSayi" style="color:#0284c7;">0</span> / <span id="toplamPayda">0</span>
            </div>

            <div class="btn-row">
                <button class="submit-btn" id="onaylaBtn">✅ MODELİ ONAYLA</button>
                <button class="skip-btn" id="gecBtn">➡️ Sıradaki Öğrenciye Geç</button>
            </div>
            <div id="sonucMesaji" style="margin-top:12px; font-size:17px; font-weight:800; min-height:28px; text-align:center;"></div>
        </div>

        <script>
            let allLabels = __ETIKETLER__;
            let allPureNames = __ISIMLER__;
            let globalOgretmen = __OGRETMEN__;
            let globalSube = __SUBE__;
            let remainingIndices = allLabels.map((_, idx) => idx);

            const canvas = document.getElementById("wheelCanvas");
            const ctx = canvas.getContext("2d");
            const palette = ["#38bdf8", "#34d399", "#fb923c", "#a78bfa", "#f472b6", "#22d3ee", "#facc15", "#2dd4bf"];
            
            let currentAngleDeg = 0;
            let isSpinning = false;
            let activePureName = "";
            let activeLabel = "";
            let targetPay = 1;
            let targetPayda = 4;
            let activeModel = "Kesir Çubuğu";
            let selectedParts = new Set();
            let mistakeCount = 0;

            function drawWheelStatic() {
                ctx.clearRect(0, 0, 460, 460);
                const count = remainingIndices.length;
                if (count === 0) return;
                const arc = (2 * Math.PI) / count;
                for (let i = 0; i < count; i++) {
                    const angle = i * arc;
                    const realIdx = remainingIndices[i];
                    ctx.fillStyle = palette[realIdx % palette.length];
                    ctx.beginPath();
                    ctx.arc(230, 230, 224, angle, angle + arc, false);
                    ctx.lineTo(230, 230);
                    ctx.fill();

                    ctx.save();
                    ctx.fillStyle = "#0f172a";
                    ctx.font = "bold 16px sans-serif";
                    ctx.translate(230 + Math.cos(angle + arc / 2) * 145, 230 + Math.sin(angle + arc / 2) * 145);
                    ctx.rotate(angle + arc / 2);
                    const txt = allLabels[realIdx];
                    ctx.fillText(txt, -ctx.measureText(txt).width / 2, 6);
                    ctx.restore();
                }
            }
            drawWheelStatic();

            function returnToWheelScreen() {
                document.getElementById("questionModal").style.display = "none";
                document.getElementById("wheelScreen").style.display = "flex";
                document.getElementById("wheelScreen").style.flexDirection = "column";
                document.getElementById("wheelScreen").style.alignItems = "center";
                if (remainingIndices.length === 0) {
                    remainingIndices = allLabels.map((_, idx) => idx);
                    document.getElementById("kalanSayac").innerText = "Kalan Öğrenci: " + remainingIndices.length + " / " + allLabels.length;
                }
                canvas.style.transition = "none";
                currentAngleDeg = currentAngleDeg % 360;
                canvas.style.transform = `rotate(${currentAngleDeg}deg)`;
                drawWheelStatic();
            }

            document.getElementById("gecBtn").onclick = returnToWheelScreen;

            function spinNow() {
                if (isSpinning) return;
                if (remainingIndices.length === 0) {
                    remainingIndices = allLabels.map((_, idx) => idx);
                    drawWheelStatic();
                }
                isSpinning = true;
                const count = remainingIndices.length;
                const chosenPos = Math.floor(Math.random() * count);
                const arcDeg = 360 / count;

                const desiredEndDeg = 360 - (chosenPos * arcDeg + arcDeg / 2);
                const currentMod = ((currentAngleDeg % 360) + 360) % 360;
                let delta = desiredEndDeg - currentMod;
                if (delta < 0) delta += 360;

                const totalSpinDeg = currentAngleDeg + (5 * 360) + delta;
                currentAngleDeg = totalSpinDeg;

                canvas.style.transition = "transform 1.4s cubic-bezier(0.15, 0.85, 0.25, 1)";
                canvas.style.transform = `rotate(${totalSpinDeg}deg)`;

                setTimeout(() => {
                    isSpinning = false;
                    const winnerRealIdx = remainingIndices[chosenPos];
                    activeLabel = allLabels[winnerRealIdx];
                    activePureName = allPureNames[winnerRealIdx];

                    remainingIndices.splice(chosenPos, 1);
                    document.getElementById("kalanSayac").innerText = "Kalan Öğrenci: " + remainingIndices.length + " / " + allLabels.length;

                    confetti({ particleCount: 90, spread: 70 });
                    setTimeout(() => showQuestionModal(), 550);
                }, 1450);
            }

            document.getElementById("ortaCevirBtn").onclick = spinNow;
            canvas.onclick = spinNow;

            document.getElementById("turuSifirlaBtn").onclick = () => {
                remainingIndices = allLabels.map((_, idx) => idx);
                currentAngleDeg = 0;
                canvas.style.transition = "none";
                canvas.style.transform = "rotate(0deg)";
                document.getElementById("kalanSayac").innerText = "Kalan Öğrenci: " + remainingIndices.length + " / " + allLabels.length;
                drawWheelStatic();
            };

            function renderModels() {
                document.getElementById("boyananSayi").innerText = selectedParts.size;
                document.getElementById("toplamPayda").innerText = targetPayda;

                const barCont = document.getElementById("barContainer");
                const pizzaCont = document.getElementById("pizzaContainer");

                if (activeModel === "Kesir Çubuğu") {
                    barCont.style.display = "flex";
                    pizzaCont.style.display = "none";
                    barCont.innerHTML = "";
                    for (let i = 0; i < targetPayda; i++) {
                        const d = document.createElement("div");
                        d.className = "fraction-slice" + (selectedParts.has(i) ? " selected" : "");
                        d.innerHTML = `<div>1/${targetPayda}</div><div style="font-size:11px; opacity:0.8;">${i+1}. Parça</div>`;
                        d.onclick = () => {
                            if (selectedParts.has(i)) selectedParts.delete(i);
                            else selectedParts.add(i);
                            renderModels();
                        };
                        barCont.appendChild(d);
                    }
                } else {
                    barCont.style.display = "none";
                    pizzaCont.style.display = "flex";
                    pizzaCont.innerHTML = "";
                    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
                    svg.setAttribute("class", "pizza-svg");
                    svg.setAttribute("viewBox", "0 0 230 230");
                    const sliceA = (2 * Math.PI) / targetPayda;
                    for (let i = 0; i < targetPayda; i++) {
                        const sA = i * sliceA - Math.PI / 2;
                        const eA = sA + sliceA;
                        const x1 = 115 + 102 * Math.cos(sA), y1 = 115 + 102 * Math.sin(sA);
                        const x2 = 115 + 102 * Math.cos(eA), y2 = 115 + 102 * Math.sin(eA);
                        const large = (eA - sA) > Math.PI ? 1 : 0;
                        const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
                        path.setAttribute("d", `M 115 115 L ${x1} ${y1} A 102 102 0 ${large} 1 ${x2} ${y2} Z`);
                        path.setAttribute("class", "pizza-slice" + (selectedParts.has(i) ? " selected" : ""));
                        path.onclick = () => {
                            if (selectedParts.has(i)) selectedParts.delete(i);
                            else selectedParts.add(i);
                            renderModels();
                        };
                        svg.appendChild(path);
                    }
                    pizzaCont.appendChild(svg);
                }
            }

            document.getElementById("btnBarModel").onclick = () => {
                activeModel = "Kesir Çubuğu";
                document.getElementById("btnBarModel").classList.add("active");
                document.getElementById("btnPizzaModel").classList.remove("active");
                renderModels();
            };

            document.getElementById("btnPizzaModel").onclick = () => {
                activeModel = "Daire Modeli";
                document.getElementById("btnPizzaModel").classList.add("active");
                document.getElementById("btnBarModel").classList.remove("active");
                renderModels();
            };

            function showQuestionModal() {
                selectedParts.clear();
                mistakeCount = 0;
                targetPayda = [2, 3, 4, 5, 6, 8, 10][Math.floor(Math.random() * 7)];
                targetPay = Math.floor(Math.random() * (targetPayda - 1)) + 1;
                activeModel = Math.random() > 0.5 ? "Kesir Çubuğu" : "Daire Modeli";

                document.getElementById("btnBarModel").classList.toggle("active", activeModel === "Kesir Çubuğu");
                document.getElementById("btnPizzaModel").classList.toggle("active", activeModel === "Daire Modeli");

                document.getElementById("wheelScreen").style.display = "none";
                document.getElementById("questionModal").style.display = "flex";
                document.getElementById("onaylaBtn").style.display = "inline-block";
                document.getElementById("secilenOgrenciBaslik").innerText = "⭐ Tahtada: " + activeLabel;
                document.getElementById("gorevMetni").innerText = "Görev: " + targetPay + " / " + targetPayda + " Kesrini Modelle";
                document.getElementById("sonucMesaji").innerText = "";

                renderModels();
            }

            function veritabaninaOtomatikKaydet(ogrenci, durum, gorev, model, yanilgi, oneri, guclu) {
                const params = new URLSearchParams({
                    cark_kaydet: "1",
                    ogr: ogrenci,
                    durum: durum,
                    gorev: gorev,
                    model: model,
                    yanilgi: yanilgi,
                    oneri: oneri,
                    guclu: guclu,
                    ogretmen: globalOgretmen,
                    sube: globalSube,
                    t: Date.now().toString()
                });
                try {
                    const targetWin = window.parent || window;
                    const baseUrl = targetWin.location.href.split("?")[0];
                    targetWin.history.replaceState(null, "", baseUrl + "?" + params.toString());
                    fetch(baseUrl + "?" + params.toString(), { mode: "no-cors", cache: "no-store" }).catch(() => {});
                } catch (e) {}
            }

            document.getElementById("onaylaBtn").onclick = () => {
                const boyanan = selectedParts.size;
                const gorevStr = targetPay + "/" + targetPayda;
                const msgBox = document.getElementById("sonucMesaji");
                const modalBox = document.getElementById("questionModal");

                if (boyanan === targetPay) {
                    document.getElementById("onaylaBtn").style.display = "none";
                    const durum = mistakeCount === 0 ? "Yetkin Düzey" : "Gelişmekte Olan";
                    const yanilgi = mistakeCount === 0 
                        ? "Yok (İlk denemede hatasız modelledi)" 
                        : (mistakeCount + " hatalı denemeden sonra ipucuyla doğru sonuca ulaştı.");
                    const oneri = mistakeCount === 0 
                        ? "Kesir modelleme kavrayışı tam; sayı doğrusunda basit ve bileşik kesir geçişleriyle zenginleştirilebilir." 
                        : "Hatasını yönlendirmeyle fark edip düzeltti; öz-denetimi olumlu. Kavramı pekiştirmek için farklı geometrik modeller sunulabilir.";
                    const guclu = gorevStr + " kesrinin birim parça sayısını ve bütünle ilişkisini " + activeModel + " üzerinde başarıyla kurdu.";

                    veritabaninaOtomatikKaydet(activePureName, durum, gorevStr, activeModel, yanilgi, oneri, guclu);

                    confetti({ particleCount: 110, spread: 75 });
                    msgBox.style.color = "#059669";
                    msgBox.innerText = "🎉 HARİKA! " + activePureName + " doğru modelledi ve karnesine işlendi!";

                    setTimeout(() => {
                        try {
                            const targetWin = window.parent || window;
                            targetWin.location.reload();
                        } catch (e) {
                            returnToWheelScreen();
                        }
                    }, 1100);

                } else {
                    mistakeCount++;
                    const durum = "Gelişmekte Olan";
                    const hata = boyanan < targetPay
                        ? "Eksik parça boyama (Hedef: " + gorevStr + ", Boyanan: " + boyanan + "/" + targetPayda + ")"
                        : "Fazla parça boyama (Hedef: " + gorevStr + ", Boyanan: " + boyanan + "/" + targetPayda + ")";
                    const oneri = boyanan < targetPay
                        ? "Pay miktarını eksik saydı; boyanması gereken parça sayısı ile pay arasındaki birebir eşleme somut kartlarla pekiştirilmeli."
                        : "İstenen miktardan fazla parça boyadı; boyama yaparken sesli sayma stratejisi ve 'dur-kontrol et' adımı kazandırılmalı.";
                    const guclu = "Tahtada aktif görev aldı, " + activeModel + " üzerinde parçaları yerleştirmede istekli davrandı.";

                    veritabaninaOtomatikKaydet(activePureName, durum, gorevStr, activeModel, hata, oneri, guclu);

                    modalBox.classList.remove("shake-anim");
                    void modalBox.offsetWidth;
                    modalBox.classList.add("shake-anim");

                    msgBox.style.color = "#dc2626";
                    if (boyanan < targetPay) {
                        msgBox.innerText = "⚠️ Eksik parça boyadın (" + boyanan + "/" + targetPayda + ")! İpucu: Pay kadar (" + targetPay + " parça) boyamalısın. Tekrar dene!";
                    } else {
                        msgBox.innerText = "⚠️ Fazla parça boyadın (" + boyanan + "/" + targetPayda + ")! İpucu: Sadece " + targetPay + " parça boyamalısın. Düzeltip tekrar onayla!";
                    }
                }
            };
        </script>
    </body>
    </html>
    """
    html_kod = (
        html_kod
        .replace("__SAYI__", str(len(etiketler)))
        .replace("__ETIKETLER__", json_etiketler)
        .replace("__ISIMLER__", json_temiz_isimler)
        .replace("__OGRETMEN__", json.dumps(str(aktif_ogretmen), ensure_ascii=False))
        .replace("__SUBE__", json.dumps(str(aktif_sube), ensure_ascii=False))
    )
    components.html(html_kod, height=640)
