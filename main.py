import os
import pandas as pd
from collections import defaultdict
import pickle
import json
from datetime import datetime
import time

NOME_BASE_DEFINITIVA = "resultados_blaze.xlsx"

# ============================================================
# Função de Log JSON
# ============================================================
def salvar_log_json(dados, nome_arquivo="logs/sinais_tipo_b.jsonl"):
    os.makedirs("logs", exist_ok=True)
    dados["timestamp"] = datetime.now().isoformat()
    with open(nome_arquivo, "a", encoding="utf-8") as f:
        f.write(json.dumps(dados, ensure_ascii=False) + "\n")


# ============================================================
# Funções de Persistência e Integração (VERSÃO ROBUSTA)
# ============================================================
def salvar_modelo_longo_prazo(ia, caminho="modelo_longo_prazo.pkl"):
    try:
        pasta = os.path.dirname(caminho)
        if pasta:
            os.makedirs(pasta, exist_ok=True)

        for tentativa in range(3):
            try:
                with open(caminho, "wb") as f:
                    pickle.dump(ia, f)
                return True
            except Exception as e:
                print(f"Tentativa {tentativa + 1} de salvar o modelo falhou: {e}")
                time.sleep(0.5)
        return False
    except Exception as e:
        print(f"Erro crítico ao salvar modelo: {e}")
        return False

def carregar_modelo_longo_prazo(caminho="modelo_longo_prazo.pkl"):
    if os.path.exists(caminho):
        try:
            with open(caminho, "rb") as f:
                return pickle.load(f)
        except:
            return None
    return None


def analisar_regime_recencia(dados_recencia):
    if not dados_recencia or len(dados_recencia) < 20:
        return {
            "viés_atual": "INDEFINIDO",
            "modo_dominante": "NEUTRO",
            "xadrez_frequencia": 0.0,
            "streak_medio": 0,
            "confianca_regime": 0
        }

    cores = [d['cor'] for d in dados_recencia]
    total = len(cores)
    v = cores.count('V')
    p = cores.count('P')

    pct_v = (v / total) * 100
    pct_p = (p / total) * 100

    if pct_v >= 55:
        viés = "VERMELHO"
    elif pct_p >= 55:
        viés = "PRETO"
    else:
        viés = "EQUILIBRADO"

    alternancias = sum(1 for i in range(1, total) if cores[i] != cores[i-1] and cores[i] != 'B' and cores[i-1] != 'B')
    xadrez_freq = (alternancias / (total - 1)) * 100 if total > 1 else 0

    streaks = []
    atual = 1
    for i in range(1, total):
        if cores[i] == cores[i-1] and cores[i] != 'B':
            atual += 1
        else:
            if atual >= 2:
                streaks.append(atual)
            atual = 1
    streak_medio = sum(streaks) / len(streaks) if streaks else 0

    if xadrez_freq >= 65:
        modo = "XADREZ_DOMINANTE"
    elif streak_medio >= 3.5:
        modo = "STREAK_DOMINANTE"
    else:
        modo = "MISTO"

    confianca = min(85, int(abs(pct_v - 50) + abs(pct_p - 50)))

    return {
        "viés_atual": viés,
        "modo_dominante": modo,
        "xadrez_frequencia": round(xadrez_freq, 1),
        "streak_medio": round(streak_medio, 1),
        "confianca_regime": confianca,
        "pct_vermelho_recencia": round(pct_v, 1),
        "pct_preto_recencia": round(pct_p, 1)
    }


def integrar_recencia_no_modelo(dados_recencia, multiplicador=5):
    ia = carregar_modelo_longo_prazo()
    if ia is None:
        ia = IAPreditivaV1([], dados_recencia)
    else:
        ia.injetar_aprendizado_imediato(dados_recencia, multiplicador_peso=multiplicador)

    ia.analise_recencia = ia.analisar_comportamento_pos_numero_recencia(dados_recencia)
    ia.regime_recencia = analisar_regime_recencia(dados_recencia)
    salvar_modelo_longo_prazo(ia)
    return ia


def adicionar_a_base_longo_prazo(novos_dados):
    if not novos_dados:
        return {"sucesso": False, "mensagem": "Nenhum dado novo foi fornecido."}

    base_existente = []
    if os.path.exists(NOME_BASE_DEFINITIVA):
        try:
            base_existente = LeitorXLS(NOME_BASE_DEFINITIVA).ler_e_validar() or []
        except:
            return {"sucesso": False, "mensagem": "Não foi possível ler a base antiga."}

    dados_combinados = base_existente + novos_dados

    if os.path.exists(NOME_BASE_DEFINITIVA):
        try:
            backup_name = NOME_BASE_DEFINITIVA.replace(".xlsx", f"_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
            os.rename(NOME_BASE_DEFINITIVA, backup_name)
        except:
            pass

    try:
        df = pd.DataFrame([{"numero": d["numero"], "cor": d["cor"]} for d in dados_combinados])
        df.to_excel(NOME_BASE_DEFINITIVA, index=False)
    except Exception as e:
        return {"sucesso": False, "mensagem": f"Erro ao salvar o arquivo: {e}"}

    return treinar_base_longo_prazo_com_janelas(dados_combinados)


def reforcar_aprendizado_tipo_d(ia):
    for padrao, qtd in ia.controladores_fortes.items():
        if qtd >= 8:
            ia.padroes_fortes.append({"tipo": "CONTROLADOR_MUITO_FORTE", "padrao": padrao, "peso": qtd * 2})
    ia.padroes_fortes = sorted(ia.padroes_fortes, key=lambda x: x.get("peso", 0), reverse=True)[:30]


def treinar_base_longo_prazo_com_janelas(dados_completos):
    if not dados_completos or len(dados_completos) < 30:
        return {"sucesso": False, "mensagem": "Base muito pequena para treinamento profundo."}

    motor = MotorV1Completo(dados_completos)
    motor.processar_auditoria()
    reforcar_aprendizado_tipo_d(motor.ia)

    motor.ia.mapear_padroes_avancados(dados_completos)

    analise_numeros = motor.ia.analisar_comportamento_pos_numero()

    seen = set()
    unique_patterns = []
    for p in motor.ia.memoria_padroes_vencedores:
        try:
            key = json.dumps(p, sort_keys=True)
            if key not in seen:
                seen.add(key)
                unique_patterns.append(p)
        except:
            unique_patterns.append(p)

    motor.ia.memoria_padroes_vencedores = unique_patterns

    # Tenta salvar até 3 vezes
    sucesso_salvar = False
    for _ in range(3):
        sucesso_salvar = salvar_modelo_longo_prazo(motor.ia)
        if sucesso_salvar:
            break
        time.sleep(0.5)

    stats = getattr(motor, 'stats', {"G0": 0, "G1": 0, "G2": 0, "FALHA": 0, "NO CALL": 0})
    total_janelas = sum(stats.values()) if stats else 0

    regras_boas = 0
    for regra, dados in motor.historico_regras.items():
        if dados["total"] >= 5 and (dados["acertos"] / dados["total"]) >= 0.55:
            regras_boas += 1

    taxa_g0_g1 = ((stats.get("G0", 0) + stats.get("G1", 0)) / total_janelas * 100) if total_janelas > 0 else 0

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
        "analise_comportamento_numeros": analise_numeros,
        "mensagem": "Treinamento profundo concluído com sucesso."
    }


