import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client

# Configuração da Página
st.set_page_config(
    page_title="LATAM Cargo | WMS e Logística de Insumos",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Conexão com o Supabase com limpeza de espaços e validação rigorosa
@st.cache_resource
def init_supabase():
    try:
        url = st.secrets.get("SUPABASE_URL", "").strip()
        key = st.secrets.get("SUPABASE_KEY", "").strip()
        
        if not url or not key:
            st.error("⚠️ As chaves do Supabase não foram encontradas nos Secrets.")
            return None
            
        if not url.startswith("https://"):
            url = f"https://{url}"
            
        return create_client(url, key)
    except Exception as e:
        st.error(f"Erro crítico ao inicializar o Supabase: {e}")
        return None

supabase = init_supabase()

# Estilização CSS refinada (design corporativo com gradiente roxo e fontes grandes no menu)
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
        div[data-testid="stSidebar"] div.row-widget.stRadio div[role="radiogroup"] {
            width: 100% !important;
        }
        div[data-testid="stSidebar"] div.row-widget.stRadio div[role="radiogroup"] label {
            background: linear-gradient(135deg, #1E1B4B 0%, #0F172A 100%) !important;
            padding: 16px 20px !important;
            border-radius: 12px !important;
            margin-bottom: 12px !important;
            border: 1px solid #7C3AED !important;
            box-shadow: 0 4px 12px rgba(124, 58, 237, 0.15) !important;
            color: #F8FAFC !important;
            font-weight: 700 !important;
            width: 100% !important;
            display: flex !important;
            align-items: center !important;
            transition: all 0.2s ease-in-out;
        }
        div[data-testid="stSidebar"] div.row-widget.stRadio div[role="radiogroup"] label:hover {
            background: linear-gradient(135deg, #2E1065 0%, #1E1B4B 100%) !important;
            border-color: #A78BFA !important;
            box-shadow: 0 6px 16px rgba(167, 139, 250, 0.3) !important;
        }
        div[data-testid="stSidebar"] .stRadio label p {
            font-size: 17px !important;
            font-family: 'Segoe UI', sans-serif !important;
            letter-spacing: 0.3px !important;
            width: 100% !important;
        }
    </style>
""", unsafe_allow_html=True)

# Catálogo Oficial de Insumos LATAM Cargo
CATALOGO_ITENS = [
    {"pn": "100000000200041651", "descricao": "MANTA PLASTICA ABSORVENTE 1800 X 2400MM", "unidade": "Unidade", "preco": 38.90},
    {"pn": "100000000200041665", "descricao": "MANTA PLASTICA ABSORVENTE 1400 X 2400MM", "unidade": "Unidade", "preco": 34.00},
    {"pn": "100000000200023681", "descricao": "COPO PAPEL DESCART 180ML BCA NAZAPACK", "unidade": "Unidade", "preco": 0.30},
    {"pn": "100000000200005306", "descricao": "ETIQUETA POSICAO 11*13CM AUTOADESIVO", "unidade": "Rolo", "preco": 92.72},
    {"pn": "10042927", "descricao": "ETIQUETA PERECIVEIS", "unidade": "Unidade", "preco": 0.19},
    {"pn": "10043080", "descricao": "ETIQUETA RAIO-X - PAPEL ROLO", "unidade": "Unidade", "preco": 50.00},
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
    {"pn": "10042939", "descricao": "ENVELOPE AWB TRANSPARENTE 1 IMPRESSAO", "unidade": "Unidade", "preco": 0.15},
    {"pn": "10043644", "descricao": "ENVELOPE AWB TRANSPARENTE IMPR. VERMELHO 25x34", "unidade": "Unidade", "preco": 0.24},
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

# Função para carregar pedidos do Supabase (tabela: pedidos_wm)
def carregar_pedidos():
    if supabase:
        try:
            response = supabase.table("pedidos_wm").select("*").execute()
            return response.data if response.data else []
        except Exception:
            return []
    return []

# MENU LATERAL
st.sidebar.markdown("""
    <div style="padding: 10px 0; border-bottom: 1px solid #7C3AED; margin-bottom: 20px;">
        <h2 style="font-size: 22px; font-weight: 800; color: #FFFFFF; margin: 0;">LATAM <span style="color: #E2001A;">Cargo</span></h2>
        <p style="font-size: 13px; color: #A78BFA; margin-top: 4px;">WMS & Logística</p>
    </div>
""", unsafe_allow_html=True)

menu = st.sidebar.radio("Menu de Navegação", [
    "Painel de Gestão", 
    "Solicitar Insumos", 
    "Conferência e Ajustes", 
    "Histórico Geral", 
    "Sugestões e Erros"
], label_visibility="collapsed")

# Cabeçalho Principal
st.markdown("""
    <div style="background: linear-gradient(135deg, #2A0052 0%, #1A0033 100%); padding: 30px; border-radius: 16px; border: 1px solid #7C3AED; box-shadow: 0 8px 20px rgba(0,0,0,0.4); text-align: center; margin-bottom: 25px;">
        <h1 style="color: #FFFFFF; font-size: 30px; font-weight: 800; margin: 0;">LATAM Cargo WMS</h1>
        <p style="color: #C4B5FD; font-size: 15px; margin: 8px 0 0 0;">Gestão integrada e ágil de insumos operacionais</p>
    </div>
""", unsafe_allow_html=True)

pedidos_db = carregar_pedidos()

if menu == "Painel de Gestão":
    col1, col2 = st.columns(2)
    pendentes_count = len([p for p in pedidos_db if p.get('status') == "Pendente"])
    recebidos_count = len([p for p in pedidos_db if p.get('status') == "Recebido"])
    
    with col1:
        with st.container(border=True):
            st.markdown("<span style='font-size: 12px; font-weight: 700; color: #94A3B8; letter-spacing: 1px;'>PEDIDOS PENDENTES</span>", unsafe_allow_html=True)
            st.markdown(f"<h3 style='font-size: 38px; font-weight: 800; color: #FFFFFF; margin-top: 5px;'>{pendentes_count}</h3>", unsafe_allow_html=True)
        
    with col2:
        with st.container(border=True):
            st.markdown("<span style='font-size: 12px; font-weight: 700; color: #38A169; letter-spacing: 1px;'>PEDIDOS APROVADOS / RECEBIDOS</span>", unsafe_allow_html=True)
            st.markdown(f"<h3 style='font-size: 38px; font-weight: 800; color: #FFFFFF; margin-top: 5px;'>{recebidos_count}</h3>", unsafe_allow_html=True)
        
    st.markdown("### Histórico de Solicitações Recentes")
    with st.container(border=True):
        if pedidos_db:
            df_base = pd.DataFrame(pedidos_db)[['id', 'data', 'base', 'solicitante', 'bp', 'valor_total', 'status']]
            df_base.columns = ["ID PEDIDO", "DATA/HORA", "BASE", "SOLICITANTE", "BP", "VALOR TOTAL (R$)", "STATUS"]
            st.dataframe(df_base, use_container_width=True)
        else:
            st.info("Nenhum pedido registado no sistema ainda.")

elif menu == "Solicitar Insumos":
    st.title("Nova Requisição de Materiais")
    st.markdown("Preencha seus dados de identificação e a calculadora de insumos desejados:")
    
    with st.container(border=True):
        st.markdown("### 👤 Identificação do Solicitante")
        col_id1, col_id2, col_id3 = st.columns(3)
        with col_id1:
            nome_solicitante = st.text_input("Seu Nome Completo")
        with col_id2:
            bp_solicitante = st.text_input("Seu BP (Matrícula)")
        with col_id3:
            base_selecionada = st.selectbox("Base Operacional Solicitante", BASES_LATAM)
    
    with st.container(border=True):
        quantidades = {}
        with st.form("form_solicitacao_insumos"):
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
            
            submit_pedido = st.form_submit_button("REGISTRAR E GERAR PLANILHA DE PEDIDO 🚀", type="primary")
            
            if submit_pedido:
                if not nome_solicitante.strip() or not bp_solicitante.strip():
                    st.warning("⚠️ Por favor, preencha seu Nome e seu BP antes de registrar o pedido.")
                else:
                    itens_solicitados = []
                    for item in CATALOGO_ITENS:
                        qtd = quantidades[item['pn']]
                        if qtd > 0:
                            itens_solicitados.append({**item, "quantidade": qtd})
                            
                    if not itens_solicitados:
                        st.warning("⚠️ Insira ao menos uma quantidade desejada.")
                    else:
                        novo_pedido = {
                            "id": f"PED-{base_selecionada.split(' - ')[0]}-{str(datetime.now().timestamp())[-4:]}",
                            "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                            "data_recebimento": "Pendente",
                            "base": base_selecionada,
                            "solicitante": nome_solicitante,
                            "bp": bp_solicitante,
                            "valor_total": total_geral,
                            "status": "Pendente",
                            "itens": itens_solicitados
                        }
                        
                        # Salva no Supabase (tabela: pedidos_wm)
                        if supabase:
                            try:
                                supabase.table("pedidos_wm").insert(novo_pedido).execute()
                                st.session_state.ultimo_pedido_criado = novo_pedido
                                st.success(f"🎉 Pedido {novo_pedido['id']} registado e salvo na nuvem com sucesso!")
                            except Exception as e:
                                st.error(f"Erro ao salvar no banco de dados: {e}")
                        else:
                            st.error("⚠️ Conexão com o Supabase não configurada nos Secrets do Streamlit.")

    if 'ultimo_pedido_criado' in st.session_state:
        p_recente = st.session_state.ultimo_pedido_criado
        st.markdown("---")
        st.markdown("### 📥 Baixar Planilha de Solicitação (Pedido Oficial)")
        
        csv_pedido_linhas = ["Part Number (PN);Descricao;Unidade;Preco Unitario (R$);Quantidade Solicitada;Valor Total (R$)"]
        for it in p_recente['itens']:
            subtotal = it['quantidade'] * it['preco']
            pn_formatado = f'="{it["pn"]}"'
            csv_pedido_linhas.append(f"{pn_formatado};{it['descricao']};{it['unidade']};{it['preco']};{it['quantidade']};{subtotal:.2f}")
        csv_pedido_data = "\n".join(csv_pedido_linhas)
        
        st.download_button(
            label="📄 Baixar Planilha (.csv) do Pedido",
            data=csv_pedido_data,
            file_name=f"Planilha_Pedido_{p_recente['base'].split(' - ')[0]}_{p_recente['id']}.csv",
            mime="text/csv",
            type="primary"
        )

elif menu == "Conferência e Ajustes":
    st.title("Conferência, Ajustes e Confirmação de Recebimento")
    st.markdown("Selecione um pedido para conferir, editar itens e confirmar o recebimento.")
    
    ids_pedidos = [p['id'] for p in pedidos_db]
    if not ids_pedidos:
        st.info("Nenhum pedido disponível para conferência.")
    else:
        with st.container(border=True):
            pedido_selecionado_id = st.selectbox("Selecione o Pedido", ids_pedidos)
            pedido = next(p for p in pedidos_db if p['id'] == pedido_selecionado_id)
            
            st.markdown(f"**Base:** `{pedido['base']}` | **Solicitante:** `{pedido.get('solicitante', 'N/A')} (BP: {pedido.get('bp', 'N/A')})` | **Status:** `{pedido['status']}`")
            st.markdown("💡 *Na tabela abaixo pode clicar nas células para editar nomes, valores, alterar quantidades, ou usar os botões para adicionar/remover linhas:*")
            
            df_itens = pd.DataFrame(pedido['itens'])
            edited_df = st.data_editor(df_itens, num_rows="dynamic", use_container_width=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Confirmar Recebimento", type="primary"):
                    data_rec = datetime.now().strftime("%d/%m/%Y %H:%M")
                    if supabase:
                        try:
                            supabase.table("pedidos_wm").update({
                                "itens": edited_df.to_dict(orient="records"),
                                "status": "Recebido",
                                "data_recebimento": data_rec
                            }).eq("id", pedido['id']).execute()
                            st.success(f"🎉 Pedido {pedido['id']} marcado como Recebido na nuvem!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao atualizar: {e}")
                    
            with col2:
                csv_linhas = ["Item;Quantidade"]
                for i in pedido['itens']:
                    csv_linhas.append(f"{i.get('pn', '')} - {i.get('descricao', '')};{i.get('quantidade', 0)}")
                csv_data = "\n".join(csv_linhas)
                
                st.download_button(
                    label="Baixar Planilha de Recebimento (.csv)",
                    data=csv_data,
                    file_name=f"Insumos_Conferidos_{pedido['id']}.csv",
                    mime="text/csv"
                )

elif menu == "Histórico Geral":
    st.title("Auditoria e Histórico Geral")
    st.markdown("Consolidado completo salvo em nuvem de todas as solicitações registradas.")
    
    with st.container(border=True):
        if pedidos_db:
            dados_historico = []
            for p in pedidos_db:
                dados_historico.append({
                    "ID do Pedido": p['id'],
                    "Base": p['base'],
                    "Solicitante": p.get('solicitante', 'N/A'),
                    "BP": p.get('bp', 'N/A'),
                    "Data/Hora do Pedido": p['data'],
                    "Data/Hora Recebimento": p.get('data_recebimento', 'Pendente'),
                    "Valor Total (R$)": f"R$ {p['valor_total']:,.2f}",
                    "Status": p['status']
                })
            df_geral = pd.DataFrame(dados_historico)
            st.dataframe(df_geral, use_container_width=True)
        else:
            st.info("Nenhum pedido registado no sistema.")

elif menu == "Sugestões e Erros":
    st.title("Central de Feedback e Sugestões")
    st.markdown("Envie uma mensagem direta para a equipa de desenvolvimento.")
    
    with st.container(border=True):
        with st.form("form_feedback"):
            tipo_msg = st.selectbox("TIPO DE MENSAGEM", ["💡 Sugestão de Melhoria", "🛠️ Reportar Erro / Bug", "📌 Outro Assunto"])
            detalhes_msg = st.text_area("DETALHES", placeholder="Descreva aqui sua sugestão ou o erro encontrado...", height=150)
            submit_feedback = st.form_submit_button("Enviar Mensagem 🚀", type="primary")
            
            if submit_feedback:
                if not detalhes_msg.strip():
                    st.warning("⚠️ Por favor, preencha os detalhes da mensagem.")
                else:
                    st.success("🎉 Mensagem enviada com sucesso para a equipa de desenvolvimento!")