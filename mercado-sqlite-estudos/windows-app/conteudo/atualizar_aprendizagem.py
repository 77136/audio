#!/usr/bin/env python3
"""Atualiza as abas offline de aprendizagem e exercícios usando aprendizagem.json."""
from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent

CSS = r"""
/* Abas e aprendizagem: estilos locais, sem fontes ou recursos de rede. */
.learn-modebar{position:sticky;top:0;z-index:20;background:#fffdf5;border-bottom:1px solid #d6dfd6;box-shadow:0 3px 16px #132e3608}
.learn-modebar .wrap{display:flex;align-items:center;justify-content:space-between;gap:20px;padding-block:11px}
.learn-brand{color:var(--green);font-size:.82rem;font-weight:800;letter-spacing:.01em}
.learn-tabs{display:flex;gap:5px;padding:4px;border-radius:12px;background:#edf0e8;min-width:0}
.learn-tab{appearance:none;border:0;border-radius:8px;padding:11px 19px;background:transparent;color:#455d53;font:650 .9rem/1.3 ui-sans-serif,system-ui,sans-serif;cursor:pointer;min-width:0}
.learn-tab:hover{background:#e0e8dc}.learn-tab[aria-selected="true"]{background:var(--green);color:white;box-shadow:0 2px 5px #18303818}
.learn-tab:focus-visible,.learn-copy:focus-visible,.learn-lesson:focus-visible,.learn-code:focus-visible,[role="tabpanel"]:focus-visible{outline:3px solid #c58b19;outline-offset:4px}
#guia[hidden],#aprendizagem[hidden],#exercicios[hidden],.learn-level-panel[hidden]{display:none!important}
#guia,#aprendizagem,#exercicios,.learn-lesson{scroll-margin-top:94px}
.learn-page{padding:44px 0 52px;border-bottom:1px solid var(--line)}
.learn-intro{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:26px;align-items:start;margin-bottom:22px}
.learn-intro h2{margin-bottom:15px}.learn-intro p:last-child{margin-bottom:0}
.learn-total{display:flex;align-items:center;gap:13px;background:#e4eee0;border:1px solid #cbdcc7;border-radius:16px;padding:16px 19px;color:#345443}
.learn-total strong{font-size:2.1rem;line-height:1;color:var(--green)}.learn-total span{font-size:.78rem;line-height:1.35;max-width:98px}
.learn-notice{background:#fff0d8;border-left:4px solid #c48b25;border-radius:0 10px 10px 0;padding:14px 18px;font-size:.89rem;margin:0 0 25px}
.learn-level-tabs{display:flex;gap:8px;flex-wrap:wrap;margin:0 0 20px}
.learn-level-tabs .learn-tab{background:#fff;border:1px solid #d0ddd1;padding:12px 18px;display:flex;align-items:center;gap:12px;justify-content:center}
.learn-level-tabs .learn-tab[aria-selected="true"]{background:var(--green);border-color:var(--green)}
.learn-count{font-size:.72rem;display:inline-grid;place-items:center;min-width:23px;height:23px;padding:0 5px;border-radius:20px;background:#e8efe3;color:#3d604b}
.learn-tab[aria-selected="true"] .learn-count{background:#ffffff26;color:white}
.learn-level-heading{display:flex;align-items:baseline;gap:15px;margin:25px 0 19px;flex-wrap:wrap}
.learn-level-heading h3{font-size:1.34rem;margin:0}.learn-level-heading p{font-size:.89rem;color:var(--muted);margin:0;max-width:720px}
.learn-cards{display:grid;grid-template-columns:1fr;gap:17px}
.learn-lesson{min-width:0;border:1px solid #d4ded3;border-radius:16px;background:#fff;overflow:hidden}
.learn-lesson:target{border-color:#a27a30;box-shadow:0 0 0 3px #f6c06a5c}
.learn-lesson-head{padding:23px 26px 19px}
.learn-meta{display:flex;align-items:center;justify-content:space-between;gap:14px;margin-bottom:11px;font-size:.72rem;color:var(--green);font-weight:750;letter-spacing:.035em}
.learn-meta a{font-size:.74rem;font-weight:600;letter-spacing:0;text-decoration:none;white-space:nowrap;color:#65746c}
.learn-meta a:hover{color:var(--green);text-decoration:underline}
.learn-lesson h4{font-size:1.2rem;line-height:1.3;letter-spacing:-.015em;margin:0 0 12px;overflow-wrap:anywhere}
.learn-question{margin:0 0 16px;color:#435b50;font-size:.95rem}
.learn-tags{display:flex;flex-wrap:wrap;gap:6px;list-style:none;margin:0;padding:0}
.learn-tags li{font-family:ui-monospace,SFMono-Regular,Consolas,monospace;margin:0;padding:3px 8px;font-size:.69rem;line-height:1.45;background:#edf3e9;color:#41634c;border-radius:5px;max-width:100%;overflow-wrap:anywhere}
.learn-hint{border-top:1px solid #e8ece5;padding:12px 26px;background:#fcfdf8}
.learn-hint summary,.learn-solution>summary{font-weight:650;font-size:.87rem;cursor:pointer;color:var(--green)}
.learn-hint p{font-size:.9rem;color:var(--muted);margin:11px 0 3px}
.learn-solution{border-top:1px solid #e2e9df}
.learn-solution>summary{padding:15px 26px;background:#f2f6ee}
.learn-solution[open]>summary{border-bottom:1px solid #e2e9df;background:#e9f1e4}
.learn-solution-body{padding:22px 26px 24px;min-width:0}
.learn-codebar{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:9px}
.learn-codebar span{font-size:.73rem;font-weight:750;color:#5b6e63;letter-spacing:.07em;text-transform:uppercase}
.learn-copy{appearance:none;border:1px solid #174c3e;background:var(--green);color:white;padding:9px 14px;border-radius:8px;font:650 .8rem/1.35 ui-sans-serif,system-ui,sans-serif;cursor:pointer;white-space:nowrap}
.learn-copy:hover{background:#104b3b}.learn-copy[data-copy-state="done"]{background:#e5efdf;color:#24523c;border-color:#b7cdb0}
.learn-code{margin:0;max-width:100%;font-size:.84rem;line-height:1.7;overflow-x:auto}
.learn-explanation{margin-top:22px;padding:17px 19px;background:#f7f8f2;border-left:3px solid #92b68c;border-radius:0 9px 9px 0}
.learn-explanation h5,.learn-result-heading{font-size:.91rem;line-height:1.3;margin:0 0 9px;letter-spacing:-.01em}
.learn-explanation p{font-size:.9rem;color:#476050;margin:0 0 10px}.learn-explanation p:last-child{margin-bottom:0}
.learn-result{margin-top:22px;min-width:0}.learn-result-top{display:flex;gap:15px;justify-content:space-between;align-items:baseline;flex-wrap:wrap}
.learn-result-top a{font-size:.81rem}.learn-result-note{font-size:.79rem;color:#617265;margin:0 0 11px}
.learn-result-wrap{max-width:100%;overflow:auto;border:1px solid #d9e3d5;border-radius:9px}
.learn-result table{font-size:.78rem;margin:0}.learn-result th{font-size:.73rem;background:#edf3e8}.learn-result th,.learn-result td{padding:10px 12px;white-space:nowrap}
.learn-result td{font-family:ui-monospace,SFMono-Regular,Consolas,monospace}.learn-null{font-style:italic;color:#7b887b}
.learn-copy-status{min-height:1.7em;font-size:.82rem;font-weight:600;color:var(--green);margin:0 0 18px}
.learn-footer-note{font-size:.86rem;color:var(--muted);margin:25px 0 0;max-width:780px}
.learn-nojs{padding:14px 18px;background:#fff0d8;margin:0;font-size:.88rem}
.learn-practice-cta{margin:0 0 23px;font-size:.91rem;font-weight:700}
.exercise-cards{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px;align-items:start}
.exercise-actions{border-top:1px solid #e4eade;padding:15px 26px 18px;background:#fafcf6}
.exercise-solution-link{display:inline-flex;align-items:center;gap:9px;border:1px solid #bed2b5;border-radius:8px;background:#edf4e8;color:#285d43;padding:9px 13px;font-size:.82rem;font-weight:700;line-height:1.4;text-decoration:none}
.exercise-solution-link:hover{background:#dfeeda;color:#174d33}
.exercise-card .learn-question{margin-bottom:16px}.exercise-hint summary{font-size:.85rem}
@media(max-width:760px){.learn-brand{display:none}.learn-modebar .wrap{justify-content:center;padding-block:8px}.learn-tabs{width:100%}.learn-tabs>.learn-tab{flex:1;padding:11px 10px}.learn-page{padding:30px 0 38px}.learn-intro{grid-template-columns:minmax(0,1fr);gap:18px}.learn-total{justify-self:start;padding:12px 16px}.learn-total span{max-width:initial}.learn-total strong{font-size:1.65rem}.learn-level-tabs{gap:6px}.learn-level-tabs .learn-tab{padding:10px 11px;gap:7px;font-size:.77rem;flex:1}.learn-count{min-width:20px;height:20px;font-size:.67rem}.learn-level-heading{gap:7px}.learn-lesson-head{padding:19px 18px 17px}.learn-lesson h4{font-size:1.08rem}.learn-question{font-size:.9rem}.learn-hint{padding:12px 18px}.learn-solution>summary{padding:14px 18px}.learn-solution-body{padding:18px}.learn-code{font-size:.76rem;padding:15px}.learn-explanation{padding:14px}.learn-result-top{gap:2px}.learn-meta{font-size:.68rem}.learn-meta a{font-size:.7rem}#guia,#aprendizagem,.learn-lesson{scroll-margin-top:84px}}
@media(max-width:760px){.learn-tabs>.learn-tab{padding:11px 7px;font-size:.79rem}.exercise-cards{grid-template-columns:minmax(0,1fr)}.exercise-actions{padding:14px 18px 17px}#exercicios{scroll-margin-top:84px}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
@media print{.learn-modebar,.learn-copy,.learn-copy-status{display:none}.learn-page{padding:16px 0}.learn-lesson{break-inside:avoid}.learn-level-tabs{display:none}.learn-code{background:#f1f4ed;color:#183038;white-space:pre-wrap}.learn-result-wrap{overflow:visible}}
"""

