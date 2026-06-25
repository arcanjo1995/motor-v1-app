"""
MOTOR V1 - Painel Operacional (VERSÃO COM MOTOR UNIFICADO)
Tudo passa por um único motor: Base Longa + Recência (com prioridade)
"""

import streamlit as st
import os
from datetime import datetime

from main import (
    LeitorXLS,
    MotorV1Completo,
    treinar_base_longo_prazo_com_janelas,
    salvar_modelo_longo_prazo,
    carregar_modelo_longo_prazo
)

# ============================================================
# MOTOR UNIFICADO V1 - ÚNICO PONTO DE CONTROLE
# ============================================================
from motor_unificado import motor_unificado

if "motor_v1" not in st.session_state:
    st.session_state.motor_v1 = motor_unificado
    with st.spinner("🛡️ Carregando Motor Unificado V1 (Base Longa + Recência)..."):
        st.session_state.motor_v1.carregar_tudo()
    st.success("Motor Unificado V1 carregado com sucesso!")

motor = st.session_state.motor_v1

# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================
st.set_page_config(page_title="MOTOR V1 - Painel Operacional", page_icon="🛡️", layout="wide")
st.title("🛡️ Sistema de Auditoria Analítica - MOTOR V1")
st.caption("Versão com Motor Unificado | Recência tem prioridade nos sinais")

aba_tipo_b, aba_tipo_d, aba_padroes = st.tabs([
    "🎯 TIPO B — Sequência Operacional (Sinal Real)",
    "📊 TIPO D — Auditoria Cronológica (.xlsx)",
    "📈 Análise de Padrões Avançados"
])

NOME_BASE_DEFINITIVA = "resultados_blaze.xlsx"
NOME_RECENCIA_ATIVA = "base_recencia_ativa.xlsx"

# =========================================================================
# ABA TIPO B — SINAL REAL COM MOTOR UNIFICADO
# =========================================================================
with aba_tipo_b:
    st.header("🎯 Processamento Operacional Tipo B")
    st.info("Insira exatamente 12 números. O sinal usa **Base Longa + Recência**. A Recência fala mais alto quando o regime está confiante.")

    entrada_numeros = st.text_input(
        "Sequência dos 12 números da rodada:",
        placeholder="Exemplo: 2,11,14,4,9,12,12,7,3,9,5,12"
    )

    if st.button("🚀 Executar Releituras e Gerar Sinal"):
        if not entrada_numeros:
            st.error("Erro: Campo de entrada vazio.")
        else:
            try:
                lista_numeros = [int(x.strip()) for x in entrada_numeros.split(",")]
                if len(lista_numeros) != 12:
                    st.error("Erro: É necessário exatamente 12 números.")
                else:
                    from processador_tipo_b_atualizado import ProcessadorTipoB

                    processador = ProcessadorTipoB(lista_numeros)
                    resultado = processador.executar_sinal_real()

                    if "erro" in resultado:
                        st.error(resultado["erro"])
                    else:
                        if resultado.get("no_call"):
                            st.error(f"**NO CALL** — {resultado['justificativa']}")
                        else:
                            st.success(f"**SINAL GERADO:** {resultado['sinal']}")
                            st.write(f"**Justificativa:** {resultado['justificativa']}")

                        if resultado.get("regime_recencia"):
                            with st.expander("📊 Regime de Recência (prioridade máxima)", expanded=True):
                                st.json(resultado["regime_recencia"])

                        if resultado.get("raciocinio_trace"):
                            with st.expander("🔍 Raciocínio por Camadas (Trace Completo)", expanded=False):
                                for camada in resultado["raciocinio_trace"]:
                                    st.markdown(f"**Camada {camada.get('camada')} — {camada.get('nome')}**")
                                    st.caption(f"Resultado: {camada.get('resultado')} | Impacto: {camada.get('impacto')}")
                                    if camada.get("detalhe"):
                                        st.text(camada["detalhe"])
            except Exception as e:
                st.error(f"Erro ao processar: {e}")

