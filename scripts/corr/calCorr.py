import numpy as np
import scipy.stats as stats

# ==============================================================================
# 1. MATRIZES (COPIADAS DIRETAMENTE DO SEU VSCODE)
# ==============================================================================

matriz_modelagem_txt = """
1,000	0,000	0,000	0,000	0,000	0,467	0,467	0,000	0,467	0,000	0,467	0,000	0,423	0,030
-	1,000	0,000	0,000	0,000	0,000	0,000	0,000	0,000	0,000	0,000	0,000	0,000	0,000
-	-	1,000	0,000	0,000	0,000	0,000	0,000	0,000	0,000	0,000	0,000	0,000	0,000
-	-	-	1,000	0,000	0,000	0,000	0,000	0,000	0,000	0,000	0,000	0,000	0,000
-	-	-	-	1,000	0,000	0,000	0,000	0,000	0,000	0,158	0,158	0,158	0,158
-	-	-	-	-	1,000	1,000	0,000	0,660	0,000	0,824	0,000	0,423	0,030
-	-	-	-	-	-	1,000	0,000	0,660	0,000	0,824	0,000	0,423	0,030
-	-	-	-	-	-	-	1,000	0,340	0,000	0,000	0,000	0,000	0,000
-	-	-	-	-	-	-	-	1,000	0,000	0,660	0,000	0,423	0,030
-	-	-	-	-	-	-	-	-	1,000	0,000	0,000	0,000	0,000
-	-	-	-	-	-	-	-	-	-	1,000	0,177	0,600	0,207
-	-	-	-	-	-	-	-	-	-	-	1,000	0,577	0,485
-	-	-	-	-	-	-	-	-	-	-	-	1,000	0,515
-	-	-	-	-	-	-	-	-	-	-	-	-	1,000
"""

matriz_degradacao_txt = """
-26,1	-28,0	-32,6	-29,4	-26,5	-23,5	-29,5	-47,5	-41,6	-53,9	-25,3	-3,5	-18,5	-6,6
-	-50,0	-7,9	-25,7	-31,4	-9,0	-31,2	-49,5	-43,4	-34,0	-30,3	0,0	-8,0	-2,0
-	-	-51,9	-42,7	-35,2	0,0	-54,7	-9,1	-10,2	-3,0	-33,5	0,0	-9,1	-5,6
-	-	-	-50,5	-31,9	-9,6	-31,3	-50,5	-43,9	-34,0	-30,8	0,0	-8,9	-2,0
-	-	-	-	-30,8	-33,8	-35,7	-43,6	-43,8	-41,4	-31,2	-30,3	-34,8	-41,0
-	-	-	-	-	-8,2	-44,9	-6,9	-3,5	-0,9	-32,0	0,0	-9,7	-3,5
-	-	-	-	-	-	-47,7	-65,7	-61,0	-45,0	-34,5	-13,0	-39,0	-14,8
-	-	-	-	-	-	-	-16,7	-36,8	-21,4	-40,2	0,0	-15,4	-6,9
-	-	-	-	-	-	-	-	-50,0	-30,4	-41,3	0,0	-10,1	-5,0
-	-	-	-	-	-	-	-	-	-54,7	-40,9	0,0	-7,0	-3,2
-	-	-	-	-	-	-	-	-	-	-31,2	-30,8	-34,8	-41,6
-	-	-	-	-	-	-	-	-	-	-	-4,8	-34,2	-24,5
-	-	-	-	-	-	-	-	-	-	-	-	-47,4	-48,2
-	-	-	-	-	-	-	-	-	-	-	-	-	-50,6

"""

# ==============================================================================
# 2. FUNÇÃO DE TRATAMENTO CORRIGIDA PARA ALINHAMENTO POR COLUNA
# ==============================================================================
def extrair_triangulo_superior(texto_matriz):
    valores_vetorizados = []
    linhas = [l.strip() for l in texto_matriz.strip().split('\n') if l.strip()]
    
    for i, linha in enumerate(linhas):
        elementos = linha.split()
        
        # Iteramos por todas as colunas da linha
        for j, elem in enumerate(elementos):
            # Só extraímos se a coluna for maior ou igual à linha (triângulo superior)
            if j >= i and elem != '-':
                val_formatado = float(elem.replace(',', '.'))
                valores_vetorizados.append(val_formatado)
                
    return np.array(valores_vetorizados)

# ==============================================================================
# 3. EXECUÇÃO DO CÁLCULO
# ==============================================================================
try:
    vetor_modelagem = extrair_triangulo_superior(matriz_modelagem_txt)
    vetor_degradacao = extrair_triangulo_superior(matriz_degradacao_txt)
    
    if len(vetor_modelagem) != len(vetor_degradacao):
        print(f"Erro: As matrizes têm tamanhos diferentes!")
        print(f"Modelagem extraiu {len(vetor_modelagem)} valores. Degradação extraiu {len(vetor_degradacao)}.")
    else:
        # Correlação de Pearson (Relação linear)
        pearson_coef, pearson_p = stats.pearsonr(vetor_modelagem, vetor_degradacao)
        
        # Correlação de Spearman (Relação de ranking)
        spearman_coef, spearman_p = stats.spearmanr(vetor_modelagem, vetor_degradacao)
        
        print("-" * 50)
        print(f"Número de pontos analisados (coexecuções): {len(vetor_modelagem)}")
        print("-" * 50)
        print(f"CORRELAÇÃO DE PEARSON:")
        print(f"  Coeficiente (r): {pearson_coef:.4f}")
        print(f"  P-Valor:         {pearson_p:.4e}")
        print("-" * 50)
        print(f"CORRELAÇÃO DE SPEARMAN:")
        print(f"  Coeficiente (ρ): {spearman_coef:.4f}")
        print(f"  P-Valor:         {spearman_p:.4e}")
        print("-" * 50)

except Exception as e:
    print(f"Ocorreu um erro ao processar os dados. Detalhes: {e}")
