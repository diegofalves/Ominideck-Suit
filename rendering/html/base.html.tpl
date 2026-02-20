    /* Remove modo folha quando em app */
    body.doc-app .screen-canvas,
    body.doc-app .document-wrapper,
    body.doc-app .page,
    body.doc-app .page-container {
      width: 100% !important;
      max-width: none !important;
      margin: 0 !important;
      padding: 0 !important;
      background: transparent !important;
      box-shadow: none !important;
      border: none !important;
    }

<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" />
  <title>{{ title }}</title>
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" />
  <title>{{ title }}</title>
  <link rel="stylesheet" href="../assets/style.css">
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <style>
    /* Remove modo folha quando em app */
    body.doc-app .screen-canvas,
    body.doc-app .document-wrapper,
    body.doc-app .page,
    body.doc-app .page-container {
      width: 100% !important;
      max-width: none !important;
      margin: 0 !important;
      padding: 0 !important;
      background: transparent !important;
      box-shadow: none !important;
      border: none !important;
    }
    html, body {
      margin: 0;
      height: 100%;
      font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
      background: #0b1120;
      color: #e5e7eb;
    }
    .doc-app__header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 10px 18px;
      background: #020617;
      color: #e5e7eb;
      border-bottom: 1px solid #1f2937;
      min-height: 48px;
    }
    .doc-app__title h1 {
      margin: 0;
      font-size: 1.5rem;
      font-weight: 600;
      color: #e5e7eb;
    }
    .doc-app__title span {
      font-size: 0.95rem;
      color: #9ca3af;
      margin-left: 12px;
    }
    .doc-app__top-nav a {
      margin-left: 12px;
      font-size: 13px;
      color: #e5e7eb;
      text-decoration: none;
    }
    .doc-app__top-nav a:hover {
      text-decoration: underline;
    }
    .doc-app__layout {
      display: grid;
      grid-template-columns: 240px minmax(0, 1fr);
      height: calc(100vh - 48px);
    }
    .doc-app__sidebar {
      background: #020617;
      border-right: 1px solid #1f2937;
      padding: 10px;
      color: #9ca3af;
      overflow-y: auto;
    }
    .doc-app__sidebar a {
      display: block;
      font-size: 13px;
      color: #e5e7eb;
      text-decoration: none;
      padding: 4px 6px;
      border-radius: 4px;
    }
    .doc-app__sidebar a:hover {
      background: #111827;
    }
    .doc-app__content {
      padding: 16px 20px;
      overflow-y: auto;
      background: #0b1120;
      min-height: 100%;
    }
    .doc-section {
      margin-bottom: 24px;
    }
    .doc-section h2 {
      margin-top: 0;
      color: #e5e7eb;
    }
    .group-block,
    .object-card,
    .metadata-page,
    .toc-page,
    .objective-page,
    .roadmap-page {
      background: #020617;
      border-radius: 8px;
      border: 1px solid #1f2937;
      color: #e5e7eb;
    }
    /* Scrollbar custom */
    ::-webkit-scrollbar {
      width: 8px;
      background: #111827;
    }
    ::-webkit-scrollbar-thumb {
      background: #1f2937;
      border-radius: 4px;
    }
  </style>
</head>
<body class="doc-app">
  <header class="doc-app__header">
    <div class="doc-app__title">
      <h1>{{ title }}</h1>
      <span>{{ project_code }}</span>
    </div>
    <nav class="doc-app__top-nav">
      <a href="#sec-overview">Visão geral</a>
      <a href="#sec-objective">Objetivo</a>
      <a href="#sec-metadata">Metadados</a>
      <a href="#sec-groups">Grupos</a>
      <a href="#sec-roadmap">Roadmap</a>
    </nav>
  </header>
  <div class="doc-app__layout">
    <aside class="doc-app__sidebar">
      <div class="sidebar-section">
        <h3>Seções</h3>
        <a href="#sec-overview">Visão geral</a>
        <a href="#sec-objective">Objetivo</a>
        <a href="#sec-metadata">Metadados</a>
        <a href="#sec-groups">Grupos e objetos</a>
        <a href="#sec-roadmap">Roadmap</a>
      </div>
      <div class="sidebar-section">
        <h3>Grupos</h3>
        <!-- Links de grupos devem ser gerados dinamicamente -->
        {% for group in groups %}
          <a href="#{{ group._sidebar_id }}">{{ group.name }}</a>
        {% endfor %}
      </div>
    </aside>
    <main class="doc-app__content">
      {% if overview %}
        <section id="sec-overview" class="doc-section capa-page">
          {{ overview | safe }}
        </section>
      {% endif %}
      {% if metadata %}
        <section id="sec-metadata" class="doc-section metadata-page">
          {{ metadata | safe }}
        </section>
      {% endif %}
      {% if objective %}
        <section id="sec-objective" class="doc-section objective-page">
          {{ objective | safe }}
        </section>
      {% endif %}
      {% if groups_content %}
        <section id="sec-groups" class="doc-section toc-page">
          {{ groups_content | safe }}
        </section>
      {% endif %}
      {% if roadmap %}
        <section id="sec-roadmap" class="doc-section roadmap-page">
          {{ roadmap | safe }}
        </section>
      {% endif %}
    </main>
  </div>
  <script>
    // Navegação suave para âncoras internas
    document.querySelectorAll('a[href^="#"]').forEach(link => {
      link.addEventListener('click', e => {
        const id = link.getAttribute('href').slice(1);
        const target = document.getElementById(id);
        if (target) {
          e.preventDefault();
          target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      });
    });
  </script>
</body>
</html>
      <a href="#sec-metadata">Metadados</a>
      <a href="#sec-groups">Grupos</a>
      <a href="#sec-roadmap">Roadmap</a>
    </nav>
  </header>
  <div class="doc-app__layout">
    <aside class="doc-app__sidebar">
      <div class="sidebar-section">
        <h3>Seções</h3>
        <a href="#sec-overview">Visão geral</a>
        <a href="#sec-objective">Objetivo</a>
        <a href="#sec-metadata">Metadados</a>
        <a href="#sec-groups">Grupos e objetos</a>
        <a href="#sec-roadmap">Roadmap</a>
      </div>
      <div class="sidebar-section">
        <h3>Grupos</h3>
        {% for group in groups %}
          <a href="#group-{{ group.domain|e }}">{{ group.label }}</a>
        {% endfor %}
      </div>
    </aside>
    <main class="doc-app__content">
      {# Envolva o conteúdo principal em seções com ids fixos para navegação #}
      <section id="sec-overview" class="doc-section capa-page">
        {{ overview | default('', true) | safe }}
      </section>
      <section id="sec-metadata" class="doc-section metadata-page">
        {{ metadata | default('', true) | safe }}
      </section>
      <section id="sec-objective" class="doc-section objective-page">
        {{ objective | default('', true) | safe }}
      </section>
      <section id="sec-groups" class="doc-section groups-overview">
        {{ groups_content | default('', true) | safe }}
      </section>
      <section id="sec-roadmap" class="doc-section roadmap-page">
        {{ roadmap | default('', true) | safe }}
      </section>
    </main>
  </div>
  <script>
    document.querySelectorAll('a[href^="#"]').forEach(link => {
      link.addEventListener('click', e => {
        const id = link.getAttribute('href').slice(1);
        const target = document.getElementById(id);
        if (target) {
          e.preventDefault();
          target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      });
    });
  </script>
</body>
</html>
