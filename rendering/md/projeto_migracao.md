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
  
    - Saved Conditions
  
    - Data Type Association
  
    - Agent Event
  
    - Agents
  
    - App Actions
  
    - Actions
  
    - Batch Processes
  
    - SAVED_CONDITION_QUERY (BAU - AUTO)
  
    - AGENT_EVENT_DETAILS (AUTO)
  
    - STYLESHEET_CONTENT (BAU - AUTO)
  
    - BATCH_PROCESS_D (AUTO)
  

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
  
    - LOCATION_REFNUM (AUTO)
  
    - CONTACT_COM_METHOD (AUTO)
  
    - STYLESHEET_PROFILE (BAU - AUTO)
  
    - STYLESHEET_CONTENT (PUBLIC - AUTO)
  

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
  
    - STATUS_VALUE (BAU - AUTO)
  

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
  
    - NOTIFY_SUBJECT_CONTACT (AUTO)
  
    - ITINERARY_DETAIL (AUTO)
  
    - ITINERARY_PROFILE_D (AUTO)
  
    - LOAD_CONFIG_SETUP_ORIENTATION (AUTO)
  

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
  
    - USER_ROLE_ACR_ROLE (BAU - AUTO)
  
    - TRANSLATION_D (AUTO)
  
    - USER_MENU_ACCESS (BAU - AUTO)
  
    - USER_PREFERENCE_ACCESS (BAU - AUTO)
  


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
**Última Atualização:** 02/02/2026  
**Autor:** Diego Ferreira Alves

---




## Histórico de Alterações

| Data | Versão | Descrição | Autor |
|------|--------|-----------|--------|

| 02/02/2026 | 1.1 | Atualização do objetivo e alinhamento das seções de automação. | Diego Ferreira Alves |

| 28/01/2026 | 1.3 | Remoção do ícone de diamante das seções da tabela de roadmap e publicação do novo agrupamento de tipos de deploy (MANUAL, MIGRATION, CSV, DB.XML, ARQUIVO ZIP BI). | Diego Ferreira Alves |

| 27/01/2026 | 1.2 | Adoção do novo deploy type BUILDER-CONTROL e reforço na ordenação e no preenchimento automático das colunas da tabela Migration Project. | Diego Ferreira Alves |

| 21/01/2026 | 1.1 | Ajustes consolidados do painel de migração e da tabela Migration Project (tipos de deploy, colunas, links), reordenação dos objetos e atualização dos caches. | Diego Ferreira Alves |

| 18/01/2026 | 1.0 | Criação inicial do documento. | Diego Ferreira Alves |


---


## Roadmap de Migração

Este capítulo apresenta a estratégia de execução da migração, agrupada por tipo de implantação (Deployment Type). Cada bloco representa um grupo coeso de objetos que devem ser migrados seguindo a mesma tática operacional.






















































































































































































































































































































































































### MANUAL


Implantação manual no ambiente de destino. Objetos que requerem ação humana direta e validação específica.


**Objetos nesta estratégia:** 6


- Domains – Add Domain

- Domain Grants

- Domain Settings

- Properties

- Branding

- Relatórios (BI ZIP)


---




### MIGRATION_PROJECT


Migração via projeto de migração nativo do OTM. Objetos transportados com configurações relacionadas.


**Objetos nesta estratégia:** 62


- Saved Conditions

- Data Type Association

- Agent Event

- Agents

- App Actions

- Actions

- Batch Processes

- SAVED_CONDITION_QUERY (BAU - AUTO)

- AGENT_EVENT_DETAILS (AUTO)

- STYLESHEET_CONTENT (BAU - AUTO)

- BATCH_PROCESS_D (AUTO)

- Units of Measure (UOM)

- Business Number

- Reports

- Transport Mode

- BN Named Range

- Commodities

- Corporations

- Ship Unit Specs (THU)

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

- STATUS_VALUE (BAU - AUTO)

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

- NOTIFY_SUBJECT_CONTACT (AUTO)

- ITINERARY_DETAIL (AUTO)

- ITINERARY_PROFILE_D (AUTO)

- LOAD_CONFIG_SETUP_ORIENTATION (AUTO)

- Stylesheet Contents

- Stylesheet Profiles

- XML Templates

- Outbound XML Profiles

- Document

- Webservice

- External Systems

- External System Contact

- Manager Layouts

- Finder Sets

- Workbenches

- Business Monitors

- Access Control Lists (ACL)

- User Roles

- User Menus

- User Preferences

- USER_ROLE_ACR_ROLE (BAU - AUTO)


---




### CSV


Importação via arquivos CSV. Dados estruturados em formato de valores separados por vírgula.


**Objetos nesta estratégia:** 8


- Service Providers

- Locations

- Contacts

- Equipment Groups

- Contact Groups

- LOCATION_REFNUM (AUTO)

- CONTACT_COM_METHOD (AUTO)

- STYLESHEET_CONTENT (PUBLIC - AUTO)


---








## Grupos e Objetos de Migração OTM

Esta seção apresenta os conjuntos de objetos do Oracle Transportation Management (OTM) contemplados no escopo de migração.

---


### Grupo: Automação


Esta seção concentra os objetos responsáveis pela execução automática de regras e fluxos operacionais no OTM, como Saved Queries, Conditions e lógicas de acionamento utilizadas por Agents e processos batch. O conteúdo evidencia como cada automação está associada a um deploy type específico (MANUAL, MIGRATION, CSV, DB.XML, ZIP BI), permitindo rastrear impactos da migração sobre fluxos automáticos, dependências técnicas e a ordem correta de implantação no roadmap do projeto.




### Saved Conditions

GC3 Identificador global da entidade. É criado concatenando o nome de domínio,'.' e XID.

<div class="meta-text" markdown="1">
**Sequência:** 2
**Object Type:** SAVED_CONDITION
**OTM Table:** SAVED_CONDITION
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC


**Documentação:** DONE
**Migration Project:** DONE
**Exportação:** DONE
**Deploy:** DONE
**Validação:** DONE
</div>


### Query de Extração de Objetos
```sql
SELECT *
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

Identificador exclusivo de associação de tipo de dados.

<div class="meta-text" markdown="1">
**Sequência:** 3
**Object Type:** DATA_TYPE_ASSOCIATION
**OTM Table:** DATA_TYPE_ASSOCIATION
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC


**Documentação:** DONE
**Migration Project:** DONE
**Exportação:** DONE
**Deploy:** DONE
**Validação:** DONE
</div>


### Query de Extração de Objetos
```sql
SELECT *
FROM
  DATA_TYPE_ASSOCIATION
WHERE
  DOMAIN_NAME = 'BAU'
ORDER BY
  DATA_TYPE_ASSOCIATION_XID
```





### Agent Event

GC3 Identificador global da entidade. É criado concatenando o nome de domínio,'.' e XID.

<div class="meta-text" markdown="1">
**Sequência:** 4
**Object Type:** AGENT_EVENT
**OTM Table:** AGENT_EVENT
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC


**Documentação:** DONE
**Migration Project:** DONE
**Exportação:** DONE
**Deploy:** DONE
**Validação:** DONE
</div>


### Query de Extração de Objetos
```sql
SELECT *
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

