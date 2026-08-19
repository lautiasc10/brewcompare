/* =============================================================
   BrewCompare — main.js
   Classic script, IIFE, no modules, no build step.
   Reads window.__DB__ (written by tools/build_site.py).

   Everything here ENRICHES pages that already work without it:
   the HTML ships the content, the prices, the spec tables, the
   server-rendered radar charts and a full default comparison.
   ============================================================= */
(function () {
  "use strict";

  var DB = window.__DB__ || { products: [], scores: [], specs: [], specGroups: [], categories: [] };
  var MAX_COMPARE = 4;
  var STORE_KEY = "bc.compare";

  /* ---------------------------------------------------------- helpers --- */
  function $(sel, scope) { return (scope || document).querySelector(sel); }
  function $$(sel, scope) { return Array.prototype.slice.call((scope || document).querySelectorAll(sel)); }
  function safe(fn, name) { try { fn(); } catch (e) { console.warn("[" + name + "]", e); } }
  function escHTML(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  var reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;

  var byId = {};
  DB.products.forEach(function (p) { byId[p.id] = p; });
  var specByKey = {};
  (DB.specs || []).forEach(function (s) { specByKey[s.key] = s; });

  function money(v) {
    if (v == null) return null;
    var s = "$" + Number(v).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    return s.replace(/\.00$/, "");
  }
  function currentPrice(p) { return p.price != null ? p.price : p.retailPrice; }
  function isDeal(p) { return p.salePrice != null && p.retailPrice != null && p.salePrice < p.retailPrice; }
  function discountPct(p) { return isDeal(p) ? Math.round(100 * (p.retailPrice - p.salePrice) / p.retailPrice) : 0; }

  var IC = {
    check: '<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="20 6 9 17 4 12"/></svg>',
    ext: '<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>'
  };

  /* --------------------------------------------------- selection state --- */
  var selection = [];

  function readStore() {
    try {
      var raw = window.sessionStorage.getItem(STORE_KEY);
      return raw ? JSON.parse(raw) : [];
    } catch (e) { return []; }
  }
  function writeStore(ids) {
    try { window.sessionStorage.setItem(STORE_KEY, JSON.stringify(ids)); } catch (e) { /* memory only */ }
  }
  function idsFromHash() {
    var m = /[#&]ids=([^&]+)/.exec(location.hash || "");
    if (!m) return null;
    return decodeURIComponent(m[1]).split(",").filter(function (id) { return !!byId[id]; });
  }
  function validate(ids) {
    var seen = {}, out = [];
    (ids || []).forEach(function (id) {
      if (byId[id] && !seen[id] && out.length < MAX_COMPARE) { seen[id] = 1; out.push(id); }
    });
    return out;
  }

  function initSelection() {
    var fromHash = idsFromHash();
    selection = validate(fromHash !== null ? fromHash : readStore());
    // Landing on the comparator with nothing chosen should show a real
    // comparison, not an empty state — mirror the server-rendered default.
    if (!selection.length && isComparePage()) {
      selection = DB.products.slice()
        .sort(function (a, b) { return b.avgScore - a.avgScore; })
        .slice(0, MAX_COMPARE)
        .map(function (p) { return p.id; });
    }
    if (fromHash !== null) writeStore(selection);
  }

  function setSelection(ids, opts) {
    selection = validate(ids);
    writeStore(selection);
    if (isComparePage() && !(opts && opts.silent)) {
      var h = selection.length ? "#ids=" + selection.join(",") : " ";
      if (history.replaceState) history.replaceState(null, "", h);
      else location.hash = h;
    }
    syncToggles();
    syncNavCount();
    if (isComparePage()) renderCompare();
  }

  function toggleProduct(id) {
    var i = selection.indexOf(id);
    if (i >= 0) { selection.splice(i, 1); }
    else {
      if (selection.length >= MAX_COMPARE) {
        flashNav("Up to " + MAX_COMPARE + " machines");
        return;
      }
      selection.push(id);
    }
    setSelection(selection);
  }

  function isComparePage() { return !!$("[data-compare-results]"); }

  /* --------------------------------------------------------- nav & UI --- */
  function initNav() {
    var btn = $("[data-nav-toggle]");
    var list = $("#nav-links");
    if (!btn || !list) return;
    btn.addEventListener("click", function () {
      var open = list.classList.toggle("is-open");
      btn.setAttribute("aria-expanded", open ? "true" : "false");
      btn.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    });
    list.addEventListener("click", function (ev) {
      if (ev.target.closest("a")) {
        list.classList.remove("is-open");
        btn.setAttribute("aria-expanded", "false");
      }
    });
    document.addEventListener("keydown", function (ev) {
      if (ev.key === "Escape" && list.classList.contains("is-open")) {
        list.classList.remove("is-open");
        btn.setAttribute("aria-expanded", "false");
        btn.focus();
      }
    });
  }

  var flashTimer = null;
  function flashNav(msg) {
    var nav = $("[data-compare-nav]");
    if (!nav) return;
    var pill = $("[data-compare-count]", nav);
    if (!pill) return;
    var prev = pill.textContent;
    pill.textContent = "max";
    pill.title = msg;
    clearTimeout(flashTimer);
    flashTimer = setTimeout(function () { pill.textContent = prev; pill.title = ""; }, 1400);
  }

  function syncNavCount() {
    $$("[data-compare-nav]").forEach(function (a) {
      a.setAttribute("data-count", String(selection.length));
      var pill = $("[data-compare-count]", a);
      if (pill) pill.textContent = String(selection.length);
      a.setAttribute("href", selection.length ? "compare.html#ids=" + selection.join(",") : "compare.html");
    });
  }

  function syncToggles() {
    $$("[data-compare-toggle]").forEach(function (btn) {
      var on = selection.indexOf(btn.getAttribute("data-compare-toggle")) >= 0;
      btn.setAttribute("aria-pressed", on ? "true" : "false");
      if (!btn.classList.contains("cmp-option")) {
        var label = btn.querySelector("span") ? null : btn;
        if (label && /compar/i.test(btn.textContent)) {
          // keep the icon, swap only the trailing words
          var svg = btn.querySelector("svg");
          btn.textContent = on ? " Added" : (svg ? " Compare" : "Compare");
          if (svg) btn.insertBefore(svg, btn.firstChild);
        }
      }
    });
  }

  function initCompareButtons() {
    document.addEventListener("click", function (ev) {
      var btn = ev.target.closest("[data-compare-toggle]");
      if (!btn) return;
      ev.preventDefault();
      toggleProduct(btn.getAttribute("data-compare-toggle"));
    });
  }

  /* --------------------------------------------------------- gallery ---- */
  function initGallery() {
    var main = $("[data-gallery-main]");
    var thumbs = $$("[data-gallery-thumb]");
    if (!main || !thumbs.length) return;
    thumbs.forEach(function (t) {
      t.addEventListener("click", function () {
        var img = $("img", t);
        if (!img) return;
        main.src = img.src;
        thumbs.forEach(function (o) { o.setAttribute("aria-current", "false"); });
        t.setAttribute("aria-current", "true");
      });
    });
    document.addEventListener("keydown", function (ev) {
      if (ev.key !== "ArrowLeft" && ev.key !== "ArrowRight") return;
      if (!document.activeElement || !document.activeElement.closest(".gallery-thumbs")) return;
      var i = thumbs.indexOf(document.activeElement);
      if (i < 0) return;
      var n = (i + (ev.key === "ArrowRight" ? 1 : thumbs.length - 1)) % thumbs.length;
      thumbs[n].focus(); thumbs[n].click();
    });
  }

  /* --------------------------------------------------------- reveals ---- */
  function initReveals() {
    var els = $$("[data-reveal]");
    if (!els.length) return;
    if (reduced || !("IntersectionObserver" in window)) {
      els.forEach(function (el) { el.classList.add("is-revealed"); });
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add("is-revealed"); io.unobserve(en.target); }
      });
    }, { threshold: 0.01, rootMargin: "0px 0px -2% 0px" });
    els.forEach(function (el) { io.observe(el); });
    // Mandatory safety net: never leave content invisible (gotcha A.8 / E.4)
    setTimeout(function () {
      $$("[data-reveal]:not(.is-revealed)").forEach(function (el) {
        if (el.getBoundingClientRect().top < window.innerHeight * 1.5) el.classList.add("is-revealed");
      });
    }, 3000);
    setTimeout(function () {
      $$("[data-reveal]:not(.is-revealed)").forEach(function (el) { el.classList.add("is-revealed"); });
    }, 8000);
  }

  /* -------------------------------------------------- category filter --- */
  function initFilters() {
    var bar = $("[data-filter-bar]");
    var grid = $("[data-machine-grid]");
    if (!bar || !grid) return;
    var empty = $("[data-empty-msg]");
    var cards = $$(".pcard", grid);
    var ids = DB.products.map(function (p) { return p.id; });

    // map each card to its product by the compare button it carries
    cards.forEach(function (card) {
      var t = $("[data-compare-toggle]", card);
      card.dataset.pid = t ? t.getAttribute("data-compare-toggle") : "";
    });

    bar.addEventListener("click", function (ev) {
      var btn = ev.target.closest("[data-filter]");
      if (!btn) return;
      var key = btn.getAttribute("data-filter");
      $$("[data-filter]", bar).forEach(function (b) {
        b.setAttribute("aria-pressed", b === btn ? "true" : "false");
      });
      var shown = 0;
      cards.forEach(function (card) {
        var p = byId[card.dataset.pid];
        var on = key === "all" || (p && p.categories.indexOf(key) >= 0);
        card.hidden = !on;
        if (on) shown++;
      });
      if (empty) empty.hidden = shown > 0;
    });
    void ids;
  }

  /* ------------------------------------------------------ radar (JS) ---- */
  function radarSVG(products, size, showValues) {
    size = size || 400;
    var axes = DB.scores || [];
    var n = axes.length;
    if (!n) return "";
    var cx = size / 2, cy = size / 2, R = size / 2 - 52;
    var series = DB.series || ["var(--s1)", "var(--s2)", "var(--s3)", "var(--s4)"];
    var out = ['<svg class="radar-svg" viewBox="0 0 ' + size + ' ' + size + '" role="img" ' +
               'aria-label="Editor scores from 0 to 10 across ' + n + ' axes">'];

    function pt(i, val) {
      var a = -Math.PI / 2 + (2 * Math.PI * i / n);
      var r = R * (val / 10);
      return [cx + r * Math.cos(a), cy + r * Math.sin(a)];
    }
    function poly(val) {
      var s = [];
      for (var i = 0; i < n; i++) { var p = pt(i, val); s.push(p[0].toFixed(1) + "," + p[1].toFixed(1)); }
      return s.join(" ");
    }

    [2, 4, 6, 8, 10].forEach(function (ring) {
      out.push('<polygon class="radar-ring' + (ring === 10 ? " radar-ring--outer" : "") +
               '" points="' + poly(ring) + '"/>');
    });
    for (var i = 0; i < n; i++) {
      var a = pt(i, 10);
      out.push('<line class="radar-axis" x1="' + cx + '" y1="' + cy + '" x2="' +
               a[0].toFixed(1) + '" y2="' + a[1].toFixed(1) + '"/>');
    }
    products.forEach(function (p, si) {
      var colour = series[si % series.length];
      var pts = [], dots = [];
      axes.forEach(function (ax, ai) {
        var v = p.scores[ax.key];
        v = (typeof v === "number") ? v : 0;
        var xy = pt(ai, v);
        pts.push(xy[0].toFixed(1) + "," + xy[1].toFixed(1));
        dots.push('<circle class="radar-dot" cx="' + xy[0].toFixed(1) + '" cy="' + xy[1].toFixed(1) +
                  '" fill="' + colour + '"/>');
      });
      out.push('<polygon class="radar-poly" points="' + pts.join(" ") + '" fill="' + colour +
               '" fill-opacity="' + (products.length > 1 ? 0.2 : 0.16) + '" stroke="' + colour + '"/>');
      out.push(dots.join(""));
    });
    axes.forEach(function (ax, ai) {
      var l = pt(ai, 10);
      var ox = l[0] - cx, oy = l[1] - cy;
      var d = Math.hypot(ox, oy) || 1;
      var tx = cx + ox / d * (R + 22), ty = cy + oy / d * (R + 22);
      var anchor = Math.abs(ox) < R * 0.25 ? "middle" : (ox > 0 ? "start" : "end");
      var dy = oy > R * 0.4 ? ".9em" : (oy < -R * 0.4 ? "-.25em" : ".35em");
      out.push('<text class="radar-label" x="' + tx.toFixed(1) + '" y="' + ty.toFixed(1) +
               '" text-anchor="' + anchor + '" dy="' + dy + '">' + escHTML(ax.label) + "</text>");
      if (showValues && products.length === 1) {
        var v = products[0].scores[ax.key];
        if (typeof v === "number") {
          var vp = pt(ai, Math.min(v + 1.35, 11.4));
          out.push('<text class="radar-value" x="' + vp[0].toFixed(1) + '" y="' + vp[1].toFixed(1) +
                   '" text-anchor="middle" dy=".35em">' + v + "</text>");
        }
      }
    });
    out.push("</svg>");
    return out.join("");
  }

  /* ------------------------------------------------ comparison render --- */
  function formatSpec(key, value) {
    var spec = specByKey[key];
    if (value == null) return { html: '<span class="spec-null" title="Not published for this model">—</span>', text: false };
    if (spec.type === "bool") {
      return {
        html: value
          ? '<span class="yes">' + IC.check + " Yes</span>"
          : '<span class="no">✕ No</span>',
        text: false
      };
    }
    if (spec.type === "number") {
      var unit = spec.unit ? ' <span class="muted">' + escHTML(spec.unit) + "</span>" : "";
      return { html: String(value) + unit, text: false };
    }
    return { html: escHTML(value), text: true };
  }

  function bestIndices(key, products) {
    var spec = specByKey[key];
    var better = spec.better || "none";
    var out = {};
    if (better === "none") return out;
    var vals = products.map(function (p) { return p.specs[key]; });
    if (spec.type === "bool") {
      var anyTrue = vals.some(function (v) { return v === true; });
      var allTrue = vals.every(function (v) { return v === true; });
      if (!anyTrue || allTrue) return out;
      vals.forEach(function (v, i) { if (v === true) out[i] = 1; });
      return out;
    }
    var nums = [];
    vals.forEach(function (v, i) { if (typeof v === "number") nums.push([i, v]); });
    if (nums.length < 2) return out;
    var uniq = {};
    nums.forEach(function (n) { uniq[n[1]] = 1; });
    if (Object.keys(uniq).length === 1) return out;
    var target = nums.reduce(function (acc, n) {
      return better === "higher" ? Math.max(acc, n[1]) : Math.min(acc, n[1]);
    }, better === "higher" ? -Infinity : Infinity);
    nums.forEach(function (n) { if (n[1] === target) out[n[0]] = 1; });
    return out;
  }

  function buyBtn(p, cls) {
    return '<a class="' + cls + '" href="' + escHTML(p.affiliateUrl) + '" target="_blank" ' +
           'rel="sponsored nofollow noopener" data-buy="' + escHTML(p.id) + '">View on Amazon ' + IC.ext + "</a>";
  }

  function verdictCards(products) {
    if (products.length < 2) return "";
    var cards = [];
    var priced = products.filter(function (p) { return currentPrice(p) != null; });
    if (priced.length) {
      var cheap = priced.reduce(function (a, b) { return currentPrice(a) <= currentPrice(b) ? a : b; });
      cards.push(["Cheapest", cheap.shortName, money(currentPrice(cheap)) + " — the lowest entry price of this selection."]);
    }
    function topBy(fn) { return products.reduce(function (a, b) { return fn(a) >= fn(b) ? a : b; }); }
    var best = topBy(function (p) { return p.avgScore; });
    cards.push(["Highest overall score", best.shortName, best.avgScore + "/10 averaged across our six axes."]);
    var coffee = topBy(function (p) { return p.scores.coffee || 0; });
    cards.push(["Best in the cup", coffee.shortName, "Scores " + coffee.scores.coffee + "/10 on coffee quality."]);
    var value = topBy(function (p) { return p.scores.value || 0; });
    cards.push(["Best value", value.shortName, "Scores " + value.scores.value + "/10 for what you get per dollar."]);

    return '<div class="cmp-verdict">' + cards.map(function (c) {
      return '<div class="verdict-card"><span class="h">' + escHTML(c[0]) + '</span>' +
             '<p class="n">' + escHTML(c[1]) + '</p><p class="w">' + escHTML(c[2]) + "</p></div>";
    }).join("") + "</div>";
  }

  function comparisonHTML(products) {
    var series = DB.series || [];
    var heads = products.map(function (p, i) {
      return '<th scope="col"><div class="cmp-col-head">' +
        '<span class="cmp-swatch" style="background:' + series[i % series.length] + '"></span>' +
        '<img src="' + escHTML(p.image) + '" alt="" loading="lazy" width="124" height="124">' +
        '<a class="t" href="' + escHTML(p.url) + '">' + escHTML(p.shortName) + "</a>" +
        '<span class="p">' + (money(currentPrice(p)) || "—") + "</span>" +
        buyBtn(p, "btn btn-primary btn-sm") + "</div></th>";
    }).join("");

    var blank = products.map(function () { return "<td></td>"; }).join("");
    var rows = [];

    // price
    rows.push('<tr class="group-row"><th scope="row">Price</th>' + blank + "</tr>");
    var prices = products.map(currentPrice);
    var valid = prices.filter(function (v) { return v != null; });
    var uniqP = {}; valid.forEach(function (v) { uniqP[v] = 1; });
    var cheapest = (valid.length > 1 && Object.keys(uniqP).length > 1) ? Math.min.apply(null, valid) : null;
    rows.push('<tr><th scope="row">Current price</th>' + prices.map(function (v) {
      return '<td class="' + (cheapest != null && v === cheapest ? "cmp-best" : "") + '">' + (money(v) || "—") + "</td>";
    }).join("") + "</tr>");

    // scores
    rows.push('<tr class="group-row"><th scope="row">Editor scores</th>' + blank + "</tr>");
    (DB.scores || []).forEach(function (sc) {
      var vals = products.map(function (p) { return p.scores[sc.key]; });
      var nums = vals.filter(function (v) { return typeof v === "number"; });
      var u = {}; nums.forEach(function (v) { u[v] = 1; });
      var best = (nums.length && Object.keys(u).length > 1) ? Math.max.apply(null, nums) : null;
      rows.push('<tr><th scope="row">' + escHTML(sc.label) + "</th>" + vals.map(function (v) {
        return '<td class="' + (best != null && v === best ? "cmp-best" : "") + '">' +
          (typeof v === "number" ? v : '<span class="spec-null">—</span>') + "</td>";
      }).join("") + "</tr>");
    });

    // specs by group
    (DB.specGroups || []).forEach(function (g) {
      var groupSpecs = (DB.specs || []).filter(function (s) { return s.group === g.id && s.compare; });
      if (!groupSpecs.length) return;
      rows.push('<tr class="group-row"><th scope="row">' + escHTML(g.name) + "</th>" + blank + "</tr>");
      groupSpecs.forEach(function (spec) {
        var best = bestIndices(spec.key, products);
        var cells = products.map(function (p, i) {
          var f = formatSpec(spec.key, p.specs[spec.key]);
          var cls = (f.text ? "is-text " : "") + (best[i] ? "cmp-best" : "");
          return '<td class="' + cls.trim() + '">' + f.html + "</td>";
        }).join("");
        rows.push('<tr><th scope="row">' + escHTML(spec.label) + "</th>" + cells + "</tr>");
      });
    });

    var legend = products.map(function (p, i) {
      return '<span class="cmp-legend-item"><i style="background:' + series[i % series.length] + '"></i>' +
             escHTML(p.shortName) + "</span>";
    }).join("");

    return '<div data-compare-render>' +
      '<div class="card card-pad" style="margin-bottom:1.6rem">' +
        '<div class="section-head" style="margin-bottom:1rem">' +
          '<span class="kicker">Score profiles overlaid</span>' +
          '<h2 style="font-size:1.4rem">The shape of each machine</h2></div>' +
        radarSVG(products, 400, products.length === 1) +
        '<div class="cmp-legend">' + legend + "</div>" +
      "</div>" +
      verdictCards(products) +
      '<div class="card card-pad" style="margin-top:1.6rem">' +
        '<div class="section-head" style="margin-bottom:1rem">' +
          '<span class="kicker">Specification by specification</span>' +
          '<h2 style="font-size:1.4rem">The full table</h2>' +
          '<p class="small">Green marks the best value in the row. A dash means the figure is not published.</p></div>' +
        '<div class="table-scroll"><table class="cmp-table">' +
          '<thead><tr><th scope="col"><span class="sr-only">Specification</span></th>' + heads + "</tr></thead>" +
          "<tbody>" + rows.join("") + "</tbody></table></div>" +
      "</div></div>";
  }

  function slotsHTML() {
    var out = selection.map(function (id) {
      var p = byId[id];
      return '<div class="slot-wrap">' +
        '<div class="slot-thumb"><img src="' + escHTML(p.image) + '" alt="" loading="lazy" width="184" height="184"></div>' +
        '<button class="slot-remove" type="button" data-compare-toggle="' + escHTML(id) +
          '" aria-label="Remove ' + escHTML(p.shortName) + ' from the comparison">✕</button>' +
        '<span class="t">' + escHTML(p.shortName) + "</span></div>";
    });
    while (out.length < 2) out.push('<div class="slot-empty" aria-hidden="true">+</div>');
    return out.join("");
  }

  function renderCompare() {
    var slots = $("[data-compare-slots]");
    if (slots) slots.innerHTML = slotsHTML();

    var host = $("[data-compare-results]");
    if (!host) return;
    var wrap = $(".wrap", host) || host;
    var products = selection.map(function (id) { return byId[id]; }).filter(Boolean);

    var target = $("[data-compare-render]", wrap);
    var html;
    if (!products.length) {
      html = '<div data-compare-render><div class="cmp-empty card">' +
        "<h3>Pick two machines to begin</h3>" +
        "<p>Choose from the list above. The full specification table, the overlaid score charts and " +
        "the row-by-row winners appear here.</p></div></div>";
    } else if (products.length === 1) {
      html = '<div data-compare-render><div class="cmp-empty card">' +
        "<h3>Add one more</h3><p>" + escHTML(products[0].shortName) +
        " is selected. Pick at least one more machine to see them side by side.</p>" +
        '<p style="margin-top:1rem"><a class="btn btn-ghost btn-sm" href="' + escHTML(products[0].url) +
        '">Open the full review instead</a></p></div></div>';
    } else {
      html = comparisonHTML(products);
    }

    if (target) target.outerHTML = html;
    else wrap.insertAdjacentHTML("beforeend", html);
  }

  function initCompareSearch() {
    var input = $("[data-compare-search]");
    var opts = $("[data-compare-options]");
    if (!input || !opts) return;
    input.addEventListener("input", function () {
      var q = input.value.trim().toLowerCase();
      $$(".cmp-option", opts).forEach(function (o) {
        o.hidden = !!q && (o.getAttribute("data-search") || "").indexOf(q) < 0;
      });
    });
  }

  /* ------------------------------------------------------------- TOC ---- */
  function initToc() {
    var toc = $(".toc");
    if (!toc || !("IntersectionObserver" in window)) return;
    var links = $$("a[href^='#']", toc);
    if (!links.length) return;
    var map = {};
    links.forEach(function (a) {
      var el = document.getElementById(a.getAttribute("href").slice(1));
      if (el) map[el.id] = a;
    });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        links.forEach(function (a) { a.classList.remove("is-active"); });
        if (map[en.target.id]) map[en.target.id].classList.add("is-active");
      });
    }, { rootMargin: "-15% 0px -70% 0px", threshold: 0.01 });
    Object.keys(map).forEach(function (id) {
      var el = document.getElementById(id);
      if (el) io.observe(el);
    });
  }

  /* -------------------------------------------------- anchor scrolling -- */
  function initAnchors() {
    document.addEventListener("click", function (ev) {
      var a = ev.target.closest('a[href^="#"]');
      if (!a) return;
      var id = a.getAttribute("href");
      if (!id || id === "#" || id.indexOf("#ids=") === 0) return;
      var el = document.querySelector(id);
      if (!el) return;
      ev.preventDefault();
      var offset = 88;
      window.scrollTo({
        top: el.getBoundingClientRect().top + window.scrollY - offset,
        behavior: reduced ? "auto" : "smooth"
      });
      if (history.pushState) history.pushState(null, "", id);
    });
  }

  /* ------------------------------------------------------------- boot --- */
  function boot() {
    safe(initSelection, "initSelection");
    safe(initNav, "initNav");
    safe(initCompareButtons, "initCompareButtons");
    safe(initGallery, "initGallery");
    safe(initReveals, "initReveals");
    safe(initFilters, "initFilters");
    safe(initCompareSearch, "initCompareSearch");
    safe(initToc, "initToc");
    safe(initAnchors, "initAnchors");
    safe(syncToggles, "syncToggles");
    safe(syncNavCount, "syncNavCount");

    if (isComparePage()) {
      // Do not gate the first render on IntersectionObserver (gotcha E.4)
      safe(renderCompare, "renderCompare");
      window.addEventListener("hashchange", function () {
        var ids = idsFromHash();
        if (ids !== null) setSelection(ids, { silent: true });
      });
    }

    document.documentElement.classList.add("is-ready");
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
