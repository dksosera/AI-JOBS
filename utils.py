import os
import json
import uuid
import datetime
import google.generativeai as genai
from fpdf import FPDF
import config

# Função utilitária para sanitizar texto quando uma fonte Unicode não estiver disponível
def _sanitize_for_latin1(s):
    if s is None:
        return ''
    if not isinstance(s, str):
        s = str(s)
    replacements = {
        '\u2013': '-',  # en dash
        '\u2014': '-',  # em dash
        '\u2015': '-',  # horizontal bar
        '\u2012': '-',  # figure dash
        '\u2018': "'",  # left single quote
        '\u2019': "'",  # right single quote
        '\u201c': '"',  # left double quote
        '\u201d': '"',  # right double quote
        '\u2026': '...', # ellipsis
        '\u00a0': ' ',   # non-breaking space
        '\u200b': '',    # zero-width space
    }
    for k, v in replacements.items():
        s = s.replace(k, v)
    try:
        s.encode('latin-1')
        return s
    except UnicodeEncodeError:
        return s.encode('latin-1', 'ignore').decode('latin-1')

# Configuração da API do Google Gemini
def setup_gemini_api():
    """
    Configura a API do Google Gemini com a chave fornecida no arquivo config.py
    """
    if not config.GEMINI_API_KEY or config.GEMINI_API_KEY == "SUA_CHAVE_API_AQUI":
        raise ValueError("API key not available")
    genai.configure(api_key=config.GEMINI_API_KEY)
    return genai.GenerativeModel(config.GEMINI_MODEL)

# Funções para geração de conteúdo acadêmico
def generate_title(model, tema, nivel_academico):
    """
    Gera um título sugestivo para o trabalho acadêmico
    
    Args:
        model: Modelo Gemini configurado
        tema: Tema do trabalho acadêmico
        nivel_academico: Nível acadêmico (Ensino Médio, Graduação, Pós-Graduação)
        
    Returns:
        String contendo o título gerado
    """
    prompt = f"""
    Crie um título acadêmico atrativo e profissional para um trabalho de {nivel_academico} sobre o tema: "{tema}".
    O título deve ser claro, conciso e refletir o conteúdo acadêmico esperado.
    Retorne apenas o título, sem aspas ou formatação adicional.
    """
    
    response = model.generate_content(prompt)
    return response.text.strip()

def generate_introduction(model, tema, nivel_academico, titulo):
    """
    Gera a introdução do trabalho acadêmico
    
    Args:
        model: Modelo Gemini configurado
        tema: Tema do trabalho acadêmico
        nivel_academico: Nível acadêmico (Ensino Médio, Graduação, Pós-Graduação)
        titulo: Título gerado para o trabalho
        
    Returns:
        String contendo a introdução gerada
    """
    prompt = f"""
    Escreva uma introdução acadêmica para um trabalho de {nivel_academico} com o título "{titulo}" sobre o tema "{tema}".
    
    A introdução deve:
    1. Contextualizar o tema e sua relevância acadêmica
    2. Apresentar brevemente o problema ou questão a ser abordada
    3. Indicar o objetivo do trabalho
    4. Mencionar brevemente a metodologia ou abordagem utilizada
    5. Apresentar a estrutura do trabalho
    
    A introdução deve ter entre 3 e 5 parágrafos, dependendo do nível acadêmico, sendo mais elaborada para níveis mais avançados.
    Use linguagem formal e acadêmica apropriada para o nível especificado.
    """
    
    response = model.generate_content(prompt)
    return response.text.strip()

