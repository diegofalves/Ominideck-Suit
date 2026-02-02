# 📋 Resumos de Ajustes — Ominideck-Suit

---

## 📋 **OmniDeck 9.0 - INSTRUÇÃO MESTRA (Schema-Driven)**

### 🎯 Objetivo

Transformar o OmniDeck em um **sistema schema-driven** baseado exclusivamente nos JSONs reais do OTM (Oracle Transportation Management), onde a fonte única da verdade é o arquivo JSON de cada tabela.

**Princípio fundamental**: O schema do OTM é um **contrato técnico**, não um detalhe de implementação. Tudo no OmniDeck deve derivar dele, nunca duplicá-lo.

---

### ❗ Proibições Explícitas

- 🚫 **NÃO criar campos** que não existam no JSON do schema
- 🚫 **NÃO inferir joins** fora de `foreignKeys`
- 🚫 **NÃO hardcode** nomes de colunas
- 🚫 **NÃO duplicar schema** em outro formato
- 🚫 **NÃO misturar schema** com dados do projeto

---

### 📂 Estrutura Obrigatória de Pastas

```
/metadata
  /otm
    /tables
      ORDER_RELEASE.json
      SHIPMENT.json
      LOCATION.json
      ... (1000+ schemas reais do OTM)
```

Cada arquivo representa uma tabela do schema OTM, no formato já existente.

---

### 📐 Padrão Esperado do JSON (Validado com ORDER_RELEASE.json)

```json
{
  "table": {
    "schema": "glogowner",
    "name": "order_release",
    "description": "..."
  },
  "columns": [
    {
      "name": "ORDER_RELEASE_GID",
      "description": "The GID for the order release.",
      "dataType": "VARCHAR2",
      "size": 101,
      "isNull": false,
      "defaultValue": "",
      "isConstraint": false,
      "constraintValues": "",
      "conditionalConstraint": ""
    }
  ],
  "primaryKey": [...],
  "foreignKeys": [...],
  "childTables": [...],
  "indices": [...]
}
```

---

### 🧩 O que Deve Ser Implementado

#### 1️⃣ **Schema Repository** (Obrigatório)

```python
# ui/backend/schema_repository.py

class SchemaRepository:
    @staticmethod
    def load_table(table_name: str) -> dict:
        """Carrega schema completo da tabela do JSON"""
        
    @staticmethod
    def list_tables() -> list[str]:
        """Lista todas as tabelas disponíveis"""
        
    @staticmethod
    def get_field_descriptors(table_name: str) -> list[FieldDescriptor]:
        """Retorna descritores normalizados de campos"""
        
    @staticmethod
    def get_foreign_keys(table_name: str) -> list[ForeignKey]:
        """Retorna relacionamentos da tabela"""
```

**Regras**:
- Nome do arquivo: `{TABLE_NAME}.json`
- ID lógico: usar `table.name`
- Cache em memória permitido

---

#### 2️⃣ **Normalização de Campos** (Campo → Formulário)

```python
# ui/backend/field_descriptor.py

class FieldDescriptor:
    name: str                    # origem: column.name
    label: str                   # origem: column.description
    type: str                    # derivado de dataType
    required: bool               # derivado de isNull
    maxLength: int               # origem: column.size
    constraint: list | dict      # origem: constraintValues
    lookup: dict                 # se foreignKey existe
    section: str                 # CORE, LOCATION, DATE, FINANCE, etc
    defaultValue: any            # origem: column.defaultValue
```

**Mapeamento obrigatório de tipos**:

| dataType OTM | Tipo UI | Input HTML |
|--------------|---------|-----------|
| VARCHAR2 | text ou select | `<input type="text">` ou `<select>` |
| NUMBER | number | `<input type="number">` |
| DATE | date | `<input type="date">` |
| CHAR(1) Y/N | boolean | `<input type="checkbox">` |
| constraintValues | dropdown | `<select>` com opções |

---

#### 3️⃣ **Uso de Foreign Keys** (Lookup Dinâmico)

Sempre que uma coluna possuir `foreignKeys`:
- ✅ Marcar campo como lookup
- ✅ Exibir:
  - Tabela pai
  - Coluna pai
- ❌ **NÃO carregar dados** automaticamente
- ✅ Apenas registrar o relacionamento para uso futuro

```python
{
    "field": "SOURCE_LOCATION_GID",
    "lookup": {
        "table": "LOCATION",
        "column": "LOCATION_GID"
    }
}
```

---

#### 4️⃣ **Geração Automática de Form Sections**

Criar agrupamentos automáticos no formulário baseado em **prefixos e padrões** (não hardcode):

| Padrão | Seção | Exemplos |
|--------|-------|----------|
| PK, XID, NAME | CORE | ORDER_RELEASE_GID, ORDER_RELEASE_XID, ORDER_RELEASE_NAME |
| *_LOCATION*, *_LOC_* | LOCALIZAÇÃO | SOURCE_LOCATION_GID, DEST_LOCATION_GID |
| *_DATE, *_TIME | DATAS | EARLY_PICKUP_DATE, LATE_DELIVERY_DATE |
| *_AMOUNT, *_COST, *_RATE | FINANCEIRO | BEST_DIRECT_COST_BUY |
| *_PLAN_*, *_SCHEDULE_* | PLANEJAMENTO | PLAN_FROM_LOCATION_GID |
| ATTRIBUTE* | FLEXFIELDS | ATTRIBUTE1, ATTRIBUTE2, ... |
| INSERT_*, UPDATE_*, DOMAIN_NAME | TÉCNICO | INSERT_USER, UPDATE_DATE |

---

#### 5️⃣ **Integração com o Editor de Migração**

O editor deve:

1. **Seletor de tabela**: escolher qual tabela (ex: ORDER_RELEASE)
2. **Carregamento automático**: disparar `SchemaRepository.load_table()`
3. **Geração de formulário**: criar campos dinamicamente
4. **Preservação de valores**: campos existentes no projeto mantêm valores
5. **Validação**: conforme `isNull`, `constraintValues` e tipo

**Fluxo**:
```
Usuário seleciona tabela
     ↓
SchemaRepository carrega schema
     ↓
Gera FieldDescriptors
     ↓
Organiza em Sections
     ↓
Preenche valores existentes
     ↓
Renderiza formulário
```

📌 JSON do projeto continua sendo a **fonte persistente**  
📌 Schema apenas **orienta UI e validação**

---

#### 6️⃣ **Validações Obrigatórias**

Antes de salvar:

- ✅ Campos `isNull = false` não podem ser vazios
- ✅ Campos com `constraintValues` devem respeitar lista
- ✅ Tipos incompatíveis devem gerar erro claro
- ✅ Colunas inexistentes no schema são rejeitadas

---

### ✅ Resultado Esperado

Após implementação:

- ✅ OmniDeck passa a ser **schema-driven**
- ✅ Formulários sempre **compatíveis com OTM real**
- ✅ Evolução segura para **dezenas de tabelas**
- ✅ Base sólida para:
  - Autocomplete
  - Documentação automática
  - Geração de SQL
  - Validação de migração
  - UI inteligente

---

### 🔄 Fases de Implementação Propostas

**Fase 1**: SchemaRepository (Foundation)  
**Fase 2**: FieldDescriptor + Pipeline Schema → UI  
**Fase 3**: Integração no Editor (Tabela Dinâmica)  
**Fase 4**: Validação Schema-Aware
