import os
import pandas as pd
from collections import defaultdict
import pickle

# ============================================================
# Funções de Persistência do Modelo de Longo Prazo
# ============================================================
def salvar_modelo_longo_prazo(ia, caminho="modelo_longo_prazo.pkl"):
    try:
        with open(caminho, "wb") as f:
            pickle.dump(ia, f)
        return True
    except Exception as e:
        print(f"Erro ao salvar modelo: {e}")
        return False

def carregar_modelo_longo_prazo(caminho="modelo_longo_prazo.pkl"):
    if os.path.exists(caminho):
        try:
            with open(caminho, "rb") as f:
                return pickle.load(f)
        except:
            return None
    return None

# ============================================================
# FUNÇÃO: Treinamento com Relatório de Longo Prazo
# ============================================================
def treinar_base_longo_prazo_com_janelas(dados_completos):
    if not dados_completos or len(dados_completos) < 30:
        return {
            "sucesso": False,
            "mensagem": "Base muito pequena para treinamento profundo (mínimo 30 registros)."
        }

    motor = MotorV1Completo(dados_completos)
    motor.processar_auditoria()

    stats = getattr(motor, 'stats', {"G0": 0, "G1": 0, "G2": 0, "FALHA": 0, "NO CALL": 0})
    total_janelas = sum(stats.values()) if stats else 0

    regras_boas = 0
    for regra, dados in motor.historico_regras.items():
        if dados["total"] >= 5 and (dados["acertos"] / dados["total"]) >= 0.55:
            regras_boas += 1

    taxa_g0_g1 = ((stats.get("G0", 0) + stats.get("G1", 0)) / total_janelas * 100) if total_janelas > 0 else 0

    sucesso_salvar = salvar_modelo_longo_prazo(motor.ia)

    return {
        "sucesso": True,
        "registros_processados": len(dados_completos),
        "janelas_analisadas": total_janelas,
        "G0": stats.get("G0", 0),
        "G1": stats.get("G1", 0),
        "G2": stats.get("G2", 0),
        "FALHA": stats.get("FALHA", 0),
        "NO CALL": stats.get("NO CALL", 0),
        "regras_com_boa_performance": regras_boas,
        "assertividade_g0_g1_percent": round(taxa_g0_g1, 2),
        "modelo_salvo_com_sucesso": sucesso_salvar,
        "mensagem": "Treinamento profundo por janelas móveis concluído com sucesso."
    }


# ============================================================
# MotorNoCall - NUNCA ALTERADO
# ============================================================
class MotorNoCall:
    @staticmethod
    def checar_no_call(sub_num, sub_pol):
        cenarios_duplas = [(7, 8), (8, 9), (9, 10), (10, 11)]
        for idx1, idx2 in cenarios_duplas:
            if sub_num[idx1] == sub_num[idx2]:
                return True, "Volume 2 Cap 6: Trava das Duplas Ativa"

        posicoes_criticas_6 = [3, 4, 5, 8, 9, 10, 11]
        for pos in posicoes_criticas_6:
            if sub_num[pos] == 6:
                return True, "Volume 2 Cap 4: Trava Número 6 (Posição de No Call Ativa)"

        posicoes_criticas_2 = [8, 9, 10, 11]
        for pos in posicoes_criticas_2:
            if sub_num[pos] == 2:
                return True, "Volume 2 Cap 3: Trava Número 2"

        posicoes_criticas_b = [3, 4, 5, 8, 9, 10, 11]
        for pos in posicoes_criticas_b:
            if sub_pol[pos] == "B":
                return True, "Volume 2 Cap 5: Trava do Branco"

        return False, "Evento Neutro Operacional"


