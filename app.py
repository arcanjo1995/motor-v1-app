"""
MOTOR V1 - Painel Operacional
Versão compatível com o main.py completo (Motor Unificado embutido)
"""

import streamlit as st
import os

from main import (
    LeitorXLS,
    MotorV1Completo,
    adicionar_a_base_longo_prazo,
    carregar_modelo_longo_prazo
)

# ============================================================
# MOTOR UNIFICADO (vem do próprio main.py)
# ============================================================
from main import motor_unificado

if "motor_v1" not in st.session_state:
    st.session_state.motor_v1 = motor_unificado
    with st.spinner("🛡️ Carregando Motor Unificado V1..."):
        st.session_state.motor_v1.carregar_tudo()
    st.success("Motor Unificado V1 carregado com sucesso!")

motor = st.session_state.motor_v1

# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================
st.set_page_config(page_title="MOTOR V1", page_icon="🛡️", layout="wide")
st.title("🛡️ MOTOR V1 - Sistema de Sinais e Auditoria")
st.caption("Base Longa + Recência (Recência com prioridade)")

aba_tipo_b, aba_tipo_d, aba_padroes = st.tabs([
    "🎯 TIPO B — Sinal Real",
    "📊 TIPO D — Auditoria e Treinamento",
    "📈 Padrões Avançados"
])

NOME_BASE_DEFINITIVA = "resultados_blaze.xlsx"
NOME_RECENCIA_ATIVA = "base_recencia_ativa.xlsx"

# =========================================================================
# ABA TIPO B
# =========================================================================
with aba_tipo_b:
    st.header("🎯 TIPO B - Gerar Sinal com Motor Unificado")
    st.info("O sinal é gerado usando todo o conhecimento (Longo Prazo + Recência). A Recência tem prioridade quando o regime está confiante.")

    entrada_numeros = st.text_input(
        "Digite os 12 números separados por vírgula:",
        placeholder="Ex: 2,11,14,4,9,12,12,7,3,9,5,12"
    )

    if st.button("🚀 Executar Releituras e Gerar Sinal"):
        if not entrada_numeros:
            st.error("Campo de entrada vazio.")
        else:
            try:
                lista_numeros = [int(x.strip()) for x in entrada_numeros.split(",")]
                if len(lista_numeros) != 12:
                    st.error("É necessário exatamente 12 números.")
                else:
                    resultado = motor.gerar_sinal_tipo_b(lista_numeros)

                    if resultado.get("no_call"):
                        st.error(f"**NO CALL** — {resultado['justificativa']}")
                    else:
                        st.success(f"**SINAL GERADO: {resultado['sinal']}**")
                        st.write(f"**Justificativa:** {resultado['justificativa']}")

                    if resultado.get("regime_recencia"):
                        with st.expander("📊 Regime de Recência (Prioridade)", expanded=True):
                            st.json(resultado["regime_recencia"])

                    if resultado.get("raciocinio_trace"):
                        with st.expander("🔍 Raciocínio por Camadas (Trace)", expanded=False):
                            for camada in resultado["raciocinio_trace"]:
                                st.markdown(f"**Camada {camada.get('camada')} - {camada.get('nome')}**")
                                st.caption(f"Resultado: {camada.get('resultado')} | Impacto: {camada.get('impacto')}")
                                if camada.get("detalhe"):
                                    st.text(camada["detalhe"])
            except Exception as e:
                st.error(f"Erro ao processar: {e}")

