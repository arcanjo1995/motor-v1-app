import streamlit as st
import os
from main import (
    LeitorXLS, 
    MotorV1Completo, 
    ProcessadorTipoB,
    treinar_base_longo_prazo_com_janelas,
    integrar_recencia_no_modelo,
    adicionar_a_base_longo_prazo,
    carregar_modelo_longo_prazo,
    salvar_modelo_longo_prazo
)

st.set_page_config(page_title="MOTOR V1 - Painel Operacional", page_icon="🛡️", layout="wide")
st.title("🛡️ Sistema de Auditoria Analítica - MOTOR V1")
st.caption("Versão com Análise de Padrões Avançados")

aba_tipo_b, aba_tipo_d, aba_padroes = st.tabs([
    "🎯 TIPO B — Sequência Operacional (Sinal Real)", 
    "📊 TIPO D — Auditoria Cronológica (.xlsx)",
    "📈 Análise de Padrões Avançados"
])

NOME_BASE_DEFINITIVA = "resultados_blaze.xlsx"
NOME_RECENCIA_ATIVA = "base_recencia_ativa.xlsx"

# =========================================================================
# ABA TIPO B
# =========================================================================
with aba_tipo_b:
    st.header("🎯 Processamento Operacional Tipo B")
    st.info("Insira exatamente 12 números separados por vírgula para gerar o sinal operativo.")
    
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
                    processador = ProcessadorTipoB(lista_numeros, NOME_BASE_DEFINITIVA)
                    resultado = processador.executar_sinal_real()
                    if "erro" in resultado:
                        st.error(resultado["erro"])
                    else:
                        st.success(f"**SINAL GERADO:** {resultado['sinal']}")
                        st.write(f"**Justificativa:** {resultado['justificativa']}")
                        st.write(f"**Confiança da IA:** {resultado['confianca_ia']}%")
                        if resultado.get("raciocinio_final"):
                            st.write("**Raciocínio Final:**")
                            st.code(resultado["raciocinio_final"])
                        if resultado.get("motivo_real"):
                            st.caption(f"Motivo real da decisão: {resultado['motivo_real']}")
            except Exception as e:
                st.error(f"Erro ao processar: {e}")

