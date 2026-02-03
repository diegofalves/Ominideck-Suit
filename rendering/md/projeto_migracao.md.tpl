# {{ data.project.name }}

## Identificação do Projeto

- **Código**: {{ data.project.code }}
- **Versão**: {{ data.project.version }}
- **Consultor**: {{ data.project.consultant }}
- **Ambiente Origem**: {{ data.project.environment.source }}
- **Ambiente Destino**: {{ data.project.environment.target }}

---

{% for group in data.groups %}
## {{ group.name }}

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
