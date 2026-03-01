# OmniDeck Suite — README do App

## Objetivo

O OmniDeck Suite é uma interface para operação do documento de migração OTM.
O app desktop (PyWebView) e o modo navegador (Flask via terminal) devem ter **comportamento idêntico**:

- mesmas rotas;
- mesma lógica de backend;
- leitura e gravação nos **mesmos arquivos de projeto**;
- navegação equivalente.

Em resumo: o app desktop é apenas um facilitador de acesso/navegação sobre o mesmo servidor Flask.

---

## Arquitetura resumida

- **Backend:** Flask (`ui/backend/app.py`)
- **Desktop wrapper:** PyWebView (`omni_launcher.py`)
- **Templates:** `ui/frontend/templates`
- **Static:** `ui/frontend/static`
- **Domínio principal:** `domain/projeto_migracao/projeto_migracao.json`

Arquivos-chave de resolução de paths:

- `ui/backend/paths.py`
- `omni_launcher.py`

---

## Garantia de paridade Desktop x Navegador

Para evitar divergência entre o app em `/Applications` e o projeto em desenvolvimento, o launcher resolve explicitamente o root real do projeto e exporta:

- `OMNIDECK_PROJECT_ROOT`

Ordem de resolução de root no launcher:

1. variável de ambiente `OMNIDECK_PROJECT_ROOT`;
2. root do código-fonte (quando executado do projeto);
3. arquivo de hint `~/.omnideck/project_root.txt`;
4. diretório atual (quando iniciado no root do projeto);
5. fallback do bundle (`.app/Contents/Resources`);
6. fallback final local.

Com isso, o backend passa a consumir o mesmo conteúdo original do projeto também no app desktop.

---

## Como executar

### 1) Modo navegador (desenvolvimento)

No root do projeto:

- ativar venv;
- subir Flask (`python omni_launcher.py` ou `python tools/run_dev_server.py` conforme fluxo desejado);
- abrir no navegador.

### 2) Modo app desktop

- abrir `OmniDeck Suite.app` (Applications);
- o app sobe o mesmo servidor Flask local e abre a Home (`/`).

---

## Build e instalação do app

Script oficial: `tools/build/build_release.sh`

O script:

1. registra `PROJECT_ROOT` em `~/.omnideck/project_root.txt`;
2. gera bundle com PyInstaller;
3. instala em `/Applications/OmniDeck Suite.app`.

Se houver aviso de assinatura ad-hoc no macOS, o app ainda pode ser copiado manualmente de `dist/OmniDeck Suite.app` para `/Applications`.

---

## Rotas principais esperadas

- `/` → Home
- `/dashboard-documento-migracao` → Dashboard (canônica)
- `/documento-migracao` → Painel de documento (canônica)
- `/dashboard-migracao` → Dashboard (alias legado, retrocompatível)
- `/projeto-migracao` → Painel de projeto (alias legado, retrocompatível)
- `/cadastros` → Cadastros
- `/execucao-scripts` → Execução de scripts
- `/api/health` → Health check

---

## Troubleshooting rápido

### App diferente do navegador

1. Verificar `~/.omnideck/project_root.txt`.
2. Confirmar que aponta para o root correto do projeto.
3. Rebuildar com `tools/build/build_release.sh`.
4. Reinstalar o app em `/Applications`.

### Porta em uso (8088)

Encerrar processos antigos antes de subir nova instância.

### Cache visual

Já existe política de no-cache para rotas dinâmicas e limpeza de storage no carregamento do app.

---

## Estado atual (funcional)

- Home abrindo por padrão no app desktop;
- Dashboard com dados carregando;
- rotas principais com retorno 200;
- app desktop consumindo os arquivos originais do projeto.
