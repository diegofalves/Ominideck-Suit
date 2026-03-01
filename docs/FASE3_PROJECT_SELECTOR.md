# Fase 3: Seletor de Projeto Ativo

## Objetivo
Implementar uma interface visual para selecionar o projeto ativo na home page e persistir essa seleção em arquivo de configuração.

## Implementação

### 1. Frontend - HTML (home.html)

Adicionado dropdown de seleção no header da página home:

```html
<div class="context-item" style="display: flex; gap: 8px; align-items: center;">
  <span>Projeto Ativo:</span>
  <select id="active-project-selector" onchange="setActiveProject(this.value)">
    <option value="">-- Selecione --</option>
    {% for project in all_projects %}
    <option value="{{ project.id }}" {% if project.id == active_project_id %}selected{% endif %}>
      {{ project.name }}
    </option>
    {% endfor %}
  </select>
</div>
```

**Características:**
- Select com estilo consistente com UI (fundo translúcido, azul)
- Loop Jinja2 sobre `all_projects` passado do backend
- Marca projeto ativo com `selected` attribute
- Dispara `setActiveProject()` no change

### 2. Frontend - JavaScript (home.html)

Função para comunicar com backend:

```javascript
function setActiveProject(projectId) {
  if (!projectId) return;
  
  fetch('/api/set-active-project', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ project_id: projectId })
  })
  .then(response => {
    if (response.ok) {
      setTimeout(() => location.reload(), 300);
    } else {
      alert('Erro ao selecionar projeto');
    }
  })
  .catch(err => console.error('Erro:', err));
}
```

**Comportamento:**
- Envia POST para `/api/set-active-project` com `project_id`
- Recarrega página após 300ms se sucesso
- Mostra alert se falhar

### 3. Backend - Rota home() (app.py)

Atualizada para carregar e passar dados de projetos:

```python
@app.route("/", methods=["GET"])
def home():
    cadastros = _load_cadastros()
    
    # ... existing code ...
    
    # Carregar todos os projetos para o dropdown
    all_projects = cadastros.get("projects", [])
    
    # Carregar ID do projeto ativo
    active_project_id = os.getenv("OMNIDECK_ACTIVE_PROJECT")
    if not active_project_id:
        config_file = Path.home() / ".omnideck_config.json"
        if config_file.exists():
            try:
                with open(config_file) as f:
                    config = json.load(f)
                    active_project_id = config.get("active_project_id")
            except Exception:
                pass
    
    # Se nenhum projeto ativo, selecionar o primeiro
    if not active_project_id and all_projects:
        active_project_id = all_projects[0].get("id")
    
    return render_template(
        "home.html",
        # ... existing vars ...
        all_projects=all_projects,
        active_project_id=active_project_id,
    )
```

**Lógica:**
1. Carrega `all_projects` de cadastros
2. Tenta ler `active_project_id` de:
   - Env var `OMNIDECK_ACTIVE_PROJECT`
   - Arquivo `~/.omnideck_config.json`
3. Se nenhum ativo, usa o primeiro projeto
4. Passa ambos para template

### 4. Backend - Novo Endpoint (app.py)

Novo endpoint para persistir seleção:

```python
@app.route("/api/set-active-project", methods=["POST"])
def api_set_active_project():
    try:
        data = request.get_json() or {}
        project_id = data.get("project_id")
        
        if not project_id:
            return jsonify({"success": False, "message": "project_id é obrigatório"}), 400
        
        # Validar se projeto existe
        cadastros = _load_cadastros()
        projects = cadastros.get("projects", [])
        project_exists = any(p.get("id") == project_id for p in projects)
        
        if not project_exists:
            return jsonify({"success": False, "message": f"Projeto {project_id} não encontrado"}), 404
        
        # Salvar em ~/.omnideck_config.json
        config_file = Path.home() / ".omnideck_config.json"
        config = {}
        
        if config_file.exists():
            try:
                with open(config_file) as f:
                    config = json.load(f)
            except Exception:
                config = {}
        
        config["active_project_id"] = project_id
        
        with open(config_file, "w") as f:
            json.dump(config, f, indent=2)
        
        # Salvar em sessão
        session["active_project_id"] = project_id
        
        # Atualizar env var
        os.environ["OMNIDECK_ACTIVE_PROJECT"] = project_id
        
        return jsonify({
            "success": True,
            "message": f"Projeto {project_id} definido como ativo",
            "active_project_id": project_id
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Erro ao definir projeto ativo"
        }), 500
```

**Comportamento:**
1. Recebe `project_id` em POST JSON
2. Valida se projeto existe em cadastros
3. Persiste em 3 locais (para compatibilidade):
   - `~/.omnideck_config.json` (persistente entre execuções)
   - `session["active_project_id"]` (em tempo de execução)
   - `os.environ["OMNIDECK_ACTIVE_PROJECT"]` (env var)
4. Retorna sucesso/erro em JSON

## Fluxo Completo

1. **Navegação para home (/):**
   - Backend lê cadastros.json
   - Backend busca active_project_id (env var → config file → primeiro projeto)
   - Backend passa all_projects e active_project_id para template

2. **Usuário seleciona projeto no dropdown:**
   - HTML dispara `setActiveProject(projectId)`
   - JavaScript envia POST para `/api/set-active-project`
   - Backend valida e persiste seleção em 3 locais
   - JavaScript recarrega página

3. **Página recarregada:**
   - Backend lê novo active_project_id de config file
   - Dropdown mostra projeto selecionado
   - ProjectContext usa novo projeto ativo para todas as operações

## Persistência

**Arquivo de configuração:** `~/.omnideck_config.json`

```json
{
  "active_project_id": "proj_001"
}
```

**Precedência de leitura:**
1. Variável de ambiente `OMNIDECK_ACTIVE_PROJECT`
2. Campo em `~/.omnideck_config.json`
3. Primeiro projeto em cadastros (fallback)

## Compatibilidade com Fases Anteriores

- Usa `_load_cadastros()` existente (Fase 1)
- Usa `ProjectContext` para resolver caminhos (Fase 1)
- Integra com cadastros.html que cria novos projetos (Fase 1)
- Funciona com todos os scripts infra que usam ProjectContext (Fase 2)

## Testes Recomendados

1. Criar 2+ projetos em `/cadastros`
2. Acessar home page
3. Verificar dropdown com todos os projetos
4. Selecionar projeto diferente
5. Verificar se página recarrega
6. Voltar para home
7. Verificar se seleção anterior é mantida
8. Validar `~/.omnideck_config.json` foi criado/atualizado

## Próximas Fases

- **Fase 4:** Testar fluxo completo (criar projeto → selecionar → usar credenciais OTM)
- **Fase 5:** Documentar interface usuário e troubleshooting
