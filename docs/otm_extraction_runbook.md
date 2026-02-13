# OTM Extraction Runbook

Este documento centraliza o modelo atual de extração OTM no OmniDeck: fluxos, scripts, saídas, índices e práticas recomendadas.

## Escopo e decisão de localização

- **Formato recomendado:** `Markdown` técnico (runbook), não `README` único.
- **Local canônico:** `docs/otm_extraction_runbook.md`.
- **Motivo:** o conteúdo é transversal (domínio + infraestrutura + cache + documentação Oracle) e evolui por versões.

## Modelo canônico de dados

Hierarquia funcional usada no projeto:

1. `Projeto de Migração`
2. `MIGRATION_GROUP`
3. `MIGRATION_ITEM`
4. `Tabela OTM` (principal + subtabelas marcadas)
5. `Objetos OTM` (linhas retornadas pelas queries)

Regras principais:

- Fonte de verdade do projeto: `domain/projeto_migracao/projeto_migracao.json`.
- Query de extração por item: `object_extraction_query.content`.
- `technical_content` permanece para notas/conteúdo técnico não-extrativo.
- Subtabelas só entram no cache quando explicitamente marcadas.
- Cache sempre normaliza colunas com base em `metadata/otm/tables/<TABLE>.json`.

## Scripts de extração e responsabilidade

### 1) Estatísticas de tabelas por domínio

- Script: `infra/update_otm_tables.py`
- Objetivo: gerar estatísticas canônicas por tabela/domínio.
- Saída: `metadata/otm/domain_table_statistics.json`
- Execução:

```bash
python3 infra/update_otm_tables.py
python3 infra/update_otm_tables.py --dry-run
```

### 2) Cache de objetos por MIGRATION_ITEM

- Script: `infra/update_otm_object_cache.py`
- Objetivo: extrair objetos dos itens do projeto e persistir cache local.
- Saídas:
  - `metadata/otm/cache/objects/*.json`
  - `metadata/otm/cache/objects_index.json`
- Execução:

```bash
python3 infra/update_otm_object_cache.py --all-migration-items
python3 infra/update_otm_object_cache.py --migration-group-id "PLANNING"
python3 infra/update_otm_object_cache.py --migration-item-name "Itineraries"
```

### 3) Cache de traduções consolidado

- Script: `infra/update_otm_translations_cache.py`
- Objetivo: extrair `TRANSLATION + TRANSLATION_D` para `pt/en`, consolidado por `TRANSLATION_GID`.
- Saídas:
  - `metadata/otm/cache/translations/otm_translations.json`
  - `metadata/otm/cache/translations/otm_translations_index.json`
- Modos:
  - Completo (full): paginação automática.
  - Incremental: atualiza somente GIDs alterados desde a última geração.
- Execução:

```bash
python3 infra/update_otm_translations_cache.py
python3 infra/update_otm_translations_cache.py --incremental
```

### 4) Download de documentação Oracle (Books/Help)

- Script: `infra/update_otm_help_index.py`
- Objetivo: detectar versão do ambiente OTM, varrer URLs Oracle e baixar HTML local.
- Saídas (por versão):
  - `metadata/otm/book otm/<versao>/html/...`
  - `metadata/otm/book otm/<versao>/meta/book_files_list.json`
  - `metadata/otm/book otm/<versao>/meta/book_locator_index.json`
  - `metadata/otm/book otm/current_version.json`
- Execução:

```bash
python3 infra/update_otm_help_index.py
python3 infra/update_otm_help_index.py --incremental
python3 infra/update_otm_help_index.py --build-index-only
```

## Executor comum OTM

- Arquivo: `infra/otm_query_executor.py`
- Papel: execução HTTP de `SQL`/`SAVED_QUERY`, parse XML e retorno padronizado.
- Melhorias já aplicadas:
  - retry com backoff exponencial para falhas transitórias.
  - timeout configurável por contexto.

Observação operacional:

- Credenciais estão temporariamente hardcoded por decisão atual do projeto.
- Quando houver infraestrutura de segredos, migrar para variável de ambiente/secret manager.

## Índices e busca rápida

Índices ativos:

- Objetos por item: `metadata/otm/cache/objects_index.json`
- Traduções por GID: `metadata/otm/cache/translations/otm_translations_index.json`
- Documentação Oracle: `metadata/otm/book otm/<versao>/meta/book_locator_index.json`

Diretriz:

- Sempre manter o índice como artefato derivado da fonte principal, atualizado no mesmo ciclo da extração.

## Práticas recomendadas para integração/extração OTM

1. Preferir APIs de serviço (REST/SOAP oficiais) para integrações de sistema-a-sistema.
2. Usar SQL/DBXML para leitura técnica interna (cache, análise, documentação), não como contrato externo.
3. Implementar paginação para evitar limite de export.
4. Implementar modo incremental para reduzir custo e tempo.
5. Aplicar retry/backoff em falhas de rede.
6. Tornar saídas idempotentes (mesma entrada, mesma estrutura de cache).
7. Versionar fontes de documentação por release (`25c`, `26a`, etc.).
8. Gerar índices para acesso rápido sem leitura integral de arquivos grandes.
9. Registrar metadados de execução (`generatedAt`, `sourceScript`, contagens).
10. Separar fonte canônica (JSON de domínio/cache) de artefatos de renderização.

## Checklist de validação pós-extração

1. Arquivo gerado existe e está em JSON válido.
2. Metadados de execução atualizados (`generatedAt`/contagens).
3. Índice correspondente atualizado.
4. Sem arquivos órfãos/legados no diretório de saída.
5. Execução incremental sem mudanças não altera conteúdo funcional.
6. Execução full mantém compatibilidade do formato.

## Comandos rápidos

```bash
# Estatísticas de tabelas (somente validação)
python3 infra/update_otm_tables.py --dry-run

# Cache de objetos (1 item)
python3 infra/update_otm_object_cache.py --migration-item-name "Itineraries" --dry-run

# Traduções incremental
python3 infra/update_otm_translations_cache.py --incremental

# Books/Help incremental
python3 infra/update_otm_help_index.py --incremental
```
