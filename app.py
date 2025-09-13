import streamlit as st
import os
import base64
import json
from datetime import datetime
import config
import utils

# Configuração da página Streamlit
st.set_page_config(
    page_title="Gerador de Trabalhos Acadêmicos",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Função para criar um link de download
def get_download_link(file_path, link_text, file_format):
    with open(file_path, "rb") as file:
        contents = file.read()
    
    b64_contents = base64.b64encode(contents).decode()
    mime_type = "application/pdf" if file_format.lower() == "pdf" else "application/json"
    file_name = os.path.basename(file_path)
    
    href = f'<a href="data:{mime_type};base64,{b64_contents}" download="{file_name}">{link_text}</a>'
    return href

# Função para exibir o histórico de trabalhos
def show_history():
    st.header("Histórico de Trabalhos Gerados")
    
    history = utils.get_work_history()
    
    if not history:
        st.info("Nenhum trabalho encontrado no histórico.")
        return
    
    for i, work in enumerate(history):
        with st.expander(f"{work['titulo']} - {work['date_created']}"):
            st.write(f"**Tema:** {work['tema']}")
            st.write(f"**Nível Acadêmico:** {work['nivel_academico']}")
            st.write(f"**Estilo de Referência:** {work['estilo_referencia']}")
            
            # Botões para carregar e exportar
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"Carregar Trabalho", key=f"load_{i}"):
                    file_path = os.path.join(config.HISTORY_FOLDER, work['filename'])
                    st.session_state["current_work"] = utils.load_work_from_json(file_path)
                    st.session_state["page"] = "view"
                    st.rerun()
            
            with col2:
                if st.button(f"Exportar para PDF", key=f"export_{i}"):
                    file_path = os.path.join(config.HISTORY_FOLDER, work['filename'])
                    work_data = utils.load_work_from_json(file_path)
                    
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    pdf_filename = f"{config.HISTORY_FOLDER}/{timestamp}_{work['id']}.pdf"
                    
                    pdf_path = utils.export_to_pdf(work_data, pdf_filename)
                    st.markdown(get_download_link(pdf_path, "Baixar PDF", "pdf"), unsafe_allow_html=True)

# Função para exibir o formulário de geração de trabalho
def show_generation_form():
    st.header("Gerador de Trabalhos Acadêmicos")
    st.write("Preencha os campos abaixo para gerar um trabalho acadêmico completo.")
    
    with st.form("generation_form"):
        tema = st.text_area("Tema do Trabalho", placeholder="Ex: Impacto da Inteligência Artificial na Educação")
        
        col1, col2 = st.columns(2)
        with col1:
            nivel_academico = st.selectbox("Nível Acadêmico", config.ACADEMIC_LEVELS)
        
        with col2:
            estilo_referencia = st.selectbox("Estilo de Referência", config.REFERENCE_STYLES)
        
        submit_button = st.form_submit_button("Gerar Trabalho")
        
        if submit_button and tema:
            with st.spinner("Gerando trabalho acadêmico... Isso pode levar alguns minutos."):
                try:
                    # Gera o trabalho acadêmico
                    work_data = utils.generate_academic_work(tema, nivel_academico, estilo_referencia)
                    
                    # Armazena o trabalho na sessão
                    st.session_state["current_work"] = work_data
                    st.session_state["page"] = "view"
                    
                    st.success("Trabalho gerado com sucesso!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao gerar o trabalho: {str(e)}")
                    if "API key not available" in str(e):
                        st.warning("Verifique se você configurou a chave da API do Google Gemini no arquivo config.py.")
        elif submit_button:
            st.warning("Por favor, preencha o tema do trabalho.")

