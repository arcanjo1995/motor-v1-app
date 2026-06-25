import streamlit as st
import os
from datetime import datetime

from main import LeitorXLS
from main import MotorV1Completo
from main import adicionar_a_base_longo_prazo
from main import carregar_modelo_longo_prazo
from main import motor_unificado
from main import EngineMatematicoAvancado
from main import NOME_BASE_DEFINITIVA

# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================
st.set_page_config(page_title="MOTOR V1", page_icon="🛡️", layout="wide")

# ============================================================
# INICIALIZAÇÃO DO MOTOR NO SESSION STATE
# ============================================================
if "motor_v1" not in st.session_state:
    st.session_state.motor_v1 = motor_unificado
    with st.spinner("🛡️ Carregando Motor Unificado V1..."):
        st.session_state.motor_v1.carregar_tudo()
    st.success("Motor Unificado V1 carregado com sucesso!")

motor = st.session_state.motor_v1

# ============================================================
# PAINEL LATERAL - STATUS DO SISTEMA
# ============================================================
st.sidebar.header("⚙️ Status de Operação")
status_motor = motor.status()

if status_motor.get("ia_carregada"):
    st.sidebar.success("🤖 IA Preditiva: ATIVA")
else:
    st.sidebar.error("🤖 IA Preditiva: INATIVA")

if status_motor.get("base_longa_carregada"):
    st.sidebar.success("📊 Base Longa: CARREGADA")
else:
    st.sidebar.warning("📊 Base Longa: NÃO DETECTADA")

if status_motor.get("recencia_injetada"):
    st.sidebar.success("⚡ Recência: INJETADA (PESO +6)")
else:
    st.sidebar.info("⚡ Recência: AGUARDANDO ATUALIZAÇÃO")

if status_motor.get("ultima_atualizacao"):
    st.sidebar.caption(f"Último sincronismo: {status_motor.get('ultima_atualizacao')}")

# ============================================================
# INTERFACE PRINCIPAL
# ============================================================
st.title("🛡️ MOTOR V1 - Sistema de Sinais")
st.caption("Arquitetura Unificada: Base de Longo Prazo integrada à Recência Dinâmica com Prioridade de Filtros")

aba_tipo_b, aba_tipo_d, aba_padroes, aba_matematica = st.tabs([
    "🎯 TIPO B — Sinal Real",
    "📊 TIPO D — Auditoria",
    "📈 Padrões Aprendidos",
    "🧮 Cálculos Matemáticos Avançados"
])

