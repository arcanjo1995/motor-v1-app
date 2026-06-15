import streamlit as st
import os
from main import LeitorXLS, MotorV1Completo, ProcessadorTipoB, GerenciadorMemoriaViva

st.set_page_config(page_title="MOTOR V1 - Painel Operacional", page_icon="🛡️", layout="wide")
st.title("🛡️ Sistema de Auditoria Analítica - MOTOR V1")
st.caption("Versão Medidor de Evolução da IA — Em conformidade com o Volume 22")

aba_tipo_b, aba_tipo_d = st.tabs([
    "🎯 TIPO B — Sequência Operacional (Sinal Real)", 
    "📊 TIPO D — Auditoria Cronológica (.xlsx)"
])

NOME_BASE_DEFINITIVA = "resultados_blaze.xlsx"
NOME_RECENCIA_ATIVA = "base_recencia_ativa.xlsx"

# =========================================================================
# ABA TIPO B — SEQUÊNCIA OPERACIONAL E ALIMENTAÇÃO REAL
# =========================================================================
with aba_tipo_b:
    st.header("🎯 Processamento Operacional Tipo B")
    st.info("Insira exatamente 12 números separados por vírgula para gerar o sinal operativo.")
    
    entrada_numeros = st.text_input(
        "Sequência dos 12 números da rodada:", 
        placeholder="Exemplo: 2,11,14,4,9,12,12,7,3,9,5,12"
    )
    
    if "sinal_pendente" not in st.session_state: st.session_state.sinal_pendente = None
    if "justificativa_pendente" not in st.session_state: st.session_state.justificativa_pendente = None
    if "log_completo" not in st.session_state: st.session_state.log_completo = ""
    if "sequencia_em_uso" not in st.session_state: st.session_state.sequencia_em_uso = []

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
                    resultado_dict = processador.executar_sinal_real()
                    
                    if "erro" in resultado_dict:
                        st.error(resultado_dict["erro"])
                    else:
                        st.session_state.log_completo = resultado_dict["memoria"]
                        st.session_state.sinal_pendente = resultado_dict["sinal"]
                        st.session_state.justificativa_pendente = resultado_dict["justificativa"]
                        st.session_state.sequencia_em_uso = lista_numeros
                        st.success("Cálculo de Previsibilidade Concluído!")
            except Exception as e:
                st.error(f"Erro Crítico no processamento da sequência: {e}")

    if st.session_state.sinal_pendente:
        st.write("---")
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📝 Rascunho Analítico Interno")
            st.text_area("Memória de Cálculo (15 Releituras)", value=st.session_state.log_completo, height=340)
            
        with col2:
            st.subheader("📊 Veredito e Alimentação Real")
            sinal = st.session_state.sinal_pendente
            
            if sinal == "NO CALL":
                st.warning(f"**EXPECTATIVA:** {sinal}")
                st.caption(f"Motivo: {st.session_state.justificativa_pendente}")
                if st.button("🔄 Limpar Painel"): st.session_state.sinal_pendente = None
            else:
                st.info(f"**EXPECTATIVA ATIVA:** Operar no {sinal}")
                st.caption(f"Origem: {st.session_state.justificativa_pendente}")
                
                st.write("---")
                st.write("### 🎛️ Painel de Injeção de Dados Reais:")
                tipo_resultado = st.radio("Selecione o resultado real da operação:", ["G0", "G1", "G2", "FALHA"], horizontal=True)
                
                numeros_reais = []
                if tipo_resultado == "G0":
                    n1 = st.number_input("Digite o número que saiu na 1ª rodada (G0):", min_value=0, max_value=14, step=1, key="n1")
                    numeros_reais = [n1]
                elif tipo_resultado == "G1":
                    n1 = st.number_input("Número que saiu na 1ª rodada (Erro):", min_value=0, max_value=14, step=1, key="n1")
                    n2 = st.number_input("Número que saiu na 2ª rodada (G1 - Acerto):", min_value=0, max_value=14, step=1, key="n2")
                    numeros_reais = [n1, n2]
                elif tipo_resultado == "G2":
                    n1 = st.number_input("Número que saiu na 1ª rodada (Erro):", min_value=0, max_value=14, step=1, key="n1")
                    n2 = st.number_input("Número que saiu na 2ª rodada (Erro):", min_value=0, max_value=14, step=1, key="n2")
                    n3 = st.number_input("Número que saiu na 3ª rodada (G2 - Acerto):", min_value=0, max_value=14, step=1, key="n3")
                    numeros_reais = [n1, n2, n3]
                elif tipo_resultado == "FALHA":
                    n1 = st.number_input("Número que saiu na 1ª rodada (Erro):", min_value=0, max_value=14, step=1, key="n1")
                    n2 = st.number_input("Número que saiu na 2ª rodada (Erro):", min_value=0, max_value=14, step=1, key="n2")
                    n3 = st.number_input("Número que saiu na 3ª rodada (Erro):", min_value=0, max_value=14, step=1, key="n3")
                    numeros_reais = [n1, n2, n3]
                
                if st.button("💾 Gravar Números Reais e Evoluir IA"):
                    GerenciadorMemoriaViva.injetar_rodadas_reais(st.session_state.sequencia_em_uso, numeros_reais, NOME_RECENCIA_ATIVA)
                    st.success(f"Sucesso! Dados injetados com 100% de exatidão na IA.")
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
        with col_btn1: rodar_auditoria = st.button("🔍 Iniciar Auditoria de Recência")
        with col_btn2: salvar_como_base = st.button("💾 Definir como Nova Base de Longo Prazo")

        if rodar_auditoria:
            with open(caminho_temp, "wb") as f: f.write(arquivo_upload.getbuffer())
            if os.path.exists(NOME_RECENCIA_ATIVA): os.remove(NOME_RECENCIA_ATIVA)
            with open(NOME_RECENCIA_ATIVA, "wb") as f: f.write(arquivo_upload.getbuffer())

            leitor = LeitorXLS(caminho_temp)
            dados = leitor.ler_e_validar()
            if dados:
                motor = MotorV1Completo(dados)
                output_d = motor.processar_auditoria()
                st.success("Auditoria Realizada!")
                
                memoria_d = output_d.split("[RESULTADO FINAL TIPO D]")[0]
                resultado_d = "[RESULTADO FINAL TIPO D]" + output_d.split("[RESULTADO FINAL TIPO D]")[1]
                
                # CAPTURA DA MÉTRICA DE EVOLUÇÃO VISUAL DA IA
                valor_ia = 0.0
                for linha in resultado_d.split("\n"):
                    if "METRICA_EVOLUÇÃO_IA:" in linha:
                        valor_ia = float(linha.split("METRICA_EVOLUÇÃO_IA:")[1].split("%")[0].strip())
                
                # EXIBIÇÃO DO MEDIDOR DE APRENDIZADO
                st.write("---")
                st.subheader("🤖 Indicador de Evolução e Assertividade da IA")
                col_kpi1, col_kpi2 = st.columns([1, 3])
                with col_kpi1:
                    st.metric(label="Assertividade Pura da IA", value=f"{valor_ia:.2f}%")
                with col_kpi2:
                    st.caption("Barra de Maturação de Aprendizado por Recência:")
                    st.progress(valor_ia / 100.0)
                st.write("---")
                
                st.subheader("📋 Histórico das Janelas Móveis")
                st.text_area("Processamento em Saltos", value=memoria_d, height=200)
                st.subheader("📉 Consolidação Normativa")
                st.code(resultado_d, language="text")
            else:
                st.error("IMPOSSÍVEL CALCULAR - Estrutura fora do padrão do Volume 8.")
            if os.path.exists(caminho_temp): os.remove(caminho_temp)

        if salvar_como_base:
            with open(caminho_temp, "wb") as f: f.write(arquivo_upload.getbuffer())
            try:
                if os.path.exists(NOME_BASE_DEFINITIVA): os.remove(NOME_BASE_DEFINITIVA)
                with open(NOME_BASE_DEFINITIVA, "wb") as f: f.write(arquivo_upload.getbuffer())
                st.success(f"Sucesso! Base Histórica atualizada.")
            except Exception as e: st.error(f"Erro ao salvar arquivo base: {e}")
            if os.path.exists(caminho_temp): os.remove(caminho_temp)
