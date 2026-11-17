# GPO Fishing Macro

Projeto de [ikeuchz](https://github.com/ikeuchz): macro de pesca para Grand Piece Online, com código Python editável e organizado para servir de base a novos macros.

Esta versão é uma nova implementação assistida por Codex, escrita em código-fonte a partir do comportamento desejado. Está em desenvolvimento: a detecção e o controle precisam ser calibrados e validados no jogo. O executável enviado anteriormente não é o resultado deste código.

## Download da versão de teste

Baixe [GPO-Fishing-Macro.exe](https://github.com/ikeuchz/gpo-fishing-macro/raw/refs/heads/main/GPO-Fishing-Macro.exe) e execute no Windows 64 bits. Este é o novo executável compilado a partir do código deste projeto, não o arquivo enviado anteriormente. Não requer instalação de Python.

A compilação do commit `912da1d` passou no [GitHub Actions](https://github.com/ikeuchz/gpo-fishing-macro/actions/runs/44138822252), incluindo os testes de interface no Windows. Ainda é uma versão de teste, sem validação da pesca dentro do Roblox.

## Executar pelo código no Windows

Instale Python 3.12 de 64 bits com Tkinter (incluído no instalador padrão). Abra um terminal na pasta do projeto:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python run.py
```

1. Abra o jogo e mantenha sua resolução e escala da interface estáveis.
2. Pressione F2 e arraste sobre o minigame para selecionar a área na tela principal. Esc cancela. A área também pode ser digitada em pixels como `x, y, largura, altura`.
3. Ajuste as teclas dos itens, salve as configurações e volte à janela do jogo.
4. Pressione F1 para iniciar ou parar. F3 encerra a aplicação.

O título da janela ativa deve conter `Roblox`, ou o texto configurado na interface. Se outra janela receber foco, o macro para e solta o mouse; pressione F1 novamente no jogo para retomar. Durante a execução, alterações da interface só passam a valer na próxima partida. Os atalhos globais F1/F2/F3 são fixos nesta versão.

O macro usa captura de tela para procurar a barra azul, o fundo cinza e o indicador branco de um minigame vertical. O controle mantém ou solta o botão esquerdo conforme a posição detectada e os ganhos proporcional/derivativo. Ajuste as tolerâncias se a detecção não reconhecer a interface. O contador indica ciclos terminados visualmente, não confirmação de itens no inventário.

## Iscas e frutas

As funções opcionais vêm desligadas. Na aba **Rotinas e pontos**, capture cada ponto com o botão de captura: informe o nome e posicione o cursor no local em até três segundos. Edite as sequências em JSON e salve antes de ativar.

Os exemplos de compra e armazenamento são modelos configuráveis, não sequências já validadas para sua interface. Os pontos precisam corresponder aos botões do jogo, e as etapas devem reproduzir sua sequência manual.

```json
{
  "points": {"shop": [400, 300], "confirm": [500, 400]},
  "routines": {
    "buy": [{"click": "shop"}, {"wait": 0.5}, {"click": "confirm"}],
    "bait": [],
    "store": []
  }
}
```

Ações disponíveis: `click` em um ponto nomeado, `key` para uma letra/número e `wait` em segundos. Uma rotina ativada precisa ter ações e todos os pontos necessários. Compra ocorre no início e a cada N ciclos; seleção de isca antes do lançamento; armazenamento após cada ciclo. As coordenadas são absolutas: recapture ao mover a interface ou mudar a resolução.

Configurações ficam em `settings.json`, ao lado de `run.py` ou do executável. Esse arquivo local não é enviado ao GitHub.

## Gerar o executável

No Windows:

```powershell
.venv\Scripts\python -m pip install -r requirements-build.txt
.venv\Scripts\python -m PyInstaller --clean --noconfirm --onefile --windowed --name GPO-Fishing-Macro --collect-all mss run.py
```

O arquivo gerado fica em `dist/GPO-Fishing-Macro.exe`. Não é necessário Python na máquina que receber esse executável.

O workflow **Windows executable**, em **Actions**, testa e compila a aplicação. Após uma execução bem-sucedida, baixe o ZIP **GPO-Fishing-Macro-Windows** na seção **Artifacts** da execução (o GitHub exige login para baixar esses artefatos). Compilar com sucesso não substitui um teste de pesca no jogo.

## Estrutura para novos macros

- `config.py`: parâmetros, validação e persistência.
- `vision.py`: interpretação das imagens e controlador, sem eventos de mouse.
- `engine.py`: ciclo de automação, sequências e interrupção.
- `windows.py`: adaptador de teclado, mouse e janela ativa.
- `app.py`: interface, seleção de área e captura de pontos.

Para outro macro, adapte a detecção em `vision.py`, as etapas em `engine.py` e os parâmetros em `config.py`. Rotinas simples de cliques e teclas podem ser alteradas na interface sem modificar o Python.

## Testes

```powershell
.venv\Scripts\python -m unittest discover -s tests -v
```

Os testes usam imagens sintéticas e uma entrada simulada para verificar detecção, direção do controle, configurações e liberação do mouse ao parar, perder foco ou ocorrer erro. Não interagem com Roblox.
