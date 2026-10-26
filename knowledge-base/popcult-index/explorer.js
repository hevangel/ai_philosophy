(function () {
  'use strict';

  var DATA_PATH = 'knowledge-base/popcult-index/data.json';
  var dataPromise = null;
  var state = { ctx: null, data: null, parts: null, listType: 'concepts', query: '', domain: '', university: '', tier: '', listOpen: false };
  var TIER_LABELS = { A: 'Full free course videos', B: 'Partial video or lecture notes', C: 'Readings or reference only' };

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
        Object.keys(data.courses || {}).forEach(function (cid) {
          var byNumber = {};
          (data.courses[cid].lectures || []).forEach(function (lecture) { byNumber[lecture.n] = lecture; });
          Object.defineProperty(data.courses[cid], '_lectureByNumber', { value: byNumber });
        });
        return data;
      });
    }
    return dataPromise;
  }

  function href(type, id, chapter) {
    var singular = type === 'books' ? 'book' : type === 'concepts' ? 'concept' : type === 'courses' ? 'course' : 'philosopher';
    var value = state.ctx.appUrl('popcult/' + singular + '/' + encodeURIComponent(id));
    if (!chapter) return value;
    return value + (type === 'courses' ? '#lecture-' : '#chapter-') + chapter;
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
    return type === 'books' ? 'Books' : type === 'concepts' ? 'Concepts' : type === 'courses' ? 'Courses' : 'Philosophers';
  }

  function selectedEntity() {
    var kind = state.parts[1] || '';
    var id = state.parts[2] || '';
    if (kind === 'book') return { type: 'books', id: id };
    if (kind === 'concept') return { type: 'concepts', id: id };
    if (kind === 'philosopher') return { type: 'philosophers', id: id };
    if (kind === 'course') return { type: 'courses', id: id };
    return null;
  }

  function courseHaystack(course) {
    return [course.title, course.university, course.instructor, course.year, course.format,
      course.extent, course.description, (course.tags || []).join(' '), course.remarks].join(' ');
  }

  function courseTierCount(tier) {
    var total = 0;
    Object.keys(state.data.courses).forEach(function (id) {
      if (state.data.courses[id].tier === tier) total += 1;
    });
    return total;
  }

  function listRows() {
    var rows = Object.keys(state.data[state.listType]).map(function (id) {
      return { id: id, entity: state.data[state.listType][id] };
    });
    var query = state.query.trim().toLowerCase();
    if (state.listType === 'courses') {
      if (query) {
        rows = rows.filter(function (row) {
          return courseHaystack(row.entity).toLowerCase().indexOf(query) !== -1;
        });
      }
      if (state.university) {
        rows = rows.filter(function (row) { return row.entity.university === state.university; });
      }
      if (state.tier) {
        rows = rows.filter(function (row) { return row.entity.tier === state.tier; });
      }
      rows.sort(function (a, b) {
        var tierDelta = a.entity.tier.localeCompare(b.entity.tier);
        if (tierDelta) return tierDelta;
        var uniDelta = a.entity.university.localeCompare(b.entity.university);
        if (uniDelta) return uniDelta;
        return a.entity.title.localeCompare(b.entity.title);
      });
      return rows;
    }
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
      if (state.listType === 'courses') {
        var hint = row.entity.university + ' — ' + (TIER_LABELS[row.entity.tier] || row.entity.tier);
        return '<a class="pc-list-link' + (active ? ' active' : '') + '" href="' + href('courses', row.id) + '" title="' + e(hint) + '" aria-label="' + e(label + ' — ' + hint) + '">' +
          '<span class="pc-list-label">' + e(label) + '</span>' +
          '<span class="pc-list-count pc-list-tier-' + e(row.entity.tier.toLowerCase()) + '" aria-hidden="true">' + e(row.entity.tier) + '</span></a>';
      }
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

  function universityOptions() {
    var universities = {};
    Object.keys(state.data.courses).forEach(function (id) {
      universities[state.data.courses[id].university] = true;
    });
    var options = ['<option value="">All universities</option>'];
    Object.keys(universities).sort().forEach(function (name) {
      options.push('<option value="' + e(name) + '"' + (state.university === name ? ' selected' : '') + '>' + e(name) + '</option>');
    });
    return options.join('');
  }

  function tierOptions() {
    return ['<option value="">All material levels</option>'].concat(Object.keys(TIER_LABELS).map(function (tier) {
      return '<option value="' + tier + '"' + (state.tier === tier ? ' selected' : '') + '>' +
        e(tier + ' — ' + TIER_LABELS[tier]) + '</option>';
    })).join('');
  }

  function shell(detail) {
    var stats = state.data.stats;
    return '<div class="pc-shell' + (selectedEntity() ? ' pc-has-detail' : '') + (state.listOpen ? ' pc-list-open' : '') + '">' +
      '<header class="pc-hero"><div class="pc-eyebrow">A reverse index</div>' +
      '<h1>Philosophy × Pop Culture</h1>' +
      '<p>Start with an idea, philosopher, book, or open university course. Every chapter links to the philosophy it uses, and every philosophical idea links back to the books that put it to work.</p>' +
      '<div class="pc-stats"><span class="pc-stat"><strong>' + Object.keys(state.data.books).length + '</strong> books</span>' +
      '<span class="pc-stat"><strong>' + stats.chapters_read.toLocaleString() + '</strong> chapters analyzed</span>' +
      '<span class="pc-stat"><strong>' + Object.keys(state.data.concepts).length + '</strong> concepts</span>' +
      '<span class="pc-stat"><strong>' + Object.keys(state.data.philosophers).length + '</strong> philosophers</span>' +
      '<span class="pc-stat"><strong>' + Object.keys(state.data.courses || {}).length + '</strong> university courses</span></div></header>' +
      '<div class="pc-toolbar" aria-label="Explorer controls">' +
      '<label class="pc-search-wrap"><span class="pc-search-icon" aria-hidden="true">⌕</span>' +
      '<span class="sr-only">Search the current list</span><input class="pc-search" id="pc-search" type="search" value="' + e(state.query) + '" placeholder="Search this list…" autocomplete="off"></label>' +
      '<div class="pc-tabs" role="group" aria-label="Browse by">' +
      ['concepts', 'books', 'philosophers', 'courses'].map(function (type) {
        return '<button class="pc-tab' + (state.listType === type ? ' active' : '') + '" type="button" data-pc-type="' + type + '">' + typeLabel(type) + '</button>';
      }).join('') + '</div>' +
      (state.listType === 'courses'
        ? '<div class="pc-course-filters">' +
          '<label><span class="sr-only">University</span><select class="pc-select" id="pc-university">' + universityOptions() + '</select></label>' +
          '<label><span class="sr-only">Material level</span><select class="pc-select" id="pc-tier">' + tierOptions() + '</select></label></div>'
        : '<label><span class="sr-only">Philosophical tradition</span><select class="pc-select" id="pc-domain">' + domainOptions() + '</select></label>') + '</div>' +
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
      '<div class="pc-overview"><div class="pc-overview-card"><strong>1</strong><span>Choose Concepts, Books, Philosophers, or Courses</span></div>' +
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

  function coursesHomeDetail() {
    var courses = state.data.courses;
    var featured = Object.keys(courses).filter(function (id) { return courses[id].tier === 'A'; })
      .sort(function (a, b) { return courses[a].university.localeCompare(courses[b].university) || courses[a].title.localeCompare(courses[b].title); });
    var byUniversity = {};
    Object.keys(courses).forEach(function (id) {
      (byUniversity[courses[id].university] || (byUniversity[courses[id].university] = [])).push(id);
    });
    var groups = Object.keys(byUniversity).sort().map(function (university) {
      var entries = byUniversity[university].sort(function (a, b) {
        return courses[a].tier.localeCompare(courses[b].tier) || courses[a].title.localeCompare(courses[b].title);
      }).map(function (id) {
        var course = courses[id];
        return '<article class="pc-entry"><a class="pc-entry-title" href="' + href('courses', id) + '">' + e(course.title) + '</a>' +
          '<div class="pc-meta">' + e([course.instructor, course.year].filter(Boolean).join(' · ')) + ' · ' +
          '<span class="pc-tier pc-tier-' + e(course.tier.toLowerCase()) + '">' + e(course.tier) + '</span> ' + e(course.format) + '</div></article>';
      }).join('');
      return '<section class="pc-entry-group"><div class="pc-group-head"><a href="' + href('courses', byUniversity[university][0]) + '">' + e(university) + '</a>' +
        '<span class="pc-group-count">' + byUniversity[university].length + ' course' + (byUniversity[university].length === 1 ? '' : 's') + '</span></div>' + entries + '</section>';
    }).join('');
    return '<section class="pc-panel">' + crumbs([]) +
      '<header class="pc-detail-head"><div class="pc-kicker">University courses</div><h2>Study the ideas with their teachers</h2>' +
      '<p class="pc-intro">Alongside the books, this index curates university philosophy courses whose materials are publicly reachable. Each record links to the original videos, transcripts, lecture notes, readings, or syllabus — nothing is hosted here — and every course carries a tier saying how much of it you can actually study for free. Where the university publishes its syllabus, every lecture is indexed with what it teaches and the philosophers and concepts it uses.</p></header>' +
      '<div class="pc-tier-legend">' +
      ['A', 'B', 'C'].map(function (tier) {
        return '<div class="pc-overview-card"><span class="pc-tier pc-tier-' + tier.toLowerCase() + '">' + tier + '</span><span>' + e(TIER_LABELS[tier]) + ' — ' + courseTierCount(tier) + ' course' + (courseTierCount(tier) === 1 ? '' : 's') + '</span></div>';
      }).join('') + '</div>' +
      '<h3 class="pc-section-title">Start with a full free course</h3><div class="pc-actions">' +
      featured.map(function (id) {
        return chip('courses', id, courses[id].university + ' · ' + courses[id].title);
      }).join('') + '</div>' +
      '<h3 class="pc-section-title">All courses by university</h3>' + groups + '</section>';
  }

  function courseLink(label, url, primary) {
    if (!url) return '';
    return '<a class="pc-course-link' + (primary ? ' primary' : '') + '" href="' + e(url) + '" target="_blank" rel="noopener noreferrer">' + e(label) + ' <span aria-hidden="true">↗</span></a>';
  }

  function courseRefs(type, slug) {
    return ((state.data[type][slug] || {}).courses || []).filter(function (ref) {
      return state.data.courses[ref[0]];
    });
  }

  function courseLectureGroups(type, slug) {
    var grouped = {};
    courseRefs(type, slug).forEach(function (ref) {
      (grouped[ref[0]] || (grouped[ref[0]] = [])).push(ref[1]);
    });
    return Object.keys(grouped).sort(function (a, b) {
      var ca = state.data.courses[a], cb = state.data.courses[b];
      return ca.university.localeCompare(cb.university) || ca.title.localeCompare(cb.title);
    }).map(function (cid) {
      var course = state.data.courses[cid];
      var entries = grouped[cid].sort(function (a, b) { return a - b; }).map(function (n) {
        var lecture = course._lectureByNumber[n];
        if (!lecture) return '';
        var otherChips = '';
        if (type !== 'concepts') {
          otherChips += lecture.concepts.slice(0, 6).map(function (s2) {
            return state.data.concepts[s2] ? chip('concepts', s2, state.data.concepts[s2].name) : '';
          }).join('');
        }
        if (type !== 'philosophers') {
          otherChips += lecture.philosophers.slice(0, 4).map(function (s2) {
            return state.data.philosophers[s2] ? chip('philosophers', s2, state.data.philosophers[s2].name, 'philosopher') : '';
          }).join('');
        }
        return '<article class="pc-entry"><a class="pc-entry-title" href="' + href('courses', cid, n) + '">Lecture ' + n + ': ' + e(lecture.title) + '</a>' +
          (lecture.summary ? '<p>' + e(lecture.summary) + '</p>' : '') +
          (otherChips ? '<div class="pc-entry-tags">' + otherChips + '</div>' : '') + '</article>';
      }).join('');
      return '<section class="pc-entry-group"><div class="pc-group-head">' +
        '<a href="' + href('courses', cid) + '">' + e(course.university) + ' — ' + e(course.title) + '</a>' +
        '<span class="pc-group-count">' + grouped[cid].length + ' lecture' + (grouped[cid].length === 1 ? '' : 's') + '</span></div>' + entries + '</section>';
    }).join('');
  }

  function courseDetail(cid) {
    var course = state.data.courses[cid];
    if (!course) return missingDetail('course');
    var links = courseLink(course.links.video ? 'Watch / videos' : 'Course site', course.links.video || course.source, true);
    if (course.links.video && course.source && course.source !== course.links.video) {
      links += courseLink('Course site', course.source);
    }
    links += courseLink('Transcript', course.links.transcript) + courseLink('Notes / slides', course.links.notes) +
      courseLink('Readings', course.links.reading) + courseLink('Syllabus', course.links.syllabus);
    var siblings = Object.keys(state.data.courses).filter(function (id) {
      return id !== cid && state.data.courses[id].university === course.university;
    });
    var tags = (course.tags || []).map(function (tag) { return '<span class="pc-tag">' + e(tag) + '</span>'; }).join('');
    var lectures = course.lectures || [];
    var lectureRows = lectures.map(function (lecture) {
      var isOther = lecture.kind !== 'lecture';
      var lectureTags = lecture.concepts.map(function (slug) {
        return state.data.concepts[slug] ? chip('concepts', slug, state.data.concepts[slug].name) : '';
      }).join('') + lecture.philosophers.map(function (slug) {
        return state.data.philosophers[slug] ? chip('philosophers', slug, state.data.philosophers[slug].name, 'philosopher') : '';
      }).join('');
      return '<article class="pc-chapter' + (isOther ? ' pc-front-matter' : '') + '" id="lecture-' + lecture.n + '">' +
        '<div class="pc-chapter-number">Lecture ' + lecture.n + (isOther ? ' · ' + e(lecture.kind) : '') + '</div><h3>' + e(lecture.title) + '</h3>' +
        (lecture.summary ? '<p>' + e(lecture.summary) + '</p>' : '') +
        (lectureTags ? '<div class="pc-entry-tags">' + lectureTags + '</div>' : '') + '</article>';
    }).join('');
    return '<article class="pc-panel">' + crumbs(['Course']) +
      '<header class="pc-detail-head"><div class="pc-kicker">' + e(course.university) + ' · University course</div><h2>' + e(course.title) + '</h2>' +
      '<p class="pc-byline">' + e([course.instructor, course.year].filter(Boolean).join(' · ')) + '</p>' +
      '<p class="pc-intro">' + e(course.description) + '</p>' +
      '<div class="pc-course-badges"><span class="pc-tier pc-tier-' + e(course.tier.toLowerCase()) + '" title="' + e(TIER_LABELS[course.tier] || '') + '">' + e(course.tier) + ' — ' + e(TIER_LABELS[course.tier] || course.tier) + '</span>' +
      '<span class="pc-tag">' + e(course.format) + '</span><span class="pc-tag">' + e(course.extent) + '</span></div>' +
      (tags ? '<div class="pc-entry-tags">' + tags + '</div>' : '') + '</header>' +
      (course.concepts.length ? '<h3 class="pc-section-title">Concepts explored</h3><div class="pc-actions">' +
        course.concepts.map(function (slug) {
          return state.data.concepts[slug] ? chip('concepts', slug, state.data.concepts[slug].name) : '';
        }).join('') + '</div>' : '') +
      (course.philosophers.length ? '<h3 class="pc-section-title">Philosophers</h3><div class="pc-actions">' +
        course.philosophers.map(function (slug) {
          return state.data.philosophers[slug] ? chip('philosophers', slug, state.data.philosophers[slug].name, 'philosopher') : '';
        }).join('') + '</div>' : '') +
      (lectures.length
        ? '<h3 class="pc-section-title">Lectures <span class="pc-external-note">(' + lectures.length + ', from the public syllabus)</span></h3>' + lectureRows
        : '<h3 class="pc-section-title">Lectures</h3><div class="pc-start">No public lecture listing could be indexed for this course yet — the links below go to what the university makes public.</div>') +
      '<h3 class="pc-section-title">Course materials <span class="pc-external-note">(external sources)</span></h3>' +
      '<div class="pc-course-links">' + links + '</div>' +
      '<details class="pc-course-notes"><summary>Access notes &amp; verification</summary><p>' + e(course.remarks || 'Links verified October 2026.') + '</p></details>' +
      (siblings.length ? '<h3 class="pc-section-title">More from ' + e(course.university) + '</h3><div class="pc-actions">' +
        siblings.map(function (id) { return chip('courses', id, state.data.courses[id].title); }).join('') + '</div>' : '') +
      '</article>';
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
      (courseRefs('concepts', slug).length ? '<h3 class="pc-section-title">Courses that teach this idea</h3>' + courseLectureGroups('concepts', slug) : '') +
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
      (courseRefs('philosophers', slug).length ? '<h3 class="pc-section-title">Courses that teach this philosopher</h3>' + courseLectureGroups('philosophers', slug) : '') +
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
      '<p class="pc-intro">' + e(book.intro || 'This volume uses its subject as a way into philosophical questions raised by its stories, characters, conflicts, or cultural role.') + '</p>' +
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
    if (kind === 'course' && id) return courseDetail(id);
    return state.listType === 'courses' ? coursesHomeDetail() : homeDetail();
  }

  function titleForParts() {
    var kind = state.parts[1] || '';
    var id = state.parts[2] || '';
    if (kind === 'book' && state.data.books[id]) return state.data.books[id].title;
    if (kind === 'concept' && state.data.concepts[id]) return state.data.concepts[id].name;
    if (kind === 'philosopher' && state.data.philosophers[id]) return state.data.philosophers[id].name;
    if (kind === 'course' && state.data.courses[id]) return state.data.courses[id].title;
    return 'Philosophy × Pop Culture';
  }

  function renderCurrent() {
    state.ctx.app.innerHTML = shell(detailForParts());
    renderList();
  }

  function scrollToHashChapter() {
    if (!location.hash || !/^#(?:chapter|lecture)-\d+$/.test(location.hash)) return;
    var target = document.querySelector(location.hash);
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
      if (event.target.id === 'pc-domain') {
        state.domain = event.target.value;
        renderList();
        return;
      }
      if (event.target.id === 'pc-university') {
        state.university = event.target.value;
        renderList();
        return;
      }
      if (event.target.id === 'pc-tier') {
        state.tier = event.target.value;
        renderList();
      }
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
      if (state.listType === button.getAttribute('data-pc-type')) return;
      state.listType = button.getAttribute('data-pc-type');
      renderCurrent();
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
      scrollToHashChapter();
      window.scrollTo(0, 0);
    }).catch(function (error) {
      ctx.showError('Could not load the pop-culture index — ' + error.message);
    });
  }

  window.PopcultExplorer = { route: route };
})();