JS = r"""
(() => {
  'use strict';
  const dataElement = document.getElementById('learning-data');
  if (!dataElement) return;
  const data = JSON.parse(dataElement.textContent);
  const lessons = new Map(data.lessons.map(lesson => [lesson.id, lesson]));
  const modeTabs = [...document.querySelectorAll('[data-learn-mode]')];
  const levelTabs = [...document.querySelectorAll('[data-learn-level]')];
  const exerciseLevelTabs = [...document.querySelectorAll('[data-exercise-level]')];
  const status = document.getElementById('learn-copy-status');
  const guidePanel = document.getElementById('guia');
  const learningPanel = document.getElementById('aprendizagem');
  const exercisePanel = document.getElementById('exercicios');
  const modePanels = {guide: guidePanel, learning: learningPanel, exercises: exercisePanel};
  const modeHashes = {guide: '#guia', learning: '#aprendizagem', exercises: '#exercicios'};

  function selectMode(mode) {
    if (!modePanels[mode]) return;
    Object.entries(modePanels).forEach(([name, panel]) => { panel.hidden = name !== mode; });
    modeTabs.forEach(tab => {
      const active = tab.dataset.learnMode === mode;
      tab.setAttribute('aria-selected', String(active));
      tab.tabIndex = active ? 0 : -1;
    });
  }

  function selectLevel(level, area = 'learning') {
    if (!data.levels.some(item => item.id === level)) return;
    const tabs = area === 'exercises' ? exerciseLevelTabs : levelTabs;
    tabs.forEach(tab => {
      const active = (area === 'exercises' ? tab.dataset.exerciseLevel : tab.dataset.learnLevel) === level;
      tab.setAttribute('aria-selected', String(active));
      tab.tabIndex = active ? 0 : -1;
      document.getElementById(tab.getAttribute('aria-controls')).hidden = !active;
    });
  }

  function scrollToElement(element) {
    if (element) requestAnimationFrame(() => element.scrollIntoView({block: 'start', behavior: 'auto'}));
  }

  function routeHash(shouldScroll = true) {
    let hash;
    try { hash = decodeURIComponent(location.hash.slice(1)); }
    catch (_) { hash = ''; }
    const lessonMatch = /^consulta-(E\d{2})$/.exec(hash);
    const lesson = lessonMatch && lessons.get(lessonMatch[1]);
    if (lesson) {
      selectMode('learning');
      selectLevel(lesson.level);
      const card = document.getElementById('consulta-' + lesson.id);
      card.querySelector('.learn-solution').open = true;
      if (shouldScroll) scrollToElement(card);
      return;
    }
    const exerciseMatch = /^exercicio-(E\d{2})$/.exec(hash);
    const exercise = exerciseMatch && lessons.get(exerciseMatch[1]);
    if (exercise) {
      selectMode('exercises');
      selectLevel(exercise.level, 'exercises');
      if (shouldScroll) scrollToElement(document.getElementById('exercicio-' + exercise.id));
      return;
    }
    if (hash === 'aprendizagem') {
      selectMode('learning');
      if (shouldScroll) scrollToElement(learningPanel);
      return;
    }
    if (hash === 'exercicios') {
      selectMode('exercises');
      if (shouldScroll) scrollToElement(exercisePanel);
      return;
    }
    const target = hash && document.getElementById(hash);
    if (!hash || hash === 'guia' || (target && guidePanel.contains(target))) {
      selectMode('guide');
      if (shouldScroll && target) scrollToElement(target);
    }
  }

  function changeHash(hash) {
    if (location.hash === hash) routeHash();
    else location.hash = hash;
  }

  function activateTab(tab) {
    if (tab.dataset.learnMode) {
      selectMode(tab.dataset.learnMode);
      changeHash(modeHashes[tab.dataset.learnMode]);
    } else if (tab.dataset.learnLevel) {
      selectLevel(tab.dataset.learnLevel);
      // Um link de consulta anterior não deve continuar apontando para outro nível.
      if (/^#consulta-E\d{2}$/.test(location.hash)) {
        try { history.replaceState(null, '', '#aprendizagem'); }
        catch (_) { location.hash = '#aprendizagem'; }
      }
    } else if (tab.dataset.exerciseLevel) {
      selectLevel(tab.dataset.exerciseLevel, 'exercises');
      if (/^#exercicio-E\d{2}$/.test(location.hash)) {
        try { history.replaceState(null, '', '#exercicios'); }
        catch (_) { location.hash = '#exercicios'; }
      }
    }
  }

  function fallbackCopy(text) {
    const active = document.activeElement;
    const selection = window.getSelection();
    const ranges = [];
    if (selection) for (let i = 0; i < selection.rangeCount; i++) ranges.push(selection.getRangeAt(i).cloneRange());
    const area = document.createElement('textarea');
    area.value = text;
    area.readOnly = true;
    area.tabIndex = -1;
    area.setAttribute('aria-label', 'Texto temporário para copiar SQL');
    area.style.cssText = 'position:fixed;left:-10000px;top:0;width:1px;height:1px;opacity:0';
    document.body.appendChild(area);
    let copied = false;
    try {
      area.focus({preventScroll: true});
      area.select();
      area.setSelectionRange(0, area.value.length);
      copied = document.execCommand('copy');
    } catch (_) { copied = false; }
    finally {
      area.remove();
      if (active && typeof active.focus === 'function') active.focus({preventScroll: true});
      if (selection) {
        selection.removeAllRanges();
        ranges.forEach(range => selection.addRange(range));
      }
    }
    return copied;
  }

  async function copySQL(button) {
    const id = button.dataset.copySql;
    const code = document.getElementById('learn-sql-' + id);
    if (!code || button.getAttribute('aria-busy') === 'true') return;
    // textContent preserva operadores como < e >, sem copiar a marcação HTML.
    const text = code.textContent;
    button.setAttribute('aria-busy', 'true');
    let copied = false;
    try {
      if (navigator.clipboard && typeof navigator.clipboard.writeText === 'function') {
        try { await navigator.clipboard.writeText(text); copied = true; }
        catch (_) { copied = fallbackCopy(text); }
      } else copied = fallbackCopy(text);
      if (copied) {
        button.textContent = 'SQL copiado ✓';
        button.dataset.copyState = 'done';
        status.textContent = 'SQL de ' + id + ' copiado. Cole uma consulta por vez no SQLiteOnline.';
        setTimeout(() => { button.textContent = 'Copiar SQL'; delete button.dataset.copyState; }, 2200);
      } else {
        const selection = window.getSelection();
        if (selection) {
          code.closest('pre').focus({preventScroll: true});
          const range = document.createRange();
          range.selectNodeContents(code);
          selection.removeAllRanges();
          selection.addRange(range);
        }
        status.textContent = 'O navegador não liberou a cópia. O SQL de ' + id + ' está selecionado: pressione Ctrl+C ou ⌘C.';
      }
    } finally { button.removeAttribute('aria-busy'); }
  }

  document.addEventListener('click', event => {
    const tab = event.target.closest('[data-learn-mode], [data-learn-level], [data-exercise-level]');
    if (tab) { activateTab(tab); return; }
    const copy = event.target.closest('[data-copy-sql]');
    if (copy) { copySQL(copy); return; }
    // Reativar uma âncora já selecionada também deve mostrar o painel correto.
    const anchor = event.target.closest('a[href^="#"]');
    if (anchor && anchor.getAttribute('href') === location.hash) routeHash();
  });

  document.addEventListener('keydown', event => {
    const tab = event.target.closest('[role="tab"][data-learn-mode], [role="tab"][data-learn-level], [role="tab"][data-exercise-level]');
    if (!tab) return;
    const list = tab.closest('[role="tablist"]');
    const tabs = [...list.querySelectorAll('[role="tab"]')];
    const index = tabs.indexOf(tab);
    let next;
    if (event.key === 'ArrowRight' || event.key === 'ArrowDown') next = (index + 1) % tabs.length;
    else if (event.key === 'ArrowLeft' || event.key === 'ArrowUp') next = (index + tabs.length - 1) % tabs.length;
    else if (event.key === 'Home') next = 0;
    else if (event.key === 'End') next = tabs.length - 1;
    else return;
    event.preventDefault();
    tabs[next].focus({preventScroll: true});
    activateTab(tabs[next]);
  });

  window.addEventListener('hashchange', () => routeHash());
  selectLevel(data.levels[0].id);
  selectLevel(data.levels[0].id, 'exercises');
  routeHash(Boolean(location.hash));
})();
"""


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def paragraphs(value: str) -> str:
    return ''.join(f'<p>{esc(part.strip())}</p>' for part in value.split('\n\n') if part.strip())


