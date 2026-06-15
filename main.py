import os
import pandas as pd
from collections import defaultdict

class SequenciaOperacional:
    def __init__(self, lista_resultados):
        self.cronologia = lista_resultados
        self.numerica = [int(r['numero']) for r in self.cronologia]
        self.polaridades = [str(r['cor']).upper() for r in self.cronologia]
        self.total = len(self.numerica)

class IAPreditivaV1:
    def __init__(self, dados_longo_prazo, dados_recencia=None):
        self.dados_longo = dados_longo_prazo
        self.dados_recencia = dados_recencia
        self.modelo_transicao = defaultdict(list)
        self.modelo_numerico = defaultdict(list)
        self._treinar_modelo()

    def _treinar_modelo(self):
        if self.dados_longo and len(self.dados_longo) >= 5:
            self._processar_bloco_dados(self.dados_longo, multiplicador_peso=1)
            
        if self.dados_recencia and len(self.dados_recencia) >= 5:
            self._processar_bloco_dados(self.dados_recencia, multiplicador_peso=3)

    def _processar_bloco_dados(self, dados, multiplicador_peso):
        for i in range(len(dados) - 2):
            estado_atual_cor = (dados[i]['cor'], dados[i+1]['cor'])
            proxima_cor = dados[i+2]['cor']
            num_atual = dados[i+1]['numero']
            
            for _ in range(multiplicador_peso):
                self.modelo_transicao[estado_atual_cor].append(proxima_cor)
                self.modelo_numerico[num_atual].append(proxima_cor)

    def predizer_proxima_casa(self, sub_num, sub_pol):
        if len(sub_num) < 12:
            return "NEUTRO", 0.0
        ultimo_num = sub_num[-1]
        ultimas_cores = (sub_pol[-2], sub_pol[-1])
        
        proximas_cores_historicas = self.modelo_transicao.get(ultimas_cores, [])
        proximas_cores_por_num = self.modelo_numerico.get(ultimo_num, [])
        
        peso_geometria = 0.75 if self.dados_recencia else 0.60
        peso_numerico = 0.25 if self.dados_recencia else 0.40
        
        total_v = (proximas_cores_historicas.count('V') * peso_geometria) + (proximas_cores_por_num.count('V') * peso_numerico)
        total_p = (proximas_cores_historicas.count('P') * peso_geometria) + (proximas_cores_por_num.count('P') * peso_numerico)
        total_b = (proximas_cores_historicas.count('B') * peso_geometria) + (proximas_cores_por_num.count('B') * peso_numerico)
        
        soma_pesos = total_v + total_p + total_b
        if soma_pesos == 0:
            return "NEUTRO", 0.0
        
        prob_v = (total_v / soma_pesos) * 100
        prob_p = (total_p / soma_pesos) * 100
        
        BARREIRA_CONFIA_IA = 62.0
        
        if prob_v >= BARREIRA_CONFIA_IA and prob_v > prob_p:
            return "VERMELHO", prob_v
        elif prob_p >= BARREIRA_CONFIA_IA and prob_p > prob_v:
            return "PRETO", prob_p
        return "NEUTRO", max(prob_v, prob_p)

class GerenciadorMemoriaViva:
    @staticmethod
    def injetar_rodadas_reais(sequencia_12, numeros_gales_reais, caminho_recencia="base_recencia_ativa.xlsx"):
        novas_linhas = []
        for num in sequencia_12:
            if num == 0: cor = 'B'
            elif 1 <= num <= 7: cor = 'V'
            else: cor = 'P'
            novas_linhas.append({"numero": int(num), "cor": cor})
            
        for num in numeros_gales_reais:
            if num == 0: cor = 'B'
            elif 1 <= num <= 7: cor = 'V'
            else: cor = 'P'
            novas_linhas.append({"numero": int(num), "cor": cor})

        df_novos = pd.DataFrame(novas_linhas)
        if os.path.exists(caminho_recencia):
            try:
                df_atual = pd.read_excel(caminho_recencia)
                df_consolidado = pd.concat([df_atual, df_novos], ignore_index=True)
                df_consolidado.to_excel(caminho_recencia, index=False)
            except:
                df_novos.to_excel(caminho_recencia, index=False)
        else:
            df_novos.to_excel(caminho_recencia, index=False)

