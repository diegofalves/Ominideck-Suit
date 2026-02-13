# Agent Design Patterns OTM

## Padrão: Trigger por Evento
- Use agents para disparar ações automáticas em eventos críticos.
- Sempre valide o tipo de evento e domínio.

## Padrão: Sequenciamento de Agents
- Organize agents em sequência lógica para evitar conflitos.
- Use AGENT_SEQ_NUM para controle.

## Padrão: Validação de Dados
- Agents devem validar dados antes de executar ações.
- Evite triggers sem validação de domínio.

## Padrão: Troubleshooting Automation
- Crie agents read-only para diagnóstico.
- Evite alterações em massa sem validação.

## Padrão: Evitar Duplicidade
- Sempre filtre por DOMAIN_NAME e AGENT_TYPE_GID.
- Evite triggers múltiplos para o mesmo evento.

## Erros comuns em automações
- Falta de validação de domínio
- Sequenciamento incorreto de agents
- Triggers sem controle de tipo
- Alterações em massa sem filtro
- Falta de troubleshooting
