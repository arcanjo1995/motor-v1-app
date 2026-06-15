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
        self.dados_recencia = dados_recencia if dados_recencia else []
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

    def injetar_aprendizado_imediato(self, sub_dados, multiplicador_peso=3):
        self._processar_bloco_dados(sub_dados, multiplicador_peso)

    def predizer_proxima_casa(self, sub_num, sub_pol):
        if len(sub_num) < 12:
            return "NEUTRO", 0.0
        ultimo_num = sub_num[-1]
        ultimas_cores = (sub_pol[-2], sub_pol[-1])
        
        proximas_cores_historicas = self.modelo_transicao.get(ultimas_cores, [])
        proximas_cores_por_num = self.modelo_numerico.get(ultimo_num, [])
        
        has_recencia = len(self.dados_recencia) > 0 or len(self.modelo_transicao) > 0
        peso_geometria = 0.75 if has_recencia else 0.60
        peso_numerico = 0.25 if has_recencia else 0.40
        
        total_v = (proximas_cores_historicas.count('V') * peso_geometria) + (proximas_cores_por_num.count('V') * peso_numerico)
        total_p = (proximas_cores_historicas.count('P') * peso_geometria) + (proximas_cores_por_num.count('P') * peso_numerico)
        
        soma_pesos = total_v + total_p
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
            cor = 'B' if num == 0 else ('V' if 1 <= num <= 7 else 'P')
            novas_linhas.append({"numero": int(num), "cor": cor})
            
        for num in numeros_gales_reais:
            cor = 'B' if num == 0 else ('V' if 1 <= num <= 7 else 'P')
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
                return True, "Volume 2 Cap 6: Trava das Duplas Ativa"

        posicoes_criticas_6 = [5, 8, 9, 10]
        for pos in posicoes_criticas_6:
            if sub_num[pos] == 6:
                return True, "Volume 2 Cap 4: Trava Número 6"

        posicoes_criticas_2 = [8, 9, 10, 11]
        for pos in posicoes_criticas_2:
            if sub_num[pos] == 2:
                return True, "Volume 2 Cap 3: Trava Número 2"

        posicoes_criticas_b = [5, 8, 9, 10, 11]
        for pos in posicoes_criticas_b:
            if sub_pol[pos] == "B":
                return True, "Volume 2 Cap 5: Trava do Branco"

        return False, "Evento Neutro Operacional"

class MotorContagensProjetivas:
    @staticmethod
    def mapear_janela(sub_num, sub_pol, geometria_mercado):
        lista_bruta = []
        REGRAS_PROJECAO = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7}

        for i in range(12):
            num_atual = sub_num[i]
            if num_atual in REGRAS_PROJECAO:
                passo = REGRAS_PROJECAO[num_atual]
                
                if i + passo == 11:
                    if i < 10 and 0 in sub_num[i:11]: continue
                    direcao_sinal = "VERMELHO" if sub_pol[i] == "P" else "PRETO"
                    lista_bruta.append({
                        "direcao": direcao_sinal,
                        "tipo_regra": f"V3_ATIVADOR_{num_atual}",
                        "origem": f"Volume 3: Ativador {num_atual} direto no fechamento"
                    })
                
                elif i + passo < 11:
                    alvo_interno_idx = i + passo
                    cor_alvo_interno = sub_pol[alvo_interno_idx]
                    
                    # Correção de simetria do vetor dinâmico para evitar falsas inversões
                    if cor_alvo_interno == sub_pol[i]:
                        direcao_sinal = "PRETO" if cor_alvo_interno == "V" else "VERMELHO"
                    else:
                        direcao_sinal = "VERMELHO" if sub_pol[i] == "V" else "PRETO"
                        
                    lista_bruta.append({
                        "direcao": direcao_sinal,
                        "tipo_regra": f"V3_CADEIA_{num_atual}",
                        "origem": f"Volume 3: Repercussão em Cadeia do Ativador {num_atual} da {i+1}ª para a {alvo_interno_idx+1}ª casa"
                    })

        if sub_num[11] == 4 and sub_pol[10] == "P":
            lista_bruta.append({"direcao": "PRETO", "tipo_regra": "V12_RETENCAO_4", "origem": "Volume 12: Cap 5 - Retenção do 4 sob Base Preta"})
        elif sub_num[9] == 4 and sub_pol[10] == "P" and sub_pol[11] == "P":
            lista_bruta.append({"direcao": "PRETO", "tipo_regra": "V12_ACOPLAMENTO_4PP", "origem": "Volume 12: Cap 5 - Acoplamento Posicional 4-P-P"})

        if sub_num[11] == 10:
            lista_bruta.append({"direcao": "PRETO", "tipo_regra": "V12_RESIDUO_10", "origem": "Volume 12: Cap 2 - Resíduo do 10"})
        elif sub_num[10] == 5 and sub_num[11] == 10:
            lista_bruta.append({"direcao": "PRETO", "tipo_regra": "V12_ACOPLAMENTO_5_10", "origem": "Volume 12: Cap 4 - Acoplamento 5-10"})

        return lista_bruta

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
                return True, "FALSO_RESPIRO", "Falso Respiro: Tendência forte de VERMELHO."
            return True, "INVERSÃO", "Exaustão: 4 Vermelhos Seguidos. Quebra para PRETO."
            
        if texto_sub_pol.endswith("PPPP"):
            bloco_anterior = texto_sub_pol[4:8]
            if bloco_anterior.count("P") >= 2:
                return True, "FALSO_RESPIRO", "Falso Respiro: Tendência forte de PRETO."
            return True, "INVERSÃO", "Exaustão: 4 Pretos Seguidos. Quebra para VERMELHO."
        
        if texto_sub_pol.endswith("VPVPVP") or texto_sub_pol.endswith("PVPVPV"):
            return True, "AVISO_XADREZ", "Alerta de Ciclo de Alternância Ativo."
            
        return False, "NORMAL", "Fluxo Estável."