# =========================================================================
# ABA TIPO B — SINAL REAL
# =========================================================================
with aba_tipo_b:
    st.header("🎯 TIPO B - Gerar Sinal com Motor Unificado")
    st.info("A recência assume prioridade operacional automática quando a confiança do regime estiver calculada em valores ≥ 55%.")

    entrada_numeros = st.text_input(
        "Digite os 12 últimos números da sequência separados por vírgula:",
        placeholder="Ex: 2,11,14,4,9,12,12,7,3,9,5,12",
        key="input_sequencia_real"
    )

    if st.button("🚀 Executar e Gerar Sinal", key="btn_gerar_sinal"):
        if not entrada_numeros:
            st.error("Por favor, insira uma sequência válida de números.")
        else:
            try:
                lista_numeros = [int(x.strip()) for x in entrada_numeros.split(",")]
                if len(lista_numeros) != 12:
                    st.error("Erro operacional: São necessários exatamente 12 números para a análise de janela.")
                else:
                    # Geração do sinal pelo motor unificado
                    resultado = motor.gerar_sinal_tipo_b(lista_numeros)
                    
                    # Dedução das polaridades para cálculos matemáticos paralelos
                    polaridades = ['B' if n == 0 else ('V' if 1 <= n <= 7 else 'P') for n in lista_numeros]

                    st.write("---")
                    st.subheader("🔮 CARD DE DECISÃO OPERACIONAL")

                    if resultado.get("no_call"):
                        st.error(f"🚨 **SINAL: NO CALL (OPERAÇÃO BLOQUEADA)**")
                        st.write(f"**Justificativa de Segurança:** {resultado.get('justificativa')}")
                    else:
                        sinal_final = resultado.get("sinal")
                        if sinal_final == "VERMELHO":
                            st.markdown("<h2 style='color: #FF4B4B;'>🔴 SINAL: ENTRAR NO VERMELHO</h2>", unsafe_allow_html=True)
                        elif sinal_final == "PRETO":
                            st.markdown("<h2 style='color: #1E1E1E; background-color: #F0F2F6; padding: 10px; border-radius: 5px;'>⚫ SINAL: ENTRAR NO PRETO</h2>", unsafe_allow_html=True)
                        else:
                            st.warning(f"⚪ **SINAL: {sinal_final}**")

                        st.write(f"**Direcionamento Técnico:** {resultado.get('justificativa')}")
                        st.write(f"**Confiança Intrínseca da IA Preditiva:** {resultado.get('confianca_ia')}%")

                    # Exibição do Regime de Recência Ativo
                    if resultado.get("regime_recencia"):
                        with st.expander("📊 Regime de Recência Proporcional (Filtro Dinâmico)", expanded=True):
                            st.json(resultado["regime_recencia"])

                    # Análise matemática de raridade instantânea da sequência atual
                    raridade_atual = EngineMatematicoAvancado.calcular_raridade_sequencia(polaridades)
                    with st.expander("🧮 Análise de Raridade da Janela Atual", expanded=False):
                        st.write(f"**Streak Atual Detectado:** {raridade_atual.get('streak')}x da cor {raridade_atual.get('cor_sequencia')}")
                        st.write(f"**Probabilidade Teórica de Continuação:** {raridade_atual.get('probabilidade')}%")
                        st.info(f"**Status Estrutural:** {raridade_atual.get('status')}")

                    # Raciocínio por Camadas (Trace Completo do Sistema)
                    if resultado.get("raciocinio_trace"):
                        with st.expander("🔍 Auditoria de Raciocínio por Camadas (Decisão Hierárquica)", expanded=False):
                            for camada in resultado["raciocinio_trace"]:
                                st.markdown(f"**Camada {camada.get('camada')} — {camada.get('nome')}**")
                                st.write(f"• *Resultado Interno:* `{camada.get('resultado')}`")
                                st.write(f"• *Detalhamento:* {camada.get('detalhe')}")
                                st.write(f"• *Impacto Operacional:* `{camada.get('impacto')}`")
                                st.markdown("---")
            except Exception as e:
                st.error(f"Erro crítico no processamento dos dados digitados: {e}")

# =========================================================================
# ABA TIPO D — AUDITORIA E TREINAMENTO
# =========================================================================
with aba_tipo_d:
    st.header("📊 TIPO D - Auditoria Dinâmica e Treinamento Profundo")
    st.caption("Gerenciamento de bases de dados e recálculo das matrizes de transição probabilísticas.")

    arquivo_upload = st.file_uploader("Arraste ou envie seu arquivo Excel (.xlsx) contendo os resultados históricos:", type=["xlsx"])

    if arquivo_upload is not None:
        caminho_temp = "temp_recencia.xlsx"
        with open(caminho_temp, "wb") as f:
            f.write(arquivo_upload.getbuffer())

        st.info("Arquivo recebido com sucesso. Selecione a diretriz de processamento abaixo:")

        col1, col2, col3 = st.columns(3)
        with col1:
            btn_recencia = st.button("⚡ Injetar como Recência Ativa (Prioridade Curto Prazo)")
        with col2:
            btn_substituir = st.button("💾 Substituir Base Definitiva de Longo Prazo")
        with col3:
            btn_adicionar = st.button("➕ Agregar Dados à Base Existente")

        if btn_recencia:
            dados = LeitorXLS(caminho_temp).ler_e_validar()
            if dados and len(dados) >= 20:
                with st.spinner("Injetando e ajustando pesos da recência..."):
                    resultado = motor.processar_recencia(dados)
                st.success("✅ Recência processada e acoplada com multiplicador de alta frequência!")

                if resultado.get("regime_recencia"):
                    with st.expander("📊 Relatório de Análise do Regime Injetado", expanded=True):
                        st.json(resultado["regime_recencia"])

                # Executa a auditoria retroativa com simulação de janelas móveis baseada no MotorV1Completo
                with st.spinner("Simulando auditoria cronológica das janelas móveis..."):
                    motor_antigo = MotorV1Completo(dados)
                    output = motor_antigo.processar_auditoria()
                
                st.subheader("📝 Memória de Cálculo e Taxas de Assertividade (G0, G1, G2)")
                st.text_area("Log Completo da Auditoria Executada", output, height=400)
            else:
                st.error("Erro: A base de dados fornecida é muito pequena para estruturar um regime de recência consistente (Mínimo: 20 registros válidos).")

        if btn_substituir:
            dados = LeitorXLS(caminho_temp).ler_e_validar()
            if dados:
                with st.spinner("Substituindo base de dados e recalculando modelos de Markov..."):
                    rel = motor.absorver_base_longa(dados)
                if rel.get("sucesso"):
                    st.success("✅ Base de Longo Prazo totalmente reformulada e atualizada com sucesso!")
                    st.json(rel)
            else:
                st.error("Erro ao validar ou ler os registros do arquivo fornecido.")

        if btn_adicionar:
            dados = LeitorXLS(caminho_temp).ler_e_validar()
            if dados:
                with st.spinner("Concatenando novos dados à planilha mestre e reexecutando ciclos de janelas..."):
                    rel = adicionar_a_base_longo_prazo(dados)
                if rel.get("sucesso"):
                    st.success("✅ Registros acoplados à base definitiva e persistidos no modelo pkl com sucesso!")
                    st.json(rel)
            else:
                st.error("Erro ao processar e extrair dados válidos da planilha enviada.")

        if os.path.exists(caminho_temp):
            os.remove(caminho_temp)