# =========================================================================
# ABA TIPO D — AUDITORIA E TREINAMENTO
# =========================================================================
with aba_tipo_d:
    st.header("📊 Auditoria Cronológica Tipo D")
    st.info("Faça o upload do seu Excel. A recência é injetada com prioridade no Motor Unificado.")

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
            st.info(f"📁 Base de Longo Prazo atual tem {registros_atuais} registros.")
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
        # 1. INICIAR AUDITORIA DE RECÊNCIA (USA MOTOR UNIFICADO)
        # ============================================================
        if rodar_auditoria:
            with open(caminho_temp, "wb") as f:
                f.write(arquivo_upload.getbuffer())

            if os.path.exists(NOME_RECENCIA_ATIVA):
                os.remove(NOME_RECENCIA_ATIVA)
            with open(NOME_RECENCIA_ATIVA, "wb") as f:
                f.write(arquivo_upload.getbuffer())

            dados_rec = LeitorXLS(caminho_temp).ler_e_validar()

            if dados_rec and len(dados_rec) >= 20:
                # === USA O MOTOR UNIFICADO ===
                resultado_rec = motor.processar_recencia(dados_rec)

                st.success("✅ Recência processada e injetada com **prioridade** no Motor Unificado!")

                if resultado_rec.get("regime_recencia"):
                    with st.expander("📊 Regime Atual do Mercado (Recência)", expanded=True):
                        st.json(resultado_rec["regime_recencia"])

                # SÓ DEPOIS da leitura da recência → gera as janelas e análise
                motor_antigo = MotorV1Completo(dados_rec)
                output_d = motor_antigo.processar_auditoria()

                memoria_d = output_d.split("[RESULTADO FINAL TIPO D]")[0]
                resultado_d = "[RESULTADO FINAL TIPO D]" + output_d.split("[RESULTADO FINAL TIPO D]")[1]

                st.write("---")
                st.subheader("📋 Histórico das Janelas Móveis (após injeção da recência)")
                st.text_area("Processamento em Saltos", value=memoria_d, height=200)
                st.subheader("📉 Consolidação Normativa")
                st.code(resultado_d, language="text")
            else:
                st.error("Base de recência muito pequena ou inválida.")

            if os.path.exists(caminho_temp):
                os.remove(caminho_temp)

        # ============================================================
        # 2. SUBSTITUIR BASE DE LONGO PRAZO (USA MOTOR UNIFICADO)
        # ============================================================
        if salvar_como_base:
            with open(caminho_temp, "wb") as f:
                f.write(arquivo_upload.getbuffer())

            dados = LeitorXLS(caminho_temp).ler_e_validar()
            if dados:
                relatorio = motor.absorver_base_longa(dados)
                if relatorio.get("sucesso"):
                    st.success("✅ Base de Longo Prazo absorvida pelo **Motor Unificado**!")
                    st.info(relatorio["mensagem"])
                else:
                    st.error(relatorio.get("mensagem", "Erro desconhecido"))
            if os.path.exists(caminho_temp):
                os.remove(caminho_temp)

        # ============================================================
        # 3. ADICIONAR À BASE DE LONGO PRAZO (mantém lógica antiga por enquanto)
        # ============================================================
        if adicionar_base:
            with open(caminho_temp, "wb") as f:
                f.write(arquivo_upload.getbuffer())
            try:
                dados_novos = LeitorXLS(caminho_temp).ler_e_validar()
                if dados_novos:
                    relatorio = adicionar_a_base_longo_prazo(dados_novos)
                    if relatorio.get("sucesso"):
                        st.success("✅ Dados adicionados à base de longo prazo!")
                        st.info(f"Registros processados: {relatorio.get('registros_processados')}")
                    else:
                        st.warning(relatorio.get("mensagem"))
                else:
                    st.error("Não foi possível ler os dados do arquivo.")
            except Exception as e:
                st.error(f"Erro ao adicionar dados: {e}")
            if os.path.exists(caminho_temp):
                os.remove(caminho_temp)

