<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" />
  <title>{{ title }}</title>

  <style>
    body {
      font-family: Arial, sans-serif;
      line-height: 1.6;
      margin: 40px;
      max-width: 900px;
    }

    h1 {
      border-bottom: 2px solid #333;
      padding-bottom: 8px;
    }

    h2 {
      margin-top: 32px;
      color: #2c3e50;
    }

    h3 {
      margin-top: 24px;
      color: #34495e;
    }

    h4 {
      margin-top: 16px;
      color: #555;
    }

    ul {
      margin-left: 20px;
    }

    li {
      margin-bottom: 6px;
    }

    p {
      margin: 8px 0 12px 0;
    }
  </style>
</head>
<body>
  {{ content | safe }}
</body>
</html>
