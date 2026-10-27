/* ==========================================================================
   Mahyar Compressor PRO v2.0 — Interactive Engine, Creative Tactical Buttons,
   Pause/Resume, 4 Neon Themes, FPS Limiter & Mouse-Reactive Nebula
   ========================================================================== */

(function () {
  'use strict';

  // --------------------------------------------------------------------------
  // 1. BILINGUAL DICTIONARY (FA / EN)
  // --------------------------------------------------------------------------
  let LANG = 'fa';

  const THEMES = [
    {
      nameFa: 'سایبر نئون (بنفش/فیروزه‌ای)',
      nameEn: 'Cyber Ultraviolet',
      c1: '168, 85, 247',
      c2: '139, 92, 246',
      c3: '236, 72, 153',
      c4: '34, 211, 238',
      hex: '#22d3ee'
    },
    {
      nameFa: 'ماتریکس زمردی (سبز/فیروزه‌ای)',
      nameEn: 'Matrix Emerald',
      c1: '52, 211, 153',
      c2: '16, 185, 129',
      c3: '34, 211, 238',
      c4: '56, 189, 248',
      hex: '#34d399'
    },
    {
      nameFa: 'اوردرایو سرخ (قرمز/مگنتا)',
      nameEn: 'Crimson Overdrive',
      c1: '244, 63, 94',
      c2: '236, 72, 153',
      c3: '251, 191, 36',
      c4: '168, 85, 247',
      hex: '#f43f5e'
    },
    {
      nameFa: 'خورشیدی طلایی (طلایی/فیروزه‌ای)',
      nameEn: 'Solar Gold',
      c1: '251, 191, 36',
      c2: '249, 115, 22',
      c3: '236, 72, 153',
      c4: '34, 211, 238',
      hex: '#fbbf24'
    }
  ];

  const I18N = {
    fa: {
      tagline: '◈ موتور فوق‌پیشرفته فشرده‌سازی ویدیو مهیار',
      gpu_badge: 'NVIDIA NVENC آماده',
      mouse_fx_active: 'تم: سایبر نئون',
      source_btn: 'دانلود سورس پایتون + گیت‌هاب اکشن',
      theme_short: 'تم نئون',
      dock_short: 'داک پایین',
      mini_mode: 'انتقال به نوار پایین (Mini Dock)',
      fullscreen: 'تمام‌صفحه / پنجره',
      exit_full: 'خروج کامل',
      files: '◈ تعداد فایل‌ها',
      original: '◈ حجم اولیه کل',
      compressed: '◈ حجم فشرده شده',
      saved: '◈ حجم ذخیره‌شده',
      saved_sub: '{size} آزاد شد',
      quality: '◈ پروفایل کیفیت فشرده‌سازی',
      p_tiny: 'فوق فشرده',
      p_bal: 'متعادل هوشمند',
      p_high: 'کیفیت استودیویی',
      pd_tiny: 'بیشترین کاهش حجم ممکن؛ عالی برای ارسال سریع در تلگرام و دیسکورد.',
      pd_bal: 'بهترین تعادل طلایی بین حجم کم و شفافیت تصویر بالا.',
      pd_high: 'کیفیت تصویر وفادار به نسخه اصلی با حذف دیتای اضافه.',
      target_mode: '◈ حجم هدف دقیق (مگابایت)',
      t_none: 'خودکار (CRF)',
      t_discord: '۲۵ مگ',
      t_telegram: '۵۰ مگ',
      t_web: '۱۰ مگ',
      codec: '◈ موتور کدک تصویر',
      c_h265: 'H.265 · کم‌حجم',
      c_h264: 'H.264 · سازگار',
      res: '◈ رزولوشن خروجی',
      r_orig: 'اصلی',
      fps: '◈ نرخ فریم تصویر (FPS)',
      f_orig: 'اصلی',
      f_60: '60 فریم',
      f_30: '30 فریم',
      gpu: 'شتاب‌دهنده کارت گرافیک (GPU)',
      gpu_detected: 'آماده به کار: NVIDIA NVENC · سوییچ خودکار به CPU',
      mute: 'حذف باند صدا (Mute)',
      mute_hint: 'بی‌صدا کردن ویدیو برای کاهش حجم بیشتر',
      turbo: 'پردازش فوق‌سریع (Turbo Boost)',
      turbo_hint: 'اختصاص حداکثر توان پردازشی سیستم به موتور مهیار',
      out: '◈ مسیر ذخیره خروجی',
      out_same: 'کنار فایل اصلی (_mahyar.mp4)',
      start: 'شروع فشرده‌سازی',
      stop: 'توقف کامل',
      pause: 'مکث موقت',
      resume: 'ادامه پردازش',
      open_folder: 'پوشه خروجی',
      drop_title: 'ویدیوها را در موتور Mahyar رها کنید',
      drop_sub: 'یا برای انتخاب فایل‌ها و پوشه‌ها کلیک کنید',
      add_demo_files: 'افزودن ویدیوهای نمونه برای تست آنی',
      queue: '◈ صف پردازش و فشرده‌سازی',
      add_btn: '+ افزودن ویدیو',
      add_folder: '+ افزودن پوشه',
      sample_short: '+ نمونه',
      clear_done: 'حذف انجام‌شده‌ها',
      clear: 'پاکسازی همه',
      dock_status_idle: 'آماده پردازش در پس‌زمینه',
      dock_status_run: 'در حال فشرده‌سازی {done}/{total} · {pct}%',
      dock_status_paused: 'مکث موقت {done}/{total} · {pct}%',
      tray_show: 'باز کردن نمای کامل برنامه',
      tray_add: 'افزودن ویدیو جدید…',
      tray_start: 'شروع / توقف سریع صف',
      tray_pause: 'مکث / ادامه پردازش',
      tray_folder: 'باز کردن پوشه خروجی',
      tray_quit: 'خروج کامل از برنامه (Full Exit)',
      exited_title: 'برنامه Mahyar Compressor به صورت کامل بسته شد',
      exited_sub: 'تمامی پردازش‌های پس‌زمینه، سینی سیستم و هسته FFmpeg با موفقیت متوقف شدند.',
      relaunch_btn: 'راه‌اندازی مجدد Mahyar Compressor',
      modal_title: 'فایل‌های ارتقایافته پایتون (با دکمه‌های جدید + رفع ارور dock)',
      modal_desc: 'تمام دکمه‌های خلاقانه جدید (مکث/ادامه پردازش، تغییر تم نئونی ۴گانه، سنجاق روی همه پنجره‌ها Pin، انتخاب نرخ فریم 60/30 FPS، حالت Turbo Boost، افزودن پوشه کامل، حذف انجام‌شده‌ها، کپی گزارش و دکمه‌های پخش/پوشه روی هر کارت) به همراه رفع کامل ارور dock در فایل‌های پایتون زیر اعمال شده‌اند:',
      toast_minimized: 'برنامه به نوار پایین منتقل شد! از دکمه‌های پایین می‌توانید مکث، شروع یا خروج کامل انجام دهید.',
      toast_restored: 'بازگشت به نمای کامل استودیوی Mahyar Compressor',
      toast_all_done: 'عملیات تمام شد! با Mahyar Compressor مقدار {size} صرفه‌جویی شد 🎉',
      toast_stopped: 'عملیات فشرده‌سازی متوقف شد.',
      toast_paused: '⏸ پردازش موقتاً متوقف شد — برای ادامه روی «ادامه پردازش» بزنید.',
      toast_resumed: '▶️ پردازش ویدیو از سر گرفته شد!',
      toast_empty: 'ابتدا چند ویدیو به لیست اضافه کنید!',
      toast_added: '{n} فایل ویدیویی به صف Mahyar اضافه شد.',
      toast_folder: 'مسیر خروجی باز شد: {dir}',
      toast_play: '🎬 در حال پخش ویدیو: {name}',
      toast_copied: 'در کلیپ‌بورد کپی شد! 📋',
      toast_report: '📋 گزارش کامل آمار فشرده‌سازی در کلیپ‌بورد کپی شد!',
      toast_theme: '🎨 تم نوری برنامه تغییر کرد: {name}',
      toast_pin_on: '📌 سنجاق روی همه پنجره‌ها (Always on Top) فعال شد!',
      toast_pin_off: 'سنجاق پنجره غیرفعال شد.',
      toast_cleared_done: '{n} ویدیوی تکمیل‌شده از لیست پاک شد.',
    },
    en: {
      tagline: '◈ CYBER VIDEO COMPRESSOR ENGINE',
      gpu_badge: 'NVIDIA NVENC READY',
      mouse_fx_active: 'Theme: Cyber Ultraviolet',
      source_btn: 'Download Python Source + GitHub CI',
      theme_short: 'Neon Theme',
      dock_short: 'Mini Dock',
      mini_mode: 'Minimize to Bottom Dock',
      fullscreen: 'Toggle Fullscreen',
      exit_full: 'Full Exit',
      files: '◈ BATCH QUEUE',
      original: '◈ INPUT VOLUME',
      compressed: '◈ OUTPUT VOLUME',
      saved: '◈ SPACE SAVED',
      saved_sub: '{size} freed',
      quality: '◈ COMPRESSION PROFILE',
      p_tiny: 'Ultra Tiny',
      p_bal: 'Balanced',
      p_high: 'Master Quality',
      pd_tiny: 'Maximum shrinkage for instant sharing on Discord & Telegram.',
      pd_bal: 'Golden equilibrium between compact file size and crystal clarity.',
      pd_high: 'Studio-grade visual fidelity with smart bitrate optimization.',
      target_mode: '◈ TARGET SIZE CAP (MB)',
      t_none: 'Auto CRF',
      t_discord: '25 MB',
      t_telegram: '50 MB',
      t_web: '10 MB',
      codec: '◈ VIDEO CODEC ENGINE',
      c_h265: 'H.265 · HEVC',
      c_h264: 'H.264 · AVC',
      res: '◈ OUTPUT RESOLUTION',
      r_orig: 'Original',
      fps: '◈ FRAME RATE (FPS)',
      f_orig: 'Original',
      f_60: '60 FPS',
      f_30: '30 FPS',
      gpu: 'GPU Hardware Boost',
      gpu_detected: 'NVIDIA NVENC Ready · Auto CPU fallback',
      mute: 'Strip Audio Track',
      mute_hint: 'Remove sound for extra savings',
      turbo: 'Turbo Priority Mode',
      turbo_hint: 'Allocate maximum CPU/GPU priority to FFmpeg',
      out: '◈ DESTINATION FOLDER',
      out_same: 'Same folder as source (_mahyar.mp4)',
      start: 'LAUNCH COMPRESSION',
      stop: 'ABORT ENGINE',
      pause: 'PAUSE',
      resume: 'RESUME',
      open_folder: 'Output Folder',
      drop_title: 'Drop your videos into Mahyar Engine',
      drop_sub: 'or click anywhere here to browse files & folders',
      add_demo_files: 'Load Sample Videos for Instant Test',
      queue: '◈ COMPRESSION PIPELINE QUEUE',
      add_btn: '+ Add Videos',
      add_folder: '+ Add Folder',
      sample_short: '+ Sample',
      clear_done: 'Clear Done',
      clear: 'Clear All',
      dock_status_idle: 'Engine Idle · Running in Dock',
      dock_status_run: 'Encoding {done}/{total} · {pct}%',
      dock_status_paused: 'Paused {done}/{total} · {pct}%',
      tray_show: 'Expand Full Studio Window',
      tray_add: 'Add New Videos…',
      tray_start: 'Start / Stop Queue',
      tray_pause: 'Pause / Resume',
      tray_folder: 'Open Output Folder',
      tray_quit: 'Full Exit (Quit App)',
      exited_title: 'Mahyar Compressor Has Completely Exited',
      exited_sub: 'All background workers, system tray icons, and FFmpeg processes were terminated cleanly.',
      relaunch_btn: 'Relaunch Mahyar Compressor',
      modal_title: 'Upgraded Python Source (New Creative Buttons + Fixed dock)',
      modal_desc: 'All new creative buttons (Pause/Resume, 4 Neon Themes, Always-on-Top Pin, 60/30 FPS selector, Turbo Boost, Add Folder, Clear Done, Copy Report, and per-card Play/Folder buttons) plus the dock fix are included below:',
      toast_minimized: 'Minimized to Bottom Mini-Dock! Pause, Start, or Full Exit from the bottom bar.',
      toast_restored: 'Expanded Mahyar Compressor Studio',
      toast_all_done: 'All done! Mahyar Compressor saved {size} 🎉',
      toast_stopped: 'Compression aborted.',
      toast_paused: '⏸ Encoding paused — click Resume to continue.',
      toast_resumed: '▶️ Encoding resumed!',
      toast_empty: 'Add some videos to the queue first!',
      toast_added: '{n} video(s) added to Mahyar queue.',
      toast_folder: 'Output directory ready: {dir}',
      toast_play: '🎬 Playing video: {name}',
      toast_copied: 'Copied to clipboard! 📋',
      toast_report: '📋 Full compression report copied to clipboard!',
      toast_theme: '🎨 Visual Theme switched: {name}',
      toast_pin_on: '📌 Always on Top ENABLED!',
      toast_pin_off: 'Always on Top disabled.',
      toast_cleared_done: 'Cleared {n} completed video(s).',
    }
  };

  function tr(key, vars = {}) {
    let text = (I18N[LANG] && I18N[LANG][key]) || I18N.fa[key] || key;
    Object.keys(vars).forEach((k) => {
      text = text.replace(`{${k}}`, vars[k]);
    });
    return text;
  }

  function humanSize(bytes) {
    let n = Number(bytes) || 0;
    const units = ['B', 'KB', 'MB', 'GB', 'TB'];
    for (let i = 0; i < units.length; i++) {
      if (n < 1024 || i === units.length - 1) {
        return i === 0 ? `${Math.round(n)} B` : `${n.toFixed(1)} ${units[i]}`;
      }
      n /= 1024;
    }
    return `${n.toFixed(1)} TB`;
  }

  function fmtTime(sec) {
    sec = Math.max(0, Math.floor(sec));
    const m = Math.floor(sec / 60);
    const s = sec % 60;
    return `${m}:${s < 10 ? '0' : ''}${s}`;
  }

  // --------------------------------------------------------------------------
  // 2. INTERACTIVE MOUSE-REACTIVE AURORA + 4 NEON THEMES
  // --------------------------------------------------------------------------
  let themeIdx = 0;
  const auroraCanvas = document.getElementById('aurora-canvas');
  const actx = auroraCanvas.getContext('2d');
  const fxCanvas = document.getElementById('fx-canvas');
  const fctx = fxCanvas.getContext('2d');
  const coordsReadout = document.getElementById('cursor-coords');

  let cw = window.innerWidth;
  let ch = window.innerHeight;
  let mx = 0.5, my = 0.5;
  let tx = 0.5, ty = 0.5;
  const mouseTrail = [];
  const ripples = [];
  const confetti = [];

  function resizeCanvases() {
    cw = window.innerWidth;
    ch = window.innerHeight;
    auroraCanvas.width = cw;
    auroraCanvas.height = ch;
    fxCanvas.width = cw;
    fxCanvas.height = ch;
  }
  window.addEventListener('resize', resizeCanvases);
  resizeCanvases();

  window.addEventListener('mousemove', (e) => {
    tx = Math.max(0, Math.min(1, e.clientX / Math.max(1, cw)));
    ty = Math.max(0, Math.min(1, e.clientY / Math.max(1, ch)));
    if (coordsReadout) {
      coordsReadout.textContent = `X:${Math.round(tx * 100)}% Y:${Math.round(ty * 100)}%`;
    }
    mouseTrail.push({ x: e.clientX, y: e.clientY, life: 1.0 });
    if (mouseTrail.length > 26) mouseTrail.shift();
  });

  window.addEventListener('mousedown', (e) => {
    ripples.push({ x: e.clientX, y: e.clientY, r: 8, alpha: 0.75 });
  });

  const stars = Array.from({ length: 75 }, (_, i) => ({
    x: Math.random(),
    y: Math.random(),
    spd: 0.008 + Math.random() * 0.025,
    size: 1.1 + Math.random() * 2.1,
    phase: Math.random() * Math.PI * 2,
    colorType: i % 3
  }));

  function triggerConfettiBurst(originX, originY, count = 130) {
    const colors = ['#22d3ee', '#a855f7', '#ec4899', '#34d399', '#fbbf24', '#ffffff'];
    for (let i = 0; i < count; i++) {
      const ang = -Math.PI * 0.95 + Math.random() * Math.PI * 0.9;
      const spd = 240 + Math.random() * 680;
      confetti.push({
        x: originX,
        y: originY,
        vx: Math.cos(ang) * spd,
        vy: Math.sin(ang) * spd,
        rot: Math.random() * Math.PI * 2,
        vrot: (Math.random() - 0.5) * 14,
        color: colors[Math.floor(Math.random() * colors.length)],
        size: 5 + Math.random() * 6,
        life: 1.4 + Math.random() * 1.1
      });
    }
  }

  let lastTime = performance.now();

  function renderBackground(now) {
    const t = now * 0.001;
    const dt = Math.min(0.05, (now - lastTime) * 0.001);
    lastTime = now;

    mx += (tx - mx) * 0.12;
    my += (ty - my) * 0.12;

    actx.fillStyle = '#04020a';
    actx.fillRect(0, 0, cw, ch);

    const ox = (mx - 0.5) * 0.34;
    const oy = (my - 0.5) * 0.34;
    const th = THEMES[themeIdx];

    const blobs = [
      { col: th.c1, cx: 0.20 + ox, cy: 0.20 + oy, rf: 0.48, sp: 0.14, ph: 0.0, a: 0.28 },
      { col: th.c2, cx: 0.82 - ox, cy: 0.24 + oy, rf: 0.50, sp: 0.11, ph: 1.7, a: 0.24 },
      { col: th.c3, cx: 0.70 + ox * 0.7, cy: 0.84 - oy, rf: 0.45, sp: 0.13, ph: 3.1, a: 0.22 },
      { col: th.c4, cx: 0.16 - ox, cy: 0.80 - oy * 0.7, rf: 0.44, sp: 0.10, ph: 4.6, a: 0.25 },
      { col: th.c4, cx: mx, cy: my, rf: 0.34, sp: 0.0, ph: 0.0, a: 0.26 }
    ];

    const maxDim = Math.max(cw, ch);
    for (let i = 0; i < blobs.length; i++) {
      const b = blobs[i];
      const bx = (b.cx + (b.sp > 0 ? 0.12 * Math.sin(t * b.sp * 2 + b.ph) : 0)) * cw;
      const by = (b.cy + (b.sp > 0 ? 0.11 * Math.cos(t * b.sp * 2.5 + b.ph * 1.6) : 0)) * ch;
      const rad = b.rf * maxDim;

      const grad = actx.createRadialGradient(bx, by, 0, bx, by, rad);
      grad.addColorStop(0, `rgba(${b.col}, ${b.a})`);
      grad.addColorStop(0.55, `rgba(${b.col}, ${b.a * 0.35})`);
      grad.addColorStop(1, `rgba(${b.col}, 0)`);

      actx.fillStyle = grad;
      actx.beginPath();
      actx.arc(bx, by, rad, 0, Math.PI * 2);
      actx.fill();
    }

    const mxPx = mx * cw;
    const myPx = my * ch;
    actx.strokeStyle = `rgba(${th.c1}, 0.05)`;
    actx.lineWidth = 1;
    const step = 70;
    const shiftX = (mx - 0.5) * -40;
    const shiftY = (my - 0.5) * -40;

    actx.beginPath();
    for (let x = (shiftX % step); x < cw; x += step) {
      actx.moveTo(x, 0);
      actx.lineTo(x, ch);
    }
    for (let y = (shiftY % step); y < ch; y += step) {
      actx.moveTo(0, y);
      actx.lineTo(cw, y);
    }
    actx.stroke();

    for (let i = mouseTrail.length - 1; i >= 0; i--) {
      const pt = mouseTrail[i];
      pt.life -= dt * 2.4;
      if (pt.life <= 0) {
        mouseTrail.splice(i, 1);
        continue;
      }
      actx.fillStyle = `rgba(${th.c4}, ${pt.life * 0.26})`;
      actx.beginPath();
      actx.arc(pt.x, pt.y, 9 * pt.life, 0, Math.PI * 2);
      actx.fill();
    }

    for (let i = ripples.length - 1; i >= 0; i--) {
      const rp = ripples[i];
      rp.r += dt * 320;
      rp.alpha -= dt * 1.1;
      if (rp.alpha <= 0) {
        ripples.splice(i, 1);
        continue;
      }
      actx.strokeStyle = `rgba(${th.c4}, ${rp.alpha})`;
      actx.lineWidth = 2;
      actx.beginPath();
      actx.arc(rp.x, rp.y, rp.r, 0, Math.PI * 2);
      actx.stroke();
    }

    const starPositions = [];
    for (let i = 0; i < stars.length; i++) {
      const st = stars[i];
      const yy = (st.y - t * st.spd + (my - 0.5) * st.spd * 12 + 10) % 1.0;
      const xx = (st.x + 0.012 * Math.sin(t * 0.7 + st.phase) + (mx - 0.5) * st.spd * 12 + 10) % 1.0;
      const sx = xx * cw;
      const sy = yy * ch;
      starPositions.push({ x: sx, y: sy });

      const alpha = 0.28 + 0.52 * (0.5 + 0.5 * Math.sin(t * 2.0 + st.phase));
      actx.fillStyle = st.colorType === 0
        ? `rgba(${th.c4}, ${alpha})`
        : st.colorType === 1
          ? `rgba(${th.c1}, ${alpha})`
          : `rgba(255, 255, 255, ${alpha})`;
      actx.beginPath();
      actx.arc(sx, sy, st.size, 0, Math.PI * 2);
      actx.fill();
    }

    for (let i = 0; i < starPositions.length; i++) {
      const sp = starPositions[i];
      const dist = Math.hypot(sp.x - mxPx, sp.y - myPx);
      if (dist < 190) {
        const lineAlpha = (1 - dist / 190) * 0.42;
        actx.strokeStyle = `rgba(${th.c4}, ${lineAlpha})`;
        actx.lineWidth = 1.1;
        actx.beginPath();
        actx.moveTo(mxPx, myPx);
        actx.lineTo(sp.x, sp.y);
        actx.stroke();
      }
    }

    fctx.clearRect(0, 0, cw, ch);
    for (let i = confetti.length - 1; i >= 0; i--) {
      const p = confetti[i];
      p.vy += 980 * dt;
      p.vx *= (1 - 0.8 * dt);
      p.x += p.vx * dt;
      p.y += p.vy * dt;
      p.rot += p.vrot * dt;
      p.life -= dt * 0.65;
      if (p.life <= 0 || p.y > ch + 30) {
        confetti.splice(i, 1);
        continue;
      }
      fctx.save();
      fctx.translate(p.x, p.y);
      fctx.rotate(p.rot);
      fctx.globalAlpha = Math.max(0, Math.min(1, p.life));
      fctx.fillStyle = p.color;
      fctx.fillRect(-p.size / 2, -p.size / 4, p.size, p.size / 2);
      fctx.restore();
    }

    requestAnimationFrame(renderBackground);
  }
  requestAnimationFrame(renderBackground);

  // --------------------------------------------------------------------------
  // 3. APPLICATION STATE & SAMPLE QUEUE
  // --------------------------------------------------------------------------
  const state = {
    preset: 1,       // 0: Tiny, 1: Balanced, 2: High
    targetMb: 0,     // 0: Auto CRF, 25, 50, 10
    codec: 'h265',
    res: 'orig',
    fps: 'orig',     // 'orig' | '60' | '30'
    gpu: true,
    mute: false,
    turbo: false,
    pinned: false,
    outDir: '',
    running: false,
    paused: false,
    items: [],
    nextId: 1
  };

  const SAMPLE_VIDEOS = [
    { name: 'Cyberpunk_Gameplay_4K_60fps.mp4', width: 3840, height: 2160, duration: 142, size: 428 * 1024 * 1024 },
    { name: 'Mahyar_Studio_Showreel_2026.mkv', width: 2560, height: 1440, duration: 96, size: 215 * 1024 * 1024 },
    { name: 'Mobile_Portrait_Vlog_HDR.mov', width: 1080, height: 1920, duration: 64, size: 118 * 1024 * 1024 }
  ];

  // DOM Elements
  const appWindow = document.getElementById('app-window');
  const bottomDock = document.getElementById('bottom-mini-dock');
  const trayPopupMenu = document.getElementById('tray-popup-menu');
  const poweroffOverlay = document.getElementById('poweroff-overlay');
  const sourceModal = document.getElementById('source-modal');
  const toastEl = document.getElementById('toast-alert');
  const queueListEl = document.getElementById('queue-list');
  const dropPortal = document.getElementById('drop-portal');
  const queueHeader = document.getElementById('queue-header');
  const queueCountBadge = document.getElementById('queue-count-badge');
  const videoInput = document.getElementById('video-input');
  const folderInput = document.getElementById('folder-input');

  let toastTimer = null;
  function showToast(msg, borderColor = '#22d3ee') {
    toastEl.textContent = msg;
    toastEl.style.borderColor = borderColor;
    toastEl.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => {
      toastEl.classList.remove('show');
    }, 3400);
  }

  // --------------------------------------------------------------------------
  // 4. QUEUE MANAGEMENT & REALISTIC ENCODING ENGINE (WITH PAUSE / RESUME)
  // --------------------------------------------------------------------------
  function getSavingRatio() {
    const baseByPreset = [0.82, 0.68, 0.48][state.preset] || 0.68;
    const codecBonus = state.codec === 'h265' ? 0.08 : -0.05;
    const resBonus = state.res === '480p' ? 0.12 : state.res === '720p' ? 0.08 : state.res === '1080p' ? 0.04 : 0;
    const fpsBonus = state.fps === '30' ? 0.07 : state.fps === '60' ? 0.03 : 0;
    const muteBonus = state.mute ? 0.04 : 0;
    return Math.min(0.93, Math.max(0.30, baseByPreset + codecBonus + resBonus + fpsBonus + muteBonus));
  }

  function addQueueItem(fileObj) {
    const item = {
      id: state.nextId++,
      name: fileObj.name,
      width: fileObj.width || 1920,
      height: fileObj.height || 1080,
      duration: fileObj.duration || 85,
      inSize: fileObj.size || (95 * 1024 * 1024),
      outSize: 0,
      status: 'queued',
      progress: 0,
      speed: 0,
      eta: 0
    };
    state.items.push(item);
  }

  function seedInitialDemoFiles() {
    SAMPLE_VIDEOS.forEach((v) => addQueueItem(v));
    renderQueue();
    updateStats();
  }

  function renderQueue() {
    queueListEl.innerHTML = '';
    const hasItems = state.items.length > 0;
    queueHeader.style.display = hasItems ? 'flex' : 'none';
    queueListEl.style.display = hasItems ? 'flex' : 'none';
    dropPortal.classList.toggle('expanded-empty', !hasItems);
    queueCountBadge.textContent = String(state.items.length);

    state.items.forEach((it) => {
      const card = document.createElement('div');
      card.className = `queue-card status-${it.status}`;
      card.dataset.id = it.id;

      let orbIcon = '<i class="fa-solid fa-play"></i>';
      if (it.status === 'processing') {
        orbIcon = state.paused
          ? '<i class="fa-solid fa-pause"></i>'
          : '<i class="fa-solid fa-spinner fa-spin"></i>';
      } else if (it.status === 'done') {
        orbIcon = '<i class="fa-solid fa-check"></i>';
      }

      const fpsTag = state.fps !== 'orig' ? ` · ${state.fps}fps` : '';
      let subText = `${it.width}×${it.height}${fpsTag}  ·  ${fmtTime(it.duration)}  ·  ${humanSize(it.inSize)}`;
      if (it.status === 'processing') {
        const modeTxt = state.paused ? 'PAUSED' : `${it.speed.toFixed(1)}× (${state.gpu ? 'NVENC GPU' : 'CPU'}${state.turbo ? ' + TURBO' : ''})`;
        subText = `${modeTxt}  ·  ETA ${fmtTime(it.eta)}`;
      } else if (it.status === 'done') {
        subText = `${humanSize(it.inSize)}  →  ${humanSize(it.outSize)}  (${it.name.replace(/\.[^.]+$/, '')}_mahyar.mp4)`;
      }

      let rightHtml = '';
      if (it.status === 'processing') {
        rightHtml = `<span class="q-pct-readout">${Math.round(it.progress * 100)}%</span>`;
      } else if (it.status === 'done') {
        const savedPct = Math.round((1 - it.outSize / it.inSize) * 100);
        rightHtml = `
          <span class="q-saved-pill">−${savedPct}%</span>
          <button type="button" class="q-action-btn" data-play="${it.id}" title="پخش ویدیوی خروجی">
            <i class="fa-solid fa-play"></i>
          </button>
          <button type="button" class="q-action-btn purple" data-dir="${it.id}" title="نمایش در پوشه">
            <i class="fa-solid fa-folder-open"></i>
          </button>
          <button type="button" class="q-remove-btn" data-remove="${it.id}" title="حذف از لیست">
            <i class="fa-solid fa-xmark"></i>
          </button>
        `;
      } else {
        rightHtml = `
          <button type="button" class="q-action-btn" data-play="${it.id}" title="پیش‌نمایش ویدیو">
            <i class="fa-solid fa-play"></i>
          </button>
          <button type="button" class="q-action-btn purple" data-dir="${it.id}" title="نمایش در پوشه">
            <i class="fa-solid fa-folder-open"></i>
          </button>
          <button type="button" class="q-remove-btn" data-remove="${it.id}" title="حذف از لیست">
            <i class="fa-solid fa-xmark"></i>
          </button>
        `;
      }

      const barPct = it.status === 'done' ? 100 : Math.round(it.progress * 100);

      card.innerHTML = `
        <div class="q-card-left">
          <div class="q-status-orb">${orbIcon}</div>
          <div class="q-meta">
            <div class="q-filename" title="${it.name}">${it.name}</div>
            <div class="q-subinfo">${subText}</div>
          </div>
        </div>
        <div class="q-card-right">${rightHtml}</div>
        <div class="q-progress-track">
          <div class="q-progress-fill" style="width: ${barPct}%"></div>
        </div>
      `;

      queueListEl.appendChild(card);
    });

    // Attach Play, Folder, and Remove handlers on each card
    queueListEl.querySelectorAll('[data-play]').forEach((btn) => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const id = Number(btn.getAttribute('data-play'));
        const item = state.items.find((x) => x.id === id);
        if (item) showToast(tr('toast_play', { name: item.name }), '#22d3ee');
      });
    });

    queueListEl.querySelectorAll('[data-dir]').forEach((btn) => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        showToast(tr('toast_folder', { dir: state.outDir || 'Source Folder (_mahyar.mp4)' }), '#a855f7');
      });
    });

    queueListEl.querySelectorAll('[data-remove]').forEach((btn) => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        if (state.running) return;
        const id = Number(btn.getAttribute('data-remove'));
        state.items = state.items.filter((x) => x.id !== id);
        renderQueue();
        updateStats();
      });
    });
  }

  function updateStats() {
    const doneItems = state.items.filter((i) => i.status === 'done');
    const totalIn = doneItems.reduce((acc, i) => acc + i.inSize, 0);
    const totalOut = doneItems.reduce((acc, i) => acc + i.outSize, 0);
    const savedBytes = Math.max(0, totalIn - totalOut);
    const savedRatio = totalIn > 0 ? (1 - totalOut / totalIn) : 0;

    document.getElementById('stat-files').textContent = `${doneItems.length} / ${state.items.length}`;
    document.getElementById('stat-orig').textContent = humanSize(totalIn);
    document.getElementById('stat-comp').textContent = humanSize(totalOut);

    const savedValEl = document.getElementById('stat-saved');
    const savedSubEl = document.getElementById('stat-saved-sub');
    if (savedRatio > 0.001) {
      savedValEl.textContent = `−${Math.round(savedRatio * 100)}%`;
      savedSubEl.textContent = tr('saved_sub', { size: humanSize(savedBytes) });
    } else {
      savedValEl.textContent = '—';
      savedSubEl.textContent = tr('saved_sub', { size: '0 MB' });
    }

    if (!state.running && doneItems.length === 0) {
      document.getElementById('overall-bar').style.width = '0%';
      document.getElementById('dock-mini-bar').style.width = '0%';
      document.getElementById('dock-pct-badge').textContent = 'READY';
      document.getElementById('dock-status-text').textContent = tr('dock_status_idle');
      document.getElementById('dock-status-dot').classList.remove('running');
    } else if (state.items.length > 0) {
      const sumProgress = state.items.reduce((acc, i) => acc + (i.status === 'done' ? 1 : i.progress), 0);
      const ovPct = Math.round((sumProgress / state.items.length) * 100);
      document.getElementById('overall-bar').style.width = `${ovPct}%`;
      document.getElementById('dock-mini-bar').style.width = `${ovPct}%`;
      document.getElementById('dock-pct-badge').textContent = state.paused ? 'PAUSED' : state.running ? `${ovPct}%` : 'DONE';
      const statusKey = state.paused ? 'dock_status_paused' : state.running ? 'dock_status_run' : 'dock_status_idle';
      document.getElementById('dock-status-text').textContent = tr(statusKey, {
        done: doneItems.length,
        total: state.items.length,
        pct: ovPct
      });
      document.getElementById('dock-status-dot').classList.toggle('running', state.running && !state.paused);
    }
  }

  let encodeInterval = null;

  function togglePauseResume() {
    if (!state.running) return;
    state.paused = !state.paused;
    syncActionButtons();
    renderQueue();
    updateStats();
    showToast(tr(state.paused ? 'toast_paused' : 'toast_resumed'), state.paused ? '#fbbf24' : '#22d3ee');
  }

  function toggleCompression() {
    if (state.running) {
      clearInterval(encodeInterval);
      state.running = false;
      state.paused = false;
      state.items.forEach((it) => {
        if (it.status === 'processing') {
          it.status = 'queued';
          it.progress = 0;
        }
      });
      syncActionButtons();
      renderQueue();
      updateStats();
      showToast(tr('toast_stopped'), '#fbbf24');
      return;
    }

    let todo = state.items.filter((i) => i.status !== 'done');
    if (todo.length === 0 && state.items.length > 0) {
      state.items.forEach((i) => {
        i.status = 'queued';
        i.progress = 0;
        i.outSize = 0;
      });
      todo = state.items.slice();
    }

    if (todo.length === 0) {
      showToast(tr('toast_empty'), '#fbbf24');
      return;
    }

    state.running = true;
    state.paused = false;
    syncActionButtons();

    encodeInterval = setInterval(() => {
      if (state.paused) return;

      const current = state.items.find((i) => i.status === 'processing') ||
                      state.items.find((i) => i.status === 'queued');

      if (!current) {
        clearInterval(encodeInterval);
        state.running = false;
        state.paused = false;
        syncActionButtons();
        renderQueue();
        updateStats();

        const totalSaved = state.items.reduce((acc, i) => acc + Math.max(0, i.inSize - i.outSize), 0);
        triggerConfettiBurst(cw * 0.35, ch * 0.65, 140);
        triggerConfettiBurst(cw * 0.70, ch * 0.55, 110);
        showToast(tr('toast_all_done', { size: humanSize(totalSaved) }), '#34d399');
        return;
      }

      if (current.status === 'queued') {
        current.status = 'processing';
        current.progress = 0.04;
      } else {
        const turboMult = state.turbo ? 1.35 : 1.0;
        const step = (state.gpu ? 0.085 : 0.045) * turboMult;
        current.progress = Math.min(1, current.progress + step);
        current.speed = (state.gpu ? (3.8 + Math.random() * 1.4) : (1.4 + Math.random() * 0.5)) * turboMult;
        current.eta = Math.max(1, (1 - current.progress) * 12);

        if (current.progress >= 1) {
          current.status = 'done';
          const ratio = getSavingRatio();
          if (state.targetMb > 0) {
            current.outSize = Math.min(current.inSize * 0.9, state.targetMb * 0.96 * 1024 * 1024);
          } else {
            current.outSize = Math.round(current.inSize * (1 - ratio));
          }
        }
      }

      renderQueue();
      updateStats();
    }, 140);
  }

  function syncActionButtons() {
    const startBtn = document.getElementById('btn-start');
    const startIcon = document.getElementById('start-icon');
    const startLabel = document.getElementById('start-label');

    const pauseBtn = document.getElementById('btn-pause');
    const pauseIcon = document.getElementById('pause-icon');
    const pauseLabel = document.getElementById('pause-label');

    const dockStartBtn = document.getElementById('dock-btn-start');
    const dockStartIcon = document.getElementById('dock-start-icon');
    const dockStartLabel = document.getElementById('dock-start-label');

    const dockPauseBtn = document.getElementById('dock-btn-pause');
    const dockPauseIcon = document.getElementById('dock-pause-icon');

    if (state.running) {
      startBtn.classList.add('danger-mode');
      startIcon.className = 'fa-solid fa-stop';
      startLabel.textContent = tr('stop');

      pauseBtn.classList.remove('hidden');
      pauseIcon.className = state.paused ? 'fa-solid fa-play' : 'fa-solid fa-pause';
      pauseLabel.textContent = tr(state.paused ? 'resume' : 'pause');

      dockStartBtn.classList.add('danger-mode');
      dockStartIcon.className = 'fa-solid fa-stop';
      dockStartLabel.textContent = tr('stop');

      dockPauseBtn.classList.remove('hidden');
      dockPauseIcon.className = state.paused ? 'fa-solid fa-play' : 'fa-solid fa-pause';
    } else {
      startBtn.classList.remove('danger-mode');
      startIcon.className = 'fa-solid fa-rocket';
      startLabel.textContent = tr('start');

      pauseBtn.classList.add('hidden');

      dockStartBtn.classList.remove('danger-mode');
      dockStartIcon.className = 'fa-solid fa-play';
      dockStartLabel.textContent = tr('start');

      dockPauseBtn.classList.add('hidden');
    }
  }

  // --------------------------------------------------------------------------
  // 5. CREATIVE HUD BUTTONS (THEME SWITCHER, PIN, REPORT, FOLDER, CLEAR DONE)
  // --------------------------------------------------------------------------
  function cycleTheme() {
    themeIdx = (themeIdx + 1) % THEMES.length;
    const th = THEMES[themeIdx];
    const tName = LANG === 'fa' ? th.nameFa : th.nameEn;
    document.getElementById('theme-name-label').textContent = LANG === 'fa' ? `تم: ${th.nameFa}` : `Theme: ${th.nameEn}`;
    showToast(tr('toast_theme', { name: tName }), th.hex);
  }

  document.getElementById('btn-theme').addEventListener('click', cycleTheme);
  document.getElementById('dock-btn-theme').addEventListener('click', cycleTheme);

  const pinBtn = document.getElementById('btn-pin');
  pinBtn.addEventListener('click', () => {
    state.pinned = !state.pinned;
    pinBtn.classList.toggle('pinned', state.pinned);
    showToast(tr(state.pinned ? 'toast_pin_on' : 'toast_pin_off'), state.pinned ? '#22d3ee' : '#a855f7');
  });

  document.getElementById('btn-copy-report').addEventListener('click', () => {
    const done = state.items.filter((i) => i.status === 'done');
    const tin = done.reduce((a, i) => a + i.inSize, 0);
    const tout = done.reduce((a, i) => a + i.outSize, 0);
    const saved = Math.max(0, tin - tout);
    const pct = tin > 0 ? ((1 - tout / tin) * 100).toFixed(1) : '0.0';
    const report = [
      '=== Mahyar Compressor PRO v2.0 Report ===',
      `Files Processed: ${done.length} / ${state.items.length}`,
      `Input Volume: ${humanSize(tin)}`,
      `Output Volume: ${humanSize(tout)}`,
      `Space Saved: ${humanSize(saved)} (-${pct}%)`
    ].join('\n');
    if (navigator.clipboard) {
      navigator.clipboard.writeText(report).catch(() => {});
    }
    showToast(tr('toast_report'), '#34d399');
  });

  document.getElementById('btn-clear-done').addEventListener('click', () => {
    if (state.running) return;
    const before = state.items.length;
    state.items = state.items.filter((i) => i.status !== 'done');
    const removed = before - state.items.length;
    renderQueue();
    updateStats();
    if (removed > 0) {
      showToast(tr('toast_cleared_done', { n: removed }), '#34d399');
    }
  });

  // --------------------------------------------------------------------------
  // 6. BOTTOM MINI-DOCK, SYSTEM TRAY MENU & FULL EXIT CONTROLS
  // --------------------------------------------------------------------------
  function minimizeToBottomDock() {
    appWindow.classList.add('minimized-to-bottom');
    bottomDock.classList.remove('hidden');
    trayPopupMenu.classList.add('hidden');
    showToast(tr('toast_minimized'), '#22d3ee');
  }

  function restoreFromBottomDock() {
    bottomDock.classList.add('hidden');
    trayPopupMenu.classList.add('hidden');
    appWindow.classList.remove('minimized-to-bottom');
    showToast(tr('toast_restored'), '#a855f7');
  }

  function performFullExit() {
    if (state.running) {
      clearInterval(encodeInterval);
      state.running = false;
      state.paused = false;
      syncActionButtons();
    }
    trayPopupMenu.classList.add('hidden');
    bottomDock.classList.add('hidden');
    appWindow.classList.add('minimized-to-bottom');
    poweroffOverlay.classList.remove('hidden');
  }

  function relaunchApp() {
    poweroffOverlay.classList.add('hidden');
    appWindow.classList.remove('minimized-to-bottom');
    showToast(tr('toast_restored'), '#34d399');
  }

  document.getElementById('btn-to-dock').addEventListener('click', minimizeToBottomDock);
  document.getElementById('btn-shrink-bottom').addEventListener('click', minimizeToBottomDock);
  document.getElementById('dock-btn-expand').addEventListener('click', restoreFromBottomDock);
  document.getElementById('dock-brand-restore').addEventListener('dblclick', restoreFromBottomDock);

  document.getElementById('btn-exit-top').addEventListener('click', performFullExit);
  document.getElementById('dock-btn-quit').addEventListener('click', performFullExit);
  document.getElementById('btn-relaunch').addEventListener('click', relaunchApp);

  document.getElementById('dock-btn-menu').addEventListener('click', (e) => {
    e.stopPropagation();
    trayPopupMenu.classList.toggle('hidden');
  });

  document.getElementById('tray-item-expand').addEventListener('click', restoreFromBottomDock);
  document.getElementById('tray-item-add').addEventListener('click', () => {
    trayPopupMenu.classList.add('hidden');
    videoInput.click();
  });
  document.getElementById('tray-item-start').addEventListener('click', () => {
    trayPopupMenu.classList.add('hidden');
    toggleCompression();
  });
  document.getElementById('tray-item-pause').addEventListener('click', () => {
    trayPopupMenu.classList.add('hidden');
    togglePauseResume();
  });
  document.getElementById('tray-item-folder').addEventListener('click', () => {
    trayPopupMenu.classList.add('hidden');
    showToast(tr('toast_folder', { dir: state.outDir || 'Source Folder (_mahyar.mp4)' }));
  });
  document.getElementById('tray-item-quit').addEventListener('click', performFullExit);

  window.addEventListener('click', () => {
    trayPopupMenu.classList.add('hidden');
  });

  const fsBtn = document.getElementById('btn-fullscreen');
  const fsIcon = document.getElementById('fs-icon');
  fsBtn.addEventListener('click', () => {
    if (document.body.classList.contains('windowed-mode')) {
      document.body.classList.remove('windowed-mode');
      document.body.classList.add('fullscreen-mode');
      fsIcon.className = 'fa-solid fa-compress';
      if (document.documentElement.requestFullscreen) {
        document.documentElement.requestFullscreen().catch(() => {});
      }
    } else {
      document.body.classList.remove('fullscreen-mode');
      document.body.classList.add('windowed-mode');
      fsIcon.className = 'fa-solid fa-expand';
      if (document.fullscreenElement && document.exitFullscreen) {
        document.exitFullscreen().catch(() => {});
      }
    }
  });

  // --------------------------------------------------------------------------
  // 7. SETTINGS CONTROLS, FILE/FOLDER INPUT & LANGUAGE SWITCHER
  // --------------------------------------------------------------------------
  const crfLabels = ['CRF 30 · 64k', 'CRF 27 · 96k', 'CRF 23 · 128k'];
  const descKeys = ['pd_tiny', 'pd_bal', 'pd_high'];

  document.querySelectorAll('.segmented-control').forEach((seg) => {
    const group = seg.dataset.group;
    seg.querySelectorAll('.seg-btn').forEach((btn) => {
      btn.addEventListener('click', () => {
        seg.querySelectorAll('.seg-btn').forEach((b) => b.classList.remove('active'));
        btn.classList.add('active');
        const val = btn.dataset.val;
        if (group === 'preset') {
          state.preset = Number(val);
          document.getElementById('crf-readout').textContent = crfLabels[state.preset];
          document.getElementById('preset-desc').textContent = tr(descKeys[state.preset]);
        } else if (group === 'target') {
          state.targetMb = Number(val);
        } else if (group === 'codec') {
          state.codec = val;
        } else if (group === 'res') {
          state.res = val;
        } else if (group === 'fps') {
          state.fps = val;
          renderQueue();
        }
      });
    });
  });

  const toggleGpu = document.getElementById('toggle-gpu');
  toggleGpu.addEventListener('click', () => {
    state.gpu = !state.gpu;
    toggleGpu.setAttribute('aria-checked', String(state.gpu));
    toggleGpu.querySelector('.cyber-switch').classList.toggle('on', state.gpu);
  });

  const toggleMute = document.getElementById('toggle-mute');
  toggleMute.addEventListener('click', () => {
    state.mute = !state.mute;
    toggleMute.setAttribute('aria-checked', String(state.mute));
    toggleMute.querySelector('.cyber-switch').classList.toggle('on', state.mute);
  });

  const toggleTurbo = document.getElementById('toggle-turbo');
  toggleTurbo.addEventListener('click', () => {
    state.turbo = !state.turbo;
    toggleTurbo.setAttribute('aria-checked', String(state.turbo));
    toggleTurbo.querySelector('.cyber-switch').classList.toggle('on', state.turbo);
  });

  const outFolderLabel = document.getElementById('out-folder-label');
  const resetOutBtn = document.getElementById('btn-reset-out');
  document.getElementById('btn-choose-out').addEventListener('click', () => {
    state.outDir = 'D:\\Mahyar_Compressed_Videos';
    outFolderLabel.textContent = `📁 ${state.outDir}`;
    resetOutBtn.style.display = 'inline-flex';
    showToast(tr('toast_folder', { dir: state.outDir }));
  });

  resetOutBtn.addEventListener('click', () => {
    state.outDir = '';
    outFolderLabel.textContent = tr('out_same');
    resetOutBtn.style.display = 'none';
  });

  dropPortal.addEventListener('click', (e) => {
    if (e.target.closest('#btn-add-demo')) return;
    videoInput.click();
  });

  document.getElementById('btn-add-more').addEventListener('click', () => videoInput.click());
  document.getElementById('btn-add-folder').addEventListener('click', () => folderInput.click());
  document.getElementById('dock-btn-add').addEventListener('click', () => videoInput.click());

  document.getElementById('btn-add-demo').addEventListener('click', (e) => {
    e.stopPropagation();
    SAMPLE_VIDEOS.forEach((v) => addQueueItem(v));
    renderQueue();
    updateStats();
    showToast(tr('toast_added', { n: SAMPLE_VIDEOS.length }));
  });

  document.getElementById('btn-add-sample-bar').addEventListener('click', () => {
    const pick = SAMPLE_VIDEOS[Math.floor(Math.random() * SAMPLE_VIDEOS.length)];
    addQueueItem({
      name: `Clip_${Math.floor(100 + Math.random() * 899)}_${pick.name}`,
      width: pick.width,
      height: pick.height,
      duration: pick.duration,
      size: pick.size
    });
    renderQueue();
    updateStats();
    showToast(tr('toast_added', { n: 1 }));
  });

  function handleSelectedFiles(fileList) {
    const files = Array.from(fileList || []);
    if (!files.length) return;
    files.forEach((f) => {
      addQueueItem({
        name: f.name,
        width: 1920,
        height: 1080,
        duration: Math.max(15, Math.round(f.size / (1.4 * 1024 * 1024))),
        size: f.size || (64 * 1024 * 1024)
      });
    });
    renderQueue();
    updateStats();
    showToast(tr('toast_added', { n: files.length }));
  }

  videoInput.addEventListener('change', () => {
    handleSelectedFiles(videoInput.files);
    videoInput.value = '';
  });

  folderInput.addEventListener('change', () => {
    handleSelectedFiles(folderInput.files);
    folderInput.value = '';
  });

  window.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropPortal.classList.add('drag-over');
  });

  window.addEventListener('dragleave', () => {
    dropPortal.classList.remove('drag-over');
  });

  window.addEventListener('drop', (e) => {
    e.preventDefault();
    dropPortal.classList.remove('drag-over');
    handleSelectedFiles(e.dataTransfer && e.dataTransfer.files);
  });

  document.getElementById('btn-clear').addEventListener('click', () => {
    if (state.running) return;
    state.items = [];
    renderQueue();
    updateStats();
  });

  document.getElementById('btn-start').addEventListener('click', toggleCompression);
  document.getElementById('dock-btn-start').addEventListener('click', toggleCompression);
  document.getElementById('btn-pause').addEventListener('click', togglePauseResume);
  document.getElementById('dock-btn-pause').addEventListener('click', togglePauseResume);

  document.getElementById('btn-open-folder').addEventListener('click', () => {
    showToast(tr('toast_folder', { dir: state.outDir || 'Source Folder (_mahyar.mp4)' }));
  });
  document.getElementById('dock-btn-folder').addEventListener('click', () => {
    showToast(tr('toast_folder', { dir: state.outDir || 'Source Folder (_mahyar.mp4)' }));
  });

  document.getElementById('btn-open-source').addEventListener('click', () => {
    sourceModal.classList.remove('hidden');
  });
  document.getElementById('btn-close-modal').addEventListener('click', () => {
    sourceModal.classList.add('hidden');
  });
  sourceModal.addEventListener('click', (e) => {
    if (e.target === sourceModal) sourceModal.classList.add('hidden');
  });

  document.getElementById('btn-copy-cmd').addEventListener('click', () => {
    const code = document.getElementById('build-cmds').innerText;
    if (navigator.clipboard) {
      navigator.clipboard.writeText(code).catch(() => {});
    }
    showToast(tr('toast_copied'), '#34d399');
  });

  const langBtn = document.getElementById('btn-lang');
  function applyLanguage() {
    document.documentElement.lang = LANG;
    document.documentElement.dir = LANG === 'fa' ? 'rtl' : 'ltr';
    langBtn.textContent = LANG === 'fa' ? 'EN' : 'FA';

    document.querySelectorAll('[data-i18n]').forEach((el) => {
      const k = el.getAttribute('data-i18n');
      el.textContent = tr(k);
    });

    const th = THEMES[themeIdx];
    document.getElementById('theme-name-label').textContent = LANG === 'fa' ? `تم: ${th.nameFa}` : `Theme: ${th.nameEn}`;
    document.getElementById('preset-desc').textContent = tr(descKeys[state.preset]);
    if (!state.outDir) {
      outFolderLabel.textContent = tr('out_same');
    }
    syncActionButtons();
    renderQueue();
    updateStats();
  }

  langBtn.addEventListener('click', () => {
    LANG = LANG === 'fa' ? 'en' : 'fa';
    applyLanguage();
  });

  seedInitialDemoFiles();
  applyLanguage();
})();
