# API-criação-blockchain

API criada na matéria de blockchain e aplicações descentralizadas, o objetivo do trabalho era criar uma API que pudesse criar uma blockchain.

Rotas:

```http
  POST /transactions/create
```
irá criar uma transação

```http
  GET /transactions/mempool
```
irá retornar o mempool

```http
  GET /mine
```
irá minerar um novo bloco

```http
  GET /chain
```
irá mostrar a cadeia atual de blocos

```http
  POST /nodes/register
```
irá registrar os nós

```http
  GET /nodes/resolve
```
irá resolver os conflitos na blockchain
