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
# CONSTANTES E CONFIGURAÇÕES
# ======================
class Config:
    API_KEY = "AIzaSyDTaYm2KHHnVPdWy4l5pEaGPM7QR0g3IPc"  # SUA CHAVE PRESERVADA
    API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={API_KEY}"
    VIP_LINK = "https://exemplo.com/vip"
    MAX_REQUESTS_PER_SESSION = 30
    REQUEST_TIMEOUT = 30
    AUDIO_FILE = "https://github.com/gustapb77/ChatBotHot/raw/main/assets/audio/paloma_audio.mp3"
    AUDIO_DURATION = 7

# ======================
# SEGURANÇA
# ======================
class Security:
    @staticmethod
    def sanitize_input(text: str) -> str:
        """Remove scripts, SQL injection e limita tamanho"""
        cleaned = re.sub(r'[<>"\';()&$]', '', text)
        return cleaned[:300]

# ======================
# MODELOS DE DADOS
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
# SERVIÇOS DE BANCO DE DADOS
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
# SERVIÇOS DE API
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
# PÁGINAS
# ======================
class NewPages:
    @staticmethod
    def show_home_page():
        st.markdown("""
        <style>
            .hero-banner {
                background: linear-gradient(135deg, #1e0033, #3c0066);
                padding: 80px 20px;
                text-align: center;
                border-radius: 15px;
                color: white;
                margin-bottom: 30px;
                border: 2px solid #ff66b3;
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
            <h1 style="color: #ff66b3;">💋 Paloma Premium</h1>
            <p>Conteúdo exclusivo que você não encontra em nenhum outro lugar...</p>
            <div style="margin-top: 20px;">
                <a href="#vip" style="
                    background: #ff66b3;
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

        st.subheader("🔍 Prévia do Conteúdo VIP")
        cols = st.columns(3)
        preview_images = [
            "https://i.ibb.co/k2MJg4XC/Save-Clip-App-412457343-378531441368078-7870326395110089440-n.jpg",
            "https://i.ibb.co/MxqKBk1X/Save-Clip-App-481825770-18486618637042608-2702272791254832108-n.jpg",
            "https://i.ibb.co/F4CkkYTL/Save-Clip-App-461241348-1219420546053727-2357827070610318448-n.jpg"
        ]
        
        for col, img in zip(cols, preview_images):
            with col:
                st.image(img, use_container_width=True, caption="🔒 Conteúdo bloqueado", output_format="auto")
                st.markdown("""<div style="text-align:center; color: #ff66b3; margin-top: -15px;">VIP Only</div>""", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown(f"""
        <div style="text-align: center;">
            <h3>🔓 Acesso Ilimitado por Apenas R$29,90/mês</h3>
            <a href="{Config.VIP_LINK}" style="
                background: linear-gradient(45deg, #ff1493, #9400d3);
                color: white;
                padding: 12px 30px;
                border-radius: 30px;
                text-decoration: none;
                font-weight: bold;
                display: inline-block;
                margin-top: 10px;
            ">
                Tornar-se VIP Agora
            </a>
        </div>
        """, unsafe_allow_html=True)
        
        # ATUALIZAÇÃO002 - Botão Voltar ao Chat
        UiService.back_to_chat_button(extra_margin_top=40)

    @staticmethod
    def show_offers_page():
        st.title("🎁 Ofertas Especiais")
        st.markdown("""
        <style>
            .offer-card {
                border: 1px solid #ff66b3;
                border-radius: 15px;
                padding: 20px;
                margin-bottom: 20px;
                background: rgba(30, 0, 51, 0.3);
            }
            .offer-highlight {
                background: linear-gradient(45deg, #ff0066, #ff66b3);
                color: white;
                padding: 5px 10px;
                border-radius: 5px;
                font-weight: bold;
            }
        </style>
        """, unsafe_allow_html=True)

        # ATUALIZAÇÃO003 - Countdown Funcional (INÍCIO)
        st.markdown("""
        <style>
            #dynamic-countdown {
                font-size: 1.8em;
                font-weight: bold;
                color: #ff1493;
                animation: pulse 1.5s infinite;
            }
            @keyframes pulse {
                0% { opacity: 1; }
                50% { opacity: 0.7; }
                100% { opacity: 1; }
            }
            .offer-expired {
                color: white !important;
                background: #ff0000 !important;
                padding: 10px;
                border-radius: 5px;
            }
        </style>

        <div style="text-align: center; margin: 25px 0;">
            <h3 style="color: #ff1493; margin:0;">⏳ OFERTA RELÂMPAGO</h3>
            <div id="dynamic-countdown"></div>
            <p style="margin:5px 0 0; font-size:0.9em;">Termina em breve!</p>
        </div>

        <script>
            const endTime = new Date();
            endTime.setHours(endTime.getHours() + 24);

            function updateCountdown() {
                const now = new Date();
                const diff = endTime - now;
                
                if (diff <= 0) {
                    document.getElementById("dynamic-countdown").innerHTML = 
                        "⏰ OFERTA EXPIRADA!";
                    document.getElementById("dynamic-countdown").className = "offer-expired";
                    return;
                }
                
                const hours = Math.floor(diff / (1000 * 60 * 60));
                const mins = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
                const secs = Math.floor((diff % (1000 * 60)) / 1000);
                
                document.getElementById("dynamic-countdown").innerHTML = 
                    `${hours.toString().padStart(2, '0')}h ${mins.toString().padStart(2, '0')}m ${secs.toString().padStart(2, '0')}s`;
                
                setTimeout(updateCountdown, 1000);
            }
            updateCountdown();
        </script>
        """, unsafe_allow_html=True)
        # ATUALIZAÇÃO003 - Countdown Funcional (FIM)

        plans = [
            {
                "name": "1 Mês",
                "price": "R$ 29,90",
                "original": "R$ 49,90",
                "benefits": ["Acesso total", "Conteúdo novo diário", "Chat privado"],
                "tag": "COMUM"
            },
            {
                "name": "3 Meses",
                "price": "R$ 69,90",
                "original": "R$ 149,70",
                "benefits": ["25% de desconto", "Bônus: 1 vídeo exclusivo", "Prioridade no chat"],
                "tag": "MAIS POPULAR"
            },
            {
                "name": "1 Ano",
                "price": "R$ 199,90",
                "original": "R$ 598,80",
                "benefits": ["66% de desconto", "Presente surpresa mensal", "Acesso a conteúdos raros"],
                "tag": "MELHOR CUSTO-BENEFÍCIO"
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
                        <span style="font-size: 1.8em; color: #ff66b3; font-weight: bold;">{plan['price']}</span>
                        <span style="text-decoration: line-through; color: #888; margin-left: 10px;">{plan['original']}</span>
                    </div>
                    <ul style="padding-left: 20px;">
                        {''.join([f'<li style="margin-bottom: 5px;">{benefit}</li>' for benefit in plan['benefits']])}
                    </ul>
                    <div style="text-align: center; margin-top: 15px;">
                        <a href="{Config.VIP_LINK}?plan={plan['name'].replace(' ', '').lower()}" style="
                            background: linear-gradient(45deg, #ff1493, #9400d3);
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
        
        # ATUALIZAÇÃO002 - Botão Voltar ao Chat
        UiService.back_to_chat_button(extra_margin_top=40)

# ======================
# SERVIÇOS DE INTERFACE (UI)
# ======================
class UiService:
    # ATUALIZAÇÃO001 - Botões Responsivos (INÍCIO)
    @staticmethod
    def chat_shortcuts():
        st.markdown("""
        <style>
            .chat-shortcuts-container {
                display: flex;
                overflow-x: auto;
                gap: 8px;
                padding-bottom: 10px;
                margin-bottom: 15px;
                -webkit-overflow-scrolling: touch;
            }
            .chat-shortcuts-container::-webkit-scrollbar {
                display: none;
            }
            .chat-shortcut-btn {
                flex: 0 0 auto;
                width: 23%;
                min-width: 80px !important;
                white-space: nowrap;
                padding: 8px 5px !important;
                background: rgba(255, 102, 179, 0.15) !important;
                border: 1px solid #ff66b3 !important;
                border-radius: 8px !important;
                transition: all 0.3s !important;
                text-align: center;
                cursor: pointer;
            }
            .chat-shortcut-btn:hover {
                background: rgba(255, 102, 179, 0.3) !important;
            }
            @media (hover: none) {
                .chat-shortcut-btn:active {
                    transform: scale(0.95);
                }
            }
        </style>

        <div class="chat-shortcuts-container">
            <button class="chat-shortcut-btn" onclick="window.location.hash='home'">🏠 Início</button>
            <button class="chat-shortcut-btn" onclick="window.location.hash='gallery'">📸 Galeria</button>
            <button class="chat-shortcut-btn" onclick="window.location.hash='offers'">🎁 Ofertas</button>
            <button class="chat-shortcut-btn" onclick="window.location.hash='vip'">💎 VIP</button>
        </div>
        """, unsafe_allow_html=True)
    # ATUALIZAÇÃO001 - Botões Responsivos (FIM)

    # ATUALIZAÇÃO002 - Botão Voltar ao Chat (INÍCIO)
    @staticmethod
    def back_to_chat_button(extra_margin_top: int = 20):
        st.markdown(f"""
        <div style="margin-top: {extra_margin_top}px; text-align: center;">
            <button onclick="window.location.hash='chat'" style="
                background: linear-gradient(45deg, #ff66b3, #ff1493);
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 20px;
                cursor: pointer;
                font-size: 14px;
            ">
                ← Voltar ao Chat
            </button>
        </div>
        """, unsafe_allow_html=True)
    # ATUALIZAÇÃO002 - Botão Voltar ao Chat (FIM)

    @staticmethod
    def get_chat_audio_player():
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
    def show_call_effect():
        LIGANDO_DELAY = 5
        ATENDIDA_DELAY = 3

        call_container = st.empty()
        call_container.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #1e0033, #3c0066);
            border-radius: 20px;
            padding: 30px;
            max-width: 300px;
            margin: 0 auto;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            border: 2px solid #ff66b3;
            text-align: center;
            color: white;
            animation: pulse-ring 2s infinite;
        ">
            <div style="font-size: 3rem;">📱</div>
            <h3 style="color: #ff66b3; margin-bottom: 5px;">Ligando para Paloma...</h3>
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
            background: linear-gradient(135deg, #1e0033, #3c0066);
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
            "viewed": ["Visualizado", "Mensagem recebida", "Recebido"],
            "typing": ["Digitando", "Respondendo", "Escrevendo"]
        }
        
        message = random.choice(status_messages[status_type])
        dots = ""
        start_time = time.time()
        duration = 2.5 if status_type == "viewed" else random.uniform(3, 7)
        
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
                background: linear-gradient(145deg, #1e0033, #3c0066);
                border-radius: 15px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                border: 1px solid rgba(255, 102, 179, 0.2);
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
                color: #ff66b3;
            }
            .age-title {
                font-size: 1.8rem;
                font-weight: 700;
                margin: 0;
                color: #ff66b3;
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
            if st.button("✅ Confirmo que sou maior de 18 anos", 
                        key="age_checkbox",
                        use_container_width=True,
                        type="primary"):
                st.session_state.age_verified = True
                st.rerun()

    @staticmethod
    def setup_sidebar():
        with st.sidebar:
            st.markdown("""
            <style>
                .sidebar-header {
                    text-align: center; 
                    margin-bottom: 20px;
                }
                .sidebar-header img {
                    border-radius: 50%; 
                    border: 2px solid #ff66b3;
                    width: 80px;
                    height: 80px;
                    object-fit: cover;
                }
                .vip-badge {
                    background: linear-gradient(45deg, #ff1493, #9400d3);
                    padding: 15px;
                    border-radius: 8px;
                    color: white;
                    text-align: center;
                    margin: 10px 0;
                }
                .menu-item {
                    transition: all 0.3s;
                    padding: 10px;
                    border-radius: 5px;
                }
                .menu-item:hover {
                    background: rgba(255, 102, 179, 0.2);
                }
            </style>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="sidebar-header">
                <img src="https://i.ibb.co/ks5CNrDn/IMG-9256.jpg" alt="Paloma">
                <h3 style="color: #ff66b3; margin-top: 10px;">Paloma Premium</h3>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown("### 🌟 Menu Exclusivo")
            
            menu_options = {
                "💋 Início": "home",
                "📸 Galeria Privada": "gallery",
                "💌 Mensagens": "messages",
                "🎁 Ofertas Especiais": "offers"
            }
            
            for option, page in menu_options.items():
                if st.button(option, use_container_width=True, key=f"menu_{page}"):
                    st.session_state.current_page = page
                    st.rerun()
            
            st.markdown("---")
            st.markdown("### 🔒 Sua Conta")
            
            status = "VIP Ativo" if random.random() > 0.2 else "Conteúdo Básico"
            status_color = "#2ecc71" if status == "VIP Ativo" else "#f39c12"
            
            st.markdown(f"""
            <div style="
                background: rgba(255, 20, 147, 0.1); 
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
            st.markdown("### 💎 Upgrade VIP")
            st.markdown("""
            <div class="vip-badge">
                <p style="margin: 0 0 10px; font-weight: bold;">Acesso completo por apenas</p>
                <p style="margin: 0; font-size: 1.5em; font-weight: bold;">R$ 29,90/mês</p>
                <p style="margin: 10px 0 0; font-size: 0.8em;">Cancele quando quiser</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🔼 Tornar-se VIP", use_container_width=True, type="primary"):
                st.session_state.show_vip_offer = True
            
            st.markdown("---")
            st.markdown("""
            <div style="text-align: center; font-size: 0.7em; color: #888;">
                <p>© 2024 Paloma Premium</p>
                <p>🔞 Conteúdo para maiores de 18 anos</p>
            </div>
            """, unsafe_allow_html=True)

    @staticmethod
    def show_gallery_page(conn):
        st.title("📸 Galeria Privada")
        st.markdown("""
        <div style="
            background: rgba(255, 20, 147, 0.1);
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
        ">
            <p style="margin: 0;">Conteúdo exclusivo para assinantes VIP</p>
        </div>
        """, unsafe_allow_html=True)
        
        cols = st.columns(3)
        gallery_images = [
            "https://i.ibb.co/zhNZL4FF/IMG-9198.jpg",
            "https://i.ibb.co/Y4B7CbXf/IMG-9202.jpg",
            "https://i.ibb.co/Fqf0gPPq/IMG-9199.jpg"
        ]
        
        for idx, col in enumerate(cols):
            with col:
                st.image(
                    gallery_images[idx],
                    use_container_width=True,
                    caption=f"Preview {idx+1}"
                )
                st.markdown(f"""
                <div style="
                    text-align: center;
                    font-size: 0.8em;
                    color: #ff66b3;
                    margin-top: -10px;
                ">
                    🔒 Conteúdo bloqueado
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown(f"""
        <div style="text-align: center;">
            <h4>🔓 Desbloqueie acesso completo</h4>
            <p>Assine o plano VIP para ver todos os conteúdos</p>
            <a href="{Config.VIP_LINK}" style="
                background: linear-gradient(45deg, #ff1493, #9400d3);
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                text-decoration: none;
                display: inline-block;
                margin-top: 10px;
            ">
                Tornar-se VIP
            </a>
        </div>
        """, unsafe_allow_html=True)
        
        # ATUALIZAÇÃO002 - Botão Voltar ao Chat
        UiService.back_to_chat_button()

    @staticmethod
    def enhanced_chat_ui(conn):
        st.markdown("""
        <style>
            .chat-header {
                background: linear-gradient(90deg, #ff66b3, #ff1493);
                color: white;
                padding: 15px;
                border-radius: 10px;
                margin-bottom: 20px;
                text-align: center;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }
            .stAudio {
                border-radius: 20px !important;
                background: rgba(255, 102, 179, 0.1) !important;
                padding: 10px !important;
                margin: 10px 0 !important;
            }
            audio::-webkit-media-controls-panel {
                background: linear-gradient(45deg, #ff66b3, #ff1493) !important;
            }
        </style>
        """, unsafe_allow_html=True)
        
        # ATUALIZAÇÃO001 - Botões de Atalho
        UiService.chat_shortcuts()
        
        st.markdown(f"""
        <div class="chat-header">
            <h2 style="margin:0; font-size:1.5em; display:inline-block;">💬 Chat Privado com Paloma</h2>
        </div>
        """, unsafe_allow_html=True)
        
        st.sidebar.markdown(f"""
        <div style="
            background: rgba(255, 20, 147, 0.1);
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
        
        st.markdown("""
        <div style="
            text-align: center;
            margin-top: 20px;
            padding: 10px;
            font-size: 0.8em;
            color: #888;
        ">
            <p>🔒 Conversa privada • ✉️ Suas mensagens são confidenciais</p>
        </div>
        """, unsafe_allow_html=True)

# ======================
# SERVIÇOS DE CHAT
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
    def validate_input(user_input):
        return Security.sanitize_input(user_input)

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
            st.session_state.audio_sent = True
            st.rerun()
        
        user_input = st.chat_input("Oi amor, como posso te ajudar hoje? 💭", key="chat_input")
        
        if user_input:
            cleaned_input = ChatService.validate_input(user_input)
            
            if st.session_state.request_count >= Config.MAX_REQUESTS_PER_SESSION:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "Estou ficando cansada, amor... Que tal continuarmos mais tarde? 💋"
                })
                st.rerun()
                return
            
            st.session_state.messages.append({
                "role": "user",
                "content": cleaned_input
            })
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
                st.markdown(f"""
                <div style="
                    background: linear-gradient(45deg, #ff66b3, #ff1493);
                    color: white;
                    padding: 12px;
                    border-radius: 18px 18px 18px 0;
                    margin: 5px 0;
                ">
                    {resposta} {random.choice(["💋", "🔥", "😈"])}
                </div>
                """, unsafe_allow_html=True)
            
            st.session_state.messages.append({
                "role": "assistant",
                "content": resposta
            })
            
            st.markdown("""
            <script>
                window.scrollTo(0, document.body.scrollHeight);
            </script>
            """, unsafe_allow_html=True)

# ======================
# APLICAÇÃO PRINCIPAL
# ======================
def main():
    st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1e0033 0%, #3c0066 100%) !important;
            border-right: 1px solid #ff66b3 !important;
        }
        .stButton button {
            background: rgba(255, 20, 147, 0.2) !important;
            color: white !important;
            border: 1px solid #ff66b3 !important;
            transition: all 0.3s !important;
        }
        .stButton button:hover {
            background: rgba(255, 20, 147, 0.4) !important;
            transform: translateY(-2px) !important;
        }
        [data-testid="stChatInput"] {
            background: rgba(255, 102, 179, 0.1) !important;
            border: 1px solid #ff66b3 !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.title("💋 Paloma - Conteúdo Exclusivo")
    conn = DatabaseService.init_db()
    
    ChatService.initialize_session()
    if not st.session_state.age_verified:
        UiService.age_verification()
        st.stop()
    
    UiService.setup_sidebar()
    
    if not st.session_state.connection_complete:
        UiService.show_call_effect()
        st.session_state.connection_complete = True
        st.rerun()
    
    if not st.session_state.chat_started:
        col1, col2, col3 = st.columns([1,3,1])
        with col2:
            st.markdown("""
            <div style="text-align: center; margin: 50px 0;">
                <img src="https://i.ibb.co/ks5CNrDn/IMG-9256.jpg" width="120" style="border-radius: 50%; border: 3px solid #ff66b3;">
                <h2 style="color: #ff66b3; margin-top: 15px;">Paloma</h2>
                <p style="font-size: 1.1em;">Estou pronta para você, amor...</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("💬 Iniciar Conversa", type="primary", use_container_width=True):
                st.session_state.update({
                    "chat_started": True,
                    "current_page": "chat",
                    "audio_sent": False
                })
                st.rerun()
        st.stop()
    
    if st.session_state.current_page == "home":
        NewPages.show_home_page()
    elif st.session_state.current_page == "gallery":
        UiService.show_gallery_page(conn)
    elif st.session_state.current_page == "offers":
        NewPages.show_offers_page()
    elif st.session_state.get("show_vip_offer", False):
        st.warning("Página VIP em desenvolvimento")
        if st.button("← Voltar ao chat"):
            st.session_state.show_vip_offer = False
            st.rerun()
    else:
        UiService.enhanced_chat_ui(conn)
    
    conn.close()

if __name__ == "__main__":
    main()