GC3 Identificador global da entidade. É criado concatenando o nome de domínio,'.' e XID.

<div class="meta-text" markdown="1">
**Sequência:** 5
**Object Type:** AGENT
**OTM Table:** AGENT
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC


**Documentação:** DONE
**Migration Project:** DONE
**Exportação:** DONE
**Deploy:** DONE
**Validação:** DONE
</div>


### Query de Extração de Objetos
```sql
SELECT *
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





### App Actions

Se Y, o objeto de negócios será bloqueado durante a chamada de ação. O pode bloquear vários objetos de negócios para ações de UI/planejamento.

<div class="meta-text" markdown="1">
**Sequência:** 6
**Object Type:** APP_ACTION
**OTM Table:** APP_ACTION
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC


**Documentação:** DONE
**Migration Project:** DONE
**Exportação:** DONE
**Deploy:** DONE
**Validação:** DONE
</div>


### Query de Extração de Objetos
```sql
SELECT *
FROM
  APP_ACTION
WHERE
  DOMAIN_NAME = 'BAU'
ORDER BY
  ACTION_XID
```





### Actions

Esta tabela contém a lista de todas as ações possíveis da interface do usuário que podem ser executadas no GC3.

<div class="meta-text" markdown="1">
**Sequência:** 7
**Object Type:** ACTION
**OTM Table:** ACTION
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC


**Documentação:** DONE
**Migration Project:** DONE
**Exportação:** DONE
**Deploy:** DONE
**Validação:** DONE
</div>


### Query de Extração de Objetos
```sql
SELECT *
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





### Batch Processes

Especifica um grupo de processos em lote. Isso é usado para identificar um grupo de processos que são executados como uma cadeia.

<div class="meta-text" markdown="1">
**Sequência:** 8
**Object Type:** BATCH_PROCESS
**OTM Table:** BATCH_PROCESS
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC


**Documentação:** DONE
**Migration Project:** DONE
**Exportação:** DONE
**Deploy:** DONE
**Validação:** DONE
</div>


### Query de Extração de Objetos
```sql
SELECT *
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





### SAVED_CONDITION_QUERY (BAU - AUTO)

GC3 Identificador global da entidade. É criado concatenando o nome de domínio,'.' e XID.

<div class="meta-text" markdown="1">
**Sequência:** 453
**Object Type:** SAVED_CONDITION_QUERY
**OTM Table:** SAVED_CONDITION_QUERY
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC


**Documentação:** DONE
**Migration Project:** DONE
**Exportação:** DONE
**Deploy:** DONE
**Validação:** DONE
</div>


### Query de Extração de Objetos
```sql
SELECT *
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





### AGENT_EVENT_DETAILS (AUTO)

GC3 Identificador global da entidade. É criado concatenando o nome de domínio,'.' e XID.

<div class="meta-text" markdown="1">
**Sequência:** 14
**Object Type:** AGENT_EVENT_DETAILS
**OTM Table:** AGENT_EVENT_DETAILS
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC


**Documentação:** DONE
**Migration Project:** DONE
**Exportação:** DONE
**Deploy:** DONE
**Validação:** DONE
</div>


### Query de Extração de Objetos
```sql
SELECT *
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





### STYLESHEET_CONTENT (BAU - AUTO)

ID da versão – string de versão completa.

<div class="meta-text" markdown="1">
**Sequência:** 463
**Object Type:** STYLESHEET_CONTENT
**OTM Table:** STYLESHEET_CONTENT
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC


**Documentação:** DONE
**Migration Project:** DONE
**Exportação:** DONE
**Deploy:** DONE
**Validação:** DONE
</div>


### Query de Extração de Objetos
```sql
SELECT *
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





### BATCH_PROCESS_D (AUTO)

Especifica os processos que serão executados em um grupo de processos em lote.

<div class="meta-text" markdown="1">
**Sequência:** 38
**Object Type:** BATCH_PROCESS_D
**OTM Table:** BATCH_PROCESS_D
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC


**Documentação:** DONE
**Migration Project:** DONE
**Exportação:** DONE
**Deploy:** DONE
**Validação:** DONE
</div>


### Query de Extração de Objetos
```sql
SELECT *
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

Domínio é um conceito do GC3 que cria um grupo por cliente. Quando um cliente (remetente/provedor de serviços) instala o GC3 pela primeira vez, ele cria um domínio para si mesmo. Todos os dados subsequentes desse cliente são então anexados ao domínio. Isso cria um agrupamento lógico dos dados por cliente no GC3. Isso também permite que o GC3 hospede dados de vários clientes simultaneamente em um banco de dados GC3. Este conceito pode ser pensado como um espaço de dados virtual por cliente no GC3. Os clientes podem fornecer acesso ao seu domínio a um ou mais prestadores de serviços. Este conceito permite também armazenar códigos semelhantes entre vários clientes, localizados no seu domínio. O GID - Identificador Global é usado em todas as tabelas do GC3 para identificar códigos específicos do GC3. O GID é formulado concatenando o nome de domínio e o XID como DomainName.XID Um XID - Identificador Externo é usado para armazenar códigos específicos do cliente. Por exemplo, o Wal-Mart pode atribuir um código 'Nike' aos calçados Nike em seu inventário. A K-Mart também pode usar o código 'Nike' para calçados Nike em seu inventário. Para Wal-Mart: Nome de domínio: Wal-Mart Item_XID: Nike Item_GID: Walmart.Nike Para K-Mart: Nome de domínio: Kmart Item_XID: Nike Item_GID: Kmart.Nike.

<div class="meta-text" markdown="1">
**Sequência:** 1
**Object Type:** DOMAIN
**OTM Table:** DOMAIN
**Deployment Type:** MANUAL


**Responsável:** ITC


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


### Query de Extração de Objetos
```sql
SELECT * FROM DOMAIN
```





### Domain Grants

Esta tabela contém a lista de domínios aos quais um remetente/domínio concede acesso para visualizar ou atualizar as informações. O sinalizador is_write_access especifica se o beneficiário tem acesso de atualização.

<div class="meta-text" markdown="1">
**Sequência:** 2
**Object Type:** DOMAIN_GRANTS_MADE
**OTM Table:** DOMAIN_GRANTS_MADE
**Deployment Type:** MANUAL


**Responsável:** ITC


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


### Query de Extração de Objetos
```sql
SELECT *
FROM
  DOMAIN_GRANTS_MADE
ORDER BY
  GRANTOR_DOMAIN
```





### Domain Settings

Perfil ITL associado ao domínio.

<div class="meta-text" markdown="1">
**Sequência:** 3
**Object Type:** DOMAIN_SETTING
**OTM Table:** DOMAIN_SETTING
**Deployment Type:** MANUAL


**Responsável:** ITC


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


### Query de Extração de Objetos
```sql
SELECT *
FROM
  DOMAIN_SETTING
ORDER BY
  DOMAIN_NAME