# =========================================================================
# ABA TIPO D
# =========================================================================
with aba_tipo_d:
    st.header("📊 Auditoria Cronológica Tipo D")
    st.info("Faça o upload do seu Excel para auditar ou atualizar a base de longo prazo.")
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

        # 1. INICIAR AUDITORIA DE RECÊNCIA
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

        # 2. SUBSTITUIR BASE DE LONGO PRAZO
        if salvar_como_base:
            with open(caminho_temp, "wb") as f: f.write(arquivo_upload.getbuffer())
            try:
                if os.path.exists(NOME_BASE_DEFINITIVA): os.remove(NOME_BASE_DEFINITIVA)
                with open(NOME_BASE_DEFINITIVA, "wb") as f: f.write(arquivo_upload.getbuffer())

                dados = LeitorXLS(NOME_BASE_DEFINITIVA).ler_e_validar()
                if dados:
                    relatorio = treinar_base_longo_prazo_com_janelas(dados)
                    
                    # === FALLBACK DE SALVAMENTO ===
                    if not relatorio.get("modelo_salvo_com_sucesso", False):
                        try:
                            ia_para_salvar = relatorio.get("ia_treinada")
                            if ia_para_salvar:
                                if salvar_modelo_longo_prazo(ia_para_salvar):
                                    relatorio["modelo_salvo_com_sucesso"] = True
                        except:
                            pass
                    # ================================
                    
                    if relatorio.get("sucesso"):
                        if relatorio.get("modelo_salvo_com_sucesso"):
                            st.success("✅ Base de Longo Prazo substituída e treinada com sucesso!")
                        else:
                            st.error("Modelo ainda não foi salvo corretamente. Tente reiniciar o app.")

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

                        if "analise_comportamento_numeros" in relatorio:
                            with st.expander("🔬 Análise Detalhada por Número (Comportamento Pós-Aparição)", expanded=False):
                                st.json(relatorio["analise_comportamento_numeros"])

                        ia_atual = carregar_modelo_longo_prazo()

                        with st.expander("♟️ Padrões Avançados Aprendidos nesta Base (Xadrez e Streak) + Métricas de Assertividade", expanded=False):
                            if ia_atual:
                                st.markdown("**Xadrez**")
                                if hasattr(ia_atual, 'padroes_xadrez_detalhado') and ia_atual.padroes_xadrez_detalhado:
                                    for padrao, info in ia_atual.padroes_xadrez_detalhado.items():
                                        if info.get("total", 0) >= 8:
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
                                    st.info("Nenhum padrão de Xadrez relevante encontrado.")

                                st.markdown("**Streak**")
                                if hasattr(ia_atual, 'padroes_streak_detalhado') and ia_atual.padroes_streak_detalhado:
                                    for padrao, info in ia_atual.padroes_streak_detalhado.items():
                                        if info.get("total", 0) >= 8:
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
                                    st.info("Nenhum padrão de Streak relevante encontrado.")
                            else:
                                st.error("Modelo ainda não foi salvo corretamente. Tente novamente ou reinicie o app.")

                        with st.expander("🌌 Mapeamento Estatístico Geral (Padrões Dinâmicos e Espelhos)", expanded=False):
                            if ia_atual:
                                if hasattr(ia_atual, 'padroes_gerais_detalhado') and ia_atual.padroes_gerais_detalhado:
                                    for padrao, info in ia_atual.padroes_gerais_detalhado.items():
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
                                    st.info("Nenhum padrão geral dinâmico ou espelho encontrado.")
                    else:
                        st.warning(relatorio.get("mensagem"))
                else:
                    st.error("Não foi possível ler os dados do arquivo.")
            except Exception as e:
                st.error(f"Erro ao salvar e treinar base: {e}")
            if os.path.exists(caminho_temp): os.remove(caminho_temp)

        # 3. ADICIONAR À BASE DE LONGO PRAZO
        if adicionar_base:
            with open(caminho_temp, "wb") as f: f.write(arquivo_upload.getbuffer())
            try:
                dados_novos = LeitorXLS(caminho_temp).ler_e_validar()
                if dados_novos:
                    relatorio = adicionar_a_base_longo_prazo(dados_novos)
                    
                    if relatorio.get("sucesso"):
                        if relatorio.get("modelo_salvo_com_sucesso"):
                            st.success("✅ Dados adicionados e base treinada com sucesso!")
                            
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

                            if "analise_comportamento_numeros" in relatorio:
                                with st.expander("🔬 Análise Detalhada por Número (Comportamento Pós-Aparição)", expanded=False):
                                    st.json(relatorio["analise_comportamento_numeros"])

                            ia_atual = carregar_modelo_longo_prazo()

                            with st.expander("♟️ Padrões Avançados Aprendidos nesta Base (Xadrez e Streak) + Métricas de Assertividade", expanded=False):
                                if ia_atual:
                                    st.markdown("**Xadrez**")
                                    if hasattr(ia_atual, 'padroes_xadrez_detalhado') and ia_atual.padroes_xadrez_detalhado:
                                        for padrao, info in ia_atual.padroes_xadrez_detalhado.items():
                                            if info.get("total", 0) >= 8:
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
                                        st.info("Nenhum padrão de Xadrez relevante encontrado.")

                                    st.markdown("**Streak**")
                                    if hasattr(ia_atual, 'padroes_streak_detalhado') and ia_atual.padroes_streak_detalhado:
                                        for padrao, info in ia_atual.padroes_streak_detalhado.items():
                                            if info.get("total", 0) >= 8:
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
                                        st.info("Nenhum padrão de Streak relevante encontrado.")
                                else:
                                    st.error("Modelo ainda não foi salvo corretamente. Use o botão 'Substituir Base de Longo Prazo'.")

                        with st.expander("🌌 Mapeamento Estatístico Geral (Padrões Dinâmicos e Espelhos)", expanded=False):
                            if ia_atual:
                                if hasattr(ia_atual, 'padroes_gerais_detalhado') and ia_atual.padroes_gerais_detalhado:
                                    for padrao, info in ia_atual.padroes_gerais_detalhado.items():
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
                                    st.info("Nenhum padrão geral dinâmico ou espelho encontrado.")
                        else:
                            st.error("Treinamento realizado, mas falha ao salvar o modelo. Tente usar 'Substituir Base de Longo Prazo'.")
                    else:
                        st.warning(relatorio.get("mensagem"))
                else:
                    st.error("Não foi possível ler os dados do arquivo.")
            except Exception as e:
                st.error(f"Erro ao adicionar dados à base: {e}")
            if os.path.exists(caminho_temp): os.remove(caminho_temp)

# =========================================================================
# ABA PADRÕES
# =========================================================================
with aba_padroes:
    st.header("📈 Análise de Padrões Avançados")
    st.info("Visualização dos padrões aprendidos pelo motor.")

    if st.button("🔄 Carregar Padrões do Modelo Atual"):
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
                        if info.get("total", 0) >= 5: # exibe padrões com mais de 5 ocorrências
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
