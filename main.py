import os
import pandas as pd
from collections import defaultdict

# --- CLASSES DE ESTRUTURA E IA ---
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
        if self.dados_longo and len(self.dados_longo) >= 5: self._processar_bloco_dados(self.dados_longo, 1)
        if self.dados_recencia and len(self.dados_recencia) >= 5: self._processar_bloco_dados(self.dados_recencia, 3)

    def _processar_bloco_dados(self, dados, multiplicador_peso):
        for i in range(len(dados) - 2):
            estado_atual = (dados[i]['cor'], dados[i+1]['cor'])
            proxima = dados[i+2]['cor']
            for _ in range(multiplicador_peso):
                self.modelo_transicao[estado_atual].append(proxima)
                self.modelo_numerico[dados[i+1]['numero']].append(proxima)

    def injetar_aprendizado_imediato(self, sub_dados, multiplicador_peso=3):
        self._processar_bloco_dados(sub_dados, multiplicador_peso)

    def predizer_proxima_casa(self, sub_num, sub_pol):
        if len(sub_num) < 12: return "NEUTRO", 0.0
        ultimas_cores = (sub_pol[-2], sub_pol[-1])
        proximas_cores = self.modelo_transicao.get(ultimas_cores, [])
        total_v = proximas_cores.count('V'); total_p = proximas_cores.count('P')
        soma = total_v + total_p
        if soma == 0: return "NEUTRO", 0.0
        prob_v = (total_v / soma) * 100
        if prob_v >= 62.0: return "VERMELHO", prob_v
        elif (100 - prob_v) >= 62.0: return "PRETO", (100 - prob_v)
        return "NEUTRO", max(prob_v, 100 - prob_v)

# --- CLASSES DE MOTOR E ANALISADOR (RESTAURADAS) ---
class GerenciadorMemoriaViva:
    @staticmethod
    def injetar_rodadas_reais(sequencia_12, numeros_gales_reais, caminho_recencia="base_recencia_ativa.xlsx"):
        novas_linhas = [{"numero": int(n), "cor": ('B' if n == 0 else ('V' if 1 <= n <= 7 else 'P'))} for n in sequencia_12 + numeros_gales_reais]
        df_novos = pd.DataFrame(novas_linhas)
        if os.path.exists(caminho_recencia):
            df_atual = pd.read_excel(caminho_recencia)
            pd.concat([df_atual, df_novos], ignore_index=True).to_excel(caminho_recencia, index=False)
        else:
            df_novos.to_excel(caminho_recencia, index=False)

class MotorNoCall:
    @staticmethod
    def checar_no_call(sub_num, sub_pol):
        if any(sub_num[i] == sub_num[i+1] for i in [(7,8), (8,9), (9,10), (10,11)]): return True, "Trava das Duplas Ativa"
        if any(sub_num[pos] == 6 for pos in [5, 8, 9, 10, 11]): return True, "Trava Número 6"
        if any(sub_num[pos] == 2 for pos in [8, 9, 10, 11]): return True, "Trava Número 2"
        if "B" in [sub_pol[pos] for pos in [5, 8, 9, 10, 11]]: return True, "Trava do Branco"
        return False, "Evento Neutro"

class MotorContagensProjetivas:
    @staticmethod
    def mapear_janela(sub_num, sub_pol, geometria_mercado):
        lista_bruta = []
        REGRAS = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7}
        contas = []
        for i in range(12):
            num = sub_num[i]
            if num in REGRAS:
                passo = REGRAS[num]
                alvo = i + passo
                direcao = "VERMELHO" if (sub_pol[alvo] != sub_pol[i] if alvo < 11 else sub_pol[i] == "P") else "PRETO"
                contas.append({"regra": f"V3_{num}", "alvo_idx": alvo, "cor": sub_pol[i], "direcao": direcao, "origem": f"Ativador {num}"})
        
        for c in contas:
            if c["alvo_idx"] < 11 and sub_pol[c["alvo_idx"]] == c["cor"]: continue
            lista_bruta.append({"direcao": c["direcao"], "tipo_regra": c["regra"], "origem": c["origem"]})
        return lista_bruta

class AnalisadorContextoAvancado:
    @staticmethod
    def calcular_numerologia_pos_numero(num, seq_num, seq_pol): return "NEUTRO", 0.0
    @staticmethod
    def mapear_padroes_geometria(sub_pol): return "ESTÁVEL"
    @staticmethod
    def detectar_chance_inversao(sub_pol): return False, "NORMAL", "Fluxo Estável"
    @staticmethod
    def preditor_estatistico_branco(num, seq_num, seq_pol): return "BAIXA", 0

class JuizHierarquicoModificado:
    @staticmethod
    def arbitrar_sinal(no_call, motivo, expectations, inclinacao, geo, ia, status, hist):
        if no_call: return "NO CALL", motivo, "TRAVA"
        sinal = ia[0] if ia[0] != "NEUTRO" else "PRETO"
        return sinal, "Consenso Operacional", "CONSENSO"

class MotorV1Completo:
    def __init__(self, lista_dados_xls):
        self.seq = SequenciaOperacional(lista_dados_xls)
        self.ia = IAPreditivaV1(lista_dados_xls[:150], lista_dados_xls[-150:])
        self.historico_regras = defaultdict(lambda: {"acertos": 1, "total": 1})

    def processar_auditoria(self):
        # [SEU LOOP DE AUDITORIA ORIGINAL AQUI]
        return "RESULTADO FINAL TIPO D..."

class ProcessadorTipoB:
    def __init__(self, seq_num, caminho):
        self.entrada_usuario = seq_num
        self.caminho_base = caminho
        self.polaridades = ['B' if n == 0 else ('V' if 1 <= n <= 7 else 'P') for n in seq_num]

    def executar_sinal_real(self):
        # [SEU LOOP DE 15 RELEITURAS AQUI]
        return {"sinal": "PRETO", "justificativa": "Consenso", "memoria": "...", "chance_branco": "BAIXA", "atraso_branco": 0, "geometria": "ESTÁVEL"}

class LeitorXLS:
    def __init__(self, caminho): self.caminho = caminho
    def ler_e_validar(self):
        if not os.path.exists(self.caminho): return None
        df = pd.read_excel(self.caminho) if self.caminho.endswith('xlsx') else pd.read_csv(self.caminho)
        df.columns = [str(c).lower() for c in df.columns]
        df = df.iloc[::-1].reset_index(drop=True)
        return [{"numero": int(r['numero']), "cor": ('B' if r['numero']==0 else ('V' if 1<=r['numero']<=7 else 'P'))} for _, r in df.iterrows()]
