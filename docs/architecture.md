# Arquitetura do OmniDeck

## Entidades de Domínio

### Projeto de Migração

#### Papel
O Projeto de Migração é a entidade orquestradora do OmniDeck.
Ele governa o escopo, os objetos, as regras e o estado de uma migração OTM,
servindo como fonte única para documentação e acompanhamento.

---

#### Boundary — O que pertence

Pertencem ao Projeto de Migração:

- Identidade do projeto (código, nome, versão, responsável, ambientes)
- Grupos de objetos de migração
- Objetos de migração e seus atributos
- Tipos de deploy aplicáveis
- Status por fase da migração
- Regras de obrigatoriedade e consistência
- Estado consolidado do projeto
- Campos de texto livre explicativos (descrições, objetivos e observações)

---

#### Boundary — O que NÃO pertence

Não pertencem ao Projeto de Migração:

- HTML final
- PDF final
- Arquivos Markdown de renderização
- Cache técnico de objetos
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

## Validações de Domínio — Projeto de Migração

As validações a seguir são regras de domínio obrigatórias e devem ser
respeitadas por qualquer interface, automação ou script que interaja
com o schema canônico do Projeto de Migração.

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

### 2. Validações de Grupo

Campos obrigatórios:
- group_id (UPPER_SNAKE_CASE)
- label
- sequence (inteiro >= 1)

Regras:
- group_id deve ser único dentro do projeto
- sequence deve ser única dentro do projeto
- Grupos são ordenáveis pela propriedade sequence

---

### 3. Validações de Objeto (gerais)

Campos obrigatórios:
- sequence (inteiro >= 1)
- object_type (enum válido)
- otm_table
- deployment_type (enum válido)
- responsible

Regras:
- sequence deve ser única dentro do grupo
- otm_table deve existir na Metadata OTM
- identifiers deve ser um objeto válido

---

### 4. Validações condicionais por Deployment Type

- MANUAL  
  - Não permite identificadores técnicos

- MIGRATION_PROJECT  
  - Exige identifiers.migration_project_id

- CSV  
  - Exige identifiers.csv_file_name

- DB_XML  
  - Exige identifiers.db_xml_object_name

- ZIP_BI  
  - Exige identifiers.zip_bi_name

- BUILDER_CONTROL  
  - Exige identifiers.builder_control_id

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
- overall_status = DONE somente se todos os objetos estiverem com validation = DONE

---

## Princípios Arquiteturais

- O JSON canônico é a fonte única da verdade
- Markdown, HTML e PDF são artefatos derivados
- Texto livre nunca governa regra de negócio
- Enums governam valores fechados
- UI apenas consome e respeita o domínio
- Nenhuma regra de domínio depende de renderização