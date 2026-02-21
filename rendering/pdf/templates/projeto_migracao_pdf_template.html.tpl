<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>{{ projeto.nome }}</title>
    <link rel="stylesheet" href="pdf.css">
</head>

<body>

    <section class="cover-page">

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

            <div class="cover-meta">
                <div><strong>Versão:</strong> {{ projeto.versao }}</div>
                <div><strong>Código:</strong> {{ projeto.codigo }}</div>
                <div><strong>Consultor:</strong> {{ projeto.responsavel }}</div>
                <div><strong>Data:</strong> {{ projeto.data_geracao }}</div>
            </div>

        </div>

        <div class="cover-footer">
            Documento Confidencial – Uso Corporativo
        </div>

    </section>

    <!-- ==============================
         METADADOS
    =============================== -->
    <section class="metadata-page">
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
         SUMÁRIO
    =============================== -->
    <section class="toc-page">
        <h2>Sumário</h2>
        <ul class="toc-list">
            {% if projeto.change_history and projeto.change_history|length > 0 %}
            <li><a href="#sec-historico">Histórico de Atualizações</a></li>
            {% endif %}
            <li><a href="#sec-resumo">Resumo Executivo</a></li>
            <li><a href="#sec-roadmap">Roadmap</a></li>
        </ul>
    </section>


    <!-- ==============================
         OBJETIVO
    =============================== -->
    {% if projeto.objetivo %}
    <section id="sec-resumo">
        <h2>Resumo Executivo</h2>
        <p>{{ projeto.objetivo }}</p>
    </section>
    {% endif %}

    <!-- ==============================
         ROADMAP DE MIGRAÇÃO
    =============================== -->
    <section id="sec-roadmap" class="roadmap-page">

        {% if projeto.roadmap_dinamico %}
            {% for tipo, objetos in projeto.roadmap_dinamico.items() %}
            <div class="roadmap-block page landscape" style="page-break-before: always;">
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
    <section id="sec-grupos-otm" class="groups-page">
        <h2>Grupos e Objetos de Migração OTM</h2>
        <p class="groups-intro">
            Esta seção apresenta os conjuntos de objetos do Oracle Transportation Management (OTM) contemplados no escopo de migração.
        </p>

        {% if projeto.grupos and projeto.grupos|length > 0 %}

        {% for grupo in projeto.grupos | sort(attribute='sequence') %}
        <div class="group-block">
            <h3>{{ grupo.nome }}</h3>

            {% if grupo.descricao %}
            <p class="group-description">
                {{ grupo.descricao }}
            </p>
            {% endif %}

            {% if grupo.objetos and grupo.objetos|length > 0 %}
                {% for objeto in grupo.objetos | sort(attribute='sequence') %}
                <div class="group-item">
                    <h4>{{ objeto.name }}</h4>

                    {% if objeto.description %}
                    <div class="migration-object-description">
                        {{ objeto.description }}
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
