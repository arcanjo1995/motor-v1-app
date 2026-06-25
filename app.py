import streamlit as st
import os

from main import LeitorXLS
from main import MotorV1Completo
from main import adicionar_a_base_longo_prazo
from main import carregar_modelo_longo_prazo
from main import motor_unificado

# ============================================================
# INICIALIZAÇÃO DO MOTOR
# ============================================================
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
st.title("🛡️ MOTOR V1 - Sistema de Sinais")
st.caption("Base Longa + Recência com prioridade")

aba_tipo_b, aba_tipo_d, aba_padroes = st.tabs([
    "🎯 TIPO B — Sinal Real",
    "📊 TIPO D — Auditoria",
    "📈 Padrões"
])

# =========================================================================
# ABA TIPO B
# =========================================================================
with aba_tipo_b:
    st.header("🎯 TIPO B - Gerar Sinal com Motor Unificado")
    st.info("Recência tem prioridade quando o regime está confiante (≥ 55%).")

    entrada_numeros = st.text_input(
        "Digite os 12 números separados por vírgula:",
        placeholder="Ex: 2,11,14,4,9,12,12,7,3,9,5,12"
    )

    if st.button("🚀 Executar e Gerar Sinal"):
        if not entrada_numeros:
            st.error("Campo vazio.")
        else:
            try:
                lista_numeros = [int(x.strip()) for x in entrada_numeros.split(",")]
                if len(lista_numeros) != 12:
                    st.error("São necessários exatamente 12 números.")
                else:
                    resultado = motor.gerar_sinal_tipo_b(lista_numeros)

                    if resultado.get("no_call"):
                        st.error(f"**NO CALL** — {resultado['justificativa']}")
                    else:
                        st.success(f"**SINAL: {resultado['sinal']}**")
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
                st.error(f"Erro: {e}")

# =========================================================================
# ABA TIPO D
# =========================================================================
with aba_tipo_d:
    st.header("📊 TIPO D - Auditoria e Treinamento")

    arquivo_upload = st.file_uploader("Envie o arquivo .xlsx", type=["xlsx"])

    if arquivo_upload is not None:
        caminho_temp = "temp_recencia.xlsx"
        with open(caminho_temp, "wb") as f:
            f.write(arquivo_upload.getbuffer())

        col1, col2, col3 = st.columns(3)
        with col1:
            btn_recencia = st.button("🔍 Processar como Recência (Prioritário)")
        with col2:
            btn_substituir = st.button("💾 Substituir Base de Longo Prazo")
        with col3:
            btn_adicionar = st.button("➕ Adicionar à Base de Longo Prazo")

        if btn_recencia:
            dados = LeitorXLS(caminho_temp).ler_e_validar()
            if dados and len(dados) >= 20:
                resultado = motor.processar_recencia(dados)
                st.success("✅ Recência injetada com prioridade!")

                if resultado.get("regime_recencia"):
                    with st.expander("📊 Regime de Recência"):
                        st.json(resultado["regime_recencia"])

                motor_antigo = MotorV1Completo(dados)
                output = motor_antigo.processar_auditoria()
                st.text_area("Resultado da Auditoria", output, height=350)
            else:
                st.error("Base de recência muito pequena.")

        if btn_substituir:
            dados = LeitorXLS(caminho_temp).ler_e_validar()
            if dados:
                rel = motor.absorver_base_longa(dados)
                if rel.get("sucesso"):
                    st.success("✅ Base de Longo Prazo absorvida com sucesso!")

        if btn_adicionar:
            dados = LeitorXLS(caminho_temp).ler_e_validar()
            if dados:
                rel = adicionar_a_base_longo_prazo(dados)
                if rel.get("sucesso"):
                    st.success("✅ Dados adicionados com sucesso!")

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
            st.warning("Nenhum modelo encontrado.")
        else:
            st.success("Modelo carregado!")

            with st.expander("♟️ Padrões de Xadrez", expanded=False):
                if hasattr(ia, 'padroes_xadrez_detalhado') and ia.padroes_xadrez_detalhado:
                    for padrao, info in ia.padroes_xadrez_detalhado.items():
                        if info.get("total", 0) >= 5:
                            st.markdown(f"**{padrao}** — {info.get('total')}x")
                            st.json(info)
                else:
                    st.info("Nenhum padrão de Xadrez relevante.")

            with st.expander("🔥 Padrões de Streak", expanded=False):
                if hasattr(ia, 'padroes_streak_detalhado') and ia.padroes_streak_detalhado:
                    for padrao, info in ia.padroes_streak_detalhado.items():
                        if info.get("total", 0) >= 5:
                            st.markdown(f"**{padrao}** — {info.get('total')}x")
                            st.json(info)
                else:
                    st.info("Nenhum padrão de Streak relevante.")

            with st.expander("🌌 Padrões Gerais / Espelhos", expanded=False):
                if hasattr(ia, 'padroes_gerais_detalhado') and ia.padroes_gerais_detalhado:
                    for padrao, info in ia.padroes_gerais_detalhado.items():
                        if info.get("total", 0) >= 5:
                            st.markdown(f"**{padrao}** — {info.get('total')}x")
                            st.json(info)
                else:
                    st.info("Nenhum padrão geral relevante.")