# =========================================================================
# ABA PADRÕES — INSIGHTS DO MODELO APRENDIDO
# =========================================================================
with aba_padroes:
    st.header("📈 Mapeamento de Padrões Estruturais em Memória")
    st.caption("Visualização das estruturas estatísticas armazenadas no arquivo compilado de longo prazo.")

    if st.button("🔄 Consultar Matrizes e Padrões Ativos"):
        ia = carregar_modelo_longo_prazo()
        if ia is None:
            st.warning("Nenhum modelo preditivo estático ou compilado foi encontrado em disco. Execute um treinamento na aba de Auditoria.")
        else:
            st.success("Modelo de Longo Prazo extraído com sucesso da memória persistente!")

            # SUB-ABA 1: XADREZ
            with st.expander("♟️ Padrões de Alternância Contínua (Xadrez)", expanded=False):
                if hasattr(ia, 'padroes_xadrez_detalhado') and ia.padroes_xadrez_detalhado:
                    contagem_padroes = 0
                    for padrao, info in ia.padroes_xadrez_detalhado.items():
                        if info.get("total", 0) >= 5:
                            st.markdown(f"**Identificador:** `{padrao}` — Ocorrências Computadas: **{info.get('total')}x**")
                            st.json(info)
                            contagem_padroes += 1
                    if contagem_padroes == 0:
                        st.info("Nenhum padrão de xadrez atingiu a recorrência mínima necessária (>= 5 aparições).")
                else:
                    st.info("Nenhum padrão estrutural de xadrez catalogado no modelo.")

            # SUB-ABA 2: STREAK
            with st.expander("🔥 Padrões de Repetição Seguidda (Streak)", expanded=False):
                if hasattr(ia, 'padroes_streak_detalhado') and ia.padroes_streak_detalhado:
                    contagem_streaks = 0
                    for padrao, info in ia.padroes_streak_detalhado.items():
                        if info.get("total", 0) >= 5:
                            st.markdown(f"**Identificador:** `{padrao}` — Ocorrências Computadas: **{info.get('total')}x**")
                            st.json(info)
                            contagem_streaks += 1
                    if contagem_streaks == 0:
                        st.info("Nenhum padrão de streak atingiu a recorrência mínima necessária (>= 5 aparições).")
                else:
                    st.info("Nenhum padrão estrutural de streak catalogado no modelo.")

            # SUB-ABA 3: GERAIS E ESPELHOS
            with st.expander("🌌 Padrões Complexos, Duplos e Espelhamentos", expanded=False):
                if hasattr(ia, 'padroes_gerais_detalhado') and ia.padroes_gerais_detalhado:
                    contagem_gerais = 0
                    for padrao, info in ia.padroes_gerais_detalhado.items():
                        if info.get("total", 0) >= 5:
                            st.markdown(f"**Estrutura Combinatória:** `{padrao}` — Ocorrências Computadas: **{info.get('total')}x**")
                            st.json(info)
                            contagem_gerais += 1
                    if contagem_gerais == 0:
                        st.info("Nenhum padrão geral ou espelho complexo atingiu a recorrência mínima necessária (>= 5 aparições).")
                else:
                    st.info("Nenhum padrão estrutural complexo catalogado no modelo.")

            # SUB-ABA 4: COMPORTAMENTO PÓS-NÚMERO (ALINHADO COM FUNÇÃO DA IA)
            with st.expander("🔢 Distribuição Estatística de Comportamento Pós-Número (0 a 14)", expanded=False):
                if hasattr(ia, 'analisar_comportamento_pos_numero'):
                    with st.spinner("Compilando relatórios probabilísticos por número individual..."):
                        relatorio_numeros = ia.analisar_comportamento_pos_numero()
                    
                    for numero, dados_num in relatorio_numeros.items():
                        st.markdown(f"### 📍 Número: {numero}")
                        col_n1, col_n2, col_n3 = st.columns(3)
                        with col_n1:
                            st.write(f"• **Aparições Totais:** {dados_num.get('total_aparicoes')}")
                            st.write(f"• **Cor Predominante Posterior:** `{dados_num.get('cor_mais_frequente_apos')}`")
                        with col_n2:
                            st.write(f"• **Frequência da Dominante:** {dados_num.get('frequencia_cor_dominante_%')}%")
                            st.write(f"• **Estabilidade Histórica:** `{dados_num.get('estabilidade')}`")
                        with col_n3:
                            st.write(f"• **Saturação de Volumetria:** `{dados_num.get('saturacao')}`")
                            st.write(f"• **Tendência de Fluxo:** `{dados_num.get('tendencia_recente')}`")
                        st.write("**Distribuição Real de Frequências (V/P/B):**")
                        st.json(dados_num.get("distribuicao_pos"))
                        st.markdown("---")
                else:
                    st.info("O modelo carregado não possui suporte ou histórico para extração de comportamento pós-número.")

