<!DOCTYPE html>
<html lang="pt-br">
<head>
    <!-- ========================================
         OmniDeck - Documentação OTM Bauducco
         Template para geração PDF via wkhtmltopdf
         ======================================== -->
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="author" content="{{ data.project.consultant }}" />
    <meta name="description" content="Documentação técnica do projeto {{ data.project.name }}" />
    <meta name="generator" content="OmniDeck PDF Generator" />
    <title>{{ data.project.name }} - {{ data.project.code }}</title>

    <!-- CSS principal OmniDeck -->
    <link rel="stylesheet" href="../assets/style.css">
    <!-- Highlight.js (código) -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/default.min.css">
</head>
<body class="screen-canvas">
<div class="document-wrapper">
    <div class="document-page">
        <main class="document-content">

                        <!-- ========================================
                                 PÁGINA 1 - CAPA (apenas versão estruturada)
                                 ======================================== -->
<section class="page">
    <div class="page-container capa-page">
        <div class="capa">
            <div class="capa__label">
                DOCUMENTO DE MIGRAÇÃO OTM
            </div>

            <h1 class="capa__title">
                {{ data.project.name }}
            </h1>

            <div class="capa__meta">
                <div class="capa__version">
                    Versão: {{ data.project.version }}
                </div>
                <div class="capa__code">
                    Código: {{ data.project.code }}
                </div>
                {% if data.project.date %}
                <div class="capa__version">
                    Data: {{ data.project.date }}
                </div>
                {% endif %}
                {% if data.project.consultant %}
                <div class="capa__code">
                    Consultor: {{ data.project.consultant }}
                </div>
                {% endif %}
            </div>
        </div>
    </div>