# ============================================================
# IAPreditivaV1
# ============================================================
class IAPreditivaV1:
    def __init__(self, dados_longo_prazo, dados_recencia=None):
        self.dados_longo = dados_longo_prazo
        self.dados_recencia = dados_recencia if dados_recencia else []
        self.modelo_transicao = defaultdict(list)
        self.modelo_numerico = defaultdict(list)
        self.stats_regras = defaultdict(list)
        
        self.unidade_analise = {}
        for n in range(15):
            self.unidade_analise[n] = {
                "ocorrencias": 0, "V": 0, "P": 0, "B": 0,
                "freq_v": 0.0, "freq_p": 0.0, "freq_b": 0.0,
                "estabilidade": "NEUTRO", "saturacao": "NORMAL",
                "enfraquecimento": "ESTÁVEL", "consequencia_dominante": "NEUTRO",
                "pos_numero_V": 0, "pos_numero_P": 0, "pos_numero_B": 0,
                "pos_numero_freq_v": 0.0, "pos_numero_freq_p": 0.0, "pos_numero_freq_b": 0.0,
                "comportamento_pos_numero": "NEUTRO"
            }
        self._treinar_modelo_profundo()

    def _treinar_modelo_profundo(self):
        if self.dados_longo and len(self.dados_longo) >= 5:
            self._processar_bloco_dados(self.dados_longo, 1, True)
        if self.dados_recencia and len(self.dados_recencia) >= 5:
            self._processar_bloco_dados(self.dados_recencia, 4, True)

    def _processar_bloco_dados(self, dados, multiplicador_peso, treinamento_profundo=False):
        if not dados: return

        for i in range(len(dados) - 2):
            estado = (dados[i]['cor'], dados[i+1]['cor'])
            prox = dados[i+2]['cor']
            num = dados[i+1]['numero']
            for _ in range(multiplicador_peso):
                self.modelo_transicao[estado].append(prox)
                self.modelo_numerico[num].append(prox)

        for i in range(len(dados) - 1):
            num = int(dados[i]['numero'])
            cor_post = str(dados[i+1]['cor']).upper()
            if 0 <= num <= 14 and cor_post in ['V', 'P', 'B']:
                self.unidade_analise[num]["ocorrencias"] += multiplicador_peso
                self.unidade_analise[num][cor_post] += multiplicador_peso
                self.unidade_analise[num][f"pos_numero_{cor_post}"] += multiplicador_peso

        for n in range(15):
            total = self.unidade_analise[n]["ocorrencias"]
            if total > 0:
                self.unidade_analise[n]["freq_v"] = round((self.unidade_analise[n]["V"] / total) * 100, 2)
                self.unidade_analise[n]["freq_p"] = round((self.unidade_analise[n]["P"] / total) * 100, 2)
                self.unidade_analise[n]["freq_b"] = round((self.unidade_analise[n]["B"] / total) * 100, 2)

        if len(dados) >= 12:
            for i in range(len(dados) - 12):
                sub_num = [d['numero'] for d in dados[i:i+12]]
                sub_pol = [d['cor'] for d in dados[i:i+12]]
                cor_futura = dados[i+12]['cor'] if (i+12) < len(dados) else None
                if cor_futura:
                    texto = "".join(sub_pol)
                    for _ in range(multiplicador_peso):
                        if "PVPV" in texto: self.modelo_transicao[("XADREZ", "PVPV")].append(cor_futura)
                        if "VPVP" in texto: self.modelo_transicao[("XADREZ", "VPVP")].append(cor_futura)

    def injetar_aprendizado_imediato(self, sub_dados, multiplicador_peso=4):
        self.dados_recencia.extend(sub_dados)
        self._processar_bloco_dados(sub_dados, multiplicador_peso, True)

    def predizer_proxima_casa(self, sub_num, sub_pol):
        if len(sub_num) < 12:
            return "NEUTRO", 0.0, "Janela insuficiente"

        ultimo_num = sub_num[-1]
        ultimas_cores = (sub_pol[-2], sub_pol[-1])

        trans = self.modelo_transicao.get(ultimas_cores, [])
        por_num = self.modelo_numerico.get(ultimo_num, [])

        texto = "".join(sub_pol)
        geom = []
        if "PVPV" in texto: geom.extend(self.modelo_transicao.get(("XADREZ", "PVPV"), []))
        if "VPVP" in texto: geom.extend(self.modelo_transicao.get(("XADREZ", "VPVP"), []))

        stats = self.unidade_analise.get(ultimo_num, {"freq_v": 0, "freq_p": 0})

        v_bonus = stats.get("freq_v", 0) * 3.5
        p_bonus = stats.get("freq_p", 0) * 3.5

        pos_v = stats.get("pos_numero_V", 0)
        pos_p = stats.get("pos_numero_P", 0)
        pos_total = pos_v + pos_p

        if pos_total >= 5:
            if pos_v > pos_p * 1.25:
                v_bonus += 14
            elif pos_p > pos_v * 1.25:
                p_bonus += 14

        has_rec = len(self.dados_recencia) > 0
        p_trans = 0.22 if has_rec else 0.17
        p_num = 0.18 if has_rec else 0.16
        p_geom = 0.25

        total_v = (trans.count('V') * p_trans) + (por_num.count('V') * p_num) + (geom.count('V') * p_geom) + v_bonus
        total_p = (trans.count('P') * p_trans) + (por_num.count('P') * p_num) + (geom.count('P') * p_geom) + p_bonus

        if total_v + total_p == 0: 
            return "NEUTRO", 0.0, "Sem dados suficientes para previsão"

        prob_v = (total_v / (total_v + total_p)) * 100
        prob_p = (total_p / (total_v + total_p)) * 100

        BARREIRA = 52.5
        if prob_v >= BARREIRA and prob_v > prob_p + 4:
            return "VERMELHO", round(prob_v, 1), f"Confluência estatística forte para Vermelho ({prob_v:.1f}%)"
        elif prob_p >= BARREIRA and prob_p > prob_v + 4:
            return "PRETO", round(prob_p, 1), f"Confluência estatística forte para Preto ({prob_p:.1f}%)"
        return "NEUTRO", round(max(prob_v, prob_p), 1), "Sem confluência estatística clara"


