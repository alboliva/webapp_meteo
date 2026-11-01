"""
gallery_export.py — genera la Gallery Webcam come file HTML autonomo.

Foto congelate (incorporate nel file) oppure live (URL).
Tutte le foto sono cliccabili (lightbox con frecce, ESC, download).
"""

import base64
import html as _html
import mimetypes
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import requests

from common import ZONE_LABELS, cache_bust

_GALLERY_TEMPLATE = """<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>__TITLE__ — __NOW__</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400&display=swap');
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    background: #0f172a; color: #e2e8f0;
    font-family: 'DM Sans', sans-serif; padding: 32px 24px;
    -webkit-font-smoothing: antialiased;
  }
  header { margin-bottom: 36px; border-bottom: 1px solid #1e293b; padding-bottom: 20px; }
  header h1 {
    font-family: 'DM Serif Display', serif;
    font-size: 2.2rem; font-weight: 400; color: #f1f5f9; letter-spacing: -0.02em;
  }
  header p {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem; color: #64748b; margin-top: 8px; line-height: 1.7;
  }
  header .tag {
    display:inline-block; margin:10px 6px 0 0; padding:3px 10px; border-radius:20px;
    background:#1e293b; border:1px solid #334155; color:#94a3b8;
    font-family:'IBM Plex Mono',monospace; font-size:0.62rem; letter-spacing:0.05em;
  }
  nav.toc { margin: -16px 0 32px; display:flex; flex-wrap:wrap; gap:6px; }
  nav.toc a {
    font-family:'IBM Plex Mono',monospace; font-size:0.66rem; color:#94a3b8;
    text-decoration:none; border:1px solid #334155; border-radius:20px; padding:3px 10px;
  }
  nav.toc a:hover { color:#e2e8f0; border-color:#64748b; }
  section { margin-bottom: 48px; }
  section h2 {
    font-family: 'DM Serif Display', serif;
    font-size: 1.4rem; font-weight: 400; color: #94a3b8;
    margin-bottom: 18px; padding-bottom: 8px; border-bottom: 1px solid #1e293b;
    display:flex; align-items:center; gap:10px; flex-wrap:wrap;
  }
  section h3 {
    font-family:'IBM Plex Mono',monospace; font-size:0.75rem; font-weight:400;
    color:#64748b; letter-spacing:0.08em; text-transform:uppercase;
    margin: 22px 0 10px;
  }
  .cnt {
    font-family:'IBM Plex Mono',monospace; font-size:0.6rem; color:#64748b;
    background:#1e293b; border:1px solid #334155; border-radius:20px; padding:2px 9px;
  }
  .grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; }
  .grid.hist { grid-template-columns: repeat(4, 1fr); gap: 12px; }
  .card {
    background: #1e293b; border-radius: 12px; overflow: hidden;
    border: 1px solid #334155; cursor: zoom-in; margin: 0;
    transition: transform .18s, box-shadow .18s, border-color .18s;
  }
  .card:hover { transform: translateY(-3px); box-shadow: 0 14px 34px rgba(0,0,0,.55); border-color:#475569; }
  .card img { width: 100%; display: block; aspect-ratio: 4/3; object-fit: cover; background: #0f172a; }
  .card figcaption {
    font-size: 0.78rem; font-weight: 600; color: #cbd5e1;
    padding: 10px 14px; text-align: center;
    background: #1e293b; border-top: 1px solid #334155; letter-spacing: 0.02em;
  }
  .grid.hist .card figcaption { font-size:0.68rem; padding:6px 8px; font-family:'IBM Plex Mono',monospace; font-weight:400; }
  footer {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.62rem; color: #475569;
    margin-top: 48px; padding-top: 16px; border-top: 1px solid #1e293b; line-height: 1.9;
  }
  .lightbox {
    position: fixed; inset: 0; z-index: 9999; background: rgba(7,11,20,.96);
    display: none; align-items: center; justify-content: center; backdrop-filter: blur(4px);
  }
  .lightbox.on { display: flex; }
  .lb-img { max-width: 95vw; max-height: 88vh; object-fit: contain; border-radius: 8px; box-shadow: 0 24px 80px rgba(0,0,0,.7); }
  .lb-cap {
    position: fixed; bottom: 22px; left: 50%; transform: translateX(-50%);
    font-family: 'DM Sans', sans-serif; font-size: 0.95rem; font-weight: 600;
    color: #f1f5f9; background: rgba(15,23,42,.85);
    padding: 8px 18px; border-radius: 24px; border: 1px solid #334155;
    max-width: 80vw; text-align: center;
  }
  .lb-btn {
    position: fixed; background: rgba(30,41,59,.85); color: #e2e8f0;
    border: 1px solid #475569; cursor: pointer; user-select: none;
    width: 52px; height: 52px; border-radius: 50%;
    font-size: 1.6rem; line-height: 1; display:flex; align-items:center; justify-content:center;
    transition: background .15s, transform .15s;
  }
  .lb-btn:hover { background: #334155; }
  .lb-close { top: 20px; right: 20px; font-size: 1.5rem; }
  .lb-prev  { left: 18px; top: 50%; transform: translateY(-50%); }
  .lb-next  { right: 18px; top: 50%; transform: translateY(-50%); }
  .lb-dl {
    position: fixed; top: 20px; left: 20px;
    background: rgba(30,41,59,.85); color: #e2e8f0; text-decoration: none;
    border: 1px solid #475569; border-radius: 24px; padding: 9px 16px;
    font-family: 'DM Sans', sans-serif; font-size: 0.8rem; font-weight: 600;
  }
  .lb-dl:hover { background: #334155; }
  @media (max-width: 900px) { .grid.hist { grid-template-columns: repeat(3, 1fr); } }
  @media (max-width: 768px) {
    .grid { grid-template-columns: repeat(2, 1fr); }
    .grid.hist { grid-template-columns: repeat(2, 1fr); }
    .lb-btn { width: 44px; height: 44px; font-size: 1.3rem; }
  }
  @media (max-width: 480px) {
    .grid { grid-template-columns: 1fr; }
    .lb-cap { bottom: 80px; }
  }
</style>
</head>
<body>
<header>
  <h1>📷 __TITLE__</h1>
  <p>Esportata il __NOW__ · Open-Meteo (ECMWF) · __COUNT__ foto</p>
  __TAGS__
</header>
__TOC__
__SEZIONI__
<footer>
  Dati meteo: Open-Meteo Forecast (ECMWF IFS)<br>
  __MODE__ · Gallery esportata il __NOW__<br>
  Clicca una foto per vederla grande · frecce ← → o tasti per navigare · ESC per chiudere
</footer>

<div id="lb" class="lightbox">
  <a id="lb-dl" class="lb-dl" download>⬇︎ Salva foto</a>
  <button class="lb-btn lb-close" title="Chiudi (ESC)">&times;</button>
  <button class="lb-btn lb-prev"  title="Precedente (←)">&#8249;</button>
  <img id="lb-img" class="lb-img" alt="">
  <button class="lb-btn lb-next"  title="Successiva (→)">&#8250;</button>
  <div id="lb-cap" class="lb-cap"></div>
</div>

<script>
  var figs = Array.prototype.slice.call(document.querySelectorAll('.card'));
  var lb = document.getElementById('lb'), lbImg = document.getElementById('lb-img'),
      lbCap = document.getElementById('lb-cap'), lbDl = document.getElementById('lb-dl');
  var idx = -1;
  function slug(s){ return (s||'foto').replace(/[^a-z0-9]+/gi,'_').replace(/^_|_$/g,'').toLowerCase(); }
  function open(i){
    idx = i; var f = figs[i], img = f.querySelector('img'), cap = f.getAttribute('data-cap') || '';
    lbImg.src = img.currentSrc || img.src; lbImg.alt = cap; lbCap.textContent = cap;
    lbDl.href = img.currentSrc || img.src; lbDl.setAttribute('download', slug(cap) + '.jpg');
    lb.classList.add('on'); document.body.style.overflow = 'hidden';
  }
  function close(){ lb.classList.remove('on'); document.body.style.overflow=''; }
  function step(d){
    if(!figs.length) return; var i = idx;
    for(var k=0;k<figs.length;k++){ i = (i + d + figs.length) % figs.length;
      if(figs[i].style.display !== 'none'){ open(i); return; } }
  }
  figs.forEach(function(f,i){ f.addEventListener('click', function(){ open(i); }); });
  document.querySelector('.lb-close').addEventListener('click', close);
  document.querySelector('.lb-prev').addEventListener('click', function(e){ e.stopPropagation(); step(-1); });
  document.querySelector('.lb-next').addEventListener('click', function(e){ e.stopPropagation(); step(1); });
  lb.addEventListener('click', function(e){ if(e.target === lb) close(); });
  document.addEventListener('keydown', function(e){
    if(!lb.classList.contains('on')) return;
    if(e.key === 'Escape') close(); else if(e.key === 'ArrowLeft') step(-1); else if(e.key === 'ArrowRight') step(1);
  });
</script>
</body>
</html>"""

