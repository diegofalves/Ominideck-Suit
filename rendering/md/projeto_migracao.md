# Projeto de Migração - Configuração OTM Unificada (BR100 + Projeto)

## Identificação do Projeto

- **Código**: MIG0001
- **Versão**: 1.1
- **Consultor**: Diego Ferreira Alves
- **Ambiente Origem**: https://otmgtm-dev1-bauducco.otmgtm.us-phoenix-1.ocs.oraclecloud.com/
- **Ambiente Destino**: https://otmgtm-bauducco.otmgtm.us-phoenix-1.ocs.oraclecloud.com/

---

## Sumário

- Grupos e Objetos de Migração OTM

  - Grupo: Automação
  
    - Saved Queries
  
    - Saved Conditions
  
    - Data Type Association
  
    - Agent Event
  
    - Agents
  
    - App Actions
  
    - Actions
  
    - Batch Processes
  

  - Grupo: Configuração
  
    - Domains – Add Domain
  
    - Domain Grants
  
    - Domain Settings
  
    - Properties
  
    - Units of Measure (UOM)
  
    - Postal Code Components
  
    - Branding
  
    - Business Number
  
    - Reports
  
    - Transport Mode
  
    - BN Named Range
  

  - Grupo: Dados Mestres
  
    - Commodities
  
    - Corporations
  
    - Ship Unit Specs (THU)
  
    - Service Providers
  
    - Locations
  
    - Contacts
  
    - Equipment Groups
  
    - Items
  
    - Packaged Items
  
    - Contact Groups
  

  - Grupo: Extensão e Qualificadores
  
    - Location Refnum Qualifier
  
    - Order Release Refnum Qualifier
  
    - Order Release Line Refnum Qualifier
  
    - Packaged Item Refnum Qualifier
  
    - Item Refnum Qualifier
  
    - Shipment Refnum Qualifier
  
    - Shipment Stop Refnum Qualifier
  
    - Rate Geo Refnum Qualifier
  
    - Order Movement Refnum Qualifier
  
    - Status Types and Values
  
    - Remarks Qualifiers
  

  - Grupo: Planejamento
  
    - Audit Trail
  
    - Logic Configs
  
    - Parameter Sets
  
    - Accessorial Codes
  
    - Itinerary Leg
  
    - Itineraries
  
    - Itinerary Profiles
  
    - Load Configuration Rules
  
    - Load Configuration Setup
  
    - Order Release Types
  

  - Grupo: Integração
  
    - Stylesheet Contents
  
    - Stylesheet Profiles
  
    - XML Templates
  
    - Outbound XML Profiles
  
    - Document
  
    - Webservice
  
    - External Systems
  
    - External System Contact
  

  - Grupo: Governança e UI
  
    - Manager Layouts
  
    - Finder Sets
  
    - Workbenches
  
    - Business Monitors
  
    - Access Control Lists (ACL)
  
    - User Roles
  
    - User Menus
  
    - User Preferences
  
    - Translation (Labels)
  
    - Manage User Access
  
    - VPD Profile
  
    - Relatórios (BI ZIP)
  


---


## Objetivo do Projeto de Migração



Este projeto tem como objetivo executar a migração controlada e governada das configurações do Oracle Transportation Management (OTM), atualmente consolidadas e validadas no ambiente de homologação (HOM), para o ambiente de produção (PRD).




A migração visa unificar e padronizar o conjunto de objetos de configuração definidos no baseline BR100, incorporando também ajustes e extensões específicas do projeto Bauducco, garantindo consistência funcional, estabilidade operacional e aderência às melhores práticas de governança do OTM.




Com a execução desta migração em PROD, espera-se:





- disponibilizar integralmente as configurações necessárias para o planejamento, execução e monitoramento logístico;

- eliminar divergências entre ambientes que possam impactar comportamento de planejamento, rating, integração ou visibilidade operacional;

- assegurar rastreabilidade, capacidade de rollback e validação pós-migração, reduzindo riscos de impacto nas operações produtivas.





