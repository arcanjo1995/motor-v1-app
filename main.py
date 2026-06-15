    def ler_e_validar(self):
        if not os.path.exists(self.caminho): return None
        try:
            # Carrega o arquivo
            df = pd.read_excel(self.caminho) if self.caminho.endswith('xlsx') else pd.read_csv(self.caminho)
            df.columns = [str(c).lower().strip() for c in df.columns]
            
            # Tenta encontrar colunas por nome ou assume a posição (1ª=num, 2ª=cor)
            lista_num = [c for c in df.columns if any(x in c for x in ['num', 'val', 'giro', 'spin', 'valor'])]
            lista_cor = [c for c in df.columns if any(x in c for x in ['cor', 'color', 'c'])]
            
            col_num = lista_num[0] if lista_num else df.columns[0]
            col_cor = lista_cor[0] if lista_cor else df.columns[1]
            
            # Processamento seguro
            dados = []
            for _, r in df.iterrows():
                try:
                    num = int(r[col_num])
                    # Regra de polaridade (Blaze)
                    cor = 'B' if num == 0 else ('V' if 1 <= num <= 7 else 'P')
                    dados.append({"numero": num, "cor": cor})
                except (ValueError, TypeError):
                    continue
            
            return dados if len(dados) >= 15 else None
        except Exception as e:
            print(f"Erro crítico na leitura do XLS: {e}")
            return None