class MotorNoCall:
    @staticmethod
    def checar_no_call(sub_num, sub_pol):
        cenarios_duplas = [(7, 8), (8, 9), (9, 10), (10, 11)]
        for idx1, idx2 in cenarios_duplas:
            if sub_num[idx1] == sub_num[idx2]:
                return True, f"Volume 2 Cap 6: Trava das Duplas Ativa nas posições {idx1+1}º-{idx2+1}º"

        posicoes_criticas_6 = [5, 8, 9, 10]
        for pos in posicoes_criticas_6:
            if sub_num[pos] == 6:
                return True, f"Volume 2 Cap 4: Trava Crítica do Número 6 Posicional na {pos+1}ª casa"

        posicoes_criticas_2 = [8, 9, 10, 11]
        for pos in posicoes_criticas_2:
            if sub_num[pos] == 2:
                return True, f"Volume 2 Cap 3: Trava Crítica do Número 2 Posicional na {pos+1}ª casa"

        posicoes_criticas_b = [5, 8, 9, 10, 11]
        for pos in posicoes_criticas_b:
            if sub_pol[pos] == "B":
                return True, f"Volume 2 Cap 5: Trava Crítica do Branco Posicional na {pos+1}ª casa"

        return False, "Evento Neutro Operacional"

class MotorContagensProjetivas:
    """Módulo de Coexistência e Dominância Normativa (Volume 3 e 12)"""
    @staticmethod
    def mapear_janela(sub_num, sub_pol, geometria_mercado):
        lista_bruta = []
        REGRAS_PROJECAO = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7}

        # 1. Varre os ativadores cronológicos base (Volume 3)
        for i in range(12):
            num_atual = sub_num[i]
            if num_atual in REGRAS_PROJECAO:
                passo = REGRAS_PROJECAO[num_atual]
                if i + passo == 11:
                    if i < 10 and 0 in sub_num[i:11]:
                        continue
                    if num_atual == 4:
                        direcao_sinal = "VERMELHO" if sub_pol[i] == "P" else "PRETO"
                        soberania = 2  # Nível 2 para o Ativador 4 posicional
                    elif num_atual == 6:
                        direcao_sinal = "PRETO" if "VERMELHO" not in geometria_mercado else "VERMELHO"
                        soberania = 1
                    else:
                        direcao_sinal = "PRETO" if "PRETO" in geometria_mercado else "VERMELHO"
                        soberania = 1
                    
                    lista_bruta.append({
                        "direcao": direcao_sinal,
                        "soberania": soberania,
                        "origem": f"Volume 3: Ativador {num_atual} na {i+1}ª casa"
                    })

        # 2. Varre os acoplamentos e resíduos numéricos (Volume 12 - Soberania Máxima Nível 3)
        if sub_num[11] == 4 and sub_pol[10] == "P":
            lista_bruta.append({"direcao": "PRETO", "soberania": 3, "origem": "Volume 12: Cap 5 - Retenção do 4 sob Base Preta"})
        elif sub_num[9] == 4 and sub_pol[10] == "P" and sub_pol[11] == "P":
            lista_bruta.append({"direcao": "PRETO", "soberania": 3, "origem": "Volume 12: Cap 5 - Acoplamento Posicional 4-P-P"})

        if sub_num[11] == 10:
            lista_bruta.append({"direcao": "PRETO", "soberania": 3, "origem": "Volume 12: Cap 2 - Resíduo do 10"})
        elif sub_num[10] == 5 and sub_num[11] == 10:
            lista_bruta.append({"direcao": "PRETO", "soberania": 3, "origem": "Volume 12: Cap 4 - Acoplamento 5-10"})

        if not lista_bruta:
            return []

        # 3. FILTRO DE DOMINÂNCIA ABSOLUTA (Uma regra assume a outra)
        # Encontra o maior nível de soberania presente na janela
        maior_soberania = max([item["soberania"] for item in lista_bruta])
        
        # Filtra a lista mantendo apenas as regras que possuem a soberania máxima encontrada
        lista_filtrada = [item for item in lista_bruta if item["soberania"] == maior_soberania]
        
        # Se mesmo no mesmo nível houver direções opostas, a recência cronológica da posição decide
        direcoes = list(set([d["direcao"] for d in lista_filtrada]))
        if len(direcoes) > 1:
            # Retorna o último gatilho detectado (mais próximo do fechamento)
            return [lista_filtrada[-1]]
            
        return lista_filtrada

