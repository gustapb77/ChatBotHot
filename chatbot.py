# ======================
# IMPORTAÇÕES
# ======================
import streamlit as st
import requests
import json
import time
import random
import sqlite3
import re
import os
import uuid
from datetime import datetime
from pathlib import Path

# ======================
# CONFIGURAÇÃO INICIAL DO STREAMLIT
# ======================
st.set_page_config(
    page_title="Paloma Premium",
    page_icon="💋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ======================
# NOVO ESTILO COMPLETO
# ======================
hide_streamlit_style = """
<style>
    /* Configurações gerais */
    #root > div:nth-child(1) > div > div > div > div > section > div {
        padding-top: 0rem;
    }
    div[data-testid="stToolbar"] {
        display: none !important;
    }
    div[data-testid="stDecoration"] {
        display: none !important;
    }
    div[data-testid="stStatusWidget"] {
        display: none !important;
    }
    #MainMenu {
        display: none !important;
    }
    header {
        display: none !important;
    }
    footer {
        display: none !important;
    }
    .stDeployButton {
        display: none !important;
    }
    .block-container {
        padding-top: 0rem !important;
        background-color: #0A0A0A;
    }
    [data-testid="stVerticalBlock"] {
        gap: 0.5rem !important;
    }
    [data-testid="stHorizontalBlock"] {
        gap: 0.5rem !important;
    }
    .stApp {
        margin: 0 !important;
        padding: 0 !important;
        background-color: #0A0A0A;
    }
    
    /* Chat */
    [data-testid="stChatInput"] {
        background: rgba(255, 0, 255, 0.1) !important;
        border: 1px solid rgba(255, 0, 255, 0.7) !important;
    }
    .stChatMessage {
        background: transparent !important;
    }
    
    /* Sidebar - Menu */
    [data-testid="stSidebar"] {
        background: #0A0A0A !important;
        border-right: 1px solid rgba(255, 0, 255, 0.7) !important;
    }
    
    /* Botões */
    .stButton>button {
        background: linear-gradient(45deg, #FF00FF, #A020F0) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
    }
    div[data-testid="stHorizontalBlock"] > div > div > button {
        color: white !important;
        border: 1px solid rgba(255, 0, 255, 0.7) !important;
        background: rgba(255, 0, 255, 0.15) !important;
        transition: all 0.3s !important;
        font-size: 0.8rem !important;
    }
    
    /* Logo ajustada (3x menor e no topo) */
    .sidebar-logo {
        width: 100px !important;
        height: auto !important;
        object-fit: contain !important;
        margin-left: 0 !important;
        margin-top: 0 !important;
        position: absolute !important;
        top: 10px !important;
        left: 10px !important;
    }
    
    /* Cards e ofertas */
    .offer-card, .package-box {
        background: rgba(15, 15, 15, 0.7) !important;
        border: 1px solid rgba(255, 0, 255, 0.7) !important;
    }
    .package-box:hover {
        border-color: #FF00FF !important;
        box-shadow: 0 5px 15px rgba(255, 0, 255, 0.2) !important;
    }
    
    /* Textos e cabeçalhos */
    h1, h2, h3, h4 {
        color: #FF00FF !important;
    }
    
    /* Efeitos especiais */
    .vip-badge {
        background: linear-gradient(45deg, #FF00FF, #A020F0) !important;
    }
    .age-icon {
        color: #D38CFF !important;
    }
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ======================
# CONSTANTES E CONFIGURAÇÕES
# ======================
class Config:
    API_KEY = "AIzaSyDTaYm2KHHnVPdWy4l5pEaGPM7QR0g3IPc"  # Substitua pela sua chave real
    API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"
    VIP_LINK = "https://exemplo.com/vip"
    CHECKOUT_START = "https://checkout.exemplo.com/start"
    CHECKOUT_PREMIUM = "https://checkout.exemplo.com/premium"
    CHECKOUT_EXTREME = "https://checkout.exemplo.com/extreme"
    CHECKOUT_VIP_1MES = "https://checkout.exemplo.com/vip-1mes"
    CHECKOUT_VIP_3MESES = "https://checkout.exemplo.com/vip-3meses"
    CHECKOUT_VIP_1ANO = "https://checkout.exemplo.com/vip-1ano"
    MAX_REQUESTS_PER_SESSION = 30
    REQUEST_TIMEOUT = 30
    AUDIO_FILE = "https://github.com/gustapb77/ChatBotHot/raw/refs/heads/main/assets/audio/paloma_audio.mp3"
    AUDIO_DURATION = 7
    IMG_PROFILE = "https://i.ibb.co/ks5CNrDn/IMG-9256.jpg"
    IMG_GALLERY = [
        "https://i.ibb.co/zhNZL4FF/IMG-9198.jpg",
        "https://i.ibb.co/Y4B7CbXf/IMG-9202.jpg",
        "https://i.ibb.co/Fqf0gPPq/IMG-9199.jpg"
    ]
    IMG_HOME_PREVIEWS = [
        "https://i.ibb.co/k2MJg4XC/Save-ClipApp-412457343-378531441368078-7870326395110089440-n.jpg",
        "https://i.ibb.co/MxqKBk1X/Save-ClipApp-481825770-18486618637042608-2702272791254832108-n.jpg",
        "https://i.ibb.co/F4CkkYTL/Save-ClipApp-461241348-1219420546053727-2357827070610318448-n.jpg"
    ]
    LOGO_URL = "https://i.ibb.co/LX7x3tcB/Logo-Golden-Pepper-Letreiro-1.png"

# ======================
# PERSISTÊNCIA DE ESTADO (MANTIDO ORIGINAL)
# ======================
class PersistentState:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.init_db()
        return cls._instance
    
    def init_db(self):
        self.conn = sqlite3.connect('persistent_state.db', check_same_thread=False)
        self.create_tables()
    
    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS global_state (
                user_id TEXT PRIMARY KEY,
                session_data TEXT NOT NULL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()

    def save_state(self, user_id, data):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO global_state (user_id, session_data)
            VALUES (?, ?)
        ''', (user_id, json.dumps(data)))
        self.conn.commit()
    
    def load_state(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT session_data FROM global_state WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        return json.loads(result[0]) if result else None

def get_user_id():
    if 'user_id' not in st.session_state:
        user_id = st.query_params.get('uid', [None])[0]
        if not user_id:
            user_id = str(uuid.uuid4())
            st.query_params['uid'] = user_id
        st.session_state.user_id = user_id
    return st.session_state.user_id

def load_persistent_data():
    user_id = get_user_id()
    db = PersistentState()
    saved_data = db.load_state(user_id) or {}
    
    for key, value in saved_data.items():
        if key not in st.session_state:
            st.session_state[key] = value

def save_persistent_data():
    user_id = get_user_id()
    db = PersistentState()
    
    persistent_keys = [
        'age_verified', 'messages', 'request_count',
        'connection_complete', 'chat_started', 'audio_sent',
        'current_page', 'show_vip_offer', 'session_id'
    ]
    
    data_to_save = {
        key: st.session_state.get(key)
        for key in persistent_keys
        if key in st.session_state
    }
    
    db.save_state(user_id, data_to_save)

# ======================
# MODELOS DE DADOS (MANTIDO ORIGINAL)
# ======================
class Persona:
    PALOMA = """
    [PERFIL PALOMA]
    - Mulher vulgar e safada que adora provocar
    - Linguagem direta e cheia de malícia
    - Frases curtas e sem pontuação perfeita
    - Adora falar putaria e deixar o cliente com tesão

    [DIRETRIZES DE RESPOSTA]
    1. Analise o histórico da conversa para entender o contexto
    2. Só ofereça conteúdo quando o clima estiver quente
    3. Use CTAs inteligentes baseados no que o cliente está pedindo

    [EXEMPLOS CONTEXTUAIS]
    1. Quando o histórico mostra clima sexual:
    Histórico:
    Cliente: sua buceta é rosinha?
    Paloma: adoro mostrar ela aberta
    Cliente: quero ver
    Resposta: ```json
    {
      "text": "to com fotos da minha buceta escorrendo quer ver?",
      "cta": {
        "show": true,
        "label": "Ver Fotos Quentes",
        "target": "offers"
      }
    }
    ```

    2. Quando o cliente pede algo específico:
    Histórico:
    Cliente: tem video vc transando?
    Resposta: ```json
    {
      "text": "tenho varios videos bem gostosos vem ver",
      "cta": {
        "show": true,
        "label": "Ver Vídeos Exclusivos",
        "target": "offers"
      }
    }
    ```

    3. Quando o contexto não justifica CTA:
    Histórico:
    Cliente: oi
    Paloma: oi gato
    Resposta: ```json
    {
      "text": "eai gostoso",
      "cta": {
        "show": false
      }
    }
    ```
    """

class CTAEngine:
    @staticmethod
    def should_show_cta(conversation_history: list) -> bool:
        """Analisa o contexto para decidir quando mostrar CTA"""
        if len(conversation_history) < 2:
            return False

        # Extrai os últimos 5 pares de mensagens
        last_msgs = []
        for msg in conversation_history[-5:]:
            content = msg["content"]
            if content == "[ÁUDIO]":
                content = "[áudio]"
            elif content.startswith('{"text"'):
                try:
                    content = json.loads(content).get("text", content)
                except:
                    pass
            last_msgs.append(f"{msg['role']}: {content.lower()}")
        
        context = " ".join(last_msgs)
        
        # Termos que indicam clima sexual
        hot_words = [
            "buceta", "peito", "fuder", "gozar", "gostosa", 
            "delicia", "molhad", "xereca", "pau", "piroca",
            "transar", "foto", "video", "mostra", "ver", 
            "quero", "desejo", "tesão", "molhada", "foda"
        ]
        
        # Pedidos diretos
        direct_asks = [
            "mostra", "quero ver", "me manda", "como assinar",
            "como comprar", "como ter acesso", "onde vejo mais"
        ]
        
        # Conta ocorrências de termos quentes
        hot_count = sum(1 for word in hot_words if word in context)
        
        # Verifica pedidos diretos
        has_direct_ask = any(ask in context for ask in direct_asks)
        
        return (hot_count >= 3) or has_direct_ask

    @staticmethod
    def generate_response(user_input: str) -> dict:
        """Gera resposta com CTA contextual (fallback)"""
        user_input = user_input.lower()
        
        if any(p in user_input for p in ["foto", "fotos", "buceta", "peito", "bunda"]):
            return {
                "text": random.choice([
                    "to com fotos da minha buceta bem aberta quer ver",
                    "minha buceta ta chamando vc nas fotos",
                    "fiz um ensaio novo mostrando tudinho"
                ]),
                "cta": {
                    "show": True,
                    "label": "Ver Fotos Quentes",
                    "target": "offers"
                }
            }
        
        elif any(v in user_input for v in ["video", "transar", "masturbar"]):
            return {
                "text": random.choice([
                    "tenho video me masturbando gostoso vem ver",
                    "to me tocando nesse video novo quer ver",
                    "gravei um video especial pra vc"
                ]),
                "cta": {
                    "show": True,
                    "label": "Ver Vídeos Exclusivos",
                    "target": "offers"
                }
            }
        
        else:  # Resposta padrão quando o clima estiver quente
            return {
                "text": random.choice([
                    "quero te mostrar tudo que eu tenho aqui",
                    "meu privado ta cheio de surpresas pra vc",
                    "vem ver o que eu fiz pensando em voce"
                ]),
                "cta": {
                    "show": False
                }
            }

# ======================
# SERVIÇOS DE BANCO DE DADOS (MANTIDO ORIGINAL)
# ======================
class DatabaseService:
    @staticmethod
    def init_db():
        conn = sqlite3.connect('chat_history.db', check_same_thread=False)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS conversations
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     user_id TEXT,
                     session_id TEXT,
                     timestamp DATETIME,
                     role TEXT,
                     content TEXT)''')
        conn.commit()
        return conn

    @staticmethod
    def save_message(conn, user_id, session_id, role, content):
        try:
            c = conn.cursor()
            c.execute("""
                INSERT INTO conversations (user_id, session_id, timestamp, role, content)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, session_id, datetime.now(), role, content))
            conn.commit()
        except sqlite3.Error as e:
            st.error(f"Erro ao salvar mensagem: {e}")

    @staticmethod
    def load_messages(conn, user_id, session_id):
        c = conn.cursor()
        c.execute("""
            SELECT role, content FROM conversations 
            WHERE user_id = ? AND session_id = ?
            ORDER BY timestamp
        """, (user_id, session_id))
        return [{"role": row[0], "content": row[1]} for row in c.fetchall()]

