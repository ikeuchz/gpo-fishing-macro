# Engenharia reversa — GPO Fishing Macro

Análise estática do executável fornecido pelo usuário. O programa não foi executado. O resultado recupera bytecode, símbolos e lógica; não é uma recuperação integral do código-fonte Python original.

## Identificação

- Arquivo: `GPO fishing macro 7.00000000000001.exe`
- Tamanho: 24.666.363 bytes.
- SHA-256: `31f6923fcb0999d5bddf8dca1363109a2bcb8740cb6e8e8158c2b66caddb64f5`
- Windows x64, PE32+, interface gráfica.
- Empacotamento PyInstaller; runtime Python 3.14 (`python314.dll`).
- Módulo de entrada: `z`, nome original registrado: `z.py`.
- 81 objetos de código recuperados, incluindo classes, funções e lambdas.

## Funcionamento

`AreaSelector` implementa uma janela transparente arrastável e redimensionável para escolher a região da tela. `GPOFishingMacro` reúne interface, configurações e automação. A interface usa Tkinter; a captura usa MSS; o processamento usa NumPy. `keyboard`, `pynput` e APIs Win32 recebem atalhos e enviam eventos de teclado/mouse.

O programa lê/grava `GPOsettings.json` ao lado do executável. Os atalhos padrão são F1 para iniciar/parar, F2 para mudar a área e F3 para sair. Há teclas configuráveis para vara, outro item e fruta, tolerâncias de cor e ganhos proporcional/derivativo.

O ciclo equipa os itens e lança a vara (`cast_rod`), aguarda a indicação visual de peixe e captura a região escolhida. A função `find_color_positions` cria máscaras por canais de cor e encontra os extremos horizontais. No minigame, o programa examina azul, cinza e branco; identifica seções sem azul e calcula a posição da maior seção. Usa o erro em relação à posição branca e sua variação para decidir quando manter ou soltar o botão esquerdo. O ciclo inclui esperas, tratamento de exceções, relançamento após timeout e contador de ciclos de pesca.

`perform_auto_buy` automatiza a compra de iscas por pontos de clique configurados. `perform_store_fruit` automatiza guardar frutas. `cast_rod` também pode selecionar isca automaticamente. Essas rotinas dependem da posição da interface do jogo e de configurações do usuário.

O contador de “peixes capturados” se baseia no término visual/timeout do ciclo; esta análise não demonstra confirmação do inventário do jogo.

## Comportamento adicional confirmado

Na ausência de `GPOsettings.json`, `main` mostra um diálogo de termos. Se aceito, chama `auto_subscribe_to_youtube`: abre `https://www.youtube.com/@AsphaltCake?sub_confirmation=1`, procura a janela do navegador, tenta colocá-la em primeiro plano, envia Tab/Enter e fecha a aba com Ctrl+W. Trata-se de uma tentativa de inscrição automatizada, cujo sucesso não foi verificado.

O texto de termos atribui o programa a AsphaltCake e pede crédito ao compartilhar/modificar. Isso é conteúdo encontrado no arquivo, não uma instrução do usuário nem prova independente de autoria. A declaração interna de que o programa é seguro também não equivale a uma verificação de segurança. Nenhuma licença foi inferida ou adicionada.

Não há importação direta de um cliente HTTP no módulo principal; isso não prova ausência de comunicação ou de outros comportamentos nas dependências. Não foi feita auditoria integral de DLLs e bibliotecas.

## Arquivos

- `main.pyc`: bytecode do módulo principal, com cabeçalho para Python 3.14; preservado para análise, não para execução.
- `disassembly.txt`: desmontagem recursiva completa, com linhas originais registradas e instruções Python 3.14.
- `functions.json`: nomes, argumentos, referências e constantes simples de cada objeto de código. Tuplas e constantes complexas aparecem na desmontagem.
- `archive_inventory.json`: inventário do contêiner PyInstaller.
- `tools/analyze.py`: extrai e inspeciona novamente o executável sem importá-lo ou executá-lo.

## Reprodução

Com Python 3.14, em ambiente isolado:

```bash
python3.14 tools/analyze.py '/caminho/para/macro.exe' ./resultado
```

O analisador valida o hash do arquivo recebido e inspeciona somente o módulo principal. Ler objetos marshal de arquivos não confiáveis deve ser feito em ambiente descartável. Não use `python main.pyc`: isso executaria o macro.

## Limites e validação

Foram extraídas 997 entradas do arquivo PyInstaller e o módulo principal foi decodificado com Python 3.14. A desmontagem foi gerada recursivamente sem executar os objetos de código. Não há testes funcionais no Roblox/Windows, reconstrução completa da GUI ou código-fonte integral descompilado. Bibliotecas e o executável original não são redistribuídos neste pacote.