# ============================================================
# MotorAnalise
# ============================================================
class MotorAnalise:
    @staticmethod
    def analisar_janela(sub_num, sub_pol, ia_modelo, base_longa=None):
        resultado = {
            "camadas": [],
            "no_call": None,
            "geometria": None,
            "regras_posicionais": [],
            "contexto_avancado": {},
            "ia": {},
            "contexto_reversao": {},
            "controlador_retardador": {}
        }

        nc_ativo, motivo_nc = MotorNoCall.checar_no_call(sub_num, sub_pol)
        resultado["no_call"] = {"ativo": nc_ativo, "motivo": motivo_nc}
        resultado["camadas"].append({
            "camada": 1, "nome": "Segurança (NO CALL)",
            "resultado": f"Ativo={nc_ativo}", "detalhe": motivo_nc,
            "impacto": "BLOQUEIO" if nc_ativo else "APROVADO"
        })

        if nc_ativo:
            return resultado

        geometria = AnalisadorContextoAvancado.mapear_padroes_geometria(sub_pol)
        resultado["geometria"] = geometria
        resultado["camadas"].append({
            "camada": 2, "nome": "Geometria",
            "resultado": geometria, "detalhe": "Padrão geométrico detectado",
            "impacto": "FORTE" if geometria in ["CICLO_FECHADO_VPPV", "CICLO_FECHADO_PVVP"] else "NEUTRO"
        })

        expectativas = MotorContagensProjetivas.mapear_janela(sub_num, sub_pol, geometria)
        resultado["regras_posicionais"] = expectativas
        resultado["camadas"].append({
            "camada": 3, "nome": "Regras Posicionais (Volume 12)",
            "resultado": f"{len(expectativas)} regras ativas",
            "detalhe": [e["tipo_regra"] for e in expectativas] if expectativas else "Nenhuma",
            "impacto": "ALTO" if expectativas else "BAIXO"
        })

        modo_mercado = AnalisadorContextoAvancado.detectar_modo_mercado(sub_pol)
        resultado["contexto_avancado"] = {"modo_mercado": modo_mercado}
        resultado["camadas"].append({
            "camada": 4, "nome": "Contexto Avançado",
            "resultado": f"Modo: {modo_mercado}", "detalhe": "Detecção de regime de mercado", "impacto": "MÉDIO"
        })

        contexto_para_ia = {
            "geometria": geometria,
            "regras_posicionais": expectativas,
            "controlador_retardador": {},
            "contexto_avancado": resultado["contexto_avancado"]
        }

        direcao_ia, conf_ia, raciocinio_ia = ia_modelo.predizer_proxima_casa(sub_num, sub_pol, contexto_para_ia)

        resultado["ia"] = {
            "direcao": direcao_ia,
            "confianca": conf_ia,
            "raciocinio": raciocinio_ia
        }
        resultado["camadas"].append({
            "camada": 5, "nome": "IA Probabilística",
            "resultado": f"{direcao_ia} ({conf_ia}%)",
            "detalhe": raciocinio_ia,
            "impacto": "ALTO" if conf_ia >= 52 else "MÉDIO"
        })

        streak, xadrez_len, xadrez_quebrou, exaustao = MotorAnalise._calcular_contexto_reversao(sub_pol)
        resultado["contexto_reversao"] = {
            "streak": streak, "xadrez_len": xadrez_len,
            "xadrez_quebrou": xadrez_quebrou, "exaustao": exaustao
        }
        resultado["camadas"].append({
            "camada": 6, "nome": "Contexto de Reversão",
            "resultado": f"Streak={streak}x | Xadrez={xadrez_len}",
            "detalhe": f"Exaustão={exaustao}",
            "impacto": "ALTO" if exaustao else "BAIXO"
        })

        ctrl_ret = MotorAnalise._detectar_controlador_retardador(
            sub_num, sub_pol, expectativas, geometria, modo_mercado
        )
        resultado["controlador_retardador"] = ctrl_ret
        resultado["camadas"].append({
            "camada": 7, "nome": "Controlador vs Retardador",
            "resultado": ctrl_ret["dominancia"],
            "detalhe": f"Controladores: {ctrl_ret['controladores']} | Retardadores: {ctrl_ret['retardadores']}",
            "impacto": "ALTO"
        })

        return resultado

    @staticmethod
    def _calcular_contexto_reversao(sub_pol):
        streak = sum(1 for c in reversed(sub_pol) if c == sub_pol[-1])
        xadrez_len = 0
        for i in range(len(sub_pol)-1, 0, -1):
            if sub_pol[i] != sub_pol[i-1]:
                xadrez_len += 1
            else:
                break
        xadrez_quebrou = (sub_pol[-1] == sub_pol[-2]) if len(sub_pol) >= 2 else False
        exaustao = (streak >= 5) or (xadrez_len >= 5 and xadrez_quebrou)
        return streak, xadrez_len, xadrez_quebrou, exaustao

    @staticmethod
    def _detectar_controlador_retardador(sub_num, sub_pol, expectativas, geometria, modo_mercado):
        controladores = []
        retardadores = []

        if geometria in ["CICLO_FECHADO_VPPV", "CICLO_FECHADO_PVVP"]:
            controladores.append("Geometria forte")
        if expectativas:
            controladores.append("Regras posicionais ativas")
        if modo_mercado == "CHUVA":
            retardadores.append("Alta alternância (modo Chuva)")

        if len(controladores) > len(retardadores):
            dominancia = "CONTROLADOR"
        elif len(retardadores) > len(controladores):
            dominancia = "RETARDADOR"
        else:
            dominancia = "NEUTRO"

        return {
            "controladores": controladores,
            "retardadores": retardadores,
            "dominancia": dominancia
        }