---





## Controle de Versão

**Versão Atual:** 1.1  
**Última Atualização:** 2026-02-02  
**Autor:** Diego Ferreira Alves

---




## Histórico de Alterações

| Data | Versão | Descrição | Autor |
|------|--------|-----------|--------|

| 2026-02-02 | 1.1 | Atualização do objetivo e alinhamento das seções de automação. | Diego Ferreira Alves |

| 2026-01-28 | 1.3 | Remoção do ícone de diamante das seções da tabela de roadmap e publicação do novo agrupamento de tipos de deploy (MANUAL, MIGRATION, CSV, DB.XML, ARQUIVO ZIP BI). | Diego Ferreira Alves |

| 2026-01-27 | 1.2 | Adoção do novo deploy type BUILDER-CONTROL e reforço na ordenação e no preenchimento automático das colunas da tabela Migration Project. | Diego Ferreira Alves |

| 2026-01-21 | 1.1 | Ajustes consolidados do painel de migração e da tabela Migration Project (tipos de deploy, colunas, links), reordenação dos objetos e atualização dos caches. | Diego Ferreira Alves |

| 2026-01-18 | 1.0 | Criação inicial do documento. | Diego Ferreira Alves |


---




## Grupos e Objetos de Migração OTM

Esta seção apresenta os conjuntos de objetos do Oracle Transportation Management (OTM) contemplados no escopo de migração.

---



### Grupo: Automação


Esta seção concentra os objetos responsáveis pela execução automática de regras e fluxos operacionais no OTM, como Saved Queries, Conditions e lógicas de acionamento utilizadas por Agents e processos batch. O conteúdo evidencia como cada automação está associada a um deploy type específico (MANUAL, MIGRATION, CSV, DB.XML, ZIP BI), permitindo rastrear impactos da migração sobre fluxos automáticos, dependências técnicas e a ordem correta de implantação no roadmap do projeto.




### Saved Queries

Queries utilizadas por automações, conditions e agents

<div class="meta-text" markdown="1">
**Sequência:** 1
**Object Type:** SAVED_QUERY
**OTM Table:** 
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC
**Tipo de Migração:** 


**Documentação:** DONE
**Migration Project:** DONE
**Exportação:** DONE
**Deploy:** DONE
**Validação:** DONE
</div>


**Conteúdo Técnico:**
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



### Query de Extração
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



### Saved Conditions

Conditions utilizadas por agents e eventos

<div class="meta-text" markdown="1">
**Sequência:** 2
**Object Type:** SAVED_CONDITION
**OTM Table:** 
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC
**Tipo de Migração:** 


**Documentação:** DONE
**Migration Project:** DONE
**Exportação:** DONE
**Deploy:** DONE
**Validação:** DONE
</div>


**Conteúdo Técnico:**
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



### Query de Extração
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



### Data Type Association

Associações de tipos de dados do sistema

<div class="meta-text" markdown="1">
**Sequência:** 3
**Object Type:** DATA_TYPE_ASSOCIATION
**OTM Table:** 
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC
**Tipo de Migração:** 


**Documentação:** DONE
**Migration Project:** DONE
**Exportação:** DONE
**Deploy:** DONE
**Validação:** DONE
</div>


**Conteúdo Técnico:**
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



### Query de Extração
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



### Agent Event

Eventos de agentes do sistema

<div class="meta-text" markdown="1">
**Sequência:** 4
**Object Type:** AGENT_EVENT
**OTM Table:** 
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC
**Tipo de Migração:** 


**Documentação:** DONE
**Migration Project:** DONE
**Exportação:** DONE
**Deploy:** DONE
**Validação:** DONE
</div>


**Conteúdo Técnico:**
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



### Query de Extração
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



### Agents

Agentes ativos no domínio

<div class="meta-text" markdown="1">
**Sequência:** 5
**Object Type:** AGENT
**OTM Table:** 
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC
**Tipo de Migração:** 


