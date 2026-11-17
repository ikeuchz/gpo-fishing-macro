# GPO Fishing — ikeuchz

Macro de pesca para Grand Piece Online com uma interface nova sobre o **motor do primeiro executável fornecido**.

A implementação experimental anterior foi substituída. O código de pesca agora é o bytecode Python 3.14 recuperado daquele arquivo, preservado integralmente em `gpo_macro/assets/original_core.marshal`. A interface em `gpo_macro/app.py` usa a classe original por herança: não redefine o loop, a procura de cores, o controlador PD, o lançamento da vara ou as rotinas de iscas/frutas. Isso preserva a implementação original, mas não substitui a validação dentro do jogo.

## Download e uso

[Baixar o executável Windows 64 bits](https://github.com/ikeuchz/gpo-fishing-macro/raw/refs/heads/main/GPO-Fishing-Macro.exe)

1. Abra o jogo em modo janela ou sem bordas. O painel fica no topo; **Compactar / expandir** reduz a janela para observar a pesca sem Alt+Tab.
2. Em **Área / salvar área**, mova e redimensione a caixa verde para incluir o minigame inteiro, **incluindo o peixe branco que pode estar à esquerda da barra**. Clique novamente em **Área / salvar área** para salvar. A seleção e a moldura são as originais.
3. Configure **Rod Key** com a tecla real da vara no inventário e **Not Rod Key** com outro item. Na captura enviada, a vara aparece no slot **5** e a espada no **4**: confira esses valores no seu jogo. Não deixe a tecla padrão `1` se sua vara estiver no `5`.
4. Use **Iniciar em 3 segundos** e volte ao jogo, ou configure uma combinação como `CTRL+G` em **Atalhos**. Padrões para instalação nova: INSERT para iniciar/parar, HOME para área/salvar e END para sair.
5. Para interromper, use **Parar / cancelar** ou o atalho configurado.

**O fluxo original foi restaurado:** iniciar equipa os itens e lança a vara; o loop aguarda a fisgada, controla o minigame, conclui o ciclo e relança conforme os tempos originais. Não é mais a versão manual experimental anterior. As setas exibidas, cores, ganhos, timeouts, seleção de isca, compra e armazenamento seguem os métodos originais. Os controles completos permanecem disponíveis na parte rolável do painel.

Os ajustes são salvos no arquivo original **GPOsettings.json**, ao lado do executável. Pode reutilizar esse arquivo do primeiro macro. O antigo `settings.json` da implementação experimental não é usado, para evitar aplicar outro formato de configurações.

A inicialização desta interface entra diretamente na classe de pesca; não chama o antigo launcher nem sua rotina de abertura/inscrição no YouTube. As definições originais permanecem no recurso recuperado, mas não são chamadas pelo novo launcher.

Há um relato de bloqueio pelo Defender da versão experimental anterior, ainda sem diagnóstico concluído. O uso do motor original e as mudanças de interface não comprovam que o alerta foi resolvido. Não desative a proteção para executar o arquivo.

## Executar pelo código

Requer **Python 3.14 de 64 bits no Windows**, com Tkinter. Essa versão é necessária para ler o bytecode original.

```powershell
py -3.14 -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python run.py
```

NumPy 2.3.5, MSS 10.1.0 e keyboard 0.13.5 correspondem às versões identificadas no arquivo original. A interface e o adaptador são código-fonte editável; o motor recuperado é bytecode, não uma recuperação integral do código-fonte original.

## Gerar o executável

```powershell
.venv\Scripts\python -m pip install -r requirements-build.txt
.venv\Scripts\python -m PyInstaller --clean --noconfirm --onefile --windowed --name GPO-Fishing-Macro --collect-all mss --hidden-import keyboard --hidden-import numpy --hidden-import win32api --hidden-import win32con --hidden-import win32gui --collect-all pynput --icon gpo_macro/assets/app.ico --add-data "gpo_macro/assets;gpo_macro/assets" run.py
```

O arquivo é gerado em `dist/GPO-Fishing-Macro.exe`. O workflow **Windows executable**, na aba Actions, também compila e disponibiliza o artefato para download.

## Verificação

```powershell
.venv\Scripts\python -m unittest discover -s tests -v
```

Os testes verificam a integridade exata do recurso original, a identidade dos métodos de pesca herdados, a busca de cores, a sequência original de teclas/cliques sem enviar entradas reais e a construção da interface no Windows. Não afirmam sucesso no Roblox.

A [compilação verificada no Windows](https://github.com/ikeuchz/gpo-fishing-macro/actions/runs/44160370209) também abriu o executável final, identificou sua janela e o fechou normalmente. O recurso do motor dentro do `.exe` foi conferido contra o bytecode extraído do primeiro arquivo. Isso não equivale a um teste de pesca no Roblox.
