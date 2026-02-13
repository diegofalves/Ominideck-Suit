# Query Patterns for Agent

## 1) Header + detail with guardrails

```sql
SELECT
  orh.ORDER_RELEASE_GID,
  orh.ORDER_RELEASE_XID,
  orl.ORDER_RELEASE_LINE_GID,
  orl.ITEM_GID,
  orl.PACKAGED_ITEM_GID
FROM GLOGOWNER.ORDER_RELEASE orh
JOIN GLOGOWNER.ORDER_RELEASE_LINE orl
  ON orh.ORDER_RELEASE_GID = orl.ORDER_RELEASE_GID
WHERE orh.INSERT_DATE >= DATE '2025-01-01'
FETCH FIRST 200 ROWS ONLY;
```

## 2) Shipment with stop sequence

```sql
SELECT
  s.SHIPMENT_GID,
  s.SHIPMENT_XID,
  ss.STOP_NUM,
  ss.LOCATION_GID,
  ss.ESTIMATED_ARRIVAL
FROM GLOGOWNER.SHIPMENT s
JOIN GLOGOWNER.SHIPMENT_STOP ss
  ON s.SHIPMENT_GID = ss.SHIPMENT_GID
WHERE s.SHIPMENT_GID = :shipment_gid
ORDER BY ss.STOP_NUM;
```

## 3) Count by domain profile

```sql
SELECT
  DOMAIN_NAME,
  COUNT(*) AS total_rows
FROM GLOGOWNER.AGENT
GROUP BY DOMAIN_NAME
ORDER BY total_rows DESC;
```

## Review checklist

- Are join keys explicit and correct?
- Is domain scope enforced?
- Is the row limit appropriate for exploration?
- Are assumptions documented?
