import os
import pandas as pd

class SequenciaOperacional:
    def __init__(self, lista_resultados):
        self.cronologia = lista_resultados
        self.numerica = [int(r['numero']) for r in self.cronologia]
        self.polaridades = [str(r['cor']).upper() for r in self.cronologia]
        self.total = len(self.numerica)

class MotorNoCall:
    @staticmethod
    def checar_no_call(sub_num, sub_pol):
        for idx in [8, 9, 10, 11]:
            if sub_num[idx] == 2:
                return True, "Volume 5: Número 2 Crítico no Fechamento"
        for idx in [5, 8, 9, 10, 11]:
            if sub_num[idx] == 6:
                return True, "Volume 5: Número 6 Crítico Ativo"
            if sub_pol[idx] == "B":
                return True, "Volume 13: Ruptura Estrutural por Branco Posicional"
        for i, j in [(10, 11), (9, 10), (8, 9), (7, 8)]:
            if sub_num[i] == sub_num[j]:
                return True, f"Volume 2: Dupla do número {sub_num[i]} em Adjacência Crítica"
        return False, "Evento Neutro Operacional"

class MotorContagensProjetivas:
    @staticmethod
    def mapear_janela(sub_num, sub_pol, geometria_mercado):
        expectativas = []
        REGRAS_PROJECAO = {1: 1, 2: 6, 3: 6, 4: 3, 5: 4, 6: 5, 7: 7}

        for i in range(12):
            num_atual = sub_num[i]
            if num_atual in REGRAS_PROJECAO:
                if i + REGRAS_PROJECAO[num_atual] == 11:
                    if num_atual in [2, 4] and (11 in sub_num[i+1:]):
                        continue
                    if 0 in sub_num[i:12]:
                        continue
                    if num_atual == 6:
                        direcao_sinal = "PRETO" if "VERMELHO" not in geometria_mercado else "VERMELHO"
                    else:
                        direcao_sinal = "PRETO" if "PRETO" in geometria_mercado else "VERMELHO"
                    
                    expectativas.append({
                        "direcao": direcao_sinal,
                        "origem": f"Volume 3: Ativador {num_atual} na {i+1}ª casa"
                    })

        if sub_num[11] == 10:
            expectativas.append({"direcao": "PRETO", "origem": "Volume 12: Cap 2 - Resíduo do 10"})
        elif sub_num[10] == 5 and sub_num[11] == 10:
            expectativas.append({"direcao": "PRETO", "origem": "Volume 12: Cap 4 - Acoplamento 5-10"})
        if sub_num[11] == 4 and sub_pol[10] == "P":
            expectativas.append({"direcao": "PRETO", "origem": "Volume 2: Cap 3 - Retenção do 4 sob Base Preta"})

        return expectativas

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

        if pct_v >= 58.0: return "VERMELHO", pct_v
        if pct_p >= 58.0: return "PRETO", pct_p
        return "NEUTRO", max(pct_v, pct_p)

    @staticmethod
    def mapear_padroes_geometria(sub_pol):
        texto_sub_pol = "".join(sub_pol)
        if "VVVV" in texto_sub_pol: return "SATURAÇÃO ESTRUTURAL (V) DETECTADA NA JANELA"
        if "PPPP" in texto_sub_pol: return "SATURAÇÃO ESTRUTURAL (P) DETECTADA NA JANELA"
        if "VPVPVP" in texto_sub_pol or "PVPVPV" in texto_sub_pol: return "PADRÃO XADREZ LONGO DETECTADO (ALTA CRITICIDADE)"
        if "VPVP" in texto_sub_pol or "PVPV" in texto_sub_pol: return "PADRÃO XADREZ ATIVO NA SEQUÊNCIA"
        if "VPPV" in texto_sub_pol or "PVVP" in texto_sub_pol: return "PADRÃO ESPELHO CONFIGURADO NA SEQUÊNCIA"
        if "VVPP" in texto_sub_pol or "PPVV" in texto_sub_pol: return "RETENÇÃO EM BLOCOS COERENTE DETECTADA"
        return "ESTÁVEL"

    @staticmethod
    def preditor_estatistico_branco(num_fechamento, sequencia_num, sequencia_pol):
        if not sequencia_pol: return "BAIXA", 0
        atraso_atual = 0
        encontrou_branco = False
        for cor in reversed(sequencia_pol):
            if cor == "B":
                encontrou_branco = True
                break
            atraso_atual += 1
        if not encontrou_branco: atraso_atual = len(sequencia_pol)

        vezes_numero_apareceu, vezes_chamou_branco = 0, 0
        for i in range(len(sequencia_num) - 1):
            if sequencia_num[i] == num_fechamento:
                vezes_numero_apareceu += 1
                horizonte_proximo = sequencia_pol[i+1 : min(i+3, len(sequencia_pol))]
                if "B" in horizonte_proximo: vezes_chamou_branco += 1

        taxa_atracao = 0.0
        if int(vezes_numero_apareceu) > 0:
            taxa_atracao = (vezes_chamou_branco / vezes_numero_apareceu) * 100

        if atraso_atual >= 15 or taxa_atracao >= 20.0: chance = "ALTA"
        elif atraso_atual >= 8 or taxa_atracao >= 10.0: chance = "MÉDIA"
        else: chance = "BAIXA"
        return chance, atraso_atual