class AnalisadorContextoAvancado:
    @staticmethod
    def calcular_numerologia_pos_numero(num_fechamento, sequencia_num, sequencia_pol):
        contagem_v, contagem_p, contagem_b = 0, 0, 0
        for i in range(len(sequencia_num) - 1):
            if sequencia_num[i] == num_fechamento:
                proxima_cor = sequencia_pol[i + 1]
                if proxima_cor == "V": contagem_v += 1
                elif proxima_cor == "P": contagem_p += 1
                elif proxima_cor == "B": contagem_b += 1

        total_ocorrencias = contagem_v + contagem_p + contagem_b
        if total_ocorrencias < 3:
            return "NEUTRO", 0.0

        pct_v = (contagem_v / total_ocorrencias) * 100
        pct_p = (contagem_p / total_ocorrencias) * 100

        if pct_v >= 60.0: return "VERMELHO", pct_v
        if pct_p >= 60.0: return "PRETO", pct_p
        return "NEUTRO", max(pct_v, pct_p)

    @staticmethod
    def mapear_padroes_geometria(sub_pol):
        texto_sub_pol = "".join(sub_pol)
        if texto_sub_pol.endswith("VPPV"): return "CICLO_FECHADO_VPPV"
        if texto_sub_pol.endswith("PVVP"): return "CICLO_FECHADO_PVVP"
        if "VVVV" in texto_sub_pol: return "SATURAÇÃO ESTRUTURAL (V)"
        if "PPPP" in texto_sub_pol: return "SATURAÇÃO ESTRUTURAL (P)"
        if "VPVPVP" in texto_sub_pol or "PVPVPV" in texto_sub_pol: return "XADREZ LONGO"
        if "VPVP" in texto_sub_pol or "PVPV" in texto_sub_pol: return "XADREZ ATIVO"
        return "ESTÁVEL"

    @staticmethod
    def detectar_chance_inversao(sub_pol):
        texto_sub_pol = "".join(sub_pol)
        
        if texto_sub_pol.endswith("VVVV"):
            bloco_anterior = texto_sub_pol[4:8]
            if bloco_anterior.count("V") >= 2:
                return True, "FALSO_RESPIRO", "Falso Respiro Detetado: Tendência macro forte de VERMELHO."
            return True, "INVERSÃO", "Exaustão Crítica de Fluxo: 4 Vermelhos Seguidos. Alerta de Quebra para PRETO."
            
        if texto_sub_pol.endswith("PPPP"):
            bloco_anterior = texto_sub_pol[4:8]
            if bloco_anterior.count("P") >= 2:
                return True, "FALSO_RESPIRO", "Falso Respiro Detetado: Tendência macro forte de PRETO."
            return True, "INVERSÃO", "Exaustão Crítica de Fluxo: 4 Pretos Seguidos. Alerta de Quebra para VERMELHO."
        
        if texto_sub_pol.endswith("VPVPVP") or texto_sub_pol.endswith("PVPVPV"):
            return True, "AVISO_XADREZ", "Alerta de Ciclo de Alternância Ativo."
            
        return False, "NORMAL", "Fluxo Inercial Estável."

    @staticmethod
    def preditor_estatistico_branco(num_fechamento, sequencia_num, sequencia_pol):
        if not sequencia_pol: return "BAIXA", 0
        atraso_atual = 0
        for cor in reversed(sequencia_pol):
            if cor == "B": break
            atraso_atual += 1

        vezes_numero_apareceu, vezes_chamou_branco = 0, 0
        for i in range(len(sequencia_num) - 1):
            if sequencia_num[i] == num_fechamento:
                vezes_numero_apareceu += 1
                horizonte_proximo = sequencia_pol[i+1 : min(i+4, len(sequencia_pol))]
                if "B" in horizonte_proximo: vezes_chamou_branco += 1

        taxa_atracao = (vezes_chamou_branco / vezes_numero_apareceu) * 100 if vezes_numero_apareceu > 0 else 0.0
        chance = "ALTA" if atraso_atual >= 15 or taxa_atracao >= 18.0 else ("MÉDIA" if atraso_atual >= 8 else "BAIXA")
        return chance, atraso_atual

