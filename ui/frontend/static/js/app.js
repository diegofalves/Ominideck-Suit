// State global para rastreamento de índices
let groupIndexCounter = 0;
let objectIndexCounters = {}; // {groupIndex: counter}
let changeHistoryIndexCounter = 0;

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
      
      <label style="display: block; margin-bottom: 8px;">ID do Grupo (identificador único)</label>
      <input 
        type="text" 
        name="groups[${groupIndex}][group_id]" 
        placeholder="Ex: AUTOMATION, CONFIGURATION, MASTER_DATA"
        style="width: 100%; max-width: 400px; padding: 6px; margin-bottom: 12px;"
        required
      >

      <label style="display: block; margin-bottom: 8px;">Nome do Grupo</label>
      <input 
        type="text" 
        name="groups[${groupIndex}][label]" 
        placeholder="Ex: Automação, Tabelas, etc."
        style="width: 100%; max-width: 400px; padding: 6px; margin-bottom: 12px;"
        required
      >

      <label style="display: block; margin-bottom: 8px;">Descrição do Grupo</label>
      <textarea
        name="groups[${groupIndex}][description]"
        rows="3"
        placeholder="Descreva o propósito e escopo deste grupo"
        style="width: 100%; max-width: 600px; padding: 6px; margin-bottom: 12px; font-family: Arial, sans-serif;"
      ></textarea>
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
      <button type="button" onclick="removeObject(${groupIndex}, ${objectIndex})" style="background: #f44336; color: white; padding: 4px 8px; border: none; cursor: pointer; border-radius: 3px; font-size: 12px; display: inline-flex; align-items: center; gap: 4px;">
        🗑️ Remover
      </button>
    </div>

    <div style="margin-bottom: 12px;">
      <label style="display: block; font-weight: bold; margin-bottom: 4px;"><strong>Nome do Objeto *</strong></label>
      <input 
        type="text"
        name="groups[${groupIndex}][objects][${objectIndex}][name]"
        placeholder="Ex: Query de Elegibilidade de Frete"
        style="width: 100%; padding: 6px; font-size: 12px; border: 1px solid #ccc; border-radius: 3px;"
        required
      >
    </div>

    <div style="margin-bottom: 12px;">
      <label style="display: block; font-weight: bold; margin-bottom: 4px;">Descrição Funcional</label>
      <textarea 
        name="groups[${groupIndex}][objects][${objectIndex}][description]"
        rows="2"
        placeholder="Explique o propósito funcional deste objeto no projeto"
        style="width: 100%; padding: 6px; font-size: 12px; border: 1px solid #ccc; border-radius: 3px; font-family: Arial, sans-serif;"
      ></textarea>
    </div>

    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 12px;">
      <div>
        <label style="display: block; font-weight: bold; margin-bottom: 4px;">Status Documentação</label>
        <select 
          name="groups[${groupIndex}][objects][${objectIndex}][status_documentation]"
          style="width: 100%; padding: 6px;"
          required
        >
          <option value="PENDING">Pendente</option>
          <option value="IN_PROGRESS">Em andamento</option>
          <option value="DONE">Concluído</option>
        </select>
      </div>

      <div>
        <label style="display: block; font-weight: bold; margin-bottom: 4px;">Status Deploy</label>
        <select 
          name="groups[${groupIndex}][objects][${objectIndex}][status_deployment]"
          style="width: 100%; padding: 6px;"
          required
        >
          <option value="PENDING">Pendente</option>
          <option value="IN_PROGRESS">Em andamento</option>
          <option value="DONE">Concluído</option>
        </select>
      </div>
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
  
  // Repopular selects de tipos de objeto depois de adicionar um novo
  if (window.SchemaEngine && window.SchemaEngine.populateObjectTypeSelector) {
    setTimeout(() => {
      window.SchemaEngine.populateObjectTypeSelector();
    }, 100);
  }
}

function removeObject(groupIndex, objectIndex) {
  const objectDiv = document.querySelector(
    `.object-block[data-group-index="${groupIndex}"][data-object-index="${objectIndex}"]`
  );
  if (objectDiv) {
    objectDiv.remove();
  }
}

// ============================================================
// HISTÓRICO DE ALTERAÇÕES
// ============================================================

