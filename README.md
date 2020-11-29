# MINIMAX E ALPHA-BETA PRUNING NO AMBIENTE AGENT1

Este repositório contém o código desenvolvido no âmbito da investigação feita pelos alunos sobre os algoritmos de pesquisa adversarial Minimax e Alpha-beta pruning e a sua aplicação no contexto do simulador Agent1. Para a sua implementação foi formulado um jogo para dois jogadores no contexto do ambiente em questão. Neste jogo, um jogador (chamado Min) controla o agente através da linha de comandos e deve tentar alcançar a casa objetivo. O outro jogador (chamado Max), controlado pelo computador e usando o algoritmo Minimax ou Alpha-beta pruning, tenta impedir que o jogador Min alcance o objetivo. Verificou-se que caso seja jogado racionalmente por ambos os jogadores, ganha aquele que se encontra mais próximo da casa objetivo. Algumas das implementações permitem a visualização da árvore de estados gerada para o melhor entendimento do algoritmo e facilidade de depuração. Foram feitos vários testes de tempo e espaço e, como esperado, o algoritmo Alpha-beta pruning consome consideravelmente menos tempo e memória, principalmente quando aplicada a heurística dos *killer moves*.


Para correr o servidor, executar num terminal o seguinte comando, a partir do **diretório principal do projeto**:
    Caminho/Para/O/Diretório/agent1_alphabetapruning> python server/main.py

Para correr um jogo, executar num terminal o seguinte comando, a partir do **diretório principal do projeto**:
    Caminho/Para/O/Diretório/agent1_alphabetapruning> python client/ficheiro_desejado.py

Os vários jogos estão no diretório client, e cada um implementa de forma diferente ou o algoritmo minimax ou o alpha-beta pruning. Os nomes são descritivos.
Para configurar o número de rondas, alterar o perâmetro correspondente na função main de cada um.
Para configurar diferentes aspetos do mapa, alterar os ficheiros correspondentes no diretório input_files


Foi incluída uma demonstração em vídeo da execução do ficheiro alpha_beta_pruning.py com 13 rondas e sem visualização.

O grupo:
Francisco Mendonça
Gil Silva
Rui Bento