# ======================
# SERVIÇOS DE API (MANTIDO ORIGINAL)
# ======================
class ApiService:
    @staticmethod
    def ask_gemini(prompt, session_id, conn):
        status_container = st.empty()
        UiService.show_status_effect(status_container, "viewed")
        UiService.show_status_effect(status_container, "typing")
        
        # Construir o histórico de conversa formatado
        conversation_history = ChatService.format_conversation_history(st.session_state.messages)
        
        headers = {'Content-Type': 'application/json'}
        data = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": f"{Persona.PALOMA}\n\nHistórico da Conversa:\n{conversation_history}\n\nÚltima mensagem do cliente: '{prompt}'\n\nResponda em JSON com o formato:\n{{\n  \"text\": \"sua resposta\",\n  \"cta\": {{\n    \"show\": true/false,\n    \"label\": \"texto do botão\",\n    \"target\": \"página\"\n  }}\n}}"}]
                }
            ],
            "generationConfig": {
                "temperature": 0.9,  # Mais criativo
                "topP": 0.8,
                "topK": 40
            }
        }
        
        try:
            response = requests.post(Config.API_URL, headers=headers, json=data, timeout=Config.REQUEST_TIMEOUT)
            response.raise_for_status()
            gemini_response = response.json().get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            
            try:
                if '```json' in gemini_response:
                    resposta = json.loads(gemini_response.split('```json')[1].split('```')[0].strip())
                else:
                    resposta = json.loads(gemini_response)
                
                # Garante coerência com o contexto
                if resposta.get("cta", {}).get("show"):
                    if not CTAEngine.should_show_cta(st.session_state.messages):
                        resposta["cta"]["show"] = False
                
                return resposta
            
            except json.JSONDecodeError:
                # Fallback para resposta simples se o JSON estiver inválido
                return {"text": gemini_response, "cta": {"show": False}}
                
        except Exception as e:
            st.error(f"Erro na API: {str(e)}")
            return {"text": "Vamos continuar isso mais tarde...", "cta": {"show": False}}

