(function () {
  'use strict';

  var DATA_PATH = 'knowledge-base/popcult-index/data.json';
  var dataPromise = null;
  var state = { ctx: null, data: null, parts: null, listType: 'concepts', query: '', domain: '', listOpen: false };

  function e(value) {
    return String(value == null ? '' : value)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;')
      .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function load(ctx) {
    if (!dataPromise) {
      dataPromise = fetch(ctx.appUrl(DATA_PATH)).then(function (response) {
        if (!response.ok) throw new Error('Explorer data HTTP ' + response.status);
        if (/text\/html/i.test(response.headers.get('content-type') || '')) {
          throw new Error('Explorer data is missing');
        }
        return response.json();
      }).then(function (data) {
        Object.keys(data.books).forEach(function (bid) {
          var byNumber = {};
          data.books[bid].chapters.forEach(function (chapter) { byNumber[chapter.n] = chapter; });
          Object.defineProperty(data.books[bid], '_chapterByNumber', { value: byNumber });
        });
        return data;
      });
    }
    return dataPromise;
  }

  function href(type, id, chapter) {
    var singular = type === 'books' ? 'book' : type === 'concepts' ? 'concept' : 'philosopher';
    var value = state.ctx.appUrl('popcult/' + singular + '/' + encodeURIComponent(id));
    return value + (chapter ? '#chapter-' + chapter : '');
  }

  function chapterCount(book) {
    return book.chapters.filter(function (chapter) {
      return chapter.concepts.length || chapter.philosophers.length;
    }).length;
  }

  function entityCount(type, entity) {
    if (type === 'books') return chapterCount(entity);
    return entity.chapters.length;
  }

  function entityDomain(type, entity) {
    if (type === 'books') return entity.domains || [];
    return entity.domain ? [entity.domain] : [];
  }

  function typeLabel(type) {
    return type === 'books' ? 'Books' : type === 'concepts' ? 'Concepts' : 'Philosophers';
  }

  function selectedEntity() {
    var kind = state.parts[1] || '';
    var id = state.parts[2] || '';
    if (kind === 'book') return { type: 'books', id: id };
    if (kind === 'concept') return { type: 'concepts', id: id };
    if (kind === 'philosopher') return { type: 'philosophers', id: id };
    return null;
  }

  function listRows() {
    var rows = Object.keys(state.data[state.listType]).map(function (id) {
      return { id: id, entity: state.data[state.listType][id] };
    });
    var query = state.query.trim().toLowerCase();
    if (query) {
      rows = rows.filter(function (row) {
        var haystack = (row.entity.name || row.entity.title || '') + ' ' +
          (row.entity.intro || '') + ' ' + (row.entity.dates || '');
        return haystack.toLowerCase().indexOf(query) !== -1;
      });
    }
    if (state.domain) {
      rows = rows.filter(function (row) {
        return entityDomain(state.listType, row.entity).indexOf(state.domain) !== -1;
      });
    }
    rows.sort(function (a, b) {
      var countDelta = entityCount(state.listType, b.entity) - entityCount(state.listType, a.entity);
      if (countDelta) return countDelta;
      return (a.entity.name || a.entity.title).localeCompare(b.entity.name || b.entity.title);
    });
    return rows;
  }

  function renderList() {
    var target = document.getElementById('pc-list');
    var count = document.getElementById('pc-result-count');
    if (!target || !count) return;
    var rows = listRows();
    var selected = selectedEntity();
    count.textContent = rows.length + ' shown';
    if (!rows.length) {
      target.innerHTML = '<div class="pc-empty-list">No matches. Try another search or tradition.</div>';
      return;
    }
    target.innerHTML = rows.map(function (row) {
      var label = row.entity.name || row.entity.title;
      var active = selected && selected.type === state.listType && selected.id === row.id;
      return '<a class="pc-list-link' + (active ? ' active' : '') + '" href="' + href(state.listType, row.id) + '" title="' + e(label) + ' — ' + entityCount(state.listType, row.entity) + ' indexed chapters" aria-label="' + e(label) + ' — ' + entityCount(state.listType, row.entity) + ' indexed chapters">' +
        '<span class="pc-list-label">' + e(label) + '</span>' +
        '<span class="pc-list-count" aria-hidden="true">' + entityCount(state.listType, row.entity) + '</span></a>';
    }).join('');
  }

  function domainOptions() {
    var options = ['<option value="">All traditions</option>'];
    Object.keys(state.data.domains).forEach(function (slug) {
      options.push('<option value="' + e(slug) + '"' + (state.domain === slug ? ' selected' : '') + '>' +
        e(state.data.domains[slug].name) + '</option>');
    });
    return options.join('');
  }

  function shell(detail) {
    var stats = state.data.stats;
    return '<div class="pc-shell' + (selectedEntity() ? ' pc-has-detail' : '') + (state.listOpen ? ' pc-list-open' : '') + '">' +
      '<header class="pc-hero"><div class="pc-eyebrow">A reverse index</div>' +
      '<h1>Philosophy × Pop Culture</h1>' +
      '<p>Start with an idea, philosopher, or book. Every chapter links to the philosophy it uses, and every philosophical idea links back to the books that put it to work.</p>' +
      '<div class="pc-stats"><span class="pc-stat"><strong>' + Object.keys(state.data.books).length + '</strong> books</span>' +
      '<span class="pc-stat"><strong>' + stats.chapters_read.toLocaleString() + '</strong> chapters analyzed</span>' +
      '<span class="pc-stat"><strong>' + Object.keys(state.data.concepts).length + '</strong> concepts</span>' +
      '<span class="pc-stat"><strong>' + Object.keys(state.data.philosophers).length + '</strong> philosophers</span></div></header>' +
      '<div class="pc-toolbar" aria-label="Explorer controls">' +
      '<label class="pc-search-wrap"><span class="pc-search-icon" aria-hidden="true">⌕</span>' +
      '<span class="sr-only">Search the current list</span><input class="pc-search" id="pc-search" type="search" value="' + e(state.query) + '" placeholder="Search this list…" autocomplete="off"></label>' +
      '<div class="pc-tabs" role="group" aria-label="Browse by">' +
      ['concepts', 'books', 'philosophers'].map(function (type) {
        return '<button class="pc-tab' + (state.listType === type ? ' active' : '') + '" type="button" data-pc-type="' + type + '">' + typeLabel(type) + '</button>';
      }).join('') + '</div>' +
      '<label><span class="sr-only">Philosophical tradition</span><select class="pc-select" id="pc-domain">' + domainOptions() + '</select></label></div>' +
      '<div class="pc-grid">' + (selectedEntity() ? '<button class="pc-mobile-browse" type="button" data-pc-browse aria-expanded="' + (state.listOpen ? 'true' : 'false') + '">Browse another ' + e(typeLabel(state.listType).toLowerCase().replace(/s$/, '')) + '<span aria-hidden="true">▾</span></button>' : '') + '<aside class="pc-sidebar" aria-label="Browse results">' +
      '<div class="pc-sidebar-head"><strong id="pc-list-title">' + typeLabel(state.listType) + '</strong><span class="pc-result-count" id="pc-result-count"></span></div>' +
      '<nav class="pc-list" id="pc-list"></nav></aside><main class="pc-main">' + detail + '</main></div></div>';
  }

  function crumbs(items) {
    var values = ['<a href="' + state.ctx.appUrl('popcult') + '">Explorer</a>'];
    items.forEach(function (item) { values.push(e(item)); });
    return '<div class="pc-breadcrumbs">' + values.join(' <span aria-hidden="true">›</span> ') + '</div>';
  }

  function chip(type, id, label, extraClass) {
    return '<a class="pc-chip' + (extraClass ? ' ' + extraClass : '') + '" href="' + href(type, id) + '">' + e(label) + '</a>';
  }

  function cover(book, mini) {
    if (book.cover) {
      return '<img class="' + (mini ? 'pc-mini-cover' : 'pc-cover') + '" src="' + e(state.ctx.appUrl(book.cover)) + '" alt="Cover of ' + e(book.title) + '" loading="lazy">';
    }
    if (mini) return '<span class="pc-mini-cover" aria-hidden="true"></span>';
    return '<div class="pc-cover-fallback" aria-hidden="true">' + e(book.title.slice(0, 1)) + '</div>';
  }

  function homeDetail() {
    var concepts = Object.keys(state.data.concepts).sort(function (a, b) {
      return state.data.concepts[b].chapters.length - state.data.concepts[a].chapters.length;
    }).slice(0, 8);
    var books = Object.keys(state.data.books).sort(function (a, b) {
      return chapterCount(state.data.books[b]) - chapterCount(state.data.books[a]);
    }).slice(0, 5);
    return '<section class="pc-panel">' + crumbs([]) +
      '<header class="pc-detail-head"><div class="pc-kicker">How to explore</div><h2>Follow ideas through stories</h2>' +
      '<p class="pc-intro">Choose a concept to learn what it means and see where writers apply it. Choose a book to move chapter by chapter, then follow any concept or philosopher back across the whole collection.</p></header>' +
      '<div class="pc-overview"><div class="pc-overview-card"><strong>1</strong><span>Choose Concepts, Books, or Philosophers</span></div>' +
      '<div class="pc-overview-card"><strong>2</strong><span>Open an item from the left pane</span></div>' +
      '<div class="pc-overview-card"><strong>3</strong><span>Follow links in either direction</span></div></div>' +
      '<div class="pc-start">The number beside each item is its indexed chapter count. Use the tradition filter to narrow the map, or type in the search box.</div>' +
      '<h3 class="pc-section-title">Good places to begin</h3><div class="pc-actions">' +
      concepts.map(function (slug) { return chip('concepts', slug, state.data.concepts[slug].name); }).join('') + '</div>' +
      '<h3 class="pc-section-title">Books with the richest index</h3>' +
      books.map(function (bid) {
        var book = state.data.books[bid];
        return '<div class="pc-group-head">' + cover(book, true) + '<a href="' + href('books', bid) + '">' + e(book.title) + '</a>' +
          '<span class="pc-group-count">' + chapterCount(book) + ' indexed chapters</span></div>';
      }).join('') + '</section>';
  }

  function groupReferences(refs, entityType, entityId) {
    var grouped = {};
    refs.forEach(function (ref) {
      (grouped[ref[0]] || (grouped[ref[0]] = [])).push(ref[1]);
    });
    return Object.keys(grouped).sort(function (a, b) {
      return state.data.books[a].title.localeCompare(state.data.books[b].title);
    }).map(function (bid) {
      var book = state.data.books[bid];
      var entries = grouped[bid].map(function (number) {
        var chapter = book._chapterByNumber[number];
        var otherChips = '';
        if (entityType !== 'concepts') {
          otherChips += chapter.concepts.slice(0, 6).map(function (slug) {
            return chip('concepts', slug, state.data.concepts[slug].name);
          }).join('');
        }
        if (entityType !== 'philosophers') {
          otherChips += chapter.philosophers.slice(0, 4).map(function (slug) {
            return chip('philosophers', slug, state.data.philosophers[slug].name, 'philosopher');
          }).join('');
        }
        return '<article class="pc-entry"><a class="pc-entry-title" href="' + href('books', bid, number) + '">Chapter ' + number + ': ' + e(chapter.title) + '</a>' +
          (chapter.relation ? '<p>' + e(chapter.relation) + '</p>' : '') +
          (otherChips ? '<div class="pc-entry-tags">' + otherChips + '</div>' : '') + '</article>';
      }).join('');
      return '<section class="pc-entry-group"><div class="pc-group-head">' + cover(book, true) +
        '<a href="' + href('books', bid) + '">' + e(book.title) + '</a><span class="pc-group-count">' + grouped[bid].length + ' chapter' + (grouped[bid].length === 1 ? '' : 's') + '</span></div>' + entries + '</section>';
    }).join('');
  }

  function conceptDetail(slug) {
    var concept = state.data.concepts[slug];
    if (!concept) return missingDetail('concept');
    var domain = state.data.domains[concept.domain];
    var philosopher = concept.philosopher && state.data.philosophers[concept.philosopher];
    var related = concept.related.filter(function (row) { return state.data.concepts[row[0]]; });
    return '<article class="pc-panel">' + crumbs(['Concept']) + '<header class="pc-detail-head"><div class="pc-kicker">' + e(domain ? domain.name : 'Philosophy concept') + '</div>' +
      '<h2>' + e(concept.name) + '</h2><p class="pc-intro">' + e(concept.intro || 'This concept is indexed wherever the books use it as part of a substantive philosophical argument.') + '</p>' +
      '<div class="pc-meta">Appears in ' + concept.chapters.length + ' indexed chapters' + (philosopher ? ' · Associated with ' + e(philosopher.name) : '') + '</div>' +
      (philosopher ? '<div class="pc-actions">' + chip('philosophers', concept.philosopher, philosopher.name, 'philosopher') + '</div>' : '') + '</header>' +
      (related.length ? '<h3 class="pc-section-title">Related ideas</h3><div class="pc-actions">' + related.map(function (row) {
        return chip('concepts', row[0], state.data.concepts[row[0]].name);
      }).join('') + '</div>' : '') +
      '<h3 class="pc-section-title">Where this idea appears</h3>' +
      (concept.chapters.length ? groupReferences(concept.chapters, 'concepts', slug) : '<div class="pc-start">No indexed chapter uses this concept yet.</div>') + '</article>';
  }

  function philosopherDetail(slug) {
    var philosopher = state.data.philosophers[slug];
    if (!philosopher) return missingDetail('philosopher');
    var domain = state.data.domains[philosopher.domain];
    return '<article class="pc-panel">' + crumbs(['Philosopher']) + '<header class="pc-detail-head"><div class="pc-kicker">' + e(domain ? domain.name : 'Philosopher') + '</div>' +
      '<h2>' + e(philosopher.name) + '</h2>' + (philosopher.dates ? '<div class="pc-meta">' + e(philosopher.dates) + '</div>' : '') +
      '<p class="pc-intro">' + e(philosopher.intro || 'This philosopher appears wherever the books make substantive use of their work.') + '</p>' +
      '<div class="pc-meta">Appears in ' + philosopher.chapters.length + ' indexed chapters</div></header>' +
      (philosopher.concepts.length ? '<h3 class="pc-section-title">Key ideas in this index</h3><div class="pc-actions">' + philosopher.concepts.map(function (row) {
        return chip('concepts', row[0], state.data.concepts[row[0]].name + ' · ' + row[1]);
      }).join('') + '</div>' : '') +
      '<h3 class="pc-section-title">Where this philosopher appears</h3>' +
      (philosopher.chapters.length ? groupReferences(philosopher.chapters, 'philosophers', slug) : '<div class="pc-start">No indexed chapter cites this philosopher yet.</div>') + '</article>';
  }

  function bookDetail(bid) {
    var book = state.data.books[bid];
    if (!book) return missingDetail('book');
    var mapped = chapterCount(book);
    var domains = book.domains.map(function (slug) { return state.data.domains[slug] && state.data.domains[slug].name; }).filter(Boolean);
    var chapters = book.chapters.map(function (chapter) {
      var tags = chapter.concepts.map(function (slug) {
        return state.data.concepts[slug] ? chip('concepts', slug, state.data.concepts[slug].name) : '';
      }).join('') + chapter.philosophers.map(function (slug) {
        return state.data.philosophers[slug] ? chip('philosophers', slug, state.data.philosophers[slug].name, 'philosopher') : '';
      }).join('');
      var isMatter = ['front', 'notes', 'interlude'].indexOf(chapter.kind) !== -1;
      return '<article class="pc-chapter' + (isMatter ? ' pc-front-matter' : '') + '" id="chapter-' + chapter.n + '">' +
        '<div class="pc-chapter-number">Chapter ' + chapter.n + (isMatter ? ' · ' + e(chapter.kind) : '') + '</div><h3>' + e(chapter.title) + '</h3>' +
        (chapter.relation ? '<p>' + e(chapter.relation) + '</p>' : '') +
        (tags ? '<div class="pc-entry-tags">' + tags + '</div>' : (!isMatter ? '<div class="pc-meta">No index connection recorded.</div>' : '')) + '</article>';
    }).join('');
    return '<article class="pc-panel">' + crumbs(['Book']) + '<div class="pc-book-head">' + cover(book, false) +
      '<header class="pc-detail-head"><div class="pc-kicker">Book</div><h2>' + e(book.title) + '</h2>' +
      '<p class="pc-intro">Read the book through its philosophical map. Each chapter links outward to every concept and philosopher it substantively uses.</p>' +
      '<div class="pc-meta">' + book.chapters.length + ' sections · ' + mapped + ' indexed chapters' + (domains.length ? ' · ' + e(domains.join(' · ')) : '') + '</div></header></div>' +
      '<h3 class="pc-section-title">Chapters</h3>' + chapters + '</article>';
  }

  function missingDetail(kind) {
    return '<section class="pc-panel">' + crumbs([]) + '<header class="pc-detail-head"><div class="pc-kicker">Not found</div><h2>Unknown ' + e(kind) + '</h2>' +
      '<p class="pc-intro">This link does not match the current index. Choose another item from the list.</p></header></section>';
  }

  function detailForParts() {
    var kind = state.parts[1] || '';
    var id = state.parts[2] || '';
    if (kind === 'book' && id) return bookDetail(id);
    if (kind === 'concept' && id) return conceptDetail(id);
    if (kind === 'philosopher' && id) return philosopherDetail(id);
    return homeDetail();
  }

  function titleForParts() {
    var kind = state.parts[1] || '';
    var id = state.parts[2] || '';
    if (kind === 'book' && state.data.books[id]) return state.data.books[id].title;
    if (kind === 'concept' && state.data.concepts[id]) return state.data.concepts[id].name;
    if (kind === 'philosopher' && state.data.philosophers[id]) return state.data.philosophers[id].name;
    return 'Philosophy × Pop Culture';
  }

  function renderCurrent() {
    state.ctx.app.innerHTML = shell(detailForParts());
    renderList();
    var target = location.hash && /^#chapter-\d+$/.test(location.hash) ? document.querySelector(location.hash) : null;
    if (target) setTimeout(function () { target.scrollIntoView({ behavior: 'smooth', block: 'start' }); }, 0);
  }

  function bindEvents() {
    if (document.documentElement.dataset.popcultBound === '1') return;
    document.documentElement.dataset.popcultBound = '1';
    document.addEventListener('input', function (event) {
      if (event.target.id !== 'pc-search') return;
      state.query = event.target.value;
      renderList();
    });
    document.addEventListener('change', function (event) {
      if (event.target.id !== 'pc-domain') return;
      state.domain = event.target.value;
      renderList();
    });
    document.addEventListener('click', function (event) {
      var browse = event.target.closest ? event.target.closest('[data-pc-browse]') : null;
      if (browse) {
        state.listOpen = !state.listOpen;
        var shell = document.querySelector('.pc-shell');
        if (shell) shell.classList.toggle('pc-list-open', state.listOpen);
        browse.setAttribute('aria-expanded', state.listOpen ? 'true' : 'false');
        return;
      }
      var button = event.target.closest ? event.target.closest('[data-pc-type]') : null;
      if (!button) return;
      state.listType = button.getAttribute('data-pc-type');
      document.querySelectorAll('.pc-tab').forEach(function (tab) {
        tab.classList.toggle('active', tab === button);
      });
      var title = document.getElementById('pc-list-title');
      if (title) title.textContent = typeLabel(state.listType);
      renderList();
    });
  }

  function route(parts, ctx) {
    state.ctx = ctx;
    state.parts = parts;
    state.listOpen = false;
    var selected = selectedEntity();
    if (selected) state.listType = selected.type;
    ctx.setNav('knowledge-base');
    ctx.showStatus('Loading the philosophy map…');
    return load(ctx).then(function (data) {
      state.data = data;
      ctx.setTitle(titleForParts());
      renderCurrent();
      bindEvents();
      window.scrollTo(0, 0);
    }).catch(function (error) {
      ctx.showError('Could not load the pop-culture index — ' + error.message);
    });
  }

  window.PopcultExplorer = { route: route };
})();