**Documentação:** DONE
**Migration Project:** DONE
**Exportação:** DONE
**Deploy:** DONE
**Validação:** DONE
</div>


**Conteúdo Técnico:**
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



### Query de Extração
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



### App Actions

Ações de aplicação do OTM

<div class="meta-text" markdown="1">
**Sequência:** 6
**Object Type:** APP_ACTION
**OTM Table:** 
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC
**Tipo de Migração:** 


**Documentação:** DONE
**Migration Project:** DONE
**Exportação:** DONE
**Deploy:** DONE
**Validação:** DONE
</div>


**Conteúdo Técnico:**
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



### Query de Extração
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



### Actions

Ações gerais do sistema

<div class="meta-text" markdown="1">
**Sequência:** 7
**Object Type:** ACTION
**OTM Table:** 
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC
**Tipo de Migração:** 


**Documentação:** DONE
**Migration Project:** DONE
**Exportação:** DONE
**Deploy:** DONE
**Validação:** DONE
</div>


**Conteúdo Técnico:**
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



### Query de Extração
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



### Batch Processes

Processos batch de execução automática

<div class="meta-text" markdown="1">
**Sequência:** 8
**Object Type:** BATCH_PROCESS
**OTM Table:** 
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC
**Tipo de Migração:** 


**Documentação:** DONE
**Migration Project:** DONE
**Exportação:** DONE
**Deploy:** DONE
**Validação:** DONE
</div>


**Conteúdo Técnico:**
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



### Query de Extração
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




### Grupo: Configuração


Reúne configurações centrais do domínio OTM, incluindo domínios, grants, parâmetros e propriedades que sustentam a operação e o baseline de migração.




### Domains – Add Domain

Configuração de domínios OTM

<div class="meta-text" markdown="1">
**Sequência:** 1
**Object Type:** DOMAIN
**OTM Table:** 
**Deployment Type:** MANUAL


**Responsável:** ITC
**Tipo de Migração:** 


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


**Conteúdo Técnico:**
```sql
SELECT * FROM DOMAIN
```



### Query de Extração
```sql
SELECT * FROM DOMAIN
```



### Domain Grants

Permissões de domínio

<div class="meta-text" markdown="1">
**Sequência:** 2
**Object Type:** DOMAIN_GRANTS_MADE
**OTM Table:** 
**Deployment Type:** MANUAL


**Responsável:** ITC
**Tipo de Migração:** 


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


**Conteúdo Técnico:**
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



### Query de Extração
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



### Domain Settings

Configurações de domínio

<div class="meta-text" markdown="1">
**Sequência:** 3
**Object Type:** DOMAIN_SETTING
**OTM Table:** 
**Deployment Type:** MANUAL


**Responsável:** ITC
**Tipo de Migração:** 


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


**Conteúdo Técnico:**
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



### Query de Extração
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



### Properties

Propriedades do sistema

<div class="meta-text" markdown="1">
**Sequência:** 4
**Object Type:** PROP_INSTRUCTION
**OTM Table:** 
**Deployment Type:** MANUAL


**Responsável:** ITC
**Tipo de Migração:** 


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


**Conteúdo Técnico:**
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



### Query de Extração
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



### Units of Measure (UOM)

Unidades de medida utilizadas no domínio

<div class="meta-text" markdown="1">
**Sequência:** 5
**Object Type:** UOM
**OTM Table:** 
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC
**Tipo de Migração:** 


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


**Conteúdo Técnico:**
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



### Query de Extração
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



### Postal Code Components

Componentes de código postal

<div class="meta-text" markdown="1">
**Sequência:** 6
**Object Type:** HNAME_COMPONENT
**OTM Table:** 
**Deployment Type:** DB_XML


**Responsável:** ITC
**Tipo de Migração:** 


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


**Conteúdo Técnico:**
```sql
SELECT * FROM HNAME_COMPONENT ORDER BY HNAME_COMPONENT_XID
```



### Query de Extração
```sql
SELECT * FROM HNAME_COMPONENT ORDER BY HNAME_COMPONENT_XID
```



