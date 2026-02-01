# {{ project.name }}

## Identificação do Projeto
- Código: {{ project.code }}
- Versão: {{ project.version }}
- Consultor: {{ project.consultant }}
- Ambiente Origem: {{ project.environment.source }}
- Ambiente Destino: {{ project.environment.target }}

## Descrição
{{ project.description }}

## Objetivo
{{ project.objective }}

## Observações Gerais
{{ project.general_notes }}

{% for group in groups %}
## Grupo: {{ group.label }}
{{ group.description }}

{% for object in group.objects %}
### {{ object.object_type }} — {{ object.otm_table }}

- Sequência: {{ object.sequence }}
- Tipo de Deploy: {{ object.deployment_type }}
- Responsável: {{ object.responsible }}

#### Status
- Documentação: {{ object.status.documentation }}
- Migration Project: {{ object.status.migration_project }}
- Exportação: {{ object.status.export }}
- Deploy: {{ object.status.deploy }}
- Validação: {{ object.status.validation }}

#### Observações Técnicas
{{ object.notes }}

{% endfor %}
{% endfor %}