</section>


                        <!-- ========================================
                                 PÁGINA 2 - METADADOS DO PROJETO (apenas versão estruturada)
                                 ======================================== -->
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
                                                <td class="meta-table__value">{{ data.project.name }}</td>
                                            </tr>
                                            <tr class="meta-table__row">
                                                <td class="meta-table__label">Código</td>
                                                <td class="meta-table__value meta-table__value--code">{{ data.project.code }}</td>
                                            </tr>
                                            <tr class="meta-table__row">
                                                <td class="meta-table__label">Versão</td>
                                                <td class="meta-table__value">{{ data.project.version }}</td>
                                            </tr>
                                            {% if data.project.date %}
                                            <tr class="meta-table__row">
                                                <td class="meta-table__label">Data</td>
                                                <td class="meta-table__value">{{ data.project.date }}</td>
                                            </tr>
                                            {% endif %}
                                            <tr class="meta-table__row">
                                                <td class="meta-table__label">Consultor Responsável</td>
                                                <td class="meta-table__value">{{ data.project.consultant }}</td>
                                            </tr>
                                            {% if data.project.environment %}
                                                {% if data.project.environment.source %}
                                                <tr class="meta-table__row">
                                                    <td class="meta-table__label">Ambiente Origem</td>
                                                    <td class="meta-table__value meta-table__value--url">{{ data.project.environment.source }}</td>
                                                </tr>
                                                {% endif %}
                                                {% if data.project.environment.target %}
                                                <tr class="meta-table__row">
                                                    <td class="meta-table__label">Ambiente Destino</td>
                                                    <td class="meta-table__value meta-table__value--url">{{ data.project.environment.target }}</td>
                                                </tr>
                                                {% endif %}
                                            {% endif %}
                                            {% if data.project_metadata and data.project_metadata.summary %}
                                            <tr class="meta-table__row">
                                                <td class="meta-table__label">Resumo</td>
                                                <td class="meta-table__value">{{ data.project_metadata.summary }}</td>
                                            </tr>
                                            {% endif %}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </section>

                <!-- ========================================
                     PÁGINA 2 - METADADOS DO PROJETO
                     Usa: .page .page-container .metadata-page .meta-table
                     ======================================== -->
                <section class="page">
                    <div class="page-container">
                        <section class="metadata-page">
                            <header class="metadata-page__header">
                                <h2 class="metadata-page__title">
                                    Informações do Projeto
                                </h2>
                            </header>

                            <div class="metadata-page__content">
                                <table class="meta-table">
                                    <tbody>
                                        <tr class="meta-table__row">
                                            <td class="meta-table__label">Nome do Projeto</td>
                                            <td class="meta-table__value">{{ data.project.name }}</td>
                                        </tr>
                                        <tr class="meta-table__row">
                                            <td class="meta-table__label">Código</td>
                                            <td class="meta-table__value meta-table__value--code">{{ data.project.code }}</td>
                                        </tr>
                                        <tr class="meta-table__row">
                                            <td class="meta-table__label">Versão</td>
                                            <td class="meta-table__value">{{ data.project.version }}</td>
                                        </tr>
                                        {% if data.project.date %}
                                        <tr class="meta-table__row">
                                            <td class="meta-table__label">Data</td>
                                            <td class="meta-table__value">{{ data.project.date }}</td>
                                        </tr>
                                        {% endif %}
                                        <tr class="meta-table__row">
                                            <td class="meta-table__label">Consultor Responsável</td>
                                            <td class="meta-table__value">{{ data.project.consultant }}</td>
                                        </tr>
                                        {% if data.project.environment %}
                                            {% if data.project.environment.source %}
                                            <tr class="meta-table__row">
                                                <td class="meta-table__label">Ambiente Origem</td>
                                                <td class="meta-table__value meta-table__value--url">
                                                    {{ data.project.environment.source }}
                                                </td>
                                            </tr>
                                            {% endif %}
                                            {% if data.project.environment.target %}
                                            <tr class="meta-table__row">
                                                <td class="meta-table__label">Ambiente Destino</td>
                                                <td class="meta-table__value meta-table__value--url">
                                                    {{ data.project.environment.target }}
                                                </td>
                                            </tr>
                                            {% endif %}
                                        {% endif %}

                                        {% if data.project_metadata and data.project_metadata.summary %}
                                        <tr class="meta-table__row">
                                            <td class="meta-table__label">Resumo</td>
                                            <td class="meta-table__value">
                                                {{ data.project_metadata.summary }}
                                            </td>
                                        </tr>
                                        {% endif %}
                                    </tbody>
                                </table>
                            </div>
                        </section>
                    </div>
                </section>

                        <!-- ========================================
                                 PÁGINA 3 - SUMÁRIO (apenas versão estruturada)
                                 ======================================== -->
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
                                            {% if data.groups %}
                                                {% for group in data.groups %}
                                                <li>
                                                    <a class="toc-link" href="#group-{{ loop.index }}">{{ group.label }}</a>
                                                    {% if group.objects %}
                                                    <ul>
                                                        {% for object in group.objects %}
                                                        <li>
                                                            <a class="toc-link" href="#object-{{ group.label | replace(' ', '-') }}-{{ loop.index }}">{{ object.name }}</a>
                                                        </li>
                                                        {% endfor %}
                                                    </ul>
                                                    {% endif %}
                                                </li>
                                                {% endfor %}
                                            {% endif %}
                                        </ul>
                                    </div>
                                </div>
                            </div>
                        </section>

                <!-- ========================================
                     PÁGINA 3 - SUMÁRIO
                     Usa: .page .page-container .toc-page
                     ======================================== -->
                <section class="page">
                    <div class="page-container">
                        <section class="toc-page">
                            <header class="toc-page__header">
                                <h2 class="toc-page__title">Sumário</h2>
                            </header>

                            <div class="toc-page__content">
                                <ul>
                                    <!-- Link fixo para seções principais -->
                                    <li><a class="toc-link" href="#objetivo">Objetivo do Projeto</a></li>
                                    <li><a class="toc-link" href="#roadmap">Roadmap de Migração</a></li>
                                    <li><a class="toc-link" href="#grupos-objetos">Grupos e Objetos de Migração</a></li>

                                    <!-- Grupos dinâmicos -->
                                    {% if data.groups %}
                                        {% for group in data.groups %}
                                            <li>
                                                <a class="toc-link" href="#group-{{ loop.index }}">
                                                    {{ group.label }}
                                                </a>
                                                {% if group.objects %}
                                                    <ul>
                                                        {% for object in group.objects %}
                                                            <li>
                                                                <a class="toc-link" href="#object-{{ group.label | replace(' ', '-') }}-{{ loop.index }}">
                                                                    {{ object.name }}
                                                                </a>
                                                            </li>
                                                        {% endfor %}
                                                    </ul>
                                                {% endif %}
                                            </li>
                                        {% endfor %}
                                    {% endif %}
                                </ul>
                            </div>
                        </section>
                    </div>
                </section>

            <!-- ========================================
                 PÁGINA 4 - OBJETIVO DO PROJETO + HISTÓRICO
                 Usa: .page .page-container .objective-page .change-history-page
                 ======================================== -->

                <!-- ========================================
                     PÁGINA 4 - OBJETIVO DO PROJETO + HISTÓRICO
                     Usa: .page .page-container .objective-page .change-history-page
                     ======================================== -->
                {% if data.project_metadata.migration_objective %}
                {# PÁGINA: Objetivo do Projeto #}
                <section class="page">
                    <div class="page-container">
                        <section class="objective-page" id="objetivo">
                            <header class="objective-page__header">
                                <h2 class="objective-page__title">
                                    {{ data.project_metadata.migration_objective.title or 'Objetivo do Projeto' }}
                                </h2>
                            </header>
                            <div class="objective-page__content">
                                {% for block in data.project_metadata.migration_objective.blocks %}
                                    {% if block.type == "paragraph" %}
                                        <p>{{ block.text }}</p>
                                    {% elif block.type == "list" %}
                                        <ul>
                                            {% for item in block["items"] %}
                                                <li>{{ item }}</li>
                                            {% endfor %}
                                        </ul>
                                    {% endif %}
                                {% endfor %}
                            </div>
                        </section>
                    </div>
                </section>
                {% endif %}

            {% set history = data.project_metadata.change_history if data.project_metadata else [] %}
            {% if history and history|length > 0 %}
            {# PÁGINA: Histórico de Alterações #}
            <section class="page">
                <div class="page-container">
                    <section class="change-history-page">
                        <header class="change-history-page__header">
                            <h2 class="change-history-page__title">Histórico de Alterações</h2>
                        </header>
                        <div class="change-history-page__content">
                            <table role="table" aria-label="Histórico de versões do projeto">
                                <thead>
                                    <tr>
                                        <th scope="col">Data</th>
                                        <th scope="col">Versão</th>
                                        <th scope="col">Descrição</th>
                                        <th scope="col">Autor</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for item in history %}
                                    <tr>
                                        <td>{{ item.date | format_date_br }}</td>
                                        <td>{{ item.version }}</td>
                                        <td>{{ item.description }}</td>
                                        <td>{{ item.author }}</td>
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                    </section>
                </div>
            </section>
            {% endif %}

            <!-- ========================================
                 PÁGINA 5 - ROADMAP DE MIGRAÇÃO
                 Usa: .page .page-container .roadmap-page .deployment-type-block
                 ======================================== -->
            <section class="page" id="roadmap">
                <div class="page-container">
                    <section class="roadmap-page">
                        <header class="roadmap-page__header">
                            <h2 class="roadmap-page__title">Roadmap de Migração</h2>
                            <p class="roadmap-page__description">
                                Plano de execução agrupado por deployment type, contemplando todos os objetos dentro do escopo de migração do OTM.
                            </p>
                        </header>

                <!-- ========================================
                     PÁGINA 5 - HISTÓRICO DE ALTERAÇÕES
                     Usa: .page .page-container .change-history-page
                     ======================================== -->
                {% set history = data.project_metadata.change_history if data.project_metadata else [] %}
                {% if history and history|length > 0 %}
                <section class="page">
                    <div class="page-container">
                        <section class="change-history-page">
                            <header class="change-history-page__header">
                                <h2 class="change-history-page__title">Histórico de Alterações</h2>
                            </header>
                            <div class="change-history-page__content">
                                <table role="table" aria-label="Histórico de versões do projeto">
                                    <thead>
                                        <tr>
                                            <th scope="col">Data</th>
                                            <th scope="col">Versão</th>
                                            <th scope="col">Descrição</th>
                                            <th scope="col">Autor</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {% for item in history %}
                                        <tr>
                                            <td>{{ item.date | format_date_br }}</td>
                                            <td>{{ item.version }}</td>
                                            <td>{{ item.description }}</td>
                                            <td>{{ item.author }}</td>
                                        </tr>
                                        {% endfor %}
                                    </tbody>
                                </table>
                            </div>
                        </section>
                    </div>
                </section>
                {% endif %}

                        <!-- Exemplo simples: agrupar grupos/objetos por deployment_type -->
                        {% if data.groups %}
                            {% set deployments = {} %}
                            {% for group in data.groups %}
                                {% for object in group.objects %}
                                    {% set dt = object.deployment_type or 'UNDEFINED' %}
                                    {% if deployments.get(dt) is none %}
                                        {% set _ = deployments.update({dt: []}) %}
                                    {% endif %}
                                    {% set _ = deployments[dt].append({'group': group, 'object': object}) %}
                                {% endfor %}
                            {% endfor %}

                            {% for dt, items in deployments.items() %}
                                <article class="deployment-type-block deployment-type--{{ dt | lower }}">
                                    <header class="deployment-type-block__header">
                                        <h3 class="deployment-type-block__title">
                                            {{ dt }}
                                        </h3>
                                        <div class="deployment-type-block__count">
                                            {{ items | length }} objetos
                                        </div>
                                    </header>
                                    <p class="deployment-type-block__description">
                                        Objetos deste deployment type no escopo de migração.
                                    </p>

                                    <table class="meta-table meta-table--roadmap">
                                        <thead>
                                            <tr>
                                                <th>#</th>
                                                <th>Grupo</th>
                                                <th>Objeto</th>
                                                <th>Responsável</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {% for item in items %}
                                            <tr>
                                                <td>{{ item.object.sequence }}</td>
                                                <td>{{ item.group.label }}</td>
                                                <td>{{ item.object.name }}</td>
                                                <td>{{ item.object.owner or 'ITC' }}</td>
                                            </tr>
                                            {% endfor %}
                                        </tbody>
                                    </table>
                                </article>
                            {% endfor %}
                        {% endif %}
                    </section>
                </div>
            </section>

            <!-- ========================================
                 SEÇÃO - GRUPOS E OBJETOS (CARDS)
                 Usa: .page .page-container .group-block .object-card
                 ======================================== -->
            <section class="page" id="grupos-objetos">
                <div class="page-container">
                    {% if data.groups %}
                        <section class="groups-overview">
                            <h2 class="groups-overview__title">Grupos e Objetos de Migração OTM</h2>
                            <div class="groups-overview__content">
                                {% for group in data.groups %}
                                <div class="group-item">
                                    <div class="group-item__name">{{ group.label }}</div>
                                    <div class="group-item__count">
                                        {{ group.objects | length }} objetos
                                    </div>
                                </div>
                                {% endfor %}
                            </div>
                        </section>

                        {% for group in data.groups %}
                        <section class="group-block" id="group-{{ loop.index }}">
                            <header class="group-block__header">
                                <h2>{{ group.label }}</h2>
                            </header>
                            <div class="group-block__content">
                                {% if group.description_paragraphs %}
                                    {% for paragraph in group.description_paragraphs %}
                                        <p>{{ paragraph }}</p>
                                    {% endfor %}
                                {% endif %}

                                {% for object in group.objects %}
                                <article class="object-card" id="object-{{ group.label | replace(' ', '-') }}-{{ loop.index }}">
                                    <header class="object-card__header">
                                        <div class="object-card__title-group">
                                            <h3 class="object-card__title">{{ object.name }}</h3>
                                            {% if object.object_type %}
                                            <span class="object-card__badge object-card__badge--type">
                                                {{ object.object_type }}
                                            </span>
                                            {% endif %}
                                        </div>
                                        {% if object.sequence %}
                                        <div class="object-card__sequence">
                                            {{ object.sequence }}
                                        </div>
                                        {% endif %}
                                    </header>

                                    {% if object.description %}
                                    <p class="object-card__description">
                                        {{ object.description }}
                                    </p>
                                    {% endif %}

                                    <div class="object-card__body">
                                        <div class="object-card__metadata-grid">
                                            <div class="object-card__metadata-section">
                                                <h4>Propriedades</h4>
                                                <table class="meta-table">
                                                    <tbody>
                                                        <tr>
                                                            <td class="meta-table__label">Sequência</td>
                                                            <td class="meta-table__value">
                                                                {{ object.sequence }}
                                                            </td>
                                                        </tr>
                                                        <tr>
                                                            <td class="meta-table__label">Object Type</td>
                                                            <td class="meta-table__value">
                                                                {{ object.object_type }}
                                                            </td>
                                                        </tr>
                                                        {% if object.otm_table %}
                                                        <tr>
                                                            <td class="meta-table__label">OTM Table</td>
                                                            <td class="meta-table__value">
                                                                {{ object.otm_table }}
                                                            </td>
                                                        </tr>
                                                        {% endif %}
                                                        {% if object.group_label %}
                                                        <tr>
                                                            <td class="meta-table__label">Grupo</td>
                                                            <td class="meta-table__value">
                                                                {{ object.group_label }}
                                                            </td>
                                                        </tr>
                                                        {% endif %}
                                                        {% if object.deployment_type %}
                                                        <tr>
                                                            <td class="meta-table__label">Deployment Type</td>
                                                            <td class="meta-table__value">
                                                                {{ object.deployment_type }}
                                                            </td>
                                                        </tr>
                                                        {% endif %}
                                                        {% if object.migration_project_id %}
                                                        <tr>
                                                            <td class="meta-table__label">Migration Project ID</td>
                                                            <td class="meta-table__value">
                                                                {{ object.migration_project_id }}
                                                            </td>
                                                        </tr>
                                                        {% endif %}
                                                        {% if object.saved_query_id %}
                                                        <tr>
                                                            <td class="meta-table__label">Saved Query ID</td>
                                                            <td class="meta-table__value">
                                                                {{ object.saved_query_id }}
                                                            </td>
                                                        </tr>
                                                        {% endif %}
                                                    </tbody>
                                                </table>
                                            </div>

                                            <div class="object-card__metadata-section">
                                                <h4>Status de Execução</h4>
                                                <table class="meta-table status-table">
                                                    <tbody>
                                                        <tr>
                                                            <td class="status-table__label">Status</td>
                                                            <td class="status-table__value">
                                                                <span class="status-badge status-badge--{{ object.status | lower | replace(' ', '_') }}">
                                                                    {{ object.status }}
                                                                </span>
                                                            </td>
                                                        </tr>
                                                        <tr>
                                                            <td class="status-table__label">Documentação</td>
                                                            <td class="status-table__value">
                                                                <span class="status-badge status-badge--{{ object.documentation_status | lower | replace(' ', '_') }}">
                                                                    {{ object.documentation_status }}
                                                                </span>
                                                            </td>
                                                        </tr>
                                                    </tbody>
                                                </table>
                                            </div>
                                        </div>

                                        {% if object.notes %}
                                        <section class="object-card__notes">
                                            <h4 class="object-card__notes-title">Notas</h4>
                                            <p class="object-card__notes-content">{{ object.notes }}</p>
                                        </section>
                                        {% endif %}

                                        {% if object.object_extraction_query and object.object_extraction_query.content %}
                                        <section class="code-section mt-3">
                                            <h4>Query de Extração de Objetos</h4>
                                            {% if object.object_extraction_query.language %}
                                            <p class="small-text">
                                                Linguagem: {{ object.object_extraction_query.language | upper }}
                                            </p>
                                            {% endif %}
                                            <pre><code class="language-{{ object.object_extraction_query.language | lower }}">
{{ object.object_extraction_query.content }}
                                            </code></pre>
                                        </section>
                                        {% endif %}

                                        {% if object.technical_content and object.technical_content.content %}
                                        <section class="code-section mt-3">
                                            <h4>Conteúdo Técnico</h4>
                                            {% if object.technical_content.type %}
                                            <p class="small-text">
                                                Tipo: {{ object.technical_content.type | upper }}
                                            </p>
                                            {% endif %}
                                            <pre><code class="language-{{ object.technical_content.type | lower }}">
{{ object.technical_content.content }}
                                            </code></pre>
                                        </section>
                                        {% endif %}
                                    </div>
                                </article>
                                {% endfor %}
                            </div>
                        </section>
                        {% endfor %}
                    {% endif %}

                    <!-- Rodapé do documento -->
                    <footer class="document-footer" role="contentinfo">
                        <p class="document-footer__text">
                            {{ data.project.name }} • {{ data.project.code }} • v{{ data.project.version }}
                        </p>
                    </footer>
                </div>
            </section>

        </main>
    </div>
</div>

<!-- Highlight.js -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
<script>
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('pre code').forEach((block) => {
    try {
      hljs.highlightElement(block);
    } catch (e) {}
  });
});
</script>
</body>
</html>