### Branding

Configuração de marca e identidade visual

<div class="meta-text" markdown="1">
**Sequência:** 7
**Object Type:** BRANDING
**OTM Table:** 
**Deployment Type:** MANUAL


**Responsável:** ITC
**Tipo de Migração:** 


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>






### Business Number

Regras de números de negócio

<div class="meta-text" markdown="1">
**Sequência:** 8
**Object Type:** BN_RULE
**OTM Table:** 
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC
**Tipo de Migração:** 


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


**Conteúdo Técnico:**
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



### Query de Extração
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



### Reports

Relatórios do sistema

<div class="meta-text" markdown="1">
**Sequência:** 9
**Object Type:** REPORT
**OTM Table:** 
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC
**Tipo de Migração:** 


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


**Conteúdo Técnico:**
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



### Query de Extração
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



### Transport Mode

Modos de transporte

<div class="meta-text" markdown="1">
**Sequência:** 10
**Object Type:** TRANSPORT_MODE
**OTM Table:** 
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC
**Tipo de Migração:** 


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


**Conteúdo Técnico:**
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



### Query de Extração
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



### BN Named Range

Intervalo nomeado de números de negócio

<div class="meta-text" markdown="1">
**Sequência:** 11
**Object Type:** BN_NAMED_RANGE
**OTM Table:** 
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC
**Tipo de Migração:** 


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


**Conteúdo Técnico:**
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



### Query de Extração
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




### Grupo: Dados Mestres


Contém cadastros mestres essenciais para planejamento e execução logística (commodities, corporações, unidades de embarque, transportadoras etc.), garantindo consistência entre ambientes.




### Commodities

Cadastro de commodities vinculadas a itens

<div class="meta-text" markdown="1">
**Sequência:** 1
**Object Type:** COMMODITY
**OTM Table:** 
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC
**Tipo de Migração:** 


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


**Conteúdo Técnico:**
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



### Query de Extração
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



### Corporations

Entidades corporativas e empresas

<div class="meta-text" markdown="1">
**Sequência:** 2
**Object Type:** CORPORATION
**OTM Table:** 
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC
**Tipo de Migração:** 


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


**Conteúdo Técnico:**
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



### Query de Extração
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



### Ship Unit Specs (THU)

Especificações de unidades de transporte

<div class="meta-text" markdown="1">
**Sequência:** 3
**Object Type:** SHIP_UNIT_SPEC
**OTM Table:** 
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC
**Tipo de Migração:** 


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


**Conteúdo Técnico:**
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



### Query de Extração
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



### Service Providers

Transportadoras e prestadores de serviço

<div class="meta-text" markdown="1">
**Sequência:** 4
**Object Type:** SERVPROV
**OTM Table:** 
**Deployment Type:** CSV


**Responsável:** ITC
**Tipo de Migração:** 


**Documentação:** PENDING
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** PENDING
**Validação:** PENDING
</div>


**Conteúdo Técnico:**
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



### Query de Extração
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



### Locations

Localizações e endereços

<div class="meta-text" markdown="1">
**Sequência:** 5
**Object Type:** LOCATION
**OTM Table:** 
**Deployment Type:** INTEGRATION


**Responsável:** ITC
**Tipo de Migração:** 


**Documentação:** PENDING
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** PENDING
**Validação:** PENDING
</div>


**Conteúdo Técnico:**
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



### Query de Extração
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



### Contacts

Contatos e informações de pessoas

<div class="meta-text" markdown="1">
**Sequência:** 6
**Object Type:** CONTACT
**OTM Table:** 
**Deployment Type:** CSV


**Responsável:** ITC
**Tipo de Migração:** 


**Documentação:** PENDING
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** PENDING
**Validação:** PENDING
</div>


**Conteúdo Técnico:**
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



### Query de Extração
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



### Equipment Groups

Grupos de equipamentos

