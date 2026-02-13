# Query Patterns OTM

## 1. Listar shipments por status
**Quando usar:** Consultar shipments filtrando por status específico.
**Query exemplo:**
SELECT s.SHIPMENT_GID, ss.STATUS_TYPE_GID, ss.STATUS_VALUE_GID
FROM SHIPMENT s, SHIPMENT_STATUS ss
WHERE s.SHIPMENT_GID = ss.SHIPMENT_GID
  AND ss.STATUS_TYPE_GID = 'PLANNED'
**Riscos evitados:** Explosão de linhas por falta de filtro.

## 2. Validar existência sem duplicidade (EXISTS)
**Quando usar:** Garantir que um registro existe sem gerar duplicidade.
**Query exemplo:**
SELECT s.SHIPMENT_GID
FROM SHIPMENT s
WHERE EXISTS (
  SELECT 1 FROM SHIPMENT_STATUS ss
  WHERE ss.SHIPMENT_GID = s.SHIPMENT_GID
    AND ss.STATUS_TYPE_GID = 'PLANNED'
)
**Riscos evitados:** Duplicidade por joins desnecessários.

## 3. Query segura multi-domain
**Quando usar:** Consultar dados de múltiplos domínios.
**Query exemplo:**
SELECT s.SHIPMENT_GID, s.DOMAIN_NAME
FROM SHIPMENT s
WHERE s.DOMAIN_NAME = :domain
**Riscos evitados:** Vazamento de dados entre domínios.

## 4. Últimos registros com limite seguro
**Quando usar:** Buscar últimos registros sem sobrecarregar o sistema.
**Query exemplo:**
SELECT s.SHIPMENT_GID
FROM SHIPMENT s
ORDER BY s.SHIPMENT_GID DESC
FETCH FIRST 200 ROWS ONLY
**Riscos evitados:** Queries pesadas e lentas.

## 5. Query de troubleshooting (read-only)
**Quando usar:** Diagnóstico de problemas sem alterar dados.
**Query exemplo:**
SELECT * FROM SHIPMENT s WHERE s.DOMAIN_NAME = :domain
**Riscos evitados:** Alteração acidental de dados.

## 6. Query para validação de agents
**Quando usar:** Validar se um agent está corretamente configurado.
**Query exemplo:**
SELECT a.AGENT_GID, a.AGENT_TYPE_GID
FROM AGENT a
WHERE a.DOMAIN_NAME = :domain
**Riscos evitados:** Falta de validação de domínio.
