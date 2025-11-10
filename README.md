# ​Evolutium - O Agente de Análise de Ativos com IA #

​(Licença Proprietária - All Rights Reserved)

## ​🎯 O que é o Evolutium? ##

​O Evolutium é uma plataforma de IA projetada para analisar o mercado de ações, atualmente, ele monitora mais de 600 ativos da bolsa e utiliza inteligência artificial para:

​Selecionar as melhores oportunidades de compra.

​Sugerir quais ativos em carteira devem ser vendidos.

​Criar relatórios de performance.

​Manter uma conta de usuário virtual com saldo e ativos para fácil gerenciamento.

Todas essas escolhas são baseadas em dados e informações de cada ativo, além disso o bot monitora as últimas notícias de empresa.

## ​🚀 O Futuro do Evolutium: ##

​O nome "Evolutium" não foi escolhido atoa, a versão atual é apenas um bot de análise, mas a versão final é muito mais ambiciosa.

​O verdadeiro Evolutium será um agente de IA meta-adaptativo, a ideia é que ele não apenas analise ativos, mas que ele seja capaz de:

​Aprender com os Erros: Analisar os relatórios de performance e os resultados das decisões tomadas por todos os usuários que utilizam o evolutium.

​Ser Auto-Corretivo: Identificar falhas em sua própria lógica ou estratégia de análise (ex: "Minha sugestão de venda para o ativo X foi prematura").

​Evoluir Autonomamente: Alterar seu próprio código-fonte para implementar melhorias, corrigir estratégias e lançar novas atualizações de forma autônoma.

​Esta é a minha roadmap final do projeto para criar uma IA que verdadeiramente "evolui".

## ​🛠️ Guia de Instalação Local ##

​Este guia irá ajudá-lo a configurar e executar o aplicativo Evolutium AI no seu próprio computador.

​Pré-requisitos:

​Python: Certifique-se de ter o Python 3.x instalado.

​Git: Você precisará do Git para clonar o repositório. (Disponível em git-scm.com).

​Editor de Código: Recomendo fortemente o Visual Studio Code.

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

com upgrade terminado é so instalar os requirements e depois do requiremets autaliza a api com o

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


--------------------------------------------------------------------------------------------------------------------------------

## ​⚠️ Atenção e Boas Práticas ##
​!! IMPORTANTE !!
Quando o bot iniciar a análise pela primeira vez, o processo vai demorar (cerca de 10 a 15 minutos), pois ele está processando centenas de ativos NÃO RECARREGUE A PÁGINA durante esse tempo.

​Uso Recomendado: executar a análise uma vez por dia.

​Salvamento: Não se preocupe em salvar pois o seu próprio computador grava todas as suas informações automaticamente no banco de dados.

​Disclaimer: Este é um projeto de portfólio criado por min para demonstração técnica, não me responsabilizo por perdas financeiras, use por sua conta e risco.

## ​🐛 Bugs ou Dúvidas? ##
​Encontrou um problema ou tem uma sugestão? Abra uma "Issue" aqui no repositório do GitHub.

--------------------------------------------------------------------------------------------------------------------------------