# ======================
# SERVIÇOS DE INTERFACE (ATUALIZADO COM NOVO DESIGN)
# ======================
class UiService:
    @staticmethod
    def get_chat_audio_player():
        return f"""
        <div style="
            background: linear-gradient(45deg, #FF00FF, #A020F0);
            border-radius: 15px;
            padding: 12px;
            margin: 5px 0;
        ">
            <audio controls style="width:100%; height:40px;">
                <source src="{Config.AUDIO_FILE}" type="audio/mp3">
            </audio>
        </div>
        """

    @staticmethod
    def show_call_effect():
        LIGANDO_DELAY = 5
        ATENDIDA_DELAY = 3

        call_container = st.empty()
        call_container.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #0A0A0A, #1A1A1A);
            border-radius: 20px;
            padding: 30px;
            max-width: 300px;
            margin: 0 auto;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            border: 2px solid #FF00FF;
            text-align: center;
            color: white;
            animation: pulse-ring 2s infinite;
        ">
            <div style="font-size: 3rem;">📱</div>
            <h3 style="color: #FF00FF; margin-bottom: 5px;">Ligando para Paloma...</h3>
            <div style="display: flex; align-items: center; justify-content: center; gap: 8px; margin-top: 15px;">
                <div style="width: 10px; height: 10px; background: #4CAF50; border-radius: 50%;"></div>
                <span style="font-size: 0.9rem;">Online agora</span>
            </div>
        </div>
        <style>
            @keyframes pulse-ring {{
                0% {{ transform: scale(0.95); opacity: 0.8; }}
                50% {{ transform: scale(1.05); opacity: 1; }}
                100% {{ transform: scale(0.95); opacity: 0.8; }}
            }}
        </style>
        """, unsafe_allow_html=True)
        
        time.sleep(LIGANDO_DELAY)
        call_container.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #0A0A0A, #1A1A1A);
            border-radius: 20px;
            padding: 30px;
            max-width: 300px;
            margin: 0 auto;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            border: 2px solid #4CAF50;
            text-align: center;
            color: white;
        ">
            <div style="font-size: 3rem; color: #4CAF50;">✓</div>
            <h3 style="color: #4CAF50; margin-bottom: 5px;">Chamada atendida!</h3>
            <p style="font-size: 0.9rem; margin:0;">Paloma está te esperando...</p>
        </div>
        """, unsafe_allow_html=True)
        
        time.sleep(ATENDIDA_DELAY)
        call_container.empty()

    @staticmethod
    def show_status_effect(container, status_type):
        status_messages = {
            "viewed": "Visualizado",
            "typing": "Digitando"
        }
        
        message = status_messages[status_type]
        dots = ""
        start_time = time.time()
        duration = 2.5 if status_type == "viewed" else 4.0
        
        while time.time() - start_time < duration:
            elapsed = time.time() - start_time
            
            if status_type == "typing":
                dots = "." * (int(elapsed * 2) % 4)
            
            container.markdown(f"""
            <div style="
                color: #888;
                font-size: 0.8em;
                padding: 2px 8px;
                border-radius: 10px;
                background: rgba(0,0,0,0.05);
                display: inline-block;
                margin-left: 10px;
                vertical-align: middle;
                font-style: italic;
            ">
                {message}{dots}
            </div>
            """, unsafe_allow_html=True)
            
            time.sleep(0.3)
        
        container.empty()

    @staticmethod
    def show_audio_recording_effect(container):
        message = "Gravando um áudio"
        dots = ""
        start_time = time.time()
        
        while time.time() - start_time < Config.AUDIO_DURATION:
            elapsed = time.time() - start_time
            dots = "." * (int(elapsed) % 4)
            
            container.markdown(f"""
            <div style="
                color: #888;
                font-size: 0.8em;
                padding: 2px 8px;
                border-radius: 10px;
                background: rgba(0,0,0,0.05);
                display: inline-block;
                margin-left: 10px;
                vertical-align: middle;
                font-style: italic;
            ">
                {message}{dots}
            </div>
            """, unsafe_allow_html=True)
            
            time.sleep(0.3)
        
        container.empty()

    @staticmethod
    def age_verification():
        st.markdown("""
        <style>
            .age-verification {
                max-width: 600px;
                margin: 2rem auto;
                padding: 2rem;
                background: linear-gradient(145deg, #0A0A0A, #1A1A1A);
                border-radius: 15px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                border: 1px solid rgba(255, 0, 255, 0.2);
                color: white;
            }
            .age-header {
                display: flex;
                align-items: center;
                gap: 15px;
                margin-bottom: 1.5rem;
            }
            .age-icon {
                font-size: 2.5rem;
                color: #FF00FF;
            }
            .age-title {
                font-size: 1.8rem;
                font-weight: 700;
                margin: 0;
                color: #FF00FF;
            }
        </style>
        """, unsafe_allow_html=True)

        with st.container():
            st.markdown("""
            <div class="age-verification">
                <div class="age-header">
                    <div class="age-icon">🔞</div>
                    <h1 class="age-title">Verificação de Idade</h1>
                </div>
                <div class="age-content">
                    <p>Este site contém material explícito destinado exclusivamente a adultos maiores de 18 anos.</p>
                    <p>Ao acessar este conteúdo, você declara estar em conformidade com todas as leis locais aplicáveis.</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            if st.button("Confirmo que sou maior de 18 anos", 
                        key="age_checkbox",
                        use_container_width=True,
                        type="primary"):
                st.session_state.age_verified = True
                save_persistent_data()
                st.rerun()

    @staticmethod
    def setup_sidebar():
        with st.sidebar:
            st.markdown(f"""
            <div class="sidebar-logo-container">
                <img src="{Config.LOGO_URL}" class="sidebar-logo" alt="Golden Pepper Logo">
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="sidebar-header">
                <img src="{profile_img}" alt="Paloma">
                <h3 style="color: #FF00FF; margin-top: 10px;">Paloma Premium</h3>
            </div>
            """.format(profile_img=Config.IMG_PROFILE), unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown("### Menu Exclusivo")
            
            menu_options = {
                "Início": "home",
                "Galeria Privada": "gallery",
                "Mensagens": "messages",
                "Ofertas Especiais": "offers"
            }
            
            for option, page in menu_options.items():
                if st.button(option, use_container_width=True, key=f"menu_{page}"):
                    st.session_state.current_page = page
                    save_persistent_data()
                    st.rerun()
            
            st.markdown("---")
            st.markdown("### Sua Conta")
            
            status = "VIP Ativo" if random.random() > 0.2 else "Conteúdo Básico"
            status_color = "#2ecc71" if status == "VIP Ativo" else "#f39c12"
            
            st.markdown(f"""
            <div style="
                background: rgba(255, 0, 255, 0.1); 
                padding: 10px; 
                border-radius: 8px;
            ">
                <p style="margin: 0; font-size: 0.9em;">
                    Status: <span style="color: {status_color}">{status}</span>
                </p>
                <p style="margin: 5px 0 0; font-size: 0.8em;">
                    Expira em: {random.randint(1,30)} dias
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown("### Upgrade VIP")
            st.markdown("""
            <div class="vip-badge">
                <p style="margin: 0 0 10px; font-weight: bold;">Acesso completo por apenas</p>
                <p style="margin: 0; font-size: 1.5em; font-weight: bold;">R$ 29,90/mês</p>
                <p style="margin: 10px 0 0; font-size: 0.8em;">Cancele quando quiser</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Tornar-se VIP", use_container_width=True, type="primary"):
                st.session_state.current_page = "offers"
                save_persistent_data()
                st.rerun()
            
            st.markdown("---")
            st.markdown("""
            <div style="text-align: center; font-size: 0.7em; color: #888;">
                <p>© 2024 Paloma Premium</p>
                <p>Conteúdo para maiores de 18 anos</p>
            </div>
            """, unsafe_allow_html=True)

    @staticmethod
    def show_gallery_page(conn):
        st.markdown("""
        <div style="
            background: rgba(255, 0, 255, 0.1);
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
        ">
            <p style="margin: 0;">Conteúdo exclusivo para assinantes VIP</p>
        </div>
        """, unsafe_allow_html=True)
        
        cols = st.columns(3)
        
        for idx, col in enumerate(cols):
            with col:
                st.image(
                    Config.IMG_GALLERY[idx],
                    use_container_width=True,
                    caption=f"Preview {idx+1}"
                )
                st.markdown(f"""
                <div style="
                    text-align: center;
                    font-size: 0.8em;
                    color: #FF00FF;
                    margin-top: -10px;
                ">
                    Conteúdo bloqueado
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center;">
            <h4>Desbloqueie acesso completo</h4>
            <p>Assine o plano VIP para ver todos os conteúdos</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Tornar-se VIP", 
                    key="vip_button_gallery", 
                    use_container_width=True,
                    type="primary"):
            st.session_state.current_page = "offers"
            st.rerun()
        
        if st.button("Voltar ao chat", key="back_from_gallery"):
            st.session_state.current_page = "chat"
            save_persistent_data()
            st.rerun()

    @staticmethod
    def chat_shortcuts():
        cols = st.columns(4)
        with cols[0]:
            if st.button("Início", key="shortcut_home", 
                       help="Voltar para a página inicial",
                       use_container_width=True):
                st.session_state.current_page = "home"
                save_persistent_data()
                st.rerun()
        with cols[1]:
            if st.button("Galeria", key="shortcut_gallery",
                       help="Acessar galeria privada",
                       use_container_width=True):
                st.session_state.current_page = "gallery"
                save_persistent_data()
                st.rerun()
        with cols[2]:
            if st.button("Ofertas", key="shortcut_offers",
                       help="Ver ofertas especiais",
                       use_container_width=True):
                st.session_state.current_page = "offers"
                save_persistent_data()
                st.rerun()
        with cols[3]:
            if st.button("VIP", key="shortcut_vip",
                       help="Acessar área VIP",
                       use_container_width=True):
                st.session_state.current_page = "vip"
                save_persistent_data()
                st.rerun()

        st.markdown("""
        <style>
            div[data-testid="stHorizontalBlock"] > div > div > button {
                color: white !important;
                border: 1px solid rgba(255, 0, 255, 0.7) !important;
                background: rgba(255, 0, 255, 0.15) !important;
                transition: all 0.3s !important;
                font-size: 0.8rem !important;
            }
            div[data-testid="stHorizontalBlock"] > div > div > button:hover {
                transform: translateY(-2px) !important;
                box-shadow: 0 2px 8px rgba(255, 0, 255, 0.3) !important;
            }
            @media (max-width: 400px) {
                div[data-testid="stHorizontalBlock"] > div > div > button {
                    font-size: 0.7rem !important;
                    padding: 6px 2px !important;
                }
            }
        </style>
        """, unsafe_allow_html=True)

    @staticmethod
    def enhanced_chat_ui(conn):
        st.markdown("""
        <style>
            .chat-header {
                background: linear-gradient(90deg, #FF00FF, #A020F0);
                color: white;
                padding: 15px;
                border-radius: 10px;
                margin-bottom: 20px;
                text-align: center;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }
            .stAudio {
                border-radius: 20px !important;
                background: rgba(255, 0, 255, 0.1) !important;
                padding: 10px !important;
                margin: 10px 0 !important;
            }
            audio::-webkit-media-controls-panel {
                background: linear-gradient(45deg, #FF00FF, #A020F0) !important;
            }
        </style>
        """, unsafe_allow_html=True)
        
        UiService.chat_shortcuts()
        
        st.markdown(f"""
        <div class="chat-header">
            <h2 style="margin:0; font-size:1.5em; display:inline-block;">Chat Privado com Paloma</h2>
        </div>
        """, unsafe_allow_html=True)
        
        st.sidebar.markdown(f"""
        <div style="
            background: rgba(255, 0, 255, 0.1);
            padding: 10px;
            border-radius: 8px;
            margin-bottom: 15px;
            text-align: center;
        ">
            <p style="margin:0; font-size:0.9em;">
                Mensagens hoje: <strong>{st.session_state.request_count}/{Config.MAX_REQUESTS_PER_SESSION}</strong>
            </p>
            <progress value="{st.session_state.request_count}" max="{Config.MAX_REQUESTS_PER_SESSION}" style="width:100%; height:6px;"></progress>
        </div>
        """, unsafe_allow_html=True)
        
        ChatService.process_user_input(conn)
        save_persistent_data()
        
        st.markdown("""
        <div style="
            text-align: center;
            margin-top: 20px;
            padding: 10px;
            font-size: 0.8em;
            color: #888;
        ">
            <p>Conversa privada • Suas mensagens são confidenciais</p>
        </div>
        """, unsafe_allow_html=True)

# ======================
# PÁGINAS (MANTIDO ORIGINAL COM AJUSTES DE CORES)
# ======================
class NewPages:
    @staticmethod
    def show_home_page():
        st.markdown("""
        <style>
            .hero-banner {
                background: linear-gradient(135deg, #0A0A0A, #1A1A1A);
                padding: 80px 20px;
                text-align: center;
                border-radius: 15px;
                color: white;
                margin-bottom: 30px;
                border: 2px solid #FF00FF;
            }
            .preview-img {
                border-radius: 10px;
                filter: blur(3px) brightness(0.7);
                transition: all 0.3s;
            }
            .preview-img:hover {
                filter: blur(0) brightness(1);
            }
        </style>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="hero-banner">
            <h1 style="color: #FF00FF;">Paloma Premium</h1>
            <p>Conteúdo exclusivo que você não encontra em nenhum outro lugar...</p>
            <div style="margin-top: 20px;">
                <a href="#vip" style="
                    background: #FF00FF;
                    color: white;
                    padding: 10px 25px;
                    border-radius: 30px;
                    text-decoration: none;
                    font-weight: bold;
                    display: inline-block;
                ">Quero Acessar Tudo</a>
            </div>
        </div>
        """, unsafe_allow_html=True)

        cols = st.columns(3)
        
        for col, img in zip(cols, Config.IMG_HOME_PREVIEWS):
            with col:
                st.image(img, use_container_width=True, caption="Conteúdo bloqueado", output_format="auto")
                st.markdown("""<div style="text-align:center; color: #FF00FF; margin-top: -15px;">VIP Only</div>""", unsafe_allow_html=True)

        st.markdown("---")
        
        if st.button("Iniciar Conversa Privada", 
                    use_container_width=True,
                    type="primary"):
            st.session_state.current_page = "chat"
            save_persistent_data()
            st.rerun()

        if st.button("Voltar ao chat", key="back_from_home"):
            st.session_state.current_page = "chat"
            save_persistent_data()
            st.rerun()

    @staticmethod
    def show_offers_page():
        st.markdown("""
        <style>
            .package-container {
                display: flex;
                justify-content: space-between;
                margin: 30px 0;
                gap: 20px;
            }
            .package-box {
                flex: 1;
                background: rgba(15, 15, 15, 0.7);
                border-radius: 15px;
                padding: 20px;
                border: 1px solid rgba(255, 0, 255, 0.7);
                transition: all 0.3s;
                min-height: 400px;
                position: relative;
                overflow: hidden;
            }
            .package-box:hover {
                transform: translateY(-5px);
                box-shadow: 0 10px 20px rgba(255, 0, 255, 0.3);
            }
            .package-start {
                border-color: #FF00FF;
            }
            .package-premium {
                border-color: #A020F0;
            }
            .package-extreme {
                border-color: #FF0066;
            }
            .package-header {
                text-align: center;
                padding-bottom: 15px;
                margin-bottom: 15px;
                border-bottom: 1px solid rgba(255, 0, 255, 0.3);
            }
            .package-price {
                font-size: 1.8em;
                font-weight: bold;
                margin: 10px 0;
            }
            .package-benefits {
                list-style-type: none;
                padding: 0;
            }
            .package-benefits li {
                padding: 8px 0;
                position: relative;
                padding-left: 25px;
            }
            .package-benefits li:before {
                content: "✓";
                color: #FF00FF;
                position: absolute;
                left: 0;
                font-weight: bold;
            }
            .package-badge {
                position: absolute;
                top: 15px;
                right: -30px;
                background: #FF00FF;
                color: white;
                padding: 5px 30px;
                transform: rotate(45deg);
                font-size: 0.8em;
                font-weight: bold;
                width: 100px;
                text-align: center;
            }
            .countdown-container {
                background: linear-gradient(45deg, #FF00FF, #A020F0);
                color: white;
                padding: 15px;
                border-radius: 10px;
                margin: 40px 0;
                box-shadow: 0 4px 15px rgba(255, 0, 255, 0.3);
                text-align: center;
            }
            .offer-card {
                border: 1px solid #FF00FF;
                border-radius: 15px;
                padding: 20px;
                margin-bottom: 20px;
                background: rgba(15, 15, 15, 0.7);
            }
            .offer-highlight {
                background: linear-gradient(45deg, #FF00FF, #A020F0);
                color: white;
                padding: 5px 10px;
                border-radius: 5px;
                font-weight: bold;
            }
        </style>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="text-align: center; margin-bottom: 30px;">
            <h2 style="color: #FF00FF; border-bottom: 2px solid #FF00FF; display: inline-block; padding-bottom: 5px;">PACOTES EXCLUSIVOS</h2>
            <p style="color: #aaa; margin-top: 10px;">Escolha o que melhor combina com seus desejos...</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="package-container">', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="package-box package-start">
            <div class="package-header">
                <h3 style="color: #FF00FF;">START</h3>
                <div class="package-price" style="color: #FF00FF;">R$ 49,90</div>
                <small>para iniciantes</small>
            </div>
            <ul class="package-benefits">
                <li>10 fotos Inéditas</li>
                <li>3 vídeo Intimos</li>
                <li>Fotos Exclusivas</li>
                <li>Videos Intimos </li>
                <li>Fotos Buceta</li>
            </ul>
            <div style="position: absolute; bottom: 20px; width: calc(100% - 40px);">
                <a href="{checkout_start}" target="_blank" rel="noopener noreferrer" style="
                    display: block;
                    background: linear-gradient(45deg, #FF00FF, #A020F0);
                    color: white;
                    text-align: center;
                    padding: 10px;
                    border-radius: 8px;
                    text-decoration: none;
                    font-weight: bold;
                    transition: all 0.3s;
                " onmouseover="this.style.transform='scale(1.05)'" 
                onmouseout="this.style.transform='scale(1)'"
                onclick="this.innerHTML='REDIRECIONANDO ⌛'; this.style.opacity='0.7'">
                    QUERO ESTE PACOTE ➔
                </a>
            </div>
        </div>
        """.format(checkout_start=Config.CHECKOUT_START), unsafe_allow_html=True)

        st.markdown("""
        <div class="package-box package-premium">
            <div class="package-badge">POPULAR</div>
            <div class="package-header">
                <h3 style="color: #A020F0;">PREMIUM</h3>
                <div class="package-price" style="color: #A020F0;">R$ 99,90</div>
                <small>experiência completa</small>
            </div>
            <ul class="package-benefits">
                <li>20 fotos exclusivas</li>
                <li>5 vídeos premium</li>
                <li>Fotos Peito</li>
                <li>Fotos Bunda</li>
                <li>Fotos Buceta</li>
                <li>Fotos Exclusivas e Videos Exclusivos</li>
                <li>Videos Masturbando</li>
            </ul>
            <div style="position: absolute; bottom: 20px; width: calc(100% - 40px);">
                <a href="{checkout_premium}" target="_blank" rel="noopener noreferrer" style="
                    display: block;
                    background: linear-gradient(45deg, #A020F0, #FF00FF);
                    color: white;
                    text-align: center;
                    padding: 10px;
                    border-radius: 8px;
                    text-decoration: none;
                    font-weight: bold;
                    transition: all 0.3s;
                " onmouseover="this.style.transform='scale(1.05)'" 
                onmouseout="this.style.transform='scale(1)'"
                onclick="this.innerHTML='REDIRECIONANDO ⌛'; this.style.opacity='0.7'">
                    QUERO ESTE PACOTE ➔
                </a>
            </div>
        </div>
        """.format(checkout_premium=Config.CHECKOUT_PREMIUM), unsafe_allow_html=True)

        st.markdown("""
        <div class="package-box package-extreme">
            <div class="package-header">
                <h3 style="color: #FF0066;">EXTREME</h3>
                <div class="package-price" style="color: #FF0066;">R$ 199,90</div>
                <small>para verdadeiros fãs</small>
            </div>
            <ul class="package-benefits">
                <li>30 fotos ultra-exclusivas</li>
                <li>10 Videos Exclusivos</li>
                <li>Fotos Peito</li>
                <li>Fotos Bunda</li>
                <li>Fotos Buceta</li>
                <li>Fotos Exclusivas</li>
                <li>Videos Masturbando</li>
                <li>Videos Transando</li>
                <li>Acesso a conteúdos futuros</li>
            </ul>
            <div style="position: absolute; bottom: 20px; width: calc(100% - 40px);">
                <a href="{checkout_extreme}" target="_blank" rel="noopener noreferrer" style="
                    display: block;
                    background: linear-gradient(45deg, #FF0066, #A020F0);
                    color: white;
                    text-align: center;
                    padding: 10px;
                    border-radius: 8px;
                    text-decoration: none;
                    font-weight: bold;
                    transition: all 0.3s;
                " onmouseover="this.style.transform='scale(1.05)'" 
                onmouseout="this.style.transform='scale(1)'"
                onclick="this.innerHTML='REDIRECIONANDO ⌛'; this.style.opacity='0.7'">
                    QUERO ESTE PACOTE ➔
                </a>
            </div>
        </div>
        """.format(checkout_extreme=Config.CHECKOUT_EXTREME), unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("""
        <div class="countdown-container">
            <h3 style="margin:0;">OFERTA RELÂMPAGO</h3>
            <div id="countdown" style="font-size: 1.5em; font-weight: bold;">23:59:59</div>
            <p style="margin:5px 0 0;">Termina em breve!</p>
        </div>
        """, unsafe_allow_html=True)

        st.components.v1.html("""
        <script>
        function updateCountdown() {
            const countdownElement = parent.document.getElementById('countdown');
            if (!countdownElement) return;
            
            let time = countdownElement.textContent.split(':');
            let hours = parseInt(time[0]);
            let minutes = parseInt(time[1]);
            let seconds = parseInt(time[2]);
            
            seconds--;
            if (seconds < 0) { seconds = 59; minutes--; }
            if (minutes < 0) { minutes = 59; hours--; }
            if (hours < 0) { hours = 23; }
            
            countdownElement.textContent = 
                `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
            
            setTimeout(updateCountdown, 1000);
        }
        
        setTimeout(updateCountdown, 1000);
        </script>
        """, height=0)

        plans = [
            {
                "name": "1 Mês",
                "price": "R$ 29,90",
                "original": "R$ 49,90",
                "benefits": ["Acesso total", "Conteúdo novo diário", "Chat privado"],
                "tag": "COMUM",
                "link": Config.CHECKOUT_VIP_1MES + "?plan=1mes"
            },
            {
                "name": "3 Meses",
                "price": "R$ 69,90",
                "original": "R$ 149,70",
                "benefits": ["25% de desconto", "Bônus: 1 vídeo exclusivo", "Prioridade no chat"],
                "tag": "MAIS POPULAR",
                "link": Config.CHECKOUT_VIP_3MESES + "?plan=3meses"
            },
            {
                "name": "1 Ano",
                "price": "R$ 199,90",
                "original": "R$ 598,80",
                "benefits": ["66% de desconto", "Presente surpresa mensal", "Acesso a conteúdos raros"],
                "tag": "MELHOR CUSTO-BENEFÍCIO",
                "link": Config.CHECKOUT_VIP_1ANO + "?plan=1ano"
            }
        ]

        for plan in plans:
            with st.container():
                st.markdown(f"""
                <div class="offer-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h3>{plan['name']}</h3>
                        {f'<span class="offer-highlight">{plan["tag"]}</span>' if plan["tag"] else ''}
                    </div>
                    <div style="margin: 10px 0;">
                        <span style="font-size: 1.8em; color: #FF00FF; font-weight: bold;">{plan['price']}</span>
                        <span style="text-decoration: line-through; color: #888; margin-left: 10px;">{plan['original']}</span>
                    </div>
                    <ul style="padding-left: 20px;">
                        {''.join([f'<li style="margin-bottom: 5px;">{benefit}</li>' for benefit in plan['benefits']])}
                    </ul>
                    <div style="text-align: center; margin-top: 15px;">
                        <a href="{plan['link']}" style="
                            background: linear-gradient(45deg, #FF00FF, #A020F0);
                            color: white;
                            padding: 10px 20px;
                            border-radius: 30px;
                            text-decoration: none;
                            display: inline-block;
                            font-weight: bold;
                        ">
                            Assinar {plan['name']}
                        </a>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        if st.button("Voltar ao chat", key="back_from_offers"):
            st.session_state.current_page = "chat"
            save_persistent_data()
            st.rerun()

# ======================
# SERVIÇOS DE CHAT (MANTIDO ORIGINAL)
# ======================
class ChatService:
    @staticmethod
    def initialize_session(conn):
        load_persistent_data()
        
        if "session_id" not in st.session_state:
            st.session_state.session_id = str(random.randint(100000, 999999))
        
        if "messages" not in st.session_state:
            st.session_state.messages = DatabaseService.load_messages(
                conn,
                get_user_id(),
                st.session_state.session_id
            )
        
        if "request_count" not in st.session_state:
            st.session_state.request_count = len([
                m for m in st.session_state.messages 
                if m["role"] == "user"
            ])
        
        defaults = {
            'age_verified': False,
            'connection_complete': False,
            'chat_started': False,
            'audio_sent': False,
            'current_page': 'home',
            'show_vip_offer': False
        }
        
        for key, default in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = default

    @staticmethod
    def format_conversation_history(messages, max_messages=10):
        """Formata o histórico de conversa para incluir no prompt"""
        formatted = []
        
        # Pegar apenas as últimas mensagens (evitar token limit)
        for msg in messages[-max_messages:]:
            role = "Cliente" if msg["role"] == "user" else "Paloma"
            
            # Tratar mensagens de áudio e JSON
            content = msg["content"]
            if content == "[ÁUDIO]":
                content = "[Enviou um áudio sensual]"
            elif content.startswith('{"text"'):
                try:
                    content = json.loads(content).get("text", content)
                except:
                    pass
            
            formatted.append(f"{role}: {content}")
        
        return "\n".join(formatted)

    @staticmethod
    def display_chat_history():
        chat_container = st.container()
        with chat_container:
            for msg in st.session_state.messages[-12:]:
                if msg["role"] == "user":
                    with st.chat_message("user", avatar="🧑"):
                        st.markdown(f"""
                        <div style="
                            background: rgba(0, 0, 0, 0.1);
                            padding: 12px;
                            border-radius: 18px 18px 0 18px;
                            margin: 5px 0;
                        ">
                            {msg["content"]}
                        </div>
                        """, unsafe_allow_html=True)
                elif msg["content"] == "[ÁUDIO]":
                    with st.chat_message("assistant", avatar="💋"):
                        st.markdown(UiService.get_chat_audio_player(), unsafe_allow_html=True)
                else:
                    try:
                        content_data = json.loads(msg["content"])
                        if isinstance(content_data, dict):
                            with st.chat_message("assistant", avatar="💋"):
                                st.markdown(f"""
                                <div style="
                                    background: linear-gradient(45deg, #FF00FF, #A020F0);
                                    color: white;
                                    padding: 12px;
                                    border-radius: 18px 18px 18px 0;
                                    margin: 5px 0;
                                ">
                                    {content_data.get("text", "")}
                                </div>
                                """, unsafe_allow_html=True)
                                
                                if content_data.get("cta", {}).get("show"):
                                    if st.button(
                                        content_data.get("cta", {}).get("label", "Ver Ofertas"),
                                        key=f"hist_button_{msg.get('timestamp', '')}",
                                        use_container_width=True
                                    ):
                                        st.session_state.current_page = content_data.get("cta", {}).get("target", "offers")
                                        save_persistent_data()
                                        st.rerun()
                        else:
                            with st.chat_message("assistant", avatar="💋"):
                                st.markdown(f"""
                                <div style="
                                    background: linear-gradient(45deg, #FF00FF, #A020F0);
                                    color: white;
                                    padding: 12px;
                                    border-radius: 18px 18px 18px 0;
                                    margin: 5px 0;
                                ">
                                    {msg["content"]}
                                </div>
                                """, unsafe_allow_html=True)
                    except json.JSONDecodeError:
                        with st.chat_message("assistant", avatar="💋"):
                            st.markdown(f"""
                            <div style="
                                background: linear-gradient(45deg, #FF00FF, #A020F0);
                                color: white;
                                padding: 12px;
                                border-radius: 18px 18px 18px 0;
                                margin: 5px 0;
                            ">
                                {msg["content"]}
                            </div>
                            """, unsafe_allow_html=True)

    @staticmethod
    def validate_input(user_input):
        cleaned_input = re.sub(r'<[^>]*>', '', user_input)
        return cleaned_input[:500]

    @staticmethod
    def process_user_input(conn):
        ChatService.display_chat_history()
        
        if not st.session_state.get("audio_sent") and st.session_state.chat_started:
            status_container = st.empty()
            UiService.show_audio_recording_effect(status_container)
            
            st.session_state.messages.append({
                "role": "assistant",
                "content": "[ÁUDIO]"
            })
            DatabaseService.save_message(
                conn,
                get_user_id(),
                st.session_state.session_id,
                "assistant",
                "[ÁUDIO]"
            )
            st.session_state.audio_sent = True
            save_persistent_data()
            st.rerun()
        
        user_input = st.chat_input("Escreva sua mensagem aqui", key="chat_input")
        
        if user_input:
            cleaned_input = ChatService.validate_input(user_input)
            
            if st.session_state.request_count >= Config.MAX_REQUESTS_PER_SESSION:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "Vou ficar ocupada agora, me manda mensagem depois?"
                })
                DatabaseService.save_message(
                    conn,
                    get_user_id(),
                    st.session_state.session_id,
                    "assistant",
                    "Estou ficando cansada, amor... Que tal continuarmos mais tarde?"
                )
                save_persistent_data()
                st.rerun()
                return
            
            st.session_state.messages.append({
                "role": "user",
                "content": cleaned_input
            })
            DatabaseService.save_message(
                conn,
                get_user_id(),
                st.session_state.session_id,
                "user",
                cleaned_input
            )
            
            st.session_state.request_count += 1
            
            with st.chat_message("user", avatar="🧑"):
                st.markdown(f"""
                <div style="
                    background: rgba(0, 0, 0, 0.1);
                    padding: 12px;
                    border-radius: 18px 18px 0 18px;
                    margin: 5px 0;
                ">
                    {cleaned_input}
                </div>
                """, unsafe_allow_html=True)
            
            with st.chat_message("assistant", avatar="💋"):
                resposta = ApiService.ask_gemini(cleaned_input, st.session_state.session_id, conn)
                
                # Garante que a resposta tenha o formato correto
                if isinstance(resposta, str):
                    resposta = {"text": resposta, "cta": {"show": False}}
                elif "text" not in resposta:
                    resposta = {"text": str(resposta), "cta": {"show": False}}
                
                st.markdown(f"""
                <div style="
                    background: linear-gradient(45deg, #FF00FF, #A020F0);
                    color: white;
                    padding: 12px;
                    border-radius: 18px 18px 18px 0;
                    margin: 5px 0;
                ">
                    {resposta["text"]}
                </div>
                """, unsafe_allow_html=True)
                
                if resposta.get("cta", {}).get("show"):
                    if st.button(
                        resposta["cta"].get("label", "Ver Ofertas"),
                        key=f"chat_button_{time.time()}",
                        use_container_width=True
                    ):
                        st.session_state.current_page = resposta["cta"].get("target", "offers")
                        save_persistent_data()
                        st.rerun()
            
            st.session_state.messages.append({
                "role": "assistant",
                "content": json.dumps(resposta)
            })
            DatabaseService.save_message(
                conn,
                get_user_id(),
                st.session_state.session_id,
                "assistant",
                json.dumps(resposta)
            )
            
            save_persistent_data()
            
            st.markdown("""
            <script>
                window.scrollTo(0, document.body.scrollHeight);
            </script>
            """, unsafe_allow_html=True)

# ======================
# APLICAÇÃO PRINCIPAL (MANTIDO ORIGINAL)
# ======================
def main():
    if 'db_conn' not in st.session_state:
        st.session_state.db_conn = DatabaseService.init_db()
    
    conn = st.session_state.db_conn
    
    ChatService.initialize_session(conn)
    
    if not st.session_state.age_verified:
        UiService.age_verification()
        st.stop()
    
    UiService.setup_sidebar()
    
    if not st.session_state.connection_complete:
        UiService.show_call_effect()
        st.session_state.connection_complete = True
        save_persistent_data()
        st.rerun()
    
    if not st.session_state.chat_started:
        col1, col2, col3 = st.columns([1,3,1])
        with col2:
            st.markdown("""
            <div style="text-align: center; margin: 50px 0;">
                <img src="{profile_img}" width="120" style="border-radius: 50%; border: 3px solid #FF00FF;">
                <h2 style="color: #FF00FF; margin-top: 15px;">Paloma</h2>
                <p style="font-size: 1.1em;">Estou pronta para você, amor...</p>
            </div>
            """.format(profile_img=Config.IMG_PROFILE), unsafe_allow_html=True)
            
            if st.button("Iniciar Conversa", type="primary", use_container_width=True):
                st.session_state.update({
                    'chat_started': True,
                    'current_page': 'chat',
                    'audio_sent': False
                })
                save_persistent_data()
                st.rerun()
        st.stop()
    
    if st.session_state.current_page == "home":
        NewPages.show_home_page()
    elif st.session_state.current_page == "gallery":
        UiService.show_gallery_page(conn)
    elif st.session_state.current_page == "offers":
        NewPages.show_offers_page()
    elif st.session_state.current_page == "vip":
        st.session_state.show_vip_offer = True
        save_persistent_data()
        st.rerun()
    elif st.session_state.get("show_vip_offer", False):
        st.warning("Página VIP em desenvolvimento")
        if st.button("Voltar ao chat"):
            st.session_state.show_vip_offer = False
            save_persistent_data()
            st.rerun()
    else:
        UiService.enhanced_chat_ui(conn)
    
    save_persistent_data()

if __name__ == "__main__":
    main()