def render_preview(lesson: dict) -> str:
    preview = lesson['preview']
    columns, rows = preview['columns'], preview['rows']
    if not rows:
        return '<p class="learn-result-note">Esta consulta retorna um resultado vazio na base original.</p>'
    head = ''.join(f'<th scope="col">{esc(column)}</th>' for column in columns)
    body = ''.join('<tr>' + ''.join('<td><span class="learn-null">NULL</span></td>' if cell is None else f'<td>{esc(cell)}</td>' for cell in row) + '</tr>' for row in rows)
    return (f'<p class="learn-result-note">Prévia: {len(rows)} de {lesson["expected_rows"]} linhas. Valores monetários seguem a unidade indicada no nome da coluna.</p>'
            f'<div class="learn-result-wrap" tabindex="0" role="region" aria-label="Prévia do resultado de {esc(lesson["id"])}"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>')


def render_lesson(lesson: dict, label: str) -> str:
    lesson_id = esc(lesson['id'])
    tags = ''.join(f'<li>{esc(concept)}</li>' for concept in lesson['concepts'])
    return f'''<article class="learn-lesson" id="consulta-{lesson_id}" data-lesson-id="{lesson_id}" aria-labelledby="learn-title-{lesson_id}" tabindex="-1">
  <div class="learn-lesson-head">
    <div class="learn-meta"><span>{lesson_id} · {esc(label)}</span><a href="#consulta-{lesson_id}" aria-label="Link direto para a consulta {lesson_id}">Link da consulta ↗</a></div>
    <h4 id="learn-title-{lesson_id}">{esc(lesson['title'])}</h4>
    <p class="learn-question">{esc(lesson['question'])}</p>
    <ul class="learn-tags" aria-label="Conceitos desta consulta">{tags}</ul>
  </div>
  <details class="learn-hint"><summary>Uma dica antes de tentar</summary><p>{esc(lesson['hint'])}</p></details>
  <details class="learn-solution">
    <summary>Ver SQL, explicação e resultado</summary>
    <div class="learn-solution-body">
      <div class="learn-codebar"><span>Consulta completa · SQLite</span><button type="button" class="learn-copy" data-copy-sql="{lesson_id}" aria-label="Copiar SQL da consulta {lesson_id}">Copiar SQL</button></div>
      <pre class="learn-code" tabindex="0" aria-label="Código SQL da consulta {lesson_id}"><code id="learn-sql-{lesson_id}">{esc(lesson['sql'])}</code></pre>
      <div class="learn-explanation"><h5>Como a consulta funciona</h5>{paragraphs(lesson['explanation'])}</div>
      <div class="learn-result"><div class="learn-result-top"><h5 class="learn-result-heading">Resultado esperado · {lesson['expected_rows']} linhas</h5><a href="04_resultados_esperados.html#{lesson_id}" target="_blank" rel="noopener">Conferir resultado de {lesson_id} ↗</a></div>{render_preview(lesson)}</div>
    </div>
  </details>
</article>'''


