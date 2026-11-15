import streamlit as st
import pandas as pd
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from supabase import create_client, Client

# Configuração da Página
st.set_page_config(
    page_title="LATAM Cargo | WMS e Logística de Insumos",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS refinada idêntica ao design corporativo desejado
st.markdown("""
    <style>
        .main { background-color: #121824; color: #F8FAFC; }
        .stButton>button {
            background-color: #E2001A !important;
            color: #FFFFFF !important;
            border-radius: 8px !important;
            font-weight: 700 !important;
            height: 48px !important;
            border: none !important;
            width: 100% !important;
            transition: background 0.2s;
        }
        .stButton>button:hover {
            background-color: #C50017 !important;
        }
        div[data-testid="stSidebar"] div.row-widget.stRadio div[role="radiogroup"] label div:first-child {
            display: none !important;
        }
        div[data-testid="stSidebar"] div.row-widget.stRadio div[role="radiogroup"] label {
            background-color: #1E293B !important;
            padding: 12px 16px !important;
            border-radius: 8px !important;
            margin-bottom: 8px !important;
            border: 1px solid #334155 !important;
            color: #F8FAFC !important;
            font-weight: 600 !important;
        }
        div[data-testid="stSidebar"] div.row-widget.stRadio div[role="radiogroup"] label:hover {
            background-color: rgba(226, 0, 26, 0.15) !important;
            border-color: #E2001A !important;
            color: #FFFFFF !important;
        }
        div[data-testid="stSidebar"] .stRadio label p {
            font-size: 15px !important;
            font-family: 'Segoe UI', sans-serif !important;
        }
    </style>
""", unsafe_allow_html=True)

# Conexão com o Supabase via Secrets
@st.cache_resource
def init_supabase():
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

supabase: Client = init_supabase()

def buscar_usuarios():
    try:
        response = supabase.table("usuarios").select("*").execute()
        usuarios_dict = {u["bp"]: u for u in response.data}
        if not usuarios_dict:
            # Usuário padrão caso a tabela esteja totalmente vazia
            return {
                "4872423": {"nome": "Isadora Sousa Lima", "base": "FOR - Fortaleza", "senha": "123", "email": "isadora@latam.com"}
            }
        return usuarios_dict
    except Exception:
        return {
            "4872423": {"nome": "Isadora Sousa Lima", "base": "FOR - Fortaleza", "senha": "123", "email": "isadora@latam.com"}
        }

def salvar_usuario_supabase(bp, dados):
    try:
        supabase.table("usuarios").upsert({"bp": bp, **dados}).execute()
    except Exception as e:
        st.error(f"Erro ao salvar usuário no Supabase: {e}")

def buscar_pedidos():
    try:
        response = supabase.table("pedidos").select("*").execute()
        return response.data
    except Exception:
        return []

def salvar_pedido_supabase(pedido):
    try:
        supabase.table("pedidos").insert(pedido).execute()
    except Exception as e:
        st.error(f"Erro ao salvar pedido no Supabase: {e}")

def atualizar_pedido_supabase(pedido_id, novos_itens, novo_status):
    try:
        supabase.table("pedidos").update({"itens": novos_itens, "status": novo_status}).eq("id", pedido_id).execute()
    except Exception as e:
        st.error(f"Erro ao atualizar pedido: {e}")

# Função para Disparo Real de E-mail via SMTP (Recuperação de Senha)
def enviar_email_smtp(destinatario_email, nome_usuario, nova_senha):
    try:
        servidor_smtp = "smtp.gmail.com"
        porta_smtp = 587
        remetente_email = st.secrets["EMAIL_USUARIO"]
        senha_remetente = st.secrets["EMAIL_SENHA"]
        
        msg = MIMEMultipart()
        msg['From'] = remetente_email
        msg['To'] = destinatario_email
        msg['Subject'] = "🔒 Recuperação de Senha - LATAM WMS Insumos"
        
        corpo = f"""
        Olá, {nome_usuario},
        
        Recebemos uma solicitação de redefinição de senha para o seu acesso ao WMS de Insumos da LATAM Cargo.
        
        Sua nova senha temporária cadastrada é: {nova_senha}
        
        Atenciosamente,
        Equipe de Logística / WMS LATAM Cargo
        """
        msg.attach(MIMEText(corpo, 'plain'))
        
        server = smtplib.SMTP(servidor_smtp, porta_smtp)
        server.starttls()
        server.login(remetente_email, senha_remetente)
        server.sendmail(remetente_email, destinatario_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Erro ao disparar e-mail SMTP: {e}")
        return False

# Catálogo Oficial de Insumos LATAM Cargo
CATALOGO_ITENS = [
    {"pn": "100000000200041651", "descricao": "MANTA PLASTICA ABSORVENTE 1800 X 2400MM", "unidade": "Unidade", "preco": 3890.00},
    {"pn": "100000000200041665", "descricao": "MANTA PLASTICA ABSORVENTE 1400 X 2400MM", "unidade": "Unidade", "preco": 3400.00},
    {"pn": "100000000200023681", "descricao": "COPO PAPEL DESCART 180ML BCA NAZAPACK", "unidade": "Unidade", "preco": 0.30},
    {"pn": "100000000200005306", "descricao": "ETIQUETA POSICAO 11*13CM AUTOADESIVO", "unidade": "Rolo", "preco": 19.86},
    {"pn": "10042927", "descricao": "ETIQUETA PERECIVEIS", "unidade": "Unidade", "preco": 0.19},
    {"pn": "10043080", "descricao": "ETIQUETA RAIO-X - PAPEL ROLO", "unidade": "Unidade", "preco": 500.00},
    {"pn": "10042944", "descricao": "SACO LIXO AMARELO 100L PEBD RECICLADO 75cm x 105cm", "unidade": "Unidade", "preco": 0.30},
    {"pn": "10042940", "descricao": "SACO LIXO AZUL 100L PEBD RECICLADO 75cm x 105cm", "unidade": "Unidade", "preco": 0.25},
    {"pn": "10042946", "descricao": "SACO LIXO VERDE 100L PEBD RECICLADO 75cm x 105cm", "unidade": "Unidade", "preco": 0.30},
    {"pn": "10042942", "descricao": "SACO LIXO VERMELHO 100L PEBD RECICLADO 75cm x 105cm", "unidade": "Unidade", "preco": 0.28},
    {"pn": "10043265", "descricao": "SACO LIXO AMARELO 200L PEBD RECICLADO 95cm x 1,10cm", "unidade": "Unidade", "preco": 0.35},
    {"pn": "10043266", "descricao": "SACO LIXO AZUL 200L PEBD RECICLADO 95cm x 110cm", "unidade": "Unidade", "preco": 0.38},
    {"pn": "10043268", "descricao": "SACO LIXO PRETO 200L PEBD RECICLADO 95cm x 110cm", "unidade": "Unidade", "preco": 0.37},
    {"pn": "10043269", "descricao": "SACO LIXO VERMELHO 200L PEBD RECICLADO 95cm x 110cm", "unidade": "Unidade", "preco": 0.38},
    {"pn": "10050462", "descricao": "ETIQUETA ADESIVA EMBORRACHADA", "unidade": "Rolo", "preco": 36.00},
    {"pn": "10043603", "descricao": "ENVELOPE CONHECIMENTO AEREO TRANSPARENTE 25x19", "unidade": "Unidade", "preco": 0.19},
    {"pn": "10043629", "descricao": "BOBINA PLASTICA PARA PALETIZAÇÃO", "unidade": "Rolo", "preco": 229.50},
    {"pn": "10043477", "descricao": "LACRE P/ SACO COLETOR DE CARGA BRANCO", "unidade": "Unidade", "preco": 0.50},
    {"pn": "10053503", "descricao": "PAPEL SULFITE A4 COPIMAX", "unidade": "Resma", "preco": 26.32},
    {"pn": "10042984", "descricao": "FITA 48X50 HOT MELT 30 GRAMAS", "unidade": "Unidade", "preco": 4.43},
    {"pn": "100000000200041300", "descricao": "FILM PLASTICO ROLO 500MMX0,25MM", "unidade": "Unidade", "preco": 47.80},
    {"pn": "100000000200020082", "descricao": "ALCOOL GEL 70% 500ML", "unidade": "Unidade", "preco": 8.32},
    {"pn": "10043628", "descricao": "BOX 2", "unidade": "Unidade", "preco": 7.76},
    {"pn": "10043517", "descricao": "CAIXA PARA ARQUIVO - PESO MAX 5 KILOS", "unidade": "Unidade", "preco": 7.41},
    {"pn": "10043611", "descricao": "BOX 1", "unidade": "Unidade", "preco": 7.12},
    {"pn": "10043376", "descricao": "BOX 3", "unidade": "Unidade", "preco": 15.31},
    {"pn": "10043639", "descricao": "CONTAINER BOX", "unidade": "Unidade", "preco": 21.61},
    {"pn": "10039100", "descricao": "CALCADO SEGURANCA TIPO BOTINA PRETA - TAM 35", "unidade": "PAR", "preco": 91.16},
    {"pn": "10039101", "descricao": "CALCADO SEGURANCA TIPO BOTINA PRETA - TAM 36", "unidade": "PAR", "preco": 91.16},
    {"pn": "10039102", "descricao": "CALCADO SEGURANCA TIPO BOTINA PRETA - TAM 37", "unidade": "PAR", "preco": 91.16},
    {"pn": "10039103", "descricao": "CALCADO SEGURANCA TIPO BOTINA PRETA - TAM 38", "unidade": "PAR", "preco": 91.16},
    {"pn": "10039104", "descricao": "CALCADO SEGURANCA TIPO BOTINA PRETA - TAM 39", "unidade": "PAR", "preco": 91.13},
    {"pn": "10039105", "descricao": "CALCADO SEGURANCA TIPO BOTINA PRETA - TAM 40", "unidade": "PAR", "preco": 91.44},
    {"pn": "10039106", "descricao": "CALCADO SEGURANCA TIPO BOTINA PRETA - TAM 41", "unidade": "PAR", "preco": 91.30},
    {"pn": "10039107", "descricao": "CALCADO SEGURANCA TIPO BOTINA PRETA - TAM 42", "unidade": "PAR", "preco": 92.00},
    {"pn": "10039131", "descricao": "CALCADO SEGURANCA ESPECIAL - TAM 34", "unidade": "PAR", "preco": 105.12},
    {"pn": "10039133", "descricao": "CALCADO SEGURANCA ESPECIAL - TAM 36", "unidade": "PAR", "preco": 104.94},
    {"pn": "10039135", "descricao": "CALCADO SEGURANCA ESPECIAL - TAM 38", "unidade": "PAR", "preco": 104.94},
    {"pn": "10039137", "descricao": "CALCADO SEGURANCA ESPECIAL - TAM 40", "unidade": "PAR", "preco": 104.93},
    {"pn": "10039139", "descricao": "CALCADO SEGURANCA ESPECIAL - TAM 42", "unidade": "PAR", "preco": 104.94},
    {"pn": "10035280", "descricao": "CALCO 150*250*150MM BO KIT DUPLO", "unidade": "Unidade", "preco": 330.00},
    {"pn": "10042939", "descricao": "ENVELOPE AWB TRANSPARENTE 1 IMPRESSAO", "unidade": "Unidade", "preco": 0.30},
    {"pn": "10043644", "descricao": "ENVELOPE AWB TRANSPARENTE IMPR. VERMELHO 25x34", "unidade": "Unidade", "preco": 0.60},
    {"pn": "100000000010000277", "descricao": "ETIQUETA CONEXAO 14,5*4,5CM COUCHE", "unidade": "Unidade", "preco": 0.13},
    {"pn": "10042902", "descricao": "LAMINA P/ ESTILETE LARGO", "unidade": "Unidade", "preco": 1.57},
    {"pn": "10043556", "descricao": "LUVA DE SEGURANCA MALHA ALGODAO REVESTIDA (TAM 10)", "unidade": "PAR", "preco": 6.68},
    {"pn": "10043559", "descricao": "LUVA DE SEGURANCA MALHA ALGODAO REVESTIDA (TAM 7)", "unidade": "PAR", "preco": 7.22},
    {"pn": "10043558", "descricao": "LUVA DE SEGURANCA MALHA ALGODAO REVESTIDA (TAM 8)", "unidade": "PAR", "preco": 7.37},
    {"pn": "10043557", "descricao": "LUVA DE SEGURANCA MALHA ALGODAO REVESTIDA (TAM 9)", "unidade": "PAR", "preco": 7.21},
    {"pn": "10040975", "descricao": "TRENA 8M*25MM ACO PLAST", "unidade": "Unidade", "preco": 64.34}
]

BASES_LATAM = [
    "AJU - Aracaju", "BEL - Belém", "BOG - Bogotá (Colômbia)", "BSB - Brasília",
    "BVB - Boa Vista", "CGB - Cuiabá", "CGH - São Paulo (Congonhas)", "CGR - Campo Grande",
    "CNF - Belo Horizonte (Confins)", "CWB - Curitiba", "FLN - Florianópolis", "FOR - Fortaleza",
    "GIG - Rio de Janeiro (Galeão)", "GRU - Guarulhos (Hub Principal)", "GYN - Goiânia",
    "IGU - Foz do Iguaçu", "JFK - Nova York (EUA)", "JPA - João Pessoa", "LIM - Lima (Peru)",
    "MAD - Madri (Espanha)", "MAO - Manaus", "MCZ - Maceió", "MCP - Macapá", "MIA - Miami (EUA)",
    "NAT - Natal", "PMW - Palmas", "POA - Porto Alegre", "PVH - Porto Velho", "RBR - Rio Branco",
    "SCL - Santiago (Chile)", "SLZ - São Luís", "SSA - Salvador", "THE - Teresina",
    "VCP - Campinas (Viracopos)", "VIX - Vitória"
]

if 'usuario_logado' not in st.session_state:
    st.session_state.usuario_logado = None

usuarios_db = buscar_usuarios()
pedidos_db = buscar_pedidos()

# TELA DE AUTENTICAÇÃO COM CARD ARREDONDADO
if not st.session_state.usuario_logado:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    
    with col2:
        with st.container(border=True):
            st.markdown("""
                <div style="text-align: center; margin-bottom: 20px;">
                    <h1 style="font-size: 28px; font-weight: 800; color: #FFFFFF; margin: 0;">LATAM <span style="color: #E2001A;">Cargo</span></h1>
                    <p style="font-size: 13px; color: #94A3B8; margin-top: 6px;">WMS e Logística de Insumos - Acesso Corporativo</p>
                </div>
            """, unsafe_allow_html=True)
            
            tab1, tab2, tab3 = st.tabs(["Entrar", "Cadastrar BP", "Esqueci a Senha"])
            
            with tab1:
                st.markdown("<br>", unsafe_allow_html=True)
                bp_input = st.text_input("BP (Código Funcional)", key="login_bp")
                senha_input = st.text_input("Senha Pessoal", type="password", key="login_senha")
                
                if st.button("Acessar Sistema", type="primary"):
                    if bp_input in usuarios_db and usuarios_db[bp_input]["senha"] == senha_input:
                        st.session_state.usuario_logado = {"bp": bp_input, **usuarios_db[bp_input]}
                        st.rerun()
                    else:
                        st.error("⚠️ BP ou senha incorretos.")

            with tab2:
                st.markdown("<br>", unsafe_allow_html=True)
                c_nome = st.text_input("Nome Completo")
                c_bp = st.text_input("BP (Código Funcional)", key="cad_bp")
                c_email = st.text_input("E-mail Corporativo (@latam.com)", key="cad_email")
                c_base = st.selectbox("Base Operacional", BASES_LATAM)
                c_senha = st.text_input("Criar Senha Pessoal", type="password", key="cad_senha")
                
                if st.button("Concluir Cadastro", key="btn_cad"):
                    if not c_nome or not c_bp or not c_email or not c_senha:
                        st.warning("⚠️ Preencha todos os campos.")
                    elif c_bp in usuarios_db:
                        st.error("⚠️ Este BP já está cadastrado.")
                    else:
                        novo_usuario = {"nome": c_nome, "base": c_base, "senha": c_senha, "email": c_email}
                        salvar_usuario_supabase(c_bp, novo_usuario)
                        st.success("🎉 Cadastro realizado e salvo no Supabase com sucesso! Faça login na aba ao lado.")

            with tab3:
                st.markdown("<br>", unsafe_allow_html=True)
                r_bp = st.text_input("Informe seu BP", key="rec_bp")
                r_email = st.text_input("Informe seu E-mail Corporativo", key="rec_email")
                r_novasenha = st.text_input("Definir Nova Senha Pessoal", type="password", key="rec_senha")
                
                if st.button("Enviar E-mail de Recuperação", key="btn_rec"):
                    if r_bp in usuarios_db and usuarios_db[r_bp]["email"] == r_email:
                        usuarios_db[r_bp]["senha"] = r_novasenha
                        salvar_usuario_supabase(r_bp, usuarios_db[r_bp])
                        sucesso_envio = enviar_email_smtp(r_email, usuarios_db[r_bp]['nome'], r_novasenha)
                        
                        if sucesso_envio:
                            st.success("🎉 Senha alterada e e-mail disparado com sucesso para o seu corporativo!")
                        else:
                            st.warning("⚠️ Senha alterada, mas houve falha no envio do SMTP.")
                    else:
                        st.error("⚠️ BP ou e-mail não conferem com os registros.")

else:
    # APLICAÇÃO PRINCIPAL COM CABEÇALHO ROXO E MENU LIMPO
    user = st.session_state.usuario_logado
    
    st.sidebar.markdown("""
        <div style="padding: 10px 0; border-bottom: 1px solid #334155; margin-bottom: 20px;">
            <h2 style="font-size: 20px; font-weight: 800; color: #FFFFFF; margin: 0;">LATAM <span style="color: #E2001A;">Cargo</span></h2>
            <p style="font-size: 12px; color: #94A3B8; margin-top: 4px;">WMS & Logística</p>
        </div>
    """, unsafe_allow_html=True)
    
    menu = st.sidebar.radio("Menu de Navegação", [
        "Painel de Gestão", 
        "Solicitar Insumos", 
        "Conferência e Ajustes", 
        "Histórico Geral", 
        "Sugestões e Erros"
    ], label_visibility="collapsed")
    
    st.sidebar.markdown("---")
    if st.sidebar.button("Sair do Sistema", type="secondary"):
        st.session_state.usuario_logado = None
        st.rerun()

    pedidos_base = [p for p in pedidos_db if p['base'] == user['base']]

    if menu == "Painel de Gestão":
        st.markdown(f"""
            <div style="background: linear-gradient(135deg, #2A0052 0%, #1A0033 100%); padding: 25px 30px; border-radius: 16px; border: 1px solid #4C1D95; box-shadow: 0 8px 20px rgba(0,0,0,0.4); display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px;">
                <div>
                    <h1 style="color: #FFFFFF; font-size: 28px; font-weight: 800; margin: 0;">Painel WMS - Base {user['base'].split(' - ')[0]}</h1>
                    <p style="color: #C4B5FD; font-size: 14px; margin: 5px 0 0 0;">Visão geral de operações e solicitações de insumos</p>
                </div>
                <div style="text-align: right;">
                    <span style="color: #FFFFFF; font-size: 16px; font-weight: 700; display: block;">{user['nome']}</span>
                    <span style="color: #A78BFA; font-size: 13px;">Base: {user['base']} (BP: {user['bp']})</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        pendentes_count = len([p for p in pedidos_base if p['status'] == "Pendente"])
        recebidos_count = len([p for p in pedidos_base if p['status'] == "Recebido"])
        
        with col1:
            with st.container(border=True):
                st.markdown("<span style='font-size: 12px; font-weight: 700; color: #94A3B8; letter-spacing: 1px;'>PEDIDOS PENDENTES</span>", unsafe_allow_html=True)
                st.markdown(f"<h3 style='font-size: 38px; font-weight: 800; color: #FFFFFF; margin-top: 5px;'>{pendentes_count}</h3>", unsafe_allow_html=True)
            
        with col2:
            with st.container(border=True):
                st.markdown("<span style='font-size: 12px; font-weight: 700; color: #38A169; letter-spacing: 1px;'>PEDIDOS APROVADOS / RECEBIDOS</span>", unsafe_allow_html=True)
                st.markdown(f"<h3 style='font-size: 38px; font-weight: 800; color: #FFFFFF; margin-top: 5px;'>{recebidos_count}</h3>", unsafe_allow_html=True)
            
        st.markdown("### Histórico de Solicitações da Base")
        with st.container(border=True):
            if pedidos_base:
                df_base = pd.DataFrame(pedidos_base)[['id', 'data', 'solicitante', 'valorTotal', 'status']]
                df_base.columns = ["ID PEDIDO", "DATA", "SOLICITANTE", "VALOR TOTAL (R$)", "STATUS"]
                st.dataframe(df_base, use_container_width=True)
            else:
                st.info("Nenhum pedido registado para esta base ainda.")

    elif menu == "Solicitar Insumos":
        st.title("Nova Requisição de Materiais")
        st.markdown("Selecione as quantidades desejadas para os itens abaixo:")
        
        with st.container(border=True):
            quantidades = {}
            for idx, item in enumerate(CATALOGO_ITENS):
                col1, col2, col3, col4 = st.columns([2, 4, 1, 1])
                with col1:
                    st.text(item['pn'])
                with col2:
                    st.text(item['descricao'])
                with col3:
                    st.text(f"R$ {item['preco']:.2f}")
                with col4:
                    quantidades[item['pn']] = st.number_input("Qtd", min_value=0, value=0, key=f"qtd_{idx}", label_visibility="collapsed")
                    
            total_geral = sum(q * next(i['preco'] for i in CATALOGO_ITENS if i['pn'] == pn) for pn, q in quantidades.items() if q > 0)
            st.markdown(f"### Valor Total Estimado: R$ {total_geral:,.2f}")
            
            if st.button("SALVAR E REGISTRAR PEDIDO", type="primary"):
                itens_solicitados = []
                for item in CATALOGO_ITENS:
                    qtd = quantidades[item['pn']]
                    if qtd > 0:
                        itens_solicitados.append({**item, "quantidade": qtd})
                        
                if not itens_solicitados:
                    st.warning("⚠️ Insira ao menos uma quantidade desejada.")
                else:
                    novo_pedido = {
                        "id": f"PED-{user['base'].split(' - ')[0]}-{str(datetime.now().timestamp())[-4:]}",
                        "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "base": user['base'],
                        "solicitante": user['nome'],
                        "valorTotal": total_geral,
                        "status": "Pendente",
                        "itens": itens_solicitados
                    }
                    salvar_pedido_supabase(novo_pedido)
                    st.success(f"🎉 Pedido {novo_pedido['id']} registado no Supabase com sucesso!")
                    st.rerun()

    elif menu == "Conferência e Ajustes":
        st.title("Conferência, Ajustes e Confirmação de Recebimento")
        st.markdown("Ajuste quantidades ou nomes divergentes conforme o que chegou fisicamente na base, confirme e baixe o CSV final.")
        
        ids_pedidos = [p['id'] for p in pedidos_base]
        if not ids_pedidos:
            st.info("Nenhum pedido disponível para conferência nesta base.")
        else:
            with st.container(border=True):
                pedido_selecionado_id = st.selectbox("Selecione o Pedido para Conferência", ids_pedidos)
                pedido = next(p for p in pedidos_base if p['id'] == pedido_selecionado_id)
                
                st.markdown(f"**Status Atual:** `{pedido['status']}`")
                
                df_itens = pd.DataFrame(pedido['itens'])
                edited_df = st.data_editor(df_itens, num_rows="dynamic", use_container_width=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Salvar Ajustes & Confirmar Recebimento", type="primary"):
                        novos_itens = edited_df.to_dict(orient="records")
                        atualizar_pedido_supabase(pedido['id'], novos_itens, "Recebido")
                        st.success(f"🎉 Pedido {pedido['id']} confirmado no Supabase!")
                        st.rerun()
                        
                with col2:
                    csv_linhas = ["Item;Quantidade"]
                    for i in pedido['itens']:
                        csv_linhas.append(f"{i['pn']} - {i['descricao']};{i['quantidade']}")
                    csv_data = "\n".join(csv_linhas)
                    
                    st.download_button(
                        label="Baixar Planilha Insumos (.csv) LATAM",
                        data=csv_data,
                        file_name=f"Insumos_Conferidos_{pedido['base'].split(' - ')[0]}_{pedido['id']}.csv",
                        mime="text/csv"
                    )

    elif menu == "Histórico Geral":
        st.title("Auditoria e Histórico Geral")
        st.markdown("Consolidado de todas as solicitações e conferências da rede LATAM Cargo.")
        
        with st.container(border=True):
            if pedidos_db:
                df_geral = pd.DataFrame(pedidos_db)[['id', 'data', 'base', 'solicitante', 'valorTotal', 'status']]
                df_geral.columns = ["ID", "DATA", "BASE", "SOLICITANTE", "VALOR TOTAL (R$)", "STATUS"]
                st.dataframe(df_geral, use_container_width=True)
            else:
                st.info("Nenhum pedido registado no sistema global.")

    elif menu == "Sugestões e Erros":
        st.title("Central de Feedback, Sugestões e Erros")
        st.markdown("Encontrou algum problema no sistema ou tem uma ideia de melhoria? Envie uma mensagem direta para a equipe de desenvolvimento.")
        
        with st.container(border=True):
            formspree_html = f"""
            <form action="https://formspree.io/f/mrenybwd" method="POST" style="color: #F8FAFC;">
                <input type="hidden" name="Colaborador" value="{user['nome']} (BP: {user['bp']})">
                <input type="hidden" name="Base" value="{user['base']}">
                
                <div style="margin-bottom: 20px;">
                    <label style="display: block; font-weight: 700; margin-bottom: 8px; color: #94A3B8;">TIPO DE MENSAGEM</label>
                    <select name="Tipo" style="width: 100%; padding: 12px; border-radius: 8px; background: #0F172A; color: #FFF; border: 1px solid #334155;">
                        <option value="Sugestao">💡 Sugestão de Melhoria</option>
                        <option value="Erro">🛠️ Reportar Erro / Bug</option>
                        <option value="Outro">📌 Outro Assunto</option>
                    </select>
                </div>
                
                <div style="margin-bottom: 20px;">
                    <label style="display: block; font-weight: 700; margin-bottom: 8px; color: #94A3B8;">DETALHES DA MENSAGEM</label>
                    <textarea name="Mensagem" rows="5" placeholder="Descreva aqui sua sugestão ou o erro encontrado..." style="width: 100%; padding: 12px; border-radius: 8px; background: #0F172A; color: #FFF; border: 1px solid #334155;" required></textarea>
                </div>
                
                <button type="submit" style="background: #E2001A; color: white; padding: 14px 20px; border: none; border-radius: 8px; font-weight: 700; width: 100%; cursor: pointer;">Enviar Mensagem 🚀</button>
            </form>
            """
            st.markdown(formspree_html, unsafe_allow_html=True)