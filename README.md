# Valoriza

# Padronização da API

Este documento define os padrões e convenções utilizados no desenvolvimento da API do projeto.

O objetivo é garantir **consistência, previsibilidade e facilidade de manutenção**, permitindo que diferentes integrantes do projeto implementem e consumam a API seguindo as mesmas regras.

---

## Sumário

* [1. Objetivo](#1-objetivo)
* [2. Estrutura da API](#2-estrutura-da-api)
* [3. Versionamento](#3-versionamento)
* [4. Nomenclatura](#4-nomenclatura)
* [5. Métodos HTTP](#5-métodos-http)
* [6. Status HTTP](#6-status-http)
* [7. Formato das respostas](#7-formato-das-respostas)
* [8. Tratamento de erros](#8-tratamento-de-erros)
* [9. Autenticação](#9-autenticação)
* [10. Validação de dados](#10-validação-de-dados)
* [11. Paginação](#11-paginação)
* [12. Filtros e ordenação](#12-filtros-e-ordenação)
* [13. Datas e horários](#13-datas-e-horários)
* [14. IDs](#14-ids)
* [15. Documentação dos endpoints](#15-documentação-dos-endpoints)
* [16. Exemplo de endpoint](#16-exemplo-de-endpoint)
* [17. Organização do código](#17-organização-do-código)
* [18. Boas práticas](#18-boas-práticas)
* [19. Checklist para novos endpoints](#19-checklist-para-novos-endpoints)
* [20. Responsabilidades](#20-responsabilidades)

---

# 1. Objetivo

A API deve seguir padrões consistentes em relação a:

* Estrutura das URLs;
* Nomenclatura de recursos;
* Métodos HTTP;
* Códigos de status;
* Formato das respostas;
* Tratamento de erros;
* Autenticação;
* Validação de dados;
* Paginação;
* Filtros;
* Documentação.

Qualquer novo endpoint deve seguir as regras descritas neste documento.

Caso seja necessário criar uma exceção, ela deve ser discutida e documentada antes da implementação.

---

# 2. Estrutura da API

Os endpoints devem seguir a seguinte estrutura:

```text
/api/v1/{recurso}
```

Exemplos:

```text
/api/v1/usuarios
/api/v1/usuarios/{id}
/api/v1/produtos
/api/v1/produtos/{id}
/api/v1/conversas
/api/v1/conversas/{id}/mensagens
```

A API deve utilizar recursos, e não ações, nas URLs.

### Preferir

```text
GET /api/v1/usuarios
POST /api/v1/usuarios
```

### Evitar

```text
GET /api/v1/getUsuarios
POST /api/v1/criarUsuario
```

O comportamento da operação deve ser definido pelo método HTTP.

---

# 3. Versionamento

A API deve ser versionada utilizando o prefixo:

```text
/api/v1
```

Exemplo:

```text
GET /api/v1/usuarios
```

Caso futuramente seja necessário realizar uma alteração incompatível com a versão atual, uma nova versão poderá ser criada:

```text
/api/v2/usuarios
```

A criação de uma nova versão deve ser utilizada somente quando uma alteração incompatível realmente exigir isso.

---

# 4. Nomenclatura

## 4.1 Recursos

Os recursos devem utilizar nomes no plural.

### Correto

```text
/usuarios
/produtos
/conversas
/mensagens
```

### Evitar

```text
/usuario
/produto
/conversa
/mensagem
```

---

## 4.2 IDs

IDs devem ser utilizados diretamente na URL:

```text
/api/v1/usuarios/{id}
```

Exemplo:

```text
/api/v1/usuarios/123
```

---

## 4.3 Query Parameters

Parâmetros de consulta devem utilizar nomes descritivos.

Exemplo:

```text
/api/v1/usuarios?page=1&limit=20
```

---

# 5. Métodos HTTP

| Método   | Utilização                              |
| -------- | --------------------------------------- |
| `GET`    | Buscar dados                            |
| `POST`   | Criar um recurso                        |
| `PUT`    | Substituir/atualizar um recurso inteiro |
| `PATCH`  | Atualizar parcialmente um recurso       |
| `DELETE` | Remover um recurso                      |

### Exemplos

Buscar usuários:

```http
GET /api/v1/usuarios
```

Buscar um usuário:

```http
GET /api/v1/usuarios/{id}
```

Criar usuário:

```http
POST /api/v1/usuarios
```

Atualizar usuário:

```http
PATCH /api/v1/usuarios/{id}
```

Remover usuário:

```http
DELETE /api/v1/usuarios/{id}
```

---

# 6. Status HTTP

Os endpoints devem utilizar códigos HTTP adequados para representar o resultado da operação.

| Código | Significado           | Utilização                                    |
| ------ | --------------------- | --------------------------------------------- |
| `200`  | OK                    | Requisição executada com sucesso              |
| `201`  | Created               | Recurso criado com sucesso                    |
| `204`  | No Content            | Operação realizada sem conteúdo para retornar |
| `400`  | Bad Request           | Requisição inválida                           |
| `401`  | Unauthorized          | Usuário não autenticado                       |
| `403`  | Forbidden             | Usuário autenticado, mas sem permissão        |
| `404`  | Not Found             | Recurso não encontrado                        |
| `409`  | Conflict              | Conflito com o estado atual do recurso        |
| `422`  | Unprocessable Entity  | Dados enviados não são válidos                |
| `500`  | Internal Server Error | Erro inesperado no servidor                   |

---

# 7. Formato das respostas

As respostas devem seguir um padrão consistente.

## 7.1 Resposta de objeto

Exemplo:

```json
{
  "data": {
    "id": "123",
    "nome": "João",
    "email": "joao@email.com"
  }
}
```

---

## 7.2 Resposta de lista

Exemplo:

```json
{
  "data": [
    {
      "id": "123",
      "nome": "João"
    },
    {
      "id": "456",
      "nome": "Maria"
    }
  ]
}
```

---

## 7.3 Resposta sem conteúdo

Quando a operação não precisar retornar dados, utilizar:

```http
204 No Content
```

Não é necessário enviar um JSON vazio.

---

# 8. Tratamento de erros

Os erros devem seguir um formato único para facilitar o tratamento no aplicativo mobile.

Formato:

```json
{
  "error": {
    "code": "USER_NOT_FOUND",
    "message": "Usuário não encontrado."
  }
}
```

## 8.1 Código do erro

O campo `code` deve ser identificável e consistente.

Exemplos:

```text
USER_NOT_FOUND
INVALID_CREDENTIALS
INVALID_DATA
UNAUTHORIZED
FORBIDDEN
RESOURCE_CONFLICT
INTERNAL_ERROR
```

---

## 8.2 Mensagem

O campo `message` deve apresentar uma descrição compreensível do erro.

Exemplo:

```json
{
  "error": {
    "code": "INVALID_DATA",
    "message": "O campo email deve ser válido."
  }
}
```

---

## 8.3 Erros de validação

Quando houver vários campos inválidos, o erro pode informar quais campos precisam ser corrigidos.

Exemplo:

```json
{
  "error": {
    "code": "INVALID_DATA",
    "message": "Existem campos inválidos.",
    "fields": {
      "email": "Email inválido.",
      "nome": "Nome é obrigatório."
    }
  }
}
```

---

# 9. Autenticação

Endpoints que exigem autenticação devem utilizar o header:

```http
Authorization: Bearer <token>
```

Exemplo:

```http
Authorization: Bearer eyJhbGciOi...
```

Endpoints públicos devem ser explicitamente identificados na documentação.

### Exemplo

```text
POST /api/v1/auth/login
```

Não requer autenticação.

Enquanto:

```text
GET /api/v1/usuarios/me
```

Requer autenticação.

---

# 10. Validação de dados

Toda entrada recebida pela API deve ser validada antes de ser processada.

Devem ser considerados:

* Campos obrigatórios;
* Tipo do dado;
* Tamanho mínimo;
* Tamanho máximo;
* Formato;
* Valores permitidos;
* Relacionamentos entre campos.

Exemplo:

```json
{
  "nome": "João",
  "email": "joao@email.com"
}
```

Se `email` for obrigatório e estiver ausente:

```http
422 Unprocessable Entity
```

```json
{
  "error": {
    "code": "INVALID_DATA",
    "message": "O campo email é obrigatório."
  }
}
```

A validação deve ocorrer no backend mesmo que o aplicativo mobile também realize validações.

---

# 11. Paginação

Endpoints que retornam grandes quantidades de dados devem utilizar paginação.

Formato recomendado:

```text
GET /api/v1/usuarios?page=1&limit=20
```

Onde:

* `page` = página solicitada;
* `limit` = quantidade máxima de itens por página.

A resposta deve informar os dados de paginação.

Exemplo:

```json
{
  "data": [
    {
      "id": "123",
      "nome": "João"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 100
  }
}
```

---

# 12. Filtros e ordenação

Filtros devem ser enviados utilizando query parameters.

Exemplo:

```text
GET /api/v1/usuarios?status=active
```

Múltiplos filtros:

```text
GET /api/v1/usuarios?status=active&role=admin
```

Ordenação:

```text
GET /api/v1/usuarios?sort=nome
```

Ordem decrescente:

```text
GET /api/v1/usuarios?sort=-nome
```

Caso seja necessário utilizar uma convenção diferente, ela deve ser documentada no endpoint.

---

# 13. Datas e horários

Datas devem utilizar um formato padronizado.

Preferencialmente, utilizar ISO 8601.

Exemplo:

```text
2026-09-15T21:30:00Z
```

Ao documentar um campo de data, informar claramente:

* Se representa data ou data/hora;
* Qual timezone é utilizado;
* Se o valor é enviado ou retornado em UTC.

Exemplo:

```json
{
  "createdAt": "2026-09-15T21:30:00Z"
}
```

---

# 14. IDs

Os IDs utilizados pela API devem possuir um formato consistente em todo o projeto.

Exemplo:

```json
{
  "id": "123"
}
```

Ou, caso o projeto utilize UUID:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000"
}
```

A escolha do formato deve ser definida no projeto e mantida de maneira consistente.

---

# 15. Documentação dos endpoints

Todo endpoint implementado deve possuir documentação.

Cada endpoint deve seguir o modelo:

````markdown
## MÉTODO /api/v1/recurso

### Descrição

Descrição do objetivo do endpoint.

### Autenticação

- Requer autenticação: Sim/Não

### Parâmetros

| Nome | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| id | string | Sim | Identificador do recurso |

### Body

```json
{
  "campo": "valor"
}
````

### Resposta — 200

```json
{
  "data": {}
}
```

### Erros

* `400` — Requisição inválida
* `401` — Não autenticado
* `404` — Recurso não encontrado
* `500` — Erro interno

````

---

# 16. Exemplo de endpoint

## GET `/api/v1/usuarios/{id}`

### Descrição

Retorna os dados de um usuário específico.

### Autenticação

Requer autenticação.

### Parâmetros

| Nome | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `id` | string | Sim | Identificador do usuário |

### Exemplo de requisição

```http
GET /api/v1/usuarios/123
Authorization: Bearer <token>
````

### Resposta — 200

```json
{
  "data": {
    "id": "123",
    "nome": "João",
    "email": "joao@email.com"
  }
}
```

### Possíveis erros

#### 401 — Não autenticado

```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Autenticação necessária."
  }
}
```

#### 404 — Usuário não encontrado

```json
{
  "error": {
    "code": "USER_NOT_FOUND",
    "message": "Usuário não encontrado."
  }
}
```

#### 500 — Erro interno

```json
{
  "error": {
    "code": "INTERNAL_ERROR",
    "message": "Ocorreu um erro interno."
  }
}
```

---

# 17. Organização do código

A implementação deve seguir uma estrutura organizada e separada por responsabilidades.

Uma estrutura possível:

```text
src/
├── controllers/
├── services/
├── repositories/
├── models/
├── routes/
├── middlewares/
├── validators/
├── utils/
└── config/
```

### Controllers

Responsáveis por:

* Receber a requisição;
* Extrair os dados;
* Chamar o serviço apropriado;
* Retornar a resposta HTTP.

### Services

Responsáveis pelas regras de negócio.

### Repositories

Responsáveis pelo acesso aos dados/banco de dados.

### Validators

Responsáveis pela validação das entradas.

### Middlewares

Responsáveis por comportamentos que precisam ocorrer antes ou durante o processamento das requisições, como autenticação.

---

# 18. Boas práticas

## 18.1 Não duplicar regras de negócio

Regras de negócio devem ficar nos serviços apropriados e não espalhadas pelos controllers.

---

## 18.2 Não retornar informações desnecessárias

A API deve retornar somente os dados necessários para aquela operação.

---

## 18.3 Não expor informações sensíveis

Nunca retornar:

* Senhas;
* Tokens internos;
* Chaves privadas;
* Credenciais;
* Informações internas do servidor.

---

## 18.4 Manter consistência

Endpoints que possuem comportamentos semelhantes devem seguir estruturas semelhantes.

Por exemplo, evitar que um endpoint retorne:

```json
{
  "data": {}
}
```

e outro endpoint equivalente retorne diretamente:

```json
{}
```

---

## 18.5 Não utilizar mensagens de erro inconsistentes

Evitar:

```json
{
  "message": "Usuário não existe"
}
```

em um endpoint e:

```json
{
  "erro": "User not found"
}
```

em outro.

Todos devem seguir o padrão definido neste documento.

---

# 19. Checklist para novos endpoints

Antes de considerar um endpoint concluído, verificar:

### Estrutura

* [ ] A URL segue `/api/v1/{recurso}`?
* [ ] O recurso está no plural?
* [ ] O endpoint utiliza o método HTTP correto?
* [ ] A nomenclatura segue o padrão do projeto?

### Autenticação

* [ ] Foi definido se o endpoint exige autenticação?
* [ ] A autenticação está sendo validada corretamente?
* [ ] Permissões foram verificadas quando necessário?

### Validação

* [ ] Campos obrigatórios foram definidos?
* [ ] Dados recebidos são validados?
* [ ] Erros de validação seguem o padrão?

### Resposta

* [ ] A resposta segue o formato padrão?
* [ ] O status HTTP está correto?
* [ ] Dados sensíveis não estão sendo retornados?

### Erros

* [ ] Os erros utilizam o formato padrão?
* [ ] O `code` do erro é consistente?
* [ ] A mensagem é clara?

### Documentação

* [ ] O endpoint está documentado?
* [ ] Parâmetros estão documentados?
* [ ] Body está documentado, quando aplicável?
* [ ] Respostas de sucesso estão documentadas?
* [ ] Possíveis erros estão documentados?

---

# 20. Responsabilidades

A implementação da API deve seguir esta documentação independentemente de qual integrante esteja responsável pelo card.

As responsabilidades específicas de cada integrante devem ser definidas nos cards do projeto.

Quando houver colaboração entre integrantes em uma funcionalidade, ambos devem seguir os mesmos padrões definidos neste documento.

Alterações nos padrões da API devem ser comunicadas ao restante da equipe e atualizadas nesta documentação.

---

# Histórico de alterações

| Data       | Alteração                                      | Responsável |
| ---------- | ---------------------------------------------- | ----------- |
| 2026-09-15 | Criação da documentação de padronização da API | Equipe      |

---

## Regra principal

> **Se um novo endpoint não se encaixar naturalmente nos padrões deste documento, a estrutura deve ser discutida antes da implementação.**

A documentação deve evoluir junto com o projeto e permanecer como a fonte de referência para o desenvolvimento da API.
