# Solução para Problema de Renderização de Tabelas no PDF

## Causa Raiz Identificada

**1. Case sensitivity:**
- O método `build_cache_filename` gerava nomes de arquivos em minúsculas (ex: `public_domain_grants_made...json`), mas os arquivos de cache estavam em MAIÚSCULAS (ex: `PUBLIC_DOMAIN_GRANTS_MADE...json`).
- Em sistemas Linux (case-sensitive), nunca havia correspondência, impedindo o carregamento dos caches.

**2. Template incompleto:**
- O bloco de "Resultado da Extração" existia apenas para o primeiro objeto de cada grupo.
- Objetos subsequentes (como Domain Grants, Properties, etc.) não tinham esse bloco, logo não exibiam tabelas.

**3. migration_item_name divergente:**
- O nome no JSON podia ter formatos diferentes do usado para gerar o arquivo de cache, causando desencontro.

---

## Solução Implementada

**Função `get_object_cache_data` com busca em 3 camadas:**
- Match exato (macOS, case-insensitive por padrão)
- Match case-insensitive via scan do diretório (resolve o problema Linux/UPPERCASE)
- Fallback por domínio + tabela + sequência + grupo — ignora variações no migration_item_name, tornando o sistema resiliente a futuros desencontros de nome

**Template atualizado:**
- O bloco de extração foi adicionado ao loop de objetos 2º+ em diante, seguindo a mesma estrutura do 1º objeto (tabela fora do `<div class="group-item">`, dentro de `<section class="page landscape">`)

---

## Resultado

- 56 tabelas renderizadas, incluindo:
  - Domain Grants (47 linhas)
  - Saved Conditions (255 linhas)
  - Service Providers (384 linhas)
  - Locations (384 linhas)
- Todos os 65 arquivos de cache encontrados e exibidos corretamente.

---

**Base de conhecimento criada em 26/02/2026.**