// Converter data de ISO (YYYY-MM-DD) para formato BR (DD/MM/YYYY)
function formatDateToBR(dateStr) {
  if (!dateStr) return '';
  // Se já está no formato BR, retorna como está
  if (dateStr.includes('/')) return dateStr;
  // Converte de YYYY-MM-DD para DD/MM/YYYY
  const parts = dateStr.split('-');
  if (parts.length === 3) {
    return `${parts[2]}/${parts[1]}/${parts[0]}`;
  }
  return dateStr;
}

function buildChangeHistoryRow(index, data = {}) {
  const row = document.createElement("tr");
  row.className = "change-history-row";
  row.dataset.index = index;
  row.style.borderBottom = "1px solid #e0e0e0";

  // Formatar data para padrão BR
  const dateBR = formatDateToBR(data.date);

  // Modo visualização (padrão)
  row.innerHTML = `
    <td style="padding: 8px; font-size: 13px;">
      <span class="view-mode" data-field="date">${dateBR || '-'}</span>
      <input type="text" class="edit-mode" name="change_history[${index}][date]" value="${dateBR || ''}" placeholder="DD/MM/YYYY" style="display: none; width: 100%; padding: 4px; font-size: 12px;">
    </td>
    <td style="padding: 8px; font-size: 13px;">
      <span class="view-mode" data-field="version">${data.version || '-'}</span>
      <input type="text" class="edit-mode" name="change_history[${index}][version]" value="${data.version || ''}" style="display: none; width: 100%; padding: 4px; font-size: 12px;">
    </td>
    <td style="padding: 8px; font-size: 13px;">
      <span class="view-mode" data-field="description">${data.description || '-'}</span>
      <input type="text" class="edit-mode" name="change_history[${index}][description]" value="${data.description || ''}" style="display: none; width: 100%; padding: 4px; font-size: 12px;">
    </td>
    <td style="padding: 8px; font-size: 13px;">
      <span class="view-mode" data-field="author">${data.author || '-'}</span>
      <input type="text" class="edit-mode" name="change_history[${index}][author]" value="${data.author || ''}" style="display: none; width: 100%; padding: 4px; font-size: 12px;">
    </td>
    <td style="padding: 2px 8px; text-align: center; font-size: 0;">
      <button type="button" class="edit-btn" onclick="toggleEditHistoryRow(${index})" style="background: #2196F3; color: white; border: none; padding: 3px 6px; border-radius: 3px; cursor: pointer; font-size: 13px; margin: 0 4px 0 0;" title="Editar">
        ✏️
      </button>
      <button type="button" class="save-btn" onclick="toggleEditHistoryRow(${index})" style="display: none; background: #4CAF50; color: white; border: none; padding: 3px 6px; border-radius: 3px; cursor: pointer; font-size: 13px; margin: 0 4px 0 0;" title="Salvar">
        ✔️
      </button>
      <button type="button" onclick="removeChangeHistoryRow(${index})" style="background: #f44336; color: white; border: none; padding: 3px 6px; border-radius: 3px; cursor: pointer; font-size: 13px; margin: 0;" title="Remover">
        🗑️
      </button>
    </td>
  `;

  return row;
}

function toggleEditHistoryRow(index) {
  const row = document.querySelector(`.change-history-row[data-index="${index}"]`);
  if (!row) return;
  
  const viewModes = row.querySelectorAll('.view-mode');
  const editModes = row.querySelectorAll('.edit-mode');
  const editBtn = row.querySelector('.edit-btn');
  const saveBtn = row.querySelector('.save-btn');
  
  const isEditing = editModes[0].style.display !== 'none';
  
  if (isEditing) {
    // Salvar: atualizar spans com valores dos inputs
    editModes.forEach((input, idx) => {
      viewModes[idx].textContent = input.value || '-';
    });
    // Trocar para modo visualização
    viewModes.forEach(span => span.style.display = '');
    editModes.forEach(input => input.style.display = 'none');
    editBtn.style.display = '';
    saveBtn.style.display = 'none';
    
    // Atualizar controle de versão
    updateVersionControl();
  } else {
    // Editar: mostrar inputs
    viewModes.forEach(span => span.style.display = 'none');
    editModes.forEach(input => input.style.display = '');
    editBtn.style.display = 'none';
    saveBtn.style.display = '';
  }
}

function addChangeHistoryRow(data = {}) {
  const container = document.getElementById("change-history-rows");
  const index = changeHistoryIndexCounter++;
  const row = buildChangeHistoryRow(index, data);
  container.appendChild(row);
  
  // Atualizar controle de versão automaticamente
  updateVersionControl();
}

