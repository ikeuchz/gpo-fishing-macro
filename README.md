# GPO Fishing Macro

Projeto de [ikeuchz](https://github.com/ikeuchz): macro de pesca para Grand Piece Online, com código Python editável e organizado para servir de base a novos macros.

Esta versão é uma nova implementação assistida por Codex, escrita em código-fonte a partir do comportamento desejado. Está em desenvolvimento: a detecção e o controle precisam ser calibrados e validados no jogo. O executável enviado anteriormente não é o resultado deste código.

## Download da versão de teste

Baixe [GPO-Fishing-Macro.exe](https://github.com/ikeuchz/gpo-fishing-macro/raw/refs/heads/main/GPO-Fishing-Macro.exe) e execute no Windows 64 bits. Este é o novo executável compilado a partir do código deste projeto, não o arquivo enviado anteriormente. Não requer instalação de Python.

Há um relato de detecção pelo Microsoft Defender na versão anterior, ainda sem diagnóstico concluído. As mudanças de interface, atalhos e ícone não confirmam a segurança do executável; não desative a proteção para executá-lo.

A compilação do commit `77b8986` passou no [GitHub Actions](https://github.com/ikeuchz/gpo-fishing-macro/actions/runs/44154476707), incluindo os testes de interface no Windows. Ainda é uma versão de teste, sem validação da pesca dentro do Roblox.

## Executar pelo código no Windows

Instale Python 3.12 de 64 bits com Tkinter (incluído no instalador padrão). Abra um terminal na pasta do projeto:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python run.py
```

1. Abra o jogo e mantenha sua resolução e escala da interface estáveis.
2. Clique em **Selecionar área** e arraste sobre o minigame para selecionar a área na tela principal. Esc cancela. A área também pode ser digitada em pixels como `x, y, largura, altura`.
3. Ajuste as teclas dos itens, salve as configurações e volte à janela do jogo.
4. Clique em **Iniciar em 3 segundos** e volte ao jogo durante a contagem. Use **Parar / cancelar** para interromper. Você também pode configurar atalhos na aba **Atalhos**.

O título da janela ativa deve conter `Roblox`, ou o texto configurado na interface. Se outra janela receber foco, o macro para e solta o mouse; use seu atalho configurado no jogo para retomar. Durante a execução, alterações da interface só passam a valer na próxima partida. Os atalhos padrão agora são **INSERT** (iniciar/parar), **HOME** (área) e **END** (sair). Na aba **Atalhos**, é possível trocar por combinações como **CTRL+G**, **ALT+P**, outras teclas de navegação ou F1–F12. Salve para aplicar; atalhos duplicados são rejeitados. Configurações antigas recebem os novos padrões automaticamente.

### Acompanhar o peixe sem lançar a vara sozinho

O lançamento automático agora vem **desligado**. Inicie o macro, volte ao jogo e lance a vara manualmente. Ele aguarda a leitura do minigame em três quadros consecutivos antes de atuar. Sem leitura, solta o mouse e não troca de item nem relança por timeout. A opção **Lançar vara automaticamente** na aba de rotinas é separada e só deve ser ativada se você quiser esse comportamento.

Na seleção verde podem aparecer as duas barras. A leitura agora separa a barra de controle da barra de progresso. O campo **Barra de controle** usa `left` (esquerda) por padrão; troque por `right` se a barra com o peixe estiver à direita. A barra de progresso não entra no cálculo. A detecção ainda depende das cores azul/cinza/branco da sua interface; se não corresponderem, será preciso calibrar com uma captura real do minigame.

A moldura verde permanece visível. Uma seta branca do lado de fora marca o **PEIXE**; uma seta verde-água marca **VOCÊ**, a posição estimada do marcador pela abertura da barra azul. Elas acompanham a leitura real, não são movimentos decorativos. Se a leitura sumir, as setas somem e o botão do mouse é solto. A moldura e as setas são transparentes a cliques e ficam fora da região analisada para não interferir na captura.

### Ver o painel durante a pesca

**Sempre visível** fica ativado por padrão. Use **Modo compacto / completo** para deixar apenas os controles e o status na tela. Mova o painel para fora do retângulo verde. O jogo deve estar em modo janela ou janela sem bordas: uma janela Tk pode não aparecer sobre tela cheia exclusiva. O macro continua parando se o jogo perder o foco; observar o painel não exige Alt+Tab. Para clicar nas configurações, pare e depois reinicie no jogo.

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
.venv\Scripts\python -m PyInstaller --clean --noconfirm --onefile --windowed --name GPO-Fishing-Macro --collect-all mss --icon gpo_macro/assets/app.ico --add-data "gpo_macro/assets;gpo_macro/assets" run.py
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