class JuizHierarquicoModificado:
    @staticmethod
    def arbitrar_sinal(no_call_ativo, motivo_nc, expectativas, inclinacao_num):
        if no_call_ativo: return "NO CALL", motivo_nc
        if not expectativas: return "NO CALL", "Ausência de Diretriz Ativa"
        direcao_inclinacao, porc = inclinacao_num
        direcoes_projetadas = list(set([e["direcao"] for e in expectativas]))

        if len(direcoes_projetadas) > 1:
            if direcao_inclinacao in direcoes_projetadas and porc >= 65.0:
                return direcao_inclinacao, f"Volume 18: Conflito resolvido por Inclinação ({porc:.1f}%)"
            return "NO CALL", "Volume 18: Conflito Hierárquico Não Resolvido"
        return direcoes_projetadas[0], expectativas[0]["origem"]

class MotorV1Completo:
    def __init__(self, lista_dados_xls):
        self.seq = SequenciaOperacional(lista_dados_xls)

    def processar_auditoria(self):
        idx = 0
        memorias_calculo = []
        janelas_auditadas = []
        historico_recencia = []
        stats = {"G0": 0, "G1": 0, "G2": 0, "FALHA": 0, "NO CALL": 0}

        while idx + 12 < self.seq.total:
            sub_num = self.seq.numerica[idx : idx + 12]
            sub_pol = self.seq.polaridades[idx : idx + 12]

            geometria = AnalisadorContextoAvancado.mapear_padroes_geometria(sub_pol)
            nc_ativo, motivo_nc = MotorNoCall.checar_no_call(sub_num, sub_pol)
            expectativas = MotorContagensProjetivas.mapear_janela(sub_num, sub_pol, geometria)

            num_fechamento = sub_num[-1]
            inclinacao_num = AnalisadorContextoAvancado.calcular_numerologia_pos_numero(num_fechamento, self.seq.numerica, self.seq.polaridades)
            expectativa_preliminar, justificativa = JuizHierarquicoModificado.arbitrar_sinal(nc_ativo, motivo_nc, expectativas, inclinacao_num)

            if len(historico_recencia) > 0:
                falhas_recentes = historico_recencia.count("FALHA")
                taxa_falha_momento = (falhas_recentes / len(historico_recencia)) * 100
                if taxa_falha_momento >= 40.0 and expectativa_preliminar != "NO CALL":
                    expectativa_final = "NO CALL"
                    justificativa = f"Volume 21: Bloqueio por Degradação ({taxa_falha_momento:.1f}%)"
                else: expectativa_final = expectativa_preliminar
            else: expectativa_final = expectativa_preliminar

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
                for g_idx, cor_real in enumerate(correcoes_reais):
                    if cor_real == expectativa_final:
                        classificacao = f"G{g_idx}"
                        salto = g_idx + 1
                        break
                if classificacao == "FALHA": salto = 3
                if horizonte_max == 3:
                    stats[classificacao] += 1
                    resultado_movel = "FALHA" if classificacao == "FALHA" else "ACERTO"
                    historico_recencia.append(resultado_movel)
                    if len(historico_recencia) > 5: historico_recencia.pop(0)

            log_linha = f"Janela {len(janelas_auditadas) + 1}: {sub_num} -> Expectativa: {expectativa_final} -> Correção: {classificacao}"
            memorias_calculo.append(log_linha)
            janelas_auditadas.append(classificacao)
            idx += 12 + salto

        return self._gerar_relatorio_texto(memorias_calculo, stats, len(janelas_auditadas))

    def _gerar_relatorio_texto(self, memorias, stats, qtd_janelas):
        total_com_sinal = sum([stats["G0"], stats["G1"], stats["G2"], stats["FALHA"]])
        denominador = total_com_sinal if total_com_sinal > 0 else 1
        denominador_nc = qtd_janelas if qtd_janelas > 0 else 1

        p_g0, p_g1, p_g2, p_fa = (stats["G0"]/denominador)*100, (stats["G1"]/denominador)*100, (stats["G2"]/denominador)*100, (stats["FALHA"]/denominador)*100
        p_nc = (stats["NO CALL"]/denominador_nc)*100
        total_v, total_p, total_b = self.seq.polaridades.count("V"), self.seq.polaridades.count("P"), self.seq.polaridades.count("B")

        degradacao = "INEXISTENTE" if p_fa < 15 else "FORTE"
        recuperacao = "FORTE" if p_g0 > 50 else "INEXISTENTE"
        chance_branco = "ALTA" if total_b > (self.seq.total * 0.07) else "BAIXA"
        estado_mercado = "ESTÁVEL" if p_fa < 20 else "INSTABILIDADE"

        output = "[MEMÓRIA DE CÁLCULO DAS JANELAS]\n" + "\n".join(memorias) + "\n\n"
        output += "[RESULTADO FINAL ESTATÍSTICO]\n"
        output += f"CRONOLOGIA VALIDADA: {self.seq.total}\n"
        output += "CONSOLIDAÇÃO DAS JANELAS:\n"
        output += f" - Janelas Extraídas (Saltos): {qtd_janelas}\n"
        output += f" - Taxa G0: {stats['G0']} Ocorrências ({p_g0:.2f}%)\n"
        output += f" - Taxa G1: {stats['G1']} Ocorrências ({p_g1:.2f}%)\n"
        output += f" - Taxa G2: {stats['G2']} Ocorrências ({p_g2:.2f}%)\n"
        output += f" - Taxa de Falha: {stats['FALHA']} Ocorrências ({p_fa:.2f}%)\n"
        output += f" - Taxa de NO CALL: {stats['NO CALL']} Ocorrências ({p_nc:.2f}%)\n"
        output += f"MACROANÁLISE: Fluxo linear com {total_v}V, {total_p}P e {total_b}B mapeados.\n"
        output += "RECÊNCIA EVOLUTIVA: Avaliação sequencial calculada estritamente via Regra de Reinício em Saltos.\n"
        output += "CONTROLADOR CONSOLIDADO: Ativadores de Contagem Projetiva de Volume 3.\n"
        output += "RETARDADOR CONSOLIDADO: Filtros posicionais do Apêndice A em atividade.\n"
        output += f"DEGRADAÇÃO: {degradacao}\n"
        output += f"RECUPERAÇÃO: {recuperacao}\n"
        output += f"CHANCE DE BRANCO: {chance_branco}\n"
        output += "EXPECTATIVA OBSERVACIONAL: NEUTRA\n"
        output += f"ESTADO ATUAL DO MERCADO: {estado_mercado}\n"
        return output

