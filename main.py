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
        """
        Inicializa a IA Preditiva utilizando a cronologia reconstruída.
        Mapeia a probabilidade de transição de estados com base em pesos de contexto.
        """
        self.dados = dados_limpos
        self.modelo_transicao = defaultdict(list)
        self.modelo_numerico = defaultdict(list)
        self._treinar_modelo()

    def _treinar_modelo(self):
        """
        Treina a IA analisando os padrões históricos de recência.
        Mapeia sequências de cores e resíduos de fechamentos numéricos.
        """
        if not self.dados or len(self.dados) < 5:
            return

        for i in range(len(self.dados) - 2):
            # Padrão sequencial geométrico (últimas 2 pedras)
            estado_atual_cor = (self.dados[i]['cor'], self.dados[i+1]['cor'])
            proxima_cor = self.dados[i+2]['cor']
            self.modelo_transicao[estado_atual_cor].append(proxima_cor)

            # Padrão de resíduo numérico imediato
            num_atual = self.dados[i+1]['numero']
            self.modelo_numerico[num_atual].append(proxima_cor)

    def predizer_proxima_casa(self, sub_num, sub_pol):
        """
        Executa a inferência cruzando a Geometria Atual com a tendência histórica.
        Retorna o Veredito da IA e a sua taxa de confiança percentual.
        """
        if len(sub_num) < 12:
            return "NEUTRO", 0.0

        ultimo_num = sub_num[-1]
        ultimas_cores = (sub_pol[-2], sub_pol[-1])

        # 1. Probabilidade por Padrão de Polaridade (Peso 60%)
        proximas_cores_historicas = self.modelo_transicao.get(ultimas_cores, [])
        # 2. Probabilidade por Resíduo de Fechamento (Peso 40%)
        proximas_cores_por_num = self.modelo_numerico.get(ultimo_num, [])

        total_v = (proximas_cores_historicas.count('V') * 0.6) + (proximas_cores_por_num.count('V') * 0.4)
        total_p = (proximas_cores_historicas.count('P') * 0.6) + (proximas_cores_por_num.count('P') * 0.4)
        total_b = (proximas_cores_historicas.count('B') * 0.6) + (proximas_cores_por_num.count('B') * 0.4)

        soma_pesos = total_v + total_p + total_b
        if soma_pesos == 0:
            return "NEUTRO", 0.0

        prob_v = (total_v / soma_pesos) * 100
        prob_p = (total_p / soma_pesos) * 100

        # Barreira estatística de segurança para ativação do sinal da IA
        BARREIRA_CONFIA_IA = 58.0

        if prob_v >= BARREIRA_CONFIA_IA and prob_v > prob_p:
            return "VERMELHO", prob_v
        elif prob_p >= BARREIRA_CONFIA_IA and prob_p > prob_v:
            return "PRETO", prob_p
        
        return "NEUTRO", max(prob_v, prob_p)

class MotorNoCall:
    @staticmethod
    def checar_no_call(sub_num, sub_pol):
        # 1. REGRA DAS DUPLAS (Volume 2, Capítulo 6) - Adjacência Cronológica Absoluta
        cenarios_duplas =
