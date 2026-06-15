import os
import pandas as pd
from collections import defaultdict

# --- Classes de Base (SequenciaOperacional, IAPreditivaV1, GerenciadorMemoriaViva, MotorNoCall) 
# permanecem idênticas à sua versão funcional atual ---

class AnalisadorContextoAvancado:
    @staticmethod
    def medir_entropia_janela(sub_num):
        # Mede a diversidade de números. Quanto mais perto de 1.0, mais aleatório (ruído).
        return len(set(sub_num)) / 12

    @staticmethod
    def calcular_numerologia_pos_numero(num_fechamento, sequencia_num, sequencia_pol):
        contagem_v, contagem_p, contagem_b = 0, 0, 0
        for i in range(len(sequencia_num) - 1):
            if sequencia_num[i] == num_fechamento:
                proxima_cor = sequencia_pol[i + 1]
                if proxima_cor == "V": contagem_v += 1
                elif proxima_cor == "P": contagem_p += 1
                elif proxima_cor == "B": contagem_b += 1
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
        if "VVVV" in texto: return "SATURAÇÃO_V"
        if "PPPP" in texto: return "SATURAÇÃO_P"
        return "ESTÁVEL"

    @staticmethod
    def detectar_chance_inversao(sub_pol):
        texto = "".join(sub_pol)
        if texto.endswith("VVVV"): return True, "INVERSÃO", "Exaustão V"
        if texto.endswith("PPPP"): return True, "INVERSÃO", "Exaustão P"
        return False, "NORMAL", "Fluxo Estável"

    @staticmethod
    def preditor_estatistico_branco(num, seq_num, seq_pol):
        atraso = 0
        for cor in reversed(seq_pol):
            if cor == "B": break
            atraso += 1
        return ("ALTA" if atraso >= 15 else "BAIXA"), atraso

class JuizHierarquicoModificado:
    @staticmethod
    def arbitrar_sinal(no_call_ativo, motivo_nc, expectations, inclinacao_num, geometria_mercado, previsao_ia, status_inversao, historico_regras, entropia, ultima_posicao):
        if no_call_ativo: return "NO CALL", motivo_nc, "TRAVA_SEGURANCA"
        
        # Filtro de Entropia: Se o mercado estiver caótico, não opera.
        if entropia > 0.85: return "NO CALL", "Mercado em Alta Entropia (Caos)", "ENTROPIA"

        risco_ativo, tipo_inversao, justificativa_inv = status_inversao
        direcao_ia, confianca_ia = previsao_ia
        
        sinal_projetado = None
        origens = []
        regra_vencedora_id = "NENHUMA"
        
        if expectations:
            forcas = {"VERMELHO": 0.0, "PRETO": 0.0}
            for item in expectations:
                id_r = item["tipo_regra"]
                # PESO POR POSIÇÃO: O historico agora cruza regra + posição do ativador
                chave_pos = f"{id_r}_POS_{item.get('origem_idx', 0)}"
                stats = historico_regras[chave_pos]
                taxa = stats["acertos"] / max(1, stats["total"])
                
                # SOBERANIA DE CONTEXTO: Regras com melhor assertividade na posição atual ganham peso
                peso_vivo = 3.0 * (1.0 + taxa)
                forcas[item["direcao"]] += peso_vivo
                origens.append(f"{item['tipo_regra']} ({peso_vivo:.1f})")
            
            sinal_projetado = "VERMELHO" if forcas["VERMELHO"] > forcas["PRETO"] else "PRETO"
            regra_vencedora_id = "PROJECAO_ATIVA"

        if risco_ativo and tipo_inversao == "INVERSÃO":
            return ("PRETO" if "Vermelhos" in justificativa_inv else "VERMELHO"), "Intercepção de Exaustão", "INVERSION_REAL"

        if sinal_projetado: return sinal_projetado, f"Dominância: {' + '.join(origens)}", regra_vencedora_id
        
        return "PRETO", "Consenso Operacional", "CONSENSO"

class MotorV1Completo:
    def __init__(self, lista_dados_xls):
        self.seq = SequenciaOperacional(lista_dados_xls)
        self.ia = IAPreditivaV1(lista_dados_xls[:150], lista_dados_xls[-150:])
        self.historico_regras = defaultdict(lambda: {"acertos": 1, "total": 1})

    def processar_auditoria(self):
        idx, memorias, stats = 0, [], {"G0": 0, "G1": 0, "G2": 0, "FALHA": 0, "NO CALL": 0}
        while idx + 12 < self.seq.total:
            sub_num = self.seq.numerica[idx : idx + 12]
            sub_pol = self.seq.polaridades[idx : idx + 12]
            
            # Cálculo dos novos filtros
            entropia = AnalisadorContextoAvancado.medir_entropia_janela(sub_num)
            geometria = AnalisadorContextoAvancado.mapear_padroes_geometria(sub_pol)
            status_inv = AnalisadorContextoAvancado.detectar_chance_inversao(sub_pol)
            nc_ativo, motivo_nc = MotorNoCall.checar_no_call(sub_num, sub_pol)
            expectativas = MotorContagensProjetivas.mapear_janela(sub_num, sub_pol, geometria)
            
            previsao_ia = self.ia.predizer_proxima_casa(sub_num, sub_pol)
            
            expectativa_final, justificativa, regra_id = JuizHierarquicoModificado.arbitrar_sinal(
                nc_ativo, motivo_nc, expectativas, AnalisadorContextoAvancado.calcular_numerologia_pos_numero(sub_num[-1], self.seq.numerica, self.seq.polaridades), 
                geometria, previsao_ia, status_inv, self.historico_regras, entropia, idx
            )

            # (Loop de resultados e salto mantidos como no seu original)
            # ... [seu código de classificação G0/G1/Falha] ...

            # APRENDIZADO POR POSIÇÃO (Evolução significativa)
            if regra_id != "NENHUMA" and regra_id != "SISTEMA_TRAVADO":
                for item in expectativas:
                    chave = f"{item['tipo_regra']}_POS_{item['origem_idx']}"
                    self.historico_regras[chave]["total"] += 1
                    if classificacao in ["G0", "G1"]: self.historico_regras[chave]["acertos"] += 1
            
            idx += 12 + salto
        return self._gerar_relatorio_texto(memorias, stats, len(janelas_auditadas))