function removeChangeHistoryRow(index) {
  const row = document.querySelector(`.change-history-row[data-index="${index}"]`);
  if (row) {
    row.remove();
    // Atualizar controle de versão após remover linha
    updateVersionControl();
  }
}

// Função para sincronizar Controle de Versão com última entrada do histórico
function updateVersionControl() {
  const historyContainer = document.getElementById("change-history-rows");
  if (!historyContainer) return;
  
  const allRows = Array.from(historyContainer.querySelectorAll('.change-history-row'));

  const parseHistoryDate = (rawDate) => {
    if (!rawDate) return null;
    const value = String(rawDate).trim();
    if (!value) return null;

    // DD/MM/YYYY
    let match = value.match(/^(\d{2})\/(\d{2})\/(\d{4})$/);
    if (match) {
      const day = Number(match[1]);
      const month = Number(match[2]) - 1;
      const year = Number(match[3]);
      return Date.UTC(year, month, day);
    }

    // YYYY-MM-DD
    match = value.match(/^(\d{4})-(\d{2})-(\d{2})$/);
    if (match) {
      const year = Number(match[1]);
      const month = Number(match[2]) - 1;
      const day = Number(match[3]);
      return Date.UTC(year, month, day);
    }

    const timestamp = Date.parse(value);
    return Number.isNaN(timestamp) ? null : timestamp;
  };

  const entries = allRows
    .map((row, position) => ({
      position,
      version: row.querySelector('input[name*="[version]"]')?.value?.trim() || '',
      date: row.querySelector('input[name*="[date]"]')?.value?.trim() || '',
      author: row.querySelector('input[name*="[author]"]')?.value?.trim() || ''
    }))
    .filter((entry) => entry.version || entry.date || entry.author);

  const versionField = document.getElementById('version_control_current_version');
  const dateField = document.getElementById('version_control_last_update');
  const authorField = document.getElementById('version_control_author');

  if (entries.length === 0) {
    if (versionField) versionField.value = '';
    if (dateField) dateField.value = '';
    if (authorField) authorField.value = '';
    return;
  }

  // Regra: usar a entrada mais recente por data. Se não houver data válida, usa a última preenchida.
  let latestEntry = entries[0];
  for (let i = 1; i < entries.length; i++) {
    const candidate = entries[i];
    const latestDate = parseHistoryDate(latestEntry.date);
    const candidateDate = parseHistoryDate(candidate.date);

    if (candidateDate !== null && latestDate !== null) {
      if (candidateDate > latestDate || (candidateDate === latestDate && candidate.position > latestEntry.position)) {
        latestEntry = candidate;
      }
      continue;
    }

    if (candidateDate !== null && latestDate === null) {
      latestEntry = candidate;
      continue;
    }

    if (candidateDate === null && latestDate === null && candidate.position > latestEntry.position) {
      latestEntry = candidate;
    }
  }

  if (versionField) versionField.value = latestEntry.version;
  if (dateField) dateField.value = latestEntry.date;
  if (authorField) authorField.value = latestEntry.author;
}

// Observar mudanças nos campos do histórico
function observeHistoryChanges() {
  const historyContainer = document.getElementById("change-history-rows");
  if (!historyContainer) return;
  
  // Adicionar listeners para todos os inputs existentes e futuros
  historyContainer.addEventListener('input', (e) => {
    if (e.target.tagName === 'INPUT') {
      updateVersionControl();
    }
  });
}

document.addEventListener("DOMContentLoaded", () => {
  if (window.initialChangeHistory && Array.isArray(window.initialChangeHistory)) {
    if (window.initialChangeHistory.length > 0) {
      window.initialChangeHistory.forEach((item) => addChangeHistoryRow(item));
    } else {
      addChangeHistoryRow({});
    }
  } else {
    addChangeHistoryRow({});
  }
  
  // Inicializar observador de mudanças e atualização inicial
  observeHistoryChanges();
  updateVersionControl();
});