def generate_development(model, tema, nivel_academico, titulo, introducao, estilo_referencia):
    """
    Gera o desenvolvimento do trabalho acadêmico
    
    Args:
        model: Modelo Gemini configurado
        tema: Tema do trabalho acadêmico
        nivel_academico: Nível acadêmico (Ensino Médio, Graduação, Pós-Graduação)
        titulo: Título gerado para o trabalho
        introducao: Introdução gerada para o trabalho
        estilo_referencia: Estilo de referência (APA ou ABNT)
        
    Returns:
        String contendo o desenvolvimento gerado
    """
    prompt = f"""
    Escreva o desenvolvimento completo para um trabalho acadêmico de {nivel_academico} com o título "{titulo}" sobre o tema "{tema}".
    
    Considere a seguinte introdução para manter a coerência:
    """
    prompt += f"""
    {introducao}
    """
    prompt += f"""
    
    O desenvolvimento deve:
    1. Ser dividido em seções com subtítulos claros e relevantes
    2. Apresentar uma revisão teórica sobre o tema
    3. Discutir diferentes perspectivas e abordagens sobre o assunto
    4. Incluir pelo menos 5 citações de autores relevantes no formato {estilo_referencia}
    5. Ter profundidade adequada ao nível acadêmico ({nivel_academico})
    6. Apresentar argumentos bem fundamentados e análise crítica
    
    Para nível de Ensino Médio: 3-4 seções com parágrafos mais simples e diretos
    Para nível de Graduação: 4-5 seções com análise mais aprofundada
    Para nível de Pós-Graduação: 5-6 seções com análise crítica e teórica mais sofisticada
    
    Use linguagem formal e acadêmica apropriada para o nível especificado.
    Inclua citações no formato {estilo_referencia} ao longo do texto.
    """
    
    response = model.generate_content(prompt)
    return response.text.strip()

def generate_conclusion(model, tema, nivel_academico, titulo, desenvolvimento):
    """
    Gera a conclusão do trabalho acadêmico
    
    Args:
        model: Modelo Gemini configurado
        tema: Tema do trabalho acadêmico
        nivel_academico: Nível acadêmico (Ensino Médio, Graduação, Pós-Graduação)
        titulo: Título gerado para o trabalho
        desenvolvimento: Desenvolvimento gerado para o trabalho
        
    Returns:
        String contendo a conclusão gerada
    """
    # Extraímos apenas os primeiros 1000 caracteres do desenvolvimento para não sobrecarregar o prompt
    desenvolvimento_resumido = desenvolvimento[:1000] + "..." if len(desenvolvimento) > 1000 else desenvolvimento
    
    prompt = f"""
    Escreva uma conclusão acadêmica para um trabalho de {nivel_academico} com o título "{titulo}" sobre o tema "{tema}".
    
    Considere o seguinte início do desenvolvimento para manter a coerência:
    """
    prompt += f"""
    {desenvolvimento_resumido}
    """
    prompt += f"""
    
    A conclusão deve:
    1. Retomar brevemente os principais pontos discutidos no trabalho
    2. Apresentar as conclusões obtidas a partir da análise realizada
    3. Destacar a relevância e implicações dos resultados
    4. Sugerir possíveis desdobramentos ou pesquisas futuras
    
    A conclusão deve ter entre 2 e 4 parágrafos, dependendo do nível acadêmico, sendo mais elaborada para níveis mais avançados.
    Use linguagem formal e acadêmica apropriada para o nível especificado.
    Não introduza novas informações ou citações na conclusão.
    """
    
    response = model.generate_content(prompt)
    return response.text.strip()

def generate_references(model, tema, nivel_academico, desenvolvimento, estilo_referencia):
    """
    Gera as referências bibliográficas do trabalho acadêmico
    
    Args:
        model: Modelo Gemini configurado
        tema: Tema do trabalho acadêmico
        nivel_academico: Nível acadêmico (Ensino Médio, Graduação, Pós-Graduação)
        desenvolvimento: Desenvolvimento gerado para o trabalho
        estilo_referencia: Estilo de referência (APA ou ABNT)
        
    Returns:
        String contendo as referências geradas
    """
    # Extraímos apenas os primeiros 2000 caracteres do desenvolvimento para não sobrecarregar o prompt
    desenvolvimento_resumido = desenvolvimento[:2000] + "..." if len(desenvolvimento) > 2000 else desenvolvimento
    
    prompt = f"""
    Crie uma lista de referências bibliográficas reais e relevantes para um trabalho acadêmico de {nivel_academico} sobre o tema "{tema}".
    
    Considere o seguinte desenvolvimento do trabalho para identificar autores e obras citadas:
    """
    prompt += f"""
    {desenvolvimento_resumido}
    """
    prompt += f"""
    
    As referências devem:
    1. Seguir rigorosamente o formato {estilo_referencia}
    2. Incluir todas as obras citadas no desenvolvimento
    3. Adicionar outras referências relevantes para complementar (total entre 8-15 referências)
    4. Ser organizadas em ordem alfabética
    5. Incluir apenas obras reais e verificáveis (livros, artigos, sites acadêmicos)
    6. Ter diversidade de tipos de fontes (livros, artigos, sites, etc.)
    
    Para nível de Ensino Médio: 8-10 referências mais acessíveis
    Para nível de Graduação: 10-12 referências mais específicas
    Para nível de Pós-Graduação: 12-15 referências incluindo artigos científicos recentes
    
    Formate as referências estritamente de acordo com o padrão {estilo_referencia}.
    """
    
    response = model.generate_content(prompt)
    return response.text.strip()