<div class="meta-text" markdown="1">
**Sequência:** 7
**Object Type:** EQUIPMENT_GROUP
**OTM Table:** 
**Deployment Type:** CSV


**Responsável:** ITC
**Tipo de Migração:** 


**Documentação:** PENDING
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** PENDING
**Validação:** PENDING
</div>


**Conteúdo Técnico:**
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



### Query de Extração
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



### Items

Itens e produtos

<div class="meta-text" markdown="1">
**Sequência:** 8
**Object Type:** ITEM
**OTM Table:** 
**Deployment Type:** INTEGRATION


**Responsável:** ITC
**Tipo de Migração:** 


**Documentação:** PENDING
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** PENDING
**Validação:** PENDING
</div>


**Conteúdo Técnico:**
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



### Query de Extração
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



### Packaged Items

Itens embalados

<div class="meta-text" markdown="1">
**Sequência:** 9
**Object Type:** PACKAGED_ITEM
**OTM Table:** 
**Deployment Type:** INTEGRATION


**Responsável:** ITC
**Tipo de Migração:** 


**Documentação:** PENDING
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** PENDING
**Validação:** PENDING
</div>


**Conteúdo Técnico:**
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



### Query de Extração
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



### Contact Groups

Grupos de contatos

<div class="meta-text" markdown="1">
**Sequência:** 10
**Object Type:** CONTACT_GROUP
**OTM Table:** 
**Deployment Type:** CSV


**Responsável:** ITC
**Tipo de Migração:** 


**Documentação:** PENDING
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** PENDING
**Validação:** PENDING
</div>


**Conteúdo Técnico:**
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



### Query de Extração
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




### Grupo: Extensão e Qualificadores


Agrupa qualificadores, códigos e extensões necessárias para classificação, tributação ou regras específicas de negócio do projeto.




### Location Refnum Qualifier

Qualificador de número de referência de localização

<div class="meta-text" markdown="1">
**Sequência:** 1
**Object Type:** LOCATION_REFNUM_QUAL
**OTM Table:** 
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC
**Tipo de Migração:** 


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


**Conteúdo Técnico:**
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



### Query de Extração
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



### Order Release Refnum Qualifier

Qualificador de número de referência de liberação de pedido

<div class="meta-text" markdown="1">
**Sequência:** 2
**Object Type:** ORDER_RELEASE_REFNUM_QUAL
**OTM Table:** 
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC
**Tipo de Migração:** 


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


**Conteúdo Técnico:**
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



### Query de Extração
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



### Order Release Line Refnum Qualifier

Qualificador de número de referência de linha de liberação

<div class="meta-text" markdown="1">
**Sequência:** 3
**Object Type:** ORDER_RELEASE_LINE_REFNUM_QUAL
**OTM Table:** 
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC
**Tipo de Migração:** 


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


**Conteúdo Técnico:**
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



### Query de Extração
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



### Packaged Item Refnum Qualifier

Qualificador de número de referência de item embalado

<div class="meta-text" markdown="1">
**Sequência:** 4
**Object Type:** PACKAGED_ITEM_REFNUM_QUAL
**OTM Table:** 
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC
**Tipo de Migração:** 


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


**Conteúdo Técnico:**
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



### Query de Extração
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



### Item Refnum Qualifier

Qualificador de número de referência de item

<div class="meta-text" markdown="1">
**Sequência:** 5
**Object Type:** ITEM_REFNUM_QUAL
**OTM Table:** 
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC
**Tipo de Migração:** 


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


**Conteúdo Técnico:**
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



### Query de Extração
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



### Shipment Refnum Qualifier

Qualificador de número de referência de remessa

<div class="meta-text" markdown="1">
**Sequência:** 6
**Object Type:** SHIPMENT_REFNUM_QUAL
**OTM Table:** 
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC
**Tipo de Migração:** 


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


**Conteúdo Técnico:**
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



### Query de Extração
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



### Shipment Stop Refnum Qualifier

Qualificador de número de referência de parada de remessa

