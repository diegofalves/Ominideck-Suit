// State global para rastreamento de índices
let groupIndexCounter = 0;
let objectIndexCounters = {}; // {groupIndex: counter}

// ============================================================
// GERENCIAMENTO DE GRUPOS
// ============================================================

function addGroup() {
  const container = document.getElementById("groups-container");
  const groupIndex = groupIndexCounter++;
  objectIndexCounters[groupIndex] = 0;

  const groupDiv = document.createElement("div");
  groupDiv.className = "group-block";
  groupDiv.dataset.groupIndex = groupIndex;
  groupDiv.style.border = "2px solid #999";
  groupDiv.style.padding = "16px";
  groupDiv.style.marginBottom = "20px";
  groupDiv.style.backgroundColor = "#f9f9f9";

  groupDiv.innerHTML = `
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
      <h3 style="margin: 0;">Grupo ${groupIndex + 1}</h3>
      <button type="button" onclick="removeGroup(${groupIndex})" style="background: #d32f2f; color: white; padding: 6px 12px; border: none; cursor: pointer; border-radius: 4px;">
        ❌ Remover Grupo
      </button>
    </div>

    <fieldset style="margin-bottom: 16px;">
      <legend>Informações do Grupo</legend>
      
      <label style="display: block; margin-bottom: 8px;">Nome do Grupo</label>
      <input 
        type="text" 
        name="groups[${groupIndex}][label]" 
        placeholder="Ex: Automação, Tabelas, etc."
        style="width: 100%; max-width: 400px; padding: 6px; margin-bottom: 12px;"
        required
      >

      <label style="display: block; margin-bottom: 8px;">Sequência</label>
      <input 
        type="number" 
        name="groups[${groupIndex}][sequence]" 
        placeholder="1, 2, 3..."
        style="width: 100%; max-width: 400px; padding: 6px;"
        min="1"
        required
      >
    </fieldset>

    <fieldset>
      <legend>Objetos</legend>
      <div class="objects-container-${groupIndex}" style="border-left: 3px solid #2196F3; padding-left: 12px; margin-bottom: 12px;"></div>
      <button type="button" onclick="addObject(${groupIndex})" style="background: #4CAF50; color: white; padding: 8px 16px; border: none; cursor: pointer; border-radius: 4px; font-weight: bold;">
        ➕ Adicionar Objeto
      </button>
    </fieldset>

    <hr style="margin: 16px 0;">
  `;

  container.appendChild(groupDiv);
}

function removeGroup(groupIndex) {
  const groupDiv = document.querySelector(`.group-block[data-group-index="${groupIndex}"]`);
  if (groupDiv) {
    groupDiv.remove();
    delete objectIndexCounters[groupIndex];
  }
}

// ============================================================
// GERENCIAMENTO DE OBJETOS
// ============================================================

function addObject(groupIndex) {
  const objectIndex = objectIndexCounters[groupIndex]++;
  const container = document.querySelector(`.objects-container-${groupIndex}`);

  const objectDiv = document.createElement("div");
  objectDiv.className = "object-block";
  objectDiv.dataset.groupIndex = groupIndex;
  objectDiv.dataset.objectIndex = objectIndex;
  objectDiv.style.backgroundColor = "white";
  objectDiv.style.border = "1px solid #ddd";
  objectDiv.style.padding = "12px";
  objectDiv.style.marginBottom = "12px";
  objectDiv.style.borderRadius = "4px";

  objectDiv.innerHTML = `
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid #eee;">
      <h4 style="margin: 0; color: #666;">Objeto #${objectIndex + 1}</h4>
      <button type="button" onclick="removeObject(${groupIndex}, ${objectIndex})" style="background: #f44336; color: white; padding: 4px 8px; border: none; cursor: pointer; border-radius: 3px; font-size: 12px;">
        🗑️ Remover
      </button>
    </div>

    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 12px;">
      <div>
        <label style="display: block; font-weight: bold; margin-bottom: 4px;">Tipo de Objeto</label>
        <select 
          name="groups[${groupIndex}][objects][${objectIndex}][object_type]"
          class="dynamic-object-type-selector"
          style="width: 100%; padding: 6px;"
          required
        >
          <!-- Será populado por SchemaEngine -->
        </select>
      </div>

      <div>
        <label style="display: block; font-weight: bold; margin-bottom: 4px;">Tipo de Deployment</label>
        <select 
          name="groups[${groupIndex}][objects][${objectIndex}][deployment_type]"
          style="width: 100%; padding: 6px;"
          required
        >
          <option value="">Selecione...</option>
          <option value="MIGRATION_PROJECT">MIGRATION_PROJECT</option>
          <option value="MANUAL">MANUAL</option>
          <option value="CSV">CSV</option>
        </select>
      </div>
    </div>

    <div style="margin-bottom: 12px;">
      <label style="display: block; font-weight: bold; margin-bottom: 4px;">Sequência</label>
      <input 
        type="number" 
        name="groups[${groupIndex}][objects][${objectIndex}][sequence]"
        style="width: 100%; max-width: 200px; padding: 6px;"
        placeholder="1, 2, 3..."
        min="1"
      >
    </div>
  `;

  container.appendChild(objectDiv);
}