def render_learning(data: dict) -> str:
    lessons = {lesson['id']: lesson for lesson in data['lessons']}
    tabs, panels = [], []
    for index, level in enumerate(data['levels']):
        level_id, label = esc(level['id']), esc(level['label'])
        selected, tabindex, hidden = ('true', '0', '') if index == 0 else ('false', '-1', ' hidden')
        tabs.append(f'<button type="button" class="learn-tab" id="learn-tab-{level_id}" role="tab" aria-selected="{selected}" aria-controls="learn-panel-{level_id}" tabindex="{tabindex}" data-learn-level="{level_id}">{label}<span class="learn-count" aria-label="{len(level["ids"])} consultas">{len(level["ids"])}</span></button>')
        cards = '\n'.join(render_lesson(lessons[item], level['label']) for item in level['ids'])
        panels.append(f'<section class="learn-level-panel" id="learn-panel-{level_id}" role="tabpanel" aria-labelledby="learn-tab-{level_id}" tabindex="0"{hidden}><div class="learn-level-heading"><h3>{label}</h3><p>{esc(level["description"])}</p></div><div class="learn-cards">{cards}</div></section>')
    return f'''<section class="learn-page" id="aprendizagem" role="tabpanel" aria-labelledby="learn-tab-learning" tabindex="0" hidden>
  <div class="wrap">
    <div class="learn-intro"><div><p class="section-label">Aprendizagem / consultas por nível</p><h2>Aprenda SQL, uma consulta por vez.</h2><p class="section-intro">Escolha um nível, leia a pergunta e tente escrever sua consulta. Quando precisar, abra a dica ou compare com o SQL completo e sua explicação. Tudo aqui funciona sem conexão depois de baixar esta pasta.</p></div><div class="learn-total"><strong>{len(lessons)}</strong><span>consultas explicadas<br>com resultado de referência</span></div></div>
    <p class="learn-notice"><strong>No SQLiteOnline, cole uma consulta por vez.</strong> O botão Run executa a seleção; sem seleção, executa todo o editor. Esta aba é um guia de estudo: execute as consultas na base <code>mercado.db</code> aberta no site.</p>
    <p class="learn-practice-cta"><a href="#exercicios">Praticar na lista de exercícios →</a></p>
    <div class="learn-level-tabs" role="tablist" aria-label="Nível das consultas">{''.join(tabs)}</div>
    <p class="learn-copy-status" id="learn-copy-status" role="status" aria-live="polite" aria-atomic="true">Abra uma consulta para ver o SQL e copiar.</p>
    {''.join(panels)}
    <p class="learn-footer-note">As prévias foram calculadas na base original. Se você alterar os dados, os resultados podem mudar. Pratique pela aba <a href="#exercicios">Exercícios</a> ou use os arquivos <a href="02_exercicios.sql">de enunciados</a> e <a href="03_gabarito.sql">do gabarito</a>. O <a href="#modelo">mapa de relacionamentos</a> fica disponível no guia.</p>
  </div>
</section>'''


