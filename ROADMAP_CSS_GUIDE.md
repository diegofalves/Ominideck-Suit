# 📋 Guia CSS - Capítulo "Roadmap de Migração"

## 📌 Contexto

Este documento descreve a arquitetura CSS preparada para o capítulo **"Roadmap de Migração"** no documento de migração OTM.

O capítulo apresenta um **plano de execução visual** agrupado por **Deployment Types** (MANUAL, MIGRATION, CSV, DB.XML, ZIP BI), facilitando a compreensão da sequência e estratégia de implantação.

---

## 🎯 Objetivo do Capítulo

O Roadmap de Migração deve:

✅ Ser visualmente um plano executivo  
✅ Agrupar objetos por tipo de deployment  
✅ Manter hierarquia clara e legível  
✅ Garantir paginação segura em A4  
✅ Ter identidade visual coerente com o resto do documento  

---

## 🏗️ Estrutura HTML Esperada

```html
<section class="roadmap-page">
  <!-- Cabeçalho -->
  <header class="roadmap-page__header">
    <h2 class="roadmap-page__title">Roadmap de Migração</h2>
    <p class="roadmap-page__description">
      Descrição do roadmap completo...
    </p>
  </header>

  <!-- Bloco: MANUAL -->
  <div class="deployment-type-block deployment-type--manual">
    <div class="deployment-type-block__header">
      <h3 class="deployment-type-block__title">MANUAL</h3>
      <span class="deployment-type-block__count">5 objetos</span>
    </div>
    <p class="deployment-type-block__description">
      Descrição da estratégia MANUAL...
    </p>
    <ul class="deployment-type-block__items">
      <li class="deployment-type-block__item">
        <span class="deployment-type-block__item-name">ACCOUNT_NUMBER</span>
        <span class="deployment-type-block__item-detail">(1/5)</span>
      </li>
      <!-- Mais itens -->
    </ul>
  </div>

  <!-- Bloco: MIGRATION -->
  <div class="deployment-type-block deployment-type--migration">
    <!-- Estrutura similar -->
  </div>

  <!-- Bloco: CSV -->
  <div class="deployment-type-block deployment-type--csv">
    <!-- Estrutura similar -->
  </div>

  <!-- Bloco: DB.XML -->
  <div class="deployment-type-block deployment-type--dbxml">
    <!-- Estrutura similar -->
  </div>

  <!-- Bloco: ZIP BI -->
  <div class="deployment-type-block deployment-type--zipbi">
    <!-- Estrutura similar -->
  </div>
</section>
```

---

## 🎨 Classes CSS e Seus Papéis

### Contêiner Principal

**`.roadmap-page`**
- Wrapper do capítulo inteiro
- `page-break-before: always` → inicia em nova página
- `page-break-inside: avoid` → evita quebra no meio
- `padding: 0` → usa padding de `.page-container` pai

**`.roadmap-page__header`**
- Container do título e descrição
- `page-break-after: avoid` → mantém título com conteúdo

**`.roadmap-page__title`**
- Título h2 do capítulo
- `font-size: 1.5rem` → destaque apropriado
- `border-bottom: 3px solid var(--color-accent)` → separação visual
- `margin-bottom: 1rem` → espaçamento consistente

**`.roadmap-page__description`**
- Parágrafo de contexto do roadmap
- `page-break-after: avoid` → mantém com título

---

### Blocos de Deployment Type

**`.deployment-type-block`**
- Card visual para cada tipo de deploy
- `margin: 1.5rem 0` → espaçamento vertical
- `padding: 1.5rem` → conteúdo interno
- `background: #f8fafb` → fundo leve, não ofuscante
- `border: 1px solid var(--card-border-subtle)` → definição de borda sutil
- `border-left: 4px solid var(--color-accent)` → accent bar à esquerda
- `page-break-inside: avoid` → **CRÍTICO**: evita quebra do bloco

