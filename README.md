# MEUS MANOS!!!!!!!!!!!

O Evolutium é uma ia que verifica 600+ de ativos e escolhe a melhor opção, alem de criar uma conta com seu saldo e ativos ja comprados para voce
não se perder, ela tambem verifica qual dos ativos seria bom para vender, se quiserem dou uma explicação melhor de como ela funciona, pra finalizar
caso queriam um ativo que nao esta na lista do config.py é so me falar que eu adiciono para todos.

Como Executar o Evolutium Ia Localmente?

Este guia irá ajudá-lo a configurar e executar o aplicativo Evolutium AI no seu próprio computador.

Pré-requisitos:

Python: Certifique-se de ter o Python instalado.
Git: Você precisará do Git para clonar o repositório da pra baixalo em git-scm.com.
Visual Studio: e aqui que a magica acontece Certifique-se de telo.

--------------------------------------------------------------------------------------------------------------------------------

Passo 1: 

Baixar o Projeto: Abra seu terminal (NO VISUAL STUDIO) e clone o repositório do GitHub:
git clone https://github.com/MarcosPFA15/Evolutium.git
Depois, entre na pasta do projeto:
cd Evolutium/evolutium_project

--------------------------------------------------------------------------------------------------------------------------------

Passo 2: Configurar o Ambiente
Crie um Ambiente Virtual:

python -m venv venv
venv\Scripts\activate  # No Windows

source venv/bin/activate  # No macOS/Linux

Instale as Dependências:
O arquivo requirements.txt contém todas as bibliotecas que o projeto precisa. Instale-as com um único comando:

pip install -r requirements.txt

---------------------------------------------------------------------------------------------------------------------------------

Passo 3: Preparar o Banco de Dados
Este comando cria o banco de dados local (db.sqlite3) com todas as tabelas necessárias.

python manage.py migrate

--------------------------------------------------------------------------------------------------------------------------------

Passo 4: Executar o Aplicativo!
Agora você está pronto para iniciar o servidor local:

python manage.py runserver

O terminal mostrará um link abra este link no seu navegador para acessar o aplicativo.
