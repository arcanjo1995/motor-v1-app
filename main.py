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
                return True, f"Volume 2 Cap 6: Trava das Duplas Ativa"

        posicoes_criticas_6 = [5, 8, 9, 10]
        for pos in posicoes_criticas_6:
            if sub_num[pos] == 6:
                return True, f"Volume 2 Cap 4: Trava Número 6"

        posicoes_criticas_2 = [8, 9, 10, 11]
        for pos in posicoes_criticas_2:
            if sub_num[pos] == 2:
                return True, f"Volume 2 Cap 3: Trava Número 2"

        posicoes_criticas_b = [5, 8, 9, 10, 11]
        for pos in posicoes_criticas_b:
            if sub_pol[pos] == "B":
                return True, f"Volume 2 Cap 5: Trava do Branco"

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
                    if i < 10 and 0 in sub_num[i:11]:
                        continue
                    if num_atual == 4:
                        direcao_sinal = "VERMELHO" if sub_pol[i] == "P" else "PRETO"
                        identificador_regra = "V3_ATIVADOR_4"
                    elif num_atual == 6:
                        direcao_sinal = "PRETO" if "VERMELHO" not in geometria_mercado else "VERMELHO"
                        identificador_regra = "V3_ATIVADOR_6"
                    else:
                        direcao_sinal = "VERMELHO" if sub_pol[i] == "P" else "PRETO"
                        identificador_regra = f"V3_ATIVADOR_{num_atual}"
                    
                    lista_bruta.append({
                        "direcao": direcao_sinal,
                        "tipo_regra": identificador_regra,
                        "origem": f"Volume 3: Ativador {num_atual} na {i+1}ª casa"
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
    """Juiz de Aprendizado de Eficácia de Regras por Recência Viva"""
    @staticmethod
    def arbitrar_sinal(no_call_ativo, motivo_nc, expectations, inclinacao_num, geometria_mercado, previsao_ia, status_inversao, historico_revalida_regras):
        if no_call_ativo: 
            return "NO CALL", motivo_nc, "SISTEMA_TRAVADO"

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
                # CALIBRALÇÃO DE PESO VIVO POR RECÊNCIA: Se a regra estiver performando bem no XLS, o peso dela sobe dinamicamente
                taxa_acerto_recente = historico_revalida_regras[id_r]["acertos"] / max(1, historico_revalida_regras[id_r]["total"])
                
                # Base de soberania do manual multiplicada pela taxa real de eficácia do momento atual do arquivo
                base_soberania = 3.0 if "V12_" in id_r else 2.0
                peso_vivo = base_soberania * (1.0 + taxa_acerto_recente)
                
                forcas[item["direcao"]] += peso_vivo
                origens[item["direcao"]].append(f"{item['origem']} [Peso Vivo: {peso_vivo:.1f}]")
                
                if peso_vivo > maior_peso_id[item["direcao"]][1]:
                    maior_peso_id[item["direcao"]] = (id_r, peso_vivo)
                
            if forcas["VERMELHO"] != forcas["PRETO"]:
                sinal_dominante = "VERMELHO" if forcas["VERMELHO"] > forcas["PRETO"] else "PRETO"
                regra_vencedora_id = maior_peso_id[sinal_dominante][0]
                
                # Intercepção flexível se a IA recente detectar a quebra do ciclo dominante enfraquecido
                if direcao_ia != "NEUTRO" and direcao_ia != sinal_dominante and confianca_ia >= 59.0:
                    sinal_projetado = direcao_ia
                    justificativa_proj = f"Intercepção por IA de Recência ({confianca_ia:.1f}%) quebrando dominância enfraquecida de {sinal_dominante}."
                    regra_vencedora_id = "IA_INTERCEPCAO"
                else:
                    sinal_projetado = sinal_dominante
                    justificativa_proj = f"Dominância Recente Dinâmica: " + " + ".join(origens[sinal_dominante])
            else:
                if direcao_ia != "NEUTRO":
                    sinal_projetado = direcao_ia
                    justificativa_proj = f"Coexistência Empatada resolvida por IA de Recência ({confianca_ia:.1f}%)"
                    regra_vencedora_id = "IA_DESEMPATE"
                else:
                    sinal_projetado = expectations[-1]["direcao"]
                    justificativa_proj = f"Coexistência Empatada resolvida por Proximidade: {expectations[-1]['origem']}"
                    regra_vencedora_id = expectations[-1]["tipo_regra"]

        if geometria_mercado == "CICLO_FECHADO_VPPV":
            return "PRETO", "Geometria VPPV -> Alvo PRETO", "GEOMETRIA"
            
        if geometria_mercado == "CICLO_FECHADO_PVVP":
            return "VERMELHO", "Geometria PVVP -> Alvo VERMELHO", "GEOMETRIA"

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
        
        # Criação da tabela viva de revalidação de regras por recência em tempo real
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

            # ALIMENTAÇÃO DA TABELA DE EFICÁCIA VIVA DAS REGRAS (Foco total em G0 e G1)
            if regra_ativa_id != "NENHUMA" and regra_ativa_id != "SISTEMA_TRAVADO":
                self.historico_regras[regra_ativa_id]["total"] += 1
                if classificacao in ["G0", "G1"]:
                    self.historico_regras[regra_ativa_id]["acertos"] += 1

            bloco_vivido = []
            for k in range(idx, min(idx + 12 + salto, self.seq.total)):
                bloco_vivido.append({"numero": self.seq.numerica[k], "cor": self.seq.polaridades[k]})
            self.ia.injetar_aprendizado_imediato(bloco_vivido, multiplicador_peso=3)

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
        
        # Criação de tabela dummy neutra apenas para manter compatibilidade com o Tipo B vivo
        regras_b = defaultdict(lambda: {"acertos": 1, "total": 1})
        sinal_final, justificativa, _ = JuizHierarquicoModificado.arbitrar_sinal(
            nc_ativo, motivo_nc, expectativas, inclinacao_num, saturacao, previsao_ia, status_inv, regras_b
        )

        chance_branco, casas_atraso = AnalisadorContextoAvancado.preditor_estatistico_branco(num_fechamento, num_global, pol_global)

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