```





### Properties

Instrução de propriedade.

<div class="meta-text" markdown="1">
**Sequência:** 4
**Object Type:** PROP_INSTRUCTION
**OTM Table:** PROP_INSTRUCTION
**Deployment Type:** MANUAL


**Responsável:** ITC


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


### Query de Extração de Objetos
```sql
SELECT *
FROM
  PROP_INSTRUCTION
WHERE
  PROP_INSTRUCTION_SET_GID = 'CUSTOM'
ORDER BY
  PROP_SEQUENCE_NUM
```





### Units of Measure (UOM)

Esta tabela armazena as diversas unidades de medidas que podem ser usadas nos cálculos do GC3. Alguns exemplos de UOM são: Velocidade - Milha por Hora, Quilômetro por Hora etc, Duração - Dias, Minutos, Hora etc.

<div class="meta-text" markdown="1">
**Sequência:** 5
**Object Type:** UOM
**OTM Table:** UOM
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


### Query de Extração de Objetos
```sql
SELECT *
FROM
  UOM
ORDER BY
  TYPE
```





### Postal Code Components

Esta tabela define o nome da hierarquia do local. A hierarquia pode ser qualquer combinação e níveis do nome. Por exemplo, EUA/PA/Filadélfia é uma hierarquia de três níveis com País/Estado/Cidade, EUA/19406 é uma hierarquia de dois níveis com País/Código Postal.

<div class="meta-text" markdown="1">
**Sequência:** 6
**Object Type:** HNAME_COMPONENT
**OTM Table:** HNAME_COMPONENT
**Deployment Type:** DB_XML


**Responsável:** ITC


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


### Query de Extração de Objetos
```sql
SELECT * FROM HNAME_COMPONENT ORDER BY HNAME_COMPONENT_XID
```





### Branding

Tabela de configuração de branding para personalização visual da aplicação.

<div class="meta-text" markdown="1">
**Sequência:** 7
**Object Type:** BRANDING
**OTM Table:** BRANDING
**Deployment Type:** MANUAL


**Responsável:** ITC


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>






### Business Number

Esta é uma tabela interna usada para gerar números comerciais pela lógica do aplicativo gerador de negócios. As regras definem como os números comerciais são gerados. No momento, como apenas o gerador de sequência de imagens está implementado, apenas as definições de sequência de imagens são usadas. O usuário precisa fornecer o tipo de número comercial e o contexto. O mecanismo BN localiza a melhor definição de regra correspondente com base no tipo de regra, domínio e data atual. Depois que a definição da regra for localizada, o contexto será usado para gerar o número comercial.

<div class="meta-text" markdown="1">
**Sequência:** 8
**Object Type:** BN_RULE
**OTM Table:** BN_RULE
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


### Query de Extração de Objetos
```sql
SELECT *
FROM
  BN_RULE
WHERE
  DOMAIN_NAME = 'BAU'
  AND BN_RULE_XID LIKE '%BAU%'
ORDER BY
  BN_RULE_XID
```





### Reports

A tabela REPORT contém a lista de relatórios padrão e customizados. Um registro por relatório.

<div class="meta-text" markdown="1">
**Sequência:** 9
**Object Type:** REPORT
**OTM Table:** REPORT
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


### Query de Extração de Objetos
```sql
SELECT *
FROM
  REPORT
WHERE
  DOMAIN_NAME = 'BAU'
ORDER BY
  REPORT_XID
```





### Transport Mode

Esta é a tabela mestra que armazena os diversos meios de transporte que podem ser utilizados para o envio da mercadoria. Alguns exemplos incluem: Air Train Truck Ship etc.

<div class="meta-text" markdown="1">
**Sequência:** 10
**Object Type:** TRANSPORT_MODE
**OTM Table:** TRANSPORT_MODE
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


### Query de Extração de Objetos
```sql
SELECT *
FROM
  TRANSPORT_MODE
WHERE
  DOMAIN_NAME = 'BAU'
ORDER BY
  TRANSPORT_MODE_XID
```





### BN Named Range

Cada registro representa uma coleção de intervalos pré-atribuídos.

<div class="meta-text" markdown="1">
**Sequência:** 11
**Object Type:** BN_NAMED_RANGE
**OTM Table:** BN_NAMED_RANGE
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


### Query de Extração de Objetos
```sql
SELECT *
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

Este é um agrupamento dos itens. Vários itens podem fazer parte de uma mercadoria. Esta tabela pode definir o modo de transporte dos itens da mercadoria. Por exemplo, materiais perigosos não podem ser transportados por via aérea.

<div class="meta-text" markdown="1">
**Sequência:** 1
**Object Type:** COMMODITY
**OTM Table:** COMMODITY
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


### Query de Extração de Objetos
```sql
SELECT *
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

Esta tabela é usada em conjunto com a tabela Localização. Ele contém detalhes adicionais sobre o local que é uma empresa. Ele contém as informações de faturamento e remessa.

<div class="meta-text" markdown="1">
**Sequência:** 2
**Object Type:** CORPORATION
**OTM Table:** CORPORATION
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


### Query de Extração de Objetos
```sql
SELECT *
FROM
  CORPORATION
WHERE
  DOMAIN_NAME = 'BAU'
ORDER BY
  CORPORATION_XID
```





### Ship Unit Specs (THU)

SHIP_UNIT_SPEC armazena informações de especificação adicionais para a unidade de envio de uma remessa.

<div class="meta-text" markdown="1">
**Sequência:** 3
**Object Type:** SHIP_UNIT_SPEC
**OTM Table:** SHIP_UNIT_SPEC
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


### Query de Extração de Objetos
```sql
SELECT *
FROM
  SHIP_UNIT_SPEC
WHERE
  DOMAIN_NAME = 'BAU'
  AND UNIT_TYPE = 'T'
ORDER BY
  SHIP_UNIT_SPEC_XID
```





### Service Providers

Esta tabela armazena as informações sobre os provedores de serviços.

<div class="meta-text" markdown="1">
**Sequência:** 4
**Object Type:** SERVPROV
**OTM Table:** SERVPROV
**Deployment Type:** CSV


**Responsável:** ITC


**Documentação:** PENDING
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** PENDING
**Validação:** PENDING
</div>


### Query de Extração de Objetos
```sql
SELECT *
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

Um Local é um local onde ocorrem atividades relacionadas ao transporte, como carga e descarga de carga. Além disso, um local pode representar uma empresa e/ou um provedor de serviços.

<div class="meta-text" markdown="1">
**Sequência:** 5
**Object Type:** LOCATION
**OTM Table:** LOCATION
**Deployment Type:** CSV


**Responsável:** ITC


**Documentação:** PENDING
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** PENDING
**Validação:** PENDING
</div>


### Query de Extração de Objetos
```sql
SELECT *
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





### Contacts

Esta tabela é usada para identificar uma pessoa de contato em um local para comunicação.

<div class="meta-text" markdown="1">
**Sequência:** 6
**Object Type:** CONTACT
**OTM Table:** CONTACT
**Deployment Type:** CSV


**Responsável:** ITC


**Documentação:** PENDING
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** PENDING
**Validação:** PENDING
</div>


### Query de Extração de Objetos
```sql
SELECT *
FROM
  CONTACT C,
  CONTACT_COM_METHOD CCM
