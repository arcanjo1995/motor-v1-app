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
    def __init__(self, dados_limpos):
        self.dados = dados_limpos
        self.modelo_transicao = defaultdict(list)
        self.modelo_numerico = defaultdict(list)
        self._treinar_modelo()

    def _treinar_modelo(self):
        if not self.dados or len(self.dados) < 5:
            return
        for i in range(len(self.dados) - 2):
            estado_atual_cor = (self.dados[i]['cor'], self.dados[i+1]['cor'])
            proxima_cor = self.dados[i+2]['cor']
            self.modelo_transicao[estado_atual_cor].append(proxima_cor)
            num_atual = self.dados[i+1]['numero']
            self.modelo_numerico[num_atual].append(proxima_cor)

    def predizer_proxima_casa(self, sub_num, sub_pol):
        if len(sub_num) < 12:
            return "NEUTRO", 0.0
        ultimo_num = sub_num[-1]
        ultimas_cores = (sub_pol[-2], sub_pol[-1])
        proximas_cores_historicas = self.modelo_transicao.get(ultimas_cores, [])
        proximas_cores_por_num = self.modelo_numerico.get(ultimo_num, [])
        total_v = (proximas_cores_historicas.count('V') * 0.6) + (proximas_cores_por_num.count('V') * 0.4)
        total_p = (proximas_cores_historicas.count('P') * 0.6) + (proximas_cores_por_num.count('P') * 0.4)
        total_b = (proximas_cores_historicas.count('B') * 0.6) + (proximas_cores_por_num.count('B') * 0.4)
        soma_pesos = total_v + total_p + total_b
        if soma_pesos == 0:
            return "NEUTRO", 0.0
        prob_v = (total_v / soma_pesos) * 100
        prob_p = (total_p / soma_pesos) * 100
        BARREIRA_CONFIA_IA = 58.0
        if prob_v >= BARREIRA_CONFIA_IA and prob_v > prob_p:
            return "VERMELHO", prob_v
        elif prob_p >= BARREIRA_CONFIA_IA and prob_p > prob_v:
            return "PRETO", prob_p
        return "NEUTRO", max(prob_v, prob_p)

