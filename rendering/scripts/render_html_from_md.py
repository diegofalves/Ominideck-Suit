import json
from pathlib import Path
from jinja2 import Environment, select_autoescape
from datetime import datetime

from objective_utils import extract_project_metadata

BASE_DIR = Path(__file__).resolve().parents[2]
DEFAULT_JSON = BASE_DIR / "domain" / "projeto_migracao" / "projeto_migracao.json"
OUTPUT_FILE = BASE_DIR / "rendering" / "html" / "projeto_migracao.html"

REQUIRED_STATUS = {"documentation", "migration_project", "export", "deploy", "validation"}
SPECIAL_GROUP_IDS = {"SEM_GRUPO", "GROUP_0", "IGNORADOS"}

def format_date_br(date_str):
    """Converte data para formato brasileiro DD/MM/YYYY"""
    if not date_str:
        return date_str
    try:
        # Tenta parsear no formato YYYY-MM-DD
        date_obj = datetime.strptime(str(date_str), "%Y-%m-%d")
        return date_obj.strftime("%d/%m/%Y")
    except (ValueError, TypeError):
        # Se falhar, retorna a string original
        return date_str

TEMPLATE_HTML = r"""
<!doctype html>
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
    <link rel="stylesheet" href="../assets/style.css" />
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

                {% if history and history|length > 0 %}
                <section class="change-history-page" aria-label="Histórico de Alterações">
                    <header class="change-history-page__header">
                        <h2 class="change-history-page__title">Histórico de Alterações</h2>
                    </header>
                    <div class="change-history-page__content">
                        <table role="table" aria-label="Histórico de alterações do projeto">
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
                {% endif %}
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

                                {% elif dt_key in ["CSV", "DB.XML"] %}
                                    <!-- CSV / DB.XML: Resp., Seq., Grupo, Descrição, Tabela OTM -->
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

                                {% elif dt_key == "ARQUIVO ZIP BI" %}
                                    <!-- ARQUIVO ZIP BI: Resp., Seq., Grupo, Descrição, Tabela OTM -->
                                    <table class="meta-table meta-table--roadmap" role="table" aria-label="Objetos ARQUIVO ZIP BI">
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

                                {% elif dt_key == "INTEGRATION" %}
                                    <!-- INTEGRATION: Resp., Seq., Grupo, Descrição, Tabela OTM -->
                                    <table class="meta-table meta-table--roadmap" role="table" aria-label="Objetos INTEGRATION">
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

                    <!-- Conteúdo Técnico -->
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

                    <!-- Query de Extração (apenas se for um campo independente) -->
                    {% if object.saved_query and object.saved_query.sql and object.saved_query.type != "extraction" %}
                    <section class="code-section code-section--query" aria-label="Query de extração">
                        <header class="code-section__header">
                            <h4 class="code-section__title">Query de Extração</h4>
                            <span class="code-section__lang">SQL</span>
                        </header>
                        <div class="code-section__content">
                            <pre class="code-block code-block--sql"><code class="language-sql">{{ object.saved_query.sql }}</code></pre>
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

    <script>
    // SQL Syntax Highlighting
    document.addEventListener('DOMContentLoaded', function() {
        document.querySelectorAll('.language-sql').forEach(function(block) {
            let code = block.textContent;
            
            // SQL Keywords
            const keywords = /\b(SELECT|FROM|WHERE|JOIN|LEFT|RIGHT|INNER|OUTER|ON|AND|OR|NOT|IN|EXISTS|LIKE|BETWEEN|IS|NULL|AS|GROUP BY|ORDER BY|HAVING|DISTINCT|COUNT|SUM|AVG|MAX|MIN|UNION|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP|TABLE|INDEX|VIEW|DATABASE|CASE|WHEN|THEN|ELSE|END)\b/gi;
            
            code = code.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
            
            // Highlight keywords
            code = code.replace(keywords, '<span class="keyword">$1</span>');
            
            // Highlight strings
            code = code.replace(/('([^'\\]|\\.)*')/g, '<span class="string">$1</span>');
            
            // Highlight numbers
            code = code.replace(/\b(\d+)\b/g, '<span class="number">$1</span>');
            
            // Highlight comments
            code = code.replace(/(--[^\n]*)/g, '<span class="comment">$1</span>');
            code = code.replace(/(\/\*[\s\S]*?\*\/)/g, '<span class="comment">$1</span>');
            
            block.innerHTML = code;
        });
    });
    </script>
</body>
</html>
""".lstrip()