# Função para exibir o trabalho gerado
def show_work_view():
    if "current_work" not in st.session_state:
        st.warning("Nenhum trabalho carregado. Gere um novo trabalho ou carregue do histórico.")
        st.session_state["page"] = "generate"
        st.rerun()
        return
    
    work = st.session_state["current_work"]
    
    # Botões de navegação
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("« Voltar para Geração"):
            st.session_state["page"] = "generate"
            st.rerun()
    
    with col2:
        if st.button("« Voltar para Histórico"):
            st.session_state["page"] = "history"
            st.rerun()
    
    # Título e informações do trabalho
    st.title(work["titulo"])
    
    st.write(f"**Tema:** {work['tema']}")
    st.write(f"**Nível Acadêmico:** {work['nivel_academico']}")
    st.write(f"**Estilo de Referência:** {work['estilo_referencia']}")
    
    # Botões de exportação
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Exportar para PDF"):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            pdf_filename = f"{config.HISTORY_FOLDER}/{timestamp}_{work.get('id', 'novo')}.pdf"
            
            pdf_path = utils.export_to_pdf(work, pdf_filename)
            st.markdown(get_download_link(pdf_path, "Baixar PDF", "pdf"), unsafe_allow_html=True)
    
    with col2:
        if st.button("Exportar para JSON"):
            if "json_filename" in work:
                json_path = work["json_filename"]
                st.markdown(get_download_link(json_path, "Baixar JSON", "json"), unsafe_allow_html=True)
            else:
                # Se o trabalho não tiver um arquivo JSON associado, cria um novo
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                json_filename = f"{config.HISTORY_FOLDER}/{timestamp}_{work.get('id', 'novo')}.json"
                
                with open(json_filename, "w", encoding="utf-8") as f:
                    json.dump(work, f, ensure_ascii=False, indent=4)
                
                st.markdown(get_download_link(json_filename, "Baixar JSON", "json"), unsafe_allow_html=True)
    
    # Exibição das seções do trabalho
    st.header("Introdução")
    with st.expander("Ver Introdução", expanded=True):
        st.write(work["introducao"])
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Expandir Introdução"):
                with st.spinner("Expandindo introdução..."):
                    model = utils.setup_gemini_api()
                    work["introducao"] = utils.expand_section(model, work["introducao"], "Introdução", work["nivel_academico"])
                    st.session_state["current_work"] = work
                    st.rerun()
        with col2:
            if st.button("Reescrever Introdução"):
                with st.spinner("Reescrevendo introdução..."):
                    model = utils.setup_gemini_api()
                    work["introducao"] = utils.rewrite_section(model, work["introducao"], "Introdução", work["nivel_academico"])
                    st.session_state["current_work"] = work
                    st.rerun()
    
    st.header("Desenvolvimento")
    with st.expander("Ver Desenvolvimento", expanded=True):
        st.write(work["desenvolvimento"])
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Expandir Desenvolvimento"):
                with st.spinner("Expandindo desenvolvimento..."):
                    model = utils.setup_gemini_api()
                    work["desenvolvimento"] = utils.expand_section(model, work["desenvolvimento"], "Desenvolvimento", work["nivel_academico"])
                    st.session_state["current_work"] = work
                    st.rerun()
        with col2:
            if st.button("Reescrever Desenvolvimento"):
                with st.spinner("Reescrevendo desenvolvimento..."):
                    model = utils.setup_gemini_api()
                    work["desenvolvimento"] = utils.rewrite_section(model, work["desenvolvimento"], "Desenvolvimento", work["nivel_academico"])
                    st.session_state["current_work"] = work
                    st.rerun()
    
    st.header("Conclusão")
    with st.expander("Ver Conclusão", expanded=True):
        st.write(work["conclusao"])
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Expandir Conclusão"):
                with st.spinner("Expandindo conclusão..."):
                    model = utils.setup_gemini_api()
                    work["conclusao"] = utils.expand_section(model, work["conclusao"], "Conclusão", work["nivel_academico"])
                    st.session_state["current_work"] = work
                    st.rerun()
        with col2:
            if st.button("Reescrever Conclusão"):
                with st.spinner("Reescrevendo conclusão..."):
                    model = utils.setup_gemini_api()
                    work["conclusao"] = utils.rewrite_section(model, work["conclusao"], "Conclusão", work["nivel_academico"])
                    st.session_state["current_work"] = work
                    st.rerun()
    
    st.header("Referências")
    with st.expander("Ver Referências", expanded=True):
        st.write(work["referencias"])

# Função principal
def main():
    # Inicializa o estado da sessão se necessário
    if "page" not in st.session_state:
        st.session_state["page"] = "generate"
    
    # Barra lateral
    with st.sidebar:
        st.title("📚 Gerador de Trabalhos Acadêmicos")
        st.write("Crie trabalhos acadêmicos completos com IA")
        
        st.divider()
        
        # Navegação
        if st.button("Gerar Novo Trabalho"):
            st.session_state["page"] = "generate"
            st.rerun()
        
        if st.button("Ver Histórico"):
            st.session_state["page"] = "history"
            st.rerun()
        
        st.divider()
        
        # Informações
        st.write("### Sobre")
        st.write("Este sistema utiliza IA para gerar trabalhos acadêmicos completos.")
        st.write("Desenvolvido com Google Gemini API.")
        
        # Verificação da API key
        if config.GEMINI_API_KEY == "SUA_CHAVE_API_AQUI":
            st.warning("⚠️ Configure sua chave API no arquivo config.py")
    
    # Conteúdo principal
    if st.session_state["page"] == "generate":
        show_generation_form()
    elif st.session_state["page"] == "history":
        show_history()
    elif st.session_state["page"] == "view":
        show_work_view()

# Executa o aplicativo
if __name__ == "__main__":
    main()