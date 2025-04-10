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
from datetime import datetime
from pathlib import Path

# ======================
# CONSTANTES (CONFIGURAÇÕES ORIGINAIS PRESERVADAS)
# ======================
class Config:
    API_KEY = "AIzaSyDTaYm2KHHnVPdWy4l5pEaGPM7QR0g3IPc"  # Mantida conforme solicitado
    API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"
    VIP_LINK = "https://exemplo.com/vip"
    MAX_REQUESTS_PER_SESSION = 30
    REQUEST_TIMEOUT = 30
    AUDIO_FILE = "https://raw.githubusercontent.com/seu-usuario/seu-repo/main/paloma_audio.mp3"
    AUDIO_DURATION = 7  # Segundos do áudio

# ======================
# MODELO PERSONA (ORIGINAL)
# ======================
class Persona:
    PALOMA = """
    [CONFIGURAÇÃO DA PERSONALIDADE]
    Você é Paloma, criadora de conteúdo adulto premium. Suas características:
    
    [TOM]
    - Linguagem: informal mas sofisticada
    - Sedução: sugestiva, nunca explícita
    - Persuasão: focada em despertar curiosidade
    
    [TÉCNICAS DE VENDA]
    1. Escassez: "Isso é só para os meus mais chegados..."
    2. Prova Social: "Meus assinantes sempre pedem mais..."
    3. Benefícios: "Você vai ter acesso a..."
    4. Chamadas Indiretas: "Quer ver o que preparei pra você?"
    
    [REGRA DE OURO]
    - Nunca diga diretamente "compre" ou "assine"
    - Sempre insinue, sugira, provoque curiosidade
    """