def expand_section(model, section_content, section_name, nivel_academico):
    """
    Expande uma seção específica do trabalho acadêmico
    
    Args:
        model: Modelo Gemini configurado
        section_content: Conteúdo atual da seção
        section_name: Nome da seção (Introdução, Desenvolvimento, Conclusão)
        nivel_academico: Nível acadêmico (Ensino Médio, Graduação, Pós-Graduação)
        
    Returns:
        String contendo a seção expandida
    """
    prompt = f"""
    Expanda e enriqueça a seguinte seção de {section_name} de um trabalho acadêmico de {nivel_academico}:
    
    {section_content}
    
    A expansão deve:
    1. Manter a coerência com o conteúdo original
    2. Adicionar mais detalhes, exemplos e explicações
    3. Aprofundar a análise e argumentação
    4. Manter o estilo e tom acadêmico apropriado para o nível {nivel_academico}
    5. Aumentar em aproximadamente 50% o tamanho do texto original
    
    Retorne a versão expandida completa da seção, não apenas os trechos adicionados.
    """
    
    response = model.generate_content(prompt)
    return response.text.strip()

def rewrite_section(model, section_content, section_name, nivel_academico):
    """
    Reescreve uma seção específica do trabalho acadêmico
    
    Args:
        model: Modelo Gemini configurado
        section_content: Conteúdo atual da seção
        section_name: Nome da seção (Introdução, Desenvolvimento, Conclusão)
        nivel_academico: Nível acadêmico (Ensino Médio, Graduação, Pós-Graduação)
        
    Returns:
        String contendo a seção reescrita
    """
    prompt = f"""
    Reescreva a seguinte seção de {section_name} de um trabalho acadêmico de {nivel_academico}, mantendo as mesmas ideias principais mas com uma abordagem e estrutura diferentes:
    
    {section_content}
    
    A reescrita deve:
    1. Manter as mesmas ideias e argumentos principais
    2. Usar uma estrutura de parágrafos diferente
    3. Utilizar sinônimos e construções frasais alternativas
    4. Manter o nível de formalidade e adequação acadêmica para o nível {nivel_academico}
    5. Ter aproximadamente o mesmo tamanho do texto original
    
    Retorne a versão reescrita completa da seção.
    """
    
    response = model.generate_content(prompt)
    return response.text.strip()

# Funções para gerenciamento de histórico e arquivos
def save_work_to_json(work_data):
    """
    Salva o trabalho gerado em um arquivo JSON
    
    Args:
        work_data: Dicionário contendo os dados do trabalho
        
    Returns:
        String contendo o caminho do arquivo JSON salvo
    """
    # Cria a pasta de histórico se não existir
    os.makedirs(config.HISTORY_FOLDER, exist_ok=True)
    
    # Gera um ID único para o arquivo
    work_id = str(uuid.uuid4())
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{config.HISTORY_FOLDER}/{timestamp}_{work_id}.json"
    
    # Adiciona metadados ao trabalho
    work_data["id"] = work_id
    work_data["timestamp"] = timestamp
    work_data["date_created"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Salva o arquivo JSON
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(work_data, f, ensure_ascii=False, indent=4)
    
    return filename

def load_work_from_json(filename):
    """
    Carrega um trabalho salvo a partir de um arquivo JSON
    
    Args:
        filename: Caminho do arquivo JSON
        
    Returns:
        Dicionário contendo os dados do trabalho
    """
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)

