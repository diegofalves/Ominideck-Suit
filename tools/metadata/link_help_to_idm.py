import json
import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm
import unicodedata
from pathlib import Path

def normalize_column_name(name):
    # Convert to lowercase
    name = name.lower()
    # Remove accents
    name = ''.join(
        c for c in unicodedata.normalize('NFD', name)
        if unicodedata.category(c) != 'Mn'
    )
    # Remove spaces and special characters
    name = ''.join(c for c in name if c.isalnum())
    return name

def main():
    base_path = os.path.join('otm_builder', 'schema', 'base')
    help_path = os.path.join('otm_builder', 'help')
    convertido_path = os.path.join(help_path, 'convertido')
    os.makedirs(convertido_path, exist_ok=True)

    # 1. Ler planilha MoSCoW (específica do projeto)
    # Nota: esse arquivo é específico de cada projeto
    # Para Bauducco, procurar em: ~/OmniDeck/data/projects/bauducco/
    
    try:
        from ui.backend.project_context import get_active_project_context
        context = get_active_project_context()
        if context:
            project_data_root = context.project_data_root
        else:
            project_data_root = Path.cwd()
    except:
        project_data_root = Path.cwd()
    
    mosco_file = project_data_root / 'KPMG @ Bauducco_MoSCoW List.xlsx'
    if not mosco_file.exists():
        # Fallback para path antigo
        mosco_file = Path(base_path) / 'KPMG @ Bauducco_MoSCoW List.xlsx'
    
    df = pd.read_excel(mosco_file, engine='openpyxl', header=2)

    # Normalizar os nomes das colunas
    df.columns = [c.strip().upper().replace(" ", "_") for c in df.columns]

    # Mapa de colunas possíveis
    mapa_colunas = {
        "ID_MOSCOW": "IDM",
        "PROCESSO": "Processo",
        "PROCESSO_-_GRUPO": "Processo",
        "REQUISITO": "Requisito"
    }

    # Renomear para padrão interno
    df = df.rename(columns={orig: novo for orig, novo in mapa_colunas.items() if orig in df.columns})

    # Selecionar colunas principais
    colunas_necessarias = ["IDM", "Processo", "Requisito"]
    df = df[[c for c in colunas_necessarias if c in df.columns]]

    # Remover linhas sem valores relevantes
    df = df.dropna(subset=["IDM", "Requisito"])
    
    # Agrupar requisitos por IDM e concatenar as descrições para melhor contexto
    idm_reqs = df.groupby('IDM')['Requisito'].apply(lambda x: ' '.join(x)).to_dict()

    # 2. Ler índice help_index.json e conteúdo help_normalized.md
    help_index_file = os.path.join(help_path, 'index', 'help_index.json')
    help_md_file = os.path.join(help_path, 'convertido', 'help_normalized.md')

    with open(help_index_file, 'r', encoding='utf-8') as f:
        help_index = json.load(f)

    with open(help_md_file, 'r', encoding='utf-8') as f:
        help_md_content = f.read()

    # Extrair os textos dos tópicos do help
    topics = []
    if isinstance(help_index, list) and all(isinstance(t, dict) for t in help_index):
        # ✅ Estrutura moderna (com id, title, start, end)
        for topic in help_index:
            start = topic.get('start', 0)
            end = topic.get('end', len(help_md_content))
            text = help_md_content[start:end].strip()
            topics.append({
                'id': topic.get('id', ''),
                'title': topic.get('title', 'Sem título'),
                'text': text
            })
    else:
        # 🧩 Estrutura antiga ou simples (lista de títulos ou strings)
        for i, title in enumerate(help_index):
            topics.append({
                'id': f"topic_{i+1}",
                'title': str(title),
                'text': ''  # conteúdo vazio (modo degradado)
            })

    # Garantir que existam textos válidos
    help_texts = [t['text'].strip() for t in topics if t['text'].strip()]
    if not help_texts:
        print("⚠️ Nenhum texto válido encontrado nos tópicos do Help. Usando placeholders temporários...")
        help_texts = ["placeholder" for _ in topics]

    # Substituir textos vazios por placeholders
    for t in topics:
        if not t['text'].strip():
            t['text'] = "placeholder"

    vectorizer = TfidfVectorizer(stop_words='english')
    help_tfidf = vectorizer.fit_transform(help_texts)

    # 4. Para cada IDM, calcular similaridade e listar os 3 tópicos mais similares
    results = {}
    print('Calculando similaridades entre IDM requisitos e tópicos do help...')
    for idm, req_text in tqdm(idm_reqs.items(), total=len(idm_reqs)):
        req_vec = vectorizer.transform([req_text])
        sims = cosine_similarity(req_vec, help_tfidf).flatten()
        top_indices = sims.argsort()[-3:][::-1]
        top_topics = []
        for idx in top_indices:
            top_topics.append({
                'topic_id': topics[idx]['id'],
                'title': topics[idx]['title'],
                'similarity': float(sims[idx])
            })
        results[idm] = top_topics

    # 5. Salvar resultados
    output_file = os.path.join(convertido_path, 'idm_help_links.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # 6. Exibir resumo final
    print(f'\nResultados salvos em {output_file}')
    print(f'Total de IDM processados: {len(results)}')
    print('Exemplo de links para o primeiro IDM:')
    first_idm = next(iter(results))
    for link in results[first_idm]:
        print(f"  - [{link['title']}] (ID: {link['topic_id']}), Similaridade: {link['similarity']:.4f}")

if __name__ == '__main__':
    main()