# ============================================================
# IAPreditivaV1 (COMPLETO)
# ============================================================
class IAPreditivaV1:
    def __init__(self, dados_longo_prazo, dados_recencia=None):
        self.dados_longo = dados_longo_prazo
        self.dados_recencia = dados_recencia if dados_recencia else []
        self.modelo_transicao = defaultdict(list)
        self.modelo_numerico = defaultdict(list)

        self.unidade_analise = {}
        for n in range(15):
            self.unidade_analise[n] = {
                "ocorrencias": 0, "V": 0, "P": 0, "B": 0,
                "freq_v": 0.0, "freq_p": 0.0, "freq_b": 0.0,
                "estabilidade": "NEUTRO", "saturacao": "NORMAL",
                "enfraquecimento": "ESTÁVEL", "comportamento_dominante": "NEUTRO",
                "pos_numero_V": 0, "pos_numero_P": 0, "pos_numero_B": 0,
                "pos_numero_freq_v": 0.0, "pos_numero_freq_p": 0.0, "pos_numero_freq_b": 0.0,
                "comportamento_pos_numero": "NEUTRO", "retencao_media": 0,
                "ultimas_cores": []
            }

        self.xadrez_stats = {"quebras": 0, "continuacoes": 0, "numeros_quebradores": defaultdict(int)}
        self.streak_breaker_stats = {"V": defaultdict(int), "P": defaultdict(int)}
        self.color_ngrams = {1: defaultdict(int), 2: defaultdict(int), 3: defaultdict(int)}

        self.padroes_xadrez_detalhado = defaultdict(lambda: {
            "total": 0, "apos_V": 0, "apos_P": 0, "apos_B": 0,
            "quebradores": defaultdict(int), "g0": 0, "g1": 0
        })
        self.padroes_streak_detalhado = defaultdict(lambda: {
            "total": 0, "apos_V": 0, "apos_P": 0, "apos_B": 0,
            "quebradores": defaultdict(int), "g0": 0, "g1": 0
        })

        self.memoria_padroes_vencedores = []
        self.historico_regras = defaultdict(lambda: {"acertos": 0, "total": 0})
        self.controladores_fortes = defaultdict(int)
        self.padroes_fortes = []
        self.analise_recencia = {}
        self.regime_recencia = None

        self._treinar_modelo_profundo()

    def __getstate__(self):
        state = self.__dict__.copy()
        for key in ['modelo_transicao', 'modelo_numerico', 'color_ngrams',
                    'xadrez_stats', 'streak_breaker_stats',
                    'padroes_xadrez_detalhado', 'padroes_streak_detalhado']:
            if key in state:
                state[key] = dict(state[key])
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.modelo_transicao = defaultdict(list, state.get('modelo_transicao', {}))
        self.modelo_numerico = defaultdict(list, state.get('modelo_numerico', {}))
        self.color_ngrams = {k: defaultdict(int, v) for k, v in state.get('color_ngrams', {1: {}, 2: {}, 3: {}}).items()}
        self.xadrez_stats = {"quebras": 0, "continuacoes": 0, "numeros_quebradores": defaultdict(int)}
        self.xadrez_stats.update(state.get('xadrez_stats', {}))
        self.streak_breaker_stats = {"V": defaultdict(int), "P": defaultdict(int)}
        self.streak_breaker_stats.update(state.get('streak_breaker_stats', {}))
        self.padroes_xadrez_detalhado = defaultdict(lambda: {
            "total": 0, "apos_V": 0, "apos_P": 0, "apos_B": 0,
            "quebradores": defaultdict(int), "g0": 0, "g1": 0
        }, state.get('padroes_xadrez_detalhado', {}))
        self.padroes_streak_detalhado = defaultdict(lambda: {
            "total": 0, "apos_V": 0, "apos_P": 0, "apos_B": 0,
            "quebradores": defaultdict(int), "g0": 0, "g1": 0
        }, state.get('padroes_streak_detalhado', {}))

    def _treinar_modelo_profundo(self):
        if self.dados_longo and len(self.dados_longo) >= 5:
            self._processar_bloco_dados(self.dados_longo, 1, True)
        if self.dados_recencia and len(self.dados_recencia) >= 5:
            self._processar_bloco_dados(self.dados_recencia, 4, True)

    def mapear_padroes_avancados(self, dados):
        if not dados or len(dados) < 10:
            return

        cores = [d['cor'] for d in dados]
        numeros = [d['numero'] for d in dados]

        i = 0
        while i < len(cores) - 4:
            janela = cores[i:i+4]
            if all(janela[j] != janela[j-1] for j in range(1, 4)) and 'B' not in janela:
                if i + 4 < len(cores):
                    proximo_cor = cores[i+4]
                    num_quebra = numeros[i+3]
                    chave = "XADREZ_4"
                    self.padroes_xadrez_detalhado[chave]["total"] += 1
                    self.padroes_xadrez_detalhado[chave][f"apos_{proximo_cor}"] += 1
                    if proximo_cor != janela[-1]:
                        self.padroes_xadrez_detalhado[chave]["quebradores"][num_quebra] += 1
            i += 1

        i = 0
        while i < len(cores) - 3:
            if cores[i] == cores[i+1] == cores[i+2] and cores[i] != 'B':
                if i + 3 < len(cores):
                    proximo_cor = cores[i+3]
                    num_quebra = numeros[i+3]
                    chave = "STREAK_3"
                    self.padroes_streak_detalhado[chave]["total"] += 1
                    self.padroes_streak_detalhado[chave][f"apos_{proximo_cor}"] += 1
                    if proximo_cor != cores[i]:
                        self.padroes_streak_detalhado[chave]["quebradores"][num_quebra] += 1
            i += 1

        for i in range(len(cores)):
            self.color_ngrams[1][cores[i]] += 1
            if i + 1 < len(cores):
                self.color_ngrams[2][f"{cores[i]}-{cores[i+1]}"] += 1
            if i + 2 < len(cores):
                self.color_ngrams[3][f"{cores[i]}-{cores[i+1]}-{cores[i+2]}"] += 1

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
                self.unidade_analise[num]["ultimas_cores"].append(cor_post)
                if len(self.unidade_analise[num]["ultimas_cores"]) > 10:
                    self.unidade_analise[num]["ultimas_cores"].pop(0)

        for n in range(15):
            total = self.unidade_analise[n]["ocorrencias"]
            if total > 0:
                self.unidade_analise[n]["freq_v"] = round((self.unidade_analise[n]["V"] / total) * 100, 2)
                self.unidade_analise[n]["freq_p"] = round((self.unidade_analise[n]["P"] / total) * 100, 2)
                self.unidade_analise[n]["freq_b"] = round((self.unidade_analise[n]["B"] / total) * 100, 2)
                self.unidade_analise[n]["comportamento_dominante"] = self._calcular_comportamento_dominante(n)
                self.unidade_analise[n]["estabilidade"] = self._calcular_estabilidade(n)
                self.unidade_analise[n]["enfraquecimento"] = self._calcular_enfraquecimento(n)
                self.unidade_analise[n]["saturacao"] = self._calcular_saturacao(n)

    def _calcular_comportamento_dominante(self, num):
        freq_v = self.unidade_analise[num]["freq_v"]
        freq_p = self.unidade_analise[num]["freq_p"]
        if freq_v > freq_p + 8: return "VERMELHO"
        elif freq_p > freq_v + 8: return "PRETO"
        return "NEUTRO"

    def _calcular_estabilidade(self, num):
        ultimas = self.unidade_analise[num]["ultimas_cores"]
        if len(ultimas) < 5: return "NEUTRO"
        dominante = self.unidade_analise[num]["comportamento_dominante"]
        if dominante == "NEUTRO": return "NEUTRO"
        count = sum(1 for c in ultimas if c == ('V' if dominante == "VERMELHO" else 'P'))
        taxa = count / len(ultimas)
        if taxa >= 0.7: return "ESTÁVEL"
        elif taxa <= 0.4: return "INSTÁVEL"
        return "NEUTRO"

    def _calcular_enfraquecimento(self, num):
        return "ENFRAQUECIDO" if self.unidade_analise[num]["estabilidade"] == "INSTÁVEL" else "ESTÁVEL"

    def _calcular_saturacao(self, num):
        total = self.unidade_analise[num]["ocorrencias"]
        if total > 800: return "ALTA"
        elif total > 400: return "MÉDIA"
        return "BAIXA"

    def injetar_aprendizado_imediato(self, sub_dados, multiplicador_peso=4, analise_contexto=None):
        self.dados_recencia.extend(sub_dados)
        self._processar_bloco_dados(sub_dados, multiplicador_peso, True)
        if analise_contexto:
            for regra in analise_contexto.get("regras_posicionais", []):
                self.historico_regras[regra.get("tipo_regra", "DESCONHEVIDO")]["total"] += 1

    def registrar_padrao_vencedor(self, analise_contexto, resultado):
        if resultado not in ["G0", "G1"]: return
        padrao = {
            "geometria": analise_contexto.get("geometria"),
            "regras_ativas": [r.get("tipo_regra") for r in analise_contexto.get("regras_posicionais", [])],
            "controlador_dominante": analise_contexto.get("controlador_retardador", {}).get("dominancia"),
            "modo_mercado": analise_contexto.get("contexto_avancado", {}).get("modo_mercado"),
            "resultado": resultado,
            "peso": 1
        }
        if padrao not in self.memoria_padroes_vencedores:
            self.memoria_padroes_vencedores.append(padrao)
        if len(self.memoria_padroes_vencedores) > 50:
            self.memoria_padroes_vencedores.pop(0)

    def calcular_bonus_memoria(self, analise_contexto):
        bonus = 0
        for padrao in self.memoria_padroes_vencedores:
            match = 0
            if padrao.get("geometria") == analise_contexto.get("geometria"):
                match += 8
            comuns = set(padrao.get("regras_ativas", [])) & set([r.get("tipo_regra") for r in analise_contexto.get("regras_posicionais", [])])
            match += len(comuns) * 3
            if match >= 12:
                bonus += 4
        return min(bonus, 22)

    def predizer_proxima_casa(self, sub_num, sub_pol, analise_contexto=None):
        if len(sub_num) < 12:
            return "NEUTRO", 0.0, "Janela insuficiente"

        ultimo_num = sub_num[-1]
        ultimas_cores = (sub_pol[-2], sub_pol[-1])

        trans = self.modelo_transicao.get(ultimas_cores, [])
        por_num = self.modelo_numerico.get(ultimo_num, [])
        stats = self.unidade_analise.get(ultimo_num, {"freq_v": 0, "freq_p": 0})

        v_bonus = stats.get("freq_v", 0) * 3.5
        p_bonus = stats.get("freq_p", 0) * 3.5

        comportamento = stats.get("comportamento_dominante", "NEUTRO")
        estabilidade = stats.get("estabilidade", "NEUTRO")
        enfraquecimento = stats.get("enfraquecimento", "ESTÁVEL")
        saturacao = stats.get("saturacao", "BAIXA")

        if comportamento == "VERMELHO": v_bonus += 12
        elif comportamento == "PRETO": p_bonus += 12

        if estabilidade == "ESTÁVEL":
            if comportamento == "VERMELHO": v_bonus += 10
            elif comportamento == "PRETO": p_bonus += 10
        elif estabilidade == "INSTÁVEL":
            v_bonus -= 8
            p_bonus -= 8

        if enfraquecimento == "ENFRAQUECIDO":
            v_bonus -= 10
            p_bonus -= 10

        if saturacao == "ALTA":
            v_bonus -= 6
            p_bonus -= 6

        pos_v = stats.get("pos_numero_V", 0)
        pos_p = stats.get("pos_numero_P", 0)
        if pos_v + pos_p >= 5:
            if pos_v > pos_p * 1.25: v_bonus += 14
            elif pos_p > pos_v * 1.25: p_bonus += 14

        if hasattr(self, 'analise_recencia') and self.analise_recencia:
            if ultimo_num in self.analise_recencia:
                info = self.analise_recencia[ultimo_num]
                if info.get("tendencia_recente") == "FORTE":
                    if info["cor_mais_frequente_apos"] == "VERMELHO":
                        v_bonus += 15
                    else:
                        p_bonus += 15

        if analise_contexto:
            prob_streak_v = self.calcular_probabilidade_streak_empirica('V', 5)
            prob_streak_p = self.calcular_probabilidade_streak_empirica('P', 5)
            prob_xadrez_5 = self.calcular_probabilidade_xadrez_empirica(5)

            if prob_streak_v > 2.0 or prob_streak_p > 2.0:
                if sub_pol[-1] == 'V': p_bonus += 18
                else: v_bonus += 18

            if prob_xadrez_5 < 3.0 and analise_contexto.get("contexto_reversao", {}).get("xadrez_quebrou"):
                if sub_pol[-1] == 'V': v_bonus += 22
                else: p_bonus += 22

        if hasattr(self, 'xadrez_stats') and self.xadrez_stats:
            if ultimo_num in self.xadrez_stats.get('numeros_quebradores', {}):
                if sub_pol[-1] == 'V':
                    p_bonus += 12
                else:
                    v_bonus += 12

        if hasattr(self, 'streak_breaker_stats'):
            if sub_pol[-1] == 'V' and ultimo_num in self.streak_breaker_stats.get('V', {}):
                p_bonus += 10
            elif sub_pol[-1] == 'P' and ultimo_num in self.streak_breaker_stats.get('P', {}):
                v_bonus += 10

        has_rec = len(self.dados_recencia) > 0
        p_trans, p_num, p_geom = (0.22 if has_rec else 0.17), (0.18 if has_rec else 0.16), 0.25

        total_v = (trans.count('V') * p_trans) + (por_num.count('V') * p_num) + (0 * p_geom) + v_bonus
        total_p = (trans.count('P') * p_trans) + (por_num.count('P') * p_num) + (0 * p_geom) + p_bonus

        if analise_contexto:
            bonus_memoria = self.calcular_bonus_memoria(analise_contexto)
            if total_v > total_p: total_v += bonus_memoria
            else: total_p += bonus_memoria

        if total_v + total_p == 0:
            return "NEUTRO", 0.0, "Sem dados suficientes"

        prob_v = (total_v / (total_v + total_p)) * 100
        prob_p = (total_p / (total_v + total_p)) * 100

        BARREIRA = 52.5
        if prob_v >= BARREIRA and prob_v > prob_p + 4:
            return "VERMELHO", round(prob_v, 1), f"Confluência forte para Vermelho ({prob_v:.1f}%)"
        elif prob_p >= BARREIRA and prob_p > prob_v + 4:
            return "PRETO", round(prob_p, 1), f"Confluência forte para Preto ({prob_p:.1f}%)"
        return "NEUTRO", round(max(prob_v, prob_p), 1), "Sem confluência clara"

    def calcular_probabilidade_streak_empirica(self, cor, k):
        todos = (self.dados_longo or []) + (self.dados_recencia or [])
        if len(todos) < k + 1: return 0.0
        total = len(todos) - k
        count = sum(1 for i in range(total) if all(d['cor'] == cor for d in todos[i:i+k]))
        return round((count / total) * 100, 2) if total > 0 else 0.0

    def calcular_probabilidade_xadrez_empirica(self, k):
        todos = (self.dados_longo or []) + (self.dados_recencia or [])
        if len(todos) < k + 1: return 0.0
        total = len(todos) - k
        count = 0
        for i in range(total):
            janela = [d['cor'] for d in todos[i:i+k]]
            if all(janela[j] != janela[j-1] for j in range(1, len(janela))):
                count += 1
        return round((count / total) * 100, 2) if total > 0 else 0.0

    def analisar_comportamento_pos_numero_recencia(self, dados_recencia):
        if not dados_recencia or len(dados_recencia) < 30:
            return {"mensagem": "Base de recência muito pequena para análise confiável"}

        relatorio = {}
        contagem = {n: {"total": 0, "pos_V": 0, "pos_P": 0, "pos_B": 0} for n in range(15)}

        for i in range(len(dados_recencia) - 1):
            num = dados_recencia[i]['numero']
            cor_proxima = dados_recencia[i + 1]['cor']
            contagem[num]["total"] += 1
            if cor_proxima == "V":
                contagem[num]["pos_V"] += 1
            elif cor_proxima == "P":
                contagem[num]["pos_P"] += 1
            else:
                contagem[num]["pos_B"] += 1

        for num in range(15):
            dados = contagem[num]
            if dados["total"] == 0:
                continue

            total = dados["total"]
            cores = {"VERMELHO": dados["pos_V"], "PRETO": dados["pos_P"], "BRANCO": dados["pos_B"]}
            cor_dominante = max(cores, key=cores.get)
            freq = round((cores[cor_dominante] / total) * 100, 2)

            relatorio[num] = {
                "total_aparicoes_recencia": total,
                "cor_mais_frequente_apos": cor_dominante,
                "frequencia_cor_dominante_%": freq,
                "tendencia_recente": "FORTE" if freq >= 65 else ("MODERADA" if freq >= 55 else "FRACA")
            }

        return relatorio

    def analisar_comportamento_pos_numero(self):
        relatorio = {}
        for num in range(15):
            dados = self.unidade_analise[num]
            total = dados["ocorrencias"]
            if total == 0:
                continue

            cores_pos = {
                "VERMELHO": dados["pos_numero_V"],
                "PRETO": dados["pos_numero_P"],
                "BRANCO": dados["pos_numero_B"]
            }
            cor_dominante = max(cores_pos, key=cores_pos.get)
            freq_dominante = round((cores_pos[cor_dominante] / total) * 100, 2)

            ultimas = dados["ultimas_cores"]
            if len(ultimas) >= 8:
                ultimas_dominantes = sum(1 for c in ultimas if c == ('V' if cor_dominante == "VERMELHO" else 'P'))
                taxa_ultimas = ultimas_dominantes / len(ultimas)
                if taxa_ultimas < 0.5:
                    tendencia = "EM MUDANÇA / SATURAÇÃO POSSÍVEL"
                elif taxa_ultimas >= 0.75:
                    tendencia = "ESTÁVEL"
                else:
                    tendencia = "MODERADO"
            else:
                tendencia = "DADOS INSUFICIENTES"

            relatorio[num] = {
                "total_aparicoes": total,
                "cor_mais_frequente_apos": cor_dominante,
                "frequencia_cor_dominante_%": freq_dominante,
                "distribuicao_pos": cores_pos,
                "comportamento_dominante": dados["comportamento_dominante"],
                "estabilidade": dados["estabilidade"],
                "saturacao": dados["saturacao"],
                "tendencia_recente": tendencia
            }
        return relatorio