# ============================================================
# JuizHierarquicoModificado - Reforçado com Hierarquia mais clara
# ============================================================
class JuizHierarquicoModificado:
    @staticmethod
    def arbitrar_sinal(no_call_ativo, motivo_nc, expectations, inclinacao_num, geometria_mercado, 
                       previsao_ia, status_inversao, historico_revalida_regras, 
                       modo_mercado="NEUTRO", 
                       streak_atual=0, xadrez_len=0, xadrez_quebrou=False,
                       contexto_exaustao=False,
                       sintese_evidencias=None):
        
        # 1. NO CALL tem prioridade absoluta
        if no_call_ativo:
            return "NO CALL", motivo_nc, "SISTEMA_TRAVADO"

        direcao_ia, confianca_ia, raciocinio_ia = previsao_ia

        # 2. Regras posicionais fortes (prioridade alta)
        if expectations:
            count_v = sum(1 for item in expectations if item["direcao"] == "VERMELHO")
            count_p = sum(1 for item in expectations if item["direcao"] == "PRETO")

            if count_v > count_p:
                return "VERMELHO", "Regra posicional ativa com apoio", "REGRA_POSICIONAL"
            elif count_p > count_v:
                return "PRETO", "Regra posicional ativa com apoio", "REGRA_POSICIONAL"

        # 3. Geometria forte (com contexto)
        if geometria_mercado in ["CICLO_FECHADO_VPPV", "CICLO_FECHADO_PVVP"]:
            if streak_atual >= 4 or xadrez_len >= 4:
                return "NO CALL", f"Geometria forte, mas contexto de alta alternância/streak ({streak_atual}x)", "GEOMETRIA_CONTEXTO"
            
            if geometria_mercado == "CICLO_FECHADO_VPPV": 
                return "PRETO", "Geometria VPPV (Padrão forte)", "GEOMETRIA_FORTE"
            if geometria_mercado == "CICLO_FECHADO_PVVP": 
                return "VERMELHO", "Geometria PVVP (Padrão forte)", "GEOMETRIA_FORTE"

        # 4. IA com contexto de reversão
        if direcao_ia != "NEUTRO" and confianca_ia >= 52:
            if contexto_exaustao or (streak_atual >= 5) or (xadrez_len >= 4 and xadrez_quebrou):
                return direcao_ia, f"IA + Contexto de reversão ({raciocinio_ia})", "IA_CONTEXTO_REVERSAO"
            return direcao_ia, f"IA Preditiva ({confianca_ia:.1f}%)", "IA_PREDITIVA"

        return "NO CALL", "Sem confluência suficiente após análise estruturada", "SISTEMA_TRAVADO"