class JuizHierarquicoModificado:
    @staticmethod
    def arbitrar_sinal(no_call_ativo, motivo_nc, expectations, inclinacao_num, geometria_mercado, previsao_ia, status_inversao, historico_revalida_regras):
        if no_call_ativo: 
            return "NO CALL", motivo_nc, "SISTEMA_TRAVADO"

        # Correção ortográfica do bug de escopo que quebrava o PVVP/VPPV
        if geometria_mercado == "CICLO_FECHADO_VPPV":
            return "PRETO", "Geometria VPPV -> Alvo PRETO", "GEOMETRIA"
            
        if geometria_mercado == "CICLO_FECHADO_PVVP":
            return "VERMELHO", "Geometria PVVP -> Alvo VERMELHO", "GEOMETRIA"

        risco_ativo, tipo_inversao, justificativa_inv = status_inversao
        direcao_ia, confianca_ia = previsao_ia
        direcao_inclinacao, porc = inclinacao_num

        sinal_projetado = None
        justificativa_proj = ""
        regra_vencedora_id = "NENHUMA"
        
        if expectations:
            forcas = {"VERMELHO": 0.0, "PRETO": 0.0}
            origens = {"VERMELHO": [], "PRETO": []}
            maior_peso_id = {"VERMELHO": ("NENHUMA", 0.0), "PRETO": ("NENHUMA", 0.0)}
            
            for item in expectations:
                id_r = item["tipo_regra"]
                taxa_acerto_recente = historico_revalida_regras[id_r]["acertos"] / max(1, historico_revalida_regras[id_r]["total"])
                
                base_soberania = 3.0
                peso_vivo = base_soberania * (1.0 + taxa_acerto_recente)
                
                forcas[item["direcao"]] += peso_vivo
                origens[item["direcao"]].append(f"{item['origem']} [Peso Vivo: {peso_vivo:.1f}]")
                
                if peso_vivo > maior_peso_id[item["direcao"]][1]:
                    maior_peso_id[item["direcao"]] = (id_r, peso_vivo)
                
            if forcas["VERMELHO"] != forcas["PRETO"]:
                sinal_dominante = "VERMELHO" if forcas["VERMELHO"] > forcas["PRETO"] else "PRETO"
                sinal_oposto = "PRETO" if sinal_dominante == "VERMELHO" else "VERMELHO"
                regra_vencedora_id = maior_peso_id[sinal_dominante][0]
                
                # Ajuste Fino Anti-Esmagamento: Só entrega para a IA se ela tiver alta confiança absoluta (>65%)
                if forcas[sinal_oposto] > 0 and direcao_ia != "NEUTRO" and confianca_ia > 65.0:
                    sinal_projetado = direcao_ia
                    justificativa_proj = f"Veredito de Recência Extrema: IA ({confianca_ia:.1f}%) assume o controle do choque de matrizes."
                    regra_vencedora_id = "IA_ARBITRAGEM_CHOQUE"
                else:
                    sinal_projetado = sinal_dominante
                    justificativa_proj = "Dominância Recente Dinâmica: " + " + ".join(origens[sinal_dominante])
            else:
                if direcao_ia != "NEUTRO":
                    sinal_projetado = direcao_ia
                    justificativa_proj = f"Coexistência Empatada resolvida por IA de Recência ({confianca_ia:.1f}%)"
                    regra_vencedora_id = "IA_DESEMPATE"
                else:
                    sinal_projetado = expectations[-1]["direcao"]
                    justificativa_proj = f"Coexistência Empatada resolvida por Proximidade: {expectations[-1]['origem']}"
                    regra_vencedora_id = expectations[-1]["tipo_regra"]

        if risco_ativo and tipo_inversao == "FALSO_RESPIRO":
            if sinal_projetado:
                return sinal_projetado, f"Filtro Cruzado Futuro: {justificativa_proj}", regra_vencedora_id
            cor_dominante = "VERMELHO" if "VERMELHO" in justificativa_inv else "PRETO"
            return cor_dominante, f"Filtro Antirespiro: Mantendo {cor_dominante}.", "ANTI_RESPIRO"

        if risco_ativo and tipo_inversao == "INVERSÃO":
            if sinal_projetado:
                return sinal_projetado, f"Filtro Cruzado Futuro: {justificativa_proj}", regra_vencedora_id
            sinal_inverso = "PRETO" if "Vermelhos Seguidos" in justificativa_inv else "VERMELHO"
            return sinal_inverso, f"Intercepção de Exaustão (4 Casas): {justificativa_inv}", "INVERSION_REAL"

        if sinal_projetado:
            return sinal_projetado, justificativa_proj, regra_vencedora_id
            
        if direcao_inclinacao != "NEUTRO" and porc >= 60.0:
            return direcao_inclinacao, f"Matriz Pós-Número: {porc:.1f}%", "MATRIZ_INCLINA"
        if direcao_ia != "NEUTRO" and confianca_ia >= 62.0:
            return direcao_ia, f"IA Preditiva: {confianca_ia:.1f}%", "IA_PREDITIVA"
        if direcao_ia != "NEUTRO":
            return direcao_ia, f"Vetor Recente IA: {direcao_ia} ({confianca_ia:.1f}%)", "IA_VETOR"
            
        return "PRETO", "Consenso Operacional", "CONSENSO_FECHAMENTO"