WHERE
  C.CONTACT_GID = CCM.CONTACT_GID
ORDER BY
  FIRST_NAME
```





### Equipment Groups

Esta tabela define as categorias que podem ser utilizadas para agrupamento dos equipamentos. Por exemplo, os equipamentos podem ser agrupados em: Funil Coberto 42FT, Flatcar 60FT, Congelado, Aquecido etc. O usuário também pode registrar o tamanho (comprimento, altura, largura), peso e volume. Também pode ser estabelecida uma ligação aos controlos de temperatura definidos.

<div class="meta-text" markdown="1">
**Sequência:** 7
**Object Type:** EQUIPMENT_GROUP
**OTM Table:** EQUIPMENT_GROUP
**Deployment Type:** CSV


**Responsável:** ITC


**Documentação:** PENDING
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** PENDING
**Validação:** PENDING
</div>


### Query de Extração de Objetos
```sql
SELECT *
FROM
  EQUIPMENT_GROUP EG
WHERE
  EG.DOMAIN_NAME = 'BAU'
ORDER BY
  EG.EQUIPMENT_GROUP_XID
```





### Items

Esta é a tabela mestre de itens. Define os diversos itens da base de dados do cliente. O item pode ser definido em diversas categorias de classificação governamental. GC3 inclui as categorias para representar NMFC, STCC, HTS e SITC. Outros detalhes como unidades de envio mínimas e máximas, tamanho do palete etc. também são definidos nesta tabela.

<div class="meta-text" markdown="1">
**Sequência:** 8
**Object Type:** ITEM
**OTM Table:** ITEM
**Deployment Type:** INTEGRATION


**Responsável:** ITC


**Documentação:** PENDING
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** PENDING
**Validação:** PENDING
</div>


### Query de Extração de Objetos
```sql
SELECT *
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

O GID do item empacotado.

<div class="meta-text" markdown="1">
**Sequência:** 9
**Object Type:** PACKAGED_ITEM
**OTM Table:** PACKAGED_ITEM
**Deployment Type:** INTEGRATION


**Responsável:** ITC


**Documentação:** PENDING
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** PENDING
**Validação:** PENDING
</div>


### Query de Extração de Objetos
```sql
SELECT *
FROM
  XML_TEMPLATE xt
WHERE
  xt.DOMAIN_NAME = 'BAU'
ORDER BY
  xt.XML_TEMPLATE_XID
```





### Contact Groups

A tabela contact_group associa contatos individuais a um contato de grupo (não pessoal). Ao criar esta associação, ela permite que configurações de atributos como interesse em notificações de eventos específicos sejam definidas no nível do grupo, de modo que não precise ser definido no nível individual.

<div class="meta-text" markdown="1">
**Sequência:** 10
**Object Type:** CONTACT_GROUP
**OTM Table:** CONTACT_GROUP
**Deployment Type:** CSV


**Responsável:** ITC


**Documentação:** PENDING
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** PENDING
**Validação:** PENDING
</div>


### Query de Extração de Objetos
```sql
SELECT *
FROM
  STYLESHEET_CONTENT
WHERE
  DOMAIN_NAME = 'BAU'
ORDER BY
  DOMAIN_NAME,
  STYLESHEET_CONTENT_XID
```





### LOCATION_REFNUM (AUTO)

Uma referência a um local entre os vários sistemas aplicativos dentro de uma empresa, que pode ser um identificador global de local ou uma nova definição de local. Por exemplo, um local pode ser referenciado como XYZ no aplicativo ERP, 123 no aplicativo JDE, etc., dentro da mesma empresa.

<div class="meta-text" markdown="1">
**Sequência:** 154
**Object Type:** LOCATION_REFNUM
**OTM Table:** LOCATION_REFNUM
**Deployment Type:** CSV


**Responsável:** ITC


**Documentação:** PENDING
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** PENDING
**Validação:** PENDING
</div>


### Query de Extração de Objetos
```sql
SELECT *
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





### CONTACT_COM_METHOD (AUTO)

O GID de contato.

<div class="meta-text" markdown="1">
**Sequência:** 66
**Object Type:** CONTACT_COM_METHOD
**OTM Table:** CONTACT_COM_METHOD
**Deployment Type:** CSV


**Responsável:** ITC


**Documentação:** PENDING
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** PENDING
**Validação:** PENDING
</div>


### Query de Extração de Objetos
```sql
SELECT *
FROM
  CONTACT C,
  CONTACT_COM_METHOD CCM
WHERE
  C.CONTACT_GID = CCM.CONTACT_GID
ORDER BY
  FIRST_NAME
```





### STYLESHEET_PROFILE (BAU - AUTO)

GC3 Identificador global da entidade. É criado concatenando o nome de domínio,'.' e XID.

<div class="meta-text" markdown="1">
**Sequência:** 465
**Object Type:** STYLESHEET_PROFILE
**OTM Table:** STYLESHEET_PROFILE
**Deployment Type:** INTEGRATION


**Responsável:** ITC


**Documentação:** PENDING
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** PENDING
**Validação:** PENDING
</div>


### Query de Extração de Objetos
```sql
SELECT *
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





### STYLESHEET_CONTENT (PUBLIC - AUTO)

ID da versão – string de versão completa.

<div class="meta-text" markdown="1">
**Sequência:** 464
**Object Type:** STYLESHEET_CONTENT
**OTM Table:** STYLESHEET_CONTENT
**Deployment Type:** CSV


**Responsável:** ITC


**Documentação:** PENDING
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** PENDING
**Validação:** PENDING
</div>


### Query de Extração de Objetos
```sql
SELECT *
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

Um qualificador para a referência de local. Esta tabela contém o identificador real utilizado pela empresa para o mesmo local, entre vários sistemas (SAP, JDE etc.).

<div class="meta-text" markdown="1">
**Sequência:** 1
**Object Type:** LOCATION_REFNUM_QUAL
**OTM Table:** LOCATION_REFNUM_QUAL
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


### Query de Extração de Objetos
```sql
SELECT *
FROM
  LOCATION_REFNUM_QUAL
WHERE LOCATION_REFNUM_QUAL_GID IN (SELECT LOCATION_REFNUM_QUAL_GID FROM LOCATION_REFNUM)
  AND DOMAIN_NAME = 'BAU'
ORDER BY
  DOMAIN_NAME,
  LOCATION_REFNUM_QUAL_XID
```





### Order Release Refnum Qualifier

Esta tabela contém o nome do qualificador para o link de referência da identificação interna do cliente para uma base de pedidos. Por exemplo, o cliente pode ter aplicações SAP ou JDE internamente para especificar os pedidos.

<div class="meta-text" markdown="1">
**Sequência:** 2
**Object Type:** ORDER_RELEASE_REFNUM_QUAL
**OTM Table:** ORDER_RELEASE_REFNUM_QUAL
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


### Query de Extração de Objetos
```sql
SELECT *
FROM
  ORDER_RELEASE_REFNUM_QUAL
WHERE ORDER_RELEASE_REFNUM_QUAL_GID IN (SELECT ORDER_RELEASE_REFNUM_QUAL_GID FROM ORDER_RELEASE_REFNUM)
  AND DOMAIN_NAME = 'BAU'
