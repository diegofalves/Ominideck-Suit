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
    <link rel="stylesheet" href="../assets/style.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/default.min.css">
</head>
<body>
    <div class="pdf-viewer screen-canvas">
        <div class="page">
            <div class="page-content">
                <!-- =============================================
                     SEÇÃO 1: CAPA DO DOCUMENTO
                     - Página completa A4 com background institucional
                     - Centralização vertical e horizontal
                     ============================================= -->
                <div class="page-container document-page capa-page" role="banner">
                    <div class="capa">
                        <div class="capa-conteudo">
                            <div class="capa__branding">
                                <span class="capa__label">Documentação Técnica OTM</span>
                            </div>
                            <h1 class="capa__title">{{ data.project.name }}</h1>
                            <div class="capa__meta">
                                <span class="capa__version">Versão {{ data.project.version }}</span>
                                <span class="capa__code">{{ data.project.code }}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- =============================================
             SEÇÃO 2: METADADOS DO PROJETO
             - Informações gerais e ambientes
             ============================================= -->
        <div class="page">
            <div class="page-content">
                <main class="document-content" role="main">
                    <section class="metadata-page" aria-label="Informações do Projeto">
                        <header class="metadata-page__header">
                            <h2 class="metadata-page__title">Informações do Projeto</h2>
                        </header>
                        
                        <table class="meta-table meta-table--project" role="table" aria-label="Dados do projeto">
                            <thead class="visually-hidden">
                                <tr>
                                    <th scope="col">Propriedade</th>
                                    <th scope="col">Valor</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr class="meta-table__row">
                                    <th scope="row" class="meta-table__label">Código</th>
                                    <td class="meta-table__value">{{ data.project.code }}</td>
                                </tr>
                                <tr class="meta-table__row">
                                    <th scope="row" class="meta-table__label">Versão</th>
                                    <td class="meta-table__value">{{ data.project.version }}</td>
                                </tr>
                                <tr class="meta-table__row">
                                    <th scope="row" class="meta-table__label">Consultor</th>
                                    <td class="meta-table__value">{{ data.project.consultant }}</td>
                                </tr>
                                <tr class="meta-table__row meta-table__row--separator">
                                    <th scope="row" class="meta-table__label">Ambiente Origem</th>
                                    <td class="meta-table__value meta-table__value--url">{{ data.project.environment.source }}</td>
                                </tr>
                                <tr class="meta-table__row">
                                    <th scope="row" class="meta-table__label">Ambiente Destino</th>
                                    <td class="meta-table__value meta-table__value--url">{{ data.project.environment.target }}</td>
                                </tr>
                            </tbody>
                        </table>
                    </section>
                </main>
            </div>
        </div>

        <!-- =============================================
             SEÇÃO 3: SUMÁRIO
             - Índice de todos os grupos e objetos
             ============================================= -->
        <div class="page">
            <div class="page-content">
                <section class="toc-page" aria-label="Sumário">
                    <header class="toc-page__header">
                        <h2 class="toc-page__title">Sumário</h2>
                    </header>
                    <div class="toc-page__content">
                        <ul>
                            <li><a href="#objetivo-migracao" class="toc-link">Objetivo do Projeto de Migração</a></li>
                            <li><a href="#controle-versao" class="toc-link">Controle de Versão e Histórico de Alterações</a></li>
                            <li>Grupos e Objetos de Migração OTM
                                <ul>
                                    {% for group in data.groups %}
                                    {% set group_id = "group-" + group.label.lower().replace(" ", "-").replace("ã", "a").replace("é", "e").replace("ç", "c") %}
                                    <li><a href="#{{ group_id }}" class="toc-link">Grupo: {{ group.label }}</a>
                                        {% if group.objects %}
                                        <ul>
                                            {% for object in group.objects %}
                                            {% set object_id = "object-" + object.name.lower().replace(" ", "-").replace("(", "").replace(")", "").replace("ã", "a").replace("é", "e").replace("ç", "c") %}
                                            <li><a href="#{{ object_id }}" class="toc-link">{{ object.name }}</a></li>
                                            {% endfor %}
                                        </ul>
                                        {% endif %}
                                    </li>
                                    {% endfor %}
                                </ul>
                            </li>
                        </ul>
                    </div>
                </section>
            </div>
        </div>

        <!-- =============================================
             SEÇÃO 4: OBJETIVO DA MIGRAÇÃO
             ============================================= -->
        {% if data.project_metadata.migration_objective.blocks %}
        <div class="page">
            <div class="page-content">
                <section class="objective-page" aria-label="{{ data.project_metadata.migration_objective.title }}" id="objetivo-migracao">
                    <header class="objective-page__header">
                        <h2 class="objective-page__title">{{ data.project_metadata.migration_objective.title }}</h2>
                    </header>
                    <div class="objective-page__content">
                        {% for block in data.project_metadata.migration_objective.blocks %}
                            {% if block.type == "paragraph" %}
                                <p class="objective-page__paragraph">{{ block.text }}</p>
                            {% elif block.type == "list" %}
                                <ul class="objective-page__list">
                                    {% for item in block["items"] %}
                                        <li>{{ item }}</li>
                                    {% endfor %}
                                </ul>
                            {% endif %}
                        {% endfor %}
                    </div>
                </section>
            </div>
        </div>
        {% endif %}

        <!-- =============================================
             SEÇÃO 5: CONTROLE DE VERSÃO E HISTÓRICO
             ============================================= -->
        {% set history = data.project_metadata.change_history %}
        {% if history and history|length > 0 %}
        <div class="page">
            <div class="page-content">
                <section class="version-control-page" aria-label="Controle de Versão" id="controle-versao">
                    <header class="version-control-page__header">
                        <h2 class="version-control-page__title">Controle de Versão</h2>
                    </header>
                    <div class="version-control-page__content">
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
                                    <td data-label="Data">{{ item.date | format_date_br }}</td>
                                    <td data-label="Versão">{{ item.version }}</td>
                                    <td data-label="Descrição">{{ item.description }}</td>
                                    <td data-label="Autor">{{ item.author }}</td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </section>
            </div>
        </div>
        {% endif %}

        <!-- =============================================
             SEÇÃO 6.5: ROADMAP DE MIGRAÇÃO
             - Plano de execução agrupado por deployment type
             - Colunas específicas por tipo de deployment
             ============================================= -->
        <div class="page">
            <div class="page-content">
                <section class="roadmap-page" aria-label="Roadmap de Migração" id="roadmap">
                    <header class="roadmap-page__header">
                        <h2 class="roadmap-page__title">Roadmap de Migração</h2>
                        <p class="roadmap-page__description">
                            Este capítulo apresenta a estratégia de execução da migração, agrupada por tipo de implantação (Deployment Type). 
                            Cada bloco representa um grupo coeso de objetos que devem ser migrados seguindo a mesma tática operacional.
                            As colunas de cada tabela variam conforme o tipo de deployment, refletindo as informações técnicas relevantes para cada estratégia.
                        </p>
                    </header>

                    <!-- MAPA DE OBJETOS AGRUPADOS POR DEPLOYMENT TYPE E GRUPO -->
                    {% set deployment_map = {} %}
                    {% for group in data.groups %}
                        {% for obj in group.objects %}
                            {% set dt = obj.deployment_type or "INDEFINIDO" %}
                            {% if dt not in deployment_map %}
                                {% set _ = deployment_map.update({dt: []}) %}
                            {% endif %}
                            {% set obj_data = {
                                "name": obj.name,
                                "description": obj.description,
                                "object_type": obj.object_type,
                                "responsible": obj.responsible,
                                "sequence": obj.sequence,
                                "group_label": group.label,
                                "deployment_type": obj.deployment_type,
                                "saved_query_id": obj.get("saved_query_id", None),
                                "migration_project_id": "%s-%03d" % (obj.object_type[:3].upper(), obj.sequence)
                            } %}
                            {% set _ = deployment_map[dt].append(obj_data) %}
                        {% endfor %}
                    {% endfor %}

                    <!-- ITERAÇÃO SOBRE DEPLOYMENT TYPES NA ORDEM CORRETA -->
                    {% set dt_order = ["MANUAL", "MIGRATION_PROJECT", "CSV", "DB.XML", "ARQUIVO ZIP BI", "INTEGRATION"] %}
                    {% for dt_key in dt_order %}
                        {% if dt_key in deployment_map %}
                            {% set dt_objects = deployment_map[dt_key] %}
                            {% set css_class = dt_key.lower().replace(".", "").replace(" ", "").replace("_", "") %}
                            
                            <div class="deployment-type-block deployment-type--{{ css_class }}" aria-label="Deployment Type: {{ dt_key }}">
                                <div class="deployment-type-block__header">
                                    <h3 class="deployment-type-block__title">{{ dt_key }}</h3>
                                    <span class="deployment-type-block__count">{{ dt_objects | length }} {{ "objeto" if dt_objects | length == 1 else "objetos" }}</span>
                                </div>
                                
                                <p class="deployment-type-block__description">
                                    {% if dt_key == "MANUAL" %}
                                        Implantação manual no ambiente de destino. Objetos que requerem ação humana direta e validação específica.
                                    {% elif dt_key == "MIGRATION_PROJECT" %}
                                        Migração via projeto de migração nativo do OTM. Objetos transportados com configurações relacionadas.
                                    {% elif dt_key == "CSV" %}
                                        Importação via arquivos CSV. Dados estruturados em formato de valores separados por vírgula.
                                    {% elif dt_key == "DB.XML" %}
                                        Migração via banco de dados e arquivos XML. Transportação com integridade de relacionamentos.
                                    {% elif dt_key == "ARQUIVO ZIP BI" %}
                                        Exportação para arquivo ZIP com conteúdo BI. Inclui dashboards, relatórios e visualizações.
                                    {% elif dt_key == "INTEGRATION" %}
                                        Integração e configuração de interfaces externas. Objetos de conectividade e troca de dados com sistemas terceiros.
                                    {% endif %}
                                </p>

                                <!-- TABELAS COM COLUNAS ESPECÍFICAS POR DEPLOYMENT TYPE -->
                                {% if dt_key == "MANUAL" %}
                                    <!-- MANUAL: Resp., Grupo, Descrição, Tabela OTM -->
                                    <table class="meta-table meta-table--roadmap" role="table" aria-label="Objetos MANUAL">
                                        <thead>
                                            <tr>
                                                <th scope="col" class="meta-table__header">Resp.</th>
                                                <th scope="col" class="meta-table__header">Grupo</th>
                                                <th scope="col" class="meta-table__header">Descrição</th>
                                                <th scope="col" class="meta-table__header">Tabela OTM</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {% for obj in dt_objects | sort(attribute="sequence") %}
                                                <tr class="meta-table__row">
                                                    <td class="meta-table__value">{{ obj.responsible }}</td>
                                                    <td class="meta-table__value">{{ obj.group_label }}</td>
                                                    <td class="meta-table__value">{{ obj.description }}</td>
                                                    <td class="meta-table__value">{{ obj.object_type }}</td>
                                                </tr>
                                            {% endfor %}
                                        </tbody>
                                    </table>

                                {% elif dt_key == "MIGRATION_PROJECT" %}
                                    <!-- MIGRATION_PROJECT: Resp., Seq., ID Migration Project, Grupo, Descrição, Tabela OTM, Saved Query ID -->
                                    <table class="meta-table meta-table--roadmap" role="table" aria-label="Objetos MIGRATION_PROJECT">
                                        <thead>
                                            <tr>
                                                <th scope="col" class="meta-table__header">Resp.</th>
                                                <th scope="col" class="meta-table__header">Seq.</th>
                                                <th scope="col" class="meta-table__header">ID Migration Project</th>
                                                <th scope="col" class="meta-table__header">Grupo</th>
                                                <th scope="col" class="meta-table__header">Descrição</th>
                                                <th scope="col" class="meta-table__header">Tabela OTM</th>
                                                <th scope="col" class="meta-table__header">Saved Query ID</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {% for obj in dt_objects | sort(attribute="sequence") %}
                                                <tr class="meta-table__row">
                                                    <td class="meta-table__value">{{ obj.responsible }}</td>
                                                    <td class="meta-table__value">{{ obj.sequence }}</td>
                                                    <td class="meta-table__value">{{ obj.migration_project_id }}</td>
                                                    <td class="meta-table__value">{{ obj.group_label }}</td>
                                                    <td class="meta-table__value">{{ obj.description }}</td>
                                                    <td class="meta-table__value">{{ obj.object_type }}</td>
                                                    <td class="meta-table__value">{% if obj.saved_query_id %}{{ obj.saved_query_id }}{% else %}—{% endif %}</td>
                                                </tr>
                                            {% endfor %}
                                        </tbody>
                                    </table>

                                {% elif dt_key in ["CSV", "DB.XML", "ARQUIVO ZIP BI", "INTEGRATION"] %}
                                    <!-- CSV / DB.XML / ARQUIVO ZIP BI / INTEGRATION: Resp., Seq., Grupo, Descrição, Tabela OTM -->
                                    <table class="meta-table meta-table--roadmap" role="table" aria-label="Objetos {{ dt_key }}">
                                        <thead>
                                            <tr>
                                                <th scope="col" class="meta-table__header">Resp.</th>
                                                <th scope="col" class="meta-table__header">Seq.</th>
                                                <th scope="col" class="meta-table__header">Grupo</th>
                                                <th scope="col" class="meta-table__header">Descrição</th>
                                                <th scope="col" class="meta-table__header">Tabela OTM</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {% for obj in dt_objects | sort(attribute="sequence") %}
                                                <tr class="meta-table__row">
                                                    <td class="meta-table__value">{{ obj.responsible }}</td>
                                                    <td class="meta-table__value">{{ obj.sequence }}</td>
                                                    <td class="meta-table__value">{{ obj.group_label }}</td>
                                                    <td class="meta-table__value">{{ obj.description }}</td>
                                                    <td class="meta-table__value">{{ obj.object_type }}</td>
                                                </tr>
                                            {% endfor %}
                                        </tbody>
                                    </table>
                                {% endif %}
                            </div>
                        {% endif %}
                    {% endfor %}
                </section>
            </div>
        </div>

        <!-- =============================================
             SEÇÃO 7: OVERVIEW DOS GRUPOS
             ============================================= -->

        <!-- =============================================
             SEÇÃO 3: GRUPOS E OBJETOS DE MIGRAÇÃO
             - Iteração sobre grupos de objetos
             - Cards para cada objeto com metadados e código
             ============================================= -->
        {% for group in data.groups %}
        {% set group_index = loop.index %}
        {% set group_id = "group-" + group.label.lower().replace(" ", "-").replace("ã", "a").replace("é", "e").replace("ç", "c") %}
        <div class="page">
            <div class="page-content">
                {% if loop.first %}
                <!-- Overview do grupos - inserido na primeira página -->
                <section class="groups-overview" aria-label="Grupos e Objetos de Migração OTM" id="grupos-overview">
                    <header class="groups-overview__header">
                        <h2 class="groups-overview__title">Grupos e Objetos de Migração OTM</h2>
                    </header>
                    <div class="groups-overview__content">
                        <p>Esta seção apresenta os conjuntos de objetos do Oracle Transportation Management (OTM) contemplados no escopo de migração.</p>
                    </div>
                </section>
                {% endif %}
                
                <section class="group-block" aria-label="Grupo: {{ group.label }}" id="{{ group_id }}">
                    <!-- Cabeçalho do Grupo -->
                    <header class="group-block__header">
                        <h2 class="group-block__title">Grupo: {{ group.label }}</h2>
                    </header>

                    {% if group.description %}
                    <div class="group-block__description">
                        {% for paragraph in group.description_paragraphs %}
                            <p>{{ paragraph }}</p>
                        {% endfor %}
                    </div>
                    {% endif %}

                    <!-- Lista de Objetos do Grupo -->
                    <div class="group-block__content">
                        {% for object in group.objects %}
                        {% set object_id = "object-" + object.name.lower().replace(" ", "-").replace("(", "").replace(")", "").replace("ã", "a").replace("é", "e").replace("ç", "c") %}
                        <!-- ==========================================
                             OBJETO: {{ object.name }}
                             Tipo: {{ object.object_type }}
                             Sequência: {{ object.sequence }}
                             ========================================== -->
                        <article class="object-card" aria-label="{{ object.name }}" id="{{ object_id }}">
                            <!-- Header do Objeto -->
                            <header class="object-card__header">
                                <div class="object-card__title-group">
                                    <h3 class="object-card__title">
                                        {{ object.name }}
                                    </h3>
                                </div>
                                {% if object.sequence %}
                                <span class="object-card__sequence">#{{ object.sequence }}</span>
                                {% endif %}
                            </header>

                    <!-- Descrição do Objeto -->
                    {% if object.description %}
                    <p class="object-card__description">{{ object.description }}</p>
                    {% endif %}

                    <!-- Metadados do Objeto -->
                    <div class="object-card__body">
                        <div class="object-card__metadata-grid">
                            <div class="object-card__metadata-section">
                                <table class="meta-table meta-table--object" role="table" aria-label="Propriedades de {{ object.name }}">
                                    <thead class="visually-hidden">
                                        <tr>
                                            <th scope="col">Propriedade</th>
                                            <th scope="col">Valor</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <!-- Propriedades Básicas -->
                                        <tr class="meta-table__row">
                                            <th scope="row" class="meta-table__label">Sequência</th>
                                            <td class="meta-table__value">{{ object.sequence }}</td>
                                        </tr>
                                        <tr class="meta-table__row">
                                            <th scope="row" class="meta-table__label">Object Type</th>
                                            <td class="meta-table__value">{{ object.object_type }}</td>
                                        </tr>
                                        {% if object.otm_table %}
                                        <tr class="meta-table__row">
                                            <th scope="row" class="meta-table__label">OTM Table</th>
                                            <td class="meta-table__value meta-table__value--code">{{ object.otm_table }}</td>
                                        </tr>
                                        {% endif %}
                                        <tr class="meta-table__row">
                                            <th scope="row" class="meta-table__label">Deployment Type</th>
                                            <td class="meta-table__value">{{ object.deployment_type }}</td>
                                        </tr>
                                        <tr class="meta-table__row">
                                            <th scope="row" class="meta-table__label">Responsável</th>
                                            <td class="meta-table__value">{{ object.responsible }}</td>
                                        </tr>
                                        {% if object.migration_type %}
                                        <tr class="meta-table__row">
                                            <th scope="row" class="meta-table__label">Tipo de Migração</th>
                                            <td class="meta-table__value">{{ object.migration_type }}</td>
                                        </tr>
                                        {% endif %}

                                        <!-- Identificadores Dinâmicos -->
                                        {% for key, value in object.identifiers.items() %}
                                        <tr class="meta-table__row meta-table__row--identifier">
                                            <th scope="row" class="meta-table__label">{{ key.replace('_', ' ') | title }}</th>
                                            <td class="meta-table__value">{{ value }}</td>
                                        </tr>
                                        {% endfor %}
                                    </tbody>
                                </table>
                            </div>

                            <!-- Status do Objeto -->
                            <div class="object-card__metadata-section">
                                <div class="status-panel" aria-label="Status do objeto">
                                    <h4 class="status-panel__title">Status</h4>
                                    <table class="status-table" role="table">
                                        <thead class="visually-hidden">
                                            <tr>
                                                <th scope="col">Etapa</th>
                                                <th scope="col">Status</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            <tr class="status-table__row">
                                                <th scope="row" class="status-table__label">Documentação</th>
                                                <td class="status-table__value">
                                                    <span class="status-badge status-badge--{{ object.status.documentation | lower | default('pending') }}">
                                                        {{ object.status.documentation }}
                                                    </span>
                                                </td>
                                            </tr>
                                            <tr class="status-table__row">
                                                <th scope="row" class="status-table__label">Migration Project</th>
                                                <td class="status-table__value">
                                                    <span class="status-badge status-badge--{{ object.status.migration_project | lower | default('pending') }}">
                                                        {{ object.status.migration_project }}
                                                    </span>
                                                </td>
                                            </tr>
                                            <tr class="status-table__row">
                                                <th scope="row" class="status-table__label">Exportação</th>
                                                <td class="status-table__value">
                                                    <span class="status-badge status-badge--{{ object.status.export | lower | default('pending') }}">
                                                        {{ object.status.export }}
                                                    </span>
                                                </td>
                                            </tr>
                                            <tr class="status-table__row">
                                                <th scope="row" class="status-table__label">Deploy</th>
                                                <td class="status-table__value">
                                                    <span class="status-badge status-badge--{{ object.status.deploy | lower | default('pending') }}">
                                                        {{ object.status.deploy }}
                                                    </span>
                                                </td>
                                            </tr>
                                            <tr class="status-table__row">
                                                <th scope="row" class="status-table__label">Validação</th>
                                                <td class="status-table__value">
                                                    <span class="status-badge status-badge--{{ object.status.validation | lower | default('pending') }}">
                                                        {{ object.status.validation }}
                                                    </span>
                                                </td>
                                            </tr>
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>

                        <!-- Notas (se existirem) -->
                        {% if object.notes %}
                        <aside class="object-card__notes" aria-label="Notas adicionais">
                            <h4 class="object-card__notes-title">Notas</h4>
                            <p class="object-card__notes-content">{{ object.notes }}</p>
                        </aside>
                        {% endif %}
                    </div>

                    <!-- Query de Extração de Objetos -->
                    {% if object.object_extraction_query and object.object_extraction_query.content %}
                    <section class="code-section" aria-label="Query de extração de objetos">
                        <header class="code-section__header">
                            <h4 class="code-section__title">Query de Extração de Objetos</h4>
                            <span class="code-section__lang">{{ object.object_extraction_query.language | upper }}</span>
                        </header>
                        <div class="code-section__content">
                            <pre class="code-block"><code class="language-{{ object.object_extraction_query.language | lower }}">{{ object.object_extraction_query.content }}</code></pre>
                        </div>
                    </section>
                    {% endif %}

                    {% if object.technical_content and object.technical_content.content %}
                    <section class="code-section" aria-label="Conteúdo técnico">
                        <header class="code-section__header">
                            <h4 class="code-section__title">Conteúdo Técnico</h4>
                            <span class="code-section__lang">{{ object.technical_content.type | upper }}</span>
                        </header>
                        <div class="code-section__content">
                            <pre class="code-block"><code class="language-{{ object.technical_content.type | lower }}">{{ object.technical_content.content }}</code></pre>
                        </div>
                    </section>
                    {% endif %}
                        </article>
                        {% endfor %}
                    </div>
                </section>

                {% if loop.last %}
                <!-- =============================================
                     RODAPÉ DO DOCUMENTO
                     ============================================= -->
                <footer class="document-footer" role="contentinfo">
                    <p class="document-footer__text">
                        {{ data.project.name }} • {{ data.project.code }} • v{{ data.project.version }}
                    </p>
                </footer>
                {% endif %}
            </div>
        </div>
        {% endfor %}
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
    <script>
    // Initialize highlight.js
    document.addEventListener('DOMContentLoaded', (event) => {
        document.querySelectorAll('pre code').forEach((block) => {
            hljs.highlightElement(block);
        });
    });
    </script>
</body>
</html>