class JuizHierarquicoModificado:
    @staticmethod
    def arbitrar_sinal(no_call_ativo, motivo_nc, expectativas, inclinacao_num, geometria_mercado, previsao_ia, status_inversao):
        if no_call_ativo: 
            return "NO CALL", motivo_nc

        risco_ativo, tipo_inversao, justificativa_inv = status_inversao
        direcao_ia, confianca_ia = previsao_ia
        direcao_inclinacao, porc = inclinacao_num
        direcoes_projetadas = list(set([e["direcao"] for e in expectativas]))

        if geometria_mercado == "CICLO_FECHADO_VPPV":
            if "VERMELHO" in direcoes_projetadas and direcao_ia == "PRETO":
                return "PRETO", "Fusão Normativa: Ciclo VPPV + Validação da IA convergem para PRETO"
            return "PRETO", "Volume 6 Cap 2: Fechamento de Ciclo Simétrico VPPV -> Forçando PRETO"
            
        if geometria_mercado == "CICLO_FECHADO_PVVP":
            if "PRETO" in direcoes_projetadas and direcao_ia == "VERMELHO":
                return "VERMELHO", "Fusão Normativa: Ciclo PVVP + Validação da IA convergem para VERMELHO"
            return "VERMELHO", "Volume 6 Cap 2: Fechamento de Ciclo Simétrico PVVP -> Forçando VERMELHO"

        if risco_ativo and tipo_inversao == "FALSO_RESPIRO":
            if expectativas:
                return direcoes_projetadas[0], f"Dominância Total: Regra Soberana assume o sinal -> {expectativas[0]['origem']}"
            cor_dominante = "VERMELHO" if "VERMELHO" in justificativa_inv else "PRETO"
            return cor_dominante, f"Volume 14 Cap 4 (Filtro Antirespiro): Mantendo {cor_dominante}."

        if risco_ativo and tipo_inversao == "INVERSÃO":
            sinal_inverso = "PRETO" if "Vermelhos Seguidos" in justificativa_inv else "VERMELHO"
            return sinal_inverso, f"Volume 14 Cap 2 (Intercepção de Exaustão): {justificativa_inv}"

        if expectativas:
            # Como a dominância já filtrou a melhor contagem antes, o Juiz executa direto sem gerar NO CALL por conflito
            return direcoes_projetadas[0], f"Sinal de Dominância Projetiva: {expectativas[0]['origem']}"
            
        if direcao_inclinacao != "NEUTRO" and porc >= 60.0:
            return direcao_inclinacao, f"Matriz Pós-Número: {porc:.1f}%"
        if direcao_ia != "NEUTRO" and confianca_ia >= 62.0:
            return direcao_ia, f"IA Preditiva: {confianca_ia:.1f}%"
        if direcao_ia != "NEUTRO":
            return direcao_ia, f"Vetor Direcional Recente: IA força entrada operativa para {direcao_ia} ({confianca_ia:.1f}%)"
            
        return "PRETO", "Veredito por Consenso de Fechamento Operacional"

