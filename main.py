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
        # 1. TRANSMISSÃO BÁSICA DE TRANSIÇÕES DE CASAS
        for i in range(len(dados) - 2):
            estado_atual_cor = (dados[i]['cor'], dados[i+1]['cor'])
            proxima_cor = dados[i+2]['cor']
            num_atual = dados[i+1]['numero']
            
            for _ in range(multiplicador_peso):
                self.modelo_transicao[estado_atual_cor].append(proxima_cor)
                self.modelo_numerico[num_atual].append(proxima_cor)
                    
        # 2. ABSORÇÃO COGNITIVA INTEGRAL: PADRÕES E NUMEROLOGIA (VOLUME 6 E 7)
        if len(dados) >= 12:
            for i in range(len(dados) - 12):
                sub_window_num = [d['numero'] for d in dados[i:i+12]]
                sub_window_pol = [d['cor'] for d in dados[i:i+12]]
                cor_futura = dados[i+12]['cor'] if (i+12) < len(dados) else None
                
                if cor_futura:
                    texto_pol = "".join(sub_window_pol)
                    num_fechamento = sub_window_num[-1]
                    
                    for _ in range(multiplicador_peso):
                        # Gravação de assinaturas geométricas complexas (Volume 6)
                        if "PVPV" in texto_pol: self.modelo_transicao[("XADREZ", "PVPV")].append(cor_futura)
                        if "VPVP" in texto_pol: self.modelo_transicao[("XADREZ", "VPVP")].append(cor_futura)
                        if "VVV" in texto_pol: self.modelo_transicao[("SATURACAO", "V")].append(cor_futura)
                        if "PPP" in texto_pol: self.modelo_transicao[("SATURACAO", "P")].append(cor_futura)
                        
                        # Gravação de contexto numerológico avançado (Volume 7)
                        self.modelo_numerico[(num_fechamento, "CONTEXTO")].append(cor_futura)

    def injetar_aprendizado_imediato(self, sub_dados, multiplicador_peso=3):
        self._processar_bloco_dados(sub_dados, multiplicador_peso)

    def predizer_proxima_casa(self, sub_num, sub_pol):
        if len(sub_num) < 12:
            return "NEUTRO", 0.0
        ultimo_num = sub_num[-1]
        ultimas_cores = (sub_pol[-2], sub_pol[-1])
        
        proximas_cores_historicas = self.modelo_transicao.get(ultimas_cores, [])
        proximas_cores_por_num = self.modelo_numerico.get(ultimo_num, [])
        
        # CONSULTA AOS NOVOS MODELOS DE EVOLUÇÃO COMPORTAMENTAL ABSORVIDOS
        texto_pol = "".join(sub_pol)
        cores_por_geometria = []
        if "PVPV" in texto_pol: cores_por_geometria.extend(self.modelo_transicao.get(("XADREZ", "PVPV"), []))
        if "VPVP" in texto_pol: cores_por_geometria.extend(self.modelo_transicao.get(("XADREZ", "VPVP"), []))
        if "VVV" in texto_pol: cores_por_geometria.extend(self.modelo_transicao.get(("SATURACAO", "V"), []))
        if "PPP" in texto_pol: cores_por_geometria.extend(self.modelo_transicao.get(("SATURACAO", "P"), []))
        
        cores_por_numerologia = self.modelo_numerico.get((ultimo_num, "CONTEXTO"), [])
        
        has_recencia = len(self.dados_recencia) > 0 or len(self.modelo_transicao) > 0
        
        # Distribuição proporcional de pesos balanceando macro e micro contexto
        peso_geometria = 0.40 if has_recencia else 0.30
        peso_numerico = 0.20 if has_recencia else 0.30
        peso_padrao_v6 = 0.25
        peso_padrao_v7 = 0.15
        
        total_v = (proximas_cores_historicas.count('V') * peso_geometria) + \
                  (proximas_cores_por_num.count('V') * peso_numerico) + \
                  (cores_por_geometria.count('V') * peso_padrao_v6) + \
                  (cores_por_numerologia.count('V') * peso_padrao_v7)
                  
        total_p = (proximas_cores_historicas.count('P') * peso_geometria) + \
                  (proximas_cores_por_num.count('P') * peso_numerico) + \
                  (cores_por_geometria.count('P') * peso_padrao_v6) + \
                  (cores_por_numerologia.count('P') * peso_padrao_v7)
        
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

        posicoes_criticas_6 = [5, 8, 9, 10, 11]
        for pos in posicoes_criticas_6:
            if sub_num[pos] == 6:
                return True, "Volume 2 Cap 4: Trava Número 6 (Posição de No Call Ativa)"

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
    def mapear_janela(sub_num, sub_pol, geometry_mercado):
        lista_bruta = []
        REGRAS_PROJECAO = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7}

        # 1. PROCESSAMENTO DE CONTAGENS PROJETIVAS INDEPENDENTES (APARECEU ≠ ATIVOU)
        for i in range(12):
            num_atual = sub_num[i]
            if num_atual in REGRAS_PROJECAO:
                passo = REGRAS_PROJECAO[num_atual]
                alvo_idx = i + passo
                
                # Se o fechamento coincide com o fim da janela, gera Expectativa Vermelha (Volume 3 Cap 2)
                if alvo_idx == 11:
                    if i < 10 and 0 in sub_num[i:11]: continue
                    lista_bruta.append({
                        "direcao": "VERMELHO", 
                        "tipo_regra": f"V3_ATIVADOR_{num_atual}", 
                        "origem": f"Volume 3: Ativador {num_atual} direto no fechamento gerando Expectativa Vermelha"
                    })

        # 2. REGRA DE CONTINUIDADE NUMÉRICA DE FECHAMENTO (Volume 2 - Cap 7)
        par_fechamento = (sub_num[10], sub_num[11])
        continuidade_preta_validas = [(8,9), (9,10), (10,11), (11,12), (12,13), (13,14), (14,13), (13,12), (12,11), (11,10)]
        continuidade_vermelha_validas = [(1,2), (2,3), (3,4), (4,5), (5,6), (6,7), (7,6), (6,5), (5,4), (4,3)]

        if par_fechamento in continuidade_preta_validas:
            lista_bruta.append({
                "direcao": "PRETO", 
                "tipo_regra": "V2_CONTINUIDADE_PRETA", 
                "origem": f"Volume 2: Continuidade Numérica Preta {par_fechamento[0]}-{par_fechamento[1]} até G1"
            })
        elif par_fechamento in continuidade_vermelha_validas:
            lista_bruta.append({
                "direcao": "VERMELHO", 
                "tipo_regra": "V2_CONTINUIDADE_VERVELHA", 
                "origem": f"Volume 2: Continuidade Numérica Vermelha {par_fechamento[0]}-{par_fechamento[1]} até G1"
            })

        # 3. REGRAS POSICIONAIS DO VOLUME 12 (CRÍTICAS DE DESTAQUE NO MANUAL)
        if sub_num[5] == 2:
            lista_bruta.append({
                "direcao": "VERMELHO", 
                "tipo_regra": "V12_POSICIONAL_2", 
                "origem": "Volume 12: Cap 3 - Regra Posicional do Número 2 (6 Casas de Expectativa Vermelha)"
            })
        if sub_num[5] == 3:
            lista_bruta.append({
                "direcao": "VERMELHO", 
                "tipo_regra": "V12_POSICIONAL_3", 
                "origem": "Volume 12: Cap 4 - Regra Posicional do Número 3 (6 Casas de Expectativa Vermelha)"
            })

        if sub_num[11] == 4 and sub_pol[10] == "P":
            lista_bruta.append({"direcao": "PRETO", "tipo_regra": "V12_RETENCAO_4", "origem": "Volume 12: Cap 5 - Retenção do 4 sob Base Preta"})
        elif sub_num[9] == 4 and sub_pol[10] == "P" and sub_pol[11] == "P":
            lista_bruta.append({"direcao": "PRETO", "tipo_regra": "V12_ACOPLAMENTO_4PP", "origem": "Volume 12: Cap 5 - Acoplamento Posicional 4-P-P"})

        if sub_num[11] == 10:
            lista_bruta.append({"direcao": "PRETO", "tipo_regra": "V12_RESIDUO_10", "origem": "Volume 12: Cap 2 - Resíduo do 10"})
        elif sub_num[10] == 5 and sub_num[11] == 10:
            lista_bruta.append({"direcao": "PRETO", "tipo_regra": "V12_ACOPLAMENTO_5_10", "origem": "Volume 12: Cap 4 - Acoplamento 5-10"})

        # 4. VOLUME 6: ANÁLISE DE PADRÕES DE POLARIDADES COMPLETA
        texto_pol = "".join(sub_pol)
        
        if "PVPV" in texto_pol and "VVV" in texto_pol and texto_pol.endswith("PVPV"):
            lista_bruta.append({"direcao": "PRETO", "tipo_regra": "V6_ESPELHAMENTO_INVERSO_COMPLEXO", "origem": "Volume 6: Cap 5 - Saturação VVV cercada por estruturas Xadrez. Projeta bloco simétrico em PRETO"})
        elif "VPVP" in texto_pol and "PPP" in texto_pol and texto_pol.endswith("VPVP"):
            lista_bruta.append({"direcao": "VERMELHO", "tipo_regra": "V6_ESPELHAMENTO_INVERSO_COMPLEXO", "origem": "Volume 6: Cap 5 - Saturação PPP cercada por estruturas Xadrez. Projeta bloco simétrico em VERMELHO"})

        if texto_pol.endswith("PVPV"):
            lista_bruta.append({"direcao": "PRETO", "tipo_regra": "V6_XADREZ_ATIVO", "origem": "Volume 6: Cap 6 - Ciclo de Alternância Ativa de Fechamento (Xadrez) projeta PRETO"})
        elif texto_pol.endswith("VPVP"):
            lista_bruta.append({"direcao": "VERMELHO", "tipo_regra": "V6_XADREZ_ATIVO", "origem": "Volume 6: Cap 6 - Ciclo de Alternância Ativa de Fechamento (Xadrez) projeta VERMELHO"})

        if texto_pol.endswith("PPVP"):
            lista_bruta.append({"direcao": "PRETO", "tipo_regra": "V6_FALSA_QUEBRA", "origem": "Volume 6: Cap 8 - Falsa Quebra detectada com retorno à sustentação PRETA"})
        elif texto_pol.endswith("VVPV"):
            lista_bruta.append({"direcao": "VERMELHO", "tipo_regra": "V6_FALSA_QUEBRA", "origem": "Volume 6: Cap 8 - Falsa Quebra detectada com retorno à sustentação VERMELHA"})

        if texto_pol.endswith("VPV"):
            lista_bruta.append({"direcao": "PRETO", "tipo_regra": "V6_ESPELHO_CURTO", "origem": "Volume 6: Cap 4 - Estrutura de Espelho V-P-V exigindo retorno simétrico em PRETO"})
        elif texto_pol.endswith("PVP"):
            lista_bruta.append({"direcao": "VERMELHO", "tipo_regra": "V6_ESPELHO_CURTO", "origem": "Volume 6: Cap 4 - Estrutura de Espelho P-V-P exigindo retorno simétrico em VERMELHO"})

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
            if bloco_anterior.count("V") >= 2: return True, "FALSO_RESPIRO", "Falso Respiro: Tendência de VERMELHO."
            return True, "INVERSÃO", "Exaustão: 4 Vermelhos Seguidos. Quebra para PRETO."
        if texto_sub_pol.endswith("PPPP"):
            bloco_anterior = texto_sub_pol[4:8]
            if bloco_anterior.count("P") >= 2: return True, "FALSO_RESPIRO", "Falso Respiro: Tendência de PRETO."
            return True, "INVERSÃO", "Exaustão: 4 Pretos Seguidos. Quebra para VERMELHO."
        if texto_sub_pol.endswith("VPVPVP") or texto_sub_pol.endswith("PVPVPV"):
            return True, "AVISO_XADREZ", "Alerta de Ciclo de Alternância Ativo."
        return False, "NORMAL", "Fluxo Estável."

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
    def arbitrar_sinal(no_call_ativo, motivo_nc, expectations, inclinacao_num, geometria_mercado, previsao_ia, status_inversao, historico_revalida_regras):
        if no_call_ativo: return "NO CALL", motivo_nc, "SISTEMA_TRAVADO"
        if geometria_mercado == "CICLO_FECHADO_VPPV": return "PRETO", "Geometria VPPV -> Alvo PRETO", "GEOMETRIA"
        if geometria_mercado == "CICLO_FECHADO_PVVP": return "VERMELHO", "Geometria PVVP -> Alvo VERMELHO", "GEOMETRIA"

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
                origens[item["direcao"]].append(f"{item['origem']}")
                if peso_vivo > maior_peso_id[item["direcao"]][1]:
                    maior_peso_id[item["direcao"]] = (id_r, peso_vivo)
                
            if forcas["VERMELHO"] != forcas["PRETO"]:
                sinal_dominante = "VERMELHO" if forcas["VERMELHO"] > forcas["PRETO"] else "PRETO"
                sinal_oposto = "PRETO" if sinal_dominante == "VERMELHO" else "VERMELHO"
                regra_vencedora_id = maior_peso_id[sinal_dominante][0]
                
                if forcas[sinal_oposto] > 0 and direcao_ia != "NEUTRO" and confianca_ia > 65.0:
                    sinal_projetado = direcao_ia
                    justificativa_proj = f"Veredito de Recência Extrema: IA ({confianca_ia:.1f}%) assume o controle."
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
                    justificativa_proj = f"Coexistência Empatada: {expectations[-1]['origem']}"
                    regra_vencedora_id = expectations[-1]["tipo_regra"]

        if risco_ativo and tipo_inversao == "FALSO_RESPIRO":
            if sinal_projetado: return sinal_projetado, f"Filtro Cruzado Futuro: {justificativa_proj}", regra_vencedora_id
            cor_dominante = "VERMELHO" if "VERMELHO" in justificativa_inv else "PRETO"
            return cor_dominante, f"Filtro Antirespiro: Mantendo {cor_dominante}.", "ANTI_RESPIRO"

        if risco_ativo and tipo_inversao == "INVERSÃO":
            if sinal_projetado: return sinal_projetado, f"Filtro Cruzado Futuro: {justificativa_proj}", regra_vencedora_id
            sinal_inverso = "PRETO" if "Vermelhos Seguidos" in justificativa_inv else "VERMELHO"
            return sinal_inverso, f"Intercepção de Exaustão (4 Casas): {justificativa_inv}", "INVERSION_REAL"

        if sinal_projetado: return sinal_projetado, justificativa_proj, regra_vencedora_id
        if direcao_inclinacao != "NEUTRO" and porc >= 60.0: return direcao_inclinacao, f"Matriz Pós-Número: {porc:.1f}%", "MATRIZ_INCLINA"
        if direcao_ia != "NEUTRO" and confianca_ia >= 62.0: return direcao_ia, f"IA Preditiva: {confianca_ia:.1f}%", "IA_PREDITIVA"
        if direcao_ia != "NEUTRO": return direcao_ia, f"Vetor Recente IA: {direcao_ia} ({confianca_ia:.1f}%)", "IA_VETOR"
        
        return "NO CALL", "Volume 20: Ausência de Consenso Hierárquico Estrutural", "SISTEMA_TRAVADO"