def _normalize(data: dict) -> dict:
    project = dict(data.get("project", {}))
    project.setdefault("code", "")
    project.setdefault("name", "")
    project.setdefault("version", "")
    project.setdefault("consultant", "")
    project.setdefault("environment", {})
    project["environment"].setdefault("source", "")
    project["environment"].setdefault("target", "")

    groups = []
    for group in data.get("groups", []):
        group_id = str(group.get("group_id") or "").strip().upper()
        if group_id in SPECIAL_GROUP_IDS:
            continue

        objects = []
        for obj in group.get("objects", []):
            obj = dict(obj)
            obj.setdefault("identifiers", {})
            obj.setdefault("technical_content", {})
            obj.setdefault("status", {})
            obj.setdefault("otm_table", "")
            obj.setdefault("migration_type", "")
            obj.setdefault("description", "")
            obj.setdefault("responsible", "")
            obj.setdefault("deployment_type", "")
            obj.setdefault("object_type", "")
            obj.setdefault("notes", "")
            obj.setdefault("sequence", "")
            obj.setdefault("name", "")
            
            # Não gerar automaticamente saved_query a partir de technical_content
            # Deixar saved_query apenas para campos independentes no JSON
            obj.setdefault("technical_content", {})
            obj.setdefault("saved_query", None)
            
            objects.append(obj)

        group = dict(group)
        label = group.get("label") or group.get("group_name") or group.get("name", "")
        group["label"] = label
        group["name"] = label
        group.setdefault("description", "")
        group["objects"] = objects
        groups.append(group)

    project_metadata = extract_project_metadata(data)

    # Defaults e parágrafos para blocos de grupo
    go = project_metadata.get("groups_overview", {}) or {}
    if "title" not in go or not go.get("title"):
        go["title"] = "Grupos e Objetos de Migração OTM"
    if "description" not in go or not go.get("description"):
        go["description"] = "Esta seção apresenta os conjuntos de objetos do Oracle Transportation Management (OTM) contemplados no escopo de migração."

    def split_paragraphs(text: str):
        return [p.strip() for p in (text or "").split("\n\n") if p.strip()]

    go["paragraphs"] = split_paragraphs(go.get("description", ""))
    project_metadata["groups_overview"] = go

    for g in groups:
        g["description_paragraphs"] = split_paragraphs(g.get("description", ""))

    return {"project": project, "groups": groups, "project_metadata": project_metadata}


def _validate_status(data: dict) -> None:
        for group in data.get("groups", []):
                for obj in group.get("objects", []):
                        status = obj.get("status", {})
                        if not REQUIRED_STATUS.issubset(status.keys()):
                                missing = sorted(REQUIRED_STATUS - set(status.keys()))
                                raise ValueError(f"Status incompleto em objeto '{obj.get('name', '')}': faltando {missing}")


def render(json_path: Path):
        raw = json.loads(json_path.read_text(encoding="utf-8"))
        data = _normalize(raw)
        _validate_status(data)

        env = Environment(autoescape=select_autoescape(enabled_extensions=("html", "xml")))
        env.filters['format_date_br'] = format_date_br
        template = env.from_string(TEMPLATE_HTML)
        html_output = template.render(data=data)

        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_FILE.write_text(html_output, encoding="utf-8")
        print(f"HTML gerado em: {OUTPUT_FILE}")

if __name__ == "__main__":
    import sys

    json_input = Path(sys.argv[1]) if len(sys.argv) == 2 else DEFAULT_JSON
    render(json_input)