ORDER BY
  DOMAIN_NAME,
  ORDER_RELEASE_REFNUM_QUAL_XID
```





### Order Release Line Refnum Qualifier

GC3 Identificador global da entidade. É criado concatenando o nome de domínio,'.' e XID.

<div class="meta-text" markdown="1">
**Sequência:** 3
**Object Type:** ORDER_RELEASE_LINE_REFNUM_QUAL
**OTM Table:** ORDER_RELEASE_LINE_REFNUM_QUAL
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


### Query de Extração de Objetos
```sql
SELECT *
FROM
  ORDER_RELEASE_LINE_REFNUM_QUAL
WHERE OR_LINE_REFNUM_QUAL_GID IN (SELECT OR_LINE_REFNUM_QUAL_GID FROM ORDER_RELEASE_LINE_REFNUM)
  AND DOMAIN_NAME = 'BAU'
ORDER BY
  DOMAIN_NAME,
  OR_LINE_REFNUM_QUAL_XID
```





### Packaged Item Refnum Qualifier

Especifica se o qualificador refnum pode existir no objeto de negócios diversas vezes ou está restrito a ocorrer apenas uma vez e se o valor pode ser atualizado. Se o valor for MUITOS, o objeto poderá ter vários valores para o mesmo qualificador. Se o valor for UPDATE_OK ou UPDATE_NOT_OK, a regra estará em vigor, o que significa que apenas um valor será permitido para um determinado qualificador. No caso de UPDATE_NOT_OK, o valor não pode ser modificado.

<div class="meta-text" markdown="1">
**Sequência:** 4
**Object Type:** PACKAGED_ITEM_REFNUM_QUAL
**OTM Table:** PACKAGED_ITEM_REFNUM_QUAL
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


### Query de Extração de Objetos
```sql
SELECT *
FROM
  PACKAGED_ITEM_REFNUM_QUAL
WHERE PACKAGED_ITEM_REFNUM_QUAL_GID IN (SELECT PACKAGED_ITEM_REFNUM_QUAL_GID FROM PACKAGED_ITEM_REFNUM)
  AND DOMAIN_NAME = 'BAU'
ORDER BY
  DOMAIN_NAME,
  PACKAGED_ITEM_REFNUM_QUAL_XID
```





### Item Refnum Qualifier

Identifica se os números de referência com este qualificador devem ser exibidos em remessas relacionadas.

<div class="meta-text" markdown="1">
**Sequência:** 5
**Object Type:** ITEM_REFNUM_QUAL
**OTM Table:** ITEM_REFNUM_QUAL
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


### Query de Extração de Objetos
```sql
SELECT *
FROM
  ITEM_REFNUM_QUAL
WHERE ITEM_REFNUM_QUAL_GID IN (SELECT ITEM_REFNUM_QUAL_GID FROM ITEM_REFNUM)
  AND DOMAIN_NAME = 'BAU'
ORDER BY
  DOMAIN_NAME,
  ITEM_REFNUM_QUAL_XID
```





### Shipment Refnum Qualifier

A tabela mestre que armazena as descrições dos qualificadores da remessa.

<div class="meta-text" markdown="1">
**Sequência:** 6
**Object Type:** SHIPMENT_REFNUM_QUAL
**OTM Table:** SHIPMENT_REFNUM_QUAL
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


### Query de Extração de Objetos
```sql
SELECT *
FROM
  SHIPMENT_REFNUM_QUAL
WHERE SHIPMENT_REFNUM_QUAL_GID IN (SELECT SHIPMENT_REFNUM_QUAL_GID FROM SHIPMENT_REFNUM)
  AND DOMAIN_NAME = 'BAU'
ORDER BY
  DOMAIN_NAME,
  SHIPMENT_REFNUM_QUAL_XID
```





### Shipment Stop Refnum Qualifier

GC3 Identificador global da entidade. É criado concatenando o nome de domínio,'.' e XID.

<div class="meta-text" markdown="1">
**Sequência:** 7
**Object Type:** SHIPMENT_STOP_REFNUM_QUAL
**OTM Table:** SHIPMENT_STOP_REFNUM_QUAL
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


### Query de Extração de Objetos
```sql
SELECT *
FROM
  SHIPMENT_STOP_REFNUM_QUAL
WHERE SHIPMENT_STOP_REFNUM_QUAL_GID IN (SELECT SHIPMENT_STOP_REFNUM_QUAL_GID FROM SHIPMENT_STOP_REFNUM)
  AND DOMAIN_NAME = 'BAU'
ORDER BY
  DOMAIN_NAME,
  SHIPMENT_STOP_REFNUM_QUAL_XID
```





### Rate Geo Refnum Qualifier

Qualificadores disponíveis para números de referência geográfica de tarifas.

<div class="meta-text" markdown="1">
**Sequência:** 8
**Object Type:** RATE_GEO_REFNUM_QUAL
**OTM Table:** RATE_GEO_REFNUM_QUAL
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


### Query de Extração de Objetos
```sql
SELECT *
FROM
  RATE_GEO_REFNUM_QUAL
WHERE RATE_GEO_REFNUM_QUAL_GID IN (SELECT RATE_GEO_REFNUM_QUAL_GID FROM RATE_GEO_REFNUM)
  AND DOMAIN_NAME = 'BAU'
ORDER BY
  DOMAIN_NAME,
  RATE_GEO_REFNUM_QUAL_XID
```





### Order Movement Refnum Qualifier

Descrição.

<div class="meta-text" markdown="1">
**Sequência:** 9
**Object Type:** OM_REFNUM_QUAL
**OTM Table:** OM_REFNUM_QUAL
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


### Query de Extração de Objetos
```sql
SELECT *
FROM
  OM_REFNUM_QUAL
WHERE OM_REFNUM_QUAL_GID IN (SELECT OM_REFNUM_QUAL_GID FROM ORDER_MOVEMENT_REFNUM)
  AND DOMAIN_NAME = 'BAU'
ORDER BY
  DOMAIN_NAME,
  OM_REFNUM_QUAL_XID
```





### Status Types and Values

Esta tabela define os tipos de status que podem ou podem ser relatados em uma remessa de item de linha. Um tipo de status pode ter vários valores de status. Por exemplo, o tipo de status pode ser: Compromisso de planejamento de pagamento processado etc. Consulte a tabela Status_Value para obter detalhes sobre os valores de status.

<div class="meta-text" markdown="1">
**Sequência:** 10
**Object Type:** STATUS_TYPE
**OTM Table:** STATUS_TYPE
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


### Query de Extração de Objetos
```sql
SELECT *
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

Esta tabela está vinculada à tabela OB_Remark para descrever melhor os detalhes das observações no pedido base. Os qualificadores de observação são os valores enumerados para as observações.

<div class="meta-text" markdown="1">
**Sequência:** 11
**Object Type:** REMARK_QUAL
**OTM Table:** REMARK_QUAL
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


### Query de Extração de Objetos
```sql
SELECT *
FROM
  REMARK_QUAL rq
WHERE
  rq.DOMAIN_NAME = 'BAU'
ORDER BY
  rq.DATA_QUERY_TYPE_GID,
  rq.REMARK_QUAL_XID
```





