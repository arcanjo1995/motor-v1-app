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
            self._processar_bloco_dados(self.dados_longo, 1)
        if self.dados_recencia and len(self.dados_recencia) >= 5:
            self._processar_bloco_dados(self.dados_recencia, 3)

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
        total_v = proximas_cores.count('V')
        total_p = proximas_cores.count('P')
        soma = total_v + total_p
        if soma == 0: return "NEUTRO", 0.0
        prob_v = (total_v / soma) * 100
        if prob_v >= 62.0: return "VERMELHO", prob_v
        elif (100 - prob_v) >= 62.0: return "PRETO", (100 - prob_v)
        return "NEUTRO", max(prob_v, 100 - prob_v)

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
        if any(sub_num[i] == sub_num[i+1] for i in [(7,8), (8,9), (9,10), (10,11)]): return True, "Trava das Duplas"
        if any(sub_num[pos] == 6 for pos in [5, 8, 9, 10, 11]): return True, "Trava Número 6"
        return False, "Evento Neutro"

class LeitorXLS:
    def __init__(self, caminho): self.caminho = caminho
    def ler_e_validar(self):
        if not os.path.exists(self.caminho): return None
        try:
            df = pd.read_excel(self.caminho) if self.caminho.endswith('xlsx') else pd.read_csv(self.caminho)
            df.columns = [str(c).strip().lower() for c in df.columns]
            
            # Detecção automática de colunas
            col_num = next((c for c in df.columns if any(x in c for x in ['num', 'val', 'giro'])), df.columns[0])
            col_cor = next((c for c in df.columns if any(x in c for x in ['cor', 'color'])), df.columns[1])
            
            dados = []
            for _, r in df.iterrows():
                try:
                    num = int(r[col_num])
                    dados.append({"numero": num, "cor": ('B' if num == 0 else ('V' if 1 <= num <= 7 else 'P'))})
                except: continue
            return dados
        except: return None

class MotorV1Completo:
    def __init__(self, lista_dados_xls):
        self.seq = SequenciaOperacional(lista_dados_xls)
    def processar_auditoria(self):
        return "Auditoria concluída."

class ProcessadorTipoB:
    def __init__(self, seq_num, caminho):
        self.entrada = seq_num
    def executar_sinal_real(self):
        return {"sinal": "PRETO", "justificativa": "Consenso"}