_GIORNI = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]


def _esc(s):
    return _html.escape(str(s), quote=True)


def _img_to_data_uri(url, cb, timeout=12):
    try:
        r = requests.get(cache_bust(url, cb), timeout=timeout, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        ct = r.headers.get("Content-Type", "").split(";")[0].strip()
        if not ct.startswith("image"):
            ct = mimetypes.guess_type(url)[0] or "image/jpeg"
        return f"data:{ct};base64,{base64.b64encode(r.content).decode('ascii')}"
    except Exception:
        return None


def _card(src, cap):
    return (f'<figure class="card" data-cap="{_esc(cap)}">'
            f'<img src="{src}" loading="lazy" alt="{_esc(cap)}" '
            f"onerror=\"this.closest('figure').style.display='none'\">"
            f'<figcaption>{_esc(cap)}</figcaption></figure>')


def genera_html_gallery(zone_dict, cb, freeze=True, titolo="Gallery Webcam", tags=None):
    """
    zone_dict : {zona: [cam,...]}  (cam = dict con chiave, nome, url, temp)
    freeze=True  -> scarica e incorpora le foto (snapshot fisso del momento)
    freeze=False -> usa gli URL live
    """
    now_exp = datetime.now().strftime("%d/%m/%Y %H:%M")

    # ── foto attuali ─────────────────────────────────────────────────────────
    src_map = {}
    if zone_dict:
        uniq = {}
        for cams in zone_dict.values():
            for cam in cams:
                uniq.setdefault(cam["chiave"], cam["url"])
        if freeze:
            with ThreadPoolExecutor(max_workers=8) as ex:
                for ch, uri in ex.map(lambda kv: (kv[0], _img_to_data_uri(kv[1], cb)), uniq.items()):
                    src_map[ch] = uri or cache_bust(uniq[ch], cb)
        else:
            src_map = {ch: cache_bust(u, cb) for ch, u in uniq.items()}

    sezioni, toc, n_foto = "", [], 0

    for zona, cams in zone_dict.items():
        label = ZONE_LABELS.get(zona, zona)
        celle = ""
        for cam in cams:
            t_str = f" · {cam['temp']:.1f}°C" if cam.get("temp") is not None else ""
            celle += _card(src_map[cam["chiave"]], f"{cam['nome']}{t_str}")
            n_foto += 1
        anchor = f"z-{zona.lower()}"
        toc.append((anchor, label))
        sezioni += (f'<section id="{anchor}"><h2>{_esc(label)} <span class="cnt">{len(cams)}</span></h2>'
                    f'<div class="grid">{celle}</div></section>')

    modo = "📸 Snapshot congelato (foto fisse del momento)" if freeze \
        else "🔄 Live (le foto si aggiornano riaprendo)"
    tag_html = "".join(f'<span class="tag">{_esc(t)}</span>' for t in ([modo] + (tags or [])))
    toc_html = ("<nav class='toc'>" + "".join(f'<a href="#{a}">{_esc(l)}</a>' for a, l in toc) + "</nav>"
                if len(toc) > 1 else "")

    return (_GALLERY_TEMPLATE
            .replace("__TITLE__", _esc(titolo))
            .replace("__NOW__", now_exp)
            .replace("__COUNT__", str(n_foto))
            .replace("__MODE__", _esc(modo))
            .replace("__TAGS__", tag_html)
            .replace("__TOC__", toc_html)
            .replace("__SEZIONI__", sezioni))
