"""
MOTOR V1 - Painel Operacional (VERSÃO COM MOTOR UNIFICADO)
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
# IMPORTA O MOTOR UNIFICADO DO PRÓPRIO main.py
# ============================================================
from main import motor_unificado

if "motor_v1" not in st.session_state:
    st.session_state.motor_v1 = motor_unificado
    with st.spinner("🛡️ Carregando Motor Unificado V1 (Base Longa + Recência)..."):
        st.session_state.motor_v1.carregar_tudo()
    st.success("Motor Unificado V1 carregado com sucesso!")

motor = st.session_state.motor_v1

# ============================================================
# CONFIGURAÇÃO
# ============================================================
st.set_page_config(page_title="MOTOR V1", page_icon="🛡️", layout="wide")
st.title("🛡️ MOTOR V1 - Sistema de Sinais")
st.caption("Recência tem prioridade sobre o conhecimento de longo prazo")

aba_tipo_b, aba_tipo_d, aba_padroes = st.tabs([
    "🎯 TIPO B (Sinal Real)",
    "📊 TIPO D (Auditoria)",
    "📈 Padrões"
])

# =========================================================================
# ABA TIPO B
# =========================================================================
with aba_tipo_b:
    st.header("🎯 Gerar Sinal (Tipo B)")
    st.info("O Motor Unificado usa Base Longa + Recência. A Recência fala mais alto quando confiança ≥ 55%.")

    entrada = st.text_input("Insira os 12 números separados por vírgula:")

    if st.button("🚀 Executar e Gerar Sinal"):
        if not entrada:
            st.error("Campo vazio.")
        else:
            try:
                numeros = [int(x.strip()) for x in entrada.split(",")]
                if len(numeros) != 12:
                    st.error("São necessários exatamente 12 números.")
                else:
                    resultado = motor.gerar_sinal_tipo_b(numeros)

                    if resultado.get("no_call"):
                        st.error(f"**NO CALL** — {resultado['justificativa']}")
                    else:
                        st.success(f"**SINAL GERADO: {resultado['sinal']}**")
                        st.write(f"**Justificativa:** {resultado['justificativa']}")

                    if resultado.get("regime_recencia"):
                        with st.expander("📊 Regime de Recência (Prioridade)", expanded=True):
                            st.json(resultado["regime_recencia"])

                    if resultado.get("raciocinio_trace"):
                        with st.expander("🔍 Raciocínio por Camadas"):
                            for camada in resultado["raciocinio_trace"]:
                                st.markdown(f"**Camada {camada.get('camada')} - {camada.get('nome')}**")
                                st.caption(f"Resultado: {camada.get('resultado')} | Impacto: {camada.get('impacto')}")
            except Exception as e:
                st.error(f"Erro ao processar: {e}")

# =========================================================================
# ABA TIPO D
# =========================================================================
with aba_tipo_d:
    st.header("📊 Auditoria e Treinamento")

    arquivo = st.file_uploader("Envie arquivo .xlsx", type=["xlsx"])

    if arquivo:
        caminho_temp = "temp_recencia.xlsx"
        with open(caminho_temp, "wb") as f:
            f.write(arquivo.getbuffer())

        col1, col2, col3 = st.columns(3)
        with col1:
            btn_rec = st.button("🔍 Processar Recência (Prioritário)")
        with col2:
            btn_sub = st.button("💾 Substituir Base Longa")
        with col3:
            btn_add = st.button("➕ Adicionar à Base Longa")

        if btn_rec:
            dados = LeitorXLS(caminho_temp).ler_e_validar()
            if dados and len(dados) >= 20:
                resultado = motor.processar_recencia(dados)
                st.success("Recência injetada com prioridade no Motor Unificado!")
                if resultado.get("regime_recencia"):
                    st.json(resultado["regime_recencia"])

                # Gera o relatório de janelas
                motor_antigo = MotorV1Completo(dados)
                output = motor_antigo.processar_auditoria()
                st.text_area("Resultado da Auditoria", output, height=350)
            else:
                st.error("Base de recência muito pequena.")

        if btn_sub:
            dados = LeitorXLS(caminho_temp).ler_e_validar()
            if dados:
                rel = motor.absorver_base_longa(dados)
                st.success(rel.get("mensagem", "Base substituída com sucesso."))

        if btn_add:
            dados = LeitorXLS(caminho_temp).ler_e_validar()
            if dados:
                rel = adicionar_a_base_longo_prazo(dados)
                if rel.get("sucesso"):
                    st.success("Dados adicionados com sucesso!")
                else:
                    st.warning(rel.get("mensagem"))

        if os.path.exists(caminho_temp):
            os.remove(caminho_temp)

# =========================================================================
# ABA PADRÕES
# =========================================================================
with aba_padroes:
    st.header("📈 Padrões Aprendidos pelo Motor")

    if st.button("🔄 Carregar Padrões do Modelo"):
        ia = carregar_modelo_longo_prazo()
        if ia is None:
            st.warning("Nenhum modelo encontrado. Treine uma base primeiro.")
        else:
            st.success("Modelo carregado!")

            with st.expander("♟️ Padrões de Xadrez", expanded=False):
                if hasattr(ia, 'padroes_xadrez_detalhado'):
                    for padrao, info in ia.padroes_xadrez_detalhado.items():
                        if info.get("total", 0) >= 5:
                            st.markdown(f"**{padrao}** — {info.get('total')}x")
                            st.json(info)
                else:
                    st.info("Nenhum padrão de Xadrez relevante.")

            with st.expander("🔥 Padrões de Streak", expanded=False):
                if hasattr(ia, 'padroes_streak_detalhado'):
                    for padrao, info in ia.padroes_streak_detalhado.items():
                        if info.get("total", 0) >= 5:
                            st.markdown(f"**{padrao}** — {info.get('total')}x")
                            st.json(info)
                else:
                    st.info("Nenhum padrão de Streak relevante.")

            with st.expander("🌌 Padrões Gerais / Espelhos", expanded=False):
                if hasattr(ia, 'padroes_gerais_detalhado'):
                    for padrao, info in ia.padroes_gerais_detalhado.items():
                        if info.get("total", 0) >= 5:
                            st.markdown(f"**{padrao}** — {info.get('total')}x")
                            st.json(info)
                else:
                    st.info("Nenhum padrão geral relevante.")
