# Gerador de Trabalhos Acadêmicos com IA

Este sistema utiliza Inteligência Artificial (Google Gemini API) para gerar trabalhos acadêmicos completos de forma automática, incluindo título, introdução, desenvolvimento, conclusão e referências bibliográficas reais.

## Funcionalidades

- Interface web amigável usando Streamlit
- Geração de trabalhos acadêmicos completos
- Personalização por nível acadêmico (Ensino Médio, Graduação, Pós-Graduação)
- Suporte a diferentes estilos de referência (APA, ABNT)
- Expansão e reescrita automática de seções
- Histórico de trabalhos gerados
- Exportação para PDF e JSON

## Requisitos

- Python 3.7 ou superior
- Bibliotecas Python (instaláveis via pip):
  - streamlit
  - google-generativeai
  - fpdf
  - uuid
  - base64
  - os
  - json
  - datetime

## Instalação

1. Clone ou baixe este repositório

2. Instale as dependências necessárias:

```bash
pip install streamlit google-generativeai fpdf
```

3. Configure sua chave de API do Google Gemini:
   - Obtenha uma chave de API em [Google AI Studio](https://ai.google.dev/)
   - Abra o arquivo `config.py` e substitua `SUA_CHAVE_API_AQUI` pela sua chave real

## Uso

1. Execute o aplicativo Streamlit:

```bash
streamlit run app.py
```

2. Acesse a interface web no navegador (geralmente em http://localhost:8501)

3. Preencha o formulário com:
   - Tema do trabalho acadêmico
   - Nível acadêmico
   - Estilo de referência

4. Clique em "Gerar Trabalho" e aguarde o processamento

5. Visualize, expanda ou reescreva as seções do trabalho gerado

6. Exporte o trabalho em PDF ou JSON conforme necessário

## Estrutura do Projeto

- `app.py`: Script principal com a interface Streamlit
- `utils.py`: Funções auxiliares para IA, histórico e exportação
- `config.py`: Configurações e chave de API
- `works/`: Pasta para armazenar os trabalhos gerados

## Limitações

- A qualidade do conteúdo gerado depende do modelo de IA utilizado
- É necessário revisar o conteúdo gerado para garantir precisão acadêmica
- A exportação para PDF pode ter limitações com caracteres especiais

## Aviso Legal

Este sistema é uma ferramenta educacional e de auxílio à pesquisa. O conteúdo gerado deve ser revisado, editado e apropriadamente citado pelo usuário. O uso do conteúdo gerado deve seguir as políticas de integridade acadêmica da instituição do usuário.

## Licença

Este projeto é disponibilizado para uso educacional e pessoal. Não é permitido o uso comercial sem autorização.