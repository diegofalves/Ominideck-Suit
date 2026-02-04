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

{% if data.project_metadata.migration_objective.blocks %}
## {{ data.project_metadata.migration_objective.title }}

{% for block in data.project_metadata.migration_objective.blocks %}
{% if block.type == "paragraph" %}
{{ block.text }}

{% elif block.type == "list" %}
{% for item in block["items"] %}
- {{ item }}
{% endfor %}

{% endif %}
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
**Tipo de Migração:** {{ object.migration_type }}
{% if object.notes %}
**Notas:** {{ object.notes }}
{% endif %}

**Documentação:** {{ object.status.documentation }}
**Migration Project:** {{ object.status.migration_project }}
**Exportação:** {{ object.status.export }}
**Deploy:** {{ object.status.deploy }}
**Validação:** {{ object.status.validation }}
</div>

{% if object.technical_content and object.technical_content.content %}
**Conteúdo Técnico:**
```{{ object.technical_content.type | lower }}
{{ object.technical_content.content }}
```
{% endif %}

{% if object.saved_query %}
### Query de Extração
```sql
{{ object.saved_query.sql }}
```
{% endif %}

{% endfor %}
{% endfor %}