def get_work_history():
    """
    Obtém o histórico de trabalhos salvos
    
    Returns:
        Lista de dicionários contendo metadados dos trabalhos salvos
    """
    # Cria a pasta de histórico se não existir
    os.makedirs(config.HISTORY_FOLDER, exist_ok=True)
    
    history = []
    for filename in os.listdir(config.HISTORY_FOLDER):
        if filename.endswith(".json"):
            filepath = os.path.join(config.HISTORY_FOLDER, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    work_data = json.load(f)
                    history.append({
                        "id": work_data.get("id", ""),
                        "titulo": work_data.get("titulo", ""),
                        "tema": work_data.get("tema", ""),
                        "nivel_academico": work_data.get("nivel_academico", ""),
                        "estilo_referencia": work_data.get("estilo_referencia", ""),
                        "date_created": work_data.get("date_created", ""),
                        "filename": filename
                    })
            except Exception as e:
                print(f"Erro ao carregar arquivo {filename}: {e}")
    
    # Ordena por data de criação (mais recente primeiro)
    history.sort(key=lambda x: x.get("date_created", ""), reverse=True)
    return history

# Funções para exportação
def export_to_pdf(work_data, output_filename=None):
    """
    Exporta o trabalho para um arquivo PDF
    
    Args:
        work_data: Dicionário contendo os dados do trabalho
        output_filename: Nome do arquivo de saída (opcional)
        
    Returns:
        String contendo o caminho do arquivo PDF gerado
    """
    if output_filename is None:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"{config.HISTORY_FOLDER}/{timestamp}_{work_data.get('id', str(uuid.uuid4()))}.pdf"
    
    # Cria a pasta de histórico se não existir
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)
    
    # Configuração do PDF
    pdf = FPDF()
    # Margens e quebra automática de página
    pdf.set_margins(*config.PDF_MARGINS)
    try:
        pdf.set_auto_page_break(auto=True, margin=config.PDF_BOTTOM_MARGIN)
    except Exception:
        pass
    pdf.add_page()
    
    # Fonte com suporte a Unicode, se disponível
    font_path_candidates = [
        os.path.join('fonts', 'DejaVuSansCondensed.ttf'),
        'DejaVuSansCondensed.ttf',
    ]
    font_loaded = False
    for fp in font_path_candidates:
        if os.path.exists(fp):
            try:
                pdf.add_font('DejaVu', '', fp, uni=True)
                font_loaded = True
                break
            except Exception:
                pass
    font_family = 'DejaVu' if font_loaded else 'Arial'
    pdf.set_font(font_family, '', config.PDF_FONT_SIZE_TEXT)
    
    def _safe_text(t):
        return t if font_loaded else _sanitize_for_latin1(t)
    
    # Título
    pdf.set_font(font_family, '', config.PDF_FONT_SIZE_TITLE)
    pdf.multi_cell(0, 10, _safe_text(work_data.get("titulo", "")), 0, 'C')
    pdf.ln(10)
    
    # Informações do trabalho
    pdf.set_font(font_family, '', config.PDF_FONT_SIZE_TEXT)
    pdf.cell(0, 10, _safe_text(f"Tema: {work_data.get('tema', '')}"), 0, 1)
    pdf.cell(0, 10, _safe_text(f"Nível Acadêmico: {work_data.get('nivel_academico', '')}"), 0, 1)
    pdf.cell(0, 10, _safe_text(f"Estilo de Referência: {work_data.get('estilo_referencia', '')}"), 0, 1)
    pdf.cell(0, 10, _safe_text(f"Data de Criação: {work_data.get('date_created', '')}"), 0, 1)
    pdf.ln(10)
    
    # Introdução
    pdf.set_font(font_family, '', config.PDF_FONT_SIZE_HEADING)
    pdf.cell(0, 10, "INTRODUÇÃO", 0, 1, 'L')
    pdf.ln(5)
    pdf.set_font(font_family, '', config.PDF_FONT_SIZE_TEXT)
    pdf.multi_cell(0, 10, _safe_text(work_data.get("introducao", "")), 0, 'J')
    pdf.ln(10)
    
    # Desenvolvimento
    pdf.set_font(font_family, '', config.PDF_FONT_SIZE_HEADING)
    pdf.cell(0, 10, "DESENVOLVIMENTO", 0, 1, 'L')
    pdf.ln(5)
    pdf.set_font(font_family, '', config.PDF_FONT_SIZE_TEXT)
    
    # Dividimos o desenvolvimento em parágrafos para melhor formatação
    desenvolvimento = work_data.get("desenvolvimento", "")
    paragrafos = desenvolvimento.split('\n\n')
    for paragrafo in paragrafos:
        # Verifica se o parágrafo é um subtítulo (assumindo que subtítulos não terminam com ponto)
        if not paragrafo.strip().endswith('.') and len(paragrafo.strip()) < 100:
            pdf.set_font(font_family, '', config.PDF_FONT_SIZE_SUBHEADING)
            pdf.ln(5)
            pdf.multi_cell(0, 10, _safe_text(paragrafo), 0, 'L')
            pdf.set_font(font_family, '', config.PDF_FONT_SIZE_TEXT)
        else:
            pdf.multi_cell(0, 10, _safe_text(paragrafo), 0, 'J')
            pdf.ln(5)
    
    pdf.ln(10)
    
    # Conclusão
    pdf.set_font(font_family, '', config.PDF_FONT_SIZE_HEADING)
    pdf.cell(0, 10, "CONCLUSÃO", 0, 1, 'L')
    pdf.ln(5)
    pdf.set_font(font_family, '', config.PDF_FONT_SIZE_TEXT)
    pdf.multi_cell(0, 10, _safe_text(work_data.get("conclusao", "")), 0, 'J')
    pdf.ln(10)
    
    # Referências
    pdf.set_font(font_family, '', config.PDF_FONT_SIZE_HEADING)
    pdf.cell(0, 10, "REFERÊNCIAS", 0, 1, 'L')
    pdf.ln(5)
    pdf.set_font(font_family, '', config.PDF_FONT_SIZE_TEXT)
    
    # Dividimos as referências em linhas para melhor formatação
    referencias = work_data.get("referencias", "")
    linhas_ref = referencias.split('\n')
    for linha in linhas_ref:
        if linha.strip():
            pdf.multi_cell(0, 10, _safe_text(linha), 0, 'L')
    
    # Salva o PDF
    try:
        pdf.output(output_filename)
        return output_filename
    except Exception as e:
        # Fallback para caso de erro com caracteres especiais
        print(f"Erro ao gerar PDF: {e}")
        # Tenta novamente sem a fonte personalizada
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, "Erro ao gerar PDF com caracteres especiais. Verifique o arquivo JSON.", 0, 1)
        os.makedirs(config.HISTORY_FOLDER, exist_ok=True)
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        fallback_filename = f"{config.HISTORY_FOLDER}/error_{ts}.pdf"
        pdf.output(fallback_filename)
        return fallback_filename

