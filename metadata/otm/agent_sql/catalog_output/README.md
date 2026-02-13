# OTM Knowledge Navigator – README

Esta pasta contém todos os arquivos de índice essenciais para navegação, consulta e automação com Oracle OTM.

## 📦 Localização
Todos os arquivos estão em:
metadata/otm/agent_sql/catalog_output/

## 🧠 Arquivos principais

1. **sql_rules.md**
   - Regras de governança SQL para OTM
   - Define padrões de joins, filtros obrigatórios, segurança e boas práticas

2. **agent_behavior.md**
   - Orienta o comportamento do agente (GPT)
   - Prioriza evidências do GitHub, disciplina técnica e rastreabilidade

3. **schema_catalog_eligible_tables.jsonl**
   - Catálogo completo das tabelas elegíveis
   - Inclui colunas, tipos, chaves, joins, contagem por domínio e caminho do JSON fonte

4. **otm_help_enriched_index.json**
   - Índice navegável da documentação oficial OTM
   - Tópicos, subtópicos, URLs, previews e métricas de conteúdo

## 🚀 Como usar

- Consulte o **schema_catalog_eligible_tables.jsonl** para navegar pelo banco, entender tabelas, gerar queries e relacionar entidades.
- Use o **otm_help_enriched_index.json** para buscar tópicos, explicações e caminhos de leitura na documentação oficial.
- Siga as regras e orientações de **sql_rules.md** e **agent_behavior.md** para garantir queries seguras e navegação disciplinada.

## 💡 Exemplos de perguntas que podem ser respondidas
- "Em qual tabela fica o custo do shipment?"
- "Como configurar Rate Offering?"
- "Gere uma query para listar shipments por domínio."
- "Quais tabelas possuem DOMAIN_NAME?"

## 🧭 Para IA e humanos
Este README serve como guia rápido para consultores, engenheiros, squads e para o próprio GPT, facilitando a integração e o uso dos índices.

---

Qualquer dúvida, consulte os arquivos desta pasta ou navegue pelo catálogo e índice de documentação.
