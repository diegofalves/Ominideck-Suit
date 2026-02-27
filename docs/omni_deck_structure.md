

# OmniDeck – Estrutura Completa do Projeto

## 1. Visão Geral

O OmniDeck é uma aplicação orientada a Domain-Driven Design (DDD) construída para governar projetos de migração OTM com consistência, rastreabilidade e geração automatizada de documentação técnica.

A arquitetura separa claramente:

- Domínio (regras de negócio)
- Adapters (UI, CLI, renderização)
- Infraestrutura (persistência, build, empacotamento)
- Artefatos derivados (Markdown, HTML, PDF)

O JSON canônico é a fonte única da verdade.

---

# 2. Estrutura de Diretórios

```
00 - Ominideck - Bauducco
│
├── docs/
├── domain/
├── ui/
├── infra/
├── rendering/
├── scripts/
├── metadata/
├── legacy/
├── build/
├── dist/
├── omni_launcher.py
├── omni_launcher.spec
├── run.py
├── main.py
└── build_release.sh
```

---

# 3. Camada de Domínio (`domain/`)

## Responsabilidade

Contém o núcleo do sistema.  
Nenhuma regra de negócio existe fora dessa pasta.

## Contém

- Entidades (Projeto de Migração, MIGRATION_GROUP, MIGRATION_ITEM)
- Validações
- Enums
- Regras condicionais
- Estado do projeto
- Consistência entre fases
- Regras de status
- Repository Pattern (persistência JSON)

## Princípio

O domínio:

- Não conhece HTML
- Não conhece Flask
- Não conhece PyInstaller
- Não conhece UI
- Não depende de renderização

---

# 4. Camada de Interface Web (`ui/`)

## Estrutura

```
ui/
 └── backend/
      ├── app.py
      ├── routes
      ├── templates
      └── static
```

## Responsabilidade

- Receber input do usuário
- Converter form → domínio canônico
- Persistir via repository
- Renderizar páginas HTML

## Regra Arquitetural

A UI não contém regras de negócio.  
Ela apenas consome e respeita o domínio.

---

# 5. Camada de Renderização (`rendering/`)

## Responsabilidade

Transformar o JSON canônico em:

- Markdown
- HTML
- PDF (futuro adapter)

Esses são artefatos derivados.

Se o domínio mudar, a renderização reflete automaticamente.

---

# 6. Metadata OTM (`metadata/`)

Contém arquivos auxiliares usados como referência:

- Tabelas elegíveis para migração
- Catálogo de deployment_type
- Referências estruturais do OTM

É sempre read-only do ponto de vista do projeto.

---

# 7. Infraestrutura (`infra/`)

Responsável por:

- Integrações técnicas
- Serviços auxiliares
- Futuras integrações externas
- Organização estrutural de suporte

Não contém regra de domínio.

---

# 8. Scripts (`scripts/`)

Scripts auxiliares:

- Extrações
- Conversões
- Automatizações técnicas
- Ferramentas operacionais

Não participam da governança de regras.

---

# 9. Documentação (`docs/`)

Contém:

- Arquitetura
- Runbooks
- Referências técnicas
- Estrutura do projeto
- Diretrizes arquiteturais

Esta pasta é a documentação institucional do sistema.

---

# 10. Build e Empacotamento

## Arquivos

- `omni_launcher.py`
- `omni_launcher.spec`
- `build_release.sh`

## Fluxo

1. PyInstaller gera o bundle
2. xattr remove metadata inválido
3. codesign aplica assinatura ad-hoc
4. App é movido para /Applications

O aplicativo final é:

OmniDeck Suite.app

---

# 11. Persistência

A persistência utiliza:

- Repository Pattern
- JSON como armazenamento principal
- Estrutura canônica validada pelo domínio

O app é apenas uma interface.  
Os dados permanecem no repositório local.

---

# 12. Princípios Arquiteturais

- JSON é a fonte única da verdade
- Domínio governa regras
- UI nunca governa lógica
- Renderização é derivada
- Metadata é referência
- Enums garantem consistência
- Validações são obrigatórias
- Texto livre não governa regra

---

# 13. Estado Atual

✔ UI Web funcional  
✔ Validação centralizada  
✔ Persistência JSON  
✔ Build macOS via PyInstaller  
✔ Assinatura ad-hoc  
✔ Instalação em /Applications  
✔ Script de release padronizado  

Próximos adapters planejados:

- CLI
- HTML/PDF estruturado
- Exportadores automatizados

---

# 14. Modelo Mental

O OmniDeck é:

Um motor de governança de migração OTM com geração automática de documentação técnica.

Não é apenas um gerador de PDF.  
Não é apenas um checklist.  
É um sistema de domínio estruturado.