### STATUS_VALUE (BAU - AUTO)

Esta tabela define vários valores de status que podem ser atribuídos a um tipo de status. Por exemplo, para um tipo de Status de Compromisso, os valores podem ser: Completo Nenhum Parcial etc.

<div class="meta-text" markdown="1">
**Sequência:** 461
**Object Type:** STATUS_VALUE
**OTM Table:** STATUS_VALUE
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


### Query de Extração de Objetos
```sql
SELECT *
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






### Grupo: Planejamento


Foca em tabelas e estruturas que suportam o planejamento e execução de cargas, perfis de roteirização e configuração de transporte.




### Audit Trail

Tabela usada para armazenar dados de auditoria.

<div class="meta-text" markdown="1">
**Sequência:** 1
**Object Type:** AUDIT_TRAIL
**OTM Table:** AUDIT_TRAIL
**Deployment Type:** MIGRATION_PROJECT


**Query Name:** 

**Agent Gid:** 

**Finder Set Gid:** 

**Rate Offering Gid:** 

**Event Group Gid:** 

**Responsável:** ITC


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


### Query de Extração de Objetos
```sql
SELECT *
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

Valores de parâmetros (instâncias) para configuração lógica.

<div class="meta-text" markdown="1">
**Sequência:** 2
**Object Type:** LOGIC_PARAMETER
**OTM Table:** LOGIC_PARAMETER
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


### Query de Extração de Objetos
```sql
SELECT *
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

Associa o parâmetro de planejamento a um determinado conjunto. Isto é usado para organizar os parâmetros de planejamento em agrupamentos lógicos.

<div class="meta-text" markdown="1">
**Sequência:** 3
**Object Type:** PLANNING_PARAMETER
**OTM Table:** PLANNING_PARAMETER
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


### Query de Extração de Objetos
```sql
SELECT *
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

Esta é a mesa master que contém diversos acessórios necessários para transporte, coleta e entrega. Um acessório difere de um serviço especial porque o cliente tem que pagar pela utilização dos acessórios. Um exemplo de acessório é uma unidade frigorífica de caminhão, que serve para transportar sorvetes. Os acessórios definidos podem ser vinculados no nível do item ou no nível do local no GC3. A lógica do GC3 verifica se um acessório é necessário e, assim, programa e calcula o custo de acordo.

<div class="meta-text" markdown="1">
**Sequência:** 4
**Object Type:** ACCESSORIAL_CODE
**OTM Table:** ACCESSORIAL_CODE
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


### Query de Extração de Objetos
```sql
SELECT *
FROM
  ACCESSORIAL_CODE
WHERE
  DOMAIN_NAME = 'BAU'
ORDER BY
  ACCESSORIAL_CODE_XID
```





### Itinerary Leg

A perna define o caminho entre a origem e o destino. Identifica outras restrições, como modo de transporte (apenas caminhões permitidos, modo aéreo, etc.).

<div class="meta-text" markdown="1">
**Sequência:** 5
**Object Type:** LEG
**OTM Table:** LEG
**Deployment Type:** MIGRATION_PROJECT


**Query Name:** 

**Agent Gid:** 

**Finder Set Gid:** 

**Rate Offering Gid:** 

**Event Group Gid:** 

**Responsável:** ITC


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


### Query de Extração de Objetos
```sql
SELECT *
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

Esta tabela define o caminho entre dois locais. O itinerário é descrito em termos de pernas. Um itinerário pode ter um ou mais trechos. A tabela de itinerário consiste nas restrições de peso permitido para embarque para cada trajeto. O itinerário pode ser usado por uma empresa ou pode especificar restrições adicionais usando o GID do calendário, como itinerário de segunda a sexta, itinerário de fim de semana, etc.

<div class="meta-text" markdown="1">
**Sequência:** 6
**Object Type:** ITINERARY
**OTM Table:** ITINERARY
**Deployment Type:** MIGRATION_PROJECT


**Query Name:** 

**Agent Gid:** 

**Finder Set Gid:** 

**Rate Offering Gid:** 

**Event Group Gid:** 

**Responsável:** ITC


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


### Query de Extração de Objetos
```sql
SELECT *
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

Perfis de itinerario associam um ou mais itinerarios e sao utilizados em regras de grupo de embarque durante o planejamento.

<div class="meta-text" markdown="1">
**Sequência:** 7
**Object Type:** ITINERARY_PROFILE
**OTM Table:** ITINERARY_PROFILE
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


### Query de Extração de Objetos
```sql
SELECT *
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

Indica se esta regra de configuração de carga deve ser usada para construção de unidade de navio.

<div class="meta-text" markdown="1">
**Sequência:** 8
**Object Type:** LOAD_CONFIG_RULE
**OTM Table:** LOAD_CONFIG_RULE
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


### Query de Extração de Objetos
```sql
SELECT *
FROM
  LOAD_CONFIG_RULE
WHERE
  DOMAIN_NAME = 'BAU'
ORDER BY
  LOAD_CONFIG_SETUP_GID
```





### Load Configuration Setup

Índice de empilhamento da especificação da unidade do navio. Unidades com índice de empilhamento mais alto não devem ser carregadas sobre unidades com índice de empilhamento mais baixo.

<div class="meta-text" markdown="1">
**Sequência:** 9
**Object Type:** LOAD_CONFIG_SETUP
**OTM Table:** LOAD_CONFIG_SETUP
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


### Query de Extração de Objetos
```sql
SELECT *
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

Os tipos de pedidos definidos pelo remetente. Por exemplo, pedido do cliente, pedido do fabricante, pedido de compra, pedido de distribuição, etc.

<div class="meta-text" markdown="1">
**Sequência:** 10
**Object Type:** ORDER_RELEASE_TYPE
**OTM Table:** ORDER_RELEASE_TYPE
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


### Query de Extração de Objetos
```sql
SELECT *
FROM
  ORDER_RELEASE_TYPE
WHERE
  DOMAIN_NAME = 'BAU'
ORDER BY
  ORDER_RELEASE_TYPE_XID
```





### NOTIFY_SUBJECT_CONTACT (AUTO)

O GID do assunto de notificação.

<div class="meta-text" markdown="1">
**Sequência:** 186
**Object Type:** NOTIFY_SUBJECT_CONTACT
**OTM Table:** NOTIFY_SUBJECT_CONTACT
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


### Query de Extração de Objetos
```sql
SELECT *
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





### ITINERARY_DETAIL (AUTO)

Esta tabela une a tabela Itinerário à tabela Perna. É usado para resolver o relacionamento muitos-para-muitos entre Itinerário e Perna.

<div class="meta-text" markdown="1">
**Sequência:** 129
**Object Type:** ITINERARY_DETAIL
**OTM Table:** ITINERARY_DETAIL
**Deployment Type:** MIGRATION_PROJECT


**Query Name:** 

**Agent Gid:** 

**Finder Set Gid:** 

**Rate Offering Gid:** 

**Event Group Gid:** 

**Responsável:** ITC


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


### Query de Extração de Objetos
```sql
SELECT *
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





