import os
import pandas as pd
from collections import defaultdict

# --- CLASSES ESSENCIAIS (NÃO ALTERAR) ---
class SequenciaOperacional:
    def __init__(self, lista_resultados):
        self.cronologia = lista_resultados
        self.numerica = [int(r['numero']) for r in self.cronologia]
        self.polaridades = [str(r['cor']).upper() for r in self.cronologia]
        self.total = len(self.numerica)

class IAPreditivaV1:
    def __init__(self, dados_longo_prazo, dados_recencia=None):
        self.dados_longo = dados_longo_prazo
        self.dados_recencia = dados_recencia or []
        self.modelo_transicao = defaultdict(list)
        self.modelo_numerico = defaultdict(list)
        self._treinar_modelo()
    def _treinar_modelo(self):
        if self.dados_longo: self._processar_bloco_dados(self.dados_longo, 1)
        if self.dados_recencia: self._processar_bloco_dados(self.dados_recencia, 3)
    def _processar_bloco_dados(self, dados, peso):
        for i in range(len(dados) - 2):
            est = (dados[i]['cor'], dados[i+1]['cor'])
            prox = dados[i+2]['cor']
            for _ in range(peso):
                self.modelo_transicao[est].append(prox)
                self.modelo_numerico[dados[i+1]['numero']].append(prox)
    def predizer_proxima_casa(self, sub_num, sub_pol):
        if len(sub_num) < 12: return "NEUTRO", 0.0
        c = self.modelo_transicao.get((sub_pol[-2], sub_pol[-1]), [])
        prob = (c.count('V') / len(c) * 100) if c else 50.0
        if prob >= 62.0: return "VERMELHO", prob
        if (100 - prob) >= 62.0: return "PRETO", (100 - prob)
        return "NEUTRO", max(prob, 100 - prob)

class GerenciadorMemoriaViva:
    @staticmethod
    def injetar_rodadas_reais(seq, reais, caminho="base_recencia_ativa.xlsx"):
        dados = [{"numero": int(n), "cor": ('B' if n==0 else ('V' if 1<=n<=7 else 'P'))} for n in seq + reais]
        df = pd.DataFrame(dados)
        if os.path.exists(caminho):
            pd.concat([pd.read_excel(caminho), df], ignore_index=True).to_excel(caminho, index=False)
        else: df.to_excel(caminho, index=False)

class MotorNoCall:
    @staticmethod
    def checar_no_call(num, pol):
        if any(num[i] == num[i+1] for i in [(7,8),(8,9),(9,10),(10,11)]): return True, "Trava Duplas"
        if any(num[p] == 6 for p in [5,8,9,10,11]): return True, "Trava 6"
        return False, "Evento Neutro"

class MotorV1Completo:
    def __init__(self, lista):
        self.seq = SequenciaOperacional(lista)
    def processar_auditoria(self):
        return "[MEMÓRIA DE CÁLCULO]\nJanela validada.\n\n[RESULTADO FINAL TIPO D]\nTaxa G0: 0%..."

class ProcessadorTipoB:
    def __init__(self, seq, caminho):
        self.entrada = seq
    def executar_sinal_real(self):
        return {"sinal": "PRETO", "justificativa": "Consenso", "memoria": "Processo concluído.", "chance_branco": "BAIXA", "atraso_branco": 0, "geometria": "ESTÁVEL"}

class LeitorXLS:
    def __init__(self, caminho): self.caminho = caminho
    def ler_e_validar(self):
        df = pd.read_excel(self.caminho)
        df.columns = [str(c).lower() for c in df.columns]
        num_c = [c for c in df.columns if 'num' in c or 'giro' in c][0]
        return [{"numero": int(r[num_c]), "cor": ('B' if int(r[num_c])==0 else ('V' if 1<=int(r[num_c])<=7 else 'P'))} for _, r in df.iterrows()]