# ============================================================
# MotorContagensProjetivas + Classes Auxiliares (mantidos)
# ============================================================
class MotorContagensProjetivas:
    @staticmethod
    def mapear_janela(sub_num, sub_pol, geometry_mercado):
        lista_bruta = []
        REGRAS_PROJECAO = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7}

        for i in range(12):
            num_atual = sub_num[i]
            if num_atual in REGRAS_PROJECAO:
                passo = REGRAS_PROJECAO[num_atual]
                alvo_idx = i + passo
                if alvo_idx == 11:
                    if i < 10 and 0 in sub_num[i:11]: continue
                    lista_bruta.append({
                        "direcao": "VERMELHO", 
                        "tipo_regra": f"V3_ATIVADOR_{num_atual}", 
                        "origem": f"Volume 3: Ativador {num_atual}"
                    })

        par_fechamento = (sub_num[10], sub_num[11])
        continuidade_preta_validas = [(8,9), (9,10), (10,11), (11,12), (12,13), (13,14), (14,13), (13,12), (12,11), (11,10)]
        continuidade_vermelha_validas = [(1,2), (2,3), (3,4), (4,5), (5,6), (6,7), (7,6), (6,5), (5,4), (4,3)]

        if par_fechamento in continuidade_preta_validas:
            lista_bruta.append({"direcao": "PRETO", "tipo_regra": "V2_CONTINUIDADE_PRETA", "origem": "Volume 2"})
        elif par_fechamento in continuidade_vermelha_validas:
            lista_bruta.append({"direcao": "VERMELHO", "tipo_regra": "V2_CONTINUIDADE_VERMELHA", "origem": "Volume 2"})

        tem_branco_recente = any(p == "B" for p in sub_pol[7:11])

        if not tem_branco_recente:
            if sub_num[5] == 2:
                lista_bruta.append({"direcao": "VERMELHO", "tipo_regra": "V12_POSICIONAL_2", "origem": "Volume 12"})
            if sub_num[5] == 3:
                lista_bruta.append({"direcao": "VERMELHO", "tipo_regra": "V12_POSICIONAL_3", "origem": "Volume 12"})
            if sub_num[11] == 4 and sub_pol[10] == "P":
                lista_bruta.append({"direcao": "PRETO", "tipo_regra": "V12_RETENCAO_4", "origem": "Volume 12"})
            if sub_num[11] == 10:
                lista_bruta.append({"direcao": "PRETO", "tipo_regra": "V12_RESIDUO_10", "origem": "Volume 12"})
            elif sub_num[10] == 5 and sub_num[11] == 10:
                lista_bruta.append({"direcao": "PRETO", "tipo_regra": "V12_ACOPLAMENTO_5_10", "origem": "Volume 12"})

        return lista_bruta


class SequenciaOperacional:
    def __init__(self, lista_resultados):
        self.cronologia = lista_resultados
        self.numerica = [int(r['numero']) for r in self.cronologia]
        self.polaridades = [str(r['cor']).upper() for r in self.cronologia]
        self.total = len(self.numerica)

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
        df_novos_invertido = df_novos.iloc[::-1].reset_index(drop=True)
        
        if os.path.exists(caminho_recencia):
            try:
                df_atual = pd.read_excel(caminho_recencia)
                df_consolidado = pd.concat([df_novos_invertido, df_atual], ignore_index=True)
                df_consolidado.to_excel(caminho_recencia, index=False)
            except:
                df_novos_invertido.to_excel(caminho_recencia, index=False)
        else:
            df_novos_invertido.to_excel(caminho_recencia, index=False)

class AnalisadorContextoAvancado:
    @staticmethod
    def calcular_numerologia_pos_numero(num_fechamento, sequencia_num, sequencia_pol):
        contagem_v = contagem_p = contagem_b = 0
        for i in range(len(sequencia_num) - 1):
            if sequencia_num[i] == num_fechamento:
                prox = sequencia_pol[i + 1]
                if prox == "V": contagem_v += 1
                elif prox == "P": contagem_p += 1
                elif prox == "B": contagem_b += 1
        total = contagem_v + contagem_p + contagem_b
        if total < 3: return "NEUTRO", 0.0
        pct_v = (contagem_v / total) * 100
        pct_p = (contagem_p / total) * 100
        if pct_v >= 60.0: return "VERMELHO", pct_v
        if pct_p >= 60.0: return "PRETO", pct_p
        return "NEUTRO", max(pct_v, pct_p)

    @staticmethod
    def mapear_padroes_geometria(sub_pol):
        texto = "".join(sub_pol)
        if texto.endswith("VPPV"): return "CICLO_FECHADO_VPPV"
        if texto.endswith("PVVP"): return "CICLO_FECHADO_PVVP"
        if "VVVV" in texto: return "SATURAÇÃO ESTRUTURAL (V)"
        if "PPPP" in texto: return "SATURAÇÃO ESTRUTURAL (P)"
        if "VPVP" in texto or "PVPV" in texto: return "XADREZ ATIVO"
        return "ESTÁVEL"

    @staticmethod
    def detectar_chance_inversao(sub_pol):
        texto = "".join(sub_pol)
        if texto.endswith("VVVV"): return True, "INVERSÃO", "Exaustão de Vermelhos"
        if texto.endswith("PPPP"): return True, "INVERSÃO", "Exaustão de Pretos"
        return False, "NORMAL", "Fluxo Estável"

    @staticmethod
    def preditor_estatistico_branco(num_fechamento, sequencia_num, sequencia_pol):
        if not sequencia_pol: return "BAIXA", 0
        atraso = 0
        for cor in reversed(sequencia_pol):
            if cor == "B": break
            atraso += 1
        vezes_num = vezes_branco = 0
        for i in range(len(sequencia_num) - 1):
            if sequencia_num[i] == num_fechamento:
                vezes_num += 1
                if "B" in sequencia_pol[i+1:i+4]:
                    vezes_branco += 1
        taxa = (vezes_branco / vezes_num * 100) if vezes_num > 0 else 0
        chance = "ALTA" if atraso >= 15 or taxa >= 18 else ("MÉDIA" if atraso >= 8 else "BAIXA")
        return chance, atraso

    @staticmethod
    def detectar_modo_mercado(sub_pol):
        texto = "".join(sub_pol)
        alternancias = sum(1 for i in range(len(texto)-1) if texto[i] != texto[i+1])
        if alternancias >= 7: return "CHUVA"
        elif alternancias <= 3: return "RECUPERACAO"
        return "NEUTRO"


