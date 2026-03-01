documento_codigo: MIG0001
documento_nome: "Documento de Migração - Configuração OTM Unificada (BR100 + Projeto)"
tipo_documento: PROJETO_MIGRACAO
versao: "1.1"
data_geracao: "18 de janeiro de 2026"
ultima_atualizacao: "02 de fevereiro de 2026"
consultor_responsavel: "Diego Ferreira Alves"
ambiente_origem: "https://otmgtm-dev1-bauducco.otmgtm.us-phoenix-1.ocs.oraclecloud.com/"
ambiente_destino: "https://otmgtm-bauducco.otmgtm.us-phoenix-1.ocs.oraclecloud.com/"

## Capa

| Campo | Informação |
|-------|------------|
| Documento Código | MIG0001 |
| Documento Nome | Documento de Migração - Configuração OTM Unificada (BR100 + Projeto) |
| Versão | 1.1 |
| Data de Geração | 18 de janeiro de 2026 |
| Última Atualização | 02 de February de 2026 |
| Consultor Responsável | Diego Ferreira Alves |

---

## Objetivo do Documento de Migração

<div class="objetivo-container" markdown="1">
Este projeto tem como objetivo executar a migração controlada e governada das configurações do Oracle Transportation Management (OTM), atualmente consolidadas e validadas no ambiente de homologação (HOM), para o ambiente de produção (PRD).

A migração visa unificar e padronizar o conjunto de objetos de configuração definidos no baseline BR100, incorporando também ajustes e extensões específicas do projeto Bauducco, garantindo consistência funcional, estabilidade operacional e aderência às melhores práticas de governança do OTM.

Com a execução desta migração em PROD, espera-se:
- disponibilizar integralmente as configurações necessárias para o planejamento, execução e monitoramento logístico;
- eliminar divergências entre ambientes que possam impactar comportamento de planejamento, rating, integração ou visibilidade operacional;
- assegurar rastreabilidade, capacidade de rollback e validação pós-migração, reduzindo riscos de impacto nas operações produtivas.
</div>

---

## Controle de versão

| Versão | Data | Autor | Descrição |
|--------|------|-------|-----------|
| 1.3 | 28/01/2026 | Diego Ferreira Alves | Remoção do ícone de diamante das seções da tabela de roadmap e publicação do novo agrupamento de tipos de deploy (MANUAL, MIGRATION, CSV, DB.XML, ARQUIVO ZIP BI). |
| 1.2 | 27/01/2026 | Diego Ferreira Alves | Adoção do novo deploy type `BUILDER-CONTROL` e reforço na ordenação e no preenchimento automático das colunas da tabela `Migration Project`. |
| 1.1 | 21/01/2026 | Diego Ferreira Alves | Ajustes consolidados do painel de migração e da tabela Migration Project (tipos de deploy, colunas, links), reordenação dos objetos e atualização dos caches. |
| 1.0 | 18/01/2026 | Diego Ferreira Alves | Criação inicial do documento. |

---

## Histórico de alterações

| Data | Alteração | Motivo | Responsável |
|------|-----------|--------|-------------|
| 28/01/2026 | Removido o ícone “🔹” das headings que destacam cada tipo de deploy (MANUAL/MIGRATION/CSV/DB/XML/ARQUIVO ZIP BI) para harmonizar a renderização do HTML. | Tornar o painel e navegação menos dependentes de símbolos gráficos, mantendo os mesmos títulos e counts. | Diego Ferreira Alves |
| 27/01/2026 | Padronizado o preenchimento automático de colunas em `Migration Project` e reforçado o agrupamento dos tipos de deploy para as seções de Automação e Configuração. | Garantir que as tabelas reflitam corretamente o roadmap e facilitam futuras integrações (scripts/painel). | Diego Ferreira Alves |
| 21/01/2026 | Revisão geral do Documento de Migração: alinhamento dos tipos de deploy (Manual/Migration), atualização da tabela Migration Project, hiperlinks entre objetos e painel, e sincronização dos caches. | Incorporar as melhorias estruturais realizadas na iteração anterior e manter rastreabilidade da evolução. | Diego Ferreira Alves |
| 18/01/2026 | Criação inicial do Documento de Migração | Consolidação do template de migração e início do projeto de replicação para ambiente PROD | Diego Ferreira Alves |

---

## Roadmap de Migração

<div class="objetivo-container" markdown="1">
Este capítulo apresenta o **roadmap completo de migração**, mapeando todos os objetos OTM por estratégia de implantação.
</div>

{{TABLE_MIGRATION_PROJECT}}

---

## Grupos e Objetos de Migração OTM

Esta seção apresenta os **conjuntos de objetos do Oracle Transportation Management (OTM)** contemplados no escopo de migração.

### Grupo: Automação

Esta seção concentra os objetos responsáveis pela **execução automática de regras e fluxos operacionais no OTM**, como *Saved Queries*, *Conditions* e lógicas de acionamento utilizadas por *Agents* e processos batch.

O conteúdo evidencia como cada automação está associada a um **deploy type específico** (MANUAL, MIGRATION, CSV, DB.XML, ZIP BI), permitindo rastrear impactos da migração sobre fluxos automáticos, dependências técnicas e a **ordem correta de implantação** no roadmap do projeto.

A 

<div class="section-title">Saved Queries</div>

<div class="meta-text" markdown="1">
**Sequência:** 1
**OTM Table:** SAVED_QUERY
**Deployment Type:** Migration Project
**Migration Project ID:** BAU_MIG_OBJ_AUT
**Saved Query ID:** MIG_SAVED_QUERIES
**Responsável:** ITC
**Tipo de Migração:** Técnica
**Documentação:** Concluído
**Migration Project:** Concluído
**Exportação:** Concluído
**Deploy:** Concluído
**Validação:** Concluído

</div>
**Query de Extração:**
```sql
SELECT DOMAIN_NAME,
  SAVED_QUERY_XID,
  USER_QUERY_NAME,
  QUERY_NAME,
  USE_IN_FINDER,
  IS_CONDITION
FROM
  SAVED_QUERY
WHERE
  DOMAIN_NAME = 'BAU'
  AND SAVED_QUERY_GID NOT LIKE '%TEST%'
  AND SAVED_QUERY_GID NOT LIKE '%TESTE%'
  AND SAVED_QUERY_GID NOT LIKE '%MIG%'
  AND SAVED_QUERY_GID NOT LIKE '%TEMP%'
ORDER BY
  DOMAIN_NAME,
  USER_QUERY_NAME,
  SAVED_QUERY_XID
```
**Resultado da Extração:**

{{TABLE_SAVED_QUERIES}}

---

<div class="section-title">Saved Conditions</div>

<div class="meta-text" markdown="1">
**Sequência:** 2
**OTM Table:** SAVED_CONDITION
**Deployment Type:** Migration Project
**Migration Project ID:** BAU_MIG_OBJ_AUT
**Saved Query ID:** MIG_SAVED_CONDITIONS
**Responsável:** ITC
**Tipo de Migração:** Técnica
**Documentação:** Concluído
**Migration Project:** Concluído
**Exportação:** Concluído
**Deploy:** Concluído
**Validação:** Concluído

</div>
**Query de Extração:**
```sql
SELECT SC.DOMAIN_NAME,
  SC.SAVED_CONDITION_XID,
  SC.QUERY_NAME,
  SC.USER_CONDITION_NAME,
  SCQ.SAVED_QUERY_GID,
  SC.OTM_RELEASE
FROM
  SAVED_CONDITION SC,
  SAVED_CONDITION_QUERY SCQ
WHERE
  SC.SAVED_CONDITION_GID = SCQ.SAVED_CONDITION_GID
  AND SC.DOMAIN_NAME = 'BAU'
  AND SC.SAVED_CONDITION_GID NOT LIKE '%TEST%'
  AND SC.SAVED_CONDITION_GID NOT LIKE '%TESTE%'
  AND SC.SAVED_CONDITION_GID NOT LIKE '%MIG%'
  AND SC.SAVED_CONDITION_GID NOT LIKE '%TEMP%'
ORDER BY
  SC.DOMAIN_NAME,
  SC.SAVED_CONDITION_XID,
  SCQ.SAVED_QUERY_GID
```
**Resultado da Extração:**

{{TABLE_SAVED_CONDITIONS}}

---

<div class="section-title">Data Type Association</div>

<div class="meta-text" markdown="1">
**Sequência:** 3
**OTM Table:** DATA_TYPE_ASSOCIATION
**Deployment Type:** Migration Project
**Migration Project ID:** BAU_MIG_OBJ_AUT
**Saved Query ID:** MIG_DATA_TYPE_ASSOCIATIONS
**Responsável:** ITC
**Tipo de Migração:** Técnica
**Documentação:** Concluído
**Migration Project:** Concluído
**Exportação:** Concluído
**Deploy:** Concluído
**Validação:** Concluído

</div>
**Query de Extração:**
```sql
SELECT
  DOMAIN_NAME,
  DATA_TYPE_ASSOCIATION_GID,
  DATA_TYPE_ASSOCIATION_XID,
  IS_PRIMARY,
  FROM_DATA_QUERY_TYPE_GID,
  TO_DATA_QUERY_TYPE_GID,
  ASSOCIATION_QUERY,
  JAVA_PLUGIN_GID,
  OTM_RELEASE
FROM
  DATA_TYPE_ASSOCIATION
WHERE
  DOMAIN_NAME = 'BAU'
ORDER BY
  DATA_TYPE_ASSOCIATION_XID
```
**Resultado da Extração:**

{{TABLE_DATA_TYPE_ASSOCIATION}}

---

<div class="section-title">Agent Event</div>

<div class="meta-text" markdown="1">
**Sequência:** 4
**OTM Table:** AGENT_EVENT
**Deployment Type:** Migration Project
**Migration Project ID:** BAU_MIG_OBJ_AUT
**Saved Query ID:** MIG_AGENT_EVENTS
**Responsável:** ITC
**Tipo de Migração:** Técnica
**Documentação:** Concluído
**Migration Project:** Concluído
**Exportação:** Concluído
**Deploy:** Concluído
**Validação:** Concluído

</div>
**Query de Extração:**
```sql
SELECT ae.DOMAIN_NAME,
  ae.AGENT_EVENT_GID,
  ae.AGENT_EVENT_XID,
  ae.DATA_QUERY_TYPE_GID,
  ae.NOTIFY_SUBJECT_GID,
  ae.AGENT_EVENT_PARENT,
  ae.EVENT_TOPIC_CLASS,
  ae.IS_CUSTOM,
  ae.IS_LIFETIME_MOD,
  ae.DESCRIPTION,
  ae.OTM_RELEASE,
  aed.AGENT_GID,
  a.AGENT_XID,
  a.IS_ACTIVE
FROM
  AGENT_EVENT ae,
  AGENT_EVENT_DETAILS aed,
  AGENT a
WHERE
  ae.AGENT_EVENT_GID = aed.AGENT_EVENT_GID
  AND aed.AGENT_GID = a.AGENT_GID
  AND ae.DOMAIN_NAME = 'BAU'
  AND a.IS_ACTIVE = 'Y'
ORDER BY
  ae.DATA_QUERY_TYPE_GID,
  ae.AGENT_EVENT_XID,
  a.AGENT_XID
```
**Resultado da Extração:**

{{TABLE_AGENT_EVENT}}

---

<div class="section-title">Agents</div>

<div class="meta-text" markdown="1">
**Sequência:** 5
**OTM Table:** AGENT
**Deployment Type:** Migration Project
**Migration Project ID:** BAU_MIG_OBJ_AUT
**Saved Query ID:** MIG_AGENTS
**Responsável:** ITC
**Tipo de Migração:** Técnica
**Documentação:** Concluído
**Migration Project:** Concluído
**Exportação:** Concluído
**Deploy:** Concluído
**Validação:** Concluído

