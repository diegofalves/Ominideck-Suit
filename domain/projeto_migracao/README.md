# Projeto de Migração

Este domínio representa o Projeto de Migração no OmniDeck.

O Projeto de Migração é a entidade orquestradora do sistema,
responsável por governar o escopo, os objetos, as regras e o estado
de uma migração OTM.

Nenhum artefato de renderização, UI ou cache pertence a este domínio.

## Catalogo de elegibilidade para Migration Project

O arquivo canonico para definir quais tabelas devem nascer com
`deployment_type = MIGRATION_PROJECT` e:

- `metadata/otm/migration_project_eligible_tables.json`

Regras:

- Se a tabela estiver no catalogo (e dominio permitido, quando informado),
  objetos `auto_generated` sao criados/normalizados como `MIGRATION_PROJECT`.
- Se a tabela nao estiver no catalogo, o fallback e vazio (`""`), para
  definicao manual pelo usuario.
- O catalogo atual contem a lista fornecida pelo projeto e pode ser revisado
  sempre que houver alteracoes de estrategia.

Validacao recomendada antes de publicar a lista final:

- `python3 infra/validate_migration_project_eligible_tables.py`