<div class="meta-text" markdown="1">
**Sequência:** 7
**Object Type:** SHIPMENT_STOP_REFNUM_QUAL
**OTM Table:** 
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC
**Tipo de Migração:** 


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


**Conteúdo Técnico:**
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



### Query de Extração
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



### Rate Geo Refnum Qualifier

Qualificador de número de referência de taxa geográfica

<div class="meta-text" markdown="1">
**Sequência:** 8
**Object Type:** RATE_GEO_REFNUM_QUAL
**OTM Table:** 
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC
**Tipo de Migração:** 


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


**Conteúdo Técnico:**
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



### Query de Extração
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



### Order Movement Refnum Qualifier

Qualificador de número de referência de movimento de pedido

<div class="meta-text" markdown="1">
**Sequência:** 9
**Object Type:** OM_REFNUM_QUAL
**OTM Table:** 
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC
**Tipo de Migração:** 


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


**Conteúdo Técnico:**
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



### Query de Extração
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



### Status Types and Values

Tipos e valores de status do sistema

<div class="meta-text" markdown="1">
**Sequência:** 10
**Object Type:** STATUS_TYPE
**OTM Table:** 
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC
**Tipo de Migração:** 


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


**Conteúdo Técnico:**
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



### Query de Extração
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



### Remarks Qualifiers

Qualificadores de observações

<div class="meta-text" markdown="1">
**Sequência:** 11
**Object Type:** REMARK_QUAL
**OTM Table:** 
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC
**Tipo de Migração:** 


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


**Conteúdo Técnico:**
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



### Query de Extração
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




### Grupo: Planejamento


Foca em tabelas e estruturas que suportam o planejamento e execução de cargas, perfis de roteirização e configuração de transporte.




### Audit Trail

Trilha de auditoria do sistema

<div class="meta-text" markdown="1">
**Sequência:** 1
**Object Type:** AUDIT_TRAIL
**OTM Table:** 
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC
**Tipo de Migração:** 


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


**Conteúdo Técnico:**
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



### Query de Extração
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



### Logic Configs

Configurações de lógica de planejamento

<div class="meta-text" markdown="1">
**Sequência:** 2
**Object Type:** LOGIC_PARAMETER
**OTM Table:** 
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC
**Tipo de Migração:** 


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


**Conteúdo Técnico:**
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



### Query de Extração
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



### Parameter Sets

Conjuntos de parâmetros de planejamento

<div class="meta-text" markdown="1">
**Sequência:** 3
**Object Type:** PLANNING_PARAMETER
**OTM Table:** 
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC
**Tipo de Migração:** 


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


**Conteúdo Técnico:**
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



### Query de Extração
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



### Accessorial Codes

Códigos de serviços acessórios

<div class="meta-text" markdown="1">
**Sequência:** 4
**Object Type:** ACCESSORIAL_CODE
**OTM Table:** 
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC
**Tipo de Migração:** 


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


**Conteúdo Técnico:**
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



### Query de Extração
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



### Itinerary Leg

Trechos de itinerário

<div class="meta-text" markdown="1">
**Sequência:** 5
**Object Type:** LEG
**OTM Table:** 
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC
**Tipo de Migração:** 


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


**Conteúdo Técnico:**
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



### Query de Extração
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



### Itineraries

Itinerários de transporte

<div class="meta-text" markdown="1">
**Sequência:** 6
**Object Type:** ITINERARY
**OTM Table:** 
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC
**Tipo de Migração:** 


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


**Conteúdo Técnico:**
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



### Query de Extração
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



### Itinerary Profiles

Perfis de itinerários

<div class="meta-text" markdown="1">
**Sequência:** 7
**Object Type:** ITINERARY_PROFILE
**OTM Table:** 
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC
**Tipo de Migração:** 


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


**Conteúdo Técnico:**
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



### Query de Extração
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



### Load Configuration Rules

Regras de configuração de carregamento

<div class="meta-text" markdown="1">
**Sequência:** 8
**Object Type:** LOAD_CONFIG_RULE
**OTM Table:** 
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC
**Tipo de Migração:** 


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