</div>
**Query de Extração:**
```sql
SELECT
  DOMAIN_NAME,
  ACTION_GID,
  ACTION_XID,
  LABEL_KEY,
  DISPLAY_IGNORE_CRITERIA,
  ACTION_DEF_GID,
  APP_ACTION_GID,
  MANAGER_LAYOUT_GID,
  IS_LONG_RUNNING_TASK,
  LRT_INTERRUPTABILITY,
  LRT_INTERRUPT_ON_SQL,
  LRT_OBJECT_COUNT_THRESHOLD,
  OPT_FEATURE_GID,
  OTM_RELEASE,
  RESULT_MESSAGE_TEXT,
  RESULT_AUTOCLOSE_TIMEOUT,
  DEFAULT_LOG_PROFILE_GID,
  INSERT_USER,
  INSERT_DATE,
  UPDATE_USER,
  UPDATE_DATE
FROM
  ACTION
WHERE
  DOMAIN_NAME = 'BAU'
ORDER BY
  ACTION_XID
```
**Resultado da Extração:**

{{TABLE_AGENTS}}

---

<div class="section-title">App Actions</div>

<div class="meta-text" markdown="1">
**Sequência:** 6
**OTM Table:** APP_ACTION
**Deployment Type:** Migration Project
**Migration Project ID:** BAU_MIG_OBJ_AUT
**Saved Query ID:** MIG_APP_ACTIONS
**Responsável:** ITC
**Tipo de Migração:** Técnica
**Documentação:** Concluído
**Migration Project:** Concluído
**Exportação:** Concluído
**Deploy:** Concluído
**Validação:** Concluído

</div>
**Query de Extração:**
```sql
SELECT
  DOMAIN_NAME,
  ACTION_GID,
  ACTION_XID,
  LABEL_KEY,
  DISPLAY_IGNORE_CRITERIA,
  ACTION_DEF_GID,
  APP_ACTION_GID,
  MANAGER_LAYOUT_GID,
  IS_LONG_RUNNING_TASK,
  LRT_INTERRUPTABILITY,
  LRT_INTERRUPT_ON_SQL,
  LRT_OBJECT_COUNT_THRESHOLD,
  OPT_FEATURE_GID,
  OTM_RELEASE,
  RESULT_MESSAGE_TEXT,
  RESULT_AUTOCLOSE_TIMEOUT,
  DEFAULT_LOG_PROFILE_GID,
  INSERT_USER,
  INSERT_DATE,
  UPDATE_USER,
  UPDATE_DATE
FROM
  APP_ACTION
WHERE
  DOMAIN_NAME = 'BAU'
ORDER BY
  ACTION_XID
```
**Resultado da Extração:**

{{TABLE_APP_ACTIONS}}

---

<div class="section-title">Actions</div>

<div class="meta-text" markdown="1">
**Sequência:** 7
**OTM Table:** ACTION
**Deployment Type:** Migration Project
**Migration Project ID:** BAU_MIG_OBJ_AUT
**Saved Query ID:** MIG_AGENT_ACTIONS
**Responsável:** ITC
**Tipo de Migração:** Técnica
**Documentação:** Concluído
**Migration Project:** Concluído
**Exportação:** Concluído
**Deploy:** Concluído
**Validação:** Concluído

</div>
**Query de Extração:**
```sql
SELECT
  DOMAIN_NAME,
  STYLESHEET_CONTENT_GID,
  STYLESHEET_CONTENT_XID,
  USED_FOR_VIEW,
  USED_FOR_EDIT,
  MEDIA_TYPE
FROM
  STYLESHEET_CONTENT
WHERE
  DOMAIN_NAME = 'BAU'
```
**Resultado da Extração:**

{{TABLE_ACTIONS}}

---

<div class="section-title">Batch Processes</div>

<div class="meta-text" markdown="1">
**Sequência:** 8
**OTM Table:** BATCH_PROCESS
**Deployment Type:** Migration Project
**Migration Project ID:** BAU_MIG_OBJ_AUT
**Saved Query ID:** MIG_BATCH_PROCS
**Responsável:** ITC
**Tipo de Migração:** Técnica
**Documentação:** Concluído
**Migration Project:** Concluído
**Exportação:** Concluído
**Deploy:** Concluído
**Validação:** Concluído

</div>
**Query de Extração:**
```sql
SELECT
  BP.DOMAIN_NAME,
  BP.BATCH_PROCESS_XID,
  BP.DESCRIPTION,
  BP.IS_ENABLED,
  BPD.SEQUENCE_NO,
  BPD.TOPIC_ALIAS_GID
FROM
  BATCH_PROCESS BP,
  BATCH_PROCESS_D BPD
WHERE
  BP.BATCH_PROCESS_GID = BPD.BATCH_PROCESS_GID
  AND BP.IS_ENABLED = 'Y'
ORDER BY
  BP.DOMAIN_NAME,
  BP.BATCH_PROCESS_XID,
  BPD.SEQUENCE_NO
```
**Resultado da Extração:**

{{TABLE_BATCH_PROCESSES}}

---

### Grupo: Configuração

Esta seção descreve os atributos relevantes para migração, bem como as **dependências entre configurações**, assegurando que os objetos sejam implantados de forma consistente, segura e alinhada às regras de negócio vigentes no ambiente destino.

Esses objetos formam a **base técnica** sobre a qual os demais processos do OTM são executados.

<div class="section-title">Domains – Add Domain</div>

<div class="meta-text" markdown="1">
**Sequência:** 1
**OTM Table:** DOMAIN
**Deployment Type:** Manual
**Migration Project ID:** **Saved
**Saved Query ID:** **Deployment
**Responsável:** ITC
**Tipo de Migração:** Técnica
**Documentação:** Concluído
**Migration Project:** Concluído
**Exportação:** Concluído
**Deploy:** Concluído
**Validação:** Concluído

</div>
**Query de Extração:**
```sql
SELECT * FROM DOMAIN
```
**Resultado da Extração:**

{{TABLE_DOMAINS_–_ADD_DOMAIN}}

---

<div class="section-title">Domain Grants</div>

<div class="meta-text" markdown="1">
**Sequência:** 1
**OTM Table:** DOMAIN_GRANTS_MADE
**Deployment Type:** Manual
**Migration Project ID:** **Saved
**Saved Query ID:** **Deployment
**Responsável:** ITC
**Tipo de Migração:** Técnica
**Documentação:** Concluído
**Migration Project:** N/A
**Exportação:** N/A
**Deploy:** Concluído
**Validação:** Concluído

</div>
**Query de Extração:**
```sql
SELECT
  GRANTOR_DOMAIN,
  GRANTEE_DOMAIN,
  TABLE_SET,
  IS_WRITE_ACCESS
FROM
  DOMAIN_GRANTS_MADE
ORDER BY
  GRANTOR_DOMAIN
```
**Resultado da Extração:**

{{TABLE_DOMAIN_GRANTS}}

---

<div class="section-title">Domain Settings</div>

<div class="meta-text" markdown="1">
**Sequência:** 1
**OTM Table:** DOMAIN_SETTING
**Deployment Type:** Manual
**Migration Project ID:** **Saved
**Saved Query ID:** **Deployment
**Responsável:** ITC
**Tipo de Migração:** Técnica
**Documentação:** Concluído
**Migration Project:** N/A
**Exportação:** N/A
**Deploy:** Concluído
**Validação:** Concluído

</div>
**Query de Extração:**
```sql
SELECT
  DOMAIN_NAME,
  'Y' AS IS_DEFAULT,
  PLANNING_PARAMETER_SET_GID,
  POSTAL_CODE_VALIDATE_TYPE,
  FUNCTIONAL_CURRENCY_GID
FROM
  DOMAIN_SETTING
ORDER BY
  DOMAIN_NAME
```
**Resultado da Extração:**

{{TABLE_DOMAIN_SETTINGS}}

---

<div class="section-title">Properties</div>

<div class="meta-text" markdown="1">
**Sequência:** 1
**OTM Table:** PROP_INSTRUCTION
**Deployment Type:** Manual
**Migration Project ID:** **Saved
**Saved Query ID:** **Deployment
**Responsável:** ITC
**Tipo de Migração:** Técnica
**Documentação:** Concluído
**Migration Project:** N/A
**Exportação:** N/A
**Deploy:** Concluído
**Validação:** Concluído

</div>
**Query de Extração:**
```sql
SELECT
  PROP_SEQUENCE_NUM,
  INSTRUCTION,
  KEY,
  VALUE,
  DESCRIPTION
FROM
  PROP_INSTRUCTION
WHERE
  PROP_INSTRUCTION_SET_GID = 'CUSTOM'
ORDER BY
  PROP_SEQUENCE_NUM
```
**Resultado da Extração:**

{{TABLE_PROPERTIES}}

---

<div class="section-title">Units of Measure (UOM)</div>

<div class="meta-text" markdown="1">
**Sequência:** 1
**OTM Table:** UOM
**Deployment Type:** Migration Project
**Migration Project ID:** BAU_MIG_OBJ_CONFIG
**Saved Query ID:** MIG_UOM
**Responsável:** ITC
**Tipo de Migração:** Técnica
**Documentação:** Concluído
**Migration Project:** Concluído
**Exportação:** Concluído
**Deploy:** Concluído
**Validação:** Concluído

</div>
**Query de Extração:**
```sql
SELECT
  DOMAIN_NAME,
  TYPE,
  UOM_CODE,
  UOM_SHORT_DESCRIPTION,
  UOM_LONG_DESCRIPTION,
  UOM_RANK,
  IS_STORAGE_DEFAULT,
  IS_DISPLAY_DEFAULT
FROM
  UOM
ORDER BY
  TYPE
```
**Resultado da Extração:**

{{TABLE_UNITS_OF_MEASURE_(UOM)}}

---

<div class="section-title">Postal Code Components</div>

<div class="meta-text" markdown="1">
**Sequência:** 0
**OTM Table:** HNAME_COMPONENT
**Deployment Type:** DB.XML
**Migration Project ID:** **Saved
**Saved Query ID:** **Deployment
**Responsável:** ITC
**Tipo de Migração:** Técnica
**Documentação:** Concluído
**Migration Project:** N/A
**Exportação:** Concluído
**Deploy:** Concluído
**Validação:** Concluído

</div>
**Query de Extração:**
```sql
SELECT * FROM HNAME_COMPONENT ORDER BY HNAME_COMPONENT_XID
```
**Resultado da Extração:**

{{TABLE_POSTAL_CODE_COMPONENTS}}

---

<div class="section-title">Branding</div>

<div class="meta-text" markdown="1">
**Sequência:** 0
**OTM Table:** 
**Deployment Type:** Manual
**Migration Project ID:** **Saved
**Saved Query ID:** **Deployment
**Responsável:** ITC
**Tipo de Migração:** Técnica
**Documentação:** Concluído
**Migration Project:** N/A
**Exportação:** N/A
**Deploy:** Concluído
**Validação:** Concluído

</div>
**Query de Extração:**
```sql
-- não aplicável
```
**Resultado da Extração:**

{{TABLE_BRANDING}}

---

<div class="section-title">Business Number</div>

<div class="meta-text" markdown="1">
**Sequência:** 3
**OTM Table:** BN_RULE
**Deployment Type:** Migration Project
**Migration Project ID:** BAU_MIG_OBJ_CONFIG
**Saved Query ID:** MIG_BUSINESS_NUMBER
**Responsável:** ITC
**Tipo de Migração:** Técnica
**Documentação:** Concluído
**Migration Project:** Concluído
**Exportação:** Concluído
**Deploy:** Concluído
**Validação:** Concluído

</div>
**Query de Extração:**
```sql
SELECT
  DOMAIN_NAME,
  BN_RULE_XID,
  BN_TYPE_GID,
  BN_GENERATOR_GID,
  RULE_DEFINITION,
  IS_DEFAULT,
  OTM_RELEASE
FROM
  BN_RULE
WHERE
  DOMAIN_NAME = 'BAU'
  AND BN_RULE_XID LIKE '%BAU%'
ORDER BY
  BN_RULE_XID
```
**Resultado da Extração:**

{{TABLE_BUSINESS_NUMBER}}

---

<div class="section-title">Reports</div>

