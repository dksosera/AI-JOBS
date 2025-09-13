# Configurações para o sistema de geração de trabalhos acadêmicos

# Chave de API do Google Gemini
# A chave deve ser fornecida via variável de ambiente GEMINI_API_KEY (carregada do .env se existir)
import os
from dotenv import load_dotenv
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyCWWOb9ux3aSwodsBibz4vEYpFPCIlef84")

# Modelo da API Gemini a ser utilizado
GEMINI_MODEL = "gemini-2.5-flash"

# Configurações de temperatura para geração de conteúdo
# Valores mais baixos = respostas mais determinísticas
# Valores mais altos = respostas mais criativas
TEMPERATURE_DEFAULT = 0.7
TEMPERATURE_CREATIVE = 0.9

# Configurações para o histórico de trabalhos
HISTORY_FOLDER = "works"

# Configurações para exportação de PDF
PDF_MARGINS = (15, 15, 15)  # margens em milímetros (esquerda, topo, direita)
PDF_BOTTOM_MARGIN = 15  # margem inferior em milímetros
PDF_FONT_SIZE_TITLE = 16
PDF_FONT_SIZE_HEADING = 14
PDF_FONT_SIZE_SUBHEADING = 12
PDF_FONT_SIZE_TEXT = 11

# Estilos de referência suportados
REFERENCE_STYLES = ["APA", "ABNT"]

# Níveis acadêmicos suportados
ACADEMIC_LEVELS = ["Ensino Médio", "Graduação", "Pós-Graduação"]