function removeObject(groupIndex, objectIndex) {
  const objectDiv = document.querySelector(
    `.object-block[data-group-index="${groupIndex}"][data-object-index="${objectIndex}"]`
  );
  if (objectDiv) {
    objectDiv.remove();
  }
}

async function toggleIdentifiers(selectElement, groupIndex, objectIndex) {
  const tableName = selectElement.value;
  const identifiersContainer = document.getElementById(`identifiers-${groupIndex}-${objectIndex}`);

  if (!tableName) {
    identifiersContainer.innerHTML = `<p style="color: #999; font-size: 12px; margin: 0;">Selecione uma tabela OTM</p>`;
    return;
  }

  // Mostrar loading
  identifiersContainer.innerHTML = `<p style="color: #666; font-size: 12px; margin: 0;">⏳ Carregando chave primária...</p>`;

  try {
    // Buscar schema da tabela
    const response = await fetch(`/api/schema/${tableName}/raw`);
    if (!response.ok) {
      throw new Error('Schema não encontrado');
    }
    
    const schema = await response.json();
    const primaryKey = schema.primaryKey || [];
    
    if (primaryKey.length === 0) {
      identifiersContainer.innerHTML = `<p style="color: #f44336; font-size: 12px; margin: 0;">⚠️ Tabela sem chave primária definida</p>`;
      return;
    }
    
    // Renderizar campos da PK
    let html = '';
    primaryKey.forEach(pk => {
      const columnName = pk.columnName || pk;
      html += `
        <div style="margin-bottom: 8px;">
          <label style="display: block; font-size: 12px; color: #666; margin-bottom: 4px;">${columnName}</label>
          <input 
            type="text" 
            name="groups[${groupIndex}][objects][${objectIndex}][identifiers][${columnName}]"
            placeholder="Valor da chave primária"
            style="width: 100%; padding: 6px; font-size: 12px; border: 1px solid #ccc; border-radius: 3px;"
            required
          >
        </div>
      `;
    });
    
    identifiersContainer.innerHTML = html;
  } catch (error) {
    console.error('[toggleIdentifiers] Erro ao carregar PK:', error);
    identifiersContainer.innerHTML = `<p style="color: #f44336; font-size: 12px; margin: 0;">❌ Erro ao carregar chave primária</p>`;
  }
}

// ============================================================
// REIDRATAÇÃO (carregar projeto existente)
// ============================================================

function hydrateProject(projectJson) {
  if (!projectJson || !projectJson.groups) {
    return;
  }

  // Limpar container
  const container = document.getElementById("groups-container");
  container.innerHTML = '';
  groupIndexCounter = 0;
  objectIndexCounters = {};

  projectJson.groups.forEach((group, groupIdx) => {
    addGroup();

    // Preencher grupo
    const groupDiv = document.querySelector(`.group-block[data-group-index="${groupIdx}"]`);
    if (groupDiv) {
      const labelInput = groupDiv.querySelector(`input[name="groups[${groupIdx}][label]"]`);
      const seqInput = groupDiv.querySelector(`input[name="groups[${groupIdx}][sequence]"]`);

      if (labelInput) labelInput.value = group.label || '';
      if (seqInput) seqInput.value = group.sequence || '';

      // Adicionar objetos
      if (group.objects && group.objects.length > 0) {
        group.objects.forEach((obj, objIdx) => {
          addObject(groupIdx);

          // Preencher objeto
          const typeSelect = groupDiv.querySelector(
            `select[name="groups[${groupIdx}][objects][${objIdx}][object_type]"]`
          );
          const deploySelect = groupDiv.querySelector(
            `select[name="groups[${groupIdx}][objects][${objIdx}][deployment_type]"]`
          );
          const seqObjInput = groupDiv.querySelector(
            `input[name="groups[${groupIdx}][objects][${objIdx}][sequence]"]`
          );

          if (typeSelect) {
            // Compatibilidade: suporta tanto 'object_type' quanto 'type'
            const objectTypeValue = obj.object_type || obj.type || '';
            typeSelect.value = objectTypeValue;
            // Trigger change para renderizar identifiers
            if (objectTypeValue) {
              toggleIdentifiers(typeSelect, groupIdx, objIdx);
            }
          }
          if (deploySelect) deploySelect.value = obj.deployment_type || '';
          if (seqObjInput) seqObjInput.value = obj.sequence || '';

          // Preencher identifiers
          if (obj.identifiers) {
            Object.keys(obj.identifiers).forEach(key => {
              const identInput = groupDiv.querySelector(
                `input[name="groups[${groupIdx}][objects][${objIdx}][identifiers][${key}]"]`
              );
              if (identInput) identInput.value = obj.identifiers[key] || '';
            });
          }
        });
      }
    }
  });
}

// ============================================================
// Bootstrap ao carregar a página
// ============================================================

document.addEventListener('DOMContentLoaded', function() {
  const existingProjectElement = document.getElementById('existing-project-data');
  if (existingProjectElement) {
    try {
      const projectData = JSON.parse(existingProjectElement.textContent);
      hydrateProject(projectData);
    } catch (e) {
      console.error('Erro ao carregar projeto:', e);
    }
  }
});