class LeitorXLS:
    def __init__(self, caminho_arquivo):
        self.caminho = caminho_arquivo

    def ler_e_validar(self):
        if not os.path.exists(self.caminho):
            return None
        try:
            df = pd.read_excel(self.caminho)
            df.columns = [str(col).strip().lower() for col in df.columns]

            col_num = None
            for c in df.columns:
                if c in ['número', 'numero', 'num']:
                    col_num = c
                    break
            if col_num is None:
                return None

            df = df.rename(columns={col_num: 'numero'})
            df = df.iloc[::-1].reset_index(drop=True)

            if len(df) < 5:
                return None

            dados = []
            for _, row in df.iterrows():
                try:
                    num = int(row['numero'])
                    if num == 0: cor = 'B'
                    elif 1 <= num <= 7: cor = 'V'
                    elif 8 <= num <= 14: cor = 'P'
                    else: continue
                    dados.append({"numero": num, "cor": cor})
                except:
                    continue
            return dados if len(dados) >= 5 else None
        except Exception as e:
            print(f"[LeitorXLS] Erro: {e}")
            return None


# ============================================================
# MotorV1Completo
# ============================================================
class MotorV1Completo:
    def __init__(self, lista_dados_xls):
        self.seq = SequenciaOperacional(lista_dados_xls)
        corte = max(0, len(lista_dados_xls) - 150)
        self.dados_longo = lista_dados_xls[:corte]
        self.dados_curto = lista_dados_xls[corte:]
        
        base_recencia = None
        if os.path.exists("base_recencia_ativa.xlsx"):
            try:
                base_recencia = LeitorXLS("base_recencia_ativa.xlsx").ler_e_validar()
            except:
                pass
        
        dados_consolidados = self.dados_curto + (base_recencia or [])
        self.ia = IAPreditivaV1(self.dados_longo, dados_consolidados)
        self.historico_regras = defaultdict(lambda: {"acertos": 1, "total": 1})
        self.stats = {"G0": 0, "G1": 0, "G2": 0, "FALHA": 0, "NO CALL": 0}

    def processar_auditoria(self):
        idx = 0
        memorias = []
        stats = {"G0": 0, "G1": 0, "G2": 0, "FALHA": 0, "NO CALL": 0}

        while idx + 12 < self.seq.total:
            sub_num = self.seq.numerica[idx:idx+12]
            sub_pol = self.seq.polaridades[idx:idx+12]

            geometria = AnalisadorContextoAvancado.mapear_padroes_geometria(sub_pol)
            status_inv = AnalisadorContextoAvancado.detectar_chance_inversao(sub_pol)
            nc_ativo, motivo_nc = MotorNoCall.checar_no_call(sub_num, sub_pol)
            expectativas = MotorContagensProjetivas.mapear_janela(sub_num, sub_pol, geometria)
            num_fech = sub_num[-1]
            inclinacao = AnalisadorContextoAvancado.calcular_numerologia_pos_numero(num_fech, self.seq.numerica, self.seq.polaridades)
            direcao_ia, conf_ia, raciocinio_ia = self.ia.predizer_proxima_casa(sub_num, sub_pol)
            modo_mercado = AnalisadorContextoAvancado.detectar_modo_mercado(sub_pol)

            streak = 0
            for c in reversed(sub_pol):
                if c == sub_pol[-1]: streak += 1
                else: break

            xadrez_len = 0
            for i in range(len(sub_pol)-1, 0, -1):
                if sub_pol[i] != sub_pol[i-1]:
                    xadrez_len += 1
                else:
                    break
            xadrez_quebrou = (sub_pol[-1] == sub_pol[-2]) if len(sub_pol) >= 2 else False

            sinal, justificativa, regra_id = JuizHierarquicoModificado.arbitrar_sinal(
                nc_ativo, motivo_nc, expectativas, inclinacao, geometria, 
                (direcao_ia, conf_ia, raciocinio_ia), status_inv, self.historico_regras,
                modo_mercado=modo_mercado,
                streak_atual=streak,
                xadrez_len=xadrez_len,
                xadrez_quebrou=xadrez_quebrou
            )

            if sinal != "NO CALL" and streak >= 6:
                if direcao_ia != sinal:
                    sinal = "NO CALL"
                    justificativa = f"Veto de streak {streak}x (contra IA)"
                    regra_id = "VETO_STREAK"

            correcoes = self.seq.polaridades[idx+12 : idx+15]
            classificacao = "FALHA"
            salto = 3

            if sinal == "NO CALL":
                classificacao = "NO CALL RESPEITADO"
                stats["NO CALL"] += 1
                salto = 1
            else:
                letra = "V" if sinal == "VERMELHO" else "P"
                for g, cor in enumerate(correcoes):
                    if cor == letra or cor == "B":
                        classificacao = f"G{g}"
                        salto = g + 1
                        break

            stats[classificacao] = stats.get(classificacao, 0) + 1

            if regra_id not in ["NENHUMA", "SISTEMA_TRAVADO"]:
                self.historico_regras[regra_id]["total"] += 1
                if classificacao in ["G0", "G1"]:
                    self.historico_regras[regra_id]["acertos"] += 1

            bloco = [{"numero": self.seq.numerica[k], "cor": self.seq.polaridades[k]} 
                     for k in range(idx, min(idx + 12 + salto, self.seq.total))]
            self.ia.injetar_aprendizado_imediato(bloco, 4)

            memorias.append(f"Janela {len(memorias)+1}: {sub_num} -> {sinal} | {justificativa} | {classificacao}")
            idx += 12 + salto

        self.stats = stats
        total_com_sinal = stats.get("G0",0) + stats.get("G1",0) + stats.get("G2",0) + stats.get("FALHA",0)
        denom = total_com_sinal if total_com_sinal > 0 else 1

        output = "[MEMÓRIA DE CÁLCULO DAS JANELAS MÓVEIS]\n"
        output += "\n".join(memorias) + "\n\n"
        output += "[RESULTADO FINAL TIPO D]\n"
        output += f"CRONOLOGIA VALIDADA: {self.seq.total} Resultados\n"
        output += f"TOTAL DE JANELAS AUDITADAS: {len(memorias)}\n"
        output += f" - Taxa G0: {stats.get('G0',0)} Ocorrências ({(stats.get('G0',0)/denom)*100:.2f}%)\n"
        output += f" - Taxa G1: {stats.get('G1',0)} Ocorrências ({(stats.get('G1',0)/denom)*100:.2f}%)\n"
        output += f" - Taxa G2: {stats.get('G2',0)} Ocorrências ({(stats.get('G2',0)/denom)*100:.2f}%)\n"
        output += f" - Taxa de Falha: {stats.get('FALHA',0)} Ocorrências ({(stats.get('FALHA',0)/denom)*100:.2f}%)\n"
        output += f" - Taxa de NO CALL: {stats.get('NO CALL',0)} Ocorrências\n\n"

        if stats.get("FALHA", 0) >= 25:
            condicao = "MERCADO EM DEGRADAÇÃO"
        elif stats.get("G0", 0) >= 50:
            condicao = "MERCADO PAGADOR"
        else:
            condicao = "MERCADO INSTÁVEL"
        output += f"ESTADO ATUAL DO MERCADO: {condicao}\n"

        return output