# ============================================================
# MotorNoCall (conservador - inalterado)
# ============================================================
class MotorNoCall:
    @staticmethod
    def checar_no_call(sub_num, sub_pol):
        cenarios_duplas = [(7, 8), (8, 9), (9, 10), (10, 11)]
        for idx1, idx2 in cenarios_duplas:
            if sub_num[idx1] == sub_num[idx2]:
                return True, "Volume 2 Cap 6: Trava das Duplas Ativa"

        posicoes_criticas_6 = [5, 8, 9, 10, 11]
        for pos in posicoes_criticas_6:
            if sub_num[pos] == 6:
                return True, "Volume 2 Cap 4: Trava Número 6 (Posição de No Call Ativa)"

        posicoes_criticas_2 = [8, 9, 10, 11]
        for pos in posicoes_criticas_2:
            if sub_num[pos] == 2:
                return True, "Volume 2 Cap 3: Trava Número 2"

        posicoes_criticas_b = [5, 8, 9, 10, 11]
        for pos in posicoes_criticas_b:
            if sub_pol[pos] == "B":
                return True, "Volume 2 Cap 5: Trava do Branco"

        return False, "Evento Neutro Operacional"


# ============================================================
# JuizHierarquicoModificado (inalterado)
# ============================================================
class JuizHierarquicoModificado:
    @staticmethod
    def arbitrar_sinal(no_call_ativo, motivo_nc, expectations, inclinacao_num, geometria_mercado, 
                       previsao_ia, status_inversao, historico_regras,
                       modo_mercado="NEUTRO", 
                       streak_atual=0, xadrez_len=0, xadrez_quebrou=False,
                       contexto_exaustao=False, sintese_evidencias=None):
        
        if no_call_ativo:
            return "NO CALL", motivo_nc, "SISTEMA_TRAVADO"

        direcao_ia, confianca_ia, raciocinio_ia = previsao_ia

        tem_inversao_final = any(
            "ESPELHO_INVERSO" in e.get("tipo_regra", "") or 
            "INVERSAO_FORTE" in e.get("tipo_regra", "")
            for e in expectations
        )

        if expectations:
            count_v = sum(1 for item in expectations if item["direcao"] == "VERMELHO")
            count_p = sum(1 for item in expectations if item["direcao"] == "PRETO")

            if tem_inversao_final:
                return "PRETO", "Inversão forte no fechamento (Espelho/Inversão)", "INVERSAO_FINAL"

            if count_v > count_p:
                return "VERMELHO", "Regra posicional forte ativa", "REGRA_POSICIONAL"
            elif count_p > count_v:
                return "PRETO", "Regra posicional forte ativa", "REGRA_POSICIONAL"

        if geometria_mercado == "CICLO_FECHADO_VPPV":
            return "PRETO", "Geometria VPPV (Padrão forte)", "GEOMETRIA_FORTE"
        if geometria_mercado == "CICLO_FECHADO_PVVP":
            return "VERMELHO", "Geometria PVVP (Padrão forte)", "GEOMETRIA_FORTE"

        if direcao_ia != "NEUTRO":
            return direcao_ia, f"IA Preditiva ({confianca_ia:.1f}%)", "IA_PREDITIVA"

        if expectations:
            count_v = sum(1 for item in expectations if item["direcao"] == "VERMELHO")
            count_p = sum(1 for item in expectations if item["direcao"] == "PRETO")
            if count_v >= count_p:
                return "VERMELHO", "Fallback por regras", "FALLBACK_REGRA"
            else:
                return "PRETO", "Fallback por regras", "FALLBACK_REGRA"

        return "VERMELHO", "Fallback padrão do sistema", "FALLBACK_PADRAO"