def render_exercise(lesson: dict, label: str) -> str:
    lesson_id = esc(lesson['id'])
    tags = ''.join(f'<li>{esc(concept)}</li>' for concept in lesson['concepts'])
    return f'''<article class="learn-lesson exercise-card" id="exercicio-{lesson_id}" data-exercise-id="{lesson_id}" aria-labelledby="exercise-title-{lesson_id}" tabindex="-1">
  <div class="learn-lesson-head">
    <div class="learn-meta"><span>{lesson_id} · {esc(label)}</span><a href="#exercicio-{lesson_id}" aria-label="Link direto para o exercício {lesson_id}">Link do exercício ↗</a></div>
    <h4 id="exercise-title-{lesson_id}">{esc(lesson['title'])}</h4>
    <p class="learn-question exercise-question">{esc(lesson['question'])}</p>
    <ul class="learn-tags" aria-label="Conceitos deste exercício">{tags}</ul>
  </div>
  <details class="learn-hint exercise-hint"><summary>Abrir uma dica</summary><p>{esc(lesson['hint'])}</p></details>
  <div class="exercise-actions"><a class="exercise-solution-link" href="#consulta-{lesson_id}" data-exercise-solution="{lesson_id}" aria-label="Ver explicação e SQL do exercício {lesson_id}">Ver explicação e SQL <span aria-hidden="true">→</span></a></div>
</article>'''