class LeitorXLS:
    def __init__(self, caminho_arquivo):
        self.caminho = caminho_arquivo

    def ler_e_validar(self):
        if not os.path.exists(self.caminho): 
            return None
        try:
            # Tenta ler como Excel, se falhar (como no iPad), lê como CSV
            try:
                df = pd.read_excel(self.caminho)
            except:
                df = pd.read_csv(self.caminho)
                
            # Limpa espaços em branco e mete os títulos em minúsculas
            df.columns = [str(col).strip().lower() for col in df.columns]
            
            # Mapeia 'val' para 'numero' e 'color' para 'cor' (Padrão exato do teu ficheiro)
            mapeamento_colunas = {
                'val': 'numero', 
                'color': 'cor',
                'roll': 'numero',
                'resultado': 'numero'
            }
            df = df.rename(columns=mapeamento_colunas)
            
            # Validação estrita: se não achar as colunas, o disjuntor trava
            if 'numero' not in df.columns or 'cor' not in df.columns:
                return None
                
            # Inverte o arquivo para ordem cronológica (do mais antigo para o mais recente)
            df_cronologico = df.iloc[::-1].reset_index(drop=True)
            if len(df_cronologico) < 15: 
                return None
                
            dados_limpos = []
            for _, l in df_cronologico.iterrows():
                try:
                    num_val = int(l["numero"])
                    cor_original = str(l["cor"]).strip().lower()
                    
                    # Tradução inteligente baseada no teu ficheiro:
                    # Se a cor for '1' ou 'red' -> Vermelho (V)
                    # Se a cor for '2' ou 'black' -> Preto (P)
                    # Se a cor for '0' ou 'white' -> Branco (B)
                    if cor_original in ['1', 'red', 'vermelho', 'v']:
                        cor_final = 'V'
                    elif cor_original in ['2', 'black', 'preto', 'p']:
                        cor_final = 'P'
                    elif cor_original in ['0', 'white', 'branco', 'b']:
                        cor_final = 'B'
                    else:
                        # Segurança baseada estritamente no número do giro
                        if num_val == 0: cor_final = 'B'
                        elif 1 <= num_val <= 7: cor_final = 'V'
                        else: cor_final = 'P'
                        
                    dados_limpos.append({
                        "numero": num_val,
                        "cor": cor_final
                    })
                except:
                    continue
                    
            if not dados_limpos:
                return None
                
            return dados_limpos
        except: 
            return None
