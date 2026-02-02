# OmniDeck - Resumo de Ajustes Implementados

## Ajuste 9.1.1 - Nome Funcional e Descrição de Objetos

**Commit:** `f934d07`

### Objetivo
Adicionar campos `name` (obrigatório) e `description` (opcional) para cada objeto do projeto, independente do tipo (lógico ou tabela OTM).

### Implementação

#### Frontend
- **Template:** Campos "Nome do Objeto" e "Descrição Funcional" adicionados em `projeto_migracao.html`
- **JavaScript:** Formulário dinâmico atualizado em `app.js` para incluir os novos campos
- **Hydrate:** Função `hydrateProject()` carrega `name` e `description` de projetos existentes

#### Backend
- **Parser:** `form_to_domain.py` inicializa objetos com `name` e `description`
- **Validação:** `validators.py` garante que `name` é obrigatório
- **Compatibilidade:** `writers.py` gera fallback `"TYPE #index"` para objetos antigos

#### UI/UX
- **Lista de Objetos:** Exibe nome como rótulo principal (negrito)
- **Dropdown:** Mostra nome funcional ao invés de "Objeto #X"
- **Metadados:** `type` e `deployment_type` aparecem como informação secundária

### Estrutura JSON
```json
{
  "name": "Query de Elegibilidade de Frete",
  "description": "Query para buscar ordens elegíveis",
  "object_type": "SAVED_QUERY",
  "deployment_type": "MIGRATION_PROJECT"
}
```

---

## Ajuste 9.1.2 - Saved Query SQL e Status Editáveis

**Commit:** Em progresso

### Objetivo
Permitir ao usuário:
1. Editar conteúdo SQL quando objeto for tipo `SAVED_QUERY`
2. Editar status de documentação e deployment para qualquer tipo de objeto

### Implementação

#### A) Saved Query SQL

**Frontend:**
- **Template:** Bloco `#saved_query_block` com textarea (hidden por padrão)
- **Schema Engine:** Controle show/hide condicional baseado em `object_type`
  - `SAVED_QUERY` → mostra textarea + required
  - Outro tipo → esconde textarea

**Backend:**
- **Parser:** Lê `saved_query_sql` e persiste em `object.saved_query.sql`
- **Validação:** SQL obrigatório se tipo = `SAVED_QUERY`
- **Compatibilidade:** `load_project()` inicializa `saved_query: {sql: ""}` para SAVED_QUERY antigos

**Estrutura JSON:**
```json
{
  "object_type": "SAVED_QUERY",
  "saved_query": {
    "sql": "SELECT * FROM ORDER_RELEASE WHERE STATUS = 'ACTIVE'"
  }
}
```

#### B) Status Editáveis

**Frontend:**
- **Template:** 2 dropdowns sempre visíveis (documentation + deployment)
- **Formulário Dinâmico:** Status incluído em objetos criados via `addObject()`
- **Hydrate:** Carrega `status.documentation` e `status.deplaoyment` corretamente

**Backend:**
- **Parser:** Trata `status_documentation` e `status_deployment` (campos aninhados)
- **Validação:** Valores permitidos: `PENDING`, `IN_PROGRESS`, `DONE`
- **Compatibilidade:** Status default `{"documentation": "PENDING", "deployment": "PENDING"}`

**Valores Permitidos:**
- `PENDING` - Pendente
- `IN_PROGRESS` - Em andamento
- `DONE` - Concluído

**Estrutura JSON:**
```json
{
  "status": {
    "documentation": "IN_PROGRESS",
    "deployment": "PENDING"
  }
}
```

### Arquivos Modificados

| Arquivo | Mudança |
|---------|---------|
| `ui/frontend/templates/projeto_migracao.html` | + bloco saved_query + dropdowns status |
| `ui/frontend/static/js/app.js` | + campos no formulário dinâmico + hydrate |
| `ui/frontend/static/js/schema-engine.js` | + controle show/hide saved_query |
| `ui/backend/form_to_domain.py` | + parser campos aninhados + inicialização |
| `ui/backend/validators.py` | + validações SQL e status |
| `ui/backend/writers.py` | + compatibilidade retroativa |

### Fluxo Completo