<div class="meta-text" markdown="1">
**Sequência:** 4
**OTM Table:** REPORT
**Deployment Type:** Migration Project
**Migration Project ID:** BAU_MIG_OBJ_CONFIG
**Saved Query ID:** MIG_REPORTS
**Responsável:** ITC
**Tipo de Migração:** Técnica
**Documentação:** Concluído
**Migration Project:** Concluído
**Exportação:** Concluído
**Deploy:** Concluído
**Validação:** Concluído

</div>
**Query de Extração:**
```sql
SELECT
  DOMAIN_NAME,
  REPORT_GID,
  REPORT_XID,
  REPORT_DISPLAY_NAME,
  REPORT_DESC,
  REPORT_GROUP_GID,
  REPORT_PHYSICAL_NAME,
  SELECT_VIA_UI,
  ADDITIONAL_URL_ARGUMENTS,
  CAN_AUTO_GENERATE,
  SECURITY_LEVEL,
  REPORT_TYPE,
  IS_RPT_MGR_DISPLAY,
  USE_HTML_PARAMFORM,
  DEFAULT_DESFORMAT,
  REPORT_FROM_DB,
  ICON_GID,
  APP_ACTION_GID,
  TRANSACTIONAL_EVENT_GID,
  SEED_DATA,
  USE_PARAMS_AS_BIND,
  THIRD_PARTY_CONTENT_TYPE,
  USE_THIRD_PARTY_DISTRIBUTION,
  IS_CONSOLIDATED,
  REPORT_SYSTEM_GID,
  REPORT_PATH,
  USE_PARAM_OPERATORS,
  DATA_QUERY_TYPE_GID,
  OTM_RELEASE
FROM
  REPORT
WHERE
  DOMAIN_NAME = 'BAU'
ORDER BY
  REPORT_XID
```
**Resultado da Extração:**

{{TABLE_REPORTS}}

---

<div class="section-title">Transport Mode</div>

<div class="meta-text" markdown="1">
**Sequência:** 5
**OTM Table:** TRANSPORT_MODE
**Deployment Type:** Migration Project
**Migration Project ID:** BAU_MIG_OBJ_CONFIG
**Saved Query ID:** MIG_TRANSPORT_MODE
**Responsável:** ITC
**Tipo de Migração:** Técnica
**Documentação:** Concluído
**Migration Project:** Concluído
**Exportação:** Concluído
**Deploy:** Concluído
**Validação:** Concluído

</div>
**Query de Extração:**
```sql
SELECT
  DOMAIN_NAME,
  TRANSPORT_MODE_GID,
  TRANSPORT_MODE_XID,
  TRANSPORT_MODE_NAME,
  TRANSPORT_MODE_QUALIFIER,
  PERFORM_SHIPPING_SPACE_CALC,
  COLOR,
  IS_MASTER_CARR_REF_REM_VISIBLE,
  CONDITIONAL_BOOKING_PROF_GID,
  IS_CONSIDER_COST,
  THU_PROFILE_GID,
  MODE_TYPE,
  X12_FORMAT_CODE,
  ALLOW_REPACK
FROM
  TRANSPORT_MODE
WHERE
  DOMAIN_NAME = 'BAU'
ORDER BY
  TRANSPORT_MODE_XID
```
**Resultado da Extração:**

{{TABLE_TRANSPORT_MODE}}

---

<div class="section-title">BN Named Range</div>

<div class="meta-text" markdown="1">
**Sequência:** 6
**OTM Table:** BN_NAMED_RANGE
**Deployment Type:** Migration Project
**Migration Project ID:** BAU_MIG_OBJ_CONFIG
**Saved Query ID:** MIG_BN_NAMED_RANGE
**Responsável:** ITC
**Tipo de Migração:** Técnica
**Documentação:** Concluído
**Migration Project:** Concluído
**Exportação:** Concluído
**Deploy:** Concluído
**Validação:** Concluído

</div>
**Query de Extração:**
```sql
SELECT
  DOMAIN_NAME,
  BN_NAMED_RANGE_GID,
  BN_NAMED_RANGE_XID,
  RECYCLING_POLICY,
  USE_BN_CONTEXT
FROM
  BN_NAMED_RANGE
WHERE
  DOMAIN_NAME = 'BAU'
ORDER BY
  BN_NAMED_RANGE_XID
```
**Resultado da Extração:**

{{TABLE_BN_NAMED_RANGE}}

---

### Grupo: Dados Mestres

esta seção está na **consistência dos dados**, na integridade referencial entre objetos e na definição dos **ciclos de atualização**, garantindo que informações críticas permaneçam válidas e sincronizadas após a migração.

Falhas nesse grupo podem gerar impactos transversais em planejamento, execução, tarifação e integração.

<div class="section-title">Commodities</div>

<div class="meta-text" markdown="1">
**Sequência:** 1
**OTM Table:** COMMODITY
**Deployment Type:** Migration Project
**Migration Project ID:** BAU_MIG_OBJ_MESTRES
**Saved Query ID:** MIG_COMMODITIES
**Responsável:** ITC
**Tipo de Migração:** Técnica
**Documentação:** Concluído
**Migration Project:** Concluído
**Exportação:** Concluído
**Deploy:** Concluído
**Validação:** Concluído

</div>
**Query de Extração:**
```sql
SELECT
  DOMAIN_NAME,
  COMMODITY_GID,
  COMMODITY_XID,
  COMMODITY_NAME,
  COMMODITY_DESCRIPTION,
  REQ_EQPMT_GROUP_PROFILE_GID
FROM
  COMMODITY
WHERE
  DOMAIN_NAME = 'BAU'
  AND COMMODITY_GID IN (
    SELECT COMMODITY_GID FROM ITEM WHERE DOMAIN_NAME = 'BAU' AND COMMODITY_GID IS NOT NULL
  )
ORDER BY COMMODITY_XID
```
**Resultado da Extração:**

{{TABLE_COMMODITIES}}

---

<div class="section-title">Corporations</div>

<div class="meta-text" markdown="1">
**Sequência:** 2
**OTM Table:** CORPORATION
**Deployment Type:** Migration Project
**Migration Project ID:** BAU_MIG_OBJ_MESTRES
**Saved Query ID:** MIG_CORPORATIONS
**Responsável:** ITC
**Tipo de Migração:** Técnica
**Documentação:** Concluído
**Migration Project:** Concluído
**Exportação:** Concluído
**Deploy:** Concluído
**Validação:** Concluído

</div>
**Query de Extração:**
```sql
SELECT
  DOMAIN_NAME,
  CORPORATION_GID,
  CORPORATION_XID,
  CORPORATION_NAME,
  IS_DOMAIN_MASTER,
  IS_SHIPPING_AGENTS_ACTIVE,
  IS_ALLOW_HOUSE_COLLECT
FROM
  CORPORATION
WHERE
  DOMAIN_NAME = 'BAU'
ORDER BY
  CORPORATION_XID
```
**Resultado da Extração:**

{{TABLE_CORPORATIONS}}

---

<div class="section-title">Ship Unit Specs (THU)</div>

<div class="meta-text" markdown="1">
**Sequência:** 3
**OTM Table:** SHIP_UNIT_SPEC
**Deployment Type:** Migration Project
**Migration Project ID:** BAU_MIG_OBJ_MESTRES
**Saved Query ID:** MIG_THU_SPECS
**Responsável:** ITC
**Tipo de Migração:** Técnica
**Documentação:** Concluído
**Migration Project:** Concluído
**Exportação:** Concluído
**Deploy:** Concluído
**Validação:** Concluído

</div>
**Query de Extração:**
```sql
SELECT
  DOMAIN_NAME,
  SHIP_UNIT_SPEC_GID,
  SHIP_UNIT_SPEC_XID,
  SHIP_UNIT_SPEC_NAME,
  LENGTH,
  LENGTH_UOM_CODE,
  WIDTH,
  WIDTH_UOM_CODE,
  HEIGHT,
  HEIGHT_UOM_CODE,
  UNIT_TYPE,
  IS_IN_ON_MAX
FROM
  SHIP_UNIT_SPEC
WHERE
  DOMAIN_NAME = 'BAU'
  AND UNIT_TYPE = 'T'
ORDER BY
  SHIP_UNIT_SPEC_XID
```
**Resultado da Extração:**

{{TABLE_SHIP_UNIT_SPECS_(THU)}}

---

<div class="section-title">Service Providers</div>

<div class="meta-text" markdown="1">
**Sequência:** 0
**OTM Table:** SERVPROV
**Deployment Type:** CSV
**Responsável:** ITC
**Tipo de Migração:** Técnica
**Documentação:** Pendente
**Migration Project:** Pendente
**Exportação:** N/A
**Deploy:** Pendente
**Validação:** Pendente

</div>
**Query de Extração:**
```sql
SELECT
  S.SERVPROV_XID,
  S.ALLOW_TENDER,
  S.IS_FLEET,
  L.LOCATION_NAME,
  L.CITY,
  L.PROVINCE_CODE,
  L.POSTAL_CODE,
  L.COUNTRY_CODE3_GID,
  L.ZONE4,
  L.LAT,
  L.LON,
  L.DESCRIPTION,
  LR.LOCATION_REFNUM_QUAL_GID,
  LR.LOCATION_REFNUM_VALUE
FROM
  SERVPROV S,
  LOCATION L,
  LOCATION_REFNUM LR
WHERE
  S.SERVPROV_GID = L.LOCATION_GID
  AND L.LOCATION_GID = LR.LOCATION_GID
ORDER BY
  L.LOCATION_NAME
```
**Resultado da Extração:**

{{TABLE_SERVICE_PROVIDERS}}

---

<div class="section-title">Locations</div>

<div class="meta-text" markdown="1">
**Sequência:** 0
**OTM Table:** LOCATION
**Deployment Type:** Integração
**Migration Project ID:** **Saved
**Saved Query ID:** **Deployment
**Responsável:** ITC
**Tipo de Migração:** Técnica
**Documentação:** Pendente
**Migration Project:** N/A
**Exportação:** N/A
**Deploy:** Pendente
**Validação:** Pendente

</div>
**Query de Extração:**
```sql
SELECT
  L.DOMAIN_NAME,
  L.LOCATION_XID,
  L.LOCATION_NAME,
  L.CITY,
  L.PROVINCE_CODE,
  L.POSTAL_CODE,
  L.COUNTRY_CODE3_GID,
  L.ZONE4,
  L.LAT,
  L.LON,
  L.DESCRIPTION,
  LR.LOCATION_REFNUM_QUAL_GID,
  LR.LOCATION_REFNUM_VALUE
FROM
  LOCATION L,
  LOCATION_REFNUM LR
WHERE
  L.LOCATION_GID = LR.LOCATION_GID
ORDER BY
  L.LOCATION_NAME
```
**Resultado da Extração:**

{{TABLE_LOCATIONS}}

---

<div class="section-title">Contacts</div>

<div class="meta-text" markdown="1">
**Sequência:** 0
**OTM Table:** CONTACT
**Deployment Type:** CSV
**Responsável:** ITC
**Tipo de Migração:** Técnica
**Documentação:** Pendente
**Migration Project:** Pendente
**Exportação:** N/A
**Deploy:** Pendente
**Validação:** Pendente

</div>
**Query de Extração:**
```sql
SELECT
  C.DOMAIN_NAME,
  C.CONTACT_XID,
  C.FIRST_NAME,
  C.LAST_NAME,
  C.EMAIL_ADDRESS,
  C.PHONE1,
  C.LANGUAGE_SPOKEN,
  C.IS_PRIMARY_CONTACT,
  C.CONTACT_TYPE,
  C.LOCATION_GID,
  CCM.COM_METHOD_GID
FROM
  CONTACT C,
  CONTACT_COM_METHOD CCM
WHERE
  C.CONTACT_GID = CCM.CONTACT_GID
ORDER BY
  FIRST_NAME
```
**Resultado da Extração:**

{{TABLE_CONTACTS}}

---

<div class="section-title">Equipment Groups</div>

<div class="meta-text" markdown="1">
**Sequência:** 0
**OTM Table:** EQUIPMENT_GROUP
**Deployment Type:** CSV
**Responsável:** ITC
**Tipo de Migração:** Técnica
**Documentação:** Pendente
**Migration Project:** Pendente
**Exportação:** N/A
**Deploy:** Pendente
**Validação:** Pendente

