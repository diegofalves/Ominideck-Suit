"""
Gerencia o contexto do projeto ativo e resolve credenciais OTM.

Permite que scripts e UI acessem configurações específicas do projeto
sem hardcoding de URLs, domínios ou credenciais.
"""
from pathlib import Path
import os
import json
from typing import Optional, Dict, Any


class ProjectContext:
    """Contexto do projeto ativo com credenciais OTM."""
    
    def __init__(self, project_id: str, cadastros_data: Dict[str, Any]):
        """
        Inicializa o contexto do projeto.
        
        Args:
            project_id: ID do projeto (ex: 'proj_001')
            cadastros_data: Dados carregados de cadastros.json
        
        Raises:
            ValueError: Se projeto não encontrado
        """
        self.project_id = project_id
        self._project_data = self._find_project(project_id, cadastros_data)
        
        if not self._project_data:
            raise ValueError(f"Projeto '{project_id}' não encontrado")
    
    def _find_project(self, project_id: str, cadastros: Dict) -> Optional[Dict]:
        """Encontra projeto por ID nos cadastros."""
        for proj in cadastros.get("projetos", []):
            if proj.get("id") == project_id:
                return proj
        return None
    
    @property
    def otm_source_url(self) -> str:
        """URL do ambiente source (DEV)."""
        return self._resolve_env_var(
            self._project_data.get("otm_config", {}).get("source_url", "")
        )
    
    @property
    def otm_target_url(self) -> str:
        """URL do ambiente target (PROD)."""
        return self._resolve_env_var(
            self._project_data.get("otm_config", {}).get("target_url", "")
        )
    
    @property
    def otm_username(self) -> str:
        """Usuário OTM."""
        return self._resolve_env_var(
            self._project_data.get("otm_config", {}).get("username", "")
        )
    
    @property
    def otm_password(self) -> str:
        """Senha OTM."""
        return self._resolve_env_var(
            self._project_data.get("otm_config", {}).get("password", "")
        )
    
    @property
    def otm_domain_name(self) -> str:
        """Nome do domínio OTM."""
        return self._project_data.get("otm_config", {}).get("domain_name", "")
    
    @property
    def otm_version(self) -> str:
        """Versão OTM."""
        return self._project_data.get("otm_config", {}).get("version", "25c")
    
    @property
    def project_data_root(self) -> Path:
        """Path raiz dos dados do projeto."""
        data_root = Path(os.getenv("OMNIDECK_DATA_PATH", "~/OmniDeck/data")).expanduser()
        relative_path = self._project_data.get("project_paths", {}).get("data_root", "")
        return data_root / relative_path
    
    @property
    def domain_path(self) -> Path:
        """Path do domínio do projeto."""
        return self.project_data_root / "domain"
    
    @property
    def metadata_path(self) -> Path:
        """Path dos metadados do projeto."""
        return self.project_data_root / "metadata"
    
    @property
    def otm_metadata_path(self) -> Path:
        """Path dos metadados OTM do projeto."""
        return self.metadata_path / "otm"
    
    @property
    def cache_path(self) -> Path:
        """Path do cache OTM do projeto."""
        return self.otm_metadata_path / "cache"
    
    @property
    def reports_path(self) -> Path:
        """Path dos relatórios gerados."""
        return self.project_data_root / "rendering" / "reports"
    
    @property
    def migration_document_path(self) -> Path:
        """Path do documento de migração do projeto."""
        return self.domain_path / "projeto_migracao" / "documento_migracao.json"
    
    def _resolve_env_var(self, value: str) -> str:
        """Resolve variáveis de ambiente no formato ${VAR_NAME}."""
        if not isinstance(value, str):
            return str(value)
        
        if value.startswith("${") and value.endswith("}"):
            var_name = value[2:-1]
            return os.getenv(var_name, "")
        return value
    
    def get_otm_connection_params(self) -> Dict[str, str]:
        """Retorna dicionário com parâmetros de conexão OTM."""
        return {
            "base_url": self.otm_source_url,
            "username": self.otm_username,
            "password": self.otm_password,
            "domain_name": self.otm_domain_name,
            "version": self.otm_version,
        }
    
    def ensure_directories_exist(self) -> None:
        """Cria diretórios do projeto se não existirem."""
        self.domain_path.mkdir(parents=True, exist_ok=True)
        self.metadata_path.mkdir(parents=True, exist_ok=True)
        self.cache_path.mkdir(parents=True, exist_ok=True)
        self.cache_path.joinpath("objects").mkdir(parents=True, exist_ok=True)
        self.cache_path.joinpath("translations").mkdir(parents=True, exist_ok=True)
        self.reports_path.mkdir(parents=True, exist_ok=True)


def get_active_project_context() -> Optional[ProjectContext]:
    """
    Retorna o contexto do projeto ativo.
    
    Ordem de resolução:
    1. Variável de ambiente OMNIDECK_ACTIVE_PROJECT
    2. Arquivo ~/.omnideck_config.json (último projeto usado)
    3. None (modo setup)
    
    Returns:
        ProjectContext ou None se nenhum projeto ativo
    """
    from ui.backend.app import _load_cadastros
    
    # 1. Tentar variável de ambiente
    project_id = os.getenv("OMNIDECK_ACTIVE_PROJECT")
    
    # 2. Tentar arquivo de config
    if not project_id:
        config_file = Path.home() / ".omnideck_config.json"
        if config_file.exists():
            try:
                config = json.loads(config_file.read_text())
                project_id = config.get("active_project_id")
            except Exception:
                pass
    
    # 3. Não encontrou, retorna None
    if not project_id:
        return None
    
    # Carrega cadastros e cria contexto
    try:
        cadastros = _load_cadastros()
        return ProjectContext(project_id, cadastros)
    except ValueError:
        # Projeto inválido, retorna None
        return None


def require_active_project(func):
    """
    Decorator que requer um projeto ativo para executar função.
    
    Levanta ValueError se não houver projeto ativo.
    """
    def wrapper(*args, **kwargs):
        context = get_active_project_context()
        if not context:
            raise ValueError(
                "Nenhum projeto ativo. Defina OMNIDECK_ACTIVE_PROJECT ou selecione na UI."
            )
        return func(*args, _project_context=context, **kwargs)
    return wrapper