# ============================================================
# MotorContagensProjetivas (inalterado)
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
                if alvo_idx == 11 or alvo_idx == 12:
                    if any(sub_num[k] == 0 for k in range(i, 12)):
                        continue
                    lista_bruta.append({
                        "direcao": "VERMELHO",
                        "tipo_regra": f"V3_ATIVADOR_{num_atual}",
                        "origem": f"Volume 3: Contagem {num_atual}"
                    })

        par_fechamento = (sub_num[10], sub_num[11])
        continuidade_preta_validas = [(8,9), (9,10), (10,11), (11,12), (12,13), (13,14), (14,13), (13,12), (12,11), (11,10)]
        continuidade_vermelha_validas = [(1,2), (2,3), (3,4), (4,5), (5,6), (6,7), (7,6), (6,5), (5,4), (4,3)]

        if par_fechamento in continuidade_preta_validas:
            lista_bruta.append({"direcao": "PRETO", "tipo_regra": "V2_CONTINUIDADE_PRETA", "origem": "Volume 2"})
        elif par_fechamento in continuidade_vermelha_validas:
            lista_bruta.append({"direcao": "VERMELHO", "tipo_regra": "V2_CONTINUIDADE_VERMELHA", "origem": "Volume 2"})

        if sub_num[11] in [3, 4, 5] and sub_pol[10] == sub_pol[11]:
            direcao = "VERMELHO" if sub_pol[11] == "V" else "PRETO"
            lista_bruta.append({
                "direcao": direcao,
                "tipo_regra": "ASSUNCAO_CONTAGEM_FINAL",
                "origem": "Assunção de contagem no fechamento da janela"
            })

        if len(sub_pol) >= 5:
            final = "".join(sub_pol[-5:])
            padroes_inversao = ["VPVPV", "PVPVP", "VPPVP", "PVVPV", "VPVPP", "PVPPV"]
            for padrao in padroes_inversao:
                if padrao in final:
                    direcao_inversao = "PRETO" if sub_pol[-1] == "V" else "VERMELHO"
                    lista_bruta.append({
                        "direcao": direcao_inversao,
                        "tipo_regra": "ESPELHO_INVERSO_FINAL",
                        "origem": f"Padrão de inversão detectado ({padrao})"
                    })
                    break

        if len(sub_pol) >= 3:
            if sub_pol[-3] == sub_pol[-2] and sub_pol[-1] != sub_pol[-2]:
                lista_bruta.append({
                    "direcao": "NEUTRO",
                    "tipo_regra": "INVERSAO_FORTE_FINAL",
                    "origem": "Inversão clara na última posição após repetição"
                })

        return lista_bruta