```
┌─────────────────────────────────────────────────────┐
│ 1. UI (Template)                                    │
├─────────────────────────────────────────────────────┤
│ Usuário seleciona: object_type = "SAVED_QUERY"     │
│ → schema-engine.js mostra textarea SQL             │
│ Usuário preenche:                                   │
│   - Nome: "Query de Frete"                          │
│   - SQL: "SELECT * FROM..."                         │
│   - Status Doc: "IN_PROGRESS"                       │
│   - Status Deploy: "PENDING"                        │
└─────────────────────────────────────────────────────┘
                      ↓ POST /projeto-migracao
┌─────────────────────────────────────────────────────┐
│ 2. Parser (form_to_domain.py)                      │
├─────────────────────────────────────────────────────┤
│ Lê do form:                                         │
│   - saved_query_sql                                 │
│   - status_documentation                            │
│   - status_deployment                               │
│ Cria objeto:                                        │
│   obj["saved_query"]["sql"] = form["saved_query_sql"]│
│   obj["status"]["documentation"] = form[...]        │
└─────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────┐
│ 3. Validação (validators.py)                       │
├─────────────────────────────────────────────────────┤
│ Verifica:                                           │
│   ✓ saved_query.sql não vazio (SAVED_QUERY)        │
│   ✓ status.documentation in [PENDING,IN_PROGRESS,DONE]│
│   ✓ status.deployment in [PENDING,IN_PROGRESS,DONE]│
│ Se erro → retorna mensagem ao usuário              │
└─────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────┐
│ 4. Persistência (writers.py)                       │
├─────────────────────────────────────────────────────┤
│ save_project() grava JSON em:                      │
│ domain/projeto_migracao/projeto_migracao.json      │
│ Com estrutura completa de saved_query e status     │
└─────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────┐
│ 5. Reload (load_project)                           │
├─────────────────────────────────────────────────────┤
│ Compatibilidade retroativa aplicada:               │
│   - Objetos antigos recebem status default         │
│   - SAVED_QUERY antigos recebem saved_query vazio  │
└─────────────────────────────────────────────────────┘
```

### Exemplo Completo - Objeto SAVED_QUERY

```json
{
  "name": "Query de Elegibilidade de Frete",
  "description": "Query para buscar ordens elegíveis",
  "object_type": "SAVED_QUERY",
  "deployment_type": "MIGRATION_PROJECT",
  "status": {
    "documentation": "IN_PROGRESS",
    "deployment": "PENDING"
  },
  "saved_query": {
    "sql": "SELECT * FROM ORDER_RELEASE WHERE STATUS = 'ACTIVE'"
  },
  "identifiers": {},
  "data": {}
}
```

### Exemplo Completo - Objeto Tabela OTM

```json
{
  "name": "Order Release Principal",
  "description": "Order release do pedido 12345",
  "object_type": "ORDER_RELEASE",
  "deployment_type": "CSV",
  "status": {
    "documentation": "DONE",
    "deployment": "IN_PROGRESS"
  },
  "identifiers": {},
  "data": {
    "ORDER_RELEASE_GID": "OPS.12345",
    "ORDER_NO": "ORD-001"
  }
}
```

### Checklist de Aceitação

- ✅ Selecionar SAVED_QUERY exibe textarea e salva no JSON
- ✅ Selecionar outro tipo esconde textarea e não polui objeto
- ✅ Status dropdowns sempre aparecem e persistem
- ✅ Editar objeto existente carrega saved_query e status corretamente
- ✅ Projetos antigos continuam abrindo e salvando sem erro
- ✅ Nenhuma mudança em SchemaRepository / schema JSON
- ✅ Validação funciona corretamente (SQL obrigatório para SAVED_QUERY)

---

## Notas Técnicas

### Compatibilidade Retroativa
Todos os ajustes mantêm compatibilidade com projetos existentes:
- Objetos antigos recebem valores default seguros
- Nenhum campo obrigatório quebra projetos legados
- `load_project()` normaliza estruturas antigas

### Princípios Mantidos
- ✅ Schema-driven: tabelas OTM continuam usando `data`
- ✅ Tipos lógicos: continuam usando `identifiers`
- ✅ Validação em camadas: HTML5 + backend
- ✅ Arquitetura DDD preservada