# =========================================================================
# ABA TIPO D
# =========================================================================
with aba_tipo_d:
    st.header("📊 TIPO D - Auditoria Cronológica e Treinamento")

    arquivo_upload = st.file_uploader("Arraste seu arquivo .xlsx aqui", type=["xlsx"])

    if arquivo_upload is not None:
        caminho_temp = "temp_recencia.xlsx"
        with open(caminho_temp, "wb") as f:
            f.write(arquivo_upload.getbuffer())

        col1, col2, col3 = st.columns(3)
        with col1:
            rodar_auditoria = st.button("🔍 Iniciar Auditoria de Recência")
        with col2:
            salvar_como_base = st.button("💾 Substituir Base de Longo Prazo")
        with col3:
            adicionar_base = st.button("➕ Adicionar à Base de Longo Prazo")

        # 1. AUDITORIA DE RECÊNCIA (usa Motor Unificado)
        if rodar_auditoria:
            dados_rec = LeitorXLS(caminho_temp).ler_e_validar()

            if dados_rec and len(dados_rec) >= 20:
                resultado_rec = motor.processar_recencia(dados_rec)
                st.success("✅ Recência processada e injetada com **prioridade** no Motor Unificado!")

                if resultado_rec.get("regime_recencia"):
                    with st.expander("📊 Regime de Recência", expanded=True):
                        st.json(resultado_rec["regime_recencia"])

                # Gera o relatório de janelas
                motor_antigo = MotorV1Completo(dados_rec)
                output_d = motor_antigo.processar_auditoria()

                memoria_d = output_d.split("[RESULTADO FINAL TIPO D]")[0]
                resultado_d = "[RESULTADO FINAL TIPO D]" + output_d.split("[RESULTADO FINAL TIPO D]")[1]

                st.write("---")
                st.subheader("📋 Histórico das Janelas Móveis")
                st.text_area("Processamento em Saltos", value=memoria_d, height=200)
                st.subheader("📉 Consolidação Normativa")
                st.code(resultado_d, language="text")
            else:
                st.error("Base de recência muito pequena ou inválida.")

        # 2. SUBSTITUIR BASE DE LONGO PRAZO
        if salvar_como_base:
            dados = LeitorXLS(caminho_temp).ler_e_validar()
            if dados:
                relatorio = motor.absorver_base_longa(dados)
                if relatorio.get("sucesso"):
                    st.success("✅ Base de Longo Prazo absorvida pelo Motor Unificado!")
                    st.info(relatorio.get("mensagem", ""))
                else:
                    st.error("Erro ao absorver a base.")

        # 3. ADICIONAR À BASE DE LONGO PRAZO
        if adicionar_base:
            dados_novos = LeitorXLS(caminho_temp).ler_e_validar()
            if dados_novos:
                relatorio = adicionar_a_base_longo_prazo(dados_novos)
                if relatorio.get("sucesso"):
                    st.success("✅ Dados adicionados com sucesso!")
                else:
                    st.warning(relatorio.get("mensagem", "Erro ao adicionar."))

        if os.path.exists(caminho_temp):
            os.remove(caminho_temp)

# =========================================================================
# ABA PADRÕES
# =========================================================================
with aba_padroes:
    st.header("📈 Análise de Padrões Avançados")

    if st.button("🔄 Carregar Padrões do Modelo Atual"):
        ia = carregar_modelo_longo_prazo()
        if ia is None:
            st.warning("Nenhum modelo de longo prazo encontrado.")
        else:
            st.success("Modelo carregado com sucesso!")

            with st.expander("♟️ Padrões de Xadrez Detalhados", expanded=False):
                if hasattr(ia, 'padroes_xadrez_detalhado') and ia.padroes_xadrez_detalhado:
                    for padrao, info in ia.padroes_xadrez_detalhado.items():
                        if info.get("total", 0) >= 5:
                            st.markdown(f"**{padrao}** — {info.get('total')}x")
                            st.json(info)
                else:
                    st.info("Nenhum padrão de Xadrez relevante encontrado.")

            with st.expander("🔥 Padrões de Streak Detalhados", expanded=False):
                if hasattr(ia, 'padroes_streak_detalhado') and ia.padroes_streak_detalhado:
                    for padrao, info in ia.padroes_streak_detalhado.items():
                        if info.get("total", 0) >= 5:
                            st.markdown(f"**{padrao}** — {info.get('total')}x")
                            st.json(info)
                else:
                    st.info("Nenhum padrão de Streak relevante encontrado.")

            with st.expander("🌌 Padrões Gerais / Espelhos", expanded=False):
                if hasattr(ia, 'padroes_gerais_detalhado') and ia.padroes_gerais_detalhado:
                    for padrao, info in ia.padroes_gerais_detalhado.items():
                        if info.get("total", 0) >= 5:
                            st.markdown(f"**{padrao}** — {info.get('total')}x")
                            st.json(info)
                else:
                    st.info("Nenhum padrão geral relevante encontrado.")
