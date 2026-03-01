# Build HTML from JSON

Sistema de renderização HTML para visualização rápida do Documento de Migração.

## 📋 Descrição

O script `build_html_from_json.py` gera uma visualização HTML standalone do documento de migração, idêntica ao PDF mas otimizada para navegador. Isso permite:

- ✅ **Visualização rápida** - Sem necessidade de gerar PDF (processo mais lento)
- ✅ **Navegação interativa** - Links âncora para todas as seções
- ✅ **CSS inline** - Arquivo HTML standalone, funciona offline
- ✅ **Mesmo conteúdo do PDF** - Usa o mesmo template base e lógica de dados

## 🚀 Uso

### Gerar HTML

```bash
python tools/rendering/build_html_from_json.py
```

Ou execute direto:

```bash
./tools/rendering/build_html_from_json.py
```

### Saída

O arquivo será gerado em:
```
rendering/html/documento_migracao_standalone.html
```

Abra no navegador:
```bash
open rendering/html/documento_migracao_standalone.html
```

## 📁 Estrutura de Arquivos

```
rendering/html/
├── templates/
│   ├── html.css                              # CSS otimizado para navegador
│   └── documento_migracao_html_template.html.tpl  # Template Jinja2
├── documento_migracao.html                   # HTML gerado pelo painel (legado)
└── documento_migracao_standalone.html        # HTML standalone com CSS inline
```

## 🎨 CSS

O arquivo `html.css` é uma adaptação do `pdf.css`, com:

- **Removidas**: Regras `@page` específicas do WeasyPrint
- **Adicionadas**: Estilos de navegador (header fixo, navegação, cards)
- **Mantidas**: Todas as classes de layout, tabelas e tipografia
- **Print-ready**: Media queries para impressão mantém layout similar ao PDF

## 🔄 Diferenças vs PDF

| Aspecto | HTML | PDF |
|---------|------|-----|
| Velocidade | ⚡ Rápido (segundos) | 🐌 Lento (minutos) |
| Navegação | 🔗 Links interativos | 📄 Estático |
| Distribuição | 📧 Email/Web | 📎 Anexo formal |
| Tamanho | ~500KB | ~2-5MB |
| Engine | Navegador | WeasyPrint |

## 🛠️ Tecnologia

- **Jinja2**: Template engine (mesmo do PDF)
- **Python 3.9+**: Runtime
- **CSS3**: Estilos com flexbox/grid
- **HTML5**: Semântica moderna

## 📝 Manutenção

Para atualizar o layout:

1. **Template**: Edite `rendering/html/templates/documento_migracao_html_template.html.tpl`
2. **Estilos**: Edite `rendering/html/templates/html.css`
3. **Lógica**: Edite `tools/rendering/build_html_from_json.py`

Sincronize com o PDF quando necessário, mas mantenha adaptações específicas do navegador.

## 🐛 Troubleshooting

### Erro "Template not found"
```bash
# Verifique se o template existe
ls -la rendering/html/templates/documento_migracao_html_template.html.tpl
```

### Erro "JSON not found"
```bash
# Verifique se o JSON existe
ls -la domain/projeto_migracao/documento_migracao.json
```

### CSS não aplicado
O CSS é injetado inline automaticamente. Se não aparecer, verifique:
```bash
# Verifique se o CSS existe
ls -la rendering/html/templates/html.css
```

## 📚 Ver Também

- `build_pdf_from_json.py` - Geração de PDF
- `render_projeto_migracao.py` - Geração de Markdown
- `render_html_from_md.py` - HTML via Markdown (legado)