---

## Ajuste 9.1.3 - Sincronização JSON ↔ Frontend

**Data:** 02/02/2026  
**Status:** ✅ Completo

### Problema Identificado

O campo **Tipo de Objeto** (`object_type`) não estava sendo preenchido automaticamente quando o usuário selecionava um objeto existente para edição. Isso ocorria porque:

1. A variável `current_object` não estava definida no momento da renderização inicial
2. O formulário não tinha um mecanismo para "carregar" um objeto sem validar todos os campos
3. O `data-current-type` estava sendo renderizado antes da definição da variável Jinja2

### Solução Implementada

#### 1. Definição Antecipada de `current_object`

**Arquivo:** `ui/frontend/templates/projeto_migracao.html`

Movido o bloco de definição do `current_object` para **antes** do seletor `object-type-selector`:

```jinja2
<form method="POST">
  <!-- Determinar current_object logo no início -->
  {% if project and project.active_group_id %}
    {% set active_id = project.active_group_id %}
    {% set current_group_ctx = namespace(data=none) %}
    {% if project.groups %}
      {% for g in project.groups %}
        {% if g.group_id == active_id %}
          {% set current_group_ctx.data = g %}
        {% endif %}
      {% endfor %}
    {% endif %}

    {% set last_edit_index = project.state.get('last_edit_object_index') %}
    {% set edit_object_index = last_edit_index | int if last_edit_index is not none else -1 %}
    
    {% set current_object = none %}
    {% if edit_object_index >= 0 and current_group_ctx.data %}
      {% set current_object = current_group_ctx.data.objects[edit_object_index] %}
    {% endif %}
  {% endif %}
```

#### 2. Modo "Load Object" (Carregar sem Validar)

**Arquivo:** `ui/backend/app.py`

Adicionado suporte para carregar objetos sem disparar validação completa:

```python
if request.method == "POST":
    action = request.form.get("action", "")
    
    # Ação especial: apenas carregar objeto no state
    if action == "load_object":
        edit_index = request.form.get("edit_object_index")
        if edit_index:
            project["state"]["last_edit_object_index"] = int(edit_index)
            save_project(project)
        return redirect("/projeto-migracao")
    
    # Caso contrário: validar e salvar normalmente
    domain_data = form_to_domain(request.form)
    validate_project(domain_data)
    save_project(domain_data)
    return redirect("/projeto-migracao")
```

#### 3. Auto-Submit do Dropdown

**Arquivo:** `ui/frontend/templates/projeto_migracao.html`

Dropdown de seleção de objetos submete automaticamente com `action=load_object`:

```html
<input type="hidden" name="action" value="" id="form_action">
<select id="edit_object_index" name="edit_object_index" 
        onchange="document.getElementById('form_action').value='load_object'; this.form.submit();">
  <option value="">— Criar novo objeto —</option>
  {% for obj in current_group.data.objects %}
    <option value="{{ loop.index0 }}">
      {{ obj.name }} — {{ obj.object_type }} · {{ obj.deployment_type }}
    </option>
  {% endfor %}
</select>
```

#### 4. Restauração do object_type no JavaScript

**Arquivo:** `ui/frontend/static/js/schema-engine.js`

O seletor já estava com lógica para ler `data-current-type` e restaurar após popular as opções:

```javascript
populateObjectTypeSelector() {
  selectors.forEach(selector => {
    const currentType = selector.dataset.currentType || selector.value;
    
    // Limpar e repopular com tabelas OTM
    selector.innerHTML = "";
    this.tables.forEach(table => {
      const option = document.createElement("option");
      option.value = table;
      option.textContent = table;
      selector.appendChild(option);
    });

    // Restaurar valor anterior
    if (currentType) {
      console.log(`[SchemaEngine] Restaurando currentType="${currentType}"`);
      selector.value = currentType;
      if (selector.name === "object_type") {
        this.loadTableSchema(currentType);
      }
    }
  });
}
```

### Fluxo Completo de Sincronização

