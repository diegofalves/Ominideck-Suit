## Fonte da Verdade: JSON vs Markdown

O OmniDeck adota JSON canônico como fonte única da verdade.
Arquivos Markdown são artefatos derivados, utilizados exclusivamente
para documentação e renderização (HTML/PDF).

Usuários interagem com dados estruturados e textos livres via UI,
que alimenta o JSON do domínio. Nenhum arquivo Markdown base é editado
manualmente.


PDF rendering será feito exclusivamente via Playwright (Chromium).
WeasyPrint está oficialmente descartado no OmniDeck por fragilidade em ambientes ARM/macOS.

## Referências Operacionais

- Runbook de extrações OTM: `docs/otm_extraction_runbook.md`
