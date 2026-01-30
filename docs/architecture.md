# Arquitetura do OmniDeck

## Entidades de Domínio

### Projeto de Migração

#### Papel
O Projeto de Migração é a entidade orquestradora do OmniDeck.
Ele governa o escopo, os objetos, as regras e o estado de uma migração OTM,
servindo como fonte única para documentação e acompanhamento.

#### Boundary — O que pertence

Pertencem ao Projeto de Migração:

- Identidade do projeto (código, nome, versão, responsável, ambientes)
- Grupos de objetos de migração
- Objetos de migração e seus atributos
- Tipos de deploy aplicáveis
- Status por fase da migração
- Regras de obrigatoriedade e consistência
- Estado consolidado do projeto

#### Boundary — O que NÃO pertence

Não pertencem ao Projeto de Migração:

- HTML final
- PDF final
- Arquivos MD de renderização
- Cache técnico de objetos
- Scripts de extração ou parsing
- Lógica de UI
- Detalhes visuais ou de layout

Esses elementos são artefatos derivados ou infraestrutura.

#### Relação com outros domínios

- Consome Metadata OTM como referência (somente leitura)
- Gera documentos técnicos e relatórios como saída
- Não modifica metadata global
