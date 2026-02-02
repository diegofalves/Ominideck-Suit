# {{ project.name }}

## Identificação do Projeto

- **Código**: {{ project.code }}
- **Versão**: {{ project.version }}
- **Consultor**: {{ project.consultant }}
- **Ambiente Origem**: {{ project.environment.source }}
- **Ambiente Destino**: {{ project.environment.target }}

---

{% for group in groups %}
{% if group.objects %}

## Grupo: {{ group.label }} ({{ loop.index }}º)

Sequência do Grupo: **{{ group.sequence }}**

{% for object in group.objects %}

### Objeto {{ loop.index }} — {{ object.type }}

- **Sequência**: {{ object.sequence }}
- **Tipo de Deploy**: {{ object.deployment_type }}
- **Responsável**: {{ object.responsible }}

#### Identificadores

{% if object.type == "SAVED_QUERY" %}
- Query Name: `{{ object.identifiers.query_name if object.identifiers and object.identifiers.query_name else "—" }}`

{% elif object.type == "AGENT" %}
- Agent GID: `{{ object.identifiers.agent_gid if object.identifiers and object.identifiers.agent_gid else "—" }}`

{% elif object.type == "TABLE" %}
- Table Name: `{{ object.identifiers.table_name if object.identifiers and object.identifiers.table_name else "—" }}`

{% elif object.type == "FINDER_SET" %}
- Finder Set GID: `{{ object.identifiers.finder_set_gid if object.identifiers and object.identifiers.finder_set_gid else "—" }}`

{% elif object.type == "RATE" %}
- Rate Offering GID: `{{ object.identifiers.rate_offering_gid if object.identifiers and object.identifiers.rate_offering_gid else "—" }}`

{% elif object.type == "EVENT_GROUP" %}
- Event Group GID: `{{ object.identifiers.event_group_gid if object.identifiers and object.identifiers.event_group_gid else "—" }}`

{% endif %}

#### Status de Progressão

| Fase | Status |
|------|--------|
| 📋 Documentação | {{ object.status.documentation }} |
| 🔧 Migration Project | {{ object.status.migration_project }} |
| 📤 Exportação | {{ object.status.export }} |
| 🚀 Deploy | {{ object.status.deploy }} |
| ✅ Validação | {{ object.status.validation }} |

{% if object.notes %}

#### Observações

{{ object.notes }}

{% endif %}

{% endfor %}

---

{% endif %}
{% endfor %}
