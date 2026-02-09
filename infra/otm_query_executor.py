#!/usr/bin/env python3
"""
Executor generico de queries OTM (SQL e Saved Query).

Fluxo principal:
1. Substitui variaveis no formato $VAR_NAME com valores de `context`.
2. Envia requisicao HTTP para endpoint OTM (DBServlet ou Saved Query).
3. Recebe XML e converte para dict Python normalizado.
4. Retorna resultado padronizado com status/payload/raw/error_message.
"""

import json
import re
import xml.etree.ElementTree as ET
from typing import Any, Dict, Optional

import requests
from requests.auth import HTTPBasicAuth


DEFAULT_TIMEOUT = 30
DEFAULT_SQL_PATH = "/GC3/glog.integration.servlet.DBServlet"
DEFAULT_SAVED_QUERY_PATH = "/GC3/glog.integration.servlet.SavedQueryServlet"
ALLOWED_EXECUTION_TYPES = {"SQL", "SAVED_QUERY"}
ALLOWED_OUTPUT_FORMATS = {"json", "md", "raw"}

# -------------------------------------------------
# Configuracao fixa do ambiente OTM (ajustar aqui)
# -------------------------------------------------
OTM_BASE_URL = "https://otmgtm-dev1-bauducco.otmgtm.us-phoenix-1.ocs.oraclecloud.com"
URL_SERVLET = f"{OTM_BASE_URL}/GC3/glog.integration.servlet.DBXMLServlet?command=xmlExport"
URL_DO_SERVICO_OTM = f"{OTM_BASE_URL}/GC3Services/TransmissionService/call"
OTM_USER = "BAU.TEST_INTEGRATION"
OTM_PASSWORD = "TestIntegracao@2025"
CREDENCIAIS = (OTM_USER, OTM_PASSWORD)
OTM_HTTP_METHOD = "POST"
OTM_VERIFY_SSL = True
OTM_TIMEOUT = DEFAULT_TIMEOUT
OTM_DEFAULT_HEADERS: Dict[str, str] = {"Accept": "application/xml"}
OTM_DEFAULT_REQUEST_PARAMS: Dict[str, Any] = {"format": "xml"}
OTM_SQL_PARAM_NAME = "sql"
OTM_SAVED_QUERY_PARAM_NAME = "savedQueryName"


class OTMQueryError(Exception):
    """Erro funcional esperado no fluxo de execucao OTM."""


def substitute_query_parameters(query_payload: str, context: Dict[str, Any]) -> str:
    """
    Substitui placeholders no formato $VAR_NAME usando valores de `context`.
    Lanca ValueError se algum placeholder nao tiver valor.
    """
    if not isinstance(query_payload, str) or not query_payload.strip():
        raise ValueError("query_payload deve ser uma string nao vazia.")
    if not isinstance(context, dict):
        raise ValueError("context deve ser um dicionario.")

    pattern = re.compile(r"\$([A-Za-z_][A-Za-z0-9_]*)")

    def replacer(match: re.Match) -> str:
        key = match.group(1)
        if key not in context:
            raise ValueError(f"Parametro ausente no context: ${key}")
        value = context[key]
        return "" if value is None else str(value)

    return pattern.sub(replacer, query_payload)


def _resolve_endpoint_url(execution_type: str, context: Dict[str, Any]) -> str:
    """Resolve URL de destino com base no tipo de execucao e contexto."""
    explicit_url = context.get("endpoint_url")
    if explicit_url:
        return str(explicit_url)

    if execution_type == "SQL" and context.get("dbservlet_url"):
        return str(context["dbservlet_url"])
    if execution_type == "SAVED_QUERY" and context.get("saved_query_url"):
        return str(context["saved_query_url"])

    if execution_type == "SQL":
        return URL_SERVLET

    base_url = OTM_BASE_URL.rstrip("/")
    if not base_url:
        raise ValueError("OTM_BASE_URL nao foi configurado em otm_query_executor.py.")

    return f"{base_url}{DEFAULT_SAVED_QUERY_PATH}"


