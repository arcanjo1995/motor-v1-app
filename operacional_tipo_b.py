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
        # Correção estrita conforme o manual: checa os últimos índices (fechamento da janela de 12 pedras)
        # Se houver duplicidade de qualquer número nas últimas casas em adjacência ativa
        if sub_num[10] == sub_num[11]:
            return True, f"Volume 2: Dupla do número {sub_num[11]} em Adjacência Crítica"
        if sub_num[9] == sub_num[10]:
            return True, f"Volume 2: Dupla do número {sub_num[10]} em Adjacência Crítica"
            
        # O número 2 e 6 só travam se estiverem estritamente nas 2 últimas posições de fechamento
        if sub_num[11] in [2, 6] or sub_num[10] in [2, 6]:
            return True, "Volume 5: Número Crítico (2 ou 6) Ativo no Fechamento"
            
        # Volume 13: Branco nas duas últimas posições impede a leitura de tendência imediata
        if sub_pol[11] == "B" or sub_pol[10] == "B":
            return True, "Volume 13: Ruptura Estrutural por Branco Posicional"
            
        return False, "Evento Neutro Operacional"

class MotorContagensProjetivas:
    @staticmethod
    def mapear_janela(sub_num, sub_pol, geometria_mercado):
        expectativas = []
        # Regras de projeção de casas do Volume 3
        REGRAS_PROJECAO = {1: 1, 2: 6, 3: 6, 4: 3, 5: 4, 6: 5, 7: 7}

        for i in range(12):
            num_atual = sub_num[i]
            if num_atual in REGRAS_PROJECAO:
                passo = REGRAS_PROJECAO[num_atual]
                # Se o passo do ativador crava exatamente na casa de projeção (última pedra da janela)
                if i + passo == 11:
                    if 0 in sub_num[i:12]: # Se houver branco no meio do caminho, aborta a projeção linear
                        continue
                    
                    if num_atual == 6:
                        direcao_sinal = "PRETO" if "VERMELHO" not in geometria_mercado else "VERMELHO"
                    else:
                        direcao_sinal = "PRETO" if "PRETO" in geometria_mercado else "VERMELHO"
                    
                    expectativas.append({
                        "direcao": direcao_sinal,
                        "origem": f"Volume 3: Ativador {num_atual} na {i+1}ª casa"
                    })

        # Gatilhos Residuais de Fechamento (Últimas pedras)
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

        if pct_v >= 55.0: return "VERMELHO", pct_v
        if pct_p >= 55.0: return "PRETO", pct_p
        return "NEUTRO", max(pct_v, pct_p)

    @staticmethod
    def mapear_padroes_geometria(sub_pol):
        texto_sub_pol = "".join(sub_pol)
        if "VVVV" in texto_sub_pol: return "SATURAÇÃO ESTRUTURAL (V)"
        if "PPPP" in texto_sub_pol: return "SATURAÇÃO ESTRUTURAL (P)"
        if "VPVPVP" in texto_sub_pol or "PVPVPV" in texto_sub_pol: return "XADREZ LONGO"
        if "VPVP" in texto_sub_pol or "PVPV" in texto_sub_pol: return "XADREZ ATIVO"
        return "ESTÁVEL"

    @staticmethod
    def preditor_estatistico_branco(num_fechamento, sequencia_num, sequencia_pol):
        if not sequencia_pol: return "BAIXA", 0
        atraso_atual = 0
        for cor in reversed(sequencia_pol):
            if cor == "B": break
            atraso_atual += 1

        vezes_numero_apareceu, vezes_chamou_branco = 0, 0
        for i in range(len(sequencia_num) - 1):
            if sequencia_num[i] == num_fechamento:
                vezes_numero_apareceu += 1
                horizonte_proximo = sequencia_pol[i+1 : min(i+4, len(sequencia_pol))]
                if "B" in horizonte_proximo: vezes_chamou_branco += 1

        taxa_atracao = (vezes_chamou_branco / vezes_numero_apareceu) * 100 if vezes_numero_apareceu > 0 else 0.0
        chance = "ALTA" if atraso_atual >= 15 or taxa_atracao >= 18.0 else ("MÉDIA" if atraso_atual >= 8 else "BAIXA")
        return chance, atraso_atual

class JuizHierarquicoModificado:
    @staticmethod
    def arbitrar_sinal(no_call_ativo, motivo_nc, expectativas, inclinacao_num):
        if no_call_ativo: return "NO CALL", motivo_nc
        if not expectativas: return "NO CALL", "Ausência de Diretriz Ativa de Volume 3"
        
        direcao_inclinacao, porc = inclinacao_num
        direcoes_projetadas = list(set([e["direcao"] for e in expectativas]))

        if len(direcoes_projetadas) > 1:
            if direcao_inclinacao in direcoes_projetadas and porc >= 55.0:
                return direcao_inclinacao, f"Volume 18: Conflito resolvido por Inclinação Histórica ({porc:.1f}%)"
            return "NO CALL", "Volume 18: Conflito Hierárquico Sem Consenso"
        return direcoes_projetadas[0], expectativas[0]["origem"]

