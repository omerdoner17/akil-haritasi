import streamlit as st
import json
import streamlit.components.v1 as components
from pedagoji_motoru import analiz_uret

def saatler_oyunu_render(aktif_ogretmen, aktif_sube, ogrenciler_listesi):
    if not ogrenciler_listesi:
        st.warning(f"⚠️ **{aktif_sube}** sınıfında henüz kayıtlı öğrenci yok! Lütfen sol menüden '🏫 Sınıf Öğrenci Listesi' sekmesine geçip öğrencilerinizi ekleyin.")
        return

    etiketler = [f"{o['maskot']} {o['ad']}" for o in ogrenciler_listesi]
    temiz_isimler = [o['ad'].strip() for o in ogrenciler_listesi]
    
    json_etiketler = json.dumps(etiketler, ensure_ascii=False)
    json_temiz_isimler = json.dumps(temiz_isimler, ensure_ascii=False)

    js_veri = f"""
        let allLabels = {json_etiketler};
        let allPureNames = {json_temiz_isimler};
        let globalOgretmen = "{aktif_ogretmen}";
        let globalSube = "{aktif_sube}";
    """

    html_kod = """
    <!DOCTYPE html>
    <html lang="tr">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Zaman Yarışı - Akrep ile Yelkovan</title>
      <script src="https://cdn.tailwindcss.com"></script>
      <link rel="preconnect" href="https://fonts.googleapis.com">
      <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
      <link href="https://fonts.googleapis.com/css2?family=Baloo+2:wght@600;700;800&family=Fredoka:wght@500;600;700&display=swap" rel="stylesheet">

      <style>
        body {
          font-family: 'Fredoka', cursive, sans-serif;
          user-select: none;
          -webkit-user-select: none;
          transition: background 0.8s ease, color 0.8s ease;
          background: radial-gradient(circle at 50% 15%, #bae6fd 0%, #e0f2fe 45%, #fef3c7 100%);
          color: #0f172a;
          margin: 0;
          padding: 8px;
          display: flex;
          flex-direction: column;
          align-items: center;
        }
        .font-baloo { font-family: 'Baloo 2', cursive, sans-serif; }
        .fun-btn { transition: all 0.2s cubic-bezier(0.34, 1.56, 0.64, 1); }
        .fun-btn:hover { transform: translateY(-2px) scale(1.02); }
        .fun-btn:active { transform: translateY(1px) scale(0.97); }
        canvas { touch-action: none; display: block; margin: 0 auto; cursor: grab; }
        canvas:active { cursor: grabbing; }
        @keyframes pulseGlow {
          0%, 100% { box-shadow: 0 0 18px rgba(99, 102, 241, 0.35); }
          50% { box-shadow: 0 0 36px rgba(236, 72, 153, 0.6); }
        }
        .clock-glow { animation: pulseGlow 3s infinite ease-in-out; }
      </style>
    </head>
    <body>

      <!-- ÜST BİLGİ & ÖĞRENCİ SEÇİMİ -->
      <header class="w-full max-w-4xl mx-auto px-2 pt-1 flex flex-wrap items-center justify-between gap-2">
        <div class="flex items-center gap-2">
          <div class="w-10 h-10 rounded-2xl bg-gradient-to-br from-amber-400 to-orange-500 border-3 border-amber-600 shadow-md flex items-center justify-center text-xl animate-bounce">
            ⏰
          </div>
          <div>
            <h1 class="text-lg md:text-xl font-extrabold text-indigo-950 tracking-wide font-baloo">
              Zaman Yarışı: Akrep ile Yelkovan
            </h1>
            <p class="text-xs text-indigo-700 font-bold" id="studentHeader">
              ⭐ Tahtada: Yükleniyor...
            </p>
          </div>
        </div>

        <div class="flex items-center gap-2">
          <button id="btnNextStudent" class="fun-btn px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl shadow-md border-b-3 border-indigo-900 font-extrabold text-xs flex items-center gap-1">
            <span>🎯</span>
            <span>Sıradaki Öğrenci</span>
          </button>
        </div>
      </header>

      <!-- ORTA BÖLÜM: DİJİTAL SAAT + DEV ANALOG SAAT -->
      <main class="w-full max-w-4xl mx-auto px-2 my-2 flex flex-col items-center justify-center">
        
        <div class="w-full max-w-sm bg-slate-900 rounded-2xl p-2 shadow-xl border-3 border-indigo-400 mb-2 flex items-center justify-between text-white relative overflow-hidden">
          <div class="flex items-center">
            <button id="btnToggleBlind" class="fun-btn px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-yellow-300 rounded-xl text-xs font-bold border border-slate-700 flex items-center gap-1">
              <span id="blindIcon">👁️</span>
              <span id="blindText">Perdele</span>
            </button>
          </div>

          <div class="flex flex-col items-center justify-center flex-1">
            <span id="digitalClockMain" class="text-2xl font-extrabold font-mono text-emerald-400 tracking-wider">
              12:00
            </span>
            <div id="verbalClock" class="text-[11px] font-bold text-slate-300">
              Saat Tam 12!
            </div>
          </div>

          <div id="blindOverlay" class="absolute inset-0 bg-slate-900/95 backdrop-blur-sm flex items-center justify-center gap-2 text-yellow-300 font-bold text-xs hidden">
            <span>🔒 Ekran Gizlendi</span>
            <button id="btnQuickReveal" class="underline text-sky-400 ml-1">Aç</button>
          </div>

          <div class="text-right flex flex-col items-end">
            <span id="dayNightBadge" class="text-[10px] bg-amber-400 text-slate-900 font-extrabold px-2 py-0.5 rounded-full shadow">
              ☀️ Gündüz
            </span>
          </div>
        </div>

        <div id="clockContainer" class="relative p-2 bg-white rounded-[36px] shadow-xl border-4 border-indigo-300 clock-glow flex items-center justify-center">
          <canvas id="clockCanvas" width="440" height="440" class="rounded-[28px] w-[280px] h-[280px] sm:w-[340px] sm:h-[340px] md:w-[380px] md:h-[380px]"></canvas>
          
          <div id="badgeStatus" class="absolute top-2 left-1/2 -translate-x-1/2 bg-amber-400 text-amber-950 px-3 py-1 rounded-full font-black text-[11px] border-2 border-amber-600 shadow whitespace-nowrap z-10">
            🖐️ İbreleri tutarak saatleri kolayca ayarlayabilirsiniz!
          </div>
        </div>
      </main>

      <!-- ALT KONTROL BUTONLARI -->
      <footer class="w-full max-w-4xl mx-auto px-2 pb-2 flex flex-col gap-1.5">
        <div class="bg-white/95 backdrop-blur rounded-2xl p-2 shadow-xl border-2 border-indigo-200 grid grid-cols-2 sm:grid-cols-6 gap-1.5">
          <button id="btnToggleMissionMode" class="fun-btn py-1.5 px-1 bg-gradient-to-r from-purple-600 to-indigo-700 text-white rounded-xl shadow font-black text-xs border-b-3 border-indigo-900 flex flex-col items-center justify-center">
            <span>🎯 Soru Modu</span>
            <span class="text-[8px] text-yellow-300">Görev Ver</span>
          </button>

          <button id="btnRace" class="fun-btn py-1.5 px-1 bg-gradient-to-r from-red-500 to-orange-600 text-white rounded-xl shadow font-bold text-xs border-b-3 border-orange-800 flex flex-col items-center justify-center">
            <span>🏁 Hızlı Yarış</span>
            <span class="text-[8px] opacity-90">Sürekli Tur</span>
          </button>

          <button id="btnExact" class="fun-btn py-1.5 px-1 bg-gradient-to-r from-emerald-500 to-teal-600 text-white rounded-xl shadow font-bold text-xs border-b-3 border-teal-800 flex flex-col items-center justify-center">
            <span>🎯 Tam Saat</span>
            <span class="text-[8px] opacity-90">Yelkovan 12'de</span>
          </button>

          <button id="btnHalf" class="fun-btn py-1.5 px-1 bg-gradient-to-r from-amber-500 to-yellow-600 text-white rounded-xl shadow font-bold text-xs border-b-3 border-amber-800 flex flex-col items-center justify-center">
            <span>🥪 Buçuk</span>
            <span class="text-[8px] opacity-90">Yelkovan 6'da</span>
          </button>

          <button id="btnQuarterPast" class="fun-btn py-1.5 px-1 bg-gradient-to-r from-sky-500 to-blue-600 text-white rounded-xl shadow font-bold text-xs border-b-3 border-blue-800 flex flex-col items-center justify-center">
            <span>🍕 Çeyrek Geçe</span>
            <span class="text-[8px] opacity-90">:15 Geçiyor</span>
          </button>

          <button id="btnQuarterTo" class="fun-btn py-1.5 px-1 bg-gradient-to-r from-orange-500 to-rose-500 text-white rounded-xl shadow font-bold text-xs border-b-3 border-rose-800 flex flex-col items-center justify-center">
            <span>🔔 Çeyrek Var</span>
            <span class="text-[8px] opacity-90">:45 Kala</span>
          </button>
        </div>

        <!-- SORU & GÖREV ÇEKMECESİ -->
        <div id="gameMissionDrawer" class="hidden bg-gradient-to-r from-purple-900 via-indigo-900 to-slate-900 text-white p-3 rounded-2xl shadow-xl border-3 border-yellow-300">
          <div class="flex flex-wrap items-center justify-between gap-2">
            <div class="flex-1 min-w-[240px]">
              <div class="flex items-center justify-between mb-1">
                <div class="flex items-center gap-1.5">
                  <span class="text-xl animate-bounce">🎯</span>
                  <span id="targetStudentLabel" class="text-xs font-black uppercase text-yellow-300">ÖĞRENCİ GÖREVİ:</span>
                </div>
                <div class="flex items-center gap-2">
                  <span id="scoreBadge" class="bg-yellow-400 text-slate-950 px-2.5 py-0.5 rounded-full text-xs font-black shadow">Puan: 0 ⭐</span>
                  <button id="btnCloseMissionDrawer" class="text-slate-300 hover:text-white text-xs px-2 py-0.5 rounded bg-white/10">✖ Kapat</button>
                </div>
              </div>

              <div id="missionTargetText" class="text-xs sm:text-sm font-black text-yellow-200 bg-black/50 px-3 py-2 rounded-xl border border-white/20 text-center sm:text-left">
                "Saat 15:30 yap!"
              </div>
            </div>

            <div class="flex items-center gap-1.5 ml-auto">
              <button id="btnCheckMission" class="fun-btn px-3 py-2 bg-yellow-400 hover:bg-yellow-300 text-slate-950 rounded-xl font-black text-xs shadow border-b-3 border-yellow-600">
                Kontrol Et! ✅
              </button>
              <button id="btnShowSolution" class="fun-btn px-2.5 py-2 bg-emerald-500 hover:bg-emerald-600 text-white rounded-xl font-bold text-xs border-b-3 border-emerald-700">
                Çözüm ✨
              </button>
              <button id="btnNewMission" class="fun-btn px-2.5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl font-bold text-xs">
                Sıradaki ❯
              </button>
            </div>
          </div>
        </div>
      </footer>

      <script>
        """ + js_veri + """

        let currentIdx = 0;
        if (allLabels && allLabels.length > 0) {
          document.getElementById('studentHeader').textContent = "⭐ Tahtada: " + allLabels[0];
        }

        const canvas = document.getElementById('clockCanvas');
        const ctx = canvas.getContext('2d');
        const verbalClock = document.getElementById('verbalClock');
        const badgeStatus = document.getElementById('badgeStatus');
        const digitalClockMain = document.getElementById('digitalClockMain');
        const dayNightBadge = document.getElementById('dayNightBadge');
        const blindOverlay = document.getElementById('blindOverlay');
        const btnToggleBlind = document.getElementById('btnToggleBlind');
        const blindIcon = document.getElementById('blindIcon');
        const blindText = document.getElementById('blindText');

        let isBlindActive = false;
        function toggleBlind(forcedState) {
          isBlindActive = (typeof forcedState === 'boolean') ? forcedState : !isBlindActive;
          if (isBlindActive) {
            blindOverlay.classList.remove('hidden');
            blindIcon.textContent = "🙈"; blindText.textContent = "Göster";
          } else {
            blindOverlay.classList.add('hidden');
            blindIcon.textContent = "👁️"; blindText.textContent = "Perdele";
          }
        }
        btnToggleBlind.addEventListener('click', () => toggleBlind());
        document.getElementById('btnQuickReveal').addEventListener('click', () => toggleBlind(false));

        const CENTER_X = canvas.width / 2;
        const CENTER_Y = canvas.height / 2;
        const RADIUS = 180;

        let currentMinutesOfDay = 12 * 60;
        let mode = 'free';
        let isDragging = false;
        let activeHand = 'minute';
        let recordSaved = false;
        let gameScore = 0;
        let lastMinute = 0;

        function addMinutes(delta) {
          currentMinutesOfDay += delta;
          while (currentMinutesOfDay < 0) currentMinutesOfDay += 1440;
          currentMinutesOfDay = currentMinutesOfDay % 1440;
          drawClock();
          updateDisplays();
        }

        function setSpecificTime(hour24, minute) {
          currentMinutesOfDay = (((hour24 * 60 + minute) % 1440) + 1440) % 1440;
          drawClock();
          updateDisplays();
        }

        function getTimeInfo() {
          const norm = ((Math.round(currentMinutesOfDay) % 1440) + 1440) % 1440;
          const minute = norm % 60;
          const h24 = Math.floor(norm / 60);
          let h12 = h24 % 12;
          if (h12 === 0) h12 = 12;
          return { hour12: h12, hour24: h24, minute: minute, totalHoursFraction: (h24 % 12) + (minute / 60), isAfternoon: h24 >= 12 };
        }

        const SAYI_ISIMLERI = { 1: "Bir", 2: "İki", 3: "Üç", 4: "Dört", 5: "Beş", 6: "Altı", 7: "Yedi", 8: "Sekiz", 9: "Dokuz", 10: "On", 11: "On Bir", 12: "On İki" };
        const BELIRTME_EKLI = { 1: "Biri", 2: "İkiyi", 3: "Üçü", 4: "Dördü", 5: "Beşi", 6: "Altıyı", 7: "Yediyi", 8: "Sekizi", 9: "Dokuzu", 10: "Onu", 11: "On Biri", 12: "On İkiyi" };
        const YONELME_EKLI = { 1: "Bire", 2: "İkiye", 3: "Üçe", 4: "Dörde", 5: "Beşe", 6: "Altıya", 7: "Yediye", 8: "Sekize", 9: "Dokuza", 10: "Ona", 11: "On Bire", 12: "On İkiye" };

        function updateDisplays() {
          const { hour12, hour24, minute } = getTimeInfo();
          const nextH12 = (hour12 % 12) + 1;
          const pad = (n) => n.toString().padStart(2, '0');

          if (hour24 >= 6 && hour24 < 18) {
            document.body.classList.remove('night-theme');
            dayNightBadge.innerHTML = "<span>☀️</span> Gündüz";
          } else {
            document.body.classList.add('night-theme');
            dayNightBadge.innerHTML = "<span>🌙</span> Gece";
          }

          digitalClockMain.textContent = `${pad(hour24)}:${pad(minute)}`;

          let text = "";
          if (minute === 0) text = `Saat Tam ${SAYI_ISIMLERI[hour12]}!`;
          else if (minute === 15) text = `Saat ${BELIRTME_EKLI[hour12]} Çeyrek Geçiyor!`;
          else if (minute === 30) text = `Saat ${SAYI_ISIMLERI[hour12]} Buçuk!`;
          else if (minute === 45) text = `Saat ${YONELME_EKLI[nextH12]} Çeyrek Var!`;
          else if (minute < 30) text = `Saat ${BELIRTME_EKLI[hour12]} ${minute} Dk Geçiyor.`;
          else text = `Saat ${YONELME_EKLI[nextH12]} ${60 - minute} Dk Var.`;
          verbalClock.textContent = text;
        }

        function drawClock() {
          ctx.save();
          ctx.clearRect(0, 0, canvas.width, canvas.height);

          ctx.beginPath(); ctx.arc(CENTER_X, CENTER_Y, RADIUS + 22, 0, Math.PI * 2); ctx.fillStyle = '#312e81'; ctx.fill();
          ctx.beginPath(); ctx.arc(CENTER_X, CENTER_Y, RADIUS + 14, 0, Math.PI * 2); ctx.fillStyle = '#ffedd5'; ctx.fill();
          ctx.beginPath(); ctx.arc(CENTER_X, CENTER_Y, RADIUS - 14, 0, Math.PI * 2); ctx.fillStyle = '#ffffff'; ctx.fill();
          ctx.lineWidth = 3; ctx.strokeStyle = '#cbd5e1'; ctx.stroke();

          const innerRadius = RADIUS - 14;
          for (let m = 0; m < 60; m++) {
            let ang = (m * Math.PI) / 30 - Math.PI / 2;
            let isFive = m % 5 === 0;
            let r = isFive ? innerRadius - 7 : innerRadius - 4;
            ctx.beginPath(); ctx.arc(CENTER_X + Math.cos(ang) * r, CENTER_Y + Math.sin(ang) * r, isFive ? 3.5 : 1.4, 0, Math.PI * 2);
            ctx.fillStyle = isFive ? '#0284c7' : '#94a3b8'; ctx.fill();
          }

          for (let num = 1; num <= 12; num++) {
            let ang = (num * Math.PI) / 6 - Math.PI / 2;
            let pm = (num === 12) ? 24 : num + 12;
            let ox = CENTER_X + Math.cos(ang) * (RADIUS - 2);
            let oy = CENTER_Y + Math.sin(ang) * (RADIUS - 2);
            ctx.beginPath(); ctx.arc(ox, oy, 12, 0, Math.PI * 2); ctx.fillStyle = '#ea580c'; ctx.fill();
            ctx.font = 'bold 10px Fredoka'; ctx.fillStyle = '#ffffff'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
            ctx.fillText(pm.toString(), ox, oy);

            let x = CENTER_X + Math.cos(ang) * (innerRadius - 38);
            let y = CENTER_Y + Math.sin(ang) * (innerRadius - 38);
            ctx.beginPath(); ctx.arc(x, y, 17, 0, Math.PI * 2); ctx.fillStyle = '#f8fafc'; ctx.fill();
            ctx.font = 'bold 22px "Baloo 2", sans-serif'; ctx.fillStyle = '#0f172a'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
            ctx.fillText(num.toString(), x, y);
          }

          const { minAngle, hrAngle } = (function() {
            const { minute, totalHoursFraction } = getTimeInfo();
            return { minAngle: (minute / 60) * Math.PI * 2, hrAngle: (totalHoursFraction / 12) * Math.PI * 2 };
          })();

          drawHand(hrAngle, RADIUS * 0.46, 18, '#ef4444', 'AKREP');
          drawHand(minAngle, RADIUS * 0.70, 12, '#0284c7', 'YELKOVAN');

          ctx.beginPath(); ctx.arc(CENTER_X, CENTER_Y, 10, 0, Math.PI * 2); ctx.fillStyle = '#f59e0b'; ctx.fill(); ctx.stroke();
          ctx.restore();
        }

        function drawHand(angle, length, width, color, name) {
          ctx.save(); ctx.translate(CENTER_X, CENTER_Y); ctx.rotate(angle);
          ctx.beginPath(); ctx.moveTo(-width/2, 8); ctx.lineTo(width/2, 8); ctx.lineTo(width/3, -length + 14); ctx.lineTo(0, -length); ctx.lineTo(-width/3, -length + 14); ctx.closePath();
          ctx.fillStyle = color; ctx.fill(); ctx.lineWidth = 2.5; ctx.strokeStyle = '#1e293b'; ctx.stroke();
          ctx.font = 'bold 9px Fredoka'; ctx.fillStyle = '#ffffff'; ctx.textAlign = 'center'; ctx.fillText(name, 0, -length + 20);
          ctx.restore();
        }

        function getPointerPos(evt) {
          const rect = canvas.getBoundingClientRect();
          const scaleX = canvas.width / rect.width;
          const scaleY = canvas.height / rect.height;
          const clientX = evt.clientX || (evt.touches && evt.touches[0].clientX);
          const clientY = evt.clientY || (evt.touches && evt.touches[0].clientY);
          return {
            x: (clientX - rect.left) * scaleX - CENTER_X,
            y: (clientY - rect.top) * scaleY - CENTER_Y
          };
        }

        function onPointerDown(evt) {
          const pos = getPointerPos(evt);
          const dist = Math.hypot(pos.x, pos.y);
          if (dist > RADIUS + 15) return;
          isDragging = true;
          activeHand = (dist <= RADIUS * 0.55) ? 'hour' : 'minute';
          onPointerMove(evt);
        }

        function onPointerMove(evt) {
          if (!isDragging) return;
          const pos = getPointerPos(evt);
          let rad = Math.atan2(pos.x, -pos.y);
          let deg = rad * 180 / Math.PI;
          if (deg < 0) deg += 360;

          if (activeHand === 'minute') {
            let exactMin = Math.round(deg / 6) % 60;
            if (Math.abs(exactMin - lastMinute) > 40) {
              if (lastMinute > 50 && exactMin < 10) {
                currentMinutesOfDay += (60 - lastMinute) + exactMin;
              } else if (lastMinute < 10 && exactMin > 50) {
                currentMinutesOfDay -= (60 - exactMin) + lastMinute;
              }
            } else {
              let currentH24 = Math.floor(currentMinutesOfDay / 60);
              currentMinutesOfDay = currentH24 * 60 + exactMin;
            }
            lastMinute = exactMin;
          } else {
            let exactHour12 = Math.round(deg / 30) % 12;
            let currentM = currentMinutesOfDay % 60;
            let isPM = currentMinutesOfDay >= 720;
            let newH24 = exactHour12 + (isPM ? 12 : 0);
            currentMinutesOfDay = newH24 * 60 + currentM;
          }
          drawClock();
          updateDisplays();
        }

        function onPointerUp() { isDragging = false; }

        canvas.addEventListener('mousedown', onPointerDown);
        window.addEventListener('mousemove', onPointerMove);
        window.addEventListener('mouseup', onPointerUp);
        canvas.addEventListener('touchstart', (e) => { onPointerDown(e); e.preventDefault(); }, { passive: false });
        window.addEventListener('touchmove', (e) => { onPointerMove(e); e.preventDefault(); }, { passive: false });
        window.addEventListener('touchend', onPointerUp);

        document.getElementById('btnNextStudent').addEventListener('click', () => {
          currentIdx = (currentIdx + 1) % allLabels.length;
          document.getElementById('studentHeader').textContent = "⭐ Tahtada: " + allLabels[currentIdx];
          document.getElementById('targetStudentLabel').textContent = allLabels[currentIdx].toUpperCase() + " GÖREVİ:";
          recordSaved = false;
          badgeStatus.textContent = "⭐ Sıradaki öğrenci tahtaya kalktı!";
        });

        document.getElementById('btnRace').addEventListener('click', () => { mode = 'race'; toggleBlind(false); badgeStatus.textContent = "🏁 Hızlı Yarış aktif!"; });
        document.getElementById('btnExact').addEventListener('click', () => { mode = 'exact'; toggleBlind(false); setSpecificTime(getTimeInfo().hour12, 0); });
        document.getElementById('btnHalf').addEventListener('click', () => { mode = 'half'; toggleBlind(false); setSpecificTime(getTimeInfo().hour12, 30); });
        document.getElementById('btnQuarterPast').addEventListener('click', () => { mode = 'quarter_past'; toggleBlind(false); setSpecificTime(getTimeInfo().hour12, 15); });
        document.getElementById('btnQuarterTo').addEventListener('click', () => { mode = 'quarter_to'; toggleBlind(false); setSpecificTime(getTimeInfo().hour12, 45); });

        const MISSIONS = [
          { text: "Saat 09:00 (Sabah Dokuz) yap!", h24: 9, m: 0 },
          { text: "Saat 15:30 (Öğleden Sonra Üç Buçuk) yap!", h24: 15, m: 30 },
          { text: "Saat 14:15 (İkiyi Çeyrek Geçiyor) yap!", h24: 14, m: 15 },
          { text: "Saat 16:45 (Beşe Çeyrek Var) yap!", h24: 16, m: 45 },
          { text: "Saat 10:00 yap!", h24: 10, m: 0 },
          { text: "Saat 18:30 yap!", h24: 18, m: 30 }
        ];

        const gameMissionDrawer = document.getElementById('gameMissionDrawer');
        let missionActive = false;
        document.getElementById('btnToggleMissionMode').addEventListener('click', () => {
          missionActive = !missionActive;
          if (missionActive) {
            gameMissionDrawer.classList.remove('hidden');
            mode = 'game';
            pickNewMission();
            toggleBlind(true);
          } else {
            gameMissionDrawer.classList.add('hidden');
            toggleBlind(false);
          }
        });
        document.getElementById('btnCloseMissionDrawer').addEventListener('click', () => {
          missionActive = false; gameMissionDrawer.classList.add('hidden'); toggleBlind(false);
        });

        function pickNewMission() {
          currentMission = MISSIONS[Math.floor(Math.random() * MISSIONS.length)];
          document.getElementById('missionTargetText').textContent = `"${currentMission.text}"`;
        }
        document.getElementById('btnNewMission').addEventListener('click', pickNewMission);
        document.getElementById('btnShowSolution').addEventListener('click', () => {
          if (currentMission) setSpecificTime(currentMission.h24, currentMission.m);
          toggleBlind(false);
        });

        // KONTROL ET (MERKEZİ PEDAGOJİ MOTORU İLE ENTEGRE DOĞRU VE HATA ANALİZİ)
        document.getElementById('btnCheckMission').addEventListener('click', () => {
          if (!currentMission) return;
          const { hour24, minute } = getTimeInfo();
          let ogr = allPureNames[currentIdx];
          let isDogru = (hour24 === currentMission.h24 && minute === currentMission.m);

          if (isDogru) {
            gameScore += 10;
            document.getElementById('scoreBadge').textContent = `Puan: ${gameScore} ⭐`;
            badgeStatus.textContent = "🎉 TEBRİKLER! Görev tahtada doğru yapıldı ve gelişim kartına işlendi!";
          } else {
            badgeStatus.textContent = `❌ Yanlış! Şu an saat ${hour24}:${minute < 10 ? '0'+minute : minute}. Gelişim kartına formasyon uygun hata kaydı düştü!`;
          }

          if (!recordSaved) {
            recordSaved = true;
            let durum = isDogru ? "Yetkin Düzey" : "Gelişmekte Olan";
            let yanilgi = isDogru ? "Yok" : `Öğrencinin 24 saat döngüsünde (${currentMission.h24}:${currentMission.m}) hedefi kaçırıp (${hour24}:${minute}) ayarladığı, zaman dilimini algılamada zorlandığı gözlendi.`;
            let oneri = isDogru ? "Zaman okuma ve saat modelleme becerisi tam; problem kurma aşamasına geçilebilir." : "CPA yaklaşımına göre fiziksel saat modelleriyle 24 saatlik zaman dilimleri tekrarlanmalı.";
            let guclu = isDogru ? "Analog saat üzerinde zamanı hatasız modelledi." : "Materyali kullanma ve deneme yapma motivasyonu yüksek.";

            let url = "http://127.0.0.1:8765/cark_kaydet?ogr=" + encodeURIComponent(ogr) +
                      "&durum=" + encodeURIComponent(durum) +
                      "&gorev=" + encodeURIComponent(currentMission.text) +
                      "&model=" + encodeURIComponent("Zaman Yarışı Analog Saat") +
                      "&yanilgi=" + encodeURIComponent(yanilgi) +
                      "&oneri=" + encodeURIComponent(oneri) +
                      "&guclu=" + encodeURIComponent(guclu) +
                      "&ogretmen=" + encodeURIComponent(globalOgretmen) +
                      "&sube=" + encodeURIComponent(globalSube) +
                      "&t=" + Date.now();
            let ping = new Image(); ping.src = url;
          }
        });

        setInterval(() => {
          if (mode === 'race') {
            addMinutes(1);
          }
        }, 100);

        window.onload = function() {
          drawClock();
          updateDisplays();
        };
      </script>
    </body>
    </html>
    """

    components.html(html_kod, height=860)