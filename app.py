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
st.caption("Versão com Análise de Comportamento na Recência")

aba_tipo_b, aba_tipo_d = st.tabs([
    "🎯 TIPO B — Sequência Operacional (Sinal Real)", 
    "📊 TIPO D — Auditoria Cronológica (.xlsx)"
])

NOME_BASE_DEFINITIVA = "resultados_blaze.xlsx"
NOME_RECENCIA_ATIVA = "base_recencia_ativa.xlsx"

# ABA TIPO B (mantida exatamente igual)
with aba_tipo_b:
    # ... (código da aba Tipo B permanece exatamente como você enviou)

# ABA TIPO D - ATUALIZADA
with aba_tipo_d:
    st.header("📊 Auditoria Cronológica Tipo D")
    arquivo_upload = st.file_uploader("Arraste o seu arquivo .xlsx aqui", type=["xlsx"])
    
    if arquivo_upload is not None:
        caminho_temp = "temp_recencia.xlsx"

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

        # INICIAR AUDITORIA DE RECÊNCIA (agora mostra análise de recência)
        if rodar_auditoria:
            with open(caminho_temp, "wb") as f: f.write(arquivo_upload.getbuffer())
            if os.path.exists(NOME_RECENCIA_ATIVA): os.remove(NOME_RECENCIA_ATIVA)
            with open(NOME_RECENCIA_ATIVA, "wb") as f: f.write(arquivo_upload.getbuffer())

            leitor = LeitorXLS(caminho_temp)
            dados = leitor.ler_e_validar()
            
            if dados:
                ia = integrar_recencia_no_modelo(dados, multiplicador=5)
                motor = MotorV1Completo(dados)
                output_d = motor.processar_auditoria()
                
                st.success("✅ Auditoria de Recência realizada e integrada!")

                # === NOVO: Mostra análise de comportamento da RECÊNCIA ===
                if hasattr(ia, 'analise_recencia') and ia.analise_recencia:
                    with st.expander("🔬 Análise de Comportamento na RECÊNCIA (pós-número)", expanded=False):
                        st.json(ia.analise_recencia)

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

        # Substituir e Adicionar (mantidos com análise de longo prazo)
        if salvar_como_base:
            # ... (código mantido exatamente como você enviou)

        if adicionar_base:
            # ... (código mantido exatamente como você enviou)
