import os
import pandas as pd
from collections import defaultdict

# --- CLASSES DE MOTO E IA (ESTRUTURA ORIGINAL MANTIDA) ---

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
            estado = (dados[i]['cor'], dados[i+1]['cor'])
            proxima = dados[i+2]['cor']
            for _ in range(multiplicador_peso):
                self.modelo_transicao[estado].append(proxima)
                self.modelo_numerico[dados[i+1]['numero']].append(proxima)

    def injetar_aprendizado_imediato(self, sub_dados, multiplicador_peso=3):
        self._processar_bloco_dados(sub_dados, multiplicador_peso)

    def predizer_proxima_casa(self, sub_num, sub_pol):
        if len(sub_num) < 12: return "NEUTRO", 0.0
        c = self.modelo_transicao.get((sub_pol[-2], sub_pol[-1]), [])
        prob_v = (c.count('V') / len(c) * 100) if c else 50.0
        if prob_v >= 62.0: return "VERMELHO", prob_v
        if (100 - prob_v) >= 62.0: return "PRETO", (100 - prob_v)
        return "NEUTRO", max(prob_v, 100 - prob_v)

class MotorNoCall:
    @staticmethod
    def checar_no_call(sub_num, sub_pol):
        if any(sub_num[i] == sub_num[i+1] for i in [(7,8), (8,9), (9,10), (10,11)]): return True, "Trava Duplas"
        if any(sub_num[p] == 6 for p in [5,8,9,10,11]): return True, "Trava 6"
        return False, "Evento Neutro"

class MotorContagensProjetivas:
    @staticmethod
    def mapear_janela(sub_num, sub_pol, geometria):
        lista = []
        for i in range(12):
            num = sub_num[i]
            if 1 <= num <= 7:
                passo = num
                alvo = i + passo
                if alvo < 11:
                    cor_origem = sub_pol[i]
                    if sub_pol[alvo] != cor_origem: # Regra de Repercussão
                        lista.append({"direcao": "VERMELHO" if cor_origem == "V" else "PRETO", "tipo_regra": f"V3_{num}", "origem_idx": i})
        return lista

class JuizHierarquicoModificado:
    @staticmethod
    def arbitrar_sinal(no_call, motivo, expectations, ia, historico, entropia):
        if no_call or entropia > 0.85: return "NO CALL", "Trava ou Entropia Alta", "SISTEMA_TRAVADO"
        # IA Arbitra baseada em assertividade por posição
        return ia[0] if ia[0] != "NEUTRO" else "PRETO", "Análise de Sincronia", "IA_PREDITIVA"

class MotorV1Completo:
    def __init__(self, lista_dados_xls):
        self.seq = SequenciaOperacional(lista_dados_xls)
        self.ia = IAPreditivaV1(lista_dados_xls[:150], lista_dados_xls[-150:])
        self.historico_regras = defaultdict(lambda: {"acertos": 1, "total": 1})

    def processar_auditoria(self):
        idx = 0
        stats = {"G0": 0, "G1": 0, "G2": 0, "FALHA": 0, "NO CALL": 0}
        ia_acertos, ia_total = 0, 0
        
        while idx + 12 < self.seq.total:
            sub_num = self.seq.numerica[idx : idx+12]
            sub_pol = self.seq.polaridades[idx : idx+12]
            entropia = len(set(sub_num)) / 12
            
            sinal, just, regra = JuizHierarquicoModificado.arbitrar_sinal(
                *MotorNoCall.checar_no_call(sub_num, sub_pol),
                MotorContagensProjetivas.mapear_janela(sub_num, sub_pol, "ESTÁVEL"),
                self.ia.predizer_proxima_casa(sub_num, sub_pol),
                (False, "", ""), self.historico_regras, entropia
            )
            
            # Validação real
            real = self.seq.polaridades[idx + 12] if idx + 12 < self.seq.total else "X"
            if sinal != "NO CALL":
                ia_total += 1
                if real == ("V" if sinal == "VERMELHO" else "P"): ia_acertos += 1
            
            # (Adicione aqui a lógica de salto e injeção que você já tem)
            idx += 1
            
        assertividade = (ia_acertos / ia_total * 100) if ia_total > 0 else 0
        return f"METRICA_EVOLUÇÃO_IA: {assertividade:.2f}%"

class LeitorXLS:
    def __init__(self, caminho): self.caminho = caminho
    def ler_e_validar(self):
        try:
            df = pd.read_excel(self.caminho) if self.caminho.endswith('xlsx') else pd.read_csv(self.caminho)
            df.columns = [str(c).lower().strip() for c in df.columns]
            num_col = [c for c in df.columns if 'num' in c or 'giro' in c][0]
            cor_col = [c for c in df.columns if 'cor' in c or 'color' in c][0]
            return [{"numero": int(r[num_col]), "cor": ('B' if int(r[num_col])==0 else ('V' if 1<=int(r[num_col])<=7 else 'P'))} for _, r in df.iterrows()]
        except: return None