</div>
**Query de Extração:**
```sql
SELECT
  EG.DOMAIN_NAME,
  EG.EQUIPMENT_GROUP_XID,
  EG.EQUIPMENT_GROUP_NAME,
  ROUND(EG.EFFECTIVE_WEIGHT,5) AS EFFECTIVE_WEIGHT,
  EG.EFFECTIVE_WEIGHT_UOM_CODE,
  ROUND(EG.EFFECTIVE_VOLUME,5) AS EFFECTIVE_VOLUME,
  EG.EFFECTIVE_VOLUME_UOM_CODE,
  ROUND(EG.WIDTH,5) AS WIDTH,
  EG.WIDTH_UOM_CODE,
  ROUND(EG.LENGTH,5) AS LENGTH,
  EG.LENGTH_UOM_CODE,
  ROUND(EG.HEIGHT,5) AS HEIGHT,
  EG.HEIGHT_UOM_CODE,
  EG.IS_CONTAINER,
  EG.ALLOW_LIFO_ONLY
FROM
  EQUIPMENT_GROUP EG
WHERE
  EG.DOMAIN_NAME = 'BAU'
ORDER BY
  EG.EQUIPMENT_GROUP_XID
```
**Resultado da Extração:**

{{TABLE_EQUIPMENT_GROUPS}}

---

<div class="section-title">Items</div>

<div class="meta-text" markdown="1">
**Sequência:** 0
**OTM Table:** ITEM
**Deployment Type:** Integração
**Migration Project ID:** **Saved
**Saved Query ID:** **Deployment
**Responsável:** ITC
**Tipo de Migração:** Técnica
**Documentação:** Pendente
**Migration Project:** N/A
**Exportação:** N/A
**Deploy:** Pendente
**Validação:** Pendente

</div>
**Query de Extração:**
```sql
SELECT
  ssp.DOMAIN_NAME,
  ssp.STYLESHEET_PROFILE_GID,
  ssp.STYLESHEET_PROFILE_XID,
  ssp.RAW_XML,
  ssp.FORMAT,
  ssp.SUBJECT_PROPKEY,
  ssp.OUT_XML_PROFILE_GID,
  ssp.DOCUMENT_ATTACH_TYPE,
  ssp.DIRECTION,
  ssp.TYPE,
  ssp.IS_FOR_NOTIFICATION_XML,
  ssp.IS_FOR_TRANSMISSION_XML,
  ssp.IS_FOR_MESSAGE_XML,
  ssp.CONTENT_GID,
  ssp.OTM_RELEASE
FROM
  STYLESHEET_PROFILE ssp
WHERE
  ssp.CONTENT_GID IN (
    SELECT
      sc.STYLESHEET_CONTENT_GID
    FROM
      STYLESHEET_CONTENT sc
    WHERE
      sc.DOMAIN_NAME = 'BAU'
  )
```
**Resultado da Extração:**

{{TABLE_ITEMS}}

---

<div class="section-title">Packaged Items</div>

<div class="meta-text" markdown="1">
**Sequência:** 0
**OTM Table:** PACKAGED_ITEM
**Deployment Type:** Integração
**Migration Project ID:** **Saved
**Saved Query ID:** **Deployment
**Responsável:** ITC
**Tipo de Migração:** Técnica
**Documentação:** Pendente
**Migration Project:** N/A
**Exportação:** N/A
**Deploy:** Pendente
**Validação:** Pendente

</div>
**Query de Extração:**
```sql
SELECT xt.DOMAIN_NAME,
  xt.XML_TEMPLATE_GID,
  xt.XML_TEMPLATE_XID,
  xt.USE_DATA,
  xt.DESCRIPTION,
  xt.GLOG_XML_ELEMENT_GID
FROM
  XML_TEMPLATE xt
WHERE
  xt.DOMAIN_NAME = 'BAU'
ORDER BY
  xt.XML_TEMPLATE_XID
```
**Resultado da Extração:**

{{TABLE_PACKAGED_ITEMS}}

---

<div class="section-title">Contact Groups</div>

<div class="meta-text" markdown="1">
**Sequência:** 0
**OTM Table:** CONTACT_GROUP
**Deployment Type:** CSV
**Migration Project ID:** N/A
**Saved Query ID:** **Deployment
**Responsável:** ITC
**Tipo de Migração:** Técnica
**Documentação:** Pendente
**Migration Project:** Pendente
**Exportação:** N/A
**Deploy:** Pendente
**Validação:** Pendente

</div>
**Query de Extração:**
```sql
SELECT
  DOMAIN_NAME,
  STYLESHEET_CONTENT_GID,
  STYLESHEET_CONTENT_XID,
  USED_FOR_VIEW,
  USED_FOR_EDIT,
  MEDIA_TYPE
FROM
  STYLESHEET_CONTENT
WHERE
  DOMAIN_NAME = 'BAU'
ORDER BY
  DOMAIN_NAME,
  STYLESHEET_CONTENT_XID
```
**Resultado da Extração:**

{{TABLE_CONTACT_GROUPS}}

---

### Grupo: Extensão e Qualificadores

<div class="section-title">Location Refnum Qualifier</div>

<div class="meta-text" markdown="1">
**Sequência:** 1
**OTM Table:** LOCATION_REFNUM_QUAL
**Deployment Type:** Migration Project
**Migration Project ID:** BAU_MIG_OBJ_EXT_QUAL
**Saved Query ID:** MIG_LOC_REF_QUAL
**Responsável:** ITC
**Tipo de Migração:** Técnica
**Documentação:** Concluído
**Migration Project:** Concluído
**Exportação:** Concluído
**Deploy:** Concluído
**Validação:** Concluído

</div>
**Query de Extração:**
```sql
SELECT
  DOMAIN_NAME,
  LOCATION_REFNUM_QUAL_XID,
  LOCATION_REFNUM_QUAL_DESC,
  IS_VISIBLE_IF_MASTER_CARR,
  DEFAULT_REFNUM_BN_TYPE_GID,
  UPDATE_FLAG
FROM
  LOCATION_REFNUM_QUAL
WHERE LOCATION_REFNUM_QUAL_GID IN (SELECT LOCATION_REFNUM_QUAL_GID FROM LOCATION_REFNUM)
  AND DOMAIN_NAME = 'BAU'
ORDER BY
  DOMAIN_NAME,
  LOCATION_REFNUM_QUAL_XID
```
**Resultado da Extração:**

{{TABLE_LOCATION_REFNUM_QUALIFIER}}

---

<div class="section-title">Order Release Refnum Qualifier</div>

<div class="meta-text" markdown="1">
**Sequência:** 2
**OTM Table:** ORDER_RELEASE_REFNUM_QUAL
**Deployment Type:** Migration Project
**Migration Project ID:** BAU_MIG_OBJ_EXT_QUAL
**Saved Query ID:** MIG_OR_REF_QUAL
**Responsável:** ITC
**Tipo de Migração:** Técnica
**Documentação:** Concluído
**Migration Project:** Concluído
**Exportação:** Concluído
**Deploy:** Concluído
**Validação:** Concluído

</div>
**Query de Extração:**
```sql
SELECT
  DOMAIN_NAME,
  ORDER_RELEASE_REFNUM_QUAL_XID,
  ORDER_RELEASE_REFNUM_QUAL_DESC,
  IS_VISIBLE_IF_MASTER_CARR,
  DEFAULT_REFNUM_BN_TYPE_GID,
  UPDATE_FLAG
FROM
  ORDER_RELEASE_REFNUM_QUAL
WHERE ORDER_RELEASE_REFNUM_QUAL_GID IN (SELECT ORDER_RELEASE_REFNUM_QUAL_GID FROM ORDER_RELEASE_REFNUM)
  AND DOMAIN_NAME = 'BAU'
ORDER BY
  DOMAIN_NAME,
  ORDER_RELEASE_REFNUM_QUAL_XID
```
**Resultado da Extração:**

{{TABLE_ORDER_RELEASE_REFNUM_QUALIFIER}}

---

<div class="section-title">Order Release Line Refnum Qualifier</div>

<div class="meta-text" markdown="1">
**Sequência:** 3
**OTM Table:** ORDER_RELEASE_LINE_REFNUM_QUAL
**Deployment Type:** Migration Project
**Migration Project ID:** BAU_MIG_OBJ_EXT_QUAL
**Saved Query ID:** MIG_ORL_REF_QUAL
**Responsável:** ITC
**Tipo de Migração:** Técnica
**Documentação:** Concluído
**Migration Project:** Concluído
**Exportação:** Concluído
**Deploy:** Concluído
**Validação:** Concluído

</div>
**Query de Extração:**
```sql
SELECT
  DOMAIN_NAME,
  OR_LINE_REFNUM_QUAL_XID,
  DESCRIPTION,
  IS_VISIBLE_IF_MASTER_CARR,
  DEFAULT_REFNUM_BN_TYPE_GID,
  OR_LINE_REFNUM_SEQUENCE_NO,
  UPDATE_FLAG
FROM
  ORDER_RELEASE_LINE_REFNUM_QUAL
WHERE OR_LINE_REFNUM_QUAL_GID IN (SELECT OR_LINE_REFNUM_QUAL_GID FROM ORDER_RELEASE_LINE_REFNUM)
  AND DOMAIN_NAME = 'BAU'
ORDER BY
  DOMAIN_NAME,
  OR_LINE_REFNUM_QUAL_XID
```
**Resultado da Extração:**

{{TABLE_ORDER_RELEASE_LINE_REFNUM_QUALIFIER}}

---

<div class="section-title">Packaged Item Refnum Qualifier</div>

<div class="meta-text" markdown="1">
**Sequência:** 4
**OTM Table:** PACKAGED_ITEM_REFNUM_QUAL
**Deployment Type:** Migration Project
**Migration Project ID:** BAU_MIG_OBJ_EXT_QUAL
**Saved Query ID:** MIG_PI_REF_QUAL
**Responsável:** ITC
**Tipo de Migração:** Técnica
**Documentação:** Concluído
**Migration Project:** Concluído
**Exportação:** Concluído
**Deploy:** Concluído
**Validação:** Concluído

</div>
**Query de Extração:**
```sql
SELECT
  DOMAIN_NAME,
  PACKAGED_ITEM_REFNUM_QUAL_XID,
  PACKAGED_ITEM_REFNUM_QUAL_DESC,
  IS_VISIBLE_IF_MASTER_CARR,
  UPDATE_FLAG
FROM
  PACKAGED_ITEM_REFNUM_QUAL
WHERE PACKAGED_ITEM_REFNUM_QUAL_GID IN (SELECT PACKAGED_ITEM_REFNUM_QUAL_GID FROM PACKAGED_ITEM_REFNUM)
  AND DOMAIN_NAME = 'BAU'
ORDER BY
  DOMAIN_NAME,
  PACKAGED_ITEM_REFNUM_QUAL_XID
```
**Resultado da Extração:**

{{TABLE_PACKAGED_ITEM_REFNUM_QUALIFIER}}

---

<div class="section-title">Item Refnum Qualifier</div>

<div class="meta-text" markdown="1">
**Sequência:** 5
**OTM Table:** ITEM_REFNUM_QUAL
**Deployment Type:** Migration Project
**Migration Project ID:** BAU_MIG_OBJ_EXT_QUAL
**Saved Query ID:** MIG_ITEM_REF_QUAL
**Responsável:** ITC
**Tipo de Migração:** Técnica
**Documentação:** Concluído
**Migration Project:** Concluído
**Exportação:** Concluído
**Deploy:** Concluído
**Validação:** Concluído

</div>
**Query de Extração:**
```sql
SELECT
  DOMAIN_NAME,
  ITEM_REFNUM_QUAL_XID,
  ITEM_REFNUM_QUAL_DESC,
  IS_VISIBLE_IF_MASTER_CARR,
  UPDATE_FLAG
FROM
  ITEM_REFNUM_QUAL
WHERE ITEM_REFNUM_QUAL_GID IN (SELECT ITEM_REFNUM_QUAL_GID FROM ITEM_REFNUM)
  AND DOMAIN_NAME = 'BAU'
ORDER BY
  DOMAIN_NAME,
  ITEM_REFNUM_QUAL_XID
```
**Resultado da Extração:**