class MotorV1Completo:
    def __init__(self, lista_dados_xls):
        self.seq = SequenciaOperacional(lista_dados_xls)

    def processar_auditoria(self):
        idx = 0
        memorias_calculo = []
        janelas_auditadas = []
        stats = {"G0": 0, "G1": 0, "G2": 0, "FALHA": 0, "NO CALL": 0}

        while idx + 12 < self.seq.total:
            sub_num = self.seq.numerica[idx : idx + 12]
            sub_pol = self.seq.polaridades[idx : idx + 12]

            geometria = AnalisadorContextoAvancado.mapear_padroes_geometria(sub_pol)
            nc_ativo, motivo_nc = MotorNoCall.checar_no_call(sub_num, sub_pol)
            expectativas = MotorContagensProjetivas.mapear_janela(sub_num, sub_pol, geometria)

            num_fechamento = sub_num[-1]
            inclinacao_num = AnalisadorContextoAvancado.calcular_numerologia_pos_numero(num_fechamento, self.seq.numerica, self.seq.polaridades)
            
            # CORREÇÃO DA LINHA DO ERRO TRACEBACK: Passagem correta dos parâmetros para o Juiz
            expectativa_final, justificativa = JuizHierarquicoModificado.arbitrar_sinal(nc_ativo, motivo_nc, expectativas, inclinacao_num)

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
                letra_esperada = "V" if expectativa_final == "VERMELHO" else "P"
                for g_idx, cor_real in enumerate(correcoes_reais):
                    if cor_real == letra_esperada:
                        classificacao = f"G{g_idx}"
                        salto = g_idx + 1
                        break
                if classificacao == "FALHA": 
                    salto = 3
                stats[classificacao] += 1

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

        estado_mercado = "ESTÁVEL" if p_fa < 22 else "INSTABILIDADE"

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
        output += f"DEGRADAÇÃO: {'FORTE' if p_fa >= 25 else 'INEXISTENTE'}\n"
        output += f"RECUPERAÇÃO: {'FORTE' if p_g0 >= 45 else 'INEXISTENTE'}\n"
        output += f"ESTADO ATUAL DO MERCADO: {estado_mercado}\n"
        return output

class LeitorXLS:
    def __init__(self, caminho_arquivo):
        self.caminho = caminho_arquivo

    def ler_e_validar(self):
        if not os.path.exists(self.caminho): return None
        try:
            try: df = pd.read_excel(self.caminho)
            except: df = pd.read_csv(self.caminho)
                
            df.columns = [str(col).strip().lower() for col in df.columns]
            
            mapeamento_colunas = {
                'val': 'numero', 'value': 'numero', 'num': 'numero', 'number': 'numero',
                'resultado': 'numero', 'roll': 'numero', 'giro': 'numero', 'spin': 'numero',
                'color': 'cor', 'cor': 'cor', 'result': 'cor'
            }
            df = df.rename(columns=mapeamento_colunas)
            
            colunas_atuais = df.columns.tolist()
            col_numero, col_cor = None, None
            
            for col in colunas_atuais:
                col_lower = str(col).lower().strip()
                if any(x in col_lower for x in ['val', 'num', 'number', 'roll', 'giro', 'spin']) and not any(x in col_lower for x in ['color', 'cor']):
                    col_numero = col
                if any(x in col_lower for x in ['color', 'cor']):
                    col_cor = col
            
            if col_numero is None and len(colunas_atuais) >= 1: col_numero = colunas_atuais[0]
            if col_cor is None and len(colunas_atuais) >= 2: col_cor = colunas_atuais[1]
            if col_numero is None or col_cor is None: return None
            
            df = df.rename(columns={col_numero: 'numero', col_cor: 'cor'})
            df_cronologico = df.iloc[::-1].reset_index(drop=True)
            if len(df_cronologico) < 15: return None
                
            LEGENDA_BRANCO = [0]
            LEGENDA_VERMELHO = [1, 2, 3, 4, 5, 6, 7]
            LEGENDA_PRETO = [8, 9, 10, 11, 12, 13, 14]
            
            dados_limpos = []
            for _, l in df_cronologico.iterrows():
                try:
                    num_val = int(l["numero"])
                    if num_val in LEGENDA_BRANCO: cor_final = 'B'
                    elif num_val in LEGENDA_VERMELHO: cor_final = 'V'
                    elif num_val in LEGENDA_PRETO: cor_final = 'P'
                    else: continue
                        
                    dados_limpos.append({"numero": num_val, "cor": cor_final})
                except: continue
            return dados_limpos if dados_limpos else None
        except: return None
