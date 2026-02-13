# Oracle OTM SQL Rules (Agent Pack v2)

## Join Style
- ALWAYS use implicit joins
- NEVER use explicit JOIN syntax

Correct:
SELECT a.col1,
       b.col2
  FROM table_a a,
       table_b b
 WHERE a.id = b.id

Forbidden:
SELECT * FROM table_a a JOIN table_b b ON a.id = b.id

## Safety Rules
- SELECT * is forbidden
- Always prefer bind variables (:domain, :gid, :xid)
- Always filter by DOMAIN_NAME when applicable
- Limit exploratory queries with FETCH FIRST 200 ROWS ONLY