class MotorV1Completo:
    def __init__(self, lista_dados_xls):
        self.seq = SequenciaOperacional(lista_dados_xls)
        corte_recencia = max(0, len(lista_dados_xls) - 150)
        dados_longo = lista_dados_xls[:corte_recencia]
        dados_curto = lista_dados_xls[corte_recencia:]
        self.ia = IAPreditivaV1(dados_longo, dados_curto)

    def processar_auditoria(self):
        idx = 0
        memorias_calculo = []
        janelas_auditadas = []
        stats = {"G0": 0, "G1": 0, "G2": 0, "FALHA": 0, "NO CALL": 0}

        while idx + 12 < self.seq.total:
            sub_num = self.seq.numerica[idx : idx + 12]
            sub_pol = self.seq.polaridades[idx : idx + 12]

            geometria = AnalisadorContextoAvancado.mapear_padroes_geometria(sub_pol)
            status_inv = AnalisadorContextoAvancado.detectar_chance_inversao(sub_pol)
            nc_ativo, motivo_nc = MotorNoCall.checar_no_call(sub_num, sub_pol)
            expectativas = MotorContagensProjetivas.mapear_janela(sub_num, sub_pol, geometria)

            num_fechamento = sub_num[-1]
            inclinacao_num = AnalisadorContextoAvancado.calcular_numerologia_pos_numero(num_fechamento, self.seq.numerica, self.seq.polaridades)
            previsao_ia = self.ia.predizer_proxima_casa(sub_num, sub_pol)
            
            expectativa_final, justificativa = JuizHierarquicoModificado.arbitrar_sinal(
                nc_ativo, motivo_nc, expectativas, inclinacao_num, geometria, previsao_ia, status_inv
            )

            horizonte_max = min(3, self.seq.total - (idx + 12))
            if horizonte_max == 0: break
            
            correcoes_reais = self.seq.polaridades[idx + 12 : idx + 12 + horizonte_max]
            classificacao = "FALHA"
            salto = 1

            if expectativa_final == "NO CALL":
                classificacao = "NO CALL RESPEITADO"
                stats["NO CALL"] += 1
                salto = 1
            else:
                letra_esperada = "V" if expectativa_final == "VERMELHO" else "P"
                for g_idx, cor_real in enumerate(correcoes_reais):
                    if cor_real == letra_esperada or cor_real == "B":
                        classificacao = f"G{g_idx}"
                        salto = g_idx + 1
                        break
                if classificacao == "FALHA": 
                    salto = 3
                stats[classificacao] += 1

            log_linha = f"Janela {len(janelas_auditadas) + 1}: {sub_num} -> Expectativa: {expectativa_final} -> Justificativa: {justificativa} -> Correção: {classificacao}"
            memorias_calculo.append(log_linha)
            janelas_auditadas.append(classificacao)
            idx += 12 + salto

        return self._gerar_relatorio_texto(memorias_calculo, stats, len(janelas_auditadas))

    def _gerar_relatorio_texto(self, memorias, stats, qtd_janelas):
        total_com_sinal = sum([stats["G0"], stats["G1"], stats["G2"], stats["FALHA"]])
        denominador = total_com_sinal if total_com_sinal > 0 else 1
        denominador_nc = qtd_janelas if qtd_janelas > 0 else 1

        p_g0 = (stats["G0"] / denominador) * 100
        p_g1 = (stats["G1"] / denominador) * 100
        p_g2 = (stats["G2"] / denominador) * 100
        p_fa = (stats["FALHA"] / denominador) * 100
        p_nc = (stats["NO CALL"] / denominador_nc) * 100

        if p_fa >= 25.0: condicao_mercado = "MERCADO EM DEGRADAÇÃO"
        elif p_g0 >= 50.0: condicao_mercado = "MERCADO PAGADOR"
        elif p_g1 >= 40.0: condicao_mercado = "MERCADO COM ATRASO CONTROLADO"
        else: condicao_mercado = "MERCADO INSTÁVEL"

        output = "[MEMÓRIA DE CÁLCULO DAS JANELAS MÓVEIS]\n" + "\n".join(memorias) + "\n\n"
        output += "[RESULTADO FINAL TIPO D]\n"
        output += f"TOTAL DE JANELAS AUDITADAS: {qtd_janelas}\n"
        output += f" - Taxa G0: {stats['G0']} ({p_g0:.2f}%)\n"
        output += f" - Taxa G1: {stats['G1']} ({p_g1:.2f}%)\n"
        output += f" - Taxa G2: {stats['G2']} ({p_g2:.2f}%)\n"
        output += f" - Taxa de Falha: {stats['FALHA']} ({p_fa:.2f}%)\n"
        output += f" - Taxa de NO CALL: {stats['NO CALL']} ({p_nc:.2f}%)\n\n"
        output += f"ESTADO ATUAL DO MERCADO: {condicao_mercado}\n"
        return output

