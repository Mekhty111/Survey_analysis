(function () {
  const D = window.SURVEY;
  const css = (v) => getComputedStyle(document.documentElement).getPropertyValue(v).trim();

  const SHORT = {
    "Tapşırıq veriləndən dərhal sonra": "Dərhal",
    "Dedlayndan bir neçə gün əvvəl": "Bir neçə gün əvvəl",
    "Dedlayndan bir gün əvvəl": "Bir gün əvvəl",
    "Dedlayn günü, son saatlarda": "Son saatlarda",
    "Dedlayndan sonra (gecikdirirəm)": "Dedlayndan sonra",
    "Bilmirəm, hər dəfə fərqli olur": "Bilmirəm / fərqli olur",
    "Rahat, heç bir problem görmürəm": "Rahat",
    "Narahat, stres hiss edirəm": "Narahat, stres",
    "Təxminən planladığım qədər": "Planladığım qədər",
    "Təxminən 1,5 dəfə çox": "1,5 dəfə çox",
    "2 dəfə və daha çox": "2 dəfə və çox",
    "Bilmirəm, plan qurmuram": "Plan qurmuram",
    "Əvvəlki plan üzrə davam edirəm və vaxtında bitirirəm": "Əvvəlki planla davam",
    "Əlavə vaxtı işi yaxşılaşdırmağa sərf edirəm": "İşi yaxşılaşdırıram",
    "Başlamağı yeni dedlayna yaxın vaxta keçirirəm": "Başlamağı təxirə salıram",
    "Mükəmməl etmək istəyirəm, ona görə başlamıram": "Mükəmməliyyətçilik",
    "Stres altında daha yaxşı işləyirəm": "Stresdə daha yaxşı işləyirəm",
    "Nədən başlayacağımı bilmirəm": "Nədən başlayacağımı bilmirəm",
    "Mesajlaşma (WhatsApp, Telegram)": "Mesajlaşma",
    "Dostlarla vaxt keçirmək": "Dostlar",
    "Seriallar / filmlər": "Seriallar, filmlər",
    "Telefonu söndürmək və ya uzaqda saxlamaq": "Telefonu uzaqlaşdırmaq",
    "To-do siyahısı / planlayıcı": "To-do siyahısı",
    "Pomodoro texnikası": "Pomodoro",
    "Kitabxanada oxumaq": "Kitabxana",
    "Dostla birlikdə oxumaq": "Dostla birlikdə",
    "Esse / kurs işi yazmaq": "Esse, kurs işi",
    "İmtahana hazırlaşmaq": "İmtahana hazırlıq",
    "Mühazirə materiallarını oxumaq": "Mühazirə materialı",
    "Laboratoriya / praktiki tapşırıq": "Laboratoriya",
    "Beynəlxalq münasibətlər və iqtisadiyyat": "Beyn. münasibətlər, iqtisadiyyat",
    "Filologiya və jurnalistika": "Filologiya, jurnalistika",
    "Sosial elmlər və psixologiya": "Sosial elmlər, psixologiya",
    "Bəli, yarımştat / frilans": "Yarımştat, frilans",
    "Bəli, tam ştat": "Tam ştat",
  };
  const short = (l) => SHORT[l] || String(l);
  const get = (path) => path.split(".").reduce((o, k) => (o == null ? o : o[k]), D);
  const fmt = (v) => (typeof v === "number" ? (Number.isInteger(v) ? String(v) : Math.abs(v) < 1 ? v.toFixed(2) : v.toFixed(1)) : v);
  const f1 = (v) => v.toFixed(1);

  // ---------- derived numbers ----------
  const heat = D.charts.heat.rows;
  const topPct = (row) => row.pct[3] + row.pct[4];
  const sg = D.charts.start_gpa, an = D.charts.allnight_gpa;
  const MONTHS = ["yanvar", "fevral", "mart", "aprel", "may", "iyun", "iyul", "avqust", "sentyabr", "oktyabr", "noyabr", "dekabr"];
  const dt = (s) => { const [y, m, d] = s.split("-").map(Number); return { y, m: MONTHS[m - 1], d }; };
  const p0 = dt(D.period[0]), p1 = dt(D.period[1]);
  D.periodText = p0.m === p1.m ? `${p0.d}–${p1.d} ${p1.m} ${p1.y}` : `${p0.d} ${p0.m} – ${p1.d} ${p1.m} ${p1.y}`;
  D.calc = {
    lowTop: topPct(heat[0]),
    highTop: topPct(heat[2]),
    startFirst: sg.means[0], startLastDay: sg.means[3],
    anFirst: an.means[0], anLast: an.means[3],
    tiktokExtra: D.insight.tiktok_screen - D.insight.no_tiktok_screen,
    allnightTen: Math.round(D.kpi.allnighter_pct / 10),
    aiUnkPct: Math.round((100 * D.unknown.ai) / D.n),
    startGap: Math.round(sg.means[0] - sg.means[3]),
    eveningRange: (() => { const c = D.charts.chrono_score; const v = [c.means[2], c.means[3]].sort((a, b) => a - b); return v[0].toFixed(1) + "–" + v[1].toFixed(1); })(),
  };
  document.querySelectorAll("[data-fill]").forEach((el) => { el.textContent = fmt(get(el.dataset.fill)); });

  // ---------- hero strip ----------
  const strip = document.getElementById("strip"), axis = document.getElementById("strip-axis");
  const st = D.charts.start_time;
  const UNK = new Set(D.uncertain_labels);
  st.labels.forEach((lab, i) => {
    if (UNK.has(lab)) return;
    const col = document.createElement("div");
    col.className = "strip-col";
    for (let k = 0; k < st.counts[i]; k++) {
      const d = document.createElement("span");
      d.className = "dot" + (i >= 3 ? " late" : "");
      col.appendChild(d);
    }
    strip.appendChild(col);
    const a = document.createElement("span");
    a.innerHTML = `<b>${st.counts[i]}</b>${short(lab)}`;
    axis.appendChild(a);
  });
  const dl = document.createElement("div");
  dl.className = "deadline";
  dl.style.left = "80%";
  dl.innerHTML = "<span>Dedlayn</span>";
  strip.appendChild(dl);
  strip.setAttribute("role", "img");
  strip.setAttribute("aria-label", st.labels.map((l, i) => `${short(l)}: ${st.counts[i]}`).join(", "));
  document.getElementById("strip-unk").innerHTML =
    `<span class="dots-inline">${'<span class="dot unk"></span>'.repeat(D.unknown.start)}</span> Daha ${D.unknown.start} nəfər "hər dəfə fərqli olur" cavabını seçib.`;

  // ---------- heatmap ----------
  const hm = document.getElementById("heat");
  const seq = ["--seq-0", "--seq-1", "--seq-2", "--seq-3", "--seq-4", "--seq-5"];
  let html = '<div></div>' + D.charts.heat.gpa.map((g) => `<div class="hd">${g}</div>`).join("");
  heat.forEach((row) => {
    html += `<div class="rl">${row.bucket}<small>n=${row.n}</small></div>`;
    row.pct.forEach((p, j) => {
      const step = p === 0 ? 0 : Math.min(5, 1 + Math.floor(p / 12));
      const ink = step >= 4 ? "var(--heat-ink-hi)" : "var(--ink)";
      html += `<div class="cell" style="background:var(${seq[step]});color:${ink}" title="Prokrastinasiya ${row.bucket}, orta bal ${D.charts.heat.gpa[j]}: ${p}%">${p}%</div>`;
    });
  });
  html += '<div></div><div class="axis-note">Orta bal intervalı → </div>';
  hm.innerHTML = html;

  // ---------- charts ----------
  Chart.defaults.font.family = '"IBM Plex Sans", system-ui, sans-serif';
  Chart.defaults.font.size = 13;
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) Chart.defaults.animation = false; else Chart.defaults.animation.duration = 500;

  const C = () => ({
    ink: css("--ink"), ink2: css("--ink-2"), ink3: css("--ink-3"), rule: css("--rule"),
    series: css("--series"), accent: css("--accent"), unk: css("--unk"), surface: css("--surface"),
  });

  // value labels at bar ends
  const endLabels = {
    id: "endLabels",
    afterDatasetsDraw(chart, _a, opts) {
      if (!opts || !opts.show) return;
      const { ctx } = chart, c = C();
      const meta = chart.getDatasetMeta(0);
      const horiz = chart.options.indexAxis === "y";
      ctx.save();
      ctx.fillStyle = c.ink;
      ctx.font = '600 13px "IBM Plex Sans", system-ui, sans-serif';
      meta.data.forEach((bar, i) => {
        const v = chart.data.datasets[0].data[i];
        const txt = opts.format ? opts.format(v) : fmt(v);
        if (horiz) { ctx.textAlign = "left"; ctx.textBaseline = "middle"; ctx.fillText(txt, bar.x + 6, bar.y); }
        else { ctx.textAlign = "center"; ctx.textBaseline = "bottom"; ctx.fillText(txt, bar.x, bar.y - 4); }
      });
      ctx.restore();
    },
  };
  Chart.register(endLabels);

  const charts = [];
  function bar(id, labels, values, o = {}) {
    const c = C();
    const horiz = o.horizontal !== false;
    const colors = labels.map((l) => (UNK.has(l) ? c.unk : o.highlight && o.highlight.includes(l) ? c.accent : c.series));
    const valueAxis = {
      beginAtZero: true, max: o.max, grace: horiz ? "14%" : "12%",
      grid: { color: c.rule, drawTicks: false }, border: { display: false },
      ticks: { color: c.ink3, padding: 6, maxTicksLimit: 5, callback: o.tick || undefined },
    };
    const catAxis = {
      grid: { display: false }, border: { color: c.rule },
      ticks: { color: c.ink2, autoSkip: false, maxRotation: 0, callback: function (v) { return short(this.getLabelForValue(v)); } },
    };
    const ch = new Chart(document.getElementById(id), {
      type: "bar",
      data: { labels, datasets: [{ data: values, backgroundColor: colors, borderRadius: 4, borderSkipped: "start",
        maxBarThickness: horiz ? 26 : 44, categoryPercentage: 0.8, barPercentage: 0.9 }] },
      options: {
        indexAxis: horiz ? "y" : "x", responsive: true, maintainAspectRatio: false,
        layout: { padding: { right: horiz ? 8 : 0, top: horiz ? 0 : 8 } },
        scales: horiz ? { x: valueAxis, y: catAxis } : { x: catAxis, y: valueAxis },
        plugins: {
          legend: { display: false },
          endLabels: { show: o.labels !== false, format: o.format },
          tooltip: {
            backgroundColor: c.ink, titleColor: c.surface, bodyColor: c.surface, padding: 10, displayColors: false,
            callbacks: {
              title: (items) => items[0].label,
              label: (item) => (o.tooltip ? o.tooltip(item) : `${o.unit || ""}${fmt(item.raw)}`),
            },
          },
        },
      },
    });
    charts.push(ch);
    return ch;
  }

  const K = D.charts, n = D.n;
  const withN = (g, name) => (item) => `${name}: ${fmt(item.raw)} (n=${g.n[item.dataIndex]})`;
  const pctOf = (counts) => counts.map((v) => Math.round((100 * v) / n));
  const pctFmt = (v) => v + "%";

  // insight charts
  bar("c-start-gpa", K.start_gpa.labels, K.start_gpa.means, { highlight: [K.start_gpa.labels[0], K.start_gpa.labels[3]], format: f1, max: 100, tooltip: withN(K.start_gpa, "Orta bal") });
  bar("c-allnight", K.allnight_gpa.labels, K.allnight_gpa.means, { horizontal: false, highlight: [K.allnight_gpa.labels[3]], format: f1, max: 100, tooltip: withN(K.allnight_gpa, "Orta bal") });
  bar("c-thief", K.thief_score.labels, K.thief_score.means, { highlight: ["TikTok"], format: f1, max: 10, tooltip: withN(K.thief_score, "Orta bal") });
  bar("c-reason", K.reason_gpa.labels, K.reason_gpa.means, { highlight: ["Stres altında daha yaxşı işləyirəm"], format: f1, max: 100, tooltip: withN(K.reason_gpa, "Orta bal") });
  bar("c-chrono", K.chrono_score.labels, K.chrono_score.means, { horizontal: false, highlight: ["Səhər"], format: f1, max: 10, tooltip: withN(K.chrono_score, "Orta bal") });
  const cg = K.coping_gpa;
  const order = cg.labels.map((l, i) => i).sort((a, b) => cg.means[b] - cg.means[a]);
  const cgSorted = { labels: order.map((i) => cg.labels[i]), means: order.map((i) => cg.means[i]), n: order.map((i) => cg.n[i]) };
  bar("c-coping", cgSorted.labels, cgSorted.means, { highlight: ["Pomodoro texnikası", "Heç nə"], format: f1, max: 100, tooltip: withN(cgSorted, "Orta bal") });

  // scatter with trend line
  (function () {
    const c = C();
    const pts = K.scatter;
    const jitter = (i) => (((i * 37) % 11) - 5) / 30;
    const xs = pts.map((p) => p.x), ys = pts.map((p) => p.y);
    const mx = xs.reduce((a, b) => a + b) / xs.length, my = ys.reduce((a, b) => a + b) / ys.length;
    const slope = xs.reduce((s, x, i) => s + (x - mx) * (ys[i] - my), 0) / xs.reduce((s, x) => s + (x - mx) ** 2, 0);
    const x0 = Math.min(...xs), x1 = Math.max(...xs);
    charts.push(new Chart(document.getElementById("c-scatter"), {
      type: "scatter",
      data: { datasets: [
        { label: "Tələbə", data: pts.map((p, i) => ({ x: p.x, y: p.y + jitter(i), real: p.y })), backgroundColor: c.series + "b3",
          borderColor: c.surface, borderWidth: 2, pointRadius: 5, pointHoverRadius: 7, pointHitRadius: 8 },
        { type: "line", label: "Trend", data: [{ x: x0, y: my + slope * (x0 - mx) }, { x: x1, y: my + slope * (x1 - mx) }],
          borderColor: c.accent, borderWidth: 2, pointRadius: 0, borderDash: [6, 4] },
      ] },
      options: {
        responsive: true, maintainAspectRatio: false,
        scales: {
          x: { title: { display: true, text: "Ekran vaxtı, saat/gün", color: c.ink2 }, grid: { color: c.rule }, border: { display: false }, ticks: { color: c.ink3 } },
          y: { min: 0, max: 11, title: { display: true, text: "Prokrastinasiya balı", color: c.ink2 }, grid: { color: c.rule }, border: { display: false }, ticks: { color: c.ink3, stepSize: 1, callback: (v) => (v >= 1 && v <= 10 ? v : "") } },
        },
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: c.ink, titleColor: c.surface, bodyColor: c.surface, padding: 10, displayColors: false,
            filter: (item) => item.datasetIndex === 0,
            callbacks: { title: () => "", label: (item) => `Ekran: ${item.raw.x} saat, bal: ${item.raw.real}/10` },
          },
        },
      },
    }));
  })();

  // overview
  bar("c-score", K.self_score.labels, K.self_score.counts, { horizontal: false, unit: "Cavab: " });
  bar("c-start", K.start_time.labels, K.start_time.counts, { unit: "Cavab: " });
  bar("c-reason-d", K.reason.labels, K.reason.counts, { unit: "Cavab: " });
  bar("c-task", K.task.labels, K.task.counts, { unit: "Cavab: " });
  bar("c-thieves", K.thieves.labels, pctOf(K.thieves.counts), { format: pctFmt, tick: pctFmt, max: 100, tooltip: (it) => `${it.raw}% (${K.thieves.counts[it.dataIndex]} nəfər)` });
  bar("c-coping-d", K.coping.labels, pctOf(K.coping.counts), { format: pctFmt, tick: pctFmt, max: 100, tooltip: (it) => `${it.raw}% (${K.coping.counts[it.dataIndex]} nəfər)` });
  bar("c-stress", K.stress.labels, K.stress.counts, { horizontal: false, unit: "Cavab: " });
  bar("c-gpa", K.gpa.labels, K.gpa.counts, { horizontal: false, unit: "Cavab: " });

  // participants
  bar("c-age", K.age.labels, K.age.counts, { unit: "Cavab: " });
  bar("c-year", K.year.labels, K.year.counts, { unit: "Cavab: " });
  bar("c-gender", K.gender.labels, K.gender.counts, { unit: "Cavab: " });
  bar("c-field", K.field.labels, K.field.counts, { unit: "Cavab: " });
  bar("c-work", K.work.labels, K.work.counts, { unit: "Cavab: " });
  bar("c-field-score", K.field_score.labels, K.field_score.means, { format: f1, max: 10, tooltip: withN(K.field_score, "Orta bal") });

  // 100% stacked bars for cross-tabs
  function stacked(id, x, colorVars, groupLabel) {
    const c = C();
    const colors = colorVars.map(css);
    const lum = (hex) => { const n = parseInt(hex.slice(1), 16); return (0.299 * (n >> 16) + 0.587 * ((n >> 8) & 255) + 0.114 * (n & 255)) / 255; };
    const labels = x.rows.map((r) => `${groupLabel ? groupLabel(r.group) : r.group} (n=${r.n})`);
    const segLabels = {
      id: "segLabels",
      afterDatasetsDraw(chart) {
        const { ctx } = chart;
        ctx.save();
        ctx.font = '600 12px "IBM Plex Sans", system-ui, sans-serif';
        ctx.textAlign = "center"; ctx.textBaseline = "middle";
        chart.data.datasets.forEach((ds, di) => {
          chart.getDatasetMeta(di).data.forEach((bar, i) => {
            const v = ds.data[i];
            if (v < 9) return;
            ctx.fillStyle = lum(colors[di]) > 0.6 ? "#16202e" : "#ffffff";
            ctx.fillText(v + "%", (bar.base + bar.x) / 2, bar.y);
          });
        });
        ctx.restore();
      },
    };
    charts.push(new Chart(document.getElementById(id), {
      type: "bar",
      data: { labels, datasets: x.cats.map((cat, ci) => ({
        label: short(cat), data: x.rows.map((r) => r.pct[ci]), backgroundColor: colors[ci],
        borderColor: c.surface, borderWidth: { right: 2 }, borderSkipped: false, maxBarThickness: 40,
      })) },
      options: {
        indexAxis: "y", responsive: true, maintainAspectRatio: false,
        scales: {
          x: { stacked: true, max: 100, grid: { color: c.rule, drawTicks: false }, border: { display: false }, ticks: { color: c.ink3, callback: (v) => v + "%", maxTicksLimit: 5 } },
          y: { stacked: true, grid: { display: false }, border: { color: c.rule }, ticks: { color: c.ink2 } },
        },
        plugins: {
          endLabels: { show: false },
          legend: { position: "top", align: "start", labels: { color: c.ink2, boxWidth: 12, boxHeight: 12, useBorderRadius: true, borderRadius: 3, padding: 12 } },
          tooltip: { backgroundColor: c.ink, titleColor: c.surface, bodyColor: c.surface, padding: 10,
            callbacks: { label: (it) => `${it.dataset.label}: ${it.raw}%` } },
        },
      },
      plugins: [segLabels],
    }));
  }
  const byScore = (g) => `Bal ${g}`;
  stacked("c-planning", K.planning_x, ["--ord-1", "--ord-2", "--ord-3", "--ord-4"]);
  stacked("c-feeling", K.feeling_x, ["--cat-1", "--cat-2", "--cat-3", "--cat-4"], byScore);
  stacked("c-extension", K.extension_x, ["--cat-1", "--cat-3", "--cat-2"], byScore);
  stacked("c-ai", K.ai_x, ["--ord-1", "--ord-2", "--ord-4"], byScore);

  // quotes
  const q = document.getElementById("quotes");
  [...new Set(D.advice)].forEach((t) => { const li = document.createElement("li"); li.textContent = t; q.appendChild(li); });

  // repaint charts when the color scheme changes
  window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => location.reload());
})();
