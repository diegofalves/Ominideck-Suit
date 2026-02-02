/**
 * Schema-Driven Form Engine (OmniDeck 9.1)
 * 
 * Modelo Correto:
 * - Tabela OTM = object_type (ex: ORDER_RELEASE, SHIPMENT)
 * - Tipos lógicos também em object_type (ex: AGENT, SAVED_QUERY)
 * - SE tipo lógico → usar identifiers (modelo antigo)
 * - SE tabela OTM → usar data (schema-driven)
 */

const LOGICAL_OBJECT_TYPES = new Set([
    "SAVED_QUERY",
    "AGENT",
    "FINDER_SET",
    "RATE",
    "EVENT_GROUP"
]);

// ============================================================
// Global State
// ============================================================

const SchemaEngine = {
    currentTable: null,
    currentSchema: null,
    tables: [],
    logicalTypes: Array.from(LOGICAL_OBJECT_TYPES),
    
    // ========================================================
    // Initialization
    // ========================================================
    
    async init() {
        console.log("[SchemaEngine 9.1] Inicializando com modelo novo...");
        await this.loadTableList();
        this.setupEventListeners();
        this.setupDynamicObjectObserver();
        console.log("[SchemaEngine 9.1] Pronto");
    },
    
    // ========================================================
    // Load table list from API
    // ========================================================
    
    async loadTableList() {
        try {
            const response = await fetch("/api/schema/tables");
            const data = await response.json();
            this.tables = data.tables || [];
            
            console.log(`[SchemaEngine] ${this.tables.length} tabelas carregadas`);
            this.populateObjectTypeSelector();
        } catch (error) {
            console.error("[SchemaEngine] Erro ao carregar tabelas:", error);
        }
    },
    
    populateObjectTypeSelector() {
        // Encontrar selects estáticos (renderizados pelo backend)
        const staticSelectors = document.querySelectorAll('select[name="object_type"]');
        
        console.log("[SchemaEngine] Selectors encontrados:", staticSelectors.length);

        if (!staticSelectors.length) {
            console.warn("[SchemaEngine] Nenhum select object_type encontrado no DOM");
            return;
        }

        // Processar cada select encontrado
        staticSelectors.forEach(selector => {
            // Passo 1: Ler valor do atributo data-current-type (renderizado pelo backend)
            const currentType = selector.getAttribute("data-current-type") || "";
            
            console.log("[SchemaEngine] Processando selector:", {
                name: selector.name,
                currentType: currentType || "(nenhum)"
            });

            // Passo 2: Limpar opções existentes
            selector.innerHTML = "";

            // Passo 3: Inserir placeholder
            const placeholder = document.createElement("option");
            placeholder.value = "";
            placeholder.textContent = "— Selecione uma tabela OTM —";
            selector.appendChild(placeholder);

            // Passo 4: Inserir tabelas OTM
            this.tables.forEach(table => {
                const option = document.createElement("option");
                option.value = table;
                option.textContent = table;
                selector.appendChild(option);
            });

            // Passo 5: Restaurar valor usando data-current-type (BACKEND-DRIVEN)
            if (currentType) {
                selector.value = currentType;
                console.log("[SchemaEngine] Valor restaurado:", {
                    selector: selector.name,
                    value: currentType
                });
            }
        });

        // Passo 6: Mostrar container do select
        const container = document.getElementById("object-type-container");
        if (container) {
            container.style.display = "block";
            console.log("[SchemaEngine] Container object-type visível");
        }
        
        console.log(`[SchemaEngine] ✅ ${staticSelectors.length} select(s) populado(s) com ${this.tables.length} tabelas OTM`);
    },

    onObjectTypeChange(objectType) {
        this.loadTableSchema(objectType);
    },
    
    // ========================================================
    // Load schema for OTM table
    // ========================================================
    
    async loadTableSchema(tableName) {
        // Se for tipo lógico: não carregar schema
        if (LOGICAL_OBJECT_TYPES.has(tableName)) {
            console.log(`[SchemaEngine] ${tableName} é tipo lógico, não carregando schema`);
            this.currentTable = null;
            this.currentSchema = null;
            this.hideSchemaPreview();
            this.hideIdentifierFields();
            this.showIdentifierFieldsForLogicalType(tableName);
            
            // Mostrar bloco Saved Query se for SAVED_QUERY
            const savedQueryBlock = document.getElementById('saved_query_block');
            if (savedQueryBlock) {
                if (tableName === 'SAVED_QUERY') {
                    savedQueryBlock.style.display = 'block';
                    const sqlTextarea = document.getElementById('saved_query_sql');
                    if (sqlTextarea) sqlTextarea.required = true;
                } else {
                    savedQueryBlock.style.display = 'none';
                    const sqlTextarea = document.getElementById('saved_query_sql');
                    if (sqlTextarea) sqlTextarea.required = false;
                }
            }
            return;
        }
        
        // Esconder bloco Saved Query para tabelas OTM
        const savedQueryBlock = document.getElementById('saved_query_block');
        if (savedQueryBlock) {
            savedQueryBlock.style.display = 'none';
            const sqlTextarea = document.getElementById('saved_query_sql');
            if (sqlTextarea) sqlTextarea.required = false;
        }
        
        // Se for tabela OTM: carregar schema
        if (!tableName) {
            console.log("[SchemaEngine] Tabela limpa");
            this.currentTable = null;
            this.currentSchema = null;
            this.hideSchemaPreview();
            this.hideIdentifierFields();
            return;
        }
        
        try {
            const response = await fetch(`/api/schema/${tableName}/fields`);
            const data = await response.json();
            
            if (data.error) {
                console.error("[SchemaEngine] Erro:", data.error);
                alert(`Erro ao carregar tabela: ${data.error}`);
                return;
            }
            
            this.currentTable = tableName;
            this.currentSchema = data;
            
            console.log(`[SchemaEngine] Schema carregado: ${tableName}`);
            
            this.showSchemaPreview(tableName, data);
            this.hideIdentifierFields();
            
            // Se for edição de objeto existente, renderizar schema com dados existentes
            const objTypeSelect = document.querySelector('select[name="object_type"]');
            if (objTypeSelect && objTypeSelect.dataset.currentType) {
                // Obter dados existentes do objeto atual
                const currentData = this.getExistingObjectData();
                if (currentData) {
                    console.log(`[SchemaEngine] Renderizando schema com dados existentes`, currentData);
                    this.renderSchemaFields(currentData);
                } else {
                    console.log(`[SchemaEngine] Renderizando schema sem dados (novo objeto)`);
                    this.renderSchemaFields(null);
                }
            }
        } catch (error) {
            console.error("[SchemaEngine] Erro ao carregar schema:", error);
        }
    },
    
    getExistingObjectData() {
        // Primeira prioridade: Dados injetados pelo template (current_object.data)
        if (window.ExistingObjectData && Object.keys(window.ExistingObjectData).length > 0) {
            console.log(`[SchemaEngine] Usando dados do template: ${Object.keys(window.ExistingObjectData).length} campos`);
            return window.ExistingObjectData;
        }
        
        // Segunda prioridade: Extrair do formulário renderizado
        const container = document.querySelector('div[id*="schema-sections"]');
        if (!container) return null;
        
        const formFields = container.querySelectorAll('input, select, textarea');
        if (formFields.length === 0) return null;
        
        const data = {};
        formFields.forEach(field => {
            // Parse "data[FIELD_NAME]" format
            const match = field.name.match(/data\[([^\]]+)\]/);
            if (match) {
                const fieldName = match[1];
                if (field.type === 'checkbox') {
                    data[fieldName] = field.checked;
                } else {
                    data[fieldName] = field.value;
                }
            }
        });
        
        return Object.keys(data).length > 0 ? data : null;
    },
    
    showSchemaPreview(tableName, schema) {
        const preview = document.getElementById("schema-preview");
        const nameSpan = document.getElementById("schema-table-name");
        const countSpan = document.getElementById("schema-field-count");
        const loadBtn = document.getElementById("load-schema-btn");
        
        if (preview && nameSpan && countSpan && loadBtn) {
            nameSpan.textContent = tableName;
            
            let totalFields = 0;
            for (const fields of Object.values(schema.sections)) {
                totalFields += fields.length;
            }
            countSpan.textContent = totalFields;
            
            preview.style.display = "block";
            loadBtn.style.display = "inline-block";
        }
    },
    
    hideSchemaPreview() {
        const preview = document.getElementById("schema-preview");
        const loadBtn = document.getElementById("load-schema-btn");
        const container = document.getElementById("schema-sections-container");
        
        if (preview) preview.style.display = "none";
        if (loadBtn) loadBtn.style.display = "none";
        if (container) {
            container.style.display = "none";
            container.innerHTML = "";
        }
    },
    
    // ========================================================
    // Render schema fields into form sections
    // ========================================================
    
    renderSchemaFields(existingData = null) {
        if (!this.currentSchema) {
            alert("Nenhuma tabela OTM selecionada");
            return;
        }
        
        const container = document.getElementById("schema-sections-container");
        if (!container) return;
        
        container.innerHTML = "";
        const sections = this.currentSchema.sections;
        
        // Renderiza cada seção com dados existentes se houver
        for (const [sectionName, fields] of Object.entries(sections)) {
            const fieldset = this.createSectionFieldset(sectionName, fields, existingData);
            container.appendChild(fieldset);
        }
        
        container.style.display = "block";
        
        console.log(`[SchemaEngine] ${Object.keys(sections).length} seções renderizadas com dados existentes`);
    },
    
    createSectionFieldset(sectionName, fields, existingData = null) {
        const fieldset = document.createElement("fieldset");
        fieldset.style.marginBottom = "24px";
        fieldset.style.padding = "16px";
        fieldset.style.border = "1px solid #ddd";
        fieldset.style.borderRadius = "4px";
        
        const legend = document.createElement("legend");
        legend.style.fontWeight = "bold";
        legend.style.color = "#2196F3";
        legend.textContent = `📋 ${sectionName}`;
        fieldset.appendChild(legend);
        
        // Renderiza cada campo com dados existentes se houver
        fields.forEach(field => {
            const div = this.createFieldDiv(field, "data", existingData);
            fieldset.appendChild(div);
        });
        
        return fieldset;
    },
    
    createFieldDiv(field, prefix = "data", existingData = null) {
        const div = document.createElement("div");
        div.style.marginBottom = "12px";
        
        // Label
        const label = document.createElement("label");
        label.style.display = "block";
        label.style.marginBottom = "4px";
        label.style.fontWeight = "500";
        
        label.innerHTML = `
            ${field.label}
            ${field.required ? '<span style="color: red;">*</span>' : ''}
            <span style="font-size: 11px; color: #999;">${field.type}</span>
        `;
        div.appendChild(label);
        
        // Input element based on type com dados existentes
        const input = this.createInputElement(field, prefix, existingData);
        div.appendChild(input);
        
        // Help text if has constraint or lookup
        if (field.constraint || field.lookup) {
            const help = document.createElement("p");
            help.style.fontSize = "11px";
            help.style.color = "#999";
            help.style.margin = "4px 0 0 0";
            
            if (field.constraint && field.constraint.options) {
                help.textContent = `✓ Valores permitidos: ${field.constraint.options.join(", ")}`;
            } else if (field.constraint && field.constraint.min !== undefined) {
                help.textContent = `✓ Range: ${field.constraint.min} - ${field.constraint.max}`;
            } else if (field.lookup) {
                help.textContent = `🔗 Lookup: ${field.lookup.table}.${field.lookup.column}`;
            }
            
            div.appendChild(help);
        }
        
        return div;
    },
    
    createInputElement(field, prefix = "data", existingData = null) {
        const input = document.createElement("input");
        input.name = `${prefix}[${field.name}]`;
        input.style.width = "100%";
        input.style.maxWidth = "400px";
        input.style.padding = "6px";
        input.style.border = "1px solid #ccc";
        input.style.borderRadius = "4px";
        
        // Set input type based on field type
        if (field.type === "number") {
            input.type = "number";
            if (field.constraint && field.constraint.min) {
                input.min = field.constraint.min;
            }
            if (field.constraint && field.constraint.max) {
                input.max = field.constraint.max;
            }
        } else if (field.type === "date") {
            input.type = "date";
        } else if (field.type === "boolean") {
            input.type = "checkbox";
            input.style.width = "auto";
        } else if (field.type === "select") {
            const select = document.createElement("select");
            select.name = `${prefix}[${field.name}]`;
            select.style.width = "100%";
            select.style.maxWidth = "400px";
            select.style.padding = "6px";
            select.style.border = "1px solid #ccc";
            select.style.borderRadius = "4px";
            
            // Add placeholder
            const placeholder = document.createElement("option");
            placeholder.value = "";
            placeholder.textContent = "— Selecione —";
            select.appendChild(placeholder);
            
            // Add options from constraint
            if (field.constraint && field.constraint.options) {
                field.constraint.options.forEach(option => {
                    const opt = document.createElement("option");
                    opt.value = option;
                    opt.textContent = option;
                    select.appendChild(opt);
                });
            }
            
            // Restaurar valor existente se disponível
            if (existingData && existingData[field.name] !== undefined) {
                select.value = existingData[field.name];
            }
            
            return select;
        } else {
            input.type = "text";
            if (field.maxLength) {
                input.maxLength = field.maxLength;
            }
        }
        
        // Restaurar valor existente ou usar default
        if (existingData && existingData[field.name] !== undefined) {
            // Valor existente tem prioridade
            if (field.type === "boolean") {
                input.checked = existingData[field.name];
            } else {
                input.value = existingData[field.name];
            }
        } else if (field.defaultValue) {
            // Usar default se não houver valor existente
            if (field.type === "boolean") {
                input.checked = field.defaultValue;
            } else {
                input.value = field.defaultValue;
            }
        }
        
        // Set required attribute
        if (field.required) {
            input.required = true;
        }
        
        // Aplicar validação leve do schema (Ajuste 9.3)
        this.attachFieldValidation(input, field);
        
        return input;
    },
    
    // ========================================================
    // Validação Leve Schema-Driven (Ajuste 9.3)
    // ========================================================
    
    attachFieldValidation(input, field) {
        // Required: destacar se vazio ao perder foco
        if (field.required) {
            input.addEventListener("blur", () => {
                if (!input.value) {
                    input.classList.add("field-error");
                } else {
                    input.classList.remove("field-error");
                }
            });
        }
        
        // Max Length: destacar se exceder ao digitar
        if (field.maxLength && input.type === "text") {
            input.addEventListener("input", () => {
                if (input.value.length > field.maxLength) {
                    input.classList.add("field-warning");
                } else {
                    input.classList.remove("field-warning");
                }
            });
        }
    },
    
    // ========================================================
    // Identifier fields for logical types
    // ========================================================
    
    hideIdentifierFields() {
        document.querySelectorAll('[id^="identifier_"]').forEach(el => {
            el.style.display = 'none';
        });
    },
    
    showIdentifierFieldsForLogicalType(objectType) {
        const mapTypeToField = {
            'SAVED_QUERY': 'identifier_query_name',
            'AGENT': 'identifier_agent_gid',
            'FINDER_SET': 'identifier_finder_set_gid',
            'RATE': 'identifier_rate_offering_gid',
            'EVENT_GROUP': 'identifier_event_group_gid'
        };
        
        if (mapTypeToField[objectType]) {
            document.getElementById(mapTypeToField[objectType]).style.display = 'block';
        }
    },
    
    // ========================================================
    // Event Listeners
    // ========================================================
    
    setupEventListeners() {
        const selector = document.querySelector('select[name="object_type"]');
        
        if (selector) {
            selector.addEventListener("change", async (e) => {
                const selectedType = e.target.value;
                if (!selectedType) {
                    this.hideIdentifierFields();
                    return;
                }
                
                if (LOGICAL_OBJECT_TYPES.has(selectedType)) {
                    // Tipo lógico: mostrar campos de identifiers
                    this.showIdentifierFieldsForLogicalType(selectedType);
                } else {
                    // Tabela OTM: carregar schema e renderizar forma
                    await this.loadTableSchema(selectedType);
                }
            });
        } else {
            console.warn("[SchemaEngine] Seletor de object_type não encontrado");
        }
        
        const loadBtn = document.getElementById("load-schema-btn");
        if (loadBtn) {
            loadBtn.addEventListener("click", () => {
                this.renderSchemaFields();
            });
        }
    },
    
    // ========================================================
    // Observer for dynamic selects
    // ========================================================
    
    setupDynamicObjectObserver() {
        // Observar mudanças no DOM para popular novos selects criados dinamicamente
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === 1) { // Element node
                        // Verificar se é um select ou contém selects
                        const selects = node.classList && node.classList.contains('dynamic-object-type-selector') 
                            ? [node] 
                            : node.querySelectorAll ? node.querySelectorAll('.dynamic-object-type-selector') : [];
                        
                        if (selects.length > 0) {
                            console.log(`[SchemaEngine] Detectado ${selects.length} novo(s) select(s), populando...`);
                            this.populateObjectTypeSelector();
                        }
                    }
                });
            });
        });
        
        // Observar o documento inteiro
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }
};

// ============================================================
// Initialize on document ready
// ============================================================

document.addEventListener("DOMContentLoaded", () => {
    SchemaEngine.init();
});
