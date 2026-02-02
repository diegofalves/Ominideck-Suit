/**
 * Schema-Driven Form Engine (OmniDeck 9.0)
 * 
 * Responsabilidades:
 * - Carregar lista de tabelas OTM do API
 * - Renderizar seletor de tabelas
 * - Carregar campos dinâmicos por seção
 * - Validar dados em tempo real
 * - Hidrar formulário ao carregar
 */

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
        console.log("[SchemaEngine] Inicializando...");
        await this.loadTableList();
        this.setupEventListeners();
        console.log("[SchemaEngine] Pronto");
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
            this.populateTableSelector();
        } catch (error) {
            console.error("[SchemaEngine] Erro ao carregar tabelas:", error);
        }
    },
    
    populateTableSelector() {
        const selector = document.getElementById("schema-table-selector");
        if (!selector) return;
        
        // Limpar opções existentes (mantém placeholder)
        while (selector.options.length > 1) {
            selector.remove(1);
        }
        
        // Adicionar tabelas
        this.tables.forEach(table => {
            const option = document.createElement("option");
            option.value = table;
            option.textContent = table;
            selector.appendChild(option);
        });
    },
    
    // ========================================================
    // Load schema for selected table
    // ========================================================
    
    async loadTableSchema(tableName) {
        if (!tableName) {
            console.log("[SchemaEngine] Tabela limpa");
            this.currentTable = null;
            this.currentSchema = null;
            this.hideSchemaPreview();
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
            console.log(`[SchemaEngine] Seções: ${Object.keys(data.sections).join(", ")}`);
            
            this.showSchemaPreview(tableName, data);
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
            alert("Nenhuma tabela selecionada");
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
            const div = this.createFieldDiv(field);
            fieldset.appendChild(div);
        });
        
        return fieldset;
    },
    
    createFieldDiv(field) {
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
        const input = this.createInputElement(field);
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
    
    createInputElement(field) {
        const input = document.createElement("input");
        input.name = field.name;
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
            select.name = field.name;
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
    // Event Listeners
    // ========================================================
    
    setupEventListeners() {
        const selector = document.getElementById("schema-table-selector");
        const loadBtn = document.getElementById("load-schema-btn");
        
        if (selector) {
            selector.addEventListener("change", (e) => {
                this.loadTableSchema(e.target.value);
            });
        }
        
        if (loadBtn) {
            loadBtn.addEventListener("click", () => {
                this.renderSchemaFields();
            });
        }
    }
};

// ============================================================
// Initialize on document ready
// ============================================================

document.addEventListener("DOMContentLoaded", () => {
    SchemaEngine.init();
});