# ============================================================
# AnalisadorContextoAvancado (inalterado)
# ============================================================
class AnalisadorContextoAvancado:
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
    def detectar_modo_mercado(sub_pol):
        texto = "".join(sub_pol)
        alternancias = sum(1 for i in range(len(texto)-1) if texto[i] != texto[i+1])
        if alternancias >= 7: return "CHUVA"
        elif alternancias <= 3: return "RECUPERACAO"
        return "NEUTRO"


# ============================================================
# LeitorXLS + SequenciaOperacional + MotorV1Completo + ProcessadorTipoB + EngineMatematicoAvancado
# ============================================================

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
            for possible in ['número', 'numero', 'num', 'number', 'result']:
                if possible in df.columns:
                    col_num = possible
                    break
            
            if col_num is None:
                for col in df.columns:
                    if df[col].dtype in ['int64', 'float64']:
                        col_num = col
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
                    num = int(float(row['numero']))
                    if num == 0:
                        cor = 'B'
                    elif 1 <= num <= 7:
                        cor = 'V'
                    elif 8 <= num <= 14:
                        cor = 'P'
                    else:
                        continue
                    dados.append({"numero": num, "cor": cor})
                except:
                    continue
            return dados if len(dados) >= 5 else None
        except Exception as e:
            print(f"[LeitorXLS] Erro: {e}")
            return None