### ITINERARY_PROFILE_D (AUTO)

Detalhes do perfil de itinerario, incluindo associacoes de itinerarios vinculadas ao perfil.

<div class="meta-text" markdown="1">
**Sequência:** 130
**Object Type:** ITINERARY_PROFILE_D
**OTM Table:** ITINERARY_PROFILE_D
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


### Query de Extração de Objetos
```sql
SELECT *
FROM ITINERARY_PROFILE IP
JOIN ITINERARY_PROFILE_D IPD
  ON IP.ITINERARY_PROFILE_GID = IPD.ITINERARY_PROFILE_GID
WHERE
  IP.DOMAIN_NAME = 'BAU'
ORDER BY
  IP.ITINERARY_PROFILE_XID,
  IPD.ITINERARY_GID
```





### LOAD_CONFIG_SETUP_ORIENTATION (AUTO)

O peso máximo permitido pode ser carregado na parte superior deste tipo de unidade quando carregada com a orientação. Isso só é verificado para unidades não semelhantes. Não se aplica ao empilhar unidades semelhantes.

<div class="meta-text" markdown="1">
**Sequência:** 144
**Object Type:** LOAD_CONFIG_SETUP_ORIENTATION
**OTM Table:** LOAD_CONFIG_SETUP_ORIENTATION
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


### Query de Extração de Objetos
```sql
SELECT *
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






### Grupo: Integração


Inclui objetos relacionados a integração e mensageria (templates, perfis XML, web services e sistemas externos) assegurando comunicação entre OTM e sistemas parceiros.




### Stylesheet Contents

ID da versão – string de versão completa.

<div class="meta-text" markdown="1">
**Sequência:** 1
**Object Type:** STYLESHEET_CONTENT
**OTM Table:** STYLESHEET_CONTENT
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


### Query de Extração de Objetos
```sql
SELECT *
FROM
  STYLESHEET_CONTENT
WHERE
  DOMAIN_NAME = 'BAU'
ORDER BY
  DOMAIN_NAME,
  STYLESHEET_CONTENT_XID
```





### Stylesheet Profiles

GC3 Identificador global da entidade. É criado concatenando o nome de domínio,'.' e XID.

<div class="meta-text" markdown="1">
**Sequência:** 2
**Object Type:** STYLESHEET_PROFILE
**OTM Table:** STYLESHEET_PROFILE
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


### Query de Extração de Objetos
```sql
SELECT *
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

Modelo XML.

<div class="meta-text" markdown="1">
**Sequência:** 3
**Object Type:** XML_TEMPLATE
**OTM Table:** XML_TEMPLATE
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


### Query de Extração de Objetos
```sql
SELECT *
FROM
  XML_TEMPLATE xt
WHERE
  xt.DOMAIN_NAME = 'BAU'
ORDER BY
  xt.XML_TEMPLATE_XID
```





### Outbound XML Profiles

Esta tabela e a tabela OUT_XMl_PROFILE_D especificam juntas os perfis XML de saída que podem ser usados ​​para limitar o tamanho dos documentos XML enviados do gc3 para sistemas externos. A tabela Out_xml_profile contém o registro de cabeçalho do perfil e define o 'gid' desse perfil. A tabela out_xml_profile_d fornece os detalhes que compõem um determinado perfil. Cada registro na tabela out_xml_profile_d indica um 'pedaço' específico de xml que deve ser excluído do documento de saída.

<div class="meta-text" markdown="1">
**Sequência:** 4
**Object Type:** OUT_XML_PROFILE
**OTM Table:** OUT_XML_PROFILE
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


### Query de Extração de Objetos
```sql
SELECT *
FROM
  OUT_XML_PROFILE oxp
WHERE
  oxp.DOMAIN_NAME = 'BAU'
ORDER BY
  oxp.OUT_XML_PROFILE_XID
```





### Document

Um campo booleano. Quando estiver definido como 'Y', esta linha e seus dados filho serão eliminados.

<div class="meta-text" markdown="1">
**Sequência:** 5
**Object Type:** DOCUMENT
**OTM Table:** DOCUMENT
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


### Query de Extração de Objetos
```sql
SELECT *
FROM
  DOCUMENT d
WHERE
  d.DOMAIN_NAME = 'BAU'
ORDER BY
  d.DOCUMENT_XID
```





### Webservice

Booleano 'Y' ou 'N' Padrão 'N'.

<div class="meta-text" markdown="1">
**Sequência:** 6
**Object Type:** WEB_SERVICE
**OTM Table:** WEB_SERVICE
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


### Query de Extração de Objetos
```sql
SELECT *
FROM
  WEB_SERVICE ws
WHERE
  ws.DOMAIN_NAME = 'BAU'
ORDER BY
  ws.WEB_SERVICE_XID
```





### External Systems

GC3 Identificador global da entidade. É criado concatenando o nome de domínio,'.' e XID.

<div class="meta-text" markdown="1">
**Sequência:** 7
**Object Type:** EXTERNAL_SYSTEM
**OTM Table:** EXTERNAL_SYSTEM
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


### Query de Extração de Objetos
```sql
SELECT *
FROM
  EXTERNAL_SYSTEM es
WHERE
  es.DOMAIN_NAME = 'BAU'
ORDER BY
  es.EXTERNAL_SYSTEM_XID
```





### External System Contact

Tabela de contatos de sistemas externos integrados ao OTM.

<div class="meta-text" markdown="1">
**Sequência:** 8
**Object Type:** EXTERNAL_CONTACT
**OTM Table:** EXTERNAL_CONTACT
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


### Query de Extração de Objetos
```sql
SELECT *
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

Isso define uma tela personalizada que é usada para visualizar ou editar entidades no sistema.

<div class="meta-text" markdown="1">
**Sequência:** 1
**Object Type:** MANAGER_LAYOUT
**OTM Table:** MANAGER_LAYOUT
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** PENDING
**Validação:** PENDING
</div>


### Query de Extração de Objetos
```sql
SELECT *
FROM
  MANAGER_LAYOUT ml
WHERE
  ml.DOMAIN_NAME = 'BAU'
ORDER BY
  ml.MANAGER_LAYOUT_XID
```





### Finder Sets

Esta tabela armazena o XML do conjunto de telas que define o layout de todas as telas de pesquisa e resultados na interface do usuário. O XML nesta tabela é armazenado como um blob e pode ser editado com o Screen Set Manager.

<div class="meta-text" markdown="1">
**Sequência:** 2
**Object Type:** FINDER_SET
**OTM Table:** FINDER_SET
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** PENDING
**Validação:** PENDING
</div>


### Query de Extração de Objetos
```sql
SELECT *
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

O GID de layout fornecido pelo usuário. Isso precisa ser único. O que isto significa é que dois usuários não podem compartilhar o mesmo layout gid.

<div class="meta-text" markdown="1">
**Sequência:** 3
**Object Type:** TRANSPORTATION_WORKBENCH
**OTM Table:** TRANSPORTATION_WORKBENCH
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC


**Documentação:** PENDING
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** PENDING
**Validação:** PENDING
</div>