**Conteúdo Técnico:**
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



### Query de Extração
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



### Load Configuration Setup

Configuração de carregamento

<div class="meta-text" markdown="1">
**Sequência:** 9
**Object Type:** LOAD_CONFIG_SETUP
**OTM Table:** 
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC
**Tipo de Migração:** 


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


**Conteúdo Técnico:**
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



### Query de Extração
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



### Order Release Types

Tipos de liberação de pedido

<div class="meta-text" markdown="1">
**Sequência:** 10
**Object Type:** ORDER_RELEASE_TYPE
**OTM Table:** 
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC
**Tipo de Migração:** 


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


**Conteúdo Técnico:**
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



### Query de Extração
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




### Grupo: Integração


Inclui objetos relacionados a integração e mensageria (templates, perfis XML, web services e sistemas externos) assegurando comunicação entre OTM e sistemas parceiros.




### Stylesheet Contents

Conteúdos de folhas de estilo

<div class="meta-text" markdown="1">
**Sequência:** 1
**Object Type:** STYLESHEET_CONTENT
**OTM Table:** 
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC
**Tipo de Migração:** 


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


**Conteúdo Técnico:**
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



### Query de Extração
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



### Stylesheet Profiles

Perfis de folhas de estilo

<div class="meta-text" markdown="1">
**Sequência:** 2
**Object Type:** STYLESHEET_PROFILE
**OTM Table:** 
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC
**Tipo de Migração:** 


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


**Conteúdo Técnico:**
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



### Query de Extração
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



### XML Templates

Templates XML para integração

<div class="meta-text" markdown="1">
**Sequência:** 3
**Object Type:** XML_TEMPLATE
**OTM Table:** 
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC
**Tipo de Migração:** 


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


**Conteúdo Técnico:**
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



### Query de Extração
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



### Outbound XML Profiles

Perfis de XML de saída

<div class="meta-text" markdown="1">
**Sequência:** 4
**Object Type:** OUT_XML_PROFILE
**OTM Table:** 
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC
**Tipo de Migração:** 


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


**Conteúdo Técnico:**
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



### Query de Extração
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



### Document

Documentos do sistema

<div class="meta-text" markdown="1">
**Sequência:** 5
**Object Type:** DOCUMENT
**OTM Table:** 
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC
**Tipo de Migração:** 


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


**Conteúdo Técnico:**
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



### Query de Extração
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



### Webservice

Serviços web para integração

<div class="meta-text" markdown="1">
**Sequência:** 6
**Object Type:** WEB_SERVICE
**OTM Table:** 
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC
**Tipo de Migração:** 


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


**Conteúdo Técnico:**
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



### Query de Extração
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



### External Systems

Configuração de sistemas externos

<div class="meta-text" markdown="1">
**Sequência:** 7
**Object Type:** EXTERNAL_SYSTEM
**OTM Table:** 
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC
**Tipo de Migração:** 


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


**Conteúdo Técnico:**
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



### Query de Extração
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



### External System Contact

Contatos de sistemas externos

<div class="meta-text" markdown="1">
**Sequência:** 8
**Object Type:** EXTERNAL_CONTACT
**OTM Table:** 
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC
**Tipo de Migração:** 


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


**Conteúdo Técnico:**
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



### Query de Extração
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




### Grupo: Governança e UI


Abriga objetos de governança, segurança e experiência do usuário (layouts, ACLs, roles, menus, traduções), garantindo aderência às políticas de acesso e usabilidade.




### Manager Layouts

Layouts de gerenciamento do OTM

<div class="meta-text" markdown="1">
**Sequência:** 1
**Object Type:** MANAGER_LAYOUT
**OTM Table:** 
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC
**Tipo de Migração:** 


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** PENDING
**Validação:** PENDING
</div>


**Conteúdo Técnico:**
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



### Query de Extração
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



### Finder Sets

Conjuntos de busca e filtros

