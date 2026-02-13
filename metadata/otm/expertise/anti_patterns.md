# Anti-patterns OTM

## ❌ Anti-pattern
JOIN SHIPMENT_STATUS sem filtrar STATUS_TYPE_GID
### Problema
Gera explosão de linhas e resultados inválidos.
### Forma correta
Sempre filtrar STATUS_TYPE_GID antes do join.

## ❌ Anti-pattern
SELECT * sem filtro de domínio
### Problema
Vazamento de dados entre domínios.
### Forma correta
Sempre filtrar DOMAIN_NAME.

## ❌ Anti-pattern
JOIN ORDER_RELEASE_LINE sem considerar sequência
### Problema
Resultados inconsistentes.
### Forma correta
Filtrar por LINE_SEQ_NUM.

## ❌ Anti-pattern
JOIN SHIPMENT_STOP sem considerar STOP_SEQ_NUM
### Problema
Resultados duplicados.
### Forma correta
Filtrar por STOP_SEQ_NUM.

## ❌ Anti-pattern
JOIN SHIPMENT_COST sem filtrar COST_TYPE_GID
### Problema
Resultados imprecisos.
### Forma correta
Filtrar por COST_TYPE_GID.

## ❌ Anti-pattern
JOIN LOCATION sem filtrar REGION_GID
### Problema
Resultados fora do escopo.
### Forma correta
Filtrar por REGION_GID.

## ❌ Anti-pattern
JOIN RATE_GEO_COST sem filtrar RATE_GEO_GID
### Problema
Resultados inválidos.
### Forma correta
Filtrar por RATE_GEO_GID.

## ❌ Anti-pattern
JOIN AGENT sem filtrar AGENT_TYPE_GID
### Problema
Resultados misturados.
### Forma correta
Filtrar por AGENT_TYPE_GID.

## ❌ Anti-pattern
JOIN INVOICE sem filtrar INVOICE_TYPE_GID
### Problema
Resultados imprecisos.
### Forma correta
Filtrar por INVOICE_TYPE_GID.

## ❌ Anti-pattern
JOIN ORDER_MOVEMENT sem filtrar MOVEMENT_SEQ_NUM
### Problema
Duplicidade de movimentos.
### Forma correta
Filtrar por MOVEMENT_SEQ_NUM.

## ❌ Anti-pattern
JOIN STATUS tables sem filtrar STATUS_TYPE_GID
### Problema
Resultados inválidos.
### Forma correta
Filtrar por STATUS_TYPE_GID.

## ❌ Anti-pattern
JOIN ADDRESS sem filtrar ADDRESS_TYPE_GID
### Problema
Resultados fora do escopo.
### Forma correta
Filtrar por ADDRESS_TYPE_GID.

## ❌ Anti-pattern
JOIN SHIPMENT_STATUS sem considerar DATA_SOURCE
### Problema
Resultados misturados.
### Forma correta
Filtrar por DATA_SOURCE.

## ❌ Anti-pattern
JOIN ORDER_RELEASE sem filtrar DOMAIN_NAME
### Problema
Vazamento de dados.
### Forma correta
Filtrar por DOMAIN_NAME.

## ❌ Anti-pattern
JOIN SHIPMENT sem filtrar DOMAIN_NAME
### Problema
Vazamento de dados.
### Forma correta
Filtrar por DOMAIN_NAME.