class MotorNoCall:
    @staticmethod
    def checar_no_call(sub_num, sub_pol):
        cenarios_duplas = [(7, 8), (8, 9), (9, 10), (10, 11)]
        for idx1, idx2 in cenarios_duplas:
            if sub_num[idx1] == sub_num[idx2]:
                return True, f"Volume 2 Cap 6: Trava das Duplas Ativa nas posições {idx1+1}º-{idx2+1}º ({sub_num[idx1]}-{sub_num[idx2]})"

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
    @staticmethod
    def mapear_janela(sub_num, sub_pol, geometria_mercado):
        expectativas = []
        REGRAS_PROJECAO = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7}

        for i in range(12):
            num_atual = sub_num[i]
            if num_atual in REGRAS_PROJECAO:
                passo = REGRAS_PROJECAO[num_atual]
                if i + passo == 11:
                    if i < 10 and 0 in sub_num[i:11]:
                        continue
                    if num_atual == 6:
                        direcao_sinal = "PRETO" if "VERMELHO" not in geometria_mercado else "VERMELHO"
                    else:
                        direcao_sinal = "PRETO" if "PRETO" in geometria_mercado else "VERMELHO"
                    expectativas.append({
                        "direcao": direcao_sinal,
                        "origem": f"Volume 3: Ativador {num_atual} na {i+1}ª casa"
                    })

        if sub_num[11] == 4 and sub_pol[10] == "P":
            expectativas.append({"direcao": "PRETO", "origem": "Volume 12: Cap 5 - Retenção do 4 sob Base Preta (Cenário 1/2)"})
        elif sub_num[9] == 4 and sub_pol[10] == "P" and sub_pol[11] == "P":
            expectativas.append({"direcao": "PRETO", "origem": "Volume 12: Cap 5 - Acoplamento Posicional 4-P-P (Cenário 3)"})

        if sub_num[11] == 10:
            expectativas.append({"direcao": "PRETO", "origem": "Volume 12: Cap 2 - Resíduo do 10"})
        elif sub_num[10] == 5 and sub_num[11] == 10:
            expectativas.append({"direcao": "PRETO", "origem": "Volume 12: Cap 4 - Acoplamento 5-10"})

        return expectativas

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

        if pct_v >= 55.0: return "VERMELHO", pct_v
        if pct_p >= 55.0: return "PRETO", pct_p
        return "NEUTRO", max(pct_v, pct_p)

    @staticmethod
    def mapear_padroes_geometria(sub_pol):
        texto_sub_pol = "".join(sub_pol)
        if "VVVV" in texto_sub_pol: return "SATURAÇÃO ESTRUTURAL (V)"
        if "PPPP" in texto_sub_pol: return "SATURAÇÃO ESTRUTURAL (P)"
        if "VPVPVP" in texto_sub_pol or "PVPVPV" in texto_sub_pol: return "XADREZ LONGO"
        if "VPVP" in texto_sub_pol or "PVPV" in texto_sub_pol: return "XADREZ ATIVO"
        return "ESTÁVEL"

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
    def arbitrar_sinal(no_call_ativo, motivo_nc, expectativas, inclinacao_num, geometria_mercado, previsao_ia):
        if no_call_ativo: 
            return "NO CALL", motivo_nc

        direcao_ia, confianca_ia = previsao_ia
        direcao_inclinacao, porc = inclinacao_num
        direcoes_projetadas = list(set([e["direcao"] for e in expectativas]))

        if expectativas:
            if len(direcoes_projetadas) > 1:
                if direcao_ia in direcoes_projetadas:
                    return direcao_ia, f"Volume 18: Conflito resolvido por Validação da IA ({confianca_ia:.1f}%)"
                if direcao_inclinacao in direcoes_projetadas and porc >= 55.0:
                    return direcao_inclinacao, f"Volume 18: Conflito resolvido por Inclinação Histórica ({porc:.1f}%)"
                return "NO CALL", "Volume 18: Conflito Hierárquico Sem Consenso (Cenário de Risco)"
            return direcoes_projetadas[0], expectativas[0]["origem"]
            
        if direcao_inclinacao != "NEUTRO" and porc >= 55.0:
            if direcao_ia == direcao_inclinacao:
                return direcao_inclinacao, f"Matriz + IA Unificadas: Alinhamento de Tendência Global com {confianca_ia:.1f}%"
            return direcao_inclinacao, f"Matriz Pós-Número Padrão: Tendência Proporcional de {porc:.1f}%"
            
        if direcao_ia != "NEUTRO" and confianca_ia >= 58.0:
            return direcao_ia, f"IA Preditiva Isolada: Fluxo Direcional Recente Confirmado de {confianca_ia:.1f}%"

        if direcao_inclinacao != "NEUTRO":
            return direcao_inclinacao, f"Desempate de Bloco Inercial: Inclinação Majoritária de {porc:.1f}%"
        if direcao_ia != "NEUTRO":
            return direcao_ia, f"Desempate de Bloco Inercial: Vetor Direcional da IA de {confianca_ia:.1f}%"
            
        return "PRETO", "Arbitragem de Bloco Inercial de Fechamento por Consenso"