# =========================================================================
# ABA MATEMÁTICA — ENGINE MATEMÁTICO AVANÇADO
# =========================================================================
with aba_matematica:
    st.header("🧮 Engine Matemático Avançado e Gestão de Risco")
    st.caption("Cálculos analíticos de macrofrequências e simulação de aporte financeiro.")

    # 1. Macrofrequência / Viés de Surfe
    st.subheader("🌊 Análise de Macrofrequência (Surfe de Viés)")
    if not os.path.exists(NOME_BASE_DEFINITIVA):
        st.warning(f"O arquivo base `{NOME_BASE_DEFINITIVA}` não foi localizado para o cálculo de desvio padrão acumulado.")
    else:
        janela_surfe = st.slider("Selecione a janela amostral retroativa para cálculo do viés de surfe:", min_value=20, max_value=500, value=100, step=10)
        vies_macro = EngineMatematicoAvancado.calcular_vies_surfe(NOME_BASE_DEFINITIVA, janela=janela_surfe)
        
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.metric(label="Frequência Real Vermelho (Alvo: 46.67%)", value=f"{vies_macro.get('frequencia_v')}%", delta=f"{vies_macro.get('desvio_v')}%")
            st.metric(label="Frequência Real Preto (Alvo: 46.67%)", value=f"{vies_macro.get('frequencia_p')}%", delta=f"{vies_macro.get('desvio_p')}%")
        with col_m2:
            st.metric(label="Frequência Real Branco (Alvo: 6.67%)", value=f"{vies_macro.get('frequencia_b')}%")
            st.info(f"**Resultado de Macroanálise:**\n\n{vies_macro.get('vies')}")

    st.markdown("---")

    # 2. Gestão de Risco e Distribuição de Stakes (Split Stake)
    st.subheader("💰 Simulador de Cobertura e Divisão de Aportes (Split Stake)")
    st.caption("Cálculo exato das frações de capital de cobertura com base na margem matemática estática.")
    
    stake_base = st.number_input("Insira o valor da sua Stake Principal na cor escolhida (R$):", min_value=1.0, max_value=5000.0, value=10.0, step=5.0)
    simulacao_stake = EngineMatematicoAvancado.simular_split_stake_cobertura(stake_base)

    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        st.metric(label="Aporte na Cor Principal", value=f"R$ {simulacao_stake.get('stake_cor'):.2f}")
        st.metric(label="Custo Total da Operação", value=f"R$ {simulacao_stake.get('custo_total_operacao'):.2f}")
    with col_s2:
        st.metric(label="Cobertura de Branco Ideal (Proporção 1/7)", value=f"R$ {simulacao_stake.get('cobertura_b_ideal_1_7'):.2f}")
        st.metric(label="Cobertura Conservadora (Proporção 1/10)", value=f"R$ {simulacao_stake.get('cobertura_b_matematica_1_10'):.2f}")
    with col_s3:
        st.metric(label="Lucro Líquido Real (Se bater o Branco)", value=f"R$ {simulacao_stake.get('lucro_liquido_se_der_branco'):.2f}")
        st.metric(label="House Edge Mapeado", value=simulacao_stake.get("house_edge_estatico"))
