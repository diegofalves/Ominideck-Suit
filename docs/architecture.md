# Arquitetura do OmniDeck

## Referências Operacionais

- Runbook de extrações OTM: `docs/otm_extraction_runbook.md`

## Visão Geral

O OmniDeck é construído seguindo princípios de **Domain-Driven Design (DDD)**.
O **Documento de Migração** é o *Aggregate Root* do sistema e representa a fonte única
da verdade para qualquer migração OTM.

Interfaces (UI Web, CLI futura), parsers e renderizadores (Markdown, HTML, PDF)
são considerados **adapters** e nunca contêm regras de negócio.

## Entidades de Domínio

### Documento de Migração

#### Papel
O Documento de Migração é a entidade orquestradora do OmniDeck.
Ele governa o escopo, os MIGRATION_ITEMs, as regras e o estado de uma migração OTM,
servindo como fonte única para documentação e acompanhamento.

Vocabulário canônico:
- MIGRATION_GROUP: agrupador lógico de execução dentro do projeto.
- MIGRATION_ITEM: item de migração vinculado a um MIGRATION_GROUP e a uma tabela OTM.
- OTM_OBJECT: cada linha retornada pelas queries de extração no OTM.

---

#### Boundary — O que pertence

Pertencem ao Documento de Migração:

- Identidade do projeto (código, nome, versão, responsável, ambientes)
- MIGRATION_GROUPs
- MIGRATION_ITEMs e seus atributos
- Tipos de deploy aplicáveis
- Status por fase da migração
- Regras de obrigatoriedade e consistência
- Estado consolidado do projeto
- Campos de texto livre explicativos (descrições, objetivos e observações)

---

#### Boundary — O que NÃO pertence

Não pertencem ao Documento de Migração:

- HTML final
- PDF final
- Arquivos Markdown de renderização
- Cache técnico de MIGRATION_ITEMs
- Scripts de extração ou parsing
- Lógica de UI
- Detalhes visuais ou de layout

Esses elementos são artefatos derivados ou infraestrutura.

---

#### Relação com outros domínios

- Consome Metadata OTM como referência (somente leitura)
- Gera documentos técnicos e relatórios como saída
- Não modifica metadata global

---

## Validações de Domínio — Documento de Migração

As validações a seguir são regras de domínio obrigatórias e devem ser
respeitadas por qualquer interface, automação ou script que interaja
com o schema canônico do Documento de Migração.

### 1. Validações do Projeto (nível raiz)

Campos obrigatórios:
- project.code
- project.name
- project.version
- project.environment.source
- project.environment.target

Regras:
- project.environment.source deve ser diferente de project.environment.target
- project.code deve ser único no escopo do repositório

---

### 2. Validações de MIGRATION_GROUP

Campos obrigatórios:
- label
- sequence (inteiro >= 1)

Regras:
- sequence deve ser única dentro do projeto
- MIGRATION_GROUPs são ordenáveis pela propriedade sequence

---

### 3. Validações de MIGRATION_ITEM (gerais)

Campos obrigatórios:
- sequence (inteiro >= 1)
- object_type (enum válido)
- deployment_type (enum válido)
- identifiers deve ser uma estrutura válida

Regras:
- sequence deve ser única dentro do MIGRATION_GROUP
- otm_table deve existir na Metadata OTM
- MIGRATION_ITEMs auto_generated devem aplicar deployment_type com base no catalogo
  metadata/otm/migration_project_eligible_tables.json (fallback vazio)

---

### 4. Validações condicionais por Tipo de MIGRATION_ITEM

Cada tipo de MIGRATION_ITEM exige identificadores específicos:

- SAVED_QUERY  
  - identifiers.query_name

- AGENT  
  - identifiers.agent_gid

- TABLE  
  - identifiers.table_name

- FINDER_SET  
  - identifiers.finder_set_gid

- RATE  
  - identifiers.rate_offering_gid

- EVENT_GROUP  
  - identifiers.event_group_gid

---

### 5. Validações de Status

Campos obrigatórios:
- documentation
- migration_project
- export
- deploy
- validation

Regras:
- Todos os status devem pertencer ao enum status
- Uma fase não pode estar em DONE se a fase anterior não estiver em DONE

Status inicial padrão:
- Todas as fases iniciam em PENDING

---

### 6. Validações de Estado do Projeto

Campos obrigatórios:
- state.overall_status (enum válido)

Regras:
- overall_status pode ser calculado ou definido manualmente
- overall_status = DONE somente se todos os MIGRATION_ITEMs estiverem com validation = DONE

---

## Princípios Arquiteturais

- O JSON canônico é a fonte única da verdade
- Markdown, HTML e PDF são artefatos derivados
- Texto livre nunca governa regra de negócio
- Enums governam valores fechados
- UI apenas consome e respeita o domínio
- Nenhuma regra de domínio depende de renderização

---

## Estado Atual da Arquitetura

- UI Web implementada (Flask + HTML + JS)
- Parser form → domain canônico
- Validação de domínio centralizada
- Persistência via Repository Pattern (JSON)
- Renderização Markdown funcional
- HTML/PDF como próximos adapters
- CLI planejada como adapter futuro