# ======================
# SERVIÇOS DE BANCO DE DADOS (ORIGINAL)
# ======================
class DatabaseService:
    @staticmethod
    def init_db():
        conn = sqlite3.connect('chat_history.db', check_same_thread=False)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS conversations
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     session_id TEXT,
                     timestamp DATETIME,
                     role TEXT,
                     content TEXT)''')
        conn.commit()
        return conn

    @staticmethod
    def save_message(conn, session_id, role, content):
        try:
            c = conn.cursor()
            c.execute("INSERT INTO conversations (session_id, timestamp, role, content) VALUES (?, ?, ?, ?)",
                     (session_id, datetime.now(), role, content))
            conn.commit()
        except sqlite3.Error as e:
            st.error(f"Erro ao salvar mensagem: {e}")

# ======================
# SERVIÇOS DE API (ORIGINAL)
# ======================
class ApiService:
    @staticmethod
    def ask_gemini(prompt, session_id, conn):
        if any(word in prompt.lower() for word in ["ver", "mostra", "foto", "vídeo", "fotinho", "foto sua"]):
            DatabaseService.save_message(conn, session_id, "user", prompt)
            resposta = f"Quer ver tudo amor? 💋 {Config.VIP_LINK}"
            DatabaseService.save_message(conn, session_id, "assistant", resposta)
            return resposta
        
        headers = {'Content-Type': 'application/json'}
        data = {
            "contents": [{
                "role": "user",
                "parts": [{"text": Persona.PALOMA + f"\nCliente disse: {prompt}\nResponda em no máximo 15 palavras"}]
            }]
        }
        
        try:
            status_container = st.empty()
            UiService.show_status_effect(status_container, "viewed")
            UiService.show_status_effect(status_container, "typing")
            
            response = requests.post(Config.API_URL, headers=headers, json=data, timeout=Config.REQUEST_TIMEOUT)
            response.raise_for_status()
            
            resposta = response.json().get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "Hmm... que tal conversarmos sobre algo mais interessante? 😉")
            
            if random.random() > 0.7:
                resposta += " " + random.choice(["Só hoje...", "Últimas vagas!", "Oferta especial 😉"])
            
            DatabaseService.save_message(conn, session_id, "user", prompt)
            DatabaseService.save_message(conn, session_id, "assistant", resposta)
            return resposta
        
        except requests.exceptions.RequestException as e:
            st.error(f"Erro na conexão: {str(e)}")
            return "Estou tendo problemas técnicos, amor... Podemos tentar de novo mais tarde? 💋"
        except Exception as e:
            st.error(f"Erro inesperado: {str(e)}")
            return "Hmm... que tal conversarmos sobre algo mais interessante? 😉"

# ======================
# SERVIÇOS DE UI (ATUALIZADO COM TODOS OS EFEITOS)
# ======================
class UiService:
    @staticmethod
    def get_chat_audio_player():
        """Player estilizado para o fluxo de mensagens"""
        return f"""
        <div style="
            background: linear-gradient(45deg, #ff66b3, #ff1493);
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
    def get_fixed_audio_player():
        """Player fixo no topo do chat"""
        return f"""
        <div style="
            margin-bottom: 20px;
            border-bottom: 1px solid rgba(255, 102, 179, 0.3);
            padding-bottom: 20px;
        ">
            <div style="
                color: #ff66b3;
                font-weight: bold;
                margin-bottom: 8px;
                display: flex;
                align-items: center;
                gap: 8px;
            ">
                <span>🎤</span>
                <span>Mensagem de Voz</span>
            </div>
            <div style="
                background: rgba(255,255,255,0.1);
                border-radius: 15px;
                padding: 10px;
            ">
                <audio controls style="width:100%; height:40px;">
                    <source src="{Config.AUDIO_FILE}" type="audio/mp3">
                </audio>
            </div>
        </div>
        """

    @staticmethod
    def show_audio_recording_effect(container):
        """Efeito 'Gravando um áudio...' com animação"""
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

    # ... (Outros métodos mantidos iguais ao original: show_call_effect, show_status_effect, age_verification, etc.)

# ======================
# SERVIÇOS DE CHAT (ATUALIZADO)
# ======================
class ChatService:
    @staticmethod
    def initialize_session():
        if "age_verified" not in st.session_state:
            st.session_state.update({
                "age_verified": False,
                "connection_complete": False,
                "chat_started": False,
                "messages": [],
                "session_id": str(random.randint(100000, 999999)),
                "request_count": 0,
                "current_page": "home",
                "show_vip_offer": False,
                "audio_sent": False
            })

    @staticmethod
    def display_chat_history():
        chat_container = st.container()
        with chat_container:
            # Player FIXO no topo (se áudio foi enviado)
            if st.session_state.get("audio_sent"):
                st.markdown(UiService.get_fixed_audio_player(), unsafe_allow_html=True)
            
            # Histórico de mensagens
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
                
                # Mensagem especial para áudio no histórico
                elif msg["content"] == "[ÁUDIO]":
                    with st.chat_message("assistant", avatar="💋"):
                        st.markdown(UiService.get_chat_audio_player(), unsafe_allow_html=True)
                
                else:
                    with st.chat_message("assistant", avatar="💋"):
                        st.markdown(f"""
                        <div style="
                            background: linear-gradient(45deg, #ff66b3, #ff1493);
                            color: white;
                            padding: 12px;
                            border-radius: 18px 18px 18px 0;
                            margin: 5px 0;
                        ">
                            {msg["content"]}
                        </div>
                        """, unsafe_allow_html=True)

    @staticmethod
    def process_user_input(conn):
        ChatService.display_chat_history()
        
        # Envio do áudio inicial
        if not st.session_state.get("audio_sent") and st.session_state.chat_started:
            status_container = st.empty()
            UiService.show_audio_recording_effect(status_container)  # 👈 EFEITO DE GRAVAÇÃO
            
            # Adiciona ao histórico como mensagem especial
            st.session_state.messages.append({
                "role": "assistant",
                "content": "[ÁUDIO]"
            })
            st.session_state.audio_sent = True
            st.rerun()
        
        # Restante do método mantido igual ao original...
        # ... (processamento de mensagens do usuário, etc.)

# ======================
# APLICAÇÃO PRINCIPAL (COM CSS ATUALIZADO)
# ======================
def main():
    st.markdown("""
    <style>
        /* Estilos para os players de áudio */
        audio {
            border-radius: 20px !important;
        }
        audio::-webkit-media-controls-panel {
            background: linear-gradient(45deg, #ff66b3, #ff1493) !important;
        }
        audio::-webkit-media-controls-play-button {
            filter: brightness(0) invert(1) !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # ... (Restante do código main() mantido igual ao original)

if __name__ == "__main__":
    main()
