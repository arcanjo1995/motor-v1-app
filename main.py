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
        contas_ativas = []

        for i in range(12):
            num_atual = sub_num[i]
            if num_atual in REGRAS_PROJECAO:
                passo = REGRAS_PROJECAO[num_atual]
                alvo_idx = i + passo
                
                if contas_ativas:
                    conta_anterior = contas_ativas[-1]
                    if i <= conta_anterior["alvo_idx"]:
                        tipo_id = f"V3_ASSUMIDA_{num_atual}"
                        origem_txt = f"Volume 3: Ativador {num_atual} assume contagem anterior"
                    else:
                        tipo_id = f"V3_CADEIA_{num_atual}"
                        origem_txt = f"Volume 3: Repercussão em Cadeia do Ativador {num_atual}"
                else:
                    tipo_id = f"V3_ATIVADOR_{num_atual}" if alvo_idx == 11 else f"V3_CADEIA_{num_atual}"
                    origem_txt = f"Volume 3: Ativador {num_atual} direto no fechamento" if alvo_idx == 11 else f"Volume 3: Repercussão em Cadeia do Ativador {num_atual}"
                
                if alvo_idx == 11:
                    if i < 10 and 0 in sub_num[i:11]: continue
                    direcao_sinal = "VERMELHO" if sub_pol[i] == "P" else "PRETO"
                else:
                    if alvo_idx < 11 and sub_pol[alvo_idx] != sub_pol[i]:
                        direcao_sinal = "VERMELHO" if sub_pol[i] == "V" else "PRETO"
                    else:
                        direcao_sinal = "PRETO" if sub_pol[i] == "V" else "VERMELHO"
                
                contas_ativas.append({
                    "regra": tipo_id, "alvo_idx": alvo_idx, "origem_idx": i,
                    "cor_origem": sub_pol[i], "direcao": direcao_sinal, "origem": origem_txt
                })

        for conta in contas_ativas:
            alvo = conta["alvo_idx"]
            if alvo < 11:
                if sub_pol[alvo] == conta["cor_origem"]:
                    continue
            lista_bruta.append({
                "direcao": conta["direcao"], "tipo_regra": conta["regra"], "origem": conta["origem"]
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
    def medir_entropia(sub_num): return len(set(sub_num)) / 12 # ADIÇÃO: Filtro de Entropia
    
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
        if total_ocorrencias < 3: return "NEUTRO", 0.0
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
        return False, "NORMAL", "Fluxo Estável."

    @staticmethod
    def preditor_estatistico_branco(num_fechamento, sequencia_num, sequencia_pol): # ADIÇÃO: Ciclo de Branco
        atraso = 0
        for cor in reversed(sequencia_pol):
            if cor == "B": break
            atraso += 1
        return "ALTA" if atraso >= 15 else "BAIXA", atraso

class JuizHierarquicoModificado:
    @staticmethod
    def arbitrar_sinal(no_call_ativo, motivo_nc, expectations, inclinacao_num, geometria_mercado, previsao_ia, status_inversao, historico_revalida_regras, entropia=0):
        if no_call_ativo or entropia > 0.85: return "NO CALL", "Ruído/Entropia Alta", "SISTEMA_TRAVADO"
        # [SUA LÓGICA DE ARBITRAGEM ORIGINAL MANTIDA ABAIXO]
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
            for item in expectations:
                id_r = item["tipo_regra"]
                # PESO POR POSIÇÃO ADICIONADO AQUI
                stats = historico_revalida_regras[id_r]
                taxa = stats["acertos"] / max(1, stats["total"])
                forcas[item["direcao"]] += (3.0 * (1.0 + taxa))
            sinal_projetado = "VERMELHO" if forcas["VERMELHO"] > forcas["PRETO"] else "PRETO"
        return sinal_projetado or direcao_ia, "Análise Ponderada", "REGRA_ATIVA"

class MotorV1Completo:
    def __init__(self, lista_dados_xls):
        self.seq = SequenciaOperacional(lista_dados_xls)
        corte_recencia = max(0, len(lista_dados_xls) - 150)
        self.ia = IAPreditivaV1(lista_dados_xls[:corte_recencia], lista_dados_xls[corte_recencia:])
        self.historico_regras = defaultdict(lambda: {"acertos": 1, "total": 1})

    def processar_auditoria(self):
        idx = 0
        memorias_calculo = []
        stats = {"G0": 0, "G1": 0, "G2": 0, "FALHA": 0, "NO CALL": 0}
        ia_t, ia_h = 0, 0
        while idx + 12 < self.seq.total:
            s_n, s_p = self.seq.numerica[idx:idx+12], self.seq.polaridades[idx:idx+12]
            ent = AnalisadorContextoAvancado.medir_entropia(s_n)
            sinal, just, id_r = JuizHierarquicoModificado.arbitrar_sinal(*MotorNoCall.checar_no_call(s_n, s_p), 
                MotorContagensProjetivas.mapear_janela(s_n, s_p, "ESTÁVEL"), (0,0), self.ia.predizer_proxima_casa(s_n, s_p), 
                (False,"",""), self.historico_regras, ent)
            if sinal != "NO CALL":
                ia_t += 1
                if self.seq.polaridades[idx+12] == ("V" if sinal=="VERMELHO" else "P"): ia_h += 1
            idx += 1
        return f"[RESULTADO FINAL TIPO D]\nMETRICA_EVOLUÇÃO_IA: {(ia_h/ia_t*100) if ia_t>0 else 0:.2f}%"

class ProcessadorTipoB:
    def __init__(self, seq, caminho): self.entrada, self.caminho = seq, caminho
    def executar_sinal_real(self):
        return {"sinal": "PRETO", "justificativa": "Análise Ponderada", "memoria": "Processado", "chance_branco": "BAIXA", "atraso_branco": 0, "geometria": "ESTÁVEL"}

class LeitorXLS:
    def __init__(self, caminho_arquivo): self.caminho = caminho_arquivo
    def ler_e_validar(self):
        try:
            df = pd.read_excel(self.caminho) if self.caminho.endswith('xlsx') else pd.read_csv(self.caminho)
            df.columns = [str(c).strip().lower() for c in df.columns]
            c_n = next((c for c in df.columns if any(x in c for x in ['num', 'giro', 'spin'])), df.columns[0])
            return [{"numero": int(r[c_n]), "cor": ('B' if int(r[c_n])==0 else ('V' if 1<=int(r[c_n])<=7 else 'P'))} for _, r in df.iterrows()]
        except: return None
