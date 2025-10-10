# MEUS MANOS!!!!!!!!!!!

O Evolutium é uma ia que verifica mais de 600 ativos da bolsa e escolhe a melhor opção, alem de criar uma conta com seu saldo e ativos ja comprados para voce
não se perder, ela tambem verifica qual dos ativos seria bom para vender e cria relatorios, se quiserem dou uma explicação melhor de como ela funciona, para finalizar
caso queriam um ativo que nao esta na lista do config.py é so me falar que eu adiciono para todos.

Este guia irá ajudá-lo a configurar e executar o aplicativo Evolutium AI no seu próprio computador.

Pré-requisitos:

Python: Certifique-se de ter o Python instalado.

Git: Você precisará do Git para clonar o repositório da pra baixalo em git-scm.com.

Visual Studio: e aqui que a magica acontece certifique-se de telo.

--------------------------------------------------------------------------------------------------------------------------------

Passo 1: 

Crie uma pasta e a abra no visual studio depois abra seu terminal (NO VISUAL STUDIO (CANTO SUPERIOR ESQUERDO)) e clone o repositório do GitHub:

git clone https://github.com/MarcosPFA15/Evolutium.git

Depois, entre na pasta do projeto:

cd Evolutium/evolutium_project

--------------------------------------------------------------------------------------------------------------------------------

Passo 2:

Instale as Dependências:
O arquivo requirements.txt contém todas as bibliotecas que o projeto precisa. Instale-as com um único comando:

pip install -r requirements.txt

caso pip não seja reconhecido utilize: 

py -m pip install -r requirements.txt

e caso tambem não funciona voce precisa corrigir o py com:

py -m ensurepip --upgrade

com upgrade terminado é so instalar os requirements com o

py -m pip install -r requirements.txt

---------------------------------------------------------------------------------------------------------------------------------

Passo 3: Preparar o Banco de Dados
Este comando cria o banco de dados local (db.sqlite3) com todas as tabelas necessárias.

python manage.py migrate

--------------------------------------------------------------------------------------------------------------------------------

Passo 4: Executar o Aplicativo!
Agora você está pronto para iniciar o servidor local:

python manage.py runserver

O terminal mostrará um link, abra este link no seu navegador com ctrl + click normalmente ele é assim: http://###.#.#.#:####/ so que as tags são numeros.

Apos isso abra um novo terminal e execute: 

python manage.py rqworker default

--------------------------------------------------------------------------------------------------------------------------------

Qualquer bug so me reportar :D

Recomendo voces usarem uma vez por dia e obrigado por baixar

!!
ATENÇÃO QUANDO O BOT COMEÇAR A ANALISAR VAI DEMORAR MESMO (10-15MIN) POREM NAO RECARREGUE A PAGINA
!!

Disclaimer: Não me responsabilizo por perdas, use por sua conta e risco.
