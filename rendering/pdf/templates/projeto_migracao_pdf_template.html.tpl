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

                {% set idx = 2 %}

                <!-- Histórico -->
                {% if projeto.change_history and projeto.change_history|length > 0 %}
                <li>
                    <a href="#sec-historico">{{ idx }}. Histórico de Atualizações</a>
                </li>
                {% set idx = idx + 1 %}
                {% endif %}

                <!-- Resumo -->
                {% if projeto.objetivo %}
                <li>
                    <a href="#sec-resumo">{{ idx }}. Resumo Executivo</a>
                </li>
                {% set idx = idx + 1 %}
                {% endif %}

                <!-- Roadmap -->
                {% if projeto.roadmap_dinamico %}
                {% set roadmap_idx = idx %}
                <li>
                    <a href="#sec-roadmap">{{ roadmap_idx }}. Roadmap de Migração</a>
                    <ol>
                        {% for tipo, objetos in projeto.roadmap_dinamico.items() %}
                        <li>
                            <a href="#roadmap-{{ tipo|lower }}">
                                {{ roadmap_idx }}.{{ loop.index }} {{ tipo }} ({{ objetos|length }} objetos)
                            </a>
                        </li>
                        {% endfor %}
                    </ol>
                </li>
                {% set idx = idx + 1 %}
                {% endif %}

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
                            <td>{{ obj.id_migration_project or obj.codigo or obj.migration_item_id or '-' }}</td>
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
        <div class="groups-intro">
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
            <h3>{{ grupo.nome }}</h3>

            {% if grupo.descricao %}
            <p class="group-description">
                {{ grupo.descricao }}
            </p>
            {% endif %}

            {% if grupo.objetos and grupo.objetos|length > 0 %}
                {% for objeto in grupo.objetos | sort(attribute='sequence') %}
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