# ============================================================
# ProcessadorTipoB - Atualizado com Hierarquia mais clara
# ============================================================
class ProcessadorTipoB:
    def __init__(self, sequencia_12_numeros, caminho_base_dados):
        self.entrada = sequencia_12_numeros
        self.caminho_base = caminho_base_dados
        self.polaridades = ['B' if n == 0 else ('V' if 1 <= n <= 7 else 'P') for n in sequencia_12_numeros]

    def executar_sinal_real(self):
        if len(self.entrada) != 12:
            return {"erro": "Necessário exatamente 12 números"}
        
        ia = carregar_modelo_longo_prazo()
        if ia is None:
            base = LeitorXLS(self.caminho_base).ler_e_validar()
            if not base:
                return {"erro": "Base de dados não encontrada"}
            ia = IAPreditivaV1(base, None)

        base_rec = None
        if os.path.exists("base_recencia_ativa.xlsx"):
            base_rec = LeitorXLS("base_recencia_ativa.xlsx").ler_e_validar()
            if base_rec:
                ia.injetar_aprendizado_imediato(base_rec, multiplicador_peso=4)

        evidencias = []

        # RELEITURA 1 - Segurança (NO CALL)
        nc_ativo, motivo_nc = MotorNoCall.checar_no_call(self.entrada, self.polaridades)
        evidencias.append({"releitura": 1, "tipo": "Segurança (NO CALL)", "resultado": {"ativo": nc_ativo, "motivo": motivo_nc}})

        # RELEITURA 2 - Geometria
        geometria = AnalisadorContextoAvancado.mapear_padroes_geometria(self.polaridades)
        evidencias.append({"releitura": 2, "tipo": "Geometria", "resultado": geometria})

        # RELEITURA 3 - Regras Projetivas (Volume 12)
        expectativas = MotorContagensProjetivas.mapear_janela(self.entrada, self.polaridades, geometria)
        evidencias.append({"releitura": 3, "tipo": "Regras Projetivas (Volume 12)", "resultado": expectativas})

        # RELEITURA 4 - Contexto Avançado
        base_longa = LeitorXLS(self.caminho_base).ler_e_validar() or []
        inclinacao = AnalisadorContextoAvancado.calcular_numerologia_pos_numero(
            self.entrada[-1], [d['numero'] for d in base_longa], [d['cor'] for d in base_longa]
        )
        modo_mercado = AnalisadorContextoAvancado.detectar_modo_mercado(self.polaridades)
        evidencias.append({"releitura": 4, "tipo": "Contexto Avançado", "resultado": {"inclinacao": inclinacao, "modo_mercado": modo_mercado}})

        # RELEITURA 5 - IA Probabilística
        direcao_ia, conf_ia, raciocinio_ia = ia.predizer_proxima_casa(self.entrada, self.polaridades)
        evidencias.append({"releitura": 5, "tipo": "IA Probabilística", "resultado": {"direcao": direcao_ia, "confianca": conf_ia, "raciocinio": raciocinio_ia}})

        # RELEITURA 6 - Análise Sequencial
        streak = 0
        for c in reversed(self.polaridades):
            if c == self.polaridades[-1]: streak += 1
            else: break

        xadrez_len = 0
        for i in range(len(self.polaridades)-1, 0, -1):
            if self.polaridades[i] != self.polaridades[i-1]:
                xadrez_len += 1
            else: break

        xadrez_quebrou = (self.polaridades[-1] == self.polaridades[-2]) if len(self.polaridades) >= 2 else False
        contexto_exaustao = (streak >= 5) or (xadrez_len >= 5 and xadrez_quebrou)

        evidencias.append({
            "releitura": 6, 
            "tipo": "Análise Sequencial (Streak/Xadrez/Exaustão)", 
            "resultado": {
                "streak": streak, 
                "xadrez_len": xadrez_len, 
                "xadrez_quebrou": xadrez_quebrou,
                "contexto_exaustao": contexto_exaustao
            }
        })

        sintese = []
        if nc_ativo:
            sintese.append("Bloqueio por NO CALL ativo.")
        if geometria in ["CICLO_FECHADO_VPPV", "CICLO_FECHADO_PVVP"]:
            sintese.append(f"Padrão geométrico forte detectado: {geometria}.")
        if expectativas:
            sintese.append(f"Regras projetivas ativas ({len(expectativas)} evidências).")
        if direcao_ia != "NEUTRO" and conf_ia >= 52:
            sintese.append(f"IA com sinal {direcao_ia} e confiança {conf_ia}%.")
        if contexto_exaustao:
            sintese.append("Contexto de exaustão/streak longo favorece reversão.")

        raciocinio_final = " | ".join(sintese) if sintese else "Análise sem confluência forte entre as camadas."

        sinal, justificativa, regra_id = JuizHierarquicoModificado.arbitrar_sinal(
            nc_ativo, motivo_nc, expectativas, inclinacao, geometria,
            (direcao_ia, conf_ia, raciocinio_ia), None,
            defaultdict(lambda: {"acertos": 1, "total": 1}),
            modo_mercado=modo_mercado,
            streak_atual=streak,
            xadrez_len=xadrez_len,
            xadrez_quebrou=xadrez_quebrou,
            contexto_exaustao=contexto_exaustao,
            sintese_evidencias=raciocinio_final
        )

        if sinal != "NO CALL" and streak >= 6:
            if direcao_ia != sinal:
                sinal = "NO CALL"
                justificativa = f"Veto de streak {streak}x (contra IA)"
                regra_id = "VETO_STREAK"

        return {
            "sinal": sinal,
            "justificativa": justificativa,
            "confianca_ia": round(conf_ia, 2),
            "no_call": nc_ativo,
            "memoria": f"[PROCESSAMENTO TIPO B - RELEITURAS ESTRUTURADAS] Sequência: {self.entrada}",
            "releituras": evidencias,
            "sintese_raciocinio": raciocinio_final,
            "decisao_final": {"sinal": sinal, "justificativa": justificativa, "regra_id": regra_id}
        }


