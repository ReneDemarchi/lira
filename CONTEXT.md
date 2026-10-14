# LIRA

Gerenciador ágil de projetos (estilo Jira, mais simples) onde equipes organizam e acompanham tarefas.

## Language

### Pessoas e acesso

**Usuário**:
Pessoa com conta no LIRA, identificada por e-mail único. Não possui papel por si só; todo poder vem das suas Participações.
_Avoid_: Conta, tipo de usuário

**Participação**:
Vínculo entre um Usuário e um Projeto, carregando o Papel daquele Usuário naquele Projeto. Um Usuário pode ter N Participações com Papéis diferentes.
_Avoid_: Membro, vínculo, permissão do usuário

**Papel**:
Nível de poder de um Usuário dentro de um Projeto: Administrador, Coordenador ou Colaborador. Existe apenas dentro de uma Participação, nunca globalmente.
_Avoid_: Tipo de usuário, perfil, cargo

**Administrador**:
Papel com controle total do Projeto; é o único que gerencia Participações (adicionar, remover, trocar Papel). Quem cria um Projeto se torna seu Administrador. Um Projeto pode ter vários, mas nunca menos de um.

**Coordenador**:
Papel que gerencia Tarefas e Etiquetas do Projeto.

**Colaborador**:
Papel que visualiza o Projeto e só altera o Estado das Tarefas das quais é Responsável.

### Trabalho

**Projeto**:
Agrupador de Tarefas, Etiquetas e Participações, identificado por um nome. Qualquer Usuário pode criar um; só seu Administrador o edita ou exclui, e a exclusão leva tudo junto.

**Tarefa**:
Unidade de trabalho que pertence a exatamente um Projeto.
_Avoid_: Issue, ticket, card

**Responsável**:
O único Usuário com Participação no Projeto encarregado de uma Tarefa, qualquer que seja seu Papel. Uma Tarefa pode estar sem Responsável.
_Avoid_: Assignee, atribuído

**Comentário**:
Texto escrito por um Usuário em uma Tarefa. Permanece mesmo se o autor deixar o Projeto.

**Etiqueta**:
Rótulo que pertence a um Projeto e classifica Tarefas; uma Tarefa pode ter várias. Todo Projeto nasce com Epic, História, Bug e Issue.
_Avoid_: Tag, label, tipo de tarefa

**Prioridade**:
Urgência de uma Tarefa: Baixa, Média, Alta ou Urgente. Lista fixa; Tarefa nova começa em Média.

**Estado**:
Etapa de uma Tarefa: A fazer, Fazendo ou Feito. Lista fixa; Tarefa nova começa em A fazer.
_Avoid_: Status, coluna

**Board**:
Visão de um Projeto com uma coluna por Estado, onde Tarefas são movidas entre colunas.
_Avoid_: Quadro, kanban

**Data limite**:
Data opcional até a qual uma Tarefa deve chegar a Feito.
_Avoid_: Prazo, deadline

**Atrasada**:
Condição de uma Tarefa cuja Data limite já passou e que não está em Feito. Não é um Estado.