def _resolve_auth(context: Dict[str, Any]) -> Optional[HTTPBasicAuth]:
    """
    Resolve autenticacao HTTP Basic a partir de:
    - context['auth'] = (username, password) ou [username, password]
    - context['username'] + context['password']
    """
    if "auth" in context and context["auth"] is not None:
        auth_value = context["auth"]
        if isinstance(auth_value, (tuple, list)) and len(auth_value) == 2:
            return HTTPBasicAuth(str(auth_value[0]), str(auth_value[1]))
        raise ValueError("`auth` deve ser tuple/list com (username, password).")

    default_user, default_password = CREDENCIAIS
    username = context.get("username", default_user)
    password = context.get("password", default_password)
    if username is None or password is None:
        raise ValueError(
            "Credenciais OTM ausentes. Configure OTM_USER/OTM_PASSWORD."
        )

    return HTTPBasicAuth(str(username), str(password))


def _build_request_params(
    execution_type: str, rendered_query_payload: str, context: Dict[str, Any]
) -> Dict[str, Any]:
    """Monta parametros da requisicao HTTP de acordo com o tipo de execucao."""
    base_params = dict(OTM_DEFAULT_REQUEST_PARAMS)
    context_params = context.get("request_params", {})
    if context_params is None:
        context_params = {}
    if not isinstance(context_params, dict):
        raise ValueError("`request_params` deve ser um dicionario.")
    base_params.update(context_params)
    params = dict(base_params)

    if execution_type == "SQL":
        sql_param_name = str(context.get("sql_param_name", OTM_SQL_PARAM_NAME))
        params[sql_param_name] = rendered_query_payload
    else:
        saved_query_param_name = str(
            context.get("saved_query_param_name", OTM_SAVED_QUERY_PARAM_NAME)
        )
        params[saved_query_param_name] = rendered_query_payload

    return params


def _send_otm_request(
    rendered_query_payload: str, execution_type: str, context: Dict[str, Any]
) -> str:
    """Envia requisicao HTTP para OTM e retorna XML bruto."""
    endpoint_url = _resolve_endpoint_url(execution_type, context)
    auth = _resolve_auth(context)

    headers = dict(OTM_DEFAULT_HEADERS)
    context_headers = context.get("headers", {})
    if context_headers is None:
        context_headers = {}
    if not isinstance(context_headers, dict):
        raise ValueError("`headers` deve ser um dicionario.")
    headers.update(context_headers)

    request_method = str(context.get("http_method", OTM_HTTP_METHOD)).upper()
    if request_method not in {"GET", "POST"}:
        raise ValueError("`http_method` deve ser GET ou POST.")

    timeout = float(context.get("timeout", OTM_TIMEOUT))
    verify_ssl = bool(context.get("verify_ssl", OTM_VERIFY_SSL))
    params = _build_request_params(execution_type, rendered_query_payload, context)

    try:
        if request_method == "GET":
            response = requests.get(
                endpoint_url,
                params=params,
                headers=headers,
                auth=auth,
                timeout=timeout,
                verify=verify_ssl,
            )
        else:
            response = requests.post(
                endpoint_url,
                data=params,
                headers=headers,
                auth=auth,
                timeout=timeout,
                verify=verify_ssl,
            )
        response.raise_for_status()
        return response.text
    except requests.RequestException as exc:
        raise OTMQueryError(f"Erro de conexao HTTP com OTM: {exc}") from exc


def _xml_element_to_dict(element: ET.Element) -> Any:
    """Converte recursivamente um Element XML em estrutura Python."""
    children = list(element)
    text = (element.text or "").strip()
    attributes = dict(element.attrib) if element.attrib else {}

    if not children:
        if attributes and text:
            return {"@attributes": attributes, "#text": text}
        if attributes:
            return {"@attributes": attributes}
        if text:
            return text
        return ""

    node_data: Dict[str, Any] = {}
    if attributes:
        node_data["@attributes"] = attributes
    if text:
        node_data["#text"] = text

    for child in children:
        child_data = _xml_element_to_dict(child)
        if child.tag in node_data:
            if not isinstance(node_data[child.tag], list):
                node_data[child.tag] = [node_data[child.tag]]
            node_data[child.tag].append(child_data)
        else:
            node_data[child.tag] = child_data

    return node_data