class MotorV1Completo:
    def __init__(self, lista_dados_xls):
        self.seq = SequenciaOperacional(lista_dados_xls)
        self.ia = IAPreditivaV1(lista_dados_xls)

    def processar_auditoria(self):
        idx = 0
        memorias_calculo = []
        janelas_auditadas = []
        stats = {"G0": 0, "G1": 0, "G2": 0, "FALHA": 0, "NO CALL": 0}

        while idx + 12 < self.seq.total:
            sub_num = self.seq.numerica[idx : idx + 12]
            sub_pol = self.seq.polaridades[idx : idx + 12]

            geometria = AnalisadorContextoAvancado.mapear_padroes_geometria(sub_pol)
            nc_ativo, motivo_nc = MotorNoCall.checar_no_call(sub_num, sub_pol)
            expectativas = MotorContagensProjetivas.mapear_janela(sub_num, sub_pol, geometria)

            num_fechamento = sub_num[-1]
            inclinacao_num = AnalisadorContextoAvancado.calcular_numerologia_pos_numero(num_fechamento, self.seq.numerica, self.seq.polaridades)
            previsao_ia = self.ia.predizer_proxima_casa(sub_num, sub_pol)
            
            expectativa_final, justificativa = JuizHierarquicoModificado.arbitrar_sinal(
                nc_ativo, motivo_nc, expectativas, inclinacao_num, geometria, previsao_ia
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

        if p_fa >= 25.0:
            condicao_mercado = "MERCADO EM DEGRADAÇÃO (Risco Elevado de Falhas)"
            degradacao = "FORTE"
            recuperacao = "INEXISTENTE"
        elif p_g0 >= 50.0:
            condicao_mercado = "MERCADO PAGADOR (Predominância de G0 Ativo)"
            degradacao = "INEXISTENTE"
            recuperacao = "FORTE"
        elif p_g1 >= 40.0:
            condicao_mercado = "MERCADO COM ATRASO CONTROLADO (Foco em G1)"
            degradacao = "LEVE"
            recuperacao = "MODERADA"
        elif p_g2 >= 30.0:
            condicao_mercado = "MERCADO DESLOCADO (G0 Enfraquecido / Alerta G2)"
            degradacao = "MODERADA"
            recuperacao = "FRACA"
        else:
            condicao_mercado = "MERCADO INSTÁVEL (Oscilação Excessiva de Vetores)"
            degradacao = "MEDIANA"
            recuperacao = "MEDIANA"

        output = "[MEMÓRIA DE CÁLCULO DAS JANELAS MÓVEIS]\n" + "\n".join(memorias) + "\n\n"
        output += "[RESULTADO FINAL TIPO D]\n"
        output += f"CRONOLOGIA VALIDADA: {self.seq.total} Resultados Reconstruídos\n"
        output += f"TOTAL DE JANELAS AUDITADAS: {qtd_janelas} Saltos Sequenciais\n"
        output += f" - Taxa G0: {stats['G0']} Ocorrências ({p_g0:.2f}%)\n"
        output += f" - Taxa G1: {stats['G1']} Ocorrências ({p_g1:.2f}%)\n"
        output += f" - Taxa G2: {stats['G2']} Ocorrências ({p_g2:.2f}%)\n"
        output += f" - Taxa de Falha: {stats['FALHA']} Ocorrências ({p_fa:.2f}%)\n"
        output += f" - Taxa de NO CALL: {stats['NO CALL']} Ocorrências ({p_nc:.2f}%)\n\n"
        output += f"DEGRADAÇÃO EVOLUTIVA: {degradacao}\n"
        output += f"RECUPERAÇÃO EVOLUTIVA: {recuperacao}\n"
        output += f"ESTADO ATUAL DO MERCADO: {condicao_mercado}\n"
        return output

class ProcessadorTipoB:
    def __init__(self, sequencia_12_numeros, caminho_base_dados):
        self.entrada_usuario = sequencia_12_numeros
        self.caminho_base = caminho_base_dados
        
        self.polaridades_usuario = []
        for num in self.entrada_usuario:
            if num == 0: 
                self.polaridades_usuario.append("B")
            elif 1 <= num <= 7: 
                self.polaridades_usuario.append("V")
            else: 
                self.polaridades_usuario.append("P")

    def executar_sinal_real(self):
        if len(self.entrada_usuario) != 12: 
            return "[ERRO] Requisito de exatamente 12 números violado."
            
        leitor = LeitorXLS(self.caminho_base)
        base_historica = leitor.ler_e_validar()
        if not base_historica: 
            return "[ERRO] Base de dados resultados_blaze.xlsx ausente."

        num_global = [d['numero'] for d in base_historica]
        pol_global = [d['cor'] for d in base_historica]

        ia_operacional = IAPreditivaV1(base_historica)
        previsao_ia = ia_operacional.predizer_proxima_casa(self.entrada_usuario, self.polaridades_usuario)

        saturacao = AnalisadorContextoAvancado.mapear_padroes_geometria(self.polaridades_usuario)
        nc_ativo, motivo_nc = MotorNoCall.checar_no_call(self.entrada_usuario, self.polaridades_usuario)
        expectativas = MotorContagensProjetivas.mapear_janela(self.entrada_usuario, self.polaridades_usuario, saturacao)
        
        num_fechamento = self.entrada_usuario[-1]
        inclinacao_num = AnalisadorContextoAvancado.calcular_numerologia_pos_numero(num_fechamento, num_global, pol_global)
        
        sinal_final, justificativa = JuizHierarquicoModificado.arbitrar_sinal(
            nc_ativo, motivo_nc, expectativas, inclinacao_num, saturacao, previsao_ia
        )

        chance_branco, casas_atraso = AnalisadorContextoAvancado.preditor_estatistico_branco(num_fechamento, num_global, pol_global)

        output = "[MEMÓRIA DE CÁLCULO]\n"
        output += f"- Mapeamento: Sequência {self.entrada_usuario} processada.\n"
        output += f"- Geometria da Janela: {saturacao}\n"
        output += f"- Previsão IA: {previsao_ia[0]} ({previsao_ia[1]:.1f}%)\n"
        output += f"- Inclinação Histórica ({num_fechamento}): {inclinacao_num[0]} ({inclinacao_num[1]:.1f}%)\n"
        output += f"- Resolução de Conflitos: {justificativa}\n\n"
        output += "[RESULTADO FINAL TIPO B]\n"
        output += f"SINAL: {sinal_final}\n"
        output += f"BRANCO: {chance_branco} CHANCE (Atraso: {casas_atraso} rodadas)\n"
        output += f"ESTADO DO MERCADO: {saturacao}\n"
        return output

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
