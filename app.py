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

with aba_tipo_b:
    st.header("🎯 Processamento Operacional Tipo B")
    st.info("Insira exatamente 12 números separados por vírgula para gerar o sinal operativo.")
    entrada_numeros = st.text_input("Sequência dos 12 números da rodada:", placeholder="Exemplo: 8,4,11,7,1,5,14,7,14,12,9,3")
    
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
                    
                    st.success("Cálculo de Previsibilidade Concluído!")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.subheader("📝 Rascunho Analítico Interno")
                        memoria = output_texto.split("[RESULTADO FINAL]")[0]
                        st.text_area("Memória de Cálculo", value=memoria, height=250)
                    with col2:
                        st.subheader("📊 Veredito do Juiz Hierárquico")
                        resultado = "[RESULTADO FINAL]" + output_texto.split("[RESULTADO FINAL]")[1]
                        st.code(resultado, language="text")
            except Exception as e:
                st.error(f"Erro Crítico no processamento da sequência: {e}")

with aba_tipo_d:
    st.header("📊 Auditoria Cronológica Tipo D")
    st.info("Faça o upload do seu Excel recente para auditar a saúde e recência do mercado.")
    arquivo_upload = st.file_uploader("Arraste o seu arquivo .xlsx aqui", type=["xlsx"])
    
    if arquivo_upload is not None:
        caminho_temp = "temp_recencia.xlsx"
        with open(caminho_temp, "wb") as f:
            f.write(arquivo_upload.getbuffer())
            
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            rodar_auditoria = st.button("🔍 Iniciar Auditoria de Recência")
        with col_btn2:
            salvar_como_base = st.button("💾 Definir como Nova Base de Longo Prazo")

        if rodar_auditoria:
            leitor = LeitorXLS(caminho_temp)
            dados = leitor.ler_e_validar()
            if dados:
                motor = MotorV1Completo(dados)
                output_d = motor.processar_auditoria()
                st.success("Auditoria Realizada!")
                
                memoria_d = output_d.split("[RESULTADO FINAL ESTATÍSTICO]")[0]
                resultado_d = "[RESULTADO FINAL ESTATÍSTICO]" + output_d.split("[RESULTADO FINAL ESTATÍSTICO]")[1]
                
                st.subheader("📋 Histórico das Janelas Móveis")
                st.text_area("Processamento em Saltos", value=memoria_d, height=200)
                st.subheader("📉 Consolidação Normativa")
                st.code(resultado_d, language="text")
            else:
                st.error("IMPOSSÍVEL CALCULAR - Estrutura fora do padrão do Volume 8.")
            if os.path.exists(caminho_temp): os.remove(caminho_temp)

        if salvar_como_base:
            try:
                if os.path.exists(NOME_BASE_DEFINITIVA): os.remove(NOME_BASE_DEFINITIVA)
                with open(NOME_BASE_DEFINITIVA, "wb") as f:
                    f.write(arquivo_upload.getbuffer())
                st.success(f"Sucesso! Arquivo gravado permanentemente como '{NOME_BASE_DEFINITIVA}'. A inteligência do Tipo B foi atualizada.")
            except Exception as e:
                st.error(f"Erro ao salvar arquivo base: {e}")
            if os.path.exists(caminho_temp): os.remove(caminho_temp)