def render_exercises(data: dict) -> str:
    lessons = {lesson['id']: lesson for lesson in data['lessons']}
    tabs, panels = [], []
    for index, level in enumerate(data['levels']):
        level_id, label = esc(level['id']), esc(level['label'])
        selected, tabindex, hidden = ('true', '0', '') if index == 0 else ('false', '-1', ' hidden')
        tabs.append(f'<button type="button" class="learn-tab" id="exercise-tab-{level_id}" role="tab" aria-selected="{selected}" aria-controls="exercise-panel-{level_id}" tabindex="{tabindex}" data-exercise-level="{level_id}">{label}<span class="learn-count" aria-label="{len(level["ids"])} exercícios">{len(level["ids"])}</span></button>')
        cards = '\n'.join(render_exercise(lessons[item], level['label']) for item in level['ids'])
        panels.append(f'<section class="learn-level-panel exercise-level-panel" id="exercise-panel-{level_id}" role="tabpanel" aria-labelledby="exercise-tab-{level_id}" tabindex="0"{hidden}><div class="learn-level-heading"><h3>{label}</h3><p>{esc(level["description"])}</p></div><div class="exercise-cards">{cards}</div></section>')
    return f'''<section class="learn-page" id="exercicios" role="tabpanel" aria-labelledby="learn-tab-exercises" tabindex="0" hidden>
  <div class="wrap">
    <div class="learn-intro"><div><p class="section-label">Exercícios / pratique por nível</p><h2>Sua vez de escrever o SQL.</h2><p class="section-intro">Aqui estão os mesmos 32 desafios de <a href="02_exercicios.sql">02_exercicios.sql</a>. Escolha um nível e resolva cada pergunta no SQLiteOnline. Abra uma dica quando precisar e confira a explicação depois de tentar.</p></div><div class="learn-total"><strong>{len(lessons)}</strong><span>exercícios para praticar<br>com dicas sob demanda</span></div></div>
    <p class="learn-notice"><strong>Prepare a base antes de começar.</strong> Abra <code>mercado.db</code> no SQLiteOnline, escreva sua consulta e execute uma por vez. O <a href="#comecar">guia de abertura</a> mostra cada passo. As respostas ficam na aba Aprendizagem, no link de cada exercício.</p>
    <div class="learn-level-tabs exercise-level-tabs" role="tablist" aria-label="Nível dos exercícios">{''.join(tabs)}</div>
    {''.join(panels)}
    <p class="learn-footer-note">Use a base original para comparar os resultados. Você pode manter esta lista aberta em uma janela e o SQLiteOnline em outra, tanto no Windows quanto no macOS. Para revisar um conceito, visite a aba <a href="#aprendizagem">Aprendizagem</a> ou o <a href="#modelo">mapa de relacionamentos</a>.</p>
  </div>
</section>'''


