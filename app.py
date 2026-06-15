import streamlit as st
import os
from main import LeitorXLS, MotorV1Completo, ProcessadorTipoB

st.set_page_config(page_title="MOTOR V1 - Painel Operacional", page_icon="🛡️", layout="wide")
st.title("🛡️ Sistema de Auditoria Analítica - MOTOR V1")
st.caption("Versão Integrada Unificada — Em conformidade com o Volume 22")

aba_tipo_b, aba_tipo_d = st.tabs([
    "🎯 TIPO B — Sequência Operacional (Sinal Real)", 
    "📊 TIPO D — Auditoria Cronológica (.xlsx)"
])

NOME_BASE_DEFINITIVA = "resultados_blaze.xlsx"
NOME_RECENCIA_ATIVA = "base_recencia_ativa.xlsx"

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
                    
                    for linha in output_texto.split("\n"):
                        if "SINAL:" in linha:
                            st.session_state.sinal_pendente = linha.split("SINAL:")[1].strip()
                        if "- Resolução de Conflitos:" in linha:
                            st.session_state.justificativa_pendente = linha.split("- Resolução de Conflitos:")[1].strip()
                            
                    st.success("Cálculo de Previsibilidade Concluído!")
            except Exception as e:
                st.error(f"Erro Crítico no processamento da sequência: {e}")

    if st.session_state.sinal_pendente:
        st.write("---")
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📝 Rascunho Analítico Interno")
            memoria_limpa = st.session_state.log_completo.split("[RESULTADO FINAL TIPO B]")[0]
            st.text_area("Memória de Cálculo", value=memoria_limpa, height=300)
            
        with col2:
            st.subheader("📊 Veredito e Correção Operacional")
            sinal = st.session_state.sinal_pendente
            
            if sinal == "NO CALL":
                st.warning(f"**EXPECTATIVA:** {sinal}")
                st.caption(f"Motivo: {st.session_state.justificativa_pendente}")
            else:
                st.info(f"**EXPECTATIVA ATIVA:** Operar no {sinal}")
                st.caption(f"Origem: {st.session_state.justificativa_pendente}")
                
                st.write("---")
                st.write("### 🎛️ Registrar Resultado Real da Entrada:")
                
                c1, c2, c3, c4 = st.columns(4)
                if c1.button("🟢 G0"):
                    st.success(f"Registrado: Sinal no {sinal} pago em G0!")
                    st.session_state.sinal_pendente = None
                if c2.button("🟡 G1"):
                    st.success(f"Registrado: Sinal no {sinal} pago em G1!")
                    st.session_state.sinal_pendente = None
                if c3.button("🟠 G2"):
                    st.success(f"Registrado: Sinal no {sinal} pago em G2!")
                    st.session_state.sinal_pendente = None
                if c4.button("🔴 FALHA"):
                    st.error(f"Registrado: Estrutura resultou em Falha.")
                    st.session_state.sinal_pendente = None

# =========================================================================
# ABA TIPO D — AUDITORIA CRONOLÓGICA DE LONGO PRAZO
# =========================================================================
with aba_tipo_d:
    st.header("📊 Auditoria Cronológica Tipo D")
    st.info("Faça o upload do seu Excel recente para auditar a saúde e recência do mercado.")
    arquivo_upload = st.file_uploader("Arraste o seu arquivo .xlsx aqui", type=["xlsx"])
    
    if arquivo_upload is not None:
        caminho_temp = "temp_recencia.xlsx"
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            rodar_auditoria = st.button("🔍 Iniciar Auditoria de Recência")
        with col_btn2:
            salvar_como_base = st.button("💾 Definir como Nova Base de Longo Prazo")

        if rodar_auditoria:
            # Salva o arquivo como temporário E também como Memória Ativa de Recência
            with open(caminho_temp, "wb") as f:
                f.write(arquivo_upload.getbuffer())
            if os.path.exists(NOME_RECENCIA_ATIVA): os.remove(NOME_RECENCIA_ATIVA)
            with open(NOME_RECENCIA_ATIVA, "wb") as f:
                f.write(arquivo_upload.getbuffer())

            leitor = LeitorXLS(caminho_temp)
            dados = leitor.ler_e_validar()
            if dados:
                motor = MotorV1Completo(dados)
                output_d = motor.processar_auditoria()
                st.success("Auditoria Realizada! A IA salvou e fixou esta base como Recência Ativa.")
                
                memoria_d = output_d.split("[RESULTADO FINAL TIPO D]")[0]
                resultado_d = "[RESULTADO FINAL TIPO D]" + output_d.split("[RESULTADO FINAL TIPO D]")[1]
                
                st.subheader("📋 Histórico das Janelas Móveis")
                st.text_area("Processamento em Saltos", value=memoria_d, height=200)
                st.subheader("📉 Consolidação Normativa")
                st.code(resultado_d, language="text")
            else:
                st.error("IMPOSSÍVEL CALCULAR - Estrutura fora do padrão do Volume 8.")
            if os.path.exists(caminho_temp): os.remove(caminho_temp)

        if salvar_como_base:
            with open(caminho_temp, "wb") as f:
                f.write(arquivo_upload.getbuffer())
            try:
                if os.path.exists(NOME_BASE_DEFINITIVA): os.remove(NOME_BASE_DEFINITIVA)
                with open(NOME_BASE_DEFINITIVA, "wb") as f:
                    f.write(arquivo_upload.getbuffer())
                st.success(f"Sucesso! Arquivo gravado permanentemente como '{NOME_BASE_DEFINITIVA}'. Base Histórica atualizada.")
            except Exception as e:
                st.error(f"Erro ao salvar arquivo base: {e}")
            if os.path.exists(caminho_temp): os.remove(caminho_temp)
