# {{ data.project.name }}

## Identificação do Projeto

- **Código**: {{ data.project.code }}
- **Versão**: {{ data.project.version }}
- **Consultor**: {{ data.project.consultant }}
- **Ambiente Origem**: {{ data.project.environment.source }}
- **Ambiente Destino**: {{ data.project.environment.target }}

---

## Sumário

- Grupos e Objetos de Migração OTM
{% for group in data.groups %}
  - Grupo: {{ group.label }}
  {% for object in group.objects %}
    - {{ object.name }}
  {% endfor %}
{% endfor %}

---

{% if data.project_metadata.migration_objective.content %}
## {{ data.project_metadata.migration_objective.title }}

{% for line in data.project_metadata.migration_objective.content %}
{{ line }}

{% endfor %}

---
{% endif %}

{% set vc = data.project_metadata.version_control %}
{% if vc.current_version or vc.last_update or vc.author %}
## Controle de Versão

{% if vc.current_version %}**Versão Atual:** {{ vc.current_version }}{% endif %}{% if vc.last_update %}  
**Última Atualização:** {{ vc.last_update }}{% endif %}{% if vc.author %}  
**Autor:** {{ vc.author }}{% endif %}

---
{% endif %}

{% set history = data.project_metadata.change_history %}
{% if history and history|length > 0 %}
## Histórico de Alterações

| Data | Versão | Descrição | Autor |
|------|--------|-----------|--------|
{% for item in history %}
| {{ item.date }} | {{ item.version }} | {{ item.description }} | {{ item.author }} |
{% endfor %}

---
{% endif %}

## Roadmap de Migração

Este capítulo apresenta a estratégia de execução da migração, agrupada por tipo de implantação (Deployment Type). Cada bloco representa um grupo coeso de objetos que devem ser migrados seguindo a mesma tática operacional.

{% set deployment_types = {} %}
{% for group in data.groups %}
{% for object in group.objects %}
{% set dt = object.deployment_type or "INDEFINIDO" %}
{% if dt not in deployment_types %}
{% set _ = deployment_types.update({dt: []}) %}
{% endif %}
{% set _ = deployment_types[dt].append(object.name) %}
{% endfor %}
{% endfor %}

{% for dt_name in ["MANUAL", "MIGRATION_PROJECT", "CSV", "DB.XML", "ARQUIVO ZIP BI"] %}
{% if dt_name in deployment_types %}
### {{ dt_name }}

{% if dt_name == "MANUAL" %}
Implantação manual no ambiente de destino. Objetos que requerem ação humana direta e validação específica.
{% elif dt_name == "MIGRATION_PROJECT" %}
Migração via projeto de migração nativo do OTM. Objetos transportados com configurações relacionadas.
{% elif dt_name == "CSV" %}
Importação via arquivos CSV. Dados estruturados em formato de valores separados por vírgula.
{% elif dt_name == "DB.XML" %}
Migração via banco de dados e arquivos XML. Transportação com integridade de relacionamentos.
{% elif dt_name == "ARQUIVO ZIP BI" %}
Exportação para arquivo ZIP com conteúdo BI. Inclui dashboards, relatórios e visualizações.
{% endif %}

**Objetos nesta estratégia:** {{ deployment_types[dt_name] | length }}

{% for obj_name in deployment_types[dt_name] %}
- {{ obj_name }}
{% endfor %}

---

{% endif %}
{% endfor %}

## Grupos e Objetos de Migração OTM

Esta seção apresenta os conjuntos de objetos do Oracle Transportation Management (OTM) contemplados no escopo de migração.

---

{% for group in data.groups %}
### Grupo: {{ group.label }}

{% if group.description %}
{{ group.description }}

{% endif %}

{% for object in group.objects %}
### {{ object.name }}

{{ object.description }}

<div class="meta-text" markdown="1">
**Sequência:** {{ object.sequence }}
**Object Type:** {{ object.object_type }}
**OTM Table:** {{ object.otm_table }}
**Deployment Type:** {{ object.deployment_type }}
{% if object.identifiers.migration_project_id %}
**Migration Project ID:** {{ object.identifiers.migration_project_id }}
{% endif %}
{% for key, value in object.identifiers.items() if key != 'migration_project_id' %}
**{{ key.replace('_', ' ') | title }}:** {{ value }}
{% endfor %}
**Responsável:** {{ object.responsible }}
{% if object.notes %}
**Notas:** {{ object.notes }}
{% endif %}

**Documentação:** {{ object.status.documentation }}
**Migration Project:** {{ object.status.migration_project }}
**Exportação:** {{ object.status.export }}
**Deploy:** {{ object.status.deploy }}
**Validação:** {{ object.status.validation }}
</div>

{% if object.object_extraction_query and object.object_extraction_query.content %}
### Query de Extração de Objetos
```{{ object.object_extraction_query.language | lower }}
{{ object.object_extraction_query.content }}
```
{% endif %}

{% if object.technical_content and object.technical_content.content %}
### Conteúdo Técnico
```{{ object.technical_content.type | lower }}
{{ object.technical_content.content }}
```
{% endif %}

{% endfor %}
{% endfor %}
