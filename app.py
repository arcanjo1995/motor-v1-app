import streamlit as st
import os
from main import (
    LeitorXLS, 
    MotorV1Completo, 
    ProcessadorTipoB,
    treinar_base_longo_prazo_com_janelas,
    integrar_recencia_no_modelo,
    adicionar_a_base_longo_prazo
)

st.set_page_config(page_title="MOTOR V1 - Painel Operacional", page_icon="🛡️", layout="wide")
st.title("🛡️ Sistema de Auditoria Analítica - MOTOR V1")
st.caption("Versão com Acumulação de Base de Longo Prazo (Append)")

aba_tipo_b, aba_tipo_d = st.tabs([
    "🎯 TIPO B — Sequência Operacional (Sinal Real)", 
    "📊 TIPO D — Auditoria Cronológica (.xlsx)"
])

NOME_BASE_DEFINITIVA = "resultados_blaze.xlsx"
NOME_RECENCIA_ATIVA = "base_recencia_ativa.xlsx"

# =========================================================================
# ABA TIPO B (mantido igual)
# =========================================================================
with aba_tipo_b:
    # ... (código da aba Tipo B permanece o mesmo)
    pass

# =========================================================================
# ABA TIPO D - COM RELATÓRIO COMPLETO
# =========================================================================
with aba_tipo_d:
    st.header("📊 Auditoria Cronológica Tipo D")
    st.info("Faça o upload do seu Excel para auditar ou atualizar a base de longo prazo.")
    arquivo_upload = st.file_uploader("Arraste o seu arquivo .xlsx aqui", type=["xlsx"])
    
    if arquivo_upload is not None:
        caminho_temp = "temp_recencia.xlsx"

        # Mostra quantos registros já existem na base
        registros_atuais = 0
        if os.path.exists(NOME_BASE_DEFINITIVA):
            try:
                dados_existentes = LeitorXLS(NOME_BASE_DEFINITIVA).ler_e_validar()
                if dados_existentes:
                    registros_atuais = len(dados_existentes)
            except:
                registros_atuais = 0

        if registros_atuais > 0:
            st.info(f"📁 **Base de Longo Prazo atual tem {registros_atuais} registros.**")
        else:
            st.warning("📁 Ainda não existe uma Base de Longo Prazo salva.")

        col1, col2, col3 = st.columns(3)
        with col1:
            rodar_auditoria = st.button("🔍 Iniciar Auditoria de Recência")
        with col2:
            salvar_como_base = st.button("💾 Substituir Base de Longo Prazo")
        with col3:
            adicionar_base = st.button("➕ Adicionar à Base de Longo Prazo")

        # ============================================================
        # 1. INICIAR AUDITORIA DE RECÊNCIA
        # ============================================================
        if rodar_auditoria:
            with open(caminho_temp, "wb") as f: f.write(arquivo_upload.getbuffer())
            if os.path.exists(NOME_RECENCIA_ATIVA): os.remove(NOME_RECENCIA_ATIVA)
            with open(NOME_RECENCIA_ATIVA, "wb") as f: f.write(arquivo_upload.getbuffer())

            leitor = LeitorXLS(caminho_temp)
            dados = leitor.ler_e_validar()
            
            if dados:
                integrar_recencia_no_modelo(dados, multiplicador=5)
                motor = MotorV1Completo(dados)
                output_d = motor.processar_auditoria()
                
                st.success("✅ Auditoria de Recência realizada e integrada ao modelo!")
                
                memoria_d = output_d.split("[RESULTADO FINAL TIPO D]")[0]
                resultado_d = "[RESULTADO FINAL TIPO D]" + output_d.split("[RESULTADO FINAL TIPO D]")[1]
                
                st.write("---")
                st.subheader("📋 Histórico das Janelas Móveis")
                st.text_area("Processamento em Saltos", value=memoria_d, height=200)
                st.subheader("📉 Consolidação Normativa")
                st.code(resultado_d, language="text")
            else:
                st.error("IMPOSSÍVEL CALCULAR - Estrutura fora do padrão do Volume 8.")
            
            if os.path.exists(caminho_temp): os.remove(caminho_temp)

        # ============================================================
        # 2. SUBSTITUIR BASE DE LONGO PRAZO (com relatório completo)
        # ============================================================
        if salvar_como_base:
            with open(caminho_temp, "wb") as f: f.write(arquivo_upload.getbuffer())
            try:
                if os.path.exists(NOME_BASE_DEFINITIVA): os.remove(NOME_BASE_DEFINITIVA)
                with open(NOME_BASE_DEFINITIVA, "wb") as f: f.write(arquivo_upload.getbuffer())

                dados = LeitorXLS(NOME_BASE_DEFINITIVA).ler_e_validar()
                if dados:
                    relatorio = treinar_base_longo_prazo_com_janelas(dados)
                    
                    if relatorio.get("sucesso"):
                        st.success("✅ Base de Longo Prazo substituída e treinada com sucesso!")
                        
                        # === RELATÓRIO COMPLETO RESTAURADO ===
                        st.subheader("📊 Relatório de Treinamento da Base Longa")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Registros Processados", relatorio["registros_processados"])
                            st.metric("Janelas Analisadas", relatorio["janelas_analisadas"])
                        with col2:
                            st.metric("G0", relatorio["G0"])
                            st.metric("G1", relatorio["G1"])
                            st.metric("G2", relatorio["G2"])
                        with col3:
                            st.metric("Falhas", relatorio["FALHA"])
                            st.metric("NO CALL", relatorio["NO CALL"])
                            st.metric("Regras Boas", relatorio["regras_com_boa_performance"])

                        st.info(f"Assertividade G0 + G1: **{relatorio['assertividade_g0_g1_percent']}%**")
                        st.caption(relatorio["mensagem"])
                    else:
                        st.warning(relatorio.get("mensagem"))
                else:
                    st.error("Não foi possível ler os dados do arquivo.")
            except Exception as e:
                st.error(f"Erro ao salvar e treinar base: {e}")
            if os.path.exists(caminho_temp): os.remove(caminho_temp)

        # ============================================================
        # 3. ADICIONAR À BASE DE LONGO PRAZO (com relatório)
        # ============================================================
        if adicionar_base:
            with open(caminho_temp, "wb") as f: f.write(arquivo_upload.getbuffer())
            try:
                dados_novos = LeitorXLS(caminho_temp).ler_e_validar()
                if dados_novos:
                    relatorio = adicionar_a_base_longo_prazo(dados_novos)
                    
                    if relatorio.get("sucesso"):
                        st.success("✅ Dados adicionados e base treinada com sucesso!")
                        
                        # === RELATÓRIO COMPLETO TAMBÉM NO BOTÃO DE ADICIONAR ===
                        st.subheader("📊 Relatório de Treinamento Após Adição")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Registros Totais na Base", relatorio["registros_processados"])
                            st.metric("Janelas Analisadas", relatorio["janelas_analisadas"])
                        with col2:
                            st.metric("G0", relatorio["G0"])
                            st.metric("G1", relatorio["G1"])
                            st.metric("G2", relatorio["G2"])
                        with col3:
                            st.metric("Falhas", relatorio["FALHA"])
                            st.metric("NO CALL", relatorio["NO CALL"])
                            st.metric("Regras Boas", relatorio["regras_com_boa_performance"])

                        st.info(f"Assertividade G0 + G1: **{relatorio['assertividade_g0_g1_percent']}%**")
                        st.caption(relatorio["mensagem"])
                    else:
                        st.warning(relatorio.get("mensagem"))
                else:
                    st.error("Não foi possível ler os dados do arquivo.")
            except Exception as e:
                st.error(f"Erro ao adicionar dados à base: {e}")
            if os.path.exists(caminho_temp): os.remove(caminho_temp)