# =========================================================================
# ABA PADRÕES
# ============================================================
with aba_padroes:
    st.header("📈 Análise de Padrões Avançados")
    st.info("Visualização dos padrões aprendidos pelo motor unificado.")

    if st.button("🔄 Carregar Padrões do Motor Atual"):
        ia = carregar_modelo_longo_prazo()
        if ia is None:
            st.warning("Nenhum modelo de longo prazo encontrado. Treine uma base primeiro.")
        else:
            st.success("Modelo carregado com sucesso!")

            with st.expander("♟️ Padrões de Xadrez Detalhados + Assertividade", expanded=True):
                if hasattr(ia, 'padroes_xadrez_detalhado') and ia.padroes_xadrez_detalhado:
                    for padrao, info in ia.padroes_xadrez_detalhado.items():
                        if info.get("total", 0) >= 5:
                            total = info.get("total", 0)
                            g0 = info.get("g0", 0)
                            g1 = info.get("g1", 0)
                            assertividade = round(((g0 + g1) / total) * 100, 1) if total > 0 else 0.0
                            st.markdown(f"**{padrao}** — {total}x")
                            st.json({
                                "Após → Vermelho": info.get("apos_V", 0),
                                "Após → Preto": info.get("apos_P", 0),
                                "Números que trollam": dict(info.get("quebradores", {})),
                                "G0": g0,
                                "G1": g1,
                                "Assertividade %": assertividade
                            })
                else:
                    st.info("Sem padrões de Xadrez registrados.")

            with st.expander("🔥 Padrões de Streak Detalhados + Assertividade", expanded=True):
                if hasattr(ia, 'padroes_streak_detalhado') and ia.padroes_streak_detalhado:
                    for padrao, info in ia.padroes_streak_detalhado.items():
                        if info.get("total", 0) >= 5:
                            total = info.get("total", 0)
                            g0 = info.get("g0", 0)
                            g1 = info.get("g1", 0)
                            assertividade = round(((g0 + g1) / total) * 100, 1) if total > 0 else 0.0
                            st.markdown(f"**{padrao}** — {total}x")
                            st.json({
                                "Após → Vermelho": info.get("apos_V", 0),
                                "Após → Preto": info.get("apos_P", 0),
                                "Números que trollam": dict(info.get("quebradores", {})),
                                "G0": g0,
                                "G1": g1,
                                "Assertividade %": assertividade
                            })
                else:
                    st.info("Sem padrões de Streak registrados.")

            with st.expander("🌌 Mapeamento Estatístico Geral (Padrões Dinâmicos e Espelhos)", expanded=False):
                if hasattr(ia, 'padroes_gerais_detalhado') and ia.padroes_gerais_detalhado:
                    for padrao, info in ia.padroes_gerais_detalhado.items():
                        if info.get("total", 0) >= 5:
                            total = info.get("total", 0)
                            g0 = info.get("g0", 0)
                            g1 = info.get("g1", 0)
                            assertividade = round(((g0 + g1) / total) * 100, 1) if total > 0 else 0.0
                            st.markdown(f"**{padrao}** — {total}x")
                            st.json({
                                "Após → Vermelho": info.get("apos_V", 0),
                                "Após → Preto": info.get("apos_P", 0),
                                "Números que quebraram": dict(info.get("quebradores", {})),
                                "G0 (Acerto Direto)": g0,
                                "G1 (Acerto no G1)": g1,
                                "Assertividade Real %": assertividade
                            })
                else:
                    st.info("Sem padrões dinâmicos ou espelhos registrados.")

            st.caption("Esses padrões são atualizados automaticamente ao treinar ou adicionar dados na base de longo prazo.")