def parse_xml_to_dict(xml_raw: str) -> Dict[str, Any]:
    """Faz parse de XML bruto e retorna dict normalizado."""
    try:
        root = ET.fromstring(xml_raw)
    except ET.ParseError as exc:
        raise OTMQueryError(f"Erro ao parsear XML: {exc}") from exc

    return {root.tag: _xml_element_to_dict(root)}


def _to_markdown(payload: Dict[str, Any]) -> str:
    """Converte payload JSON para bloco Markdown."""
    pretty_json = json.dumps(payload, indent=2, ensure_ascii=False)
    return f"```json\n{pretty_json}\n```"


def _format_payload(
    payload_json: Dict[str, Any], raw_xml: str, output_format: str
) -> Any:
    """
    Ajusta forma do payload conforme output_format:
    - json: dict normalizado
    - md: dict com JSON normalizado e versao markdown
    - raw: dict com JSON normalizado e XML bruto
    """
    if output_format == "json":
        return payload_json
    if output_format == "md":
        return {"normalized": payload_json, "markdown": _to_markdown(payload_json)}
    if output_format == "raw":
        return {"normalized": payload_json, "raw_xml": raw_xml}
    raise ValueError(f"output_format invalido: {output_format}")


def execute_otm_query(
    query_payload: str,
    execution_type: str,
    context: Dict[str, Any],
    output_format: str,
) -> Dict[str, Any]:
    """
    Executa query OTM (SQL ou Saved Query) e retorna estrutura padronizada.

    Return:
    {
      "status": "success" | "error",
      "payload": Any,
      "raw": str | None,
      "error_message": str | None
    }
    """
    raw_xml: Optional[str] = None
    try:
        normalized_execution_type = str(execution_type).upper().strip()
        if normalized_execution_type not in ALLOWED_EXECUTION_TYPES:
            raise ValueError("execution_type deve ser 'SQL' ou 'SAVED_QUERY'.")

        normalized_output_format = str(output_format).lower().strip()
        if normalized_output_format not in ALLOWED_OUTPUT_FORMATS:
            raise ValueError("output_format deve ser 'json', 'md' ou 'raw'.")

        rendered_payload = substitute_query_parameters(query_payload, context)
        raw_xml = _send_otm_request(rendered_payload, normalized_execution_type, context)
        payload_json = parse_xml_to_dict(raw_xml)
        formatted_payload = _format_payload(payload_json, raw_xml, normalized_output_format)

        return {
            "status": "success",
            "payload": formatted_payload,
            "raw": raw_xml,
            "error_message": None,
        }
    except (ValueError, OTMQueryError) as exc:
        return {
            "status": "error",
            "payload": None,
            "raw": raw_xml,
            "error_message": str(exc),
        }
    except Exception as exc:  # fallback defensivo para erro inesperado
        return {
            "status": "error",
            "payload": None,
            "raw": raw_xml,
            "error_message": f"Erro inesperado: {exc}",
        }


if __name__ == "__main__":
    example_sql = """
    SELECT SHIPMENT_GID, INSERT_DATE
    FROM SHIPMENT
    WHERE DOMAIN_NAME = '$DOMAIN_NAME'
      AND INSERT_DATE >= TO_DATE('$DATE_FROM', 'YYYY-MM-DD')
    """

    example_ctx = {
        # Parametros usados no SQL
        "DOMAIN_NAME": "BAUDUCCO",
        "DATE_FROM": "2025-01-01",
        # Parametros de conexao estao fixos no topo do arquivo.
        # Se quiser sobrescrever pontualmente, inclua no context:
        # "endpoint_url", "username", "password", "timeout", etc.
    }

    result = execute_otm_query(example_sql, "SQL", example_ctx, "json")
    print(json.dumps(result, indent=2, ensure_ascii=False))
