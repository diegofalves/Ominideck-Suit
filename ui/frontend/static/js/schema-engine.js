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
        const selectors = document.querySelectorAll('select[name="object_type"], .dynamic-object-type-selector');
        
        if (selectors.length === 0) {
            console.warn("[SchemaEngine] Nenhum seletor de object_type encontrado");
            return;
        }
        
        selectors.forEach(selector => {
            // Limpar opções existentes
            selector.innerHTML = "";
            
            // Adicionar placeholder
            const placeholder = document.createElement("option");
            placeholder.value = "";
            placeholder.textContent = "— Selecione uma tabela OTM —";
            selector.appendChild(placeholder);
            
            // Adicionar tabelas OTM
            this.tables.forEach(table => {
                const option = document.createElement("option");
                option.value = table;
                option.textContent = table;
                selector.appendChild(option);
            });
        });
        
        // Mostrar o fieldset que contém o select principal
        const container = document.getElementById("object-type-container");
        if (container) {
            container.style.display = "block";
        }
        
        console.log(`[SchemaEngine] ${selectors.length} seletores preenchidos com ${this.tables.length} tabelas OTM`);
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
            return;
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
        } catch (error) {
            console.error("[SchemaEngine] Erro ao carregar schema:", error);
        }
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
    
    renderSchemaFields() {
        if (!this.currentSchema) {
            alert("Nenhuma tabela OTM selecionada");
            return;
        }
        
        const container = document.getElementById("schema-sections-container");
        if (!container) return;
        
        container.innerHTML = "";
        const sections = this.currentSchema.sections;
        
        // Renderiza cada seção
        for (const [sectionName, fields] of Object.entries(sections)) {
            const fieldset = this.createSectionFieldset(sectionName, fields);
            container.appendChild(fieldset);
        }
        
        container.style.display = "block";
        
        console.log(`[SchemaEngine] ${Object.keys(sections).length} seções renderizadas`);
    },
    
    createSectionFieldset(sectionName, fields) {
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
        
        // Renderiza cada campo
        fields.forEach(field => {
            const div = this.createFieldDiv(field, "data");
            fieldset.appendChild(div);
        });
        
        return fieldset;
    },
    
    createFieldDiv(field, prefix = "data") {
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
        
        // Input element based on type
        const input = this.createInputElement(field, prefix);
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
    
    createInputElement(field, prefix = "data") {
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
            
            return select;
        } else {
            input.type = "text";
            if (field.maxLength) {
                input.maxLength = field.maxLength;
            }
        }
        
        // Set default value
        if (field.defaultValue) {
            input.value = field.defaultValue;
        }
        
        // Set required attribute
        if (field.required) {
            input.required = true;
        }
        
        return input;
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