### Query de Extração de Objetos
```sql
SELECT *
FROM
  TRANSPORTATION_WORKBENCH tw
WHERE
  tw.DOMAIN_NAME = 'BAU'
ORDER BY
  tw.LAYOUT_XID
```





### Business Monitors

Esta tabela é usada para armazenar as consultas salvas específicas definidas como parte de um monitor de negócios.

<div class="meta-text" markdown="1">
**Sequência:** 4
**Object Type:** BUSINESS_MONITOR_D
**OTM Table:** BUSINESS_MONITOR_D
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC


**Documentação:** PENDING
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** PENDING
**Validação:** PENDING
</div>


### Query de Extração de Objetos
```sql
SELECT *
FROM
  BUSINESS_MONITOR_D
WHERE
  DOMAIN_NAME = 'BAU'
```





### Access Control Lists (ACL)

Uma função de controle de acesso, contendo conjuntos de pontos de entrada e/ou funções secundárias. O acesso funcional é atribuído a um ACR.

<div class="meta-text" markdown="1">
**Sequência:** 5
**Object Type:** ACR_ROLE
**OTM Table:** ACR_ROLE
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC


**Documentação:** PENDING
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** PENDING
**Validação:** PENDING
</div>


### Query de Extração de Objetos
```sql
SELECT *
FROM
  ACR_ROLE AR,
  USER_ROLE_ACR_ROLE URAR
WHERE
  AR.ACR_ROLE_GID = URAR.ACR_ROLE_GID
ORDER BY
  URAR.USER_ROLE_GID
```





### User Roles

Se Y, a função do usuário é reservada pelo OTM: não pode ser excluída.

<div class="meta-text" markdown="1">
**Sequência:** 6
**Object Type:** USER_ROLE
**OTM Table:** USER_ROLE
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC


**Documentação:** PENDING
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** PENDING
**Validação:** PENDING
</div>


### Query de Extração de Objetos
```sql
SELECT *
FROM
  USER_ROLE
WHERE
  DOMAIN_NAME = 'BAU'
ORDER BY
  USER_ROLE_XID
```





### User Menus

Esta tabela contém todos os links internos do GC3 para aplicativos não localizadores na interface do usuário.

<div class="meta-text" markdown="1">
**Sequência:** 7
**Object Type:** USER_MENU
**OTM Table:** USER_MENU
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC


**Documentação:** PENDING
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** PENDING
**Validação:** PENDING
</div>


### Query de Extração de Objetos
```sql
SELECT *
FROM
  USER_MENU
WHERE
  DOMAIN_NAME = 'BAU'
ORDER BY
  USER_MENU_XID
```





### User Preferences

Tabela relacionada ao tópico do help do OTM (25c): User Preferences.

<div class="meta-text" markdown="1">
**Sequência:** 8
**Object Type:** USER_PREFERENCE_D
**OTM Table:** USER_PREFERENCE_D
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC


**Documentação:** PENDING
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** PENDING
**Validação:** PENDING
</div>


### Query de Extração de Objetos
```sql
SELECT *
FROM
  USER_PREFERENCE_D
ORDER BY
  USER_PREFERENCE_GID
```





### Translation (Labels)

Esta tabela contém todas as chaves de tradução definidas para etiquetas em todas as telas, e-mails e faxes.

<div class="meta-text" markdown="1">
**Sequência:** 9
**Object Type:** TRANSLATION
**OTM Table:** TRANSLATION
**Deployment Type:** DB_XML


**Responsável:** ITC


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


### Query de Extração de Objetos
```sql
SELECT *
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

Tabela relacionada ao tópico do help do OTM (25c): Access Control List Acoes and SmartLinks.

<div class="meta-text" markdown="1">
**Sequência:** 10
**Object Type:** USER_ACCESS
**OTM Table:** USER_ACCESS
**Deployment Type:** DB_XML


**Responsável:** ITC


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


### Query de Extração de Objetos
```sql
SELECT *
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

GC3 Identificador global da entidade. É criado concatenando o nome de domínio,'.' e XID.

<div class="meta-text" markdown="1">
**Sequência:** 11
**Object Type:** VPD_PROFILE
**OTM Table:** VPD_PROFILE
**Deployment Type:** DB_XML


**Responsável:** ITC


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


### Query de Extração de Objetos
```sql
SELECT *
FROM
  VPD_PROFILE
WHERE
  DOMAIN_NAME = 'BAU'
ORDER BY
  VPD_PROFILE_XID
```





### Relatórios (BI ZIP)

Tabela de arquivos e pacotes de relatórios do BI Publisher.

<div class="meta-text" markdown="1">
**Sequência:** 12
**Object Type:** BI_PUBLISHER_FILES
**OTM Table:** BI_PUBLISHER_FILES
**Deployment Type:** MANUAL


**Responsável:** ITC


**Documentação:** PENDING
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** PENDING
**Validação:** PENDING
</div>






### USER_ROLE_ACR_ROLE (BAU - AUTO)

Substituições de função de controle de acesso para uma determinada função de usuário.

<div class="meta-text" markdown="1">
**Sequência:** 488
**Object Type:** USER_ROLE_ACR_ROLE
**OTM Table:** USER_ROLE_ACR_ROLE
**Deployment Type:** MIGRATION_PROJECT


**Responsável:** ITC


**Documentação:** PENDING
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** PENDING
**Validação:** PENDING
</div>


### Query de Extração de Objetos
```sql
SELECT *
FROM
  ACR_ROLE AR,
  USER_ROLE_ACR_ROLE URAR
WHERE
  AR.ACR_ROLE_GID = URAR.ACR_ROLE_GID
ORDER BY
  URAR.USER_ROLE_GID
```





### TRANSLATION_D (AUTO)

Esta tabela contém o texto a ser exibido nas telas, e-mails e faxes para todos os idiomas definidos no GC3.

<div class="meta-text" markdown="1">
**Sequência:** 352
**Object Type:** TRANSLATION_D
**OTM Table:** TRANSLATION_D
**Deployment Type:** DB_XML


**Responsável:** ITC


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


### Query de Extração de Objetos
```sql
SELECT *
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





### USER_MENU_ACCESS (BAU - AUTO)

Tabela relacionada ao tópico do help do OTM (25c): User Menu - Legacy Acoes.

<div class="meta-text" markdown="1">
**Sequência:** 473
**Object Type:** USER_MENU_ACCESS
**OTM Table:** USER_MENU_ACCESS
**Deployment Type:** DB_XML


**Responsável:** ITC


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


### Query de Extração de Objetos
```sql
SELECT *
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





### USER_PREFERENCE_ACCESS (BAU - AUTO)

Tabela relacionada ao tópico do help do OTM (25c): User Preference Access.

<div class="meta-text" markdown="1">
**Sequência:** 479
**Object Type:** USER_PREFERENCE_ACCESS
**OTM Table:** USER_PREFERENCE_ACCESS
**Deployment Type:** DB_XML


**Responsável:** ITC


**Documentação:** DONE
**Migration Project:** PENDING
**Exportação:** PENDING
**Deploy:** DONE
**Validação:** PENDING
</div>


### Query de Extração de Objetos
```sql
SELECT *
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





