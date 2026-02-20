
<!DOCTYPE html>
<html lang="pt-br">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="author" content="{{ project.consultant }}" />
  <meta name="description" content="Documentação técnica do projeto {{ project.name }}" />
  <meta name="generator" content="OmniDeck PDF Generator" />
  <title>{{ project.name }} - {{ project.code }}</title>
  <link rel="stylesheet" href="pdf.css">
</head>
<body class="screen-canvas">
<div class="document-wrapper">
  <div class="document-page">
    <main class="document-content">

      <!-- CAPA -->
      <section class="page">
        <div class="page-container capa-page">
          <div class="capa">
            <div class="capa__label">PROJETO DE MIGRAÇÃO OTM</div>
            <h1 class="capa__title">{{ project.name }}</h1>
            <div class="capa__meta">
              <div class="capa__version">Versão: {{ project.version }}</div>
              <div class="capa__code">Código: {{ project.code }}</div>
              {% if project.date %}<div class="capa__version">Data: {{ project.date }}</div>{% endif %}
              {% if project.consultant %}<div class="capa__code">Consultor: {{ project.consultant }}</div>{% endif %}
            </div>
          </div>
        </div>
      </section>

      <!-- METADADOS DO PROJETO -->
      <section class="page">
        <div class="page-container">
          <div class="metadata-page">
            <header class="metadata-page__header">
              <h2 class="metadata-page__title">Informações do Projeto</h2>
            </header>
            <table class="meta-table">
              <tbody>
                <tr class="meta-table__row">
                  <td class="meta-table__label">Nome do Projeto</td>
                  <td class="meta-table__value">{{ project.name }}</td>
                </tr>
                <tr class="meta-table__row">
                  <td class="meta-table__label">Código</td>
                  <td class="meta-table__value meta-table__value--code">{{ project.code }}</td>
                </tr>
                <tr class="meta-table__row">
                  <td class="meta-table__label">Versão</td>
                  <td class="meta-table__value">{{ project.version }}</td>
                </tr>
                {% if project.date %}
                <tr class="meta-table__row">
                  <td class="meta-table__label">Data</td>
                  <td class="meta-table__value">{{ project.date }}</td>
                </tr>
                {% endif %}
                <tr class="meta-table__row">
                  <td class="meta-table__label">Consultor Responsável</td>
                  <td class="meta-table__value">{{ project.consultant }}</td>
                </tr>
                {% if project.environment %}
                  {% if project.environment.source %}
                  <tr class="meta-table__row">
                    <td class="meta-table__label">Ambiente Origem</td>
                    <td class="meta-table__value meta-table__value--url">{{ project.environment.source }}</td>
                  </tr>
                  {% endif %}
                  {% if project.environment.target %}
                  <tr class="meta-table__row">
                    <td class="meta-table__label">Ambiente Destino</td>
                    <td class="meta-table__value meta-table__value--url">{{ project.environment.target }}</td>
                  </tr>
                  {% endif %}
                {% endif %}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <!-- SUMÁRIO -->
      <section class="page">
        <div class="page-container">
          <div class="toc-page">
            <header class="toc-page__header">
              <h2 class="toc-page__title">Sumário</h2>
            </header>
            <div class="toc-page__content">
              <ul>
                <li><a class="toc-link" href="#objetivo">Objetivo do Projeto</a></li>
                <li><a class="toc-link" href="#roadmap">Roadmap de Migração</a></li>
                <li><a class="toc-link" href="#grupos-objetos">Grupos e Objetos de Migração</a></li>
                {% if groups %}
                  {% for g in groups %}
                  <li><a class="toc-link" href="#group-{{ loop.index }}">{{ g.label }}</a></li>
                  {% endfor %}
                {% endif %}
              </ul>
            </div>
          </div>
        </div>
      </section>


      <!-- OBJETIVO DO PROJETO -->
      <section class="page" id="objetivo">
        <div class="page-container">
          <div class="objective-page">
            <h2>Objetivo do Projeto</h2>
            {% if migration_objective %}
              {% for p in migration_objective %}
                <p>{{ p }}</p>
              {% endfor %}
            {% else %}
              <p>Não informado.</p>
            {% endif %}
          </div>
        </div>
      </section>

      <!-- HISTÓRICO DE ALTERAÇÕES -->
      {% set history = project.project_metadata.change_history if project.project_metadata and project.project_metadata.change_history else [] %}
      {% if history and history|length > 0 %}
      <section class="page" id="historico-alteracoes">
        <div class="page-container">
          <div class="change-history-page">
            <h2>Histórico de Alterações</h2>
            <table class="meta-table">
              <thead>
                <tr>
                  <th>Data</th>
                  <th>Versão</th>
                  <th>Descrição</th>
                  <th>Autor</th>
                </tr>
              </thead>
              <tbody>
                {% for item in history %}
                <tr>
                  <td>{{ item.date }}</td>
                  <td>{{ item.version }}</td>
                  <td>{{ item.description }}</td>
                  <td>{{ item.author }}</td>
                </tr>
                {% endfor %}
              </tbody>
            </table>
          </div>
        </div>
      </section>
      {% endif %}

      <!-- ROADMAP DE MIGRAÇÃO -->
      {% if roadmap %}
      <section class="page" id="roadmap">
        <div class="page-container">
          <div class="roadmap-page">
            <h2>Roadmap de Migração</h2>
            <ul class="roadmap-list">
              {% for step in roadmap %}
                <li class="roadmap-list__item"><strong>{{ step.title }}</strong> – {{ step.description }}</li>
              {% endfor %}
            </ul>
          </div>
        </div>
      </section>
      {% endif %}

      <!-- GRUPOS E OBJETOS -->
      {% if groups %}
      <section class="page" id="grupos-objetos">
        <div class="page-container">
          <div class="groups-overview">
            <h2>Visão Geral de Grupos</h2>
            <ul class="groups-list">
              {% for g in groups %}
                <li class="groups-list__item"><strong>{{ g.label }}</strong>{% if g.description %}<span> – {{ g.description }}</span>{% endif %}</li>
              {% endfor %}
            </ul>
          </div>
          {% for g in groups %}
          <section class="group-block" id="group-{{ loop.index }}">
            <h2>{{ g.label }}</h2>
            {% if g.description %}<p>{{ g.description }}</p>{% endif %}
            {% for o in g.objects %}
            <article class="object-card">
              <div class="object-card__bar"></div>
              <div class="object-card__content">
                <h3 class="object-card__title">{{ o.sequence }}. {{ o.name }}</h3>
                {% if o.description %}<p class="object-card__desc">{{ o.description }}</p>{% endif %}
                <p class="object-card__meta">
                  Tipo: {{ o.object_type }} |
                  Status (projeto): {{ o.status.migration_project }} |
                  Status (documentação): {{ o.status.documentation }}
                </p>
              </div>
            </article>
            {% endfor %}
          </section>
          {% endfor %}
        </div>
      </section>
      {% endif %}

    </main>
  </div>
</div>
</body>
</html>