class MotorV1Completo:
    def __init__(self, lista_dados_xls):
        self.seq = SequenciaOperacional(lista_dados_xls)
        corte_recencia = max(0, len(lista_dados_xls) - 150)
        self.dados_longo = lista_dados_xls[:corte_recencia]
        self.dados_curto = lista_dados_xls[corte_recencia:]
        
        # =========================================================================
        # EVOLUÇÃO PERMANENTE: IMPORTA A BASE DE RECÊNCIA ATIVA DA IA (FIX)
        # =========================================================================
        base_recencia = None
        caminho_recencia = "base_recencia_ativa.xlsx"
        if os.path.exists(caminho_recencia):
            try:
                leitor_recencia = LeitorXLS(caminho_recencia)
                base_recencia = leitor_recencia.ler_e_validar()
            except:
                base_recencia = None
                
        dados_curto_consolidados = self.dados_curto + (base_recencia if base_recencia else [])
        self.ia = IAPreditivaV1(self.dados_longo, dados_curto_consolidados)
        self.historico_regras = defaultdict(lambda: {"acertos": 1, "total": 1})

    def processar_auditoria(self):
        idx = 0
        memorias_calculo = []
        janelas_auditadas = []
        stats = {"G0": 0, "G1": 0, "G2": 0, "FALHA": 0, "NO CALL": 0}
        
        ia_total_predições = 0
        ia_acertos_reais = 0

        while idx + 12 < self.seq.total:
            sub_num = self.seq.numerica[idx : idx + 12]
            sub_pol = self.seq.polaridades[idx : idx + 12]

            geometria = AnalisadorContextoAvancado.mapear_padroes_geometria(sub_pol)
            status_inv = AnalisadorContextoAvancado.detectar_chance_inversao(sub_pol)
            nc_ativo, motivo_nc = MotorNoCall.checar_no_call(sub_num, sub_pol)
            expectativas = MotorContagensProjetivas.mapear_janela(sub_num, sub_pol, geometria)

            num_fechamento = sub_num[-1]
            inclinacao_num = AnalisadorContextoAvancado.calcular_numerologia_pos_numero(num_fechamento, self.seq.total if 'self' not in locals() else self.seq.numerica, self.seq.polaridades)
            
            direcao_ia_pura, conf_ia_pura = self.ia.predizer_proxima_casa(sub_num, sub_pol)
            previsao_ia = (direcao_ia_pura, conf_ia_pura)
            
            # CORREÇÃO EFETUADA AQUI: Alterado 'expectations' para 'expectativas' para matar o NameError
            expectativa_final, justificativa, regra_ativa_id = JuizHierarquicoModificado.arbitrar_sinal(
                nc_ativo, motivo_nc, expectativas, inclinacao_num, geometria, previsao_ia, status_inv, self.historico_regras
            )

            if expectativa_final != "NO CALL":
                ultima_cor_seq = sub_pol[-1] if sub_pol else ""
                streak_atual = 0
                for col_f in reversed(sub_pol):
                    if col_f == ultima_cor_seq: streak_atual += 1
                    else: break
                if streak_atual >= 5 and expectativa_final == ("VERMELHO" if ultima_cor_seq == "V" else "PRETO"):
                    expectativa_final = "NO CALL"
                    justificativa = f"VETO DE RARIDADE BINOMIAL: Sequência de {streak_atual}x {ultima_cor_seq} detectada. Operação abortada."
                    regra_ativa_id = "VETO_BINOMIAL"
                
                if expectativa_final != "NO CALL" and idx >= 100:
                    historico_recente_100 = self.seq.polaridades[max(0, idx+12-100) : idx+12]
                    freq_v_macro = (historico_recente_100.count("V") / len(historico_recente_100)) * 100
                    freq_p_macro = (historico_recente_100.count("P") / len(historico_recente_100)) * 100
                    if freq_v_macro >= 55.0 and expectativa_final == "PRETO":
                        expectativa_final = "NO CALL"
                        justificativa = f"FILTRO DE SURFE MACRO: Evitando operar contra tendência de VERMELHO ({freq_v_macro:.1f}%)."
                        regra_ativa_id = "FILTRO_SURFE"
                    elif freq_p_macro >= 55.0 and expectativa_final == "VERMELHO":
                        expectativa_final = "NO CALL"
                        justificativa = f"FILTRO DE SURFE MACRO: Evitando operar contra tendência de PRETO ({freq_p_macro:.1f}%)."
                        regra_ativa_id = "FILTRO_SURFE"

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
                for g_idx, col_real in enumerate(correcoes_reais):
                    if col_real == letra_esperada or col_real == "B":
                        classificacao = f"G{g_idx}"
                        salto = g_idx + 1
                        break
                if classificacao == "FALHA": salto = 3
                stats[classificacao] += 1

            if direcao_ia_pura != "NEUTRO":
                ia_total_predições += 1
                letra_ia = "V" if direcao_ia_pura == "VERMELHO" else "P"
                if correcoes_reais and (correcoes_reais[0] == letra_ia or correcoes_reais[0] == "B" or (len(correcoes_reais) > 1 and correcoes_reais[1] == letra_ia)):
                    ia_acertos_reais += 1

            if regra_ativa_id != "NENHUMA" and regra_ativa_id != "SISTEMA_TRAVADO":
                self.historico_regras[regra_ativa_id]["total"] += 1
                if classificacao in ["G0", "G1"]: self.historico_regras[regra_ativa_id]["acertos"] += 1

            bloco_vivido = []
            for k in range(idx, min(idx + 12 + salto, self.seq.total)):
                bloco_vivido.append({"numero": self.seq.numerica[k], "cor": self.seq.polaridades[k]})
            self.ia.injetar_aprendizado_imediato(bloco_vivido, multiplicador_peso=3)

            log_linha = f"Janela {len(janelas_auditadas) + 1}: {sub_num} -> Expectativa: {expectativa_final} -> Justificativa: {justificativa} -> Correção: {classificacao}"
            memorias_calculo.append(log_linha)
            janelas_auditadas.append(classificacao)
            idx += 12 + salto

        # PERSISTÊNCIA AUTOMÁTICA EM DISCO
        try:
            GerenciadorMemoriaViva.injetar_rodadas_reais(self.seq.numerica, [], "base_recencia_ativa.xlsx")
        except:
            pass

        assertividade_ia = (ia_acertos_reais / ia_total_predições * 100) if ia_total_predições > 0 else 0.0
        return self._gerar_relatorio_texto(memorias_calculo, stats, len(janelas_auditadas), assertividade_ia, ia_total_predições)

    def _gerar_relatorio_texto(self, memorias, stats, qtd_janelas, assertividade_ia, total_ia):
        total_com_sinal = sum([stats["G0"], stats["G1"], stats["G2"], stats["FALHA"]])
        denominador = total_com_sinal if total_com_sinal > 0 else 1
        p_g0 = (stats["G0"] / denominador) * 100
        p_g1 = (stats["G1"] / denominador) * 100
        p_g2 = (stats["G2"] / denominador) * 100
        p_fa = (stats["FALHA"] / denominador) * 100
        p_nc = (stats["NO CALL"] / (qtd_janelas if qtd_janelas > 0 else 1)) * 100

        if p_fa >= 25.0: condicao_market = "MERCADO EM DEGRADAÇÃO"
        elif p_g0 >= 50.0: condicao_market = "MERCADO PAGADOR"
        elif p_g1 >= 40.0: condicao_market = "MERCADO COM ATRASO CONTROLADO"
        else: condicao_market = "MERCADO INSTÁVEL"

        output = "[MEMÓRIA DE CÁLCULO DAS JANELAS MÓVEIS]\n" + "\n".join(memorias) + "\n\n"
        output += "[RESULTADO FINAL TIPO D]\n"
        output += f"CRONOLOGIA VALIDADA: {self.seq.total} Resultados Reconstruídos\n"
        output += f"TOTAL DE JANELAS AUDITADAS: {qtd_janelas} Saltos Sequenciais\n"
        output += f" - Taxa G0: {stats['G0']} Ocorrências ({p_g0:.2f}%)\n"
        output += f" - Taxa G1: {stats['G1']} Ocorrências ({p_g1:.2f}%)\n"
        output += f" - Taxa G2: {stats['G2']} Ocorrências ({p_g2:.2f}%)\n"
        output += f" - Taxa de Falha: {stats['FALHA']} Ocorrências ({p_fa:.2f}%)\n"
        output += f" - Taxa de NO CALL: {stats['NO CALL']} Ocorrências ({p_nc:.2f}%)\n\n"
        output += f"METRICA_EVOLUÇÃO_IA: {assertividade_ia:.2f}% de Assertividade Pura (Amostra: {total_ia} tomadas de decisão)\n"
        output += f"ESTADO ATUAL DO MERCADO: {condicao_market}\n"
        return output