```
┌─────────────────────────────────────────────────────────┐
│ 1. Página Inicial (GET /projeto-migracao)              │
├─────────────────────────────────────────────────────────┤
│ Backend:                                                │
│   → load_project() carrega JSON                         │
│   → last_edit_object_index = null                       │
│ Template:                                               │
│   → current_object = none                               │
│   → object-type-selector fica vazio                     │
│   → Dropdown "Editar Objeto" mostra 3 opções           │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ 2. Usuário Seleciona "Saved Queries" (índice 0)        │
├─────────────────────────────────────────────────────────┤
│ Frontend:                                               │
│   → onchange dispara                                    │
│   → form_action.value = "load_object"                   │
│   → form.submit()                                       │
└─────────────────────────────────────────────────────────┘
                          ↓ POST action=load_object
┌─────────────────────────────────────────────────────────┐
│ 3. Backend Processa (app.py)                           │
├─────────────────────────────────────────────────────────┤
│ Detecta action="load_object":                          │
│   → Lê edit_object_index = 0                           │
│   → project["state"]["last_edit_object_index"] = 0     │
│   → save_project() persiste state                      │
│   → redirect("/projeto-migracao")  // SEM VALIDAR      │
└─────────────────────────────────────────────────────────┘
                          ↓ GET /projeto-migracao
┌─────────────────────────────────────────────────────────┐
│ 4. Página Recarrega com Objeto Selecionado             │
├─────────────────────────────────────────────────────────┤
│ Backend:                                                │
│   → last_edit_object_index = 0                          │
│ Template:                                               │
│   → edit_object_index = 0                               │
│   → current_object = groups[0].objects[0]               │
│   → current_object.object_type = "SAVED_QUERY"          │
│   → data-current-type="SAVED_QUERY"                     │
└─────────────────────────────────────────────────────────┘
                          ↓ JavaScript Init
┌─────────────────────────────────────────────────────────┐
│ 5. SchemaEngine.populateObjectTypeSelector()           │
├─────────────────────────────────────────────────────────┤
│ Lê data-current-type="SAVED_QUERY"                     │
│ Popula selector com 2345+ tabelas OTM                  │
│ Restaura selector.value = "SAVED_QUERY"                │
│ Dispara loadTableSchema("SAVED_QUERY")                 │
│   → Mostra textarea SQL                                 │
│   → Carrega campos do objeto (name, description, etc)  │
└─────────────────────────────────────────────────────────┘
```

### Mapeamento JSON ↔ HTML

#### Campos de Projeto (Seção Superior)

| JSON Path | HTML Input name | Tipo | Observações |
|-----------|----------------|------|-------------|
| `project.code` | `code` | text | Código do projeto |
| `project.name` | `name` | text | Nome do projeto |
| `project.version` | `version` | text | Versão |
| `project.consultant` | `consultant` | text | Consultor responsável |
| `project.environment.source` | `environment.source` | text | URL ambiente origem |
| `project.environment.target` | `environment.target` | text | URL ambiente destino |

#### Campos de Grupo (Seção "Grupos do Projeto")

| JSON Path | HTML Input name | Tipo | Observações |
|-----------|----------------|------|-------------|
| `groups[i].group_id` | `groups[i].group_id` | text | ID do grupo |
| `groups[i].label` | `groups[i].label` | text | Nome exibido |
| `groups[i].sequence` | `groups[i].sequence` | number | Ordem no fluxo |

#### Campos de Objeto (Seção "Grupo Ativo")

| JSON Path | HTML Input name | Tipo | Hidratação | Observações |
|-----------|----------------|------|-----------|-------------|
| `objects[j].name` | `object_name` | text | ✅ app.js | Nome funcional (obrigatório) |
| `objects[j].description` | `object_description` | textarea | ✅ app.js | Descrição detalhada |
| `objects[j].object_type` | `object_type` | select | ✅ schema-engine.js | Tabela OTM ou tipo lógico |
| `objects[j].deployment_type` | `deployment_type` | select | ✅ app.js | MIGRATION_PROJECT, CSV, MANUAL |
| `objects[j].responsible` | `responsible` | text | ✅ app.js | Responsável pela migração |
| `objects[j].status.documentation` | `status_documentation` | select | ✅ app.js | PENDING, IN_PROGRESS, DONE |
| `objects[j].status.deployment` | `status_deployment` | select | ✅ app.js | PENDING, IN_PROGRESS, DONE |
| `objects[j].saved_query.sql` | `saved_query_sql` | textarea | ✅ app.js | SQL (condicional SAVED_QUERY) |
| `objects[j].identifiers.*` | `identifiers[...]` | text | ❌ manual | Tipos lógicos (AGENT, etc) |
| `objects[j].data.*` | `data[...]` | text | ✅ schema-driven | Tabelas OTM (campos dinâmicos) |

