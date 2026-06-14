import os
from main import LeitorXLS, MotorNoCall, MotorContagensProjetivas, AnalisadorContextoAvancado, JuizHierarquicoModificado

class ProcessadorTipoB:
    def __init__(self, sequencia_12_numeros, caminho_base_dados):
        self.entrada_usuario = sequencia_12_numeros
        self.caminho_base = caminho_base_dados
        self.polaridades_usuario = []
        for num in self.entrada_usuario:
            if num == 0: self.polaridades_usuario.append("B")
            elif num in [1,2,3,4,5,6,7]: self.polaridades_usuario.append("V")
            else: self.polaridades_usuario.append("P")

    def executar_sinal_real(self):
        if len(self.entrada_usuario) != 12: return "[ERRO] Requisito de exatamente 12 números violado."
        leitor = LeitorXLS(self.caminho_base)
        base_historica = leitor.ler_e_validar()
        if not base_historica: return "[ERRO] Base de dados resultados_blaze.xlsx ausente."

        num_global = [d['numero'] for d in base_historica]
        pol_global = [d['cor'] for d in base_historica]

        saturacao = AnalisadorContextoAvancado.mapear_padroes_geometria(self.polaridades_usuario)
        nc_ativo, motivo_nc = MotorNoCall.checar_no_call(self.entrada_usuario, self.polaridades_usuario)
        expectativas = MotorContagensProjetivas.mapear_janela(self.entrada_usuario, self.polaridades_usuario, saturacao)
        
        num_fechamento = self.entrada_usuario[-1]
        inclinacao_num = AnalisadorContextoAvancado.calcular_numerologia_pos_numero(num_fechamento, num_global, pol_global)
        sinal_final, justificativa = JuizHierarquicoModificado.arbitrar_sinal(nc_ativo, motivo_nc, expectativas, inclinacao_num)

        chance_branco, casas_atraso = AnalisadorContextoAvancado.preditor_estatistico_branco(num_fechamento, num_global, pol_global)

        if sinal_final == "NO CALL":
            mercado, qualidade, risco, expectativa_saida, controlador = "INSTÁVEL", "CRÍTICA", "CRÍTICO", "NO CALL", "Nenhum"
            retardador = motivo_nc if nc_ativo else "Contexto Indefinido"
        else:
            mercado = "MERCADO PAGADOR" if saturacao == "ESTÁVEL" else "SATURAÇÃO"
            qualidade = "EXCELENTE" if "Consenso" in justificativa else "BOA"
            risco = "BAIXO" if qualidade == "EXCELENTE" else "MÉDIO"
            expectativa_saida = "G0"
            controlador = justificativa.split("via ")[1] if "via" in justificativa else "Matriz Pós-Número"
            retardador = "Evento Neutro Operacional"

        output = "[MEMÓRIA DE CÁLCULO]\n"
        output += f"- Mapeamento: Sequência {self.entrada_usuario} processada.\n"
        output += f"- Geometria da Janela: {saturacao}\n"
        output += f"- Inclinação Histórica ({num_fechamento}): {inclinacao_num[0]} ({inclinacao_num[1]:.1f}%)\n"
        output += f"- Resolução de Conflitos: {justificativa}\n\n"
        output += "[RESULTADO FINAL]\n"
        output += f"SINAL: {sinal_final}\n"
        output += f"BRANCO: {chance_branco} CHANCE (Atraso: {casas_atraso} rodadas)\n"
        output += "RESUMO MOTOR V1: Validação analítica concluída sob restrições do Adendo Normativo.\n"
        output += f"CONTROLADOR: {controlador}\n"
        output += f"RETARDADOR: {retardador}\n"
        output += f"MERCADO: {mercado}\n"
        output += f"QUALIDADE: {qualidade}\n"
        output += f"RISCO DE ATRASO: {risco}\n"
        output += f"EXPECTATIVA: {expectativa_saida}\n"
        return output