**Modificadores de Deploy Type** (cores distintas):
- `.deployment-type--manual` → Azul (#3b82f6)
- `.deployment-type--migration` → Roxo (#8b5cf6)
- `.deployment-type--csv` → Cyan (#06b6d4)
- `.deployment-type--dbxml` → Âmbar (#f59e0b)
- `.deployment-type--zipbi` → Rosa (#ec4899)

---

### Header do Bloco

**`.deployment-type-block__header`**
- Linha com título + contagem
- `display: flex` + `justify-content: space-between` → alinhamento
- `border-bottom: 2px solid var(--card-border-subtle)` → separação
- `page-break-after: avoid` → mantém com conteúdo

**`.deployment-type-block__title`**
- Nome do deployment type (MANUAL, MIGRATION, etc.)
- `font-size: 1.1rem` + `font-weight: 600` → destaque
- `text-transform: uppercase` → padronização
- `letter-spacing: 0.5px` → legibilidade

**`.deployment-type-block__count`**
- Badge com "N objetos"
- `background: rgba(31, 78, 121, 0.08)` → sutil
- `padding: 0.3rem 0.8rem` + `border-radius: 12px` → pill shape

---

### Conteúdo do Bloco

**`.deployment-type-block__description`**
- Explicação da estratégia do deployment type
- `font-size: 0.85rem` + `color: #556b82` → secundário
- `line-height: 1.5` → legibilidade
- `page-break-after: avoid`

**`.deployment-type-block__items`**
- Lista não-ordenada de objetos
- `list-style: none` → customizado
- `display: flex` + `flex-direction: column` + `gap: 0.75rem`
- Cada item é um `li.deployment-type-block__item`

**`.deployment-type-block__item`**
- Cada objeto da lista
- Bullet customizado com `::before` em cor do deploy type
- `page-break-inside: avoid` → não quebra item

**`.deployment-type-block__item-name`**
- Nome do objeto (ex: ACCOUNT_NUMBER)
- `font-weight: 500` + `color: var(--color-headline)`

**`.deployment-type-block__item-detail`**
- Informação auxiliar (ex: "1/5")
- `color: var(--color-muted)` + `font-size: 0.8rem`

---

### Resumo Estatístico (Opcional)

**`.deployment-type-block__summary`**
- Grid com estatísticas do bloco
- `grid-template-columns: auto auto auto` → 3 colunas
- `gap: 1.5rem` → espaçamento

**`.deployment-type-block__stat`**
- Célula de estatística
- Centralizada e `page-break-inside: avoid`

**`.deployment-type-block__stat-number`**
- Número grande (ex: "5")
- `font-size: 1.4rem` + `font-weight: 700`

**`.deployment-type-block__stat-label`**
- Rótulo (ex: "OBJETOS")
- `font-size: 0.75rem` + `text-transform: uppercase`

---

## 📐 Layout e Paginação

### Garantias de A4

| Elemento | Propriedade | Valor | Razão |
|----------|-------------|-------|-------|
| `.roadmap-page` | `page-break-before` | `always` | Sempre inicia em página nova |
| `.roadmap-page` | `page-break-inside` | `avoid` | Evita quebra do capítulo inteiro |
| `.deployment-type-block` | `page-break-inside` | `avoid` | Bloco completo na mesma página |
| `.roadmap-page__header` | `page-break-after` | `avoid` | Mantém título com conteúdo |
| `.deployment-type-block__header` | `page-break-after` | `avoid` | Mantém header com blocos |

### Espaçamento

```
Roadmap de Migração (h2)
  ↓ 1rem
Descrição do Roadmap
  ↓ 1.5rem
┌─────────────────────────────┐
│ MANUAL (header)             │  1.5rem padding interno
│ ─────────────────────────── │
│ Descrição...                │  1rem margin-bottom
│                             │
│ • ACCOUNT_NUMBER (1/5)      │  0.75rem gap entre itens
│ • ...                       │
└─────────────────────────────┘
  ↓ 1.5rem margin-bottom
┌─────────────────────────────┐
│ MIGRATION                   │  ... repetir
└─────────────────────────────┘
```

---

## 🎯 Exemplo HTML Completo

```html
<section class="roadmap-page">
  <header class="roadmap-page__header">
    <h2 class="roadmap-page__title">Roadmap de Migração</h2>
    <p class="roadmap-page__description">
      Este capítulo apresenta a estratégia de execução da migração, 
      agrupada por tipo de implantação (Deployment Type). Cada bloco 
      representa um grupo coeso de objetos que devem ser migrados 
      seguindo a mesma tática operacional.
    </p>
  </header>

  <!-- MANUAL -->
  <div class="deployment-type-block deployment-type--manual">
    <div class="deployment-type-block__header">
      <h3 class="deployment-type-block__title">MANUAL</h3>
      <span class="deployment-type-block__count">5 objetos</span>
    </div>
    <p class="deployment-type-block__description">
      Implantação manual no ambiente de destino. Objetos que requerem 
      ação humana direta e validação específica.
    </p>
    <ul class="deployment-type-block__items">
      <li class="deployment-type-block__item">
        <span class="deployment-type-block__item-name">ACCOUNT_NUMBER</span>
        <span class="deployment-type-block__item-detail">(1/5)</span>
      </li>
      <li class="deployment-type-block__item">
        <span class="deployment-type-block__item-name">ACTION_DEF</span>
        <span class="deployment-type-block__item-detail">(2/5)</span>
      </li>
      <li class="deployment-type-block__item">
        <span class="deployment-type-block__item-name">ACTIVITY_TYPE</span>
        <span class="deployment-type-block__item-detail">(3/5)</span>
      </li>
      <li class="deployment-type-block__item">
        <span class="deployment-type-block__item-name">ACCESSORIAL_CODE</span>
        <span class="deployment-type-block__item-detail">(4/5)</span>
      </li>
      <li class="deployment-type-block__item">
        <span class="deployment-type-block__item-name">AD_REGION</span>
        <span class="deployment-type-block__item-detail">(5/5)</span>
      </li>
    </ul>
  </div>

  <!-- MIGRATION -->
  <div class="deployment-type-block deployment-type--migration">
    <div class="deployment-type-block__header">
      <h3 class="deployment-type-block__title">MIGRATION</h3>
      <span class="deployment-type-block__count">12 objetos</span>
    </div>
    <p class="deployment-type-block__description">
      Migração via projeto de migração nativo do OTM. 
      Objetos transportados com configurações relacionadas.
    </p>
    <ul class="deployment-type-block__items">
      <li class="deployment-type-block__item">
        <span class="deployment-type-block__item-name">SAVED_QUERY</span>
        <span class="deployment-type-block__item-detail">(1/12)</span>
      </li>
      <li class="deployment-type-block__item">
        <span class="deployment-type-block__item-name">SAVED_CONDITION</span>
        <span class="deployment-type-block__item-detail">(2/12)</span>
      </li>
      <!-- ... mais 10 ... -->
    </ul>
  </div>

  <!-- CSV, DB.XML, ZIP BI seguem padrão similar -->
</section>
```

---

## ✅ Checklist para Implementação no Jinja2

- [ ] Criar seção `roadmap-page` no template
- [ ] Adicionar heading h2 com classe `roadmap-page__title`
- [ ] Incluir parágrafo descritivo com classe `roadmap-page__description`
- [ ] Loop através dos deployment types (MANUAL, MIGRATION, CSV, DB.XML, ZIP BI)
- [ ] Para cada tipo: criar `div.deployment-type-block.deployment-type--{tipo}`
- [ ] Adicionar header com título em h3 e badge de contagem
- [ ] Adicionar descrição do deployment type
- [ ] Listar objetos em `ul.deployment-type-block__items`
- [ ] Usar `page-break-before: always` na seção para nova página
- [ ] Testar paginação em PDF com wkhtmltopdf

---

## 🧪 Testes de Paginação

```bash
# Gerar PDF com wkhtmltopdf
wkhtmltopdf \
  --enable-local-file-access \
  --page-size A4 \
  --margin-top 10mm \
  --margin-bottom 10mm \
  --margin-left 2mm \
  --margin-right 2mm \
  rendering/html/projeto_migracao.html \
  output-roadmap.pdf

# Validar:
# 1. Roadmap inicia em página nova
# 2. Blocos não quebram no meio
# 3. Cores dos deployment types estão corretas
# 4. Espaçamento é consistente
# 5. Sem páginas em branco desnecessárias
```

---

## 📚 Referências de Design

- **Tipografia**: Calibri/Arial (corpo), JetBrains Mono (código)
- **Cores Accent**: #1f4e79 (primária), com variações por deploy type
- **Espaçamento**: 1.5rem margens, 1rem padding interno
- **Quebras**: `page-break-inside: avoid` nos elementos críticos
- **Hierarquia**: h2 (capítulo) → h3 (deployment type) → lista (objetos)

---

**Criado**: 2026-02-05  
**Última Atualização**: 2026-02-05  
**Status**: ✅ CSS Preparado - Aguardando Implementação Jinja2