def render_modes() -> str:
    return '''<div class="learn-modebar"><div class="wrap"><span class="learn-brand">M. / Laboratório de SQL</span><div class="learn-tabs" role="tablist" aria-label="Área do laboratório"><button type="button" class="learn-tab" id="learn-tab-guide" role="tab" aria-selected="true" aria-controls="guia" tabindex="0" data-learn-mode="guide">Guia do banco</button><button type="button" class="learn-tab" id="learn-tab-learning" role="tab" aria-selected="false" aria-controls="aprendizagem" tabindex="-1" data-learn-mode="learning">Aprendizagem</button><button type="button" class="learn-tab" id="learn-tab-exercises" role="tab" aria-selected="false" aria-controls="exercicios" tabindex="-1" data-learn-mode="exercises">Exercícios</button></div></div></div>'''


def replace_block(source: str, name: str, content: str) -> str:
    start, end = f'<!-- LEARN:{name}:START -->', f'<!-- LEARN:{name}:END -->'
    pattern = re.compile(re.escape(start) + r'.*?' + re.escape(end), re.DOTALL)
    block = start + '\n' + content + '\n' + end
    if not pattern.search(source):
        raise ValueError(f'Marcador ausente: {name}')
    return pattern.sub(lambda _: block, source, count=1)


