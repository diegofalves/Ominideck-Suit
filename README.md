# OmniDeck – Bauducco

OmniDeck é um sistema de gestão de consultoria orientado à governança,
documentação estruturada e reutilização de conhecimento.

Este repositório representa a implementação base do OmniDeck no contexto Bauducco.
# OmniDeck – Bauducco

## Visão Geral

O **OmniDeck** é um sistema web para **estruturação, validação e gestão contínua de projetos de migração** no **Oracle Transportation Management (OTM)**.

Ele funciona como um **editor inteligente orientado a domínio**, garantindo que todas as informações de um projeto de migração sejam:
- organizadas de forma hierárquica
- semanticamente válidas
- persistidas com segurança
- reutilizáveis ao longo de todo o ciclo do projeto

Este repositório representa a **implementação base do OmniDeck aplicada ao contexto Bauducco**, servindo como referência arquitetural e funcional para outros projetos futuros.

---

## O Problema que o OmniDeck Resolve

Projetos de migração OTM tradicionalmente sofrem com:
- documentação fragmentada
- perda de informações entre sessões
- falta de validações estruturais
- dependência excessiva de planilhas e arquivos soltos
- dificuldade de evoluir o projeto ao longo do tempo

O OmniDeck resolve esse problema oferecendo um **sistema único, validado e editável**, que cresce junto com o projeto.

---

## O que o Sistema Faz Hoje

### 1. Gestão de Projetos de Migração

Permite criar e manter projetos contendo:
- código, nome e versão
- consultor responsável
- ambiente de origem e destino

Esses dados são persistidos e automaticamente carregados em cada acesso.

---

### 2. Organização Hierárquica

O projeto é estruturado de forma clara:

```
Projeto
 └── Grupos
      └── Objetos
```

- Um projeto pode conter **N grupos**
- Cada grupo pode conter **N objetos**
- A ordem é controlada por sequência

---

### 3. Suporte a Objetos OTM Reais

O OmniDeck suporta atualmente 6 tipos de objetos:

- SAVED_QUERY
- AGENT
- TABLE
- FINDER_SET
- RATE
- EVENT_GROUP

Cada tipo possui **identificadores específicos**, exibidos dinamicamente na UI e validados no domínio.

---

### 4. Validação de Domínio (DDD)

O sistema aplica regras reais de negócio antes de salvar qualquer dado:

- campos obrigatórios
- consistência entre ambientes
- obrigatoriedade de grupos e objetos
- validação tipo-específica de identifiers

Nenhum JSON inválido é persistido.

---

### 5. Editor de Longo Prazo (Edit Mode)

O OmniDeck não é um wizard descartável.

Após salvar um projeto:
- os dados permanecem persistidos
- a UI entra em modo de edição
- é possível adicionar, remover e alterar grupos e objetos
- refresh ou fechamento do navegador não causam perda de dados

O **JSON canônico** é a fonte única da verdade.

---

### 6. Pipeline de Renderização

O sistema já implementa o pipeline completo:

```
JSON (Domínio)
 → Markdown (documentação técnica)
 → HTML (visualização)
 → PDF (entregável)
```

Cada etapa é isolada, testável e reutilizável.

---

## Arquitetura

- **Domain-first** (DDD)
- Boundaries explícitos entre:
  - Domínio
  - UI
  - Renderização
  - Infraestrutura
- Validações no domínio, não na UI
- Repository Pattern para persistência
- UI como cliente do domínio

---

## Estado Atual do Projeto

✔ Editor completo e funcional  
✔ Persistência incremental  
✔ Validação de domínio ativa  
✔ UI dinâmica (grupos e objetos)  
✔ Rendering MD / HTML / PDF  
✔ Base sólida para expansão  

---

## Próximos Passos Planejados

- Integração de Metadata OTM real
- Catálogos e validações semânticas
- Execução de pipelines via UI
- CLI do OmniDeck
- Evolução para múltiplos projetos / SaaS

---

## Objetivo Final

O OmniDeck não é apenas uma ferramenta de documentação.

Ele é um **sistema de governança técnica**, projetado para:
- reduzir erros em migrações
- aumentar previsibilidade
- preservar conhecimento
- permitir evolução contínua dos projetos

---