<div class="meta-text" markdown="1">
**Sequência:** 2
**Object Type:** FINDER_SET
**OTM Table:** 
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC
**Tipo de Migração:** 


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** PENDING
**Validação:** PENDING
</div>


**Conteúdo Técnico:**
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



### Query de Extração
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



### Workbenches

Bancadas de trabalho do OTM

<div class="meta-text" markdown="1">
**Sequência:** 3
**Object Type:** TRANSPORTATION_WORKBENCH
**OTM Table:** 
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC
**Tipo de Migração:** 


**Documentação:** PENDING
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** PENDING
**Validação:** PENDING
</div>


**Conteúdo Técnico:**
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



### Query de Extração
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



### Business Monitors

Monitores de negócio

<div class="meta-text" markdown="1">
**Sequência:** 4
**Object Type:** BUSINESS_MONITOR_D
**OTM Table:** 
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC
**Tipo de Migração:** 


**Documentação:** PENDING
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** PENDING
**Validação:** PENDING
</div>


**Conteúdo Técnico:**
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



### Query de Extração
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



### Access Control Lists (ACL)

Listas de controle de acesso

<div class="meta-text" markdown="1">
**Sequência:** 5
**Object Type:** ACR_ROLE
**OTM Table:** 
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC
**Tipo de Migração:** 


**Documentação:** PENDING
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** PENDING
**Validação:** PENDING
</div>


**Conteúdo Técnico:**
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



### Query de Extração
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



### User Roles

Papéis de usuário

<div class="meta-text" markdown="1">
**Sequência:** 6
**Object Type:** USER_ROLE
**OTM Table:** 
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC
**Tipo de Migração:** 


**Documentação:** PENDING
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** PENDING
**Validação:** PENDING
</div>


**Conteúdo Técnico:**
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



### Query de Extração
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



### User Menus

Menus de usuário

<div class="meta-text" markdown="1">
**Sequência:** 7
**Object Type:** USER_MENU
**OTM Table:** 
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC
**Tipo de Migração:** 


**Documentação:** PENDING
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** PENDING
**Validação:** PENDING
</div>


**Conteúdo Técnico:**
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



### Query de Extração
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



### User Preferences

Preferências de usuário

<div class="meta-text" markdown="1">
**Sequência:** 8
**Object Type:** USER_PREFERENCE_D
**OTM Table:** 
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC
**Tipo de Migração:** 


**Documentação:** PENDING
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** PENDING
**Validação:** PENDING
</div>


**Conteúdo Técnico:**
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



### Query de Extração
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



### Translation (Labels)

Traduções e rótulos do sistema

<div class="meta-text" markdown="1">
**Sequência:** 9
**Object Type:** TRANSLATION
**OTM Table:** 
**Deployment Type:** DB_XML


**Responsável:** ITC
**Tipo de Migração:** 


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


**Conteúdo Técnico:**
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



### Query de Extração
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



### Manage User Access

Gerenciamento de acesso de usuário

<div class="meta-text" markdown="1">
**Sequência:** 10
**Object Type:** USER_ACCESS
**OTM Table:** 
**Deployment Type:** DB_XML


**Responsável:** ITC
**Tipo de Migração:** 


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


**Conteúdo Técnico:**
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



### Query de Extração
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



### VPD Profile

Perfil de segurança em nível de dados

<div class="meta-text" markdown="1">
**Sequência:** 11
**Object Type:** VPD_PROFILE
**OTM Table:** 
**Deployment Type:** DB_XML


**Responsável:** ITC
**Tipo de Migração:** 


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


**Conteúdo Técnico:**
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



### Query de Extração
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



### Relatórios (BI ZIP)

Relatórios e arquivos BI

<div class="meta-text" markdown="1">
**Sequência:** 12
**Object Type:** BI_PUBLISHER_FILES
**OTM Table:** 
**Deployment Type:** MANUAL


**Responsável:** ITC
**Tipo de Migração:** 


**Documentação:** PENDING
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** PENDING
**Validação:** PENDING
</div>