async function toggleIdentifiers(selectElement, groupIndex, objectIndex) {
  const tableName = selectElement.value;
  let identifiersContainer = document.getElementById(`identifiers-${groupIndex}-${objectIndex}`);
  if (!identifiersContainer) {
    identifiersContainer = document.getElementById("identifiers-container");
  }
  if (!identifiersContainer) {
    console.warn('[toggleIdentifiers] Container de identifiers não encontrado no DOM');
    return;
  }

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
      const groupIdInput = groupDiv.querySelector(`input[name="groups[${groupIdx}][group_id]"]`);

      if (labelInput) labelInput.value = group.label || '';
      if (groupIdInput) groupIdInput.value = group.group_id || '';

      // Adicionar objetos
      if (group.objects && group.objects.length > 0) {
        group.objects.forEach((obj, objIdx) => {
          addObject(groupIdx);

          // Preencher objeto
          const objectBlock = groupDiv.querySelector(
            `.object-block[data-group-index="${groupIdx}"][data-object-index="${objIdx}"]`
          );
          
          if (objectBlock) {
            const typeSelect = objectBlock.querySelector(
              `select[name="groups[${groupIdx}][objects][${objIdx}][object_type]"]`
            );
            const deploySelect = objectBlock.querySelector(
              `select[name="groups[${groupIdx}][objects][${objIdx}][deployment_type]"]`
            );
            const seqObjInput = objectBlock.querySelector(
              `input[name="groups[${groupIdx}][objects][${objIdx}][sequence]"]`
            );

            if (typeSelect) {
              // Compatibilidade: suporta tanto 'object_type' quanto 'type'
              const objectTypeValue = obj.object_type || obj.type || '';
              // Adicionar atributo data-current-type para que SchemaEngine possa restaurar o valor
              if (objectTypeValue) {
                typeSelect.setAttribute('data-current-type', objectTypeValue);
              }
              typeSelect.value = objectTypeValue;
            }
            if (deploySelect) deploySelect.value = obj.deployment_type || '';
            if (seqObjInput) seqObjInput.value = obj.sequence || '';

            // Preencher nome e descrição
            const nameInput = objectBlock.querySelector(
              `input[name="groups[${groupIdx}][objects][${objIdx}][name]"]`
            );
            const descInput = objectBlock.querySelector(
              `textarea[name="groups[${groupIdx}][objects][${objIdx}][description]"]`
            );

            if (nameInput) nameInput.value = obj.name || '';
            if (descInput) descInput.value = obj.description || '';

            // Preencher status
            const statusDocSelect = objectBlock.querySelector(
              `select[name="groups[${groupIdx}][objects][${objIdx}][status_documentation]"]`
            );
            const statusDepSelect = objectBlock.querySelector(
              `select[name="groups[${groupIdx}][objects][${objIdx}][status_deployment]"]`
            );

            if (statusDocSelect && obj.status) {
              statusDocSelect.value = obj.status.documentation || 'PENDING';
            }
            if (statusDepSelect && obj.status) {
              statusDepSelect.value = obj.status.deployment || 'PENDING';
            }

            // Preencher identifiers
            if (obj.identifiers) {
              Object.keys(obj.identifiers).forEach(key => {
                const identInput = objectBlock.querySelector(
                  `input[name="groups[${groupIdx}][objects][${objIdx}][identifiers][${key}]"]`
                );
                if (identInput) identInput.value = obj.identifiers[key] || '';
              });
            }
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
  // Inicializar o contador de grupos com o número de grupos já existentes
  const projectDataEl = document.getElementById('existing-project-data');
  if (projectDataEl && projectDataEl.textContent.trim()) {
    try {
      const projectJson = JSON.parse(projectDataEl.textContent);
      if (projectJson && projectJson.groups && projectJson.groups.length > 0) {
        groupIndexCounter = projectJson.groups.length;
        console.log(`[app.js] Inicializado contador de grupos: ${groupIndexCounter} (grupos existentes)`);
      }
    } catch (e) {
      console.error('[app.js] Erro ao parsear dados do projeto:', e);
    }
  }

  document.addEventListener('change', function(e) {
    if (!e.target) return;
    if (e.target.classList && e.target.classList.contains('dynamic-object-type-selector')) {
      const objectBlock = e.target.closest('.object-block');
      if (!objectBlock) return;
      const groupIndex = objectBlock.dataset.groupIndex;
      const objectIndex = objectBlock.dataset.objectIndex;
      if (groupIndex !== undefined && objectIndex !== undefined) {
        toggleIdentifiers(e.target, groupIndex, objectIndex);
      }
    }
  });
});
