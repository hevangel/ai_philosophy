/* The Philosophy Readings knowledge-base explorer.
 *
 * A two-pane explorer for knowledge-base/readings-kb: problem entries by
 * subfield, book maps, the Carneades lecture register, and a build guide.
 * Rendered into the host SPA at the /readings route; content comes from
 * data.json (built by scratchpad/readings_kb/build_data.py from the
 * knowledge-base markdown, which stays the source of truth).
 */
(function () {
  'use strict';

  var DATA_PATH = 'knowledge-base/readings-kb/data.json';
  var BASE_DIR = 'knowledge-base/readings-kb/';
  var dataPromise = null;
  var state = {
    ctx: null, data: null, parts: null,
    tab: 'problems', query: '', sub: '', lectureStatus: '', listOpen: false
  };
  var TABS = [
    ['problems', 'Problems'],
    ['books', 'Books'],
    ['lectures', 'Lectures'],
    ['guide', 'Guide']
  ];
  var STATUS_LABELS = { assigned: 'Assigned', unassigned: 'Unassigned', unusable: 'Unusable' };

  function e(value) {
    return String(value == null ? '' : value)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;')
      .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  /* ------------------------------------------------ markdown -> safe html */

  function fallbackMd(text) {
    var html = e(text || '');
    html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, function (m, label, href) {
      return '<a href="' + href + '">' + label + '</a>';
    });
    html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>');
    if (/\n\n|^- /m.test(html)) {
      var parts = html.split(/\n\n+/).map(function (p) {
        if (/^- /m.test(p)) {
          var items = p.split(/\n(?=- )/).map(function (li) {
            return '<li>' + li.replace(/^- /, '') + '</li>';
          }).join('');
          return '<ul>' + items + '</ul>';
        }
        return '<p>' + p.replace(/\n/g, ' ') + '</p>';
      });
      html = parts.join('');
    }
    return html;
  }

  // Render markdown, then rewrite links: sibling .md files become in-app
  // routes (entry files -> their problem page), external links open in tabs.
  function md(text) {
    var html;
    try {
      html = window.marked ? window.marked.parse(text || '') : fallbackMd(text);
    } catch (err) {
      html = fallbackMd(text);
    }
    if (window.DOMPurify) html = window.DOMPurify.sanitize(html);
    var tpl = document.createElement('template');
    tpl.innerHTML = html;
    var links = tpl.content.querySelectorAll('a[href]');
    for (var i = 0; i < links.length; i++) {
      var a = links[i];
      var href = a.getAttribute('href') || '';
      var mdMatch = href.match(/^([\w.-]+)\.md$/);
      if (mdMatch) {
        if (state.data && state.data.entries[mdMatch[1]]) {
          a.setAttribute('href', problemHref(mdMatch[1]));
        } else {
          a.setAttribute('href', state.ctx.appUrl('md/' + encodeURIComponent(BASE_DIR + mdMatch[0])));
        }
      } else if (/^https?:/i.test(href)) {
        if (/youtube\.com\/watch\?v=([\w-]+)/i.test(href)) a.classList.add('rk-yt-link');
        a.setAttribute('target', '_blank');
        a.setAttribute('rel', 'noopener noreferrer');
      } else if (href.charAt(0) !== '#') {
        a.setAttribute('href', state.ctx.appUrl('md/' + encodeURIComponent(BASE_DIR + href)));
        a.setAttribute('target', '_blank');
        a.setAttribute('rel', 'noopener noreferrer');
      }
    }
    return tpl.innerHTML;
  }

  /* ------------------------------------------------------------- helpers */

  function data() { return state.data; }

  function href(tail) {
    tail = String(tail || '').replace(/^\/+/, '');
    return state.ctx.appUrl('readings' + (tail ? '/' + tail : ''));
  }
  function problemHref(slug) { return href('problem/' + encodeURIComponent(slug)); }
  function bookHref(id) { return href('book/' + encodeURIComponent(id)); }
  function lectureHref(id) { return href('lecture/' + encodeURIComponent(id)); }
  function ytUrl(id) { return 'https://www.youtube.com/watch?v=' + encodeURIComponent(id); }

  function subfield(id) {
    var subs = data().subfields;
    for (var i = 0; i < subs.length; i++) if (subs[i].id === id) return subs[i];
    return { id: id, name: id, glyph: '·', hue: 210, entries: [] };
  }

  function seal(s, extra) {
    return '<span class="rk-seal' + (extra ? ' ' + extra : '') + '" style="--h:' + (s.hue || 210) + '" aria-hidden="true">' + e(s.glyph || '·') + '</span>';
  }

  function escAttr(s) { return e(s); }

  function shortBookTitle(book) {
    // catalogue line from index.md, else the map title; strip markup noise
    var t = book.catalog || book.title;
    return t.replace(/\*/g, '').split(' — ')[0].slice(0, 68);
  }

  function argCount(entry) {
    var n = 0;
    entry.positions.forEach(function (p) {
      p.blocks.forEach(function (b) { if (b.type === 'arg') n += 1; });
    });
    return n;
  }

  function crumbs(items) {
    var out = ['<a href="' + href('') + '">Readings KB</a>'];
    items.forEach(function (item) {
      // plain-text items are constants from this file; html items (the
      // subfield link) are built here and trusted
      out.push(typeof item === 'string' && item.indexOf('<') === -1 ? e(item) : item);
    });
    return '<div class="rk-breadcrumbs">' + out.join(' <span aria-hidden="true">›</span> ') + '</div>';
  }

  function chip(to, label, extra) {
    return '<a class="rk-chip' + (extra ? ' ' + extra : '') + '" href="' + to + '">' + label + '</a>';
  }

  function problemChip(slug, label) {
    var entry = data().entries[slug];
    return chip(problemHref(slug), e(label || (entry && entry.title) || slug));
  }

  function bookChip(id) {
    var book = data().books[id];
    return chip(bookHref(id), '<span class="rk-chip-num">' + e(book.num) + '</span>' + e(shortBookTitle(book)));
  }

  function ytChip(id, title) {
    return '<a class="rk-yt" href="' + e(ytUrl(id)) + '" target="_blank" rel="noopener noreferrer">' +
      '<span class="rk-yt-play" aria-hidden="true">▶</span>' + e(title || (data().lectures[id] && data().lectures[id].title) || id) + '</a>';
  }

  function flagBadges(book) {
    var out = '';
    if (book.flags.mislabelled) out += '<span class="rk-flag rk-flag-warn" title="The folder holds a different book than its catalogue name">⚠ mislabelled</span>';
    if (book.flags.no_text) out += '<span class="rk-flag rk-flag-warn" title="No extractable book text exists in the corpus">◌ no text</span>';
    if (book.flags.reconstruction) out += '<span class="rk-flag" title="Reconstructed table of contents, not book text">↻ reconstruction</span>';
    if (book.flags.stubs && !book.flags.no_text) out += '<span class="rk-flag" title="Some chapters are citation stubs only">▤ stubs</span>';
    return out;
  }

  /* ------------------------------------------------------- sidebar lists */

  function problemRows() {
    var q = state.query.trim().toLowerCase();
    var subs = data().subfields;
    var rows = [];
    subs.forEach(function (s) {
      if (state.sub && s.id !== state.sub) return;
      s.entries.forEach(function (slug) {
        var entry = data().entries[slug];
        if (!entry) return;
        if (q) {
          var hay = (entry.title + ' ' + entry.aka + ' ' + entry.note + ' ' + entry.question + ' ' +
            entry.positions.map(function (p) { return p.name; }).join(' ')).toLowerCase();
          if (hay.indexOf(q) === -1) return;
        }
        rows.push({ sub: s, entry: entry });
      });
    });
    return rows;
  }

  function bookRows() {
    var q = state.query.trim().toLowerCase();
    return Object.keys(data().books).map(function (id) { return data().books[id]; })
      .filter(function (b) {
        if (!q) return true;
        return (b.title + ' ' + b.catalog + ' ' + b.layer).toLowerCase().indexOf(q) !== -1;
      })
      .sort(function (a, b) {
        return a.num === b.num ? a.title.localeCompare(b.title) : (a.num < b.num ? -1 : 1);
      });
  }

  function lectureRows() {
    var q = state.query.trim().toLowerCase();
    var rows = Object.keys(data().lectures).map(function (id) { return data().lectures[id]; });
    if (state.lectureStatus === 'frontdoor') {
      rows = rows.filter(function (l) { return l.refs.some(function (r) { return r.star; }); });
    } else if (state.lectureStatus) {
      rows = rows.filter(function (l) { return l.status === state.lectureStatus; });
    }
    if (q) rows = rows.filter(function (l) { return l.title.toLowerCase().indexOf(q) !== -1; });
    rows.sort(function (a, b) { return a.title.localeCompare(b.title); });
    return rows;
  }

  function renderList() {
    var target = document.getElementById('rk-list');
    var count = document.getElementById('rk-result-count');
    if (!target || !count) return;
    var html = '';
    var n = 0;
    if (state.tab === 'problems') {
      var rows = problemRows();
      n = rows.length;
      if (!n) {
        html = '<div class="rk-empty-list">No problems match. Try another search or subfield.</div>';
      } else if (state.query.trim() || state.sub) {
        rows.forEach(function (row) {
          html += listLink(problemHref(row.entry.slug), e(row.entry.title),
            '<span class="rk-list-sub" style="--h:' + row.sub.hue + '">' + e(row.sub.name) + '</span>',
            selectedId('problem') === row.entry.slug);
        });
      } else {
        data().subfields.forEach(function (s) {
          var mine = rows.filter(function (r) { return r.sub.id === s.id; });
          if (!mine.length) return;
          html += '<div class="rk-list-group" style="--h:' + s.hue + '">' + seal(s, 'rk-seal-sm') +
            '<span>' + e(s.name) + '</span><span class="rk-list-group-n">' + mine.length + '</span></div>';
          mine.forEach(function (row) {
            html += listLink(problemHref(row.entry.slug), e(row.entry.title),
              row.entry.pilot ? '<span class="rk-list-star" title="Pilot entry — start here">★</span>' : '',
              selectedId('problem') === row.entry.slug);
          });
        });
      }
    } else if (state.tab === 'books') {
      var brows = bookRows();
      n = brows.length;
      if (!n) {
        html = '<div class="rk-empty-list">No books match.</div>';
      }
      brows.forEach(function (b) {
        var flags = (b.flags.mislabelled ? ' ⚠' : '') + (b.flags.no_text ? ' ◌' : '') + (b.flags.reconstruction ? ' ↻' : '');
        html += listLink(bookHref(b.id), e(b.num) + ' · ' + e(shortBookTitle(b)), flags ? '<span class="rk-list-flag" title="Caveats — see the book page">' + flags + '</span>' : '',
          selectedId('book') === b.id);
      });
    } else if (state.tab === 'lectures') {
      var lrows = lectureRows();
      n = lrows.length;
      if (!n) {
        html = '<div class="rk-empty-list">No lectures match.</div>';
      }
      lrows.forEach(function (l) {
        var star = l.refs.some(function (r) { return r.star; });
        var mark = l.status === 'unusable' ? '<span class="rk-list-flag" title="Unusable — ' + e(l.note) + '">✕</span>'
          : star ? '<span class="rk-list-star" title="Front door for a problem entry">★</span>' : '';
        html += listLink(lectureHref(l.id), e(l.title), mark, selectedId('lecture') === l.id);
      });
    }
    count.textContent = n ? n + ' shown' : '';
    target.innerHTML = html;
  }

  function listLink(url, label, badge, active) {
    return '<a class="rk-list-link' + (active ? ' active' : '') + '" href="' + url + '"><span class="rk-list-label">' + label + '</span>' +
      (badge || '') + '</a>';
  }

  function selectedId(kind) {
    return state.parts[1] === kind && state.parts[2] ? decodeURIComponent(state.parts[2]) : null;
  }

  /* ---------------------------------------------------------------- shell */

  function shell(detail) {
    var stats = data().stats;
    var selected = state.parts.length > 2;
    var toolbar =
      '<div class="rk-toolbar" aria-label="Explorer controls">' +
      (state.tab === 'guide' ? '' :
      '<label class="rk-search-wrap"><span class="rk-search-icon" aria-hidden="true">⌕</span>' +
      '<span class="sr-only">Search the current list</span>' +
      '<input class="rk-search" id="rk-search" type="search" value="' + escAttr(state.query) + '" placeholder="' +
      (state.tab === 'lectures' ? 'Search 817 lectures…' : state.tab === 'books' ? 'Search the book shelf…' : 'Search the problems…') +
      '" autocomplete="off"></label>') +
      '<div class="rk-tabs" role="group" aria-label="Browse by">' +
      TABS.map(function (t) {
        return '<button class="rk-tab' + (state.tab === t[0] ? ' active' : '') + '" type="button" data-rk-tab="' + t[0] + '">' + t[1] + '</button>';
      }).join('') + '</div>' +
      (state.tab === 'problems' ? '<select class="rk-select" id="rk-sub" aria-label="Subfield">' + subOptions() + '</select>' : '') +
      (state.tab === 'lectures' ? '<select class="rk-select" id="rk-status" aria-label="Assignment status">' + statusOptions() + '</select>' : '') +
      '</div>';

    var sidebar =
      (selected ? '<button class="rk-mobile-browse" type="button" data-rk-browse aria-expanded="' + (state.listOpen ? 'true' : 'false') + '">Browse ' +
        e(state.tab) + '<span aria-hidden="true">▾</span></button>' : '') +
      '<aside class="rk-sidebar" aria-label="Browse results">' +
      '<div class="rk-sidebar-head"><strong>' + e(tabLabel()) + '</strong><span class="rk-result-count" id="rk-result-count"></span></div>' +
      '<nav class="rk-list" id="rk-list"></nav></aside>';

    return '<div class="rk-shell' + (selected ? ' rk-has-detail' : '') + (state.listOpen ? ' rk-list-open' : '') + '">' +
      (state.tab === 'guide' ? '' : hero()) +
      toolbar +
      (state.tab === 'guide'
        ? '<main class="rk-main rk-main-full">' + detail + '</main>'
        : '<div class="rk-grid">' + sidebar + '<main class="rk-main">' + detail + '</main></div>') +
      '</div>';
  }

  function tabLabel() {
    for (var i = 0; i < TABS.length; i++) if (TABS[i][0] === state.tab) return TABS[i][1];
    return '';
  }

  function subOptions() {
    var out = ['<option value="">All subfields</option>'];
    data().subfields.forEach(function (s) {
      if (!s.entries.length) return;
      out.push('<option value="' + escAttr(s.id) + '"' + (state.sub === s.id ? ' selected' : '') + '>' +
        e(s.name) + ' (' + s.entries.length + ')</option>');
    });
    return out.join('');
  }

  function statusOptions() {
    return ['<option value="">All lectures</option>',
      '<option value="frontdoor"' + (state.lectureStatus === 'frontdoor' ? ' selected' : '') + '>★ Front doors</option>',
      '<option value="assigned"' + (state.lectureStatus === 'assigned' ? ' selected' : '') + '>Assigned</option>',
      '<option value="unassigned"' + (state.lectureStatus === 'unassigned' ? ' selected' : '') + '>Unassigned</option>',
      '<option value="unusable"' + (state.lectureStatus === 'unusable' ? ' selected' : '') + '>Unusable</option>'].join('');
  }

  function hero() {
    var stats = data().stats;
    return '<header class="rk-hero"><div class="rk-eyebrow">A problem-based knowledge base</div>' +
      '<h1>The Philosophy Readings</h1>' +
      '<p>Fifty-three standing problems of philosophy, each built from what the sources actually say: a 90-second lecture version up front, then the positions with faithful premise-by-premise reconstructions — and the books and lectures behind every claim one click away.</p>' +
      '<div class="rk-stats">' +
      '<span class="rk-stat"><strong>' + stats.entries + '</strong> problems</span>' +
      '<span class="rk-stat"><strong>' + stats.subfields + '</strong> subfields</span>' +
      '<span class="rk-stat"><strong>' + stats.books + '</strong> book maps</span>' +
      '<span class="rk-stat"><strong>' + stats.lectures_total + '</strong> lectures indexed</span>' +
      '<span class="rk-stat"><strong>' + stats.lectures_assigned + '</strong> assigned to entries</span>' +
      '</div></header>';
  }

  /* ------------------------------------------------------------ home page */

  function homeDetail() {
    var stats = data().stats;
    var subs = data().subfields;
    var pilots = ['external-world-skepticism', 'gettier-and-the-analysis-of-knowledge', 'problem-of-induction'];
    var assignedPct = Math.round(100 * stats.lectures_assigned / stats.lectures_total);

    var subCards = subs.map(function (s) {
      if (s.unbuilt) {
        return '<div class="rk-subcard rk-subcard-ghost" style="--h:' + s.hue + '">' +
          '<div class="rk-subcard-head">' + seal(s) + '<strong>' + e(s.name) + '</strong></div>' +
          '<p>' + e(s.blurb) + '</p></div>';
      }
      var examples = s.entries.slice(0, 3).map(function (slug) {
        return '<a href="' + problemHref(slug) + '">' + e(data().entries[slug].title) + '</a>';
      }).join(' · ');
      return '<div class="rk-subcard" style="--h:' + s.hue + '">' +
        '<div class="rk-subcard-head">' + seal(s) +
        '<a href="' + href('problems') + '" data-rk-sublink="' + escAttr(s.id) + '"><strong>' + e(s.name) + '</strong></a>' +
        '<span class="rk-subcard-n">' + s.entries.length + '</span></div>' +
        '<p>' + e(s.blurb) + '</p>' +
        '<div class="rk-subcard-links">' + examples + '</div></div>';
    }).join('');

    var doors = pilots.map(function (slug, i) {
      var entry = data().entries[slug];
      var s = subfield(entry.subfield);
      return '<a class="rk-door" style="--h:' + s.hue + '" href="' + problemHref(slug) + '">' +
        '<span class="rk-door-n">' + (i + 1) + '</span>' +
        '<span class="rk-door-body"><strong>' + e(entry.title) + '</strong>' +
        '<span>' + e(s.name) + ' · ' + entry.positions.length + ' positions · ' + argCount(entry) + ' reconstructed arguments</span></span>' +
        '<span class="rk-door-go" aria-hidden="true">→</span></a>';
    }).join('');

    return '<section class="rk-panel">' +
      '<h2 class="rk-section-title">Start here — three doors</h2>' +
      '<p class="rk-lede">The pilot trio, built first and built deepest. Each opens with a 90-second lecture, then sets out the positions and their canonical arguments.</p>' +
      '<div class="rk-doors">' + doors + '</div>' +
      '<h2 class="rk-section-title">Browse by subfield</h2>' +
      '<div class="rk-subcards">' + subCards + '</div>' +
      '<h2 class="rk-section-title">The three layers</h2>' +
      '<div class="rk-layers">' +
      '<a class="rk-layer" href="' + href('problems') + '"><strong>' + stats.entries + '</strong><span>Problem entries<span class="rk-layer-sub">positions → arguments → objections</span></span></a>' +
      '<a class="rk-layer" href="' + href('books') + '"><strong>' + stats.books + '</strong><span>Book maps<span class="rk-layer-sub">chapter by chapter, with caveats kept</span></span></a>' +
      '<a class="rk-layer" href="' + href('lectures') + '"><strong>' + stats.lectures_total + '</strong><span>Lecture transcripts<span class="rk-layer-sub">' + stats.lectures_assigned + ' assigned · ' + stats.lectures_unassigned + ' awaiting their problems</span></span></a>' +
      '</div>' +
      '<div class="rk-meter-wrap"><div class="rk-meter-label">Lecture coverage — ' + stats.lectures_assigned + ' of ' + stats.lectures_total + ' transcripts serve a problem entry</div>' +
      '<div class="rk-meter" role="img" aria-label="' + assignedPct + '% assigned"><div class="rk-meter-fill" style="width:' + assignedPct + '%"></div></div>' +
      '<div class="rk-meter-note">Unassigned lectures are candidates for future entries, not discards — most are definitional drills waiting for a book that supports them.</div></div>' +
      '<div class="rk-start">Every number above is an exact count of what the corpus holds — gaps are recorded in the <a href="' + href('guide') + '">build guide</a>, never padded over.</div>' +
      '</section>';
  }

  /* -------------------------------------------------------- problem pages */

  function anchorNav(entry) {
    var items = [['q', 'The question'], ['ninety', '90 seconds'], ['positions', 'Positions (' + entry.positions.length + ')']];
    if (entry.thought.length) items.push(['thought', 'Thought experiments']);
    if (entry.ladder.length) items.push(['ladder', 'Source ladder']);
    items.push(['verdict', 'Where it stands'], ['connections', 'Connections'], ['sources', 'Sources read']);
    return '<nav class="rk-anchors" aria-label="In this entry">' + items.map(function (it) {
      return '<a href="#rk-' + it[0] + '" data-rk-anchor="rk-' + it[0] + '">' + e(it[1]) + '</a>';
    }).join('') + '</nav>';
  }

  function renderBlock(b) {
    if (b.type === 'arg') {
      var steps = b.steps.map(function (s) {
        var isC = s.tag.charAt(0) === '∴' || s.tag === 'C';
        return '<div class="' + (isC ? 'rk-conc' : 'rk-prem') + '"><span class="rk-step" aria-hidden="true">' + e(s.tag) + '</span>' +
          '<div class="rk-step-text">' + md(s.text) + '</div></div>';
      }).join('');
      return '<div class="rk-arg">' +
        (b.label || b.source ? '<div class="rk-arg-head">' + (b.label ? '<span class="rk-arg-label">' + e(b.label) + '</span>' : '') +
          (b.source ? '<span class="rk-arg-src">' + md(b.source) + '</span>' : '') + '</div>' : '') +
        (b.text ? '<div class="rk-arg-note">' + md(b.text) + '</div>' : '') +
        steps + '</div>';
    }
    if (b.type === 'ul') {
      return '<ul class="rk-plainlist">' + b.items.map(function (it) { return '<li>' + md(it) + '</li>'; }).join('') + '</ul>';
    }
    if (b.label) {
      var cls = /objection/i.test(b.label) ? ' rk-note-obj' : /reply|stance|payoff/i.test(b.label) ? ' rk-note-reply' : '';
      return '<div class="rk-note' + cls + '"><span class="rk-note-label">' + e(b.label) + '</span>' +
        (b.source ? '<span class="rk-arg-src">' + md(b.source) + '</span>' : '') +
        '<div class="rk-note-text">' + md(b.text) + '</div></div>';
    }
    return '<p class="rk-p">' + md(b.text) + '</p>';
  }

  function problemDetail(slug) {
    var entry = data().entries[slug];
    if (!entry) return missingDetail('problem');
    var s = subfield(entry.subfield);
    var siblings = s.entries;
    var idx = siblings.indexOf(slug);

    var positions = entry.positions.map(function (p, i) {
      return '<article class="rk-position">' +
        '<h3 class="rk-position-name"><span class="rk-position-n" style="--h:' + s.hue + '" aria-hidden="true">' + (i + 1) + '</span>' + e(p.name) + '</h3>' +
        p.blocks.map(renderBlock).join('') + '</article>';
    }).join('');

    var thought = entry.thought.map(function (t) {
      return '<div class="rk-thought"><div class="rk-thought-icon" aria-hidden="true">◆</div>' +
        '<div>' + (t.name ? '<div class="rk-thought-name">' + e(t.name) + '</div>' : '') +
        '<div class="rk-thought-text">' + md(t.text) + '</div></div></div>';
    }).join('');

    var ladderLevels = ['Start', 'Survey', 'Primary', 'Full treatment', 'Anthology', 'Reference'];
    var ladder = entry.ladder.map(function (r, i) {
      var lvl = r.label ? ladderLevels.indexOf(r.label) : -1;
      if (lvl < 0) lvl = i;
      return '<li class="rk-rung" style="--depth:' + i + '"><span class="rk-rung-label" style="--h:' + s.hue + '">' + e(r.label || 'Step ' + (i + 1)) + '</span>' +
        '<div class="rk-rung-text">' + md(r.text) + '</div></li>';
    }).join('');

    var connections = entry.connections.map(function (c) {
      var head = c.slug ? problemChip(c.slug, c.title || data().entries[c.slug].title)
        : '<span class="rk-chip rk-chip-dead">' + e(c.title || 'Further reading') + '</span>';
      return '<div class="rk-connection">' + head + '<div class="rk-connection-text">' + md(c.text) + '</div></div>';
    }).join('');

    var otherLectures = (entry.lectures || []).filter(function (id) { return entry.frontdoor.indexOf(id) === -1; });
    var sourcesHtml = entry.sources.length
      ? '<ul class="rk-plainlist rk-sources">' + entry.sources.map(function (x) { return '<li>' + md(x) + '</li>'; }).join('') + '</ul>'
      : '';

    return '<article class="rk-panel" id="rk-problem">' + crumbs([subLink(s), 'Problem']) +
      '<header class="rk-detail-head">' +
      '<div class="rk-kicker" style="--h:' + s.hue + '">' + seal(s, 'rk-seal-sm') + ' ' + e(entry.sub_display || s.name) + '</div>' +
      '<h2>' + e(entry.title) + '</h2>' +
      (entry.note ? '<p class="rk-lede">' + e(entry.note) + '</p>' : '') +
      (entry.aka ? '<p class="rk-aka">Also known as: ' + e(entry.aka) + '</p>' : '') +
      (entry.pilot ? '<div class="rk-badges"><span class="rk-badge rk-badge-pilot" title="One of the three pilot entries — built first, built deepest">★ pilot entry</span></div>' : '') +
      '<div class="rk-meta">' + entry.positions.length + ' positions · ' + argCount(entry) + ' reconstructed arguments · ' +
      entry.frontdoor.length + ' front-door lectures' + (otherLectures.length ? ' · ' + otherLectures.length + ' further lectures' : '') + '</div>' +
      '</header>' +
      anchorNav(entry) +
      '<section class="rk-question" id="rk-q"><h3 class="rk-h3">The question</h3><div class="rk-question-text">' + md(entry.question) + '</div></section>' +
      '<section class="rk-ninety" id="rk-ninety"><h3 class="rk-h3">The 90-second version</h3>' +
      '<div class="rk-ninety-text">' + md(entry.ninety) + '</div>' +
      (entry.frontdoor.length ? '<div class="rk-yt-row">' + entry.frontdoor.map(function (id) {
        var lec = data().lectures[id];
        return ytChip(id, lec ? lec.title : id);
      }).join('') + '</div>' : '') +
      '</section>' +
      '<section id="rk-positions"><h3 class="rk-h3">Positions</h3>' + positions + '</section>' +
      (thought ? '<section id="rk-thought"><h3 class="rk-h3">Thought experiments</h3><div class="rk-thoughts">' + thought + '</div></section>' : '') +
      (ladder ? '<section id="rk-ladder"><h3 class="rk-h3">Source ladder</h3><p class="rk-lede-sm">Where to enter the reading, in ascending order of commitment.</p><ol class="rk-ladder">' + ladder + '</ol></section>' : '') +
      '<section class="rk-verdict" id="rk-verdict"><h3 class="rk-h3">Where the debate stands</h3>' +
      '<div class="rk-verdict-text">' + md(entry.verdict) + '</div>' +
      '<div class="rk-stamp" aria-hidden="true">unsettled · stays unsettled</div></section>' +
      '<section id="rk-connections"><h3 class="rk-h3">Connections</h3>' + connections +
      (entry.books && entry.books.length ? '<h3 class="rk-h3">Books behind this entry</h3><div class="rk-chips">' +
        entry.books.map(bookChip).join('') + '</div>' : '') +
      '</section>' +
      (sourcesHtml ? '<section id="rk-sources"><h3 class="rk-h3">Sources read for this entry</h3>' + sourcesHtml + '</section>' : '') +
      (entry.extra || []).map(function (x) {
        return '<section><h3 class="rk-h3">' + e(x.heading) + '</h3>' + md(x.md) + '</section>';
      }).join('') +
      siblingsNav(siblings, idx, problemHref) +
      '</article>';
  }

  function subLink(s) {
    return '<a href="' + href('problems') + '" data-rk-sublink="' + escAttr(s.id) + '">' + e(s.name) + '</a>';
  }

  function siblingsNav(ids, idx, makeHref) {
    if (ids.length < 2) return '';
    var prev = idx > 0 ? ids[idx - 1] : ids[ids.length - 1];
    var next = idx < ids.length - 1 ? ids[idx + 1] : ids[0];
    function name(id) {
      var o = data().entries[id] || data().books[id];
      return o ? (o.title) : id;
    }
    return '<nav class="rk-siblings" aria-label="More in this series">' +
      '<a class="rk-sib" href="' + makeHref(prev) + '"><span>← ' + e(name(prev)) + '</span></a>' +
      '<a class="rk-sib" href="' + makeHref(next) + '"><span>' + e(name(next)) + ' →</span></a></nav>';
  }

  /* ----------------------------------------------------------- book pages */

  function bookDetail(id) {
    var book = data().books[id];
    if (!book) return missingDetail('book');
    var ids = Object.keys(data().books).map(function (b) { return data().books[b]; })
      .sort(function (a, b) { return a.num === b.num ? a.title.localeCompare(b.title) : (a.num < b.num ? -1 : 1); })
      .map(function (b) { return b.id; });
    var idx = ids.indexOf(id);
    var companions = Object.keys(data().books).filter(function (x) {
      return x !== id && data().books[x].num === book.num;
    });

    var groups = book.groups.map(function (g) {
      var prose = g.prose.map(function (p) { return '<div class="rk-prose">' + md(p) + '</div>'; }).join('');
      var chapters = g.chapters.map(function (c) {
        return '<div class="rk-chapter">' +
          '<div class="rk-chapter-line">' +
          (c.star ? '<span class="rk-list-star" title="Feeds a problem entry directly">★</span> ' : '') +
          (c.title ? '<strong>' + e(c.title) + '</strong>' : '') + '</div>' +
          (c.note ? '<div class="rk-chapter-note">' + md(c.note) + '</div>' : '') +
          (c.entries.length ? '<div class="rk-entry-tags">' + c.entries.map(function (slug) {
            return chip(problemHref(slug), '→ ' + e(data().entries[slug].title));
          }).join('') + '</div>' : '') +
          '</div>';
      }).join('');
      return '<section class="rk-group">' +
        (g.heading ? '<div class="rk-group-head">' + e(g.heading) + '</div>' : '') +
        prose + chapters + '</section>';
    }).join('');

    return '<article class="rk-panel">' + crumbs(['Book']) +
      '<header class="rk-detail-head">' +
      '<div class="rk-book-head"><span class="rk-book-num" aria-hidden="true">' + e(book.num) + '</span>' +
      '<div><div class="rk-kicker">Book map · book layer</div><h2>' + e(book.title) + '</h2>' +
      (book.layer ? '<p class="rk-aka">' + e(book.layer) + '</p>' : '') +
      '<div class="rk-badges">' + flagBadges(book) +
      (companions.length ? companions.map(function (cid) {
        return '<span class="rk-flag"><a href="' + bookHref(cid) + '">companion map: ' + e(data().books[cid].num) + '</a></span>';
      }).join('') : '') +
      '</div>' +
      '<div class="rk-meta">' + book.fed.length + ' of 53 problems draw on this book</div>' +
      '</div></div></header>' +
      (book.fed.length ? '<div class="rk-chips rk-feeds">' + book.fed.map(problemChip).join('') + '</div>' : '') +
      (book.extraction ? '<details class="rk-extraction"><summary>Extraction note — what the corpus actually holds</summary><div>' + md(book.extraction) + '</div></details>' : '') +
      groups +
      (book.coverage ? '<section class="rk-verdict"><h3 class="rk-h3">Coverage</h3><div class="rk-verdict-text">' + md(book.coverage) + '</div></section>' : '') +
      '<div class="rk-start">The full map, with the builder’s notes, is also readable as plain markdown via <a href="' +
      state.ctx.appUrl('md/' + encodeURIComponent(BASE_DIR + 'book-maps/' + id + '.md')) + '" target="_blank" rel="noopener noreferrer">the source file</a>.</div>' +
      siblingsNav(ids, idx, bookHref) +
      '</article>';
  }

  /* -------------------------------------------------------- lecture pages */

  function lectureDetail(id) {
    var lec = data().lectures[id];
    if (!lec) return missingDetail('lecture');
    var assigned = lec.refs.length > 0;
    return '<article class="rk-panel">' + crumbs(['Lecture']) +
      '<header class="rk-detail-head"><div class="rk-kicker">Carneades lecture transcript</div><h2>' + e(lec.title) + '</h2>' +
      '<div class="rk-badges"><span class="rk-flag rk-status-' + lec.status + '">' + e(STATUS_LABELS[lec.status] || lec.status) + '</span>' +
      (lec.refs.some(function (r) { return r.star; }) ? '<span class="rk-flag rk-flag-star">★ front door</span>' : '') + '</div>' +
      (lec.note ? '<p class="rk-aka">' + e(lec.note) + '</p>' : '') +
      '</header>' +
      '<div class="rk-yt-row">' + ytChip(id) + '</div>' +
      (assigned
        ? '<h3 class="rk-h3">Serves these problem entries</h3><div class="rk-connections">' + lec.refs.map(function (r) {
            return '<div class="rk-connection">' + problemChip(r.slug) +
              (r.star ? '<span class="rk-flag rk-flag-star">★ front door — the entry’s 90-second source</span>' : '<span class="rk-flag">supporting lecture</span>') + '</div>';
          }).join('') + '</div>'
        : '<div class="rk-start">This transcript is not yet assigned to a problem entry — usually because no extracted book yet supports the problem it belongs to. It is a candidate for future entries, not a discard. See <a href="' + href('guide') + '">the build guide</a>.</div>') +
      '</article>';
  }

  /* ------------------------------------------------------------ guide tab */

  function guideDetail() {
    var stats = data().stats;
    var rows = data().subfields.map(function (s) {
      return '<div class="rk-guide-row' + (s.unbuilt ? ' rk-guide-ghost' : '') + '" style="--h:' + s.hue + '">' +
        seal(s, 'rk-seal-sm') + '<strong>' + e(s.name) + '</strong>' +
        '<span class="rk-guide-count">' + (s.unbuilt ? 'not built' : s.entries.length + ' problems') + '</span>' +
        '<span class="rk-guide-blurb">' + e(s.blurb) + '</span></div>';
    }).join('');

    return '<article class="rk-panel">' + crumbs(['Guide']) +
      '<header class="rk-detail-head"><div class="rk-kicker">How this knowledge base was built</div>' +
      '<h2>One spine, three layers, no padding</h2>' +
      '<p class="rk-intro">Everything here is organized around a single spine — <strong>subfield → problem → positions → arguments</strong> — and built in layers: the problem entries are the front; book maps and the lecture index are the load-bearing structure behind them, each claim traceable to what its source actually says.</p></header>' +
      '<div class="rk-spine" aria-hidden="true">' +
      '<div class="rk-spine-step"><strong>Subfield</strong><span>9 built, 1 deferred</span></div>' +
      '<div class="rk-spine-arrow">→</div>' +
      '<div class="rk-spine-step"><strong>Problem</strong><span>' + stats.entries + ' standing debates</span></div>' +
      '<div class="rk-spine-arrow">→</div>' +
      '<div class="rk-spine-step"><strong>Positions</strong><span>named, sourced</span></div>' +
      '<div class="rk-spine-arrow">→</div>' +
      '<div class="rk-spine-step"><strong>Arguments</strong><span>P1 · P2 · ∴C, faithful</span></div>' +
      '</div>' +
      '<h3 class="rk-h3">What every entry contains</h3>' +
      '<div class="rk-template">' +
      '<div class="rk-tstep"><span>The question</span>in plain terms</div>' +
      '<div class="rk-tstep"><span>The 90-second version</span>a lecture, distilled — the front door</div>' +
      '<div class="rk-tstep"><span>Positions</span>each with its canonical argument reconstructed premise by premise</div>' +
      '<div class="rk-tstep"><span>Objections &amp; replies</span>at the strength the source states them</div>' +
      '<div class="rk-tstep"><span>Thought experiments</span>the machinery of the debate</div>' +
      '<div class="rk-tstep"><span>Source ladder</span>from first lecture to primary text</div>' +
      '<div class="rk-tstep"><span>Where the debate stands</span>unsettled stays unsettled</div>' +
      '</div>' +
      '<h3 class="rk-h3">Subfields</h3>' +
      '<div class="rk-guide-table">' + rows + '</div>' +
      '<h3 class="rk-h3">Known shortfalls — recorded, not padded</h3>' +
      '<div class="rk-prose">' + md(data().shortfalls) + '</div>' +
      '<h3 class="rk-h3">Data quality</h3>' +
      '<p class="rk-lede-sm">8 of the 26 catalogue folders hold a different book than their name claims. The audit lives in DATA_QUALITY.md; its findings are reproduced here so no reader trusts the catalogue blindly.</p>' +
      '<div class="rk-prose">' + md(data().quality.intro) + '</div>' +
      data().quality.sections.map(function (sec) {
        return '<details class="rk-extraction"><summary>' + e(sec.heading) + '</summary><div class="rk-prose">' + md(sec.md) + '</div></details>';
      }).join('') +
      '<div class="rk-start">The markdown sources under <code>knowledge-base/readings-kb/</code> remain the source of truth; this explorer is a rendering of them, rebuilt by <code>scratchpad/readings_kb/build_data.py</code>.</div>' +
      '</article>';
  }

  function missingDetail(kind) {
    return '<section class="rk-panel">' + crumbs([]) +
      '<header class="rk-detail-head"><div class="rk-kicker">Not found</div><h2>Unknown ' + e(kind) + '</h2>' +
      '<p class="rk-intro">This link does not match the knowledge base. Choose another item from the list.</p></header></section>';
  }

  /* -------------------------------------------------------------- routing */

  function detailForParts() {
    var kind = state.parts[1] || '';
    var id = state.parts[2] || '';
    if (kind === 'problem' && id) return problemDetail(id);
    if (kind === 'book' && id) return bookDetail(id);
    if (kind === 'lecture' && id) return lectureDetail(id);
    if (kind === 'guide') return guideDetail();
    return homeDetail();  // root and tab views share the landing detail
  }

  function titleForParts() {
    var kind = state.parts[1] || '';
    var id = state.parts[2] || '';
    if (kind === 'problem' && data().entries[id]) return data().entries[id].title;
    if (kind === 'book' && data().books[id]) return 'Book ' + data().books[id].num + ' — ' + shortBookTitle(data().books[id]);
    if (kind === 'lecture' && data().lectures[id]) return data().lectures[id].title;
    if (kind === 'guide') return 'How this knowledge base was built';
    return 'The Philosophy Readings — a problem-based knowledge base';
  }

  function syncTab() {
    var kind = state.parts[1] || '';
    if (kind === 'problem' || kind === 'problems') state.tab = 'problems';
    else if (kind === 'book' || kind === 'books') state.tab = 'books';
    else if (kind === 'lecture' || kind === 'lectures') state.tab = 'lectures';
    else if (kind === 'guide') state.tab = 'guide';
    else state.tab = 'problems';
  }

  function renderCurrent() {
    syncTab();
    state.ctx.app.innerHTML = shell(detailForParts());
    renderList();
  }

  function route(parts, ctx) {
    state.ctx = ctx;
    state.parts = parts;
    state.listOpen = false;
    ctx.setNav('knowledge-base');
    ctx.showStatus('Opening the knowledge base…');
    return load(ctx).then(function (d) {
      state.data = d;
      ctx.setTitle(titleForParts());
      renderCurrent();
      bindEvents();
      window.scrollTo(0, 0);
    }).catch(function (error) {
      ctx.showError('Could not load the readings knowledge base — ' + error.message);
    });
  }

  function load(ctx) {
    if (!dataPromise) {
      dataPromise = fetch(ctx.appUrl(DATA_PATH)).then(function (response) {
        if (!response.ok) throw new Error('data HTTP ' + response.status);
        if (/text\/html/i.test(response.headers.get('content-type') || '')) {
          throw new Error('data.json is missing');
        }
        return response.json();
      });
    }
    return dataPromise;
  }

  /* --------------------------------------------------------------- events */

  function bindEvents() {
    if (document.documentElement.dataset.rkBound === '1') return;
    document.documentElement.dataset.rkBound = '1';

    document.addEventListener('input', function (event) {
      if (event.target.id !== 'rk-search') return;
      state.query = event.target.value;
      renderList();
    });

    document.addEventListener('change', function (event) {
      if (event.target.id === 'rk-sub') {
        state.sub = event.target.value;
        renderList();
      } else if (event.target.id === 'rk-status') {
        state.lectureStatus = event.target.value;
        renderList();
      }
    });

    document.addEventListener('click', function (event) {
      var t = event.target;
      var browse = t.closest ? t.closest('[data-rk-browse]') : null;
      if (browse) {
        state.listOpen = !state.listOpen;
        var shellEl = document.querySelector('.rk-shell');
        if (shellEl) shellEl.classList.toggle('rk-list-open', state.listOpen);
        browse.setAttribute('aria-expanded', state.listOpen ? 'true' : 'false');
        return;
      }
      var tabBtn = t.closest ? t.closest('[data-rk-tab]') : null;
      if (tabBtn) {
        if (state.tab === tabBtn.getAttribute('data-rk-tab') && state.parts.length === 1) return;
        state.tab = tabBtn.getAttribute('data-rk-tab');
        state.query = '';
        state.parts = ['readings', state.tab];
        state.listOpen = false;
        history.pushState(null, '', href(state.tab === 'guide' ? 'guide' : state.tab));
        state.ctx.setTitle(titleForParts());
        renderCurrent();
        window.scrollTo(0, 0);
        return;
      }
      var subLink2 = t.closest ? t.closest('[data-rk-sublink]') : null;
      if (subLink2) {
        // the SPA interceptor navigates to /readings/problems; set the
        // subfield filter here, synchronously, so the incoming render shows it
        state.tab = 'problems';
        state.sub = subLink2.getAttribute('data-rk-sublink');
        state.query = '';
      }
    });

    // smooth-scroll for the in-entry anchor nav; capture phase + stopPropagation
    // so the host SPA's link interceptor (bubble phase) never routes '#rk-…'
    document.addEventListener('click', function (event) {
      var a = event.target.closest ? event.target.closest('[data-rk-anchor]') : null;
      if (!a) return;
      var target = document.getElementById(a.getAttribute('data-rk-anchor'));
      if (!target) return;
      event.preventDefault();
      event.stopPropagation();
      target.scrollIntoView({ behavior: 'instant', block: 'start' });
      history.replaceState(null, '', a.getAttribute('href'));
    }, true);
  }

  window.ReadingsExplorer = { route: route };
})();