class ProcessadorTipoB:
    def __init__(self, sequencia_12_numeros, caminho_base_dados):
        self.entrada_usuario = sequencia_12_numeros
        self.caminho_base = caminho_base_dados
        self.caminho_recencia = "base_recencia_ativa.xlsx"
        
        self.polaridades_usuario = []
        for num in self.entrada_usuario:
            if num == 0: self.polaridades_usuario.append("B")
            elif 1 <= num <= 7: self.polaridades_usuario.append("V")
            else: self.polaridades_usuario.append("P")

    def executar_sinal_real(self):
        if len(self.entrada_usuario) != 12: 
            return {"erro": "Requisito de exatamente 12 números violado."}
            
        leitor_longo = LeitorXLS(self.caminho_base)
        base_longo = leitor_longo.ler_e_validar()
        if not base_longo: return {"erro": "Base de dados ausente."}

        base_recencia = None
        if os.path.exists(self.caminho_recencia):
            leitor_recencia = LeitorXLS(self.caminho_recencia)
            base_recencia = leitor_recencia.ler_e_validar()

        num_global = [d['numero'] for d in base_longo]
        pol_global = [d['cor'] for d in base_longo]

        ia_operacional = IAPreditivaV1(base_longo, base_recencia)
        previsao_ia = ia_operacional.predizer_proxima_casa(self.entrada_usuario, self.polaridades_usuario)

        saturacao = AnalisadorContextoAvancado.mapear_padroes_geometria(self.polaridades_usuario)
        status_inv = AnalisadorContextoAvancado.detectar_chance_inversao(self.polaridades_usuario)
        nc_ativo, motivo_nc = MotorNoCall.checar_no_call(self.entrada_usuario, self.polaridades_usuario)
        expectativas = MotorContagensProjetivas.mapear_janela(self.entrada_usuario, self.polaridades_usuario, saturacao)
        
        num_fechamento = self.entrada_usuario[-1]
        inclinacao_num = AnalisadorContextoAvancado.calcular_numerologia_pos_numero(num_fechamento, num_global, pol_global)
        
        sinal_final, justificativa = JuizHierarquicoModificado.arbitrar_sinal(
            nc_ativo, motivo_nc, expectativas, inclinacao_num, saturacao, previsao_ia, status_inv
        )

        chance_branco, casas_atraso = AnalisadorContextoAvancado.preditor_estatistico_branco(num_fechamento, num_global, pol_global)
        status_recencia = "ATIVA (Peso Triplicado e Balanceamento de 75% Recente)" if base_recencia else "INATIVA"

        output_memoria = (
            f"- Mapeamento: Sequência {self.entrada_usuario}\n"
            f"- Geometria da Janela: {saturacao}\n"
            f"- Resolução de Conflitos: {justificativa}\n"
        )

        return {
            "sinal": sinal_final,
            "justificativa": justificativa,
            "memoria": output_memoria,
            "chance_branco": chance_branco,
            "atraso_branco": casas_atraso,
            "geometria": saturacao
        }

class LeitorXLS:
    def __init__(self, caminho_arquivo):
        self.caminho = caminho_arquivo

    def ler_e_validar(self):
        if not os.path.exists(self.caminho): return None
        try:
            try: df = pd.read_excel(self.caminho)
            except: df = pd.read_csv(self.caminho)
            df.columns = [str(col).strip().lower() for col in df.columns]
            mapeamento_colunas = {
                'val': 'numero', 'value': 'numero', 'num': 'numero', 'number': 'numero',
                'resultado': 'numero', 'roll': 'numero', 'giro': 'numero', 'spin': 'numero',
                'color': 'cor', 'cor': 'cor', 'result': 'cor'
            }
            df = df.rename(columns=mapeamento_colunas)
            colunas_atuais = df.columns.tolist()
            col_numero, col_cor = None, None
            for col in colunas_atuais:
                col_lower = str(col).lower().strip()
                if any(x in col_lower for x in ['val', 'num', 'number', 'roll', 'giro', 'spin']) and not any(x in col_lower for x in ['color', 'cor']):
                    col_numero = col
                if any(x in col_lower for x in ['color', 'cor']):
                    col_cor = col
            if col_numero is None and len(colunas_atuais) >= 1: col_numero = colunas_atuais[0]
            if col_cor is None and len(colunas_atuais) >= 2: col_cor = colunas_atuais[1]
            if col_numero is None or col_cor is None: return None
            df = df.rename(columns={col_numero: 'numero', col_cor: 'cor'})
            df_cronologico = df.iloc[::-1].reset_index(drop=True)
            if len(df_cronologico) < 15: return None
            LEGENDA_BRANCO = [0]
            LEGENDA_VERMELHO = [1, 2, 3, 4, 5, 6, 7]
            LEGENDA_PRETO = [8, 9, 10, 11, 12, 13, 14]
            dados_limpos = []
            for _, l in df_cronologico.iterrows():
                try:
                    num_val = int(l["numero"])
                    if num_val in LEGENDA_BRANCO: cor_final = 'B'
                    elif num_val in LEGENDA_VERMELHO: cor_final = 'V'
                    elif num_val in LEGENDA_PRETO: cor_final = 'P'
                    else: continue
                    dados_limpos.append({"numero": num_val, "cor": cor_final})
                except: continue
            return dados_limpos if dados_limpos else None
        except: return None
