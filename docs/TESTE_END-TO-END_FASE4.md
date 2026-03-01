# Fase 4: Teste End-to-End (Guia Prático)

## 🎯 Objetivo
Validar o fluxo completo: criar projeto → selecionar → usar credenciais OTM

## 🚀 Pré-requisitos
- [ ] Aplicação Flask rodando em http://localhost:8088
- [ ] Arquivo `~/OmniDeck/data/consultoria/cadastros.json` criado (check se existe)
- [ ] Estrutura `~/OmniDeck/data/` criada

## ✅ Teste 1: Verificar Data Root

```bash
# Checar se arquivo de config global existe
cat ~/OmniDeck/data/consultoria/cadastros.json | head -20

# Esperado: JSON com estrutura { "consultorias": [], "projects": [...] }
```

---

## ✅ Teste 2: Criar Novo Projeto via UI

**Passos:**
1. Abrir navegador em http://localhost:8088/cadastros
2. Rolar até seção "Novo Projeto"
3. Preencher:
   - **Nome:** "Teste Fase 4"
   - **Descrição:** "Teste da separação framework/projeto"
4. Descer para "🔌 Configuração OTM"
5. Preencher credenciais (ou usar dados exemplo):
   - **OTM Source URL:** `http://localhost:8080`
   - **OTM Target URL:** `http://localhost:8080`
   - **Usuário:** `admin`
   - **Senha:** `admin123`
   - **Domain:** `TEST_DOMAIN`
   - **Versão:** `10.x`
6. Clicar "Salvar Projeto"

**Esperado:**
- ✅ Mensagem de sucesso
- ✅ Projeto aparece na lista acima
- ✅ Diretório `~/OmniDeck/data/projects/teste-fase-4/` criado

---

## ✅ Teste 3: Validar Estrutura Criada

```bash
# Checar diretório do projeto
ls -la ~/OmniDeck/data/projects/

# Esperado: 
# bauducco/ (do exemplo)
# teste-fase-4/ (novo projeto)

# Conteúdo do novo projeto
ls -la ~/OmniDeck/data/projects/teste-fase-4/

# Esperado:
# cache/
# migrations/
# documento_migracao.json (se migração começada)
```

---

## ✅ Teste 4: Verificar cadastros.json

```bash
# Ver conteúdo atualizado
cat ~/OmniDeck/data/consultoria/cadastros.json | python -m json.tool | grep -A 20 '"name": "Teste Fase 4"'

# Esperado: Projeto aparecer com otm_config preenchida
{
  "id": "proj_xxxx",
  "name": "Teste Fase 4",
  "otm_config": {
    "source_url": "http://localhost:8080",
    "target_url": "http://localhost:8080",
    "username": "admin",
    "password": "admin123",
    "domain_name": "TEST_DOMAIN",
    "version": "10.x"
  },
  "project_paths": {
    "data_root": "teste-fase-4"
  }
}
```

---

## ✅ Teste 5: Home Page - Dropdown de Projetos

**Passos:**
1. Navegar para home page: http://localhost:8088/
2. Olhar para header (topo da página)
3. Procurar seção "Projeto Ativo:"
4. Verificar dropdown com todos os projetos

**Esperado:**
- ✅ Dropdown visível com label "Projeto Ativo:"
- ✅ Mostra "Bauducco" (projeto exemplo) como primeira opção
- ✅ Mostra "Teste Fase 4" (novo projeto) como segunda opção
- ✅ Um projeto está marcado como `selected`

---

## ✅ Teste 6: Trocar Projeto no Dropdown

**Passos:**
1. Home page aberta
2. Clicar no dropdown "Projeto Ativo:"
3. Selecionar "Teste Fase 4"

**Esperado:**
- ✅ Página recarrega (possível flash breve)
- ✅ Dropdown volta com "Teste Fase 4" selecionado
- ✅ Arquivo `~/.omnideck_config.json` criado/atualizado

```bash
# Validar persistência
cat ~/.omnideck_config.json

# Esperado:
# {
#   "active_project_id": "proj_xxxx"
# }
```

---

## ✅ Teste 7: Selecionar Projeto Original

**Passos:**
1. No dropdown, selecionar "Bauducco" novamente

**Esperado:**
- ✅ Página recarrega
- ✅ Dropdown mostra "Bauducco" como ativo
- ✅ `~/.omnideck_config.json` atualizado para Bauducco

---

## ✅ Teste 8: ProjectContext Está Usando Novo Projeto

**Passos (em Terminal):**

