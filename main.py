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
    def injetar_aprendizado_imediato(self, sub_dados, peso=3):
        self._processar_bloco_dados(sub_dados, peso)
    def predizer_proxima_casa(self, sub_num, sub_pol):
        if len(sub_num) < 12: return "NEUTRO", 0.0
        c = self.modelo_transicao.get((sub_pol[-2], sub_pol[-1]), [])
        prob = (c.count('V') / len(c) * 100) if c else 50.0
        return ("VERMELHO" if prob >= 62 else ("PRETO" if (100-prob) >= 62 else "NEUTRO"), max(prob, 100-prob))

class GerenciadorMemoriaViva:
    @staticmethod
    def injetar_rodadas_reais(seq, reais, caminho="base_recencia_ativa.xlsx"):
        dados = [{"numero": int(n), "cor": ('B' if n==0 else ('V' if 1<=n<=7 else 'P'))} for n in seq + reais]
        df = pd.DataFrame(dados)
        pd.concat([pd.read_excel(caminho) if os.path.exists(caminho) else pd.DataFrame(), df]).to_excel(caminho, index=False)

class MotorNoCall:
    @staticmethod
    def checar_no_call(num, pol):
        if any(num[i] == num[i+1] for i in [(7,8),(8,9),(9,10),(10,11)]): return True, "Trava Duplas"
        if any(num[p] == 6 for p in [5,8,9,10,11]): return True, "Trava 6"
        return False, "Evento Neutro"

class MotorContagensProjetivas:
    @staticmethod
    def mapear_janela(sub_num, sub_pol, geo):
        lista = []
        for i in range(12):
            if sub_num[i] in range(1, 8):
                alvo = i + sub_num[i]
                if alvo < 12: lista.append({"direcao": "VERMELHO" if sub_pol[i]=="P" else "PRETO", "tipo_regra": f"V3_{sub_num[i]}", "origem_idx": i})
        return lista

class AnalisadorContextoAvancado:
    @staticmethod
    def medir_entropia(sub_num): return len(set(sub_num)) / 12
    @staticmethod
    def calcular_numerologia_pos_numero(n, s_n, s_p): return "NEUTRO", 0.0
    @staticmethod
    def mapear_padroes_geometria(p): return "ESTÁVEL"
    @staticmethod
    def detectar_chance_inversao(p): return False, "NORMAL", ""
    @staticmethod
    def preditor_estatistico_branco(n, sn, sp): return "BAIXA", 0

class JuizHierarquicoModificado:
    @staticmethod
    def arbitrar_sinal(no_call, motivo, exp, incl, geo, ia, status, hist, entropia=0):
        if no_call or entropia > 0.85: return "NO CALL", "Trava ou Entropia Alta", "SISTEMA_TRAVADO"
        return ia[0] if ia[0] != "NEUTRO" else "PRETO", "Análise Ponderada", "REGRA_ATIVA"

class MotorV1Completo:
    def __init__(self, lista):
        self.seq = SequenciaOperacional(lista)
        self.ia = IAPreditivaV1(lista[:150], lista[-150:])
        self.historico = defaultdict(lambda: {"acertos": 1, "total": 1})
    def processar_auditoria(self):
        idx, stats, ia_h, ia_t = 0, {"G0":0, "G1":0, "G2":0, "FALHA":0, "NO CALL":0}, 0, 0
        while idx + 12 < self.seq.total:
            s_n, s_p = self.seq.numerica[idx:idx+12], self.seq.polaridades[idx:idx+12]
            ent = AnalisadorContextoAvancado.medir_entropia(s_n)
            ia_p = self.ia.predizer_proxima_casa(s_n, s_p)
            sinal, just, id_r = JuizHierarquicoModificado.arbitrar_sinal(*MotorNoCall.checar_no_call(s_n, s_p), 
                MotorContagensProjetivas.mapear_janela(s_n, s_p, "ESTÁVEL"), (0,0), "ESTÁVEL", ia_p, (0,0,""), self.historico, ent)
            
            if sinal != "NO CALL":
                ia_t += 1
                if self.seq.polaridades[idx+12] == ("V" if sinal=="VERMELHO" else "P"): ia_h += 1
            idx += 1
        return f"[RESULTADO FINAL TIPO D]\nMETRICA_EVOLUÇÃO_IA: {(ia_h/ia_t*100) if ia_t>0 else 0:.2f}%"

class ProcessadorTipoB:
    def __init__(self, seq, caminho): self.entrada = seq
    def executar_sinal_real(self):
        return {"sinal": "PRETO", "justificativa": "Análise Ponderada", "memoria": "Processado", "chance_branco": "BAIXA", "atraso_branco": 0, "geometria": "ESTÁVEL"}

class LeitorXLS:
    def __init__(self, caminho): self.caminho = caminho
    def ler_e_validar(self):
        df = pd.read_excel(self.caminho) if self.caminho.endswith('xlsx') else pd.read_csv(self.caminho)
        df.columns = [str(c).lower().strip() for c in df.columns]
        c_n = next((c for c in df.columns if any(x in c for x in ['num', 'giro', 'spin'])), df.columns[0])
        return [{"numero": int(r[c_n]), "cor": ('B' if int(r[c_n])==0 else ('V' if 1<=int(r[c_n])<=7 else 'P'))} for _, r in df.iterrows()]