class MotorV1Completo:
    def __init__(self, lista_dados_xls):
        self.seq = SequenciaOperacional(lista_dados_xls)
        corte_recencia = max(0, len(lista_dados_xls) - 150)
        self.dados_longo = lista_dados_xls[:corte_recencia]
        self.dados_curto = lista_dados_xls[corte_recencia:]
        self.ia = IAPreditivaV1(self.dados_longo, self.dados_curto)
        self.historico_regras = defaultdict(lambda: {"acertos": 1, "total": 1})

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
            
            expectativa_final, justificativa, regra_ativa_id = JuizHierarquicoModificado.arbitrar_sinal(
                nc_ativo, motivo_nc, expectativas, inclinacao_num, geometria, previsao_ia, status_inv, self.historico_regras
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

            if regra_ativa_id != "NENHUMA" and regra_ativa_id != "SISTEMA_TRAVADO":
                self.historico_regras[regra_ativa_id]["total"] += 1
                if classificacao in ["G0", "G1"]:
                    self.historico_regras[regra_ativa_id]["acertos"] += 1

            bloco_vivido = []
            for k in range(idx, min(idx + 12 + salto, self.seq.total)):
                bloco_vivido.append({"numero": self.seq.numerica[k], "cor": self.seq.polaridades[k]})
            self.ia.injetar_learned_immediate = self.ia.injetar_aprendizado_imediato(bloco_vivido, multiplicador_peso=3)

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

        condicao_mercado = "MERCADO INSTÁVEL"
        if p_fa >= 25.0: condicao_mercado = "MERCADO EM DEGRADAÇÃO"
        elif p_g0 >= 50.0: condicao_mercado = "MERCADO PAGADOR"
        elif p_g1 >= 40.0: condicao_mercado = "MERCADO COM ATRASO CONTROLADO"

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