class EngineMatematicoAvancado:
    
    @staticmethod
    def calcular_raridade_sequencia(sub_pol):
        if not sub_pol:
            return {"streak": 0, "probabilidade": 100.0, "status": "SEM DADOS"}
        
        ultima_cor = sub_pol[-1]
        if ultima_cor not in ['V', 'P']:
            return {"streak": 0, "probabilidade": 100.0, "status": "BRANCO NO FECHAMENTO"}
        
        streak = 0
        for cor in reversed(sub_pol):
            if cor == ultima_cor: streak += 1
            else: break
        
        probabilidade_sequencia = ((7 / 15) ** streak) * 100
        status = "SATURAÇÃO CRÍTICA (Risco Elevado de Inversão)" if streak >= 5 else \
                 ("DESVIO PADRÃO EM CURSO" if streak >= 3 else "ESTRUTURA DENTRO DA NORMALIDADE")
        
        return {
            "streak": streak,
            "cor_sequencia": "VERMELHO" if ultima_cor == 'V' else "PRETO",
            "probabilidade": round(probabilidade_sequencia, 2),
            "status": status
        }

    @staticmethod
    def calcular_vies_surfe(caminho_base, janela=100):
        leitor = LeitorXLS(caminho_base)
        dados = leitor.ler_e_validar()
        if not dados:
            return {"vies": "INDISPONÍVEL", "desvio_v": 0.0, "desvio_p": 0.0, 
                    "frequencia_v": 46.67, "frequencia_p": 46.67, "frequencia_b": 6.67}
        
        ultimos = dados[-janela:]
        v = sum(1 for d in ultimos if d['cor'] == 'V')
        p = sum(1 for d in ultimos if d['cor'] == 'P')
        b = sum(1 for d in ultimos if d['cor'] == 'B')
        
        pct_v = (v / len(ultimos)) * 100
        pct_p = (p / len(ultimos)) * 100
        pct_b = (b / len(ultimos)) * 100
        
        desvio_v = round(pct_v - 46.67, 2)
        desvio_p = round(pct_p - 46.67, 2)
        
        vies = "SURFE DE MACROFREQUÊNCIA: VIÁS PARA VERMELHO ATIVO" if pct_v >= 53.0 else \
               ("SURFE DE MACROFREQUÊNCIA: VIÁS PARA PRETO ATIVO" if pct_p >= 53.0 else "MACROANÁLISE EQUILIBRADA")
        
        return {
            "frequencia_v": round(pct_v, 2),
            "frequencia_p": round(pct_p, 2),
            "frequencia_b": round(pct_b, 2),
            "desvio_v": desvio_v,
            "desvio_p": desvio_p,
            "vies": vies
        }

    @staticmethod
    def simular_split_stake_cobertura(stake_principal=10.0):
        stake_branco_ideal = round(stake_principal / 7.0, 2)
        stake_branco_conservador = round(stake_principal / 10.0, 2)
        custo_total = stake_principal + stake_branco_ideal
        lucro_liquido = round((stake_branco_ideal * 14) - custo_total, 2)
        
        return {
            "stake_cor": stake_principal,
            "cobertura_b_ideal_1_7": stake_branco_ideal,
            "cobertura_b_matematica_1_10": stake_branco_conservador,
            "lucro_liquido_se_der_branco": lucro_liquido,
            "custo_total_operacao": round(custo_total, 2),
            "house_edge_estatico": "-6.67%"
        }


# ============================================================
# FIM DO CÓDIGO
# ============================================================
