{% set idx = 1 %}
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>{{ projeto.nome }}</title>
    <link rel="stylesheet" href="pdf.css">
</head>

<body>

    <section id="sec-capa" class="cover-page">

        <div class="cover-header">
            OmniDeck – Projeto de Migração
        </div>

        <div class="cover-content">

            {% if projeto.logo_path %}
            <div class="cover-logo">
                <img src="{{ projeto.logo_path }}">
            </div>
            {% endif %}

            <div class="cover-category">
                PROJETO DE MIGRAÇÃO OTM
            </div>

            <h1 class="cover-title">
                {{ projeto.nome }}
            </h1>

            <div class="cover-divider"></div>

        </div>

        <div class="cover-footer">
            Documento Confidencial – Uso Corporativo
        </div>

    </section>

    <!-- ==============================
         METADADOS
    =============================== -->
    <section id="sec-metadata" class="page">
        <h2>Informações do Projeto</h2>

        <!-- BLOCO EDITORIAL -->
        <div class="metadata-context">

            {% if projeto.escopo %}
            <h3>Escopo</h3>
            <p>{{ projeto.escopo }}</p>
            {% endif %}

        </div>

        <!-- BLOCO GOVERNANÇA -->
        <div class="metadata-governance">
            <table class="metadata-table">

                {% if projeto.codigo %}
                <tr>
                    <td>Código</td>
                    <td>{{ projeto.codigo }}</td>
                </tr>
                {% endif %}

                {% if projeto.versao %}
                <tr>
                    <td>Versão</td>
                    <td>{{ projeto.versao }}</td>
                </tr>
                {% endif %}

                {% if projeto.status %}
                <tr>
                    <td>Status</td>
                    <td>{{ projeto.status }}</td>
                </tr>
                {% endif %}

                {% if projeto.cliente %}
                <tr>
                    <td>Cliente</td>
                    <td>{{ projeto.cliente }}</td>
                </tr>
                {% endif %}

                {% if projeto.environment_source_url %}
                <tr>
                    <td>Ambiente de Origem</td>
                    <td>
                        <a href="{{ projeto.environment_source_url }}">
                            {{ projeto.environment_source_url }}
                        </a>
                    </td>
                </tr>
                {% endif %}

                {% if projeto.environment_target_url %}
                <tr>
                    <td>Ambiente de Destino</td>
                    <td>
                        <a href="{{ projeto.environment_target_url }}">
                            {{ projeto.environment_target_url }}
                        </a>
                    </td>
                </tr>
                {% endif %}

            </table>
        </div>

        <!-- BLOCO DINÂMICO DE METADADOS ADICIONAIS -->
        <div class="metadata-dynamic">
            <table class="metadata-table">

                {% for key, value in projeto.items() %}

                    {% if key|lower not in ['nome','logo_path','versao','codigo','responsavel','data_geracao','objetivo','escopo','cliente','status','grupos','roadmap','environment_source_url','environment_target_url','name','code','version','consultant','state','environment']
                          and value
                          and value != ""
                          and value != []
                          and value != {} %}

                        {% if value is string or value is number or value is boolean %}
                        <tr>
                            <td>{{ key | replace('_',' ') | title }}</td>
                            <td>{{ value }}</td>
                        </tr>
                        {% endif %}

                    {% endif %}

                {% endfor %}

            </table>
        </div>
    </section>

    {% if projeto.change_history and projeto.change_history|length > 0 %}
    <section id="sec-historico" class="history-page">
        <h2>Histórico de Atualizações</h2>

        <table class="metadata-table">
            <thead>
                <tr>
                    <th>Versão</th>
                    <th>Data</th>
                    <th>Autor</th>
                    <th>Descrição</th>
                </tr>
            </thead>
            <tbody>
                {% for item in projeto.change_history %}
                <tr>
                    <td>{{ item.version }}</td>
                    <td>{{ item.date }}</td>
                    <td>{{ item.author }}</td>
                    <td>{{ item.description }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </section>
    {% endif %}

    <!-- ==============================
         SUMÁRIO (DINÂMICO HIERÁRQUICO)
    =============================== -->
    <section id="sec-sumario" class="page">
        <h2>Sumário</h2>
        <nav class="toc">
            <ol>

                <!-- 1 -->
                <li>
                    <a href="#sec-metadata">1. Informações do Projeto</a>
                </li>


                {# Filtra apenas linhas que possuem a chave 'object' e são dicionários #}
                {% set object_rows = cache_data | selectattr('object', 'defined') | list %}

                {# Coleta todas as chaves dinâmicas dos objetos #}
                {% set all_keys = [] %}
                {% for row in object_rows %}
                    {% if row['object'] is mapping %}
                        {% for key, value in row['object'].items() %}
                            {% if key not in all_keys %}
                                {% set _ = all_keys.append(key) %}
                            {% endif %}
                        {% endfor %}
                    {% endif %}
                {% endfor %}

                <table>
                    <thead>
                        <tr>
                            {% for key in all_keys %}
                                <th>{{ key }}</th>
                            {% endfor %}
                        </tr>
                    </thead>
                    <tbody>
                        {% for row in object_rows %}
                            {% if row['object'] is mapping %}
                                <tr>
                                    {% for key in all_keys %}
                                        <td>{{ row['object'][key] if key in row['object'] else '' }}</td>
                                    {% endfor %}
                                </tr>
                            {% endif %}
                        {% endfor %}
                    </tbody>
                </table>
                    </ol>
                </li>
                {% set idx = idx + 1 %}

                <!-- Grupos -->
                {% if projeto.grupos and projeto.grupos|length > 0 %}
                {% set grupos_idx = idx %}
                <li>
                    <a href="#sec-grupos-otm">{{ grupos_idx }}. Grupos e Objetos de Migração OTM</a>
                    <ol>
                        {% for grupo in projeto.grupos | sort(attribute='sequence') %}
                        {% set grupo_index = loop.index %}
                        {% set grupo_anchor = grupo.nome|replace(' ','-')|lower %}
                        <li>
                            <a href="#grupo-{{ grupo_anchor }}">
                                {{ grupos_idx }}.{{ loop.index }} {{ grupo.nome }}
                            </a>

                            {% if grupo.objetos and grupo.objetos|length > 0 %}
                            <ol>
                                {% for objeto in grupo.objetos | sort(attribute='sequence') %}
                                {% set obj_anchor = objeto.name|replace(' ','-')|lower %}
                                <li>
                                    <a href="#objeto-{{ obj_anchor }}">
                                        {{ grupos_idx }}.{{ grupo_index }}.{{ loop.index }} {{ objeto.name }}
                                    </a>
                                </li>
                                {% endfor %}
                            </ol>
                            {% endif %}

                        </li>
                        {% endfor %}
                    </ol>
                </li>
                {% endif %}

            </ol>
        </nav>
    </section>

    <!-- ==============================
         OBJETIVO
    =============================== -->
    {% if projeto.objetivo %}
    <section id="sec-resumo" class="page">
        <h2>Resumo Executivo</h2>
        <p>{{ projeto.objetivo }}</p>
    </section>
    {% endif %}

    <!-- ==============================
         ROADMAP DE MIGRAÇÃO
    =============================== -->
    <section id="sec-roadmap" class="page landscape">

        {% if projeto.roadmap_dinamico %}
            {% for tipo, objetos in projeto.roadmap_dinamico.items() %}
            <div class="roadmap-block" id="roadmap-{{ tipo|lower }}">
                {% if loop.first %}
                    <h2>Roadmap de Migração</h2>
                    <p class="roadmap-intro">
                        Este capítulo apresenta o roadmap completo de migração, mapeando todos os objetos OTM por estratégia de implantação.
                    </p>
                {% endif %}

                <h3>{{ tipo }} ({{ objetos|length }} objetos)</h3>

                {% if tipo == 'MANUAL' %}
                <table class="metadata-table">
                    <thead>
                        <tr>
                            <th>Resp.</th>
                            <th>Tipo Migração</th>
                            <th>Grupo</th>
                            <th>Descrição</th>
                            <th>Tabela OTM</th>
                        </tr>
                    </thead>
                    <tbody>
                    {% for obj in objetos | sort(attribute='seq') | sort(attribute='grupo') %}
                        <tr>
                            <td>{{ obj.responsavel }}</td>
                            <td>{{ obj.tipo_migracao }}</td>
                            <td>{{ obj.grupo }}</td>
                            <td>{{ obj.descricao }}</td>
                            <td>{{ obj.otm_table or '-' }}</td>
                        </tr>
                    {% endfor %}
                    </tbody>
                </table>

                {% elif tipo == 'MIGRATION_PROJECT' %}
                <table class="metadata-table">
                    <thead>
                        <tr>
                            <th>Resp.</th>
                            <th>Tipo Migração</th>
                            <th>Seq.</th>
                            <th>ID Migration Project</th>
                            <th>Grupo</th>
                            <th>Descrição</th>
                            <th>Tabela OTM</th>
                        </tr>
                    </thead>
                    <tbody>
                    {% for obj in objetos | sort(attribute='seq') | sort(attribute='grupo') %}
                        <tr>
                            <td>{{ obj.responsavel }}</td>
                            <td>{{ obj.tipo_migracao }}</td>
                            <td>{{ obj.seq or '-' }}</td>
                            <td></td>
                            <td>{{ obj.grupo }}</td>
                            <td>{{ obj.descricao }}</td>
                            <td>{{ obj.otm_table or '-' }}</td>
                        </tr>
                    {% endfor %}
                    </tbody>
                </table>

                {% elif tipo == 'CSV' or tipo == 'DB_XML' or tipo == 'INTEGRATION' %}
                <table class="metadata-table">
                    <thead>
                        <tr>
                            <th>Resp.</th>
                            <th>Tipo Migração</th>
                            <th>Seq.</th>
                            <th>Grupo</th>
                            <th>Descrição</th>
                            <th>Tabela OTM</th>
                        </tr>
                    </thead>
                    <tbody>
                    {% for obj in objetos | sort(attribute='seq') | sort(attribute='grupo') %}
                        <tr>
                            <td>{{ obj.responsavel }}</td>
                            <td>{{ obj.tipo_migracao }}</td>
                            <td>{{ obj.seq or '-' }}</td>
                            <td>{{ obj.grupo }}</td>
                            <td>{{ obj.descricao }}</td>
                            <td>{{ obj.otm_table or '-' }}</td>
                        </tr>
                    {% endfor %}
                    </tbody>
                </table>

                {% else %}
                <table class="metadata-table">
                    <thead>
                        <tr>
                            <th>Resp.</th>
                            <th>Tipo Migração</th>
                            <th>Grupo</th>
                            <th>Descrição</th>
                        </tr>
                    </thead>
                    <tbody>
                    {% for obj in objetos | sort(attribute='seq') | sort(attribute='grupo') %}
                        <tr>
                            <td>{{ obj.responsavel }}</td>
                            <td>{{ obj.tipo_migracao }}</td>
                            <td>{{ obj.grupo }}</td>
                            <td>{{ obj.descricao }}</td>
                        </tr>
                    {% endfor %}
                    </tbody>
                </table>
                {% endif %}

            </div>
            {% endfor %}
        {% else %}
            <p>Nenhum objeto registrado para o roadmap.</p>
        {% endif %}
    </section>

    <!-- ==============================
         GRUPOS E OBJETOS DE MIGRAÇÃO OTM
    =============================== -->
    <section id="sec-grupos-otm">
        <h2>Grupos e Objetos de Migração OTM</h2>

        <div class="groups-intro no-page-break">
            <p>
                Esta seção apresenta os conjuntos de objetos do Oracle Transportation Management (OTM) contemplados no escopo de migração, organizados por agrupamentos funcionais e estruturais do sistema.
            </p>

            <p>
                Cada grupo consolida entidades que compartilham finalidade operacional ou técnica, permitindo rastrear impactos, dependências e critérios de implantação ao longo do ciclo de migração. A organização por grupos facilita a governança do projeto, a priorização das atividades e a validação técnica entre ambiente de origem e destino.
            </p>

            <p><strong>Para cada objeto são descritos:</strong></p>

            <ul class="groups-list">
                <li>Nome técnico da entidade no OTM</li>
                <li>Contexto funcional dentro do domínio</li>
                <li>Finalidade operacional ou estrutural</li>
                <li>Papel no baseline de configuração</li>
                <li>Relevância para estabilidade do ambiente pós-migração</li>
            </ul>

            <p><strong>Essa estrutura garante rastreabilidade completa entre:</strong></p>

            <ul class="groups-list">
                <li>Roadmap de Migração</li>
                <li>Estratégia de Implantação (Manual, Migration Project, CSV, DB.XML, etc.)</li>
                <li>Governança técnica do domínio</li>
                <li>Validação funcional e homologação</li>
            </ul>
        </div>

        {% if projeto.grupos and projeto.grupos|length > 0 %}

        {% for grupo in projeto.grupos | sort(attribute='sequence') %}
        <div class="group-block{% if loop.first %} group-block-first{% endif %}" id="grupo-{{ grupo.nome|replace(' ','-')|lower }}">

            {# === FIX: garante que cabeçalho + 1º objeto não se separem === #}
            {% set objetos_sorted = (grupo.objetos | default([])) | sort(attribute='sequence') %}

            <div class="group-pack">
                <div class="group-head">
                    <h3>{{ grupo.nome }}</h3>

                    {% if grupo.descricao %}
                    <p class="group-description">
                        {{ grupo.descricao }}
                    </p>
                    {% endif %}
                </div>

                {% if objetos_sorted and objetos_sorted|length > 0 %}
                    {% set objeto = objetos_sorted[0] %}
                    <div class="group-item group-item-first" id="objeto-{{ objeto.name|replace(' ','-')|lower }}">

                        <!-- Nome Técnico do Objeto -->
                        <strong>{{ objeto.name }}</strong>

                        <!-- Linha técnica auxiliar (opcional e futura expansão) -->
                        {% if objeto.otm_table or objeto.tipo_migracao or grupo.nome %}
                        <div class="object-meta">
                            {% if objeto.otm_table %}
                                Tabela OTM: {{ objeto.otm_table }}
                            {% endif %}
                            {% if objeto.tipo_migracao %}
                                {% if objeto.otm_table %} | {% endif %}
                                Estratégia: {{ objeto.tipo_migracao }}
                            {% endif %}
                            {% if grupo.nome %}
                                {% if objeto.otm_table or objeto.tipo_migracao %} | {% endif %}
                                Grupo: {{ grupo.nome }}
                            {% endif %}
                        </div>
                        {% endif %}

                        <!-- Descrição Técnica -->
                        {% if objeto.description %}
                        <p>
                            {{ objeto.description }}
                        </p>
                        {% endif %}

                        <!-- NAVEGAÇÃO OTM (posicionada logo após a descrição) -->
                        {% if objeto.otm_navigation_path_en %}
                        <div class="object-navigation">
                            <p><strong>Navegação OTM:</strong> {{ objeto.otm_navigation_path_en }}</p>
                        </div>
                        {% endif %}

                        <!-- STATUS DO OBJETO -->
                        {% if objeto.status %}
                        <div class="object-status">
                            <strong>Status</strong>
                            <div class="status-badges">

                                {% set s = objeto.status %}

                                {% set items = [
                                    ('Documentação Técnica', s.documentation),
                                    ('Configuração do Projeto de Migração', s.migration_project),
                                    ('Preparação de Arquivos para Migração', s.export),
                                    ('Configuração Técnica no Sistema', s.deploy),
                                    ('Validação Funcional', s.validation),
                                    ('Implantação em Produção', s.deployment)
                                ] %}

                                {% for label, value in items %}
                                    {% set val = value or '-' %}
                                    {% set css_class = '' %}
                                    {% if val == 'DONE' %}
                                        {% set css_class = 'done' %}
                                    {% elif val == 'PENDING' %}
                                        {% set css_class = 'pending' %}
                                    {% elif val == 'FAILED' %}
                                        {% set css_class = 'failed' %}
                                    {% endif %}

                                    <span class="status-badge {{ css_class }}">
                                        {{ label }}: {{ val }}
                                    </span>
                                {% endfor %}

                            </div>
                        </div>
                        {% endif %}

                        <!-- QUERY DE EXTRAÇÃO -->
                        {% if objeto.object_extraction_query and objeto.object_extraction_query.content %}
                        <div class="object-extraction">
                            <p><strong>Query de Extração:</strong></p>
                            <pre><code class="language-sql">{{ objeto.object_extraction_query.content | safe }}</code></pre>
                        </div>
                        {% endif %}

                        <!-- CONTEÚDO TÉCNICO -->
                        {% if objeto.technical_content and objeto.technical_content.content %}
                        <div class="object-technical">
                            <p><strong>Conteúdo Técnico ({{ objeto.technical_content.type or 'N/A' }}):</strong></p>
                            <pre><code>{{ objeto.technical_content.content }}</code></pre>
                        </div>
                        {% endif %}

                        <!-- RELACIONAMENTOS OTM -->
                        {% if objeto.otm_subtables or objeto.otm_related_tables %}
                            <p><strong>Relacionamentos OTM:</strong></p>
                            <ul>
                                {% if objeto.otm_subtables %}
                                <li><strong>Subtables:</strong> {{ objeto.otm_subtables | join(', ') }}</li>
                                {% endif %}
                                {% if objeto.otm_related_tables %}
                                <li><strong>Related Tables:</strong> {{ objeto.otm_related_tables | join(', ') }}</li>
                                {% endif %}
                            </ul>
                        {% endif %}
                    </div>
                {% endif %}

                {% if objeto.object_cache_results %}
                <section class="page landscape object-extraction-result">
                    <p><strong>Resultado da Extração:</strong></p>
                            {% set cache = objeto.object_cache_results[0] if objeto.object_cache_results|length > 0 else None %}
                            {% if cache %}
                                {# Busca as linhas do cache, tentando os caminhos mais comuns #}
                                {% set rows = None %}
                                {% if cache.cache_data and cache.cache_data.data and cache.cache_data.data.rows %}
                                    {% set rows = cache.cache_data.data.rows %}
                                {% elif cache.cache_data and cache.cache_data.tables and objeto.otm_table and cache.cache_data.tables[objeto.otm_table] and cache.cache_data.tables[objeto.otm_table].rows %}
                                    {% set rows = cache.cache_data.tables[objeto.otm_table].rows %}
                                {% endif %}
                                {% if rows and rows|length > 0 %}
                                    {# Usa selected_columns se existir, senão coleta as chaves dinâmicas #}
                                    {% set all_keys = [] %}
                                    {% if objeto.selected_columns is defined and objeto.selected_columns %}
                                        {% for col in objeto.selected_columns %}
                                            {% set _ = all_keys.append(col) %}
                                        {% endfor %}
                                    {% else %}
                                        {# Se não houver selected_columns, pega só a chave primária (primeira coluna de cada linha) #}
                                        {% if rows and rows|length > 0 %}
                                            {% set first_row = rows[0] %}
                                            {% if first_row.items is defined %}
                                                {% set first_key = first_row.keys()|list|first %}
                                                {% if first_key %}
                                                    {% set _ = all_keys.append(first_key) %}
                                                {% endif %}
                                            {% endif %}
                                        {% endif %}
                                    {% endif %}
                                    {% if not all_keys or all_keys|length == 0 %}
                                        {% set all_keys = [] %}
                                        {% for row in rows %}
                                            {% if row.items is defined %}
                                                {% for k in row.keys() %}
                                                    {% if k not in all_keys %}
                                                        {% set _ = all_keys.append(k) %}
                                                    {% endif %}
                                                {% endfor %}
                                            {% endif %}
                                        {% endfor %}
                                    {% endif %}
                                    <table class="metadata-table" style="table-layout: fixed; width: 100%;">
                                        <thead>
                                            <tr>
                                                {% for k in objeto.selected_columns %}
                                                    <th>{{ k.split('.')[-1] }}</th>
                                                {% endfor %}
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {% for row in rows %}
                                                {% if row.items is defined %}
                                                    <tr>
                                                        {% for k in objeto.selected_columns %}
                                                            {% set is_id_col = k.lower().endswith('_id') or k.lower().endswith('_gid') or k.lower().endswith('_xid') or k.lower() in ['id', 'codigo', 'code'] %}
                                                            <td style="{{ 'overflow-wrap: anywhere; white-space: pre-wrap; padding: 0px 4px;' if is_id_col else 'word-break: break-all; overflow-wrap: break-word; hyphens: auto; white-space: pre-wrap; padding: 0px 4px;' }}">
                                                                {% if k in row %}
                                                                    {% if row[k] is iterable and row[k] is not string %}
                                                                        {{ row[k]|join(', ') if row[k]|length > 0 else 'N/A' }}
                                                                    {% else %}
                                                                        <span style="white-space: normal; display: inline-block;">{{ (row[k] if row[k] else 'N/A')|trim }}</span>
                                                                    {% endif %}
                                                                {% else %}
                                                                    'N/A'
                                                                {% endif %}
                                                            </td>
                                                        {% endfor %}
                                                    </tr>
                                                {% endif %}
                                            {% endfor %}
                                        </tbody>
                                    </table>
                                {% else %}
                                    <p style="color: #c00;">Nenhum dado encontrado nas linhas do cache.</p>
                                {% endif %}
                            {% endif %}
                </div>
                {% endif %}
                </section>
                <div style="page-break-before: always;"></div>
            </div>

            {# === Demais objetos do grupo (a partir do 2º) === #}
            {% if objetos_sorted and objetos_sorted|length > 1 %}
                {% for objeto in objetos_sorted[1:] %}
                <div class="group-item" id="objeto-{{ objeto.name|replace(' ','-')|lower }}">

                    <!-- Nome Técnico do Objeto -->
                    <strong>{{ objeto.name }}</strong>

                    <!-- Linha técnica auxiliar (opcional e futura expansão) -->
                    {% if objeto.otm_table or objeto.tipo_migracao or grupo.nome %}
                    <div class="object-meta">
                        {% if objeto.otm_table %}
                            Tabela OTM: {{ objeto.otm_table }}
                        {% endif %}
                        {% if objeto.tipo_migracao %}
                            {% if objeto.otm_table %} | {% endif %}
                            Estratégia: {{ objeto.tipo_migracao }}
                        {% endif %}
                        {% if grupo.nome %}
                            {% if objeto.otm_table or objeto.tipo_migracao %} | {% endif %}
                            Grupo: {{ grupo.nome }}
                        {% endif %}
                    </div>
                    {% endif %}

                    <!-- Descrição Técnica -->
                    {% if objeto.description %}
                    <p>
                        {{ objeto.description }}
                    </p>
                    {% endif %}

                    <!-- NAVEGAÇÃO OTM (posicionada logo após a descrição) -->
                    {% if objeto.otm_navigation_path_en %}
                    <div class="object-navigation">
                        <p><strong>Navegação OTM:</strong> {{ objeto.otm_navigation_path_en }}</p>
                    </div>
                    {% endif %}

                    <!-- STATUS DO OBJETO -->
                    {% if objeto.status %}
                    <div class="object-status">
                        <strong>Status</strong>
                        <div class="status-badges">

                            {% set s = objeto.status %}

                            {% set items = [
                                ('Documentação Técnica', s.documentation),
                                ('Configuração do Projeto de Migração', s.migration_project),
                                ('Preparação de Arquivos para Migração', s.export),
                                ('Configuração Técnica no Sistema', s.deploy),
                                ('Validação Funcional', s.validation),
                                ('Implantação em Produção', s.deployment)
                            ] %}

                            {% for label, value in items %}
                                {% set val = value or '-' %}
                                {% set css_class = '' %}
                                {% if val == 'DONE' %}
                                    {% set css_class = 'done' %}
                                {% elif val == 'PENDING' %}
                                    {% set css_class = 'pending' %}
                                {% elif val == 'FAILED' %}
                                    {% set css_class = 'failed' %}
                                {% endif %}

                                <span class="status-badge {{ css_class }}">
                                    {{ label }}: {{ val }}
                                </span>
                            {% endfor %}

                        </div>
                    </div>
                    {% endif %}

                    <!-- QUERY DE EXTRAÇÃO -->
                    {% if objeto.object_extraction_query and objeto.object_extraction_query.content %}
                    <div class="object-extraction">
                        <p><strong>Query de Extração:</strong></p>
                        <pre><code class="language-sql">{{ objeto.object_extraction_query.content | safe }}</code></pre>
                    </div>
                    {% endif %}

                    <!-- CONTEÚDO TÉCNICO -->
                    {% if objeto.technical_content and objeto.technical_content.content %}
                    <div class="object-technical">
                        <p><strong>Conteúdo Técnico ({{ objeto.technical_content.type or 'N/A' }}):</strong></p>
                        <pre><code>{{ objeto.technical_content.content }}</code></pre>
                    </div>
                    {% endif %}

                    <!-- RELACIONAMENTOS OTM -->
                    {% if objeto.otm_subtables or objeto.otm_related_tables %}
                    <div class="object-relationships">
                        <p><strong>Relacionamentos OTM:</strong></p>
                        <ul>
                            {% if objeto.otm_subtables %}
                            <li><strong>Subtables:</strong> {{ objeto.otm_subtables | join(', ') }}</li>
                            {% endif %}
                            {% if objeto.otm_related_tables %}
                            <li><strong>Related Tables:</strong> {{ objeto.otm_related_tables | join(', ') }}</li>
                            {% endif %}
                        </ul>
                    </div>
                    {% endif %}

                </div>
                {% endfor %}
            {% endif %}

        </div>
        {% endfor %}

        {% else %}
            <p>Nenhum grupo configurado para este projeto.</p>
        {% endif %}

    </section>

</body>
</html>