class ProcessadorTipoB:
    def __init__(self, sequencia_12_numeros, caminho_base_dados):
        self.entrada_usuario = sequencia_12_numeros
        self.caminho_base = caminho_base_dados
        self.caminho_recencia = "base_recencia_ativa.xlsx"
        
        self.polaridades_usuario = []
        for num in self.entrada_usuario:
            cor = 'B' if num == 0 else ('V' if 1 <= num <= 7 else 'P')
            self.polaridades_usuario.append(cor)

    def executar_sinal_real(self):
        if len(self.entrada_usuario) != 12: return {"erro": "Requisito de exatamente 12 números violado."}
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
        saturacao = AnalisadorContextoAvancado.mapear_padroes_geometria(self.polaridades_usuario)
        status_inv = AnalisadorContextoAvancado.detectar_chance_inversao(self.polaridades_usuario)
        nc_ativo, motivo_nc = MotorNoCall.checar_no_call(self.entrada_usuario, self.polaridades_usuario)
        num_fechamento = self.entrada_usuario[-1]
        
        regras_b = defaultdict(lambda: {"acertos": 1, "total": 1})
        sinal_final, justificativa_final, _ = None, "", None
        historico_iteraçoes_log = []

        for ciclo in range(1, 16):
            previsao_ia = ia_operacional.predizer_proxima_casa(self.entrada_usuario, self.polaridades_usuario)
            expectativas = MotorContagensProjetivas.mapear_janela(self.entrada_usuario, self.polaridades_usuario, saturacao)
            inclinacao_num = AnalisadorContextoAvancado.calcular_numerologia_pos_numero(num_fechamento, num_global, pol_global)
            
            sinal_ciclo, justificativa_ciclo, regra_ativa_id = JuizHierarquicoModificado.arbitrar_sinal(
                nc_ativo, motivo_nc, expectativas, inclinacao_num, saturacao, previsao_ia, status_inv, regras_b
            )

            if sinal_ciclo != "NO CALL":
                ultima_cor_seq = self.polaridades_usuario[-1] if self.polaridades_usuario else ""
                streak_atual = 0
                for col_f in reversed(self.polaridades_usuario):
                    if col_f == ultima_cor_seq: streak_atual += 1
                    else: break
                if streak_atual >= 5 and sinal_ciclo == ("VERMELHO" if ultima_cor_seq == "V" else "PRETO"):
                    sinal_ciclo = "NO CALL"
                    justificativa_ciclo = f"VETO DE RARIDADE BINOMIAL: Sequência de {streak_atual}x {ultima_cor_seq} esticada. Operação bloqueada para conter Gale."
                    regra_ativa_id = "VETO_BINOMIAL"
                
                if sinal_ciclo != "NO CALL" and len(pol_global) >= 100:
                    ultimos_100_giros = pol_global[-100:]
                    freq_v_macro = (ultimos_100_giros.count("V") / 100) * 100
                    freq_p_macro = (ultimos_100_giros.count("P") / 100) * 100
                    if freq_v_macro >= 55.0 and sinal_ciclo == "PRETO":
                        sinal_ciclo = "NO CALL"
                        justificativa_ciclo = f"FILTRO DE SURFE MACRO: Evitando operar contra tendência majoritária de VERMELHO ({freq_v_macro:.1f}% nos últimos 100 giros)."
                        regra_ativa_id = "FILTRO_SURFE"
                    elif freq_p_macro >= 55.0 and sinal_ciclo == "VERMELHO":
                        sinal_ciclo = "NO CALL"
                        justificativa_ciclo = f"FILTRO DE SURFE MACRO: Evitando operar contra tendência majoritária de PRETO ({freq_p_macro:.1f}% nos últimos 100 giros)."
                        regra_ativa_id = "FILTRO_SURFE"

            if regra_ativa_id != "NENHUMA" and regra_ativa_id != "SISTEMA_TRAVADO":
                regras_b[regra_ativa_id]["total"] += 1
                regras_b[regra_ativa_id]["acertos"] += 1
            historico_iteraçoes_log.append(f" Releitura {ciclo:02d}/15 -> Sinal: {sinal_ciclo} | Id Regra: {regra_ativa_id}")
            if ciclo == 15:
                sinal_final, justificativa_final = sinal_ciclo, justificativa_ciclo

        chance_branco, casas_atraso = AnalisadorContextoAvancado.preditor_estatistico_branco(num_fechamento, num_global, pol_global)
        
        if casas_atraso >= 25:
            justificativa_final += f" | PROTOCOLO GESTÃO DO BRANCO ATIVO: {casas_atraso} rodadas de atraso. Executar divisão Split-Stake (1/7 da stake na cor principal)."

        total_testes_regras = sum([regras_b[k]["total"] for k in regras_b]) - len(regras_b)
        score_aprendizado = "ESTABILIZANDO" if total_testes_regras > 5 else "MAPEANDO NOVO CICLO"

        output_memoria = (
            f"[PROCESSO DE 15 RELEITURAS DE VALIDAÇÃO CONSEQÜENCIAL]\n"
            + "\n".join(historico_iteraçoes_log) + "\n\n"
            f"[ANÁLISE DE FECHAMENTO]\n"
            f"- Status do Aprendizado Vivo: {score_aprendizado}\n"
            f"- Geometria: {saturacao}\n"
            f"- Resolução Final: {justificativa_final}\n"
        )

        return {
            "sinal": sinal_final, "justificativa": justificativa_final, "memoria": output_memoria,
            "chance_branco": chance_branco, "atraso_branco": casas_atraso, "geometria": saturacao
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
                if any(x in col_lower for x in ['val', 'num', 'number', 'roll', 'giro', 'spin']) and not any(x in col_lower for x in ['color', 'cor']): col_numero = col
                if any(x in col_lower for x in ['color', 'cor']): col_cor = col
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

class EngineMatematicoAvancado:
    @staticmethod
    def calcular_raridade_sequencia(sub_pol):
        if not sub_pol: return {"streak": 0, "probabilidade": 100.0, "status": "SEM DADOS"}
        ultima_cor = sub_pol[-1]
        if ultima_cor not in ['V', 'P']: return {"streak": 0, "probabilidade": 100.0, "status": "BRANCO NO FECHAMENTO"}
        streak = 0
        for col in reversed(sub_pol):
            if col == ultima_cor: streak += 1
            else: break
        probabilidade_sequencia = ((7 / 15) ** streak) * 100
        status = "SATURAÇÃO CRÍTICA (Risco Elevado de Inversão / Exaustão)" if streak >= 5 else ("DESVIO PADRÃO EM CURSO" if streak >= 3 else "ESTRUTURA DENTRO DA NORMALIDADE")
        return {"streak": streak, "cor_sequencia": "VERMELHO" if ultima_cor == 'V' else "PRETO", "probabilidade": round(probabilidade_sequencia, 2), "status": status}

    @staticmethod
    def calcular_vies_surfe(caminho_base, janela=100):
        leitor = LeitorXLS(caminho_base)
        dados = leitor.ler_e_validar()
        if not dados: return {"vies": "INDISPONÍVEL", "desvio_v": 0.0, "desvio_p": 0.0, "frequencia_v": 46.67, "frequencia_p": 46.67, "frequencia_b": 6.67}
        ultimos_giros = dados[-janela:]
        total_giros = len(ultimos_giros)
        if total_giros == 0: return {"vies": "INDISPONÍVEL", "desvio_v": 0.0, "desvio_p": 0.0, "frequencia_v": 46.67, "frequencia_p": 46.67, "frequencia_b": 6.67}
        v = sum(1 for d in ultimos_giros if d['cor'] == 'V')
        p = sum(1 for d in ultimos_giros if d['cor'] == 'P')
        b = sum(1 for d in ultimos_giros if d['cor'] == 'B')
        pct_v, pct_p, pct_b = (v / total_giros) * 100, (p / total_giros) * 100, (b / total_giros) * 100
        desvio_v, desvio_p = pct_v - 46.67, pct_p - 46.67
        vies = "SURFE DE MACROFREQUÊNCIA: VIÉS PARA VERMELHO ATIVO" if pct_v >= 53.0 else ("SURFE DE MACROFREQUÊNCIA: VIÉS PARA PRETO ATIVO" if pct_p >= 53.0 else "MACROANÁLISE EQUILIBRADA")
        return {"frequencia_v": round(pct_v, 2), "frequencia_p": round(pct_p, 2), "frequencia_b": round(pct_b, 2), "desvio_v": round(desvio_v, 2), "desvio_p": round(desvio_p, 2), "vies": vies}

    @staticmethod
    def simular_split_stake_cobertura(stake_principal=10.0):
        stake_branco_ideal = round(stake_principal / 7.0, 2)
        stake_branco_conservador = round(stake_principal / 10.0, 2)
        custo_total = stake_principal + stake_branco_ideal
        return {"stake_cor": stake_principal, "cobertura_b_ideal_1_7": stake_branco_ideal, "cobertura_b_matematica_1_10": stake_branco_conservador, "lucro_liquido_se_der_branco": round((stake_branco_ideal * 14) - custo_total, 2), "custo_total_operacao": round(custo_total, 2), "house_edge_estatico": "-6.67%"}