```python
# Ativar venv e testar ProjectContext
cd "/Users/diegoalves/Documents/01 - Diego/02 - Trabalhos/05 - ITC/02 - Projetos/01 - Bauducco/04 - Desevolvimentos OTM/00 - Ominideck - Bauducco"

source .venv/bin/activate
python3 << 'EOF'

import os
from pathlib import Path

# Simular que "Teste Fase 4" está ativo
os.environ["OMNIDECK_ACTIVE_PROJECT"] = "proj_xxxx"  # ID real do seu projeto

from ui.backend.project_context import get_active_project_context

ctx = get_active_project_context()
print(f"Projeto Ativo: {ctx.project_name}")
print(f"OTM Source: {ctx.otm_source_url}")
print(f"OTM Domain: {ctx.otm_domain_name}")
print(f"Data Root: {ctx.project_data_root}")
print(f"Cache Path: {ctx.cache_path}")

EOF
```

**Esperado:**
```
Projeto Ativo: Teste Fase 4
OTM Source: http://localhost:8080
OTM Domain: TEST_DOMAIN
Data Root: /Users/.../OmniDeck/data/projects/teste-fase-4
Cache Path: /Users/.../OmniDeck/data/projects/teste-fase-4/cache
```

---

## ✅ Teste 9: Window Title Dinâmico (macOS)

**Se estiver rodando em PyWebView:**

```bash
# Compilar e rodar launcher
cd "/Users/diegoalves/Documents/01 - Diego/02 - Trabalhos/05 - ITC/02 - Projetos/01 - Bauducco/04 - Desevolvimentos OTM/00 - Ominideck - Bauducco"

# Ativar ambiente com Teste Fase 4
export OMNIDECK_ACTIVE_PROJECT="proj_xxxx"

# Rodar launcher (se tiver PyWebView instalado)
python omni_launcher.py
```

**Esperado:**
- ✅ Window title mostra "OmniDeck Suite - Teste Fase 4"
- ✅ Não é mais genérico "OmniDeck Suite"

---

## ✅ Teste 10: Reiniciar Aplicação

**Passos:**
1. Parar servidor Flask (Ctrl+C)
2. Esperar 2 segundos
3. Iniciar servidor novamente
4. Abrir http://localhost:8088

**Esperado:**
- ✅ Home page carrega
- ✅ Dropdown mostra o último projeto selecionado (de ~/.omnideck_config.json)
- ✅ ProjectContext usa credenciais do projeto persistido

---

## 🐛 Troubleshooting

### Dropdown não aparece
- [ ] Verificar se `all_projects` está sendo passado no template
- [ ] Checar console do browser (F12 → Console)
- [ ] Verificar se cadastros.json tem projetos listados

### Seleção não persiste
- [ ] Verificar permissões em home directory: `ls -la ~/ | grep omnideck`
- [ ] Tentar criar arquivo manualmente: `echo '{}' > ~/.omnideck_config.json`
- [ ] Verificar se POST endpoint retorna sucesso (F12 → Network)

### ProjectContext retorna valores antigos
- [ ] Verificar se env var `OMNIDECK_ACTIVE_PROJECT` foi atualizado
- [ ] Reiniciar a aplicação para limpar cache
- [ ] Checar se ~/.omnideck_config.json está sendo lido corretamente

### Diretório não criado
- [ ] Verificar se ~/OmniDeck/data/ existe: `ls -la ~/OmniDeck/`
- [ ] Criar manualmente: `mkdir -p ~/OmniDeck/data/projects/`
- [ ] Verificar permissões: `ls -la ~/OmniDeck/data/`

---

## 📊 Checklist Final

- [ ] Teste 1: Data root existe ✅
- [ ] Teste 2: Novo projeto criado ✅
- [ ] Teste 3: Estrutura de diretórios criada ✅
- [ ] Teste 4: cadastros.json atualizado ✅
- [ ] Teste 5: Dropdown aparece com todos os projetos ✅
- [ ] Teste 6: Trocar projeto funciona ✅
- [ ] Teste 7: Voltar para projeto original funciona ✅
- [ ] Teste 8: ProjectContext retorna credenciais corretas ✅
- [ ] Teste 9: Window title dinâmico (se macOS) ✅
- [ ] Teste 10: Persistência entre execuções ✅

**Se todos os testes passarem:** ✅ Fases 1-3 funcionando perfeitamente!

---

## 🚀 Próximas Fases

**Fase 4B:** Testar com OTM real
- [ ] Conectar a servidor OTM real
- [ ] Executar queries com credenciais do projeto
- [ ] Validar que cache isolado funciona

**Fase 5:** Documentação
- [ ] Atualizar README para multi-projeto
- [ ] Criar guia de "Adicionar novo projeto"
- [ ] Documentar troubleshooting

**Fase 6:** Production Ready
- [ ] Validação de credenciais OTM na criação
- [ ] Migração de projetos existentes
- [ ] Backup automático de credenciais (encrypted)