class SequenciaOperacional:
    def __init__(self, lista_resultados):
        self.cronologia = lista_resultados
        self.numerica = [int(r['numero']) for r in self.cronologia]
        self.polaridades = [str(r['cor']).upper() for r in self.cronologia]
        self.total = len(self.numerica)


class MotorV1Completo:
    def __init__(self, lista_dados_xls, ia_existente=None):
        self.seq = SequenciaOperacional(lista_dados_xls)
        corte = max(0, len(lista_dados_xls) - 150)
        self.dados_longo = lista_dados_xls[:corte]
        self.dados_curto = lista_dados_xls[corte:]

        if ia_existente is not None:
            self.ia = ia_existente
        else:
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

            analise = MotorAnalise.analisar_janela(sub_num, sub_pol, self.ia)

            if analise["no_call"]["ativo"]:
                sinal = "NO CALL"
                justificativa = analise["no_call"]["motivo"]
                regra_id = "SISTEMA_TRAVADO"
                direcao_ia = "NEUTRO"
                conf_ia = 0.0
                raciocinio_ia = analise["no_call"]["motivo"]
                expectativas = []
                geometria = analise.get("geometria", "ESTÁVEL")
                streak = 0
                xadrez_len = 0
                xadrez_quebrou = False
                contexto_exaustao = False
                modo_mercado = "NEUTRO"
            else:
                geometria = analise["geometria"]
                expectativas = analise["regras_posicionais"]
                direcao_ia = analise["ia"]["direcao"]
                conf_ia = analise["ia"]["confianca"]
                raciocinio_ia = analise["ia"]["raciocinio"]
                streak = analise["contexto_reversao"]["streak"]
                xadrez_len = analise["contexto_reversao"]["xadrez_len"]
                xadrez_quebrou = analise["contexto_reversao"]["xadrez_quebrou"]
                contexto_exaustao = analise["contexto_reversao"]["exaustao"]
                modo_mercado = analise["contexto_avancado"].get("modo_mercado", "NEUTRO")

                sinal, justificativa, regra_id = JuizHierarquicoModificado.arbitrar_sinal(
                    False, "", expectativas, None, geometria,
                    (direcao_ia, conf_ia, raciocinio_ia), None, self.historico_regras,
                    modo_mercado=modo_mercado,
                    streak_atual=streak,
                    xadrez_len=xadrez_len,
                    xadrez_quebrou=xadrez_quebrou,
                    contexto_exaustao=contexto_exaustao
                )

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

            if classificacao in ["G0", "G1"]:
                contexto_analise = {
                    "geometria": geometria,
                    "regras_posicionais": expectativas,
                    "controlador_retardador": analise.get("controlador_retardador", {}),
                    "contexto_avancado": {"modo_mercado": modo_mercado}
                }
                self.ia.registrar_padrao_vencedor(contexto_analise, classificacao)

            if regra_id not in ["NENHUMA", "SISTEMA_TRAVADO"]:
                self.historico_regras[regra_id]["total"] += 1
                if classificacao in ["G0", "G1"]:
                    self.historico_regras[regra_id]["acertos"] += 1

            bloco = [{"numero": self.seq.numerica[k], "cor": self.seq.polaridades[k]} 
                     for k in range(idx, min(idx + 12 + salto, self.seq.total))]
            
            contexto_injecao = {
                "regras_posicionais": expectativas,
                "controlador_retardador": analise.get("controlador_retardador", {}),
                "geometria": geometria
            }
            self.ia.injetar_aprendizado_imediato(bloco, 4, contexto_injecao)

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

        regime_rec = None
        if os.path.exists("base_recencia_ativa.xlsx"):
            base_rec = LeitorXLS("base_recencia_ativa.xlsx").ler_e_validar()
            if base_rec:
                ia = integrar_recencia_no_modelo(base_rec, 5)
                regime_rec = ia.regime_recencia

        analise = MotorAnalise.analisar_janela(self.entrada, self.polaridades, ia)

        nc_ativo = analise["no_call"]["ativo"]
        motivo_nc = analise["no_call"]["motivo"]
        geometria = analise["geometria"]
        expectativas = analise["regras_posicionais"]
        direcao_ia = analise["ia"]["direcao"] if not nc_ativo else "NEUTRO"
        conf_ia = analise["ia"]["confianca"] if not nc_ativo else 0.0
        raciocinio_ia = analise["ia"]["raciocinio"] if not nc_ativo else motivo_nc
        streak = analise["contexto_reversao"]["streak"]
        xadrez_len = analise["contexto_reversao"]["xadrez_len"]
        xadrez_quebrou = analise["contexto_reversao"]["xadrez_quebrou"]
        contexto_exaustao = analise["contexto_reversao"]["exaustao"]
        modo_mercado = analise["contexto_avancado"].get("modo_mercado", "NEUTRO")

        raciocinio_trace = analise["camadas"]

        if nc_ativo:
            return {
                "sinal": "NO CALL",
                "justificativa": motivo_nc,
                "no_call": True,
                "regime_recencia": regime_rec,
                "motivo_real": f"NO CALL pelo MotorNoCall: {motivo_nc}"
            }

        sinal = direcao_ia
        justificativa = f"IA Preditiva ({conf_ia:.1f}%)"
        regra_id = "IA_PREDITIVA"

        if regime_rec and regime_rec["confianca_regime"] >= 55:
            viés = regime_rec["viés_atual"]
            modo = regime_rec["modo_dominante"]

            if viés in ["VERMELHO", "PRETO"]:
                sinal = viés
                justificativa = f"Recência determina viés atual: {viés} | Modo: {modo}"
                regra_id = "RECENCIA_REGIME_FORTE"

            if modo == "STREAK_DOMINANTE" and regime_rec["streak_medio"] >= 4:
                justificativa += " (Streak dominante na recência)"
            elif modo == "XADREZ_DOMINANTE":
                justificativa += " (Xadrez dominante na recência)"

        if geometria in ["CICLO_FECHADO_VPPV", "CICLO_FECHADO_PVVP"]:
            sinal = "PRETO" if geometria == "CICLO_FECHADO_VPPV" else "VERMELHO"
            justificativa = f"Geometria forte + Recência ({regime_rec['viés_atual'] if regime_rec else 'N/A'})"
            regra_id = "GEOMETRIA_FORTE"

        if sinal != "NO CALL" and streak >= 6:
            if direcao_ia != sinal:
                sinal = "NO CALL"
                justificativa = f"Veto de streak {streak}x"
                regra_id = "VETO_STREAK"

        return {
            "sinal": sinal,
            "justificativa": justificativa,
            "confianca_ia": round(conf_ia, 2),
            "no_call": False,
            "regime_recencia": regime_rec,
            "motivo_real": justificativa,
            "raciocinio_trace": raciocinio_trace,
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