#### Campos de Controle (Hidden Inputs)

| JSON Path | HTML Input name | Tipo | Função |
|-----------|----------------|------|--------|
| `active_group_id` | `active_group_id` | hidden | Identifica grupo sendo editado |
| `state.last_edit_object_index` | `edit_object_index` | select | Índice do objeto sendo editado |
| N/A | `action` | hidden | Controla se é `load_object` ou `save` |
| N/A | `active_group_index` | hidden | Índice do grupo no array |

### Compatibilidade e Edge Cases

#### Objetos Antigos sem `object_type`
```python
# writers.py - load_project()
for obj in group.get("objects", []):
    if "object_type" not in obj:
        obj["object_type"] = obj.get("type", "UNKNOWN")
```

#### SAVED_QUERY sem `saved_query.sql`
```python
# writers.py - load_project()
if obj["object_type"] == "SAVED_QUERY" and "saved_query" not in obj:
    obj["saved_query"] = {"sql": ""}
```

#### Status ausentes
```python
# writers.py - load_project()
if "status" not in obj:
    obj["status"] = {
        "documentation": "PENDING",
        "deployment": "PENDING"
    }
```

### Arquivos Envolvidos

| Arquivo | Modificações |
|---------|--------------|
| `ui/frontend/templates/projeto_migracao.html` | Movida definição de `current_object` + auto-submit dropdown + campo hidden `action` |
| `ui/frontend/static/js/schema-engine.js` | Logs de debug + restauração `data-current-type` |
| `ui/backend/app.py` | Adicionado modo `action=load_object` sem validação |
| `ui/backend/form_to_domain.py` | Parser já tratava `edit_object_index` corretamente |
| `ui/backend/writers.py` | Compatibilidade retroativa para campos ausentes |

### Validações de Integridade

✅ **Teste 1:** Selecionar objeto existente → `object_type` preenchido  
✅ **Teste 2:** Criar novo objeto → `object_type` vazio (placeholder)  
✅ **Teste 3:** Trocar tipo SAVED_QUERY ↔ ORDER_RELEASE → textarea SQL aparece/some  
✅ **Teste 4:** Salvar SAVED_QUERY sem SQL → erro de validação exibido  
✅ **Teste 5:** Abrir projeto antigo → campos retrocompatíveis inicializados  
✅ **Teste 6:** Editar e salvar → persist em `projeto_migracao.json`  

### Debugging

Para rastrear o fluxo JSON → Frontend:

1. **Console do Navegador (F12):**
   ```
   [SchemaEngine] Seletor encontrado, data-current-type="SAVED_QUERY"
   [SchemaEngine] Restaurando currentType="SAVED_QUERY"
   ```

2. **Inspecionar Elemento (object-type-selector):**
   ```html
   <select name="object_type" data-current-type="SAVED_QUERY">
     <option value="SAVED_QUERY" selected>SAVED_QUERY</option>
   </select>
   ```

3. **Verificar State no JSON:**
   ```json
   "state": {
     "last_edit_object_index": 0
   }
   ```

---

## Notas Técnicas

### Compatibilidade Retroativa
Todos os ajustes mantêm compatibilidade com projetos existentes:
- Objetos antigos recebem valores default seguros
- Nenhum campo obrigatório quebra projetos legados
- `load_project()` normaliza estruturas antigas

### Princípios Mantidos
- ✅ Schema-driven: tabelas OTM continuam usando `data`
- ✅ Tipos lógicos: continuam usando `identifiers`
- ✅ Validação em camadas: HTML5 + backend
- ✅ Arquitetura DDD preservada
- ✅ Separação clara Backend (Python) ↔ Frontend (Jinja2 + JS)
- ✅ Estado persistido no JSON (`state.last_edit_object_index`)