{{TABLE_ITEM_REFNUM_QUALIFIER}}

---

<div class="section-title">Shipment Refnum Qualifier</div>

<div class="meta-text" markdown="1">
**Sequência:** 6
**OTM Table:** SHIPMENT_REFNUM_QUAL
**Deployment Type:** Migration Project
**Migration Project ID:** BAU_MIG_OBJ_EXT_QUAL
**Saved Query ID:** MIG_SHP_REF_QUAL
**Responsável:** ITC
**Tipo de Migração:** Técnica
**Documentação:** Concluído
**Migration Project:** Concluído
**Exportação:** Concluído
**Deploy:** Concluído
**Validação:** Concluído

</div>
**Query de Extração:**
```sql
SELECT
  DOMAIN_NAME,
  SHIPMENT_REFNUM_QUAL_XID,
  SHIPMENT_REFNUM_QUAL_DESC,
  IS_VISIBLE_IF_MASTER_CARR,
  UPDATE_FLAG
FROM
  SHIPMENT_REFNUM_QUAL
WHERE SHIPMENT_REFNUM_QUAL_GID IN (SELECT SHIPMENT_REFNUM_QUAL_GID FROM SHIPMENT_REFNUM)
  AND DOMAIN_NAME = 'BAU'
ORDER BY
  DOMAIN_NAME,
  SHIPMENT_REFNUM_QUAL_XID
```
**Resultado da Extração:**

{{TABLE_SHIPMENT_REFNUM_QUALIFIER}}

---

<div class="section-title">Shipment Stop Refnum Qualifier</div>

<div class="meta-text" markdown="1">
**Sequência:** 7
**OTM Table:** SHIPMENT_STOP_REFNUM_QUAL
**Deployment Type:** Migration Project
**Migration Project ID:** BAU_MIG_OBJ_EXT_QUAL
**Saved Query ID:** MIG_STOP_REF_QUAL
**Responsável:** ITC
**Tipo de Migração:** Técnica
**Documentação:** Concluído
**Migration Project:** Concluído
**Exportação:** Concluído
**Deploy:** Concluído
**Validação:** Concluído

</div>
**Query de Extração:**
```sql
SELECT
  DOMAIN_NAME,
  SHIPMENT_STOP_REFNUM_QUAL_XID,
  SHIPMENT_STOP_REFNUM_QUAL_DESC,
  IS_VISIBLE_IF_MASTER_CARR,
  UPDATE_FLAG
FROM
  SHIPMENT_STOP_REFNUM_QUAL
WHERE SHIPMENT_STOP_REFNUM_QUAL_GID IN (SELECT SHIPMENT_STOP_REFNUM_QUAL_GID FROM SHIPMENT_STOP_REFNUM)
  AND DOMAIN_NAME = 'BAU'
ORDER BY
  DOMAIN_NAME,
  SHIPMENT_STOP_REFNUM_QUAL_XID
```
**Resultado da Extração:**

{{TABLE_SHIPMENT_STOP_REFNUM_QUALIFIER}}

---

<div class="section-title">Rate Geo Refnum Qualifier</div>

<div class="meta-text" markdown="1">
**Sequência:** 8
**OTM Table:** RATE_GEO_REFNUM_QUAL
**Deployment Type:** Migration Project
**Migration Project ID:** BAU_MIG_OBJ_EXT_QUAL
**Saved Query ID:** MIG_RGEO_REF_QUAL
**Responsável:** ITC
**Tipo de Migração:** Técnica
**Documentação:** Concluído
**Migration Project:** Concluído
**Exportação:** Concluído
**Deploy:** Concluído
**Validação:** Concluído

</div>
**Query de Extração:**
```sql
SELECT
  DOMAIN_NAME,
  RATE_GEO_REFNUM_QUAL_XID,
  RATE_GEO_REFNUM_QUAL_DESC,
  IS_VISIBLE_IF_MASTER_CARR,
  DEFAULT_REFNUM_BN_TYPE_GID,
  UPDATE_FLAG
FROM
  RATE_GEO_REFNUM_QUAL
WHERE RATE_GEO_REFNUM_QUAL_GID IN (SELECT RATE_GEO_REFNUM_QUAL_GID FROM RATE_GEO_REFNUM)
  AND DOMAIN_NAME = 'BAU'
ORDER BY
  DOMAIN_NAME,
  RATE_GEO_REFNUM_QUAL_XID
```
**Resultado da Extração:**

{{TABLE_RATE_GEO_REFNUM_QUALIFIER}}

---

<div class="section-title">Order Movement Refnum Qualifier</div>

<div class="meta-text" markdown="1">
**Sequência:** 9
**OTM Table:** OM_REFNUM_QUAL
**Deployment Type:** Migration Project
**Migration Project ID:** BAU_MIG_OBJ_EXT_QUAL
**Saved Query ID:** MIG_OM_REF_QUAL
**Responsável:** ITC
**Tipo de Migração:** Técnica
**Documentação:** Concluído
**Migration Project:** Concluído
**Exportação:** Concluído
**Deploy:** Concluído
**Validação:** Concluído

</div>
**Query de Extração:**
```sql
SELECT DOMAIN_NAME,
  OM_REFNUM_QUAL_GID,
  OM_REFNUM_QUAL_DESC,
  UPDATE_FLAG
FROM
  OM_REFNUM_QUAL
WHERE OM_REFNUM_QUAL_GID IN (SELECT OM_REFNUM_QUAL_GID FROM ORDER_MOVEMENT_REFNUM)
  AND DOMAIN_NAME = 'BAU'
ORDER BY
  DOMAIN_NAME,
  OM_REFNUM_QUAL_XID
```
**Resultado da Extração:**

{{TABLE_ORDER_MOVEMENT_REFNUM_QUALIFIER}}

---

<div class="section-title">Status Types and Values</div>

<div class="meta-text" markdown="1">
**Sequência:** 10
**OTM Table:** STATUS_TYPE
**Deployment Type:** Migration Project
**Migration Project ID:** BAU_MIG_OBJ_EXT_QUAL
**Saved Query ID:** MIG_STATUS_TYPES
**Responsável:** ITC
**Tipo de Migração:** Técnica
**Documentação:** Concluído
**Migration Project:** Concluído
**Exportação:** Concluído
**Deploy:** Concluído
**Validação:** Concluído

</div>
**Query de Extração:**
```sql
SELECT
  st.DOMAIN_NAME,
  st.STATUS_TYPE_GID,
  st.STATUS_TYPE_XID,
  st.OBJECT_TYPE,
  st.DESCRIPTION AS STATUS_TYPE_DESCRIPTION,
  st.SEQUENCE AS STATUS_TYPE_SEQUENCE,
  st.IS_EXTERNAL,
  sv.STATUS_VALUE_XID,
  sv.DESCRIPTION AS STATUS_VALUE_DESCRIPTION,
  sv.SEQUENCE AS STATUS_VALUE_SEQUENCE,
  sv.INITIAL_VALUE
FROM
  STATUS_VALUE sv,
  STATUS_TYPE st
WHERE
  sv.STATUS_TYPE_GID = st.STATUS_TYPE_GID
  AND st.IS_EXTERNAL = 'Y'
  AND (
    EXISTS (
      SELECT 1
      FROM SHIPMENT_STATUS ss
      WHERE ss.STATUS_TYPE_GID = st.STATUS_TYPE_GID
        AND ss.UPDATE_DATE >= TO_DATE('02/01/2026','DD/MM/YYYY')
    )
    OR EXISTS (
      SELECT 1
      FROM ORDER_RELEASE_STATUS ors
      WHERE ors.STATUS_TYPE_GID = st.STATUS_TYPE_GID
        AND ors.UPDATE_DATE >= TO_DATE('02/01/2026','DD/MM/YYYY')
    )
  )
ORDER BY
  st.DOMAIN_NAME,
  st.OBJECT_TYPE,
  st.STATUS_TYPE_GID,
  sv.SEQUENCE
```
**Resultado da Extração:**

{{TABLE_STATUS_TYPES_AND_VALUES}}

---

<div class="section-title">Remarks Qualifiers</div>

<div class="meta-text" markdown="1">
**Sequência:** 11
**OTM Table:** REMARK_QUAL
**Deployment Type:** Migration Project
**Migration Project ID:** BAU_MIG_OBJ_EXT_QUAL
**Saved Query ID:** MIG_REMARK_QUALS
**Responsável:** ITC
**Tipo de Migração:** Técnica
**Documentação:** Concluído
**Migration Project:** Concluído
**Exportação:** Concluído
**Deploy:** Concluído
**Validação:** Concluído

</div>
**Query de Extração:**
```sql
SELECT rq.DOMAIN_NAME,
  rq.REMARK_QUAL_GID,
  rq.REMARK_QUAL_XID,
  rq.REMARK_QUAL_DESC,
  rq.REMARK_LEVEL,
  rq.IS_VISIBLE_IF_MASTER_CARR,
  rq.UPDATE_FLAG,
  rq.TEXT_TEMPLATE_GID,
  rq.QUAL_TYPE,
  rq.DATA_QUERY_TYPE_GID
FROM
  REMARK_QUAL rq
WHERE
  rq.DOMAIN_NAME = 'BAU'
ORDER BY
  rq.DATA_QUERY_TYPE_GID,
  rq.REMARK_QUAL_XID
```
**Resultado da Extração:**

{{TABLE_REMARKS_QUALIFIERS}}

---

### Grupo: Planejamento

Esta seção oferece **visibilidade completa** dos elementos que impactam decisões de planejamento, permitindo validar que o comportamento do engine no ambiente destino permaneça aderente ao cenário produtivo.

A correta migração desses objetos é fundamental para manter **custos, níveis de serviço e eficiência operacional**.

<div class="section-title">Audit Trail</div>

<div class="meta-text" markdown="1">
**Sequência:** 1
**OTM Table:** CONTACT
**Deployment Type:** Migration Project
**Migration Project ID:** BAU_MIG_SUP_PLANEJAMENTO
**Saved Query ID:** MIG_AUDIT_TRAIL
**Responsável:** ITC
**Tipo de Migração:** Técnica
**Documentação:** Concluído
**Migration Project:** Concluído
**Exportação:** Concluído
**Deploy:** Concluído
**Validação:** Concluído

</div>
**Query de Extração:**
```sql
SELECT
  c.DOMAIN_NAME AS CONTACT_DOMAIN_NAME,
  c.CONTACT_GID,
  c.CONTACT_XID,
  c.CONTACT_TYPE,
  c.IS_PRIMARY_CONTACT,
  ccm.COM_METHOD_GID,
  ccm.COM_METHOD_RANK,
  nsc.NOTIFY_SUBJECT_GID,
  nsc.CONSOLIDATED_NOTIFY_ONLY,
  nsc.PARAMETERS
FROM
  CONTACT c
  LEFT JOIN CONTACT_COM_METHOD ccm ON ccm.CONTACT_GID = c.CONTACT_GID
  LEFT JOIN NOTIFY_SUBJECT_CONTACT nsc ON nsc.CONTACT_GID = c.CONTACT_GID AND nsc.COM_METHOD_GID = ccm.COM_METHOD_GID
WHERE
  c.DOMAIN_NAME = 'BAU'
  AND
  c.CONTACT_GID = 'BAU.AUD'
ORDER BY
  c.CONTACT_GID,
  ccm.COM_METHOD_RANK,
  nsc.NOTIFY_SUBJECT_GID
```
**Resultado da Extração:**

{{TABLE_AUDIT_TRAIL}}

---

<div class="section-title">Logic Configs</div>

<div class="meta-text" markdown="1">
**Sequência:** 2
**OTM Table:** LOGIC_PARAMETER
**Deployment Type:** Migration Project
**Migration Project ID:** BAU_MIG_SUP_PLANEJAMENTO
**Saved Query ID:** MIG_LOGIC_CONFIGS
**Responsável:** ITC
**Tipo de Migração:** Técnica
**Documentação:** Concluído
**Migration Project:** Concluído
**Exportação:** Concluído
**Deploy:** Concluído
**Validação:** Concluído

