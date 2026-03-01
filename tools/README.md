# Tools - Ferramentas e Scripts Utilitários

Esta pasta contém scripts auxiliares, ferramentas CLI e utilitários de desenvolvimento do OmniDeck.

## Estrutura

### 📦 `build/`
Scripts e assets para construção e distribuição do app desktop.

**Arquivos:**
- `build_release.sh` - Script principal de build do app macOS (.app bundle)
- `assets/` - Assets de build (ícones, iconsets)

**Uso:**
```bash
# Build e instalação do app desktop
cd /path/to/project
./tools/build/build_release.sh
```

### 🗄️ `metadata/`
Scripts para manipulação de metadados OTM (Oracle Transportation Management).

**Scripts disponíveis:**
- `build_agent_sql_catalog.py` - Gera catálogo SQL para agents
- `build_help_consolidated.py` - Consolida documentação de ajuda
- `build_help_index.py` - Indexa documentação
- `help_converter.py` - Converte formatos de help
- `help_downloader.py` - Baixa documentação Oracle
- `link_help_to_idm.py` - Vincula help com IDM
- `normalize_help_md.py` - Normaliza markdown de help
- `update_simulated_query_projeto.py` - Atualiza queries simuladas

**Uso típico:**
```bash
python tools/metadata/build_help_index.py
```

### 🎨 `rendering/`
Scripts de renderização e geração de relatórios/documentos.

**Scripts disponíveis:**
- `build_pdf_from_json.py` - Gera PDF a partir de JSON
- `fix_json_parity.py` - Corrige paridade de dados JSON
- `objective_utils.py` - Utilitários para objetivos
- `render_html_from_md.py` - Renderiza HTML de Markdown
- `render_projeto_migracao.py` - Renderiza projeto de migração
- `validate_chain.py` - Valida cadeia de dependências
- `projeto_migracao.html.tpl` - Template HTML (legado)

**Uso típico:**
```bash
python tools/rendering/render_projeto_migracao.py
python tools/rendering/build_pdf_from_json.py --input data.json --output report.pdf
```

### 🚀 `run_dev_server.py`
Launcher alternativo para desenvolvimento (servidor Flask standalone).

**Uso:**
```bash
python tools/run_dev_server.py
# Servidor disponível em http://0.0.0.0:5000
```

## Convenções

1. **Scripts executáveis** devem ter shebang: `#!/usr/bin/env python3` ou `#!/bin/bash`
2. **Imports relativos** devem usar paths absolutos do projeto
3. **Documentação inline** - cada script deve ter docstring explicando seu propósito
4. **Logs claros** - usar mensagens descritivas e emojis para facilitar leitura no terminal

## Migração Recente

Esta estrutura foi reorganizada em março/2026 para melhor clareza:
- `scripts/*` → `tools/metadata/` (scripts de metadados OTM)
- `rendering/scripts/*` → `tools/rendering/` (scripts de renderização)
- `build_release.sh` → `tools/build/` (build scripts)
- `run.py` → `tools/run_dev_server.py` (renomeado para clareza)
