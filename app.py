import streamlit as st
import os
from main import LeitorXLS, MotorV1Completo
from operacional_tipo_b import ProcessadorTipoB

st.set_page_config(page_title="MOTOR V1 - Painel Operacional", page_icon="🛡️", layout="wide")
st.title("🛡️ Sistema de Auditoria Analítica - MOTOR V1")
st.caption("Versão Integrada Unificada — Em conformidade com o Volume 22")

aba_tipo_b, aba_tipo_d = st.tabs([
    "🎯 TIPO B — Sequência Operacional (Sinal Real)", 
    "📊 TIPO D — Auditoria Cronológica (.xlsx)"
])

NOME_BASE_DEFINITIVA = "resultados_blaze.xlsx"

# =========================================================================
# ABA TIPO B — SEQUÊNCIA OPERACIONAL E CORREÇÃO MANUAL
# =========================================================================
with aba_tipo_b:
    st.header("🎯 Processamento Operacional Tipo B")
    st.info("Insira exatamente 12 números separados por vírgula para gerar o sinal operativo.")
    
    entrada_numeros = st.text_input(
        "Sequência dos 12 números da rodada:", 
        placeholder="Exemplo: 2,11,14,4,9,12,12,7,3,9,5,12"
    )
    
    # Inicializa estados na memória do Streamlit para manter o painel fixo na tela
    if "sinal_pendente" not in st.session_state:
        st.session_state.sinal_pendente = None
    if "justificativa_pendente" not in st.session_state:
        st.session_state.justificativa_pendente = None
    if "log_completo" not in st.session_state:
        st.session_state.log_completo = ""

    if st.button("🚀 Executar Releituras e Gerar Sinal"):
        if not entrada_numeros:
            st.error("Erro: Campo de entrada vazio.")
        else:
            try:
                lista_numeros = [int(x.strip()) for x in entrada_numeros.split(",") if x.strip() != ""]
                if len(lista_numeros) != 12:
                    st.error(f"Erro Regulamentar: Contém {len(lista_numeros)} números. O manual exige exatamente 12.")
                elif not os.path.exists(NOME_BASE_DEFINITIVA):
                    st.error(f"Erro: O arquivo de longo prazo '{NOME_BASE_DEFINITIVA}' não foi localizado no servidor.")
                else:
                    processador = ProcessadorTipoB(lista_numeros, NOME_BASE_DEFINITIVA)
                    output_texto = processador.executar_sinal_real()
                    
                    st.session_state.log_completo = output_texto
                    st.session_state.sinal_pendente = None
                    st.session_state.justificativa_pendente = None
                    
                    # Captura de forma segura as linhas geradas pelo motor interno
                    for linha in output_texto.split("\n"):
                        if "SINAL:" in linha:
                            st.session_state.sinal_pendente = linha.split("SINAL:")[1].strip()
                        if "- Resolução de Conflitos:" in linha:
                            st.session_state.justificativa_pendente = linha.split("- Resolução de Conflitos:")[1].strip()
                            
                    st.success("Cálculo de Previsibilidade Concluído!")
            except Exception as e:
                st.error(f"Erro Crítico no processamento da sequência: {e}")

    # Painel interativo de exibição cruzada e auditoria ao vivo no iPad
    if st.session_state.sinal_pendente:
        st.write("---")
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📝 Rascunho Analítico Interno")
            # Divide a memória antes do cabeçalho final do Tipo B
            memoria_limpa = st.session_state.log_completo.split("[RESULTADO FINAL TIPO B]")[0]
            st.text_area("Memória de Cálculo", value=memoria_limpa, height=300)
            
        with col2:
            st.subheader("📊 Veredito e Correção Operacional")
            sinal = st.session_state.sinal_pendente
            
            if sinal