</div>
**Query de Extração:**
```sql
SELECT
  DOMAIN_NAME,
  LOGIC_CONFIG_GID,
  LOGIC_PARAM_QUAL_GID,
  LOGIC_SCENARIO_GID,
  PARAM_VALUE,
  PARAM_UOM_CODE
FROM
  LOGIC_PARAMETER
WHERE
  DOMAIN_NAME = 'BAU'
ORDER BY
  DOMAIN_NAME,
  LOGIC_CONFIG_GID,
  LOGIC_PARAM_QUAL_GID
```
**Resultado da Extração:**

{{TABLE_LOGIC_CONFIGS}}

---

<div class="section-title">Parameter Sets</div>

<div class="meta-text" markdown="1">
**Sequência:** 3
**OTM Table:** PLANNING_PARAMETER
**Deployment Type:** Migration Project
**Migration Project ID:** BAU_MIG_SUP_PLANEJAMENTO
**Saved Query ID:** MIG_PARAMETER_SETS
**Responsável:** ITC
**Tipo de Migração:** Técnica
**Documentação:** Concluído
**Migration Project:** Concluído
**Exportação:** Concluído
**Deploy:** Concluído
**Validação:** Concluído

</div>
**Query de Extração:**
```sql
SELECT
  DOMAIN_NAME,
  PLANNING_PARAMETER_SET_GID,
  PLANNING_PARAM_QUALIFIER_GID,
  PLANNING_PARAM_VALUE
FROM
  PLANNING_PARAMETER
WHERE
  DOMAIN_NAME = 'BAU'
  AND PLANNING_PARAMETER_SET_GID IN ('BAU.BAU_PARAMETER_OV', 'BAU.BAU_PARAMETER')
ORDER BY
  DOMAIN_NAME,
  PLANNING_PARAMETER_SET_GID,
  PLANNING_PARAM_QUALIFIER_GID
```
**Resultado da Extração:**

{{TABLE_PARAMETER_SETS}}

---

<div class="section-title">Accessorial Codes</div>

<div class="meta-text" markdown="1">
**Sequência:** 4
**OTM Table:** ACCESSORIAL_CODE
**Deployment Type:** Migration Project
**Migration Project ID:** BAU_MIG_SUP_PLANEJAMENTO
**Saved Query ID:** MIG_ACCESSORIAL_CODES
**Responsável:** ITC
**Tipo de Migração:** Técnica
**Documentação:** Concluído
**Migration Project:** Concluído
**Exportação:** Concluído
**Deploy:** Concluído
**Validação:** Concluído

</div>
**Query de Extração:**
```sql
SELECT
  DOMAIN_NAME,
  ACCESSORIAL_CODE_XID,
  ACCESSORIAL_DESC,
  APPLY_GLOBALLY,
  IS_FLOW_THRU
FROM
  ACCESSORIAL_CODE
WHERE
  DOMAIN_NAME = 'BAU'
ORDER BY
  ACCESSORIAL_CODE_XID
```
**Resultado da Extração:**

{{TABLE_ACCESSORIAL_CODES}}

---

<div class="section-title">Itinerary Leg</div>

<div class="meta-text" markdown="1">
**Sequência:** 5
**OTM Table:** LEG
**Deployment Type:** Migration Project
**Migration Project ID:** BAU_MIG_SUP_PLANEJAMENTO
**Saved Query ID:** MIG_LEG
**Responsável:** ITC
**Tipo de Migração:** Técnica
**Documentação:** Concluído
**Migration Project:** Concluído
**Exportação:** Concluído
**Deploy:** Concluído
**Validação:** Concluído

</div>
**Query de Extração:**
```sql
SELECT
  L.LEG_GID,
  L.LEG_NAME,
  ID.ITINERARY_GID
FROM
    ITINERARY ID,
    ITINERARY_DETAIL ITD,
    LEG L
WHERE
    ID.ITINERARY_GID = ITD.ITINERARY_GID
    AND ITD.LEG_GID = L.LEG_GID
    AND ID.DOMAIN_NAME = 'BAU'
ORDER BY
    ID.ITINERARY_XID,
    ITD.SEQUENCE_NO
```
**Resultado da Extração:**

{{TABLE_ITINERARY_LEG}}

---

<div class="section-title">Itineraries</div>

<div class="meta-text" markdown="1">
**Sequência:** 6
**OTM Table:** ITINERARY
**Deployment Type:** Migration Project
**Migration Project ID:** BAU_MIG_SUP_PLANEJAMENTO
**Saved Query ID:** MIG_ITINERARIES
**Responsável:** ITC
**Tipo de Migração:** Técnica
**Documentação:** Concluído
**Migration Project:** Concluído
**Exportação:** Concluído
**Deploy:** Concluído
**Validação:** Concluído

</div>
**Query de Extração:**
```sql
SELECT
    ID.DOMAIN_NAME,
    ID.ITINERARY_GID,
    ID.ITINERARY_XID,
    ITD.LEG_GID,
    ITD.SEQUENCE_NO,
    L.LEG_NAME,
    L.LEG_TYPE,
    L.EQUIPMENT_GROUP_PROFILE_GID,
    L.MODE_PROFILE_GID,
    L.DEST_LOCATION_GID,
    L.RATE_OFFERING_GID,
    L.AUTO_CONSOLIDATION_TYPE
FROM
    ITINERARY ID,
    ITINERARY_DETAIL ITD,
    LEG L
WHERE
    ID.ITINERARY_GID = ITD.ITINERARY_GID
    AND ITD.LEG_GID = L.LEG_GID
    AND ID.DOMAIN_NAME = 'BAU'
ORDER BY
    ID.ITINERARY_XID,
    ITD.SEQUENCE_NO
```
**Resultado da Extração:**

{{TABLE_ITINERARIES}}

---

<div class="section-title">Itinerary Profiles</div>

<div class="meta-text" markdown="1">
**Sequência:** 7
**OTM Table:** ITINERARY_PROFILE
**Deployment Type:** Migration Project
**Migration Project ID:** BAU_MIG_SUP_PLANEJAMENTO
**Saved Query ID:** MIG_ITINERARY_PROFILES
**Responsável:** ITC
**Tipo de Migração:** Técnica
**Documentação:** Concluído
**Migration Project:** Concluído
**Exportação:** Concluído
**Deploy:** Concluído
**Validação:** Concluído

</div>
**Query de Extração:**
```sql
SELECT
  IP.ITINERARY_PROFILE_GID,
  IP.ITINERARY_PROFILE_XID,
  IP.ITINERARY_PROFILE_NAME,
  IP.IS_COMPATIBLE,
  IP.DOMAIN_NAME,
  IPD.ITINERARY_GID,
  IPD.DOMAIN_NAME AS DETAIL_DOMAIN_NAME
FROM ITINERARY_PROFILE IP
JOIN ITINERARY_PROFILE_D IPD
  ON IP.ITINERARY_PROFILE_GID = IPD.ITINERARY_PROFILE_GID
WHERE
  IP.DOMAIN_NAME = 'BAU'
ORDER BY
  IP.ITINERARY_PROFILE_XID,
  IPD.ITINERARY_GID
```
**Resultado da Extração:**

{{TABLE_ITINERARY_PROFILES}}

---

<div class="section-title">Load Configuration Rules</div>

<div class="meta-text" markdown="1">
**Sequência:** 8
**OTM Table:** LOAD_CONFIG_RULE
**Deployment Type:** Migration Project
**Migration Project ID:** BAU_MIG_SUP_PLANEJAMENTO
**Saved Query ID:** MIG_LOAD_CONFIG_RULES
**Responsável:** ITC
**Tipo de Migração:** Técnica
**Documentação:** Concluído
**Migration Project:** Concluído
**Exportação:** Concluído
**Deploy:** Concluído
**Validação:** Concluído

</div>
**Query de Extração:**
```sql
SELECT
  DOMAIN_NAME,
  LOAD_CONFIG_SETUP_GID,
  SEQUENCE_NO,
  TRANSPORT_HANDLING_UNIT_GID
FROM
  LOAD_CONFIG_RULE
WHERE
  DOMAIN_NAME = 'BAU'
ORDER BY
  LOAD_CONFIG_SETUP_GID
```
**Resultado da Extração:**

{{TABLE_LOAD_CONFIGURATION_RULES}}

---

<div class="section-title">Load Configuration Setup</div>

<div class="meta-text" markdown="1">
**Sequência:** 9
**OTM Table:** LOAD_CONFIG_SETUP
**Deployment Type:** Migration Project
**Migration Project ID:** BAU_MIG_SUP_PLANEJAMENTO
**Saved Query ID:** MIG_LOAD_CONFIG_SETUP
**Responsável:** ITC
**Tipo de Migração:** Técnica
**Documentação:** Concluído
**Migration Project:** Concluído
**Exportação:** Concluído
**Deploy:** Concluído
**Validação:** Concluído

</div>
**Query de Extração:**
```sql
SELECT
  LCS.DOMAIN_NAME,
  LCS.LOAD_CONFIG_SETUP_GID,
  LCS.LOAD_CONFIG_SETUP_XID,
  LCSO.ORIENTATION_GID,
  LCSO.IS_PREFERRED,
  LCSO.IS_FLOOR_COMPATIBLE,
  LCSO.MAX_TOP_WEIGHT
FROM
  LOAD_CONFIG_SETUP LCS
  JOIN LOAD_CONFIG_SETUP_ORIENTATION LCSO
    ON LCSO.LOAD_CONFIG_SETUP_GID = LCS.LOAD_CONFIG_SETUP_GID
    AND LCSO.DOMAIN_NAME = LCS.DOMAIN_NAME
WHERE
  LCS.DOMAIN_NAME = 'BAU'
ORDER BY
  LCS.LOAD_CONFIG_SETUP_GID,
  LCSO.ORIENTATION_GID
```
**Resultado da Extração:**

{{TABLE_LOAD_CONFIGURATION_SETUP}}

---

<div class="section-title">Order Release Types</div>

<div class="meta-text" markdown="1">
**Sequência:** 10
**OTM Table:** ORDER_RELEASE_TYPE
**Deployment Type:** Migration Project
**Migration Project ID:** BAU_MIG_SUP_PLANEJAMENTO
**Saved Query ID:** MIG_ORDER_RELEASE_TYPES
**Responsável:** ITC
**Tipo de Migração:** Técnica
**Documentação:** Concluído
**Migration Project:** Concluído
**Exportação:** Concluído
**Deploy:** Concluído
**Validação:** Concluído

</div>
**Query de Extração:**
```sql
SELECT
  DOMAIN_NAME,
  ORDER_RELEASE_TYPE_GID,
  ORDER_RELEASE_TYPE_XID,
  ORDER_RELEASE_TYPE_NAME
FROM
  ORDER_RELEASE_TYPE
WHERE
  DOMAIN_NAME = 'BAU'
ORDER BY
  ORDER_RELEASE_TYPE_XID
```
**Resultado da Extração:**

{{TABLE_ORDER_RELEASE_TYPES}}

---

### Grupo: Integração

<div class="section-title">Stylesheet Contents</div>

<div class="meta-text" markdown="1">
**Sequência:** 1
**OTM Table:** STYLESHEET_CONTENT
**Deployment Type:** Migration Project
**Migration Project ID:** BAU_MIG_OBJ_INT
**Saved Query ID:** MIG_STYLESHEET_CONTENTS
**Responsável:** ITC
**Tipo de Migração:** Técnica
**Documentação:** Concluído
**Migration Project:** Concluído
**Exportação:** Concluído
**Deploy:** Concluído
**Validação:** Concluído

</div>
**Query de Extração:**
```sql
SELECT
  DOMAIN_NAME,
  STYLESHEET_CONTENT_GID,
  STYLESHEET_CONTENT_XID,
  USED_FOR_VIEW,
  USED_FOR_EDIT,
  MEDIA_TYPE
FROM
  STYLESHEET_CONTENT
WHERE
  DOMAIN_NAME = 'BAU'
ORDER BY
  DOMAIN_NAME,
  STYLESHEET_CONTENT_XID
```
**Resultado da Extração:**

{{TABLE_STYLESHEET_CONTENTS}}

---

<div class="section-title">Stylesheet Profiles</div>

<div class="meta-text" markdown="1">
**Sequência:** 2
**OTM Table:** STYLESHEET_PROFILE
**Deployment Type:** Migration Project
**Migration Project ID:** BAU_MIG_OBJ_INT
**Saved Query ID:** MIG_STYLESHEET_PROFILES
**Responsável:** ITC
**Tipo de Migração:** Técnica
**Documentação:** Concluído
**Migration Project:** Concluído
**Exportação:** Concluído
**Deploy:** Concluído
**Validação:** Concluído

</div>
**Query de Extração:**
```sql
SELECT ssp.STYLESHEET_PROFILE_GID,
  ssp.STYLESHEET_PROFILE_XID,
  ssp.TEMPLATE_NAME,
  ssp.RAW_XML,
  ssp.FORMAT,
  ssp.SUBJECT_PROPKEY,
  ssp.OUT_XML_PROFILE_GID,
  ssp.DATA_GENERATOR_PLUGIN_GID,
  ssp.NOTIFY_FUNCTION_GID,
  ssp.DOCUMENT_ATTACH_TYPE,
  ssp.DIRECTION,
  ssp.TYPE,
  ssp.IS_FOR_NOTIFICATION_XML,
  ssp.IS_FOR_TRANSMISSION_XML,
  ssp.IS_FOR_MESSAGE_XML,
  ssp.CONTENT_GID,
  ssp.VIEW_CONTENT_GID,
  ssp.EDIT_CONTENT_GID,
  ssp.OTM_RELEASE,
  ssp.DOMAIN_NAME
FROM
  STYLESHEET_PROFILE ssp
WHERE
  ssp.CONTENT_GID IN (
    SELECT
      sc.STYLESHEET_CONTENT_GID
    FROM
      STYLESHEET_CONTENT sc
    WHERE
      sc.DOMAIN_NAME = 'BAU'
  )
```
**Resultado da Extração:**

{{TABLE_STYLESHEET_PROFILES}}

---

<div class="section-title">XML Templates</div>

<div class="meta-text" markdown="1">
**Sequência:** 3
**OTM Table:** XML_TEMPLATE
**Deployment Type:** Migration Project
**Migration Project ID:** BAU_MIG_OBJ_INT
**Saved Query ID:** MIG_XML_TEMPLATES
**Responsável:** ITC
**Tipo de Migração:** Técnica
**Documentação:** Concluído
**Migration Project:** Concluído
**Exportação:** Concluído
**Deploy:** Concluído
**Validação:** Concluído

</div>
**Query de Extração:**
```sql
SELECT xt.DOMAIN_NAME,
  xt.XML_TEMPLATE_GID,
  xt.XML_TEMPLATE_XID,
  xt.USE_DATA,
  xt.DESCRIPTION,
  xt.GLOG_XML_ELEMENT_GID
FROM
  XML_TEMPLATE xt
WHERE
  xt.DOMAIN_NAME = 'BAU'
ORDER BY
  xt.XML_TEMPLATE_XID
```
**Resultado da Extração:**

{{TABLE_XML_TEMPLATES}}

---

<div class="section-title">Outbound XML Profiles</div>

<div class="meta-text" markdown="1">
**Sequência:** 4
**OTM Table:** OUT_XML_PROFILE
**Deployment Type:** Migration Project
**Migration Project ID:** BAU_MIG_OBJ_INT
**Saved Query ID:** MIG_OUT_XML_PROFS
**Responsável:** ITC
**Tipo de Migração:** Técnica
**Documentação:** Concluído
**Migration Project:** Concluído
**Exportação:** Concluído
**Deploy:** Concluído
**Validação:** Concluído

</div>
**Query de Extração:**
```sql
SELECT oxp.DOMAIN_NAME,
  oxp.OUT_XML_PROFILE_GID,
  oxp.OUT_XML_PROFILE_XID,
  oxp.DEFAULT_MODE,
  oxp.SHOULD_VALIDATE,
  oxp.XML_TEMPLATE_GID,
  oxp.USE_TEMPLATE,
  oxp.INT_PREFERENCE_GID
FROM
  OUT_XML_PROFILE oxp
WHERE
  oxp.DOMAIN_NAME = 'BAU'
ORDER BY
  oxp.OUT_XML_PROFILE_XID
```
**Resultado da Extração:**

{{TABLE_OUTBOUND_XML_PROFILES}}

---

<div class="section-title">Document</div>

<div class="meta-text" markdown="1">
**Sequência:** 5
**OTM Table:** DOCUMENT
**Deployment Type:** Migration Project
**Migration Project ID:** BAU_MIG_OBJ_INT
**Saved Query ID:** MIG_DOCUMENTS
**Responsável:** ITC
**Tipo de Migração:** Técnica
**Documentação:** Concluído
**Migration Project:** Concluído
**Exportação:** Concluído
**Deploy:** Concluído
**Validação:** Concluído

</div>
**Query de Extração:**
```sql
SELECT d.DOMAIN_NAME,
  d.DOCUMENT_GID,
  d.DOCUMENT_XID,
  d.DOCUMENT_TYPE,
  d.DOCUMENT_MIME_TYPE,
  d.DOCUMENT_FILENAME,
  d.MARKED_FOR_PURGE,
  d.UPLOADED_AT,
  d.DOCUMENT_CMS_ID,
  d.CONTENT_MANAGEMENT_SYSTEM_GID,
  d.USED_AS
FROM
  DOCUMENT d
WHERE
  d.DOMAIN_NAME = 'BAU'
ORDER BY
  d.DOCUMENT_XID
```
**Resultado da Extração:**

{{TABLE_DOCUMENT}}

---

<div class="section-title">Webservice</div>

<div class="meta-text" markdown="1">
**Sequência:** 6
**OTM Table:** WEB_SERVICE
**Deployment Type:** Migration Project
**Migration Project ID:** BAU_MIG_OBJ_INT
**Saved Query ID:** MIG_WEB_SERVICE
**Responsável:** ITC
**Tipo de Migração:** Técnica
**Documentação:** Concluído
**Migration Project:** Concluído
**Exportação:** Concluído
**Deploy:** Concluído
**Validação:** Concluído

</div>
**Query de Extração:**
```sql
SELECT ws.DOMAIN_NAME,
  ws.WEB_SERVICE_GID,
  ws.WEB_SERVICE_XID,
  ws.WSDL_DOCUMENT_GID,
  ws.SERVICE_NAME,
  ws.PORT_NAME,
  ws.NAMESPACE,
  ws.SOAP_ENCODING,
  ws.USE_WSS,
  ws.WEB_SERVICE_TYPE
FROM
  WEB_SERVICE ws
WHERE
  ws.DOMAIN_NAME = 'BAU'
ORDER BY
  ws.WEB_SERVICE_XID
```
**Resultado da Extração:**

{{TABLE_WEBSERVICE}}

---

<div class="section-title">External Systems</div>

<div class="meta-text" markdown="1">
**Sequência:** 7
**OTM Table:** EXTERNAL_SYSTEM
**Deployment Type:** Migration Project
**Migration Project ID:** BAU_MIG_OBJ_INT
**Saved Query ID:** MIG_EXT_SYSTEMS
**Responsável:** ITC
**Tipo de Migração:** Técnica
**Documentação:** Concluído
**Migration Project:** Concluído
**Exportação:** Concluído
**Deploy:** Concluído
**Validação:** Concluído

</div>
**Query de Extração:**
```sql
SELECT es.DOMAIN_NAME,
  es.EXTERNAL_SYSTEM_GID,
  es.EXTERNAL_SYSTEM_XID,
  es.DESCRIPTION,
  es.USE_GLCREDENTIAL,
  es.ACTIVE_MODE,
  es.IS_ENABLE_DEBUG,
  es.IS_LOG_RESPONSE_MSG,
  es.REATTEMPT_MODE,
  es.FTP_APPEND_FILE,
  es.HTTP_ACK_EXPECTED,
  es.HTTP_USE_ACK_STATUS,
  es.HTTP_READ_RESPONSE,
  es.SERVICE_ACK_EXPECTED,
  es.SERVICE_USE_ACK_STATUS,
  es.HTTP_CLOSE_CONNECTION,
  es.DELAYED_STREAM_TRANSPORT,
  es.USE_FTPS,
  es.INCLUDE_NAMESPACE,
  es.TARGET_NAMESPACE,
  es.CONTENT_TYPE,
  es.USE_HTTP_POST_OVERRIDE,
  es.HTTP_METHOD,
  es.OTM_RELEASE,
  es.ALLOW_FOLLOW_REDIRECT
FROM
  EXTERNAL_SYSTEM es
WHERE
  es.DOMAIN_NAME = 'BAU'
ORDER BY
  es.EXTERNAL_SYSTEM_XID
```
**Resultado da Extração:**

{{TABLE_EXTERNAL_SYSTEMS}}

---

<div class="section-title">External System Contact</div>

<div class="meta-text" markdown="1">
**Sequência:** 8
**OTM Table:** CONTACT
**Deployment Type:** Migration Project
**Migration Project ID:** BAU_MIG_OBJ_INT
**Saved Query ID:** MIG_EXT_SYS_CONTACT
**Responsável:** ITC
**Tipo de Migração:** Técnica
**Documentação:** Concluído
**Migration Project:** Concluído
**Exportação:** Concluído
**Deploy:** Concluído
**Validação:** Concluído

</div>
**Query de Extração:**
```sql
SELECT c.CONTACT_GID,
  c.CONTACT_XID,
  c.IS_PRIMARY_CONTACT,
  c.EXTERNAL_SYSTEM_GID,
  c.CONTACT_TYPE,
  c.IS_BROADCAST,
  c.DOMAIN_NAME
FROM
  CONTACT c
WHERE
  c.DOMAIN_NAME = 'BAU'
  AND c.EXTERNAL_SYSTEM_GID IS NOT NULL
ORDER BY
  c.CONTACT_XID
```
**Resultado da Extração:**

{{TABLE_EXTERNAL_SYSTEM_CONTACT}}

---

### Grupo: Governança e UI

Esta seção garante que os mecanismos de **visibilidade, rastreabilidade e controle operacional** continuem disponíveis durante e após a migração, minimizando impactos para usuários finais e times de suporte.

A correta migração desses objetos é essencial para manter **transparência e governança** no ambiente destino.

<div class="section-title">Manager Layouts</div>

<div class="meta-text" markdown="1">
**Sequência:** 1
**OTM Table:** MANAGER_LAYOUT
**Deployment Type:** Migration Project
**Migration Project ID:** BAU_MIG_OBJ_GOV_UI
**Saved Query ID:** MIG_MANAGER_LAYOUTS
**Responsável:** ITC
**Tipo de Migração:** Técnica
**Documentação:** Concluído
**Migration Project:** Pendente
**Exportação:** Pendente
**Deploy:** Pendente
**Validação:** Pendente

</div>
**Query de Extração:**
```sql
SELECT
  ml.DOMAIN_NAME,
  ml.MANAGER_LAYOUT_GID,
  ml.MANAGER_LAYOUT_XID,
  ml.MANAGER_LAYOUT_NAME,
  ml.ENTITY_NAME
FROM
  MANAGER_LAYOUT ml
WHERE
  ml.DOMAIN_NAME = 'BAU'
ORDER BY
  ml.MANAGER_LAYOUT_XID
```
**Resultado da Extração:**

{{TABLE_MANAGER_LAYOUTS}}

---

<div class="section-title">Finder Sets</div>

<div class="meta-text" markdown="1">
**Sequência:** 2
**OTM Table:** FINDER_SET
**Deployment Type:** Migration Project
**Migration Project ID:** BAU_MIG_OBJ_GOV_UI
**Saved Query ID:** MIG_FINDER_SETS
**Responsável:** ITC
**Tipo de Migração:** Técnica
**Documentação:** Concluído
**Migration Project:** Pendente
**Exportação:** Pendente
**Deploy:** Pendente
**Validação:** Pendente

</div>
**Query de Extração:**
```sql
SELECT
  fs.DOMAIN_NAME,
  fs.FINDER_SET_XID,
  fs.FINDER_SET_NAME,
  fs.QUERY_TABLE_GID,
  fs.USE_IN_MIGRATION
FROM
  FINDER_SET fs
WHERE
  fs.DOMAIN_NAME = 'BAU'
  AND (
    EXISTS (
      SELECT 1
      FROM USER_MENU_LAYOUT uml
      WHERE uml.DOMAIN_NAME = 'BAU'
        AND uml.USER_MENU_LAYOUT_XML IS NOT NULL
        AND DBMS_LOB.INSTR(uml.USER_MENU_LAYOUT_XML, 'finder_set_gid=' || fs.FINDER_SET_GID, 1, 1) > 0
    )
    OR EXISTS (
      SELECT 1
      FROM USER_MENU_LAYOUT uml
      WHERE uml.DOMAIN_NAME = 'BAU'
        AND uml.USER_MENU_LAYOUT_JSON IS NOT NULL
        AND DBMS_LOB.INSTR(uml.USER_MENU_LAYOUT_JSON, 'finder_set_gid=' || fs.FINDER_SET_GID, 1, 1) > 0
    )
    OR EXISTS (
      SELECT 1
      FROM DEFAULT_FINDER_SET_ACCESS dfa
      WHERE dfa.DOMAIN_NAME = 'BAU'
        AND dfa.FINDER_SET_GID = fs.FINDER_SET_GID
    )
  )
ORDER BY
  fs.FINDER_SET_XID
```
**Resultado da Extração:**

{{TABLE_FINDER_SETS}}

---

<div class="section-title">Workbenches</div>

<div class="meta-text" markdown="1">
**Sequência:** 3
**OTM Table:** TRANSPORTATION_WORKBENCH
**Deployment Type:** Migration Project
**Migration Project ID:** BAU_MIG_OBJ_GOV_UI
**Saved Query ID:** MIG_WORKBENCHES
**Responsável:** ITC
**Tipo de Migração:** Técnica
**Documentação:** Pendente
**Migration Project:** Pendente
**Exportação:** Pendente
**Deploy:** Pendente
**Validação:** Pendente

</div>
**Query de Extração:**
```sql
SELECT
  tw.DOMAIN_NAME,
  tw.LAYOUT_GID,
  tw.LAYOUT_XID,
  tw.DESCRIPTION
FROM
  TRANSPORTATION_WORKBENCH tw
WHERE
  tw.DOMAIN_NAME = 'BAU'
ORDER BY
  tw.LAYOUT_XID
```
**Resultado da Extração:**

{{TABLE_WORKBENCHES}}

---

<div class="section-title">Business Monitors</div>

<div class="meta-text" markdown="1">
**Sequência:** 4
**OTM Table:** BUSINESS_MONITOR_D
**Deployment Type:** Migration Project
**Migration Project ID:** BAU_MIG_OBJ_GOV_UI
**Saved Query ID:** MIG_BUSINESS_MONITORS
**Responsável:** ITC
**Tipo de Migração:** Técnica
**Documentação:** Pendente
**Migration Project:** Pendente
**Exportação:** Pendente
**Deploy:** Pendente
**Validação:** Pendente

</div>
**Query de Extração:**
```sql
SELECT
  DOMAIN_NAME,
  BUSINESS_MONITOR_GID,
  SEQUENCE,
  QUERY_TABLE_GID,
  SAVED_QUERY_GID,
  FINDER_SET_GID
FROM
  BUSINESS_MONITOR_D
WHERE
  DOMAIN_NAME = 'BAU'
```
**Resultado da Extração:**

{{TABLE_BUSINESS_MONITORS}}

---

<div class="section-title">Access Control Lists (ACL)</div>

<div class="meta-text" markdown="1">
**Sequência:** 5
**OTM Table:** ACR_ROLE
**Deployment Type:** Migration Project
**Migration Project ID:** BAU_MIG_OBJ_GOV_UI
**Saved Query ID:** MIG_ACL
**Responsável:** ITC
**Tipo de Migração:** Técnica
**Documentação:** Pendente
**Migration Project:** Pendente
**Exportação:** Pendente
**Deploy:** Pendente
**Validação:** Pendente

</div>
**Query de Extração:**
```sql
SELECT
  URAR.DOMAIN_NAME,
  URAR.USER_ROLE_GID,
  AR.ACR_ROLE_XID,
  URAR.IS_GRANTED
FROM
  ACR_ROLE AR,
  USER_ROLE_ACR_ROLE URAR
WHERE
  AR.ACR_ROLE_GID = URAR.ACR_ROLE_GID
ORDER BY
  URAR.USER_ROLE_GID
```
**Resultado da Extração:**

{{TABLE_ACCESS_CONTROL_LISTS_(ACL)}}

---

<div class="section-title">User Roles</div>

<div class="meta-text" markdown="1">
**Sequência:** 6
**OTM Table:** USER_ROLE
**Deployment Type:** Migration Project
**Migration Project ID:** BAU_MIG_OBJ_GOV_UI
**Saved Query ID:** MIG_USER_ROLES
**Responsável:** ITC
**Tipo de Migração:** Técnica
**Documentação:** Pendente
**Migration Project:** Pendente
**Exportação:** Pendente
**Deploy:** Pendente
**Validação:** Pendente

</div>
**Query de Extração:**
```sql
SELECT
  DOMAIN_NAME,
  USER_ROLE_GID,
  USER_ROLE_XID,
  USER_ROLE_NAME,
  DESCRIPTION,
  ACTIVE_STATUS
FROM
  USER_ROLE
WHERE
  DOMAIN_NAME = 'BAU'
ORDER BY
  USER_ROLE_XID
```
**Resultado da Extração:**

{{TABLE_USER_ROLES}}

---

<div class="section-title">User Menus</div>

<div class="meta-text" markdown="1">
**Sequência:** 6
**OTM Table:** USER_MENU
**Deployment Type:** Migration Project
**Migration Project ID:** BAU_MIG_OBJ_GOV_UI
**Saved Query ID:** MIG_USER_MENUS
**Responsável:** ITC
**Tipo de Migração:** Técnica
**Documentação:** Pendente
**Migration Project:** Pendente
**Exportação:** Pendente
**Deploy:** Pendente
**Validação:** Pendente

</div>
**Query de Extração:**
```sql
SELECT
  DOMAIN_NAME,
  USER_MENU_GID,
  USER_MENU_XID,
  LABEL,
  MENU_TYPE,
  DESCRIPTION
FROM
  USER_MENU
WHERE
  DOMAIN_NAME = 'BAU'
ORDER BY
  USER_MENU_XID
```
**Resultado da Extração:**

{{TABLE_USER_MENUS}}

---

<div class="section-title">User Preferences</div>

<div class="meta-text" markdown="1">
**Sequência:** 7
**OTM Table:** USER_PREFERENCE_D
**Deployment Type:** Migration Project
**Migration Project ID:** BAU_MIG_OBJ_GOV_UI
**Saved Query ID:** MIG_USER_PREFERENCES
**Responsável:** ITC
**Tipo de Migração:** Técnica
**Documentação:** Pendente
**Migration Project:** Pendente
**Exportação:** Pendente
**Deploy:** Pendente
**Validação:** Pendente

</div>
**Query de Extração:**
```sql
SELECT
  DOMAIN_NAME,
  USER_PREFERENCE_GID,
  PREFERENCE_GID,
  USER_PREFERENCE_VALUE
FROM
  USER_PREFERENCE_D
ORDER BY
  USER_PREFERENCE_GID
```
**Resultado da Extração:**

{{TABLE_USER_PREFERENCES}}

---

<div class="section-title">Translation (Labels)</div>

<div class="meta-text" markdown="1">
**Sequência:** 0
**OTM Table:** TRANSLATION
**Deployment Type:** DB.XML
**Responsável:** ITC
**Tipo de Migração:** Técnica
**Documentação:** Concluído
**Migration Project:** N/A
**Exportação:** Concluído
**Deploy:** Concluído
**Validação:** Concluído

</div>
**Query de Extração:**
```sql
SELECT t.DOMAIN_NAME,
  t.TRANSLATION_GID,
  t.TRANSLATION_XID,
  t.TRANSLATION_TYPE,
  td.LANG,
  td.COUNTRY,
  td.VARIANT,
  td.TEXT
FROM
  TRANSLATION t,
  TRANSLATION_D td
WHERE
  t.TRANSLATION_GID = td.TRANSLATION_GID
  AND t.TRANSLATION_GID LIKE '%BAU%'
ORDER BY
  t.TRANSLATION_XID,
  td.LANG,
  td.COUNTRY,
  td.VARIANT
```
**Resultado da Extração:**

{{TABLE_TRANSLATION_(LABELS)}}

---

<div class="section-title">Manage User Access</div>

<div class="meta-text" markdown="1">
**Sequência:** 1
**OTM Table:** USER_ACCESS
**Deployment Type:** DB.XML
**Responsável:** ITC
**Tipo de Migração:** Técnica
**Documentação:** Concluído
**Migration Project:** N/A
**Exportação:** Concluído
**Deploy:** Concluído
**Validação:** Concluído

</div>
**Query de Extração:**
```sql
SELECT
  ua.DOMAIN_NAME,
  ua.USER_ACCESS_XID,
  ua.GL_USER_GID,
  ua.GL_LEVEL,
  ua.USER_ROLE_GID,
  uma.USER_MENU_LAYOUT_GID,
  upa.USER_PREFERENCE_GID,
  maa.MOBILE_ACTION_GID
FROM
  USER_ACCESS ua
  LEFT JOIN USER_MENU_ACCESS uma ON ua.USER_ACCESS_GID = uma.USER_ACCESS_GID
  LEFT JOIN USER_PREFERENCE_ACCESS upa ON ua.USER_ACCESS_GID = upa.USER_ACCESS_GID
  LEFT JOIN MOBILE_ACTION_ACCESS maa ON ua.USER_ACCESS_GID = maa.USER_ACCESS_GID
WHERE
  ua.DOMAIN_NAME = 'BAU'
ORDER BY
  ua.USER_ACCESS_GID
```
**Resultado da Extração:**

{{TABLE_MANAGE_USER_ACCESS}}

---

<div class="section-title">VPD Profile</div>

<div class="meta-text" markdown="1">
**Sequência:** 1
**OTM Table:** VPD_PROFILE
**Deployment Type:** DB.XML
**Responsável:** ITC
**Tipo de Migração:** Técnica
**Documentação:** Concluído
**Migration Project:** N/A
**Exportação:** Concluído
**Deploy:** Concluído
**Validação:** Concluído

</div>
**Query de Extração:**
```sql
SELECT
  *
FROM
  VPD_PROFILE
WHERE
  DOMAIN_NAME = 'BAU'
ORDER BY
  VPD_PROFILE_XID
```
**Resultado da Extração:**

{{TABLE_VPD_PROFILE}}

---

<div class="section-title">Relatorios (BI ZIP)</div>

<div class="meta-text" markdown="1">
**Sequência:** 0
**OTM Table:** BI_PUBLISHER_FILES
**Deployment Type:** Manual
**Migration Project ID:** **Saved
**Saved Query ID:** **Deployment
**Responsável:** ITC
**Tipo de Migração:** Técnica
**Documentação:** Pendente
**Migration Project:** Pendente
**Exportação:** Pendente
**Deploy:** Pendente
**Validação:** Pendente

</div>
**Query de Extração:**
```sql
SELECT
  DOMAIN_NAME,
  FILE_GID,
  FILE_NAME,
  FILE_TYPE,
  DESCRIPTION,
  CREATED_AT
FROM
  BI_PUBLISHER_FILES
WHERE
  DOMAIN_NAME = 'BAU'
ORDER BY
  FILE_NAME
```
**Resultado da Extração:**

{{TABLE_RELATORIOS_(BI_ZIP)}}

---
