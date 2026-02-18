<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ data.project.name or 'Projeto de Migração OTM' }} - Sistema MD → HTML → PDF</title>
    <link rel="stylesheet" href="../assets/style.css">
</head>
<body>
    <div class="page-container">
        <h1>{{ data.project.name or 'Projeto de Migração OTM' }}</h1>
        <p><strong>Código:</strong> {{ data.project.code }}</p>
        <p><strong>Versão:</strong> {{ data.project.version }}</p>
        <p><strong>Consultor:</strong> {{ data.project.consultant }}</p>
        <p><strong>Ambiente Origem:</strong> {{ data.project.environment.source }}</p>
        <p><strong>Ambiente Destino:</strong> {{ data.project.environment.target }}</p>

        {# Sumário dos grupos #}
        <h2>{{ data.project_metadata.groups_overview.title }}</h2>
        {% for paragraph in data.project_metadata.groups_overview.paragraphs %}
            <p>{{ paragraph }}</p>
        {% endfor %}
        <ul>
        {% for group in data.groups %}
            <li><a href="#group-{{ group.group_id|replace(' ', '-')|lower }}">{{ group.label }}</a></li>
        {% endfor %}
        </ul>

        {# Renderização dos grupos e objetos #}
        {% for group in data.groups %}
            <hr>
            <h2 id="group-{{ group.group_id|replace(' ', '-')|lower }}">{{ group.label }}</h2>
            {% for paragraph in group.description_paragraphs %}
                <p>{{ paragraph }}</p>
            {% endfor %}
            <ul>
            {% for obj in group.objects %}
                <li>
                    <strong>{{ obj.name }}</strong>
                    {% if obj.description %}<br>{{ obj.description }}{% endif %}
                    {% if obj.deployment_type %}<br><em>Deployment Type:</em> {{ obj.deployment_type }}{% endif %}
                    {% if obj.object_type %}<br><em>Object Type:</em> {{ obj.object_type }}{% endif %}
                    {% if obj.otm_table %}<br><em>OTM Table:</em> {{ obj.otm_table }}{% endif %}
                </li>
            {% endfor %}
            </ul>
        {% endfor %}
    </div>
</body>
</html>