def main() -> None:
    data = json.loads((ROOT / 'aprendizagem.json').read_text(encoding='utf-8'))
    assert len(data['lessons']) == 32, 'A aba deve conter as 32 consultas.'
    assert {lesson['id'] for lesson in data['lessons']} == {f'E{number:02}' for number in range(1, 33)}
    assert [level['id'] for level in data['levels']] == ['iniciante', 'intermediario', 'avancado']
    assigned = [item for level in data['levels'] for item in level['ids']]
    assert len(assigned) == len(set(assigned)) == 32
    path = ROOT / 'LEIA-ME.html'
    source = path.read_text(encoding='utf-8')
    if '<!-- LEARN:CONTENT:START -->' not in source:
        source = source.replace('</head>', '<!-- LEARN:STYLE:START --><!-- LEARN:STYLE:END -->\n</head>', 1)
        marker = '<header class="hero">'
        modebar = '<!-- LEARN:MODES:START -->\n' + render_modes() + '\n<!-- LEARN:MODES:END -->\n' + '''
<noscript><p class="learn-nojs">As abas interativas precisam de JavaScript. Você pode estudar pelos <a href="02_exercicios.sql">32 exercícios</a>, pelo <a href="03_gabarito.sql">gabarito SQL</a> e pelos <a href="04_resultados_esperados.html">resultados esperados</a>. O guia do banco continua disponível abaixo.</p></noscript>
'''
        source = source.replace(marker, modebar + marker, 1)
        source = source.replace('\n<main>\n', '\n', 1)
        source = source.replace('<nav class="section-nav"', '<main id="learn-main">\n<div id="guia" role="tabpanel" aria-labelledby="learn-tab-guide" tabindex="0">\n<nav class="section-nav"', 1)
        source = source.replace('</main>', '</div>\n<!-- LEARN:CONTENT:START --><!-- LEARN:CONTENT:END -->\n</main>', 1)
        source = source.replace('</body>', '<!-- LEARN:SCRIPT:START --><!-- LEARN:SCRIPT:END -->\n</body>', 1)
        old = 'Abra <a href="02_exercicios.sql">02_exercicios.sql</a> e resolva os 32 desafios em ordem.'
        new = 'Use a aba <a href="#aprendizagem">Aprendizagem</a> para explorar as 32 consultas por nível, com dicas, SQL e explicações no próprio guia. Se preferir, abra <a href="02_exercicios.sql">02_exercicios.sql</a> e resolva os desafios em ordem.'
        assert old in source
        source = source.replace(old, new, 1)
    if '<!-- LEARN:MODES:START -->' not in source:
        # Migra o guia com duas abas, mantendo o restante do HTML existente.
        old_modes = re.compile(r'<div class="learn-modebar">.*?(?=<noscript>)', re.DOTALL)
        assert old_modes.search(source), 'Barra de abas original não encontrada.'
        source = old_modes.sub(lambda _: '<!-- LEARN:MODES:START -->\n' + render_modes() + '\n<!-- LEARN:MODES:END -->\n', source, count=1)
    old_study = 'Use a aba <a href="#aprendizagem">Aprendizagem</a> para explorar as 32 consultas por nível, com dicas, SQL e explicações no próprio guia.'
    new_study = 'Pratique na aba <a href="#exercicios">Exercícios</a>, com os 32 enunciados organizados por nível. Consulte a aba <a href="#aprendizagem">Aprendizagem</a> para ver as dicas, o SQL e as explicações no próprio guia.'
    source = source.replace(old_study, new_study, 1)
    if '<!-- LEARN:PLATFORMS -->' not in source:
        intro = '<p class="section-intro">O pacote já tem uma base SQLite pronta. Não precisa instalar servidor, cadastrar clientes ou inserir produtos manualmente. Mantenha os arquivos desta pasta juntos para usar os links do guia.</p>'
        platforms = '''<!-- LEARN:PLATFORMS -->
    <aside class="callout"><p><strong>No Windows ou no macOS:</strong> extraia o ZIP antes de abrir os arquivos. No Windows, clique com o botão direito no ZIP e escolha <b>Extrair Tudo</b>; no macOS, dê dois cliques no ZIP. Na pasta extraída, abra <code>LEIA-ME.html</code> em um navegador. Mantenha a pasta completa para que os links para a base e os demais arquivos funcionem.</p></aside>'''
        assert intro in source, 'Introdução do guia não encontrada.'
        source = source.replace(intro, intro + '\n    ' + platforms, 1)
    data_json = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
    source = replace_block(source, 'MODES', render_modes())
    source = replace_block(source, 'STYLE', f'<style id="learn-styles">\n{CSS}\n</style>')
    source = replace_block(source, 'CONTENT', render_learning(data) + '\n' + render_exercises(data))
    source = replace_block(source, 'SCRIPT', f'<script type="application/json" id="learning-data">{data_json}</script>\n<script id="learn-script">\n{JS}\n</script>')
    path.write_text(source, encoding='utf-8')
    print(f'Atualizado: {path.name} · 3 abas · {len(data["lessons"])} consultas + exercícios inline · {len(data["levels"])} níveis')


if __name__ == '__main__':
    main()