# Função principal para gerar trabalho completo
def generate_academic_work(tema, nivel_academico, estilo_referencia):
    """
    Gera um trabalho acadêmico completo
    
    Args:
        tema: Tema do trabalho acadêmico
        nivel_academico: Nível acadêmico (Ensino Médio, Graduação, Pós-Graduação)
        estilo_referencia: Estilo de referência (APA ou ABNT)
        
    Returns:
        Dicionário contendo todas as seções do trabalho gerado
    """
    # Configura o modelo Gemini
    model = setup_gemini_api()
    
    # Gera o título
    titulo = generate_title(model, tema, nivel_academico)
    
    # Gera a introdução
    introducao = generate_introduction(model, tema, nivel_academico, titulo)
    
    # Gera o desenvolvimento
    desenvolvimento = generate_development(model, tema, nivel_academico, titulo, introducao, estilo_referencia)
    
    # Gera a conclusão
    conclusao = generate_conclusion(model, tema, nivel_academico, titulo, desenvolvimento)
    
    # Gera as referências
    referencias = generate_references(model, tema, nivel_academico, desenvolvimento, estilo_referencia)
    
    # Cria o dicionário com o trabalho completo
    work_data = {
        "tema": tema,
        "nivel_academico": nivel_academico,
        "estilo_referencia": estilo_referencia,
        "titulo": titulo,
        "introducao": introducao,
        "desenvolvimento": desenvolvimento,
        "conclusao": conclusao,
        "referencias": referencias
    }
    
    # Salva o trabalho no histórico
    json_filename = save_work_to_json(work_data)
    work_data["json_filename"] = json_filename
    
    return work_data