-- MERCADO BOM BAIRRO | 32 EXERCICIOS DE SQLITE
-- Use o banco importado de 01_mercado.sql ou mercado.db.
-- Este arquivo contem somente enunciados. Escreva e execute uma resposta por vez.
-- As respostas estao em 03_gabarito.sql, com os mesmos identificadores E01..E32.
-- Todos os exercicios sao de leitura: nao alteram os dados do banco.
--
-- CONVENCOES IMPORTANTES
-- 1. Dinheiro fica em centavos inteiros. Divida por 100.0 para exibir reais.
-- 2. Receita/faturamento considera somente vendas com status = 'CONCLUIDA'.
--    As views vw_itens_venda e vw_vendas_resumo tambem incluem canceladas.
-- 3. O total liquido do item e quantidade * preco_unitario_centavos,
--    arredondado ao centavo, menos desconto_centavos. Use as views: elas
--    aplicam o arredondamento com milessimos inteiros, sem imprecisao REAL.
-- 4. Datas usam texto ISO: YYYY-MM-DD ou YYYY-MM-DD HH:MM:SS.
--    Para meses, prefira inicio inclusivo e primeiro dia seguinte exclusivo.
-- 5. Nao some quantidades de UN com KG. Agregue por produto ou unidade.
-- 6. Uma venda pode ter varios itens E varios pagamentos. Unir as duas
--    tabelas diretamente multiplica linhas e pode inflar os valores.
-- 7. O estoque e um retrato fixo em 2026-09-30, nao um saldo em tempo real.

-- E01: Primeira consulta.
-- Liste id, codigo, nome e preco de venda em reais dos primeiros 10 produtos,
-- em ordem crescente de id.
-- Dica: SELECT escolhe colunas; ORDER BY ordena; LIMIT limita linhas.


-- E02: Filtros combinados.
-- Liste os produtos ativos cujo preco de venda esteja entre R$ 10 e R$ 25,
-- incluindo os dois limites. Mostre id, nome, unidade e preco em reais.
-- Ordene do menor para o maior preco, usando id para desempatar.
-- Dica: combine ativo = 1 com BETWEEN; os valores armazenados sao centavos.


-- E03: Busca parcial de texto.
-- Liste id e nome dos produtos cujo nome contenha 'arroz', ordenados por nome.
-- Dica: LIKE usa % como curinga; 'arroz' nao possui letras acentuadas.


-- E04: Informacao ausente.
-- Liste id, nome e cidade dos clientes sem email, em ordem crescente de id.
-- Dica: para testar ausencia, use IS NULL; comparar com = NULL nao funciona.


-- E05: Ordenacao e limite.
-- Mostre os 5 produtos mais caros, com nome e preco em reais.
-- Em caso de precos iguais, use o menor id primeiro.
-- Dica: DESC ordena do maior para o menor; acrescente um segundo criterio.


-- E06: Intervalo de datas.
-- Liste id, loja_id, data_venda e canal das vendas concluidas de junho de 2026.
-- Ordene por data_venda e id.
-- Dica: use data_venda >= '2026-06-01' e data_venda < '2026-07-01'.


-- E07: Resumo do cadastro.
-- Para os produtos ativos, calcule quantidade de produtos, menor preco,
-- maior preco e preco medio. Exiba os valores monetarios em reais.
-- Dica: COUNT, MIN, MAX e AVG resumem varias linhas em uma unica linha.


-- E08: Agrupamento e filtro de grupos.
-- Para cada categoria_id com pelo menos 8 produtos ativos, mostre a quantidade
-- desses produtos e seu preco medio em reais. Ordene por categoria_id.
-- Dica: WHERE filtra produtos antes de agrupar; HAVING filtra os grupos.


-- E09: Relacionamentos obrigatorios.
-- Liste id e nome do produto, nome da categoria, nome da marca e preco em reais.
-- Ordene por categoria e produto, usando id para desempatar.
-- Dica: produtos possui categoria_id e marca_id; use dois INNER JOINs.


-- E10: Relacionamento opcional.
-- Liste as primeiras 20 vendas concluidas, por id, com loja, data, nome do
-- cliente e total em reais. Quando cliente_id for NULL, exiba 'Nao identificado'.
-- Dica: a loja usa INNER JOIN; o cliente usa LEFT JOIN e COALESCE.
-- A view vw_vendas_resumo fornece exatamente uma linha por venda.


-- E11: Clientes sem compras usando LEFT JOIN.
-- Liste id e nome dos clientes que nunca tiveram uma venda concluida.
-- Ordene por id. Clientes que tenham somente vendas canceladas tambem entram.
-- Dica: coloque o filtro de status no ON e teste se o id da venda ficou NULL.


-- E12: Relacionamento muitos para muitos.
-- Liste os produtos oferecidos por pelo menos 2 fornecedores: id, produto,
-- quantidade de fornecedores e menor/maior custo ofertado em reais.
-- Ordene pela quantidade de fornecedores decrescente e depois pelo id.
-- Dica: passe pela tabela produto_fornecedores; agrupe por produto e use HAVING.


-- E13: Faturamento e ticket medio por loja.
-- Para cada loja com vendas concluidas, mostre nome, quantidade de vendas,
-- faturamento liquido e ticket medio em reais, do maior faturamento ao menor.
-- Dica: use vw_vendas_resumo; cada linha ja representa uma venda inteira.


-- E14: Clientes com maior gasto.
-- Liste clientes identificados que gastaram mais de R$ 1.000 em vendas
-- concluidas. Mostre id, nome, quantidade de vendas e gasto total em reais.
-- Ordene pelo gasto decrescente e depois pelo id.
-- Dica: agrupe a view de resumo por cliente; filtre SUM com HAVING.


-- E15: Produtos com maior receita.
-- Mostre os 10 produtos com maior receita liquida em vendas concluidas.
-- Inclua id, produto, unidade, quantidade vendida, quantidade de vendas
-- distintas e receita em reais. Desempate a receita pelo menor id.
-- Dica: vw_itens_venda fornece o total liquido por item; COUNT(DISTINCT ...)
-- conta vendas, e a quantidade fica separada por produto e sua unidade.


-- E16: Descontos por canal.
-- Para cada canal das vendas concluidas, mostre quantidade de vendas,
-- valor bruto, descontos e receita liquida em reais. Calcule tambem a taxa
-- de desconto: 100 * descontos / valor bruto, com duas casas decimais.
-- Ordene pelo canal.
-- Dica: use SUM na view de resumo; NULLIF evita divisao por zero.


-- E17: Uma venda, varios pagamentos.
-- Liste as vendas concluidas com 2 ou mais registros de pagamento.
-- Mostre id da venda, quantidade de pagamentos, total da venda e total pago
-- em reais. Ordene por id da venda.
-- Dica: agregue pagamentos por venda em uma subconsulta e so depois una ao
-- resumo de vendas. Nao una itens_venda diretamente aos pagamentos.


-- E18: Receita recebida por forma de pagamento.
-- Para cada forma usada em vendas concluidas, mostre nome, quantidade de
-- vendas distintas e total recebido em reais. Ordene pelo total decrescente
-- e depois pelo nome. Uma venda dividida entre formas aparece em cada forma.
-- Dica: una pagamentos, formas_pagamento e vendas; nao precisa dos itens.


-- E19: Produtos nunca vendidos usando NOT EXISTS.
-- Liste id, codigo e nome dos produtos que nunca participaram de uma venda
-- concluida, em ordem de id. Produtos apenas em vendas canceladas entram.
-- Dica: correlacione produtos com itens_venda e vendas dentro de NOT EXISTS.


-- E20: Clientes de mais de um canal usando EXISTS.
-- Liste id e nome dos clientes que tenham pelo menos uma venda concluida
-- no canal LOJA e pelo menos uma no canal DELIVERY. Ordene por id.
-- Dica: use dois EXISTS correlacionados pelo cliente, um para cada canal.


-- E21: Comparacao com a media da propria categoria.
-- Liste os produtos ativos cujo preco seja maior que a media dos produtos
-- ativos da MESMA categoria. Mostre id, nome, categoria e preco em reais.
-- Ordene por categoria, preco decrescente e id.
-- Dica: a subconsulta de AVG deve usar o categoria_id do produto externo.


-- E22: Classificacao com CASE.
-- Separe as vendas concluidas em faixas de valor liquido: 'Ate R$ 49,99',
-- 'De R$ 50 a R$ 149,99' e 'A partir de R$ 150'. Mostre a quantidade de
-- vendas e a receita em reais de cada faixa existente, nessa ordem.
-- Dica: CASE testa o total em centavos; agrupe pela classificacao criada.


-- E23: Primeira CTE.
-- Calcule, para cada mes de janeiro a setembro de 2026, quantidade de vendas
-- concluidas, receita e ticket medio em reais. Ordene cronologicamente.
-- Dica: WITH pode nomear um resumo mensal; strftime('%Y-%m', data_venda)
-- extrai o mes. Divida receita por quantidade para obter o ticket medio.


-- E24: Necessidade de reposicao.
-- No retrato de 2026-09-30, liste os produtos com quantidade_atual menor que
-- quantidade_minima. Mostre loja, produto, unidade, quantidade atual,
-- quantidade minima e quantidade necessaria para atingir o minimo.
-- Ordene por loja e produto, usando produto_id para desempatar.
-- Dica: vw_estoque_detalhado ja traz os nomes e o indicador precisa_repor.


-- E25: Margem bruta por categoria.
-- Para cada categoria com vendas concluidas, mostre receita liquida,
-- custo dos produtos vendidos e margem bruta em reais. Mostre tambem a
-- margem percentual: 100 * (receita - custo) / receita, com duas casas.
-- Ordene pela margem em reais decrescente e depois pela categoria.
-- Dica: use total_centavos e custo_total_centavos de vw_itens_venda.
-- A margem bruta nao desconta salarios, aluguel nem outras despesas.


-- E26: Ranking dentro de cada categoria.
-- Mostre os produtos nas 3 primeiras posicoes de receita liquida de cada
-- categoria, usando apenas vendas concluidas. Inclua categoria, produto,
-- receita em reais e posicao. Produtos empatados dividem a mesma posicao;
-- a proxima posicao nao deve ser pulada. Ordene por categoria, posicao e id.
-- Dica: agregue por produto, aplique DENSE_RANK com PARTITION BY categoria,
-- e filtre a posicao em uma consulta externa. Pode haver mais de 3 produtos.


-- E27: Comparacao com o mes anterior.
-- Para cada loja e mes com vendas concluidas de janeiro a setembro de 2026,
-- mostre receita, receita do mes anterior disponivel e variacao em reais.
-- No primeiro mes de cada loja, os dois ultimos valores devem ficar NULL.
-- Ordene por loja e mes.
-- Dica: primeiro agregue por loja/mes; LAG procura a receita anterior dentro
-- de cada loja. Nao converta o primeiro NULL em zero.


-- E28: Receita acumulada.
-- Para cada loja e mes com vendas concluidas de janeiro a setembro de 2026,
-- mostre receita mensal e receita acumulada desde janeiro, em reais.
-- Ordene por loja e mes.
-- Dica: depois de agrupar por mes, use SUM(...) OVER com PARTITION BY loja,
-- ORDER BY mes e ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW.


-- E29: Recencia, frequencia e valor dos clientes.
-- Para TODOS os clientes, mostre id, nome, data da ultima venda concluida,
-- dias desde essa venda ate 2026-09-30, quantidade de vendas concluidas e
-- gasto total em reais no periodo de janeiro a setembro de 2026.
-- Quem nao comprou deve ter quantidade/gasto zero e ultima data/dias NULL.
-- Ordene pelo gasto decrescente e depois pelo id.
-- Dica: agregue vendas concluidas em uma CTE e faca LEFT JOIN com clientes.
-- julianday('2026-09-30') - julianday(date(...)) calcula os dias corridos.


-- E30: Desempenho dos fornecedores.
-- Para TODOS os fornecedores, mostre id, nome, quantidade de pedidos
-- recebidos, pendentes e cancelados, e prazo medio REAL de recebimento em
-- dias (duas casas). Calcule o prazo somente para pedidos recebidos.
-- Fornecedor sem pedido recebido deve ter prazo medio NULL. Ordene por id.
-- Dica: LEFT JOIN preserva fornecedores; SUM(CASE ...) conta cada status;
-- AVG(CASE ...) ignora os NULLs de pedidos que nao foram recebidos.


-- E31: Conferencia do estoque.
-- Confira cada par loja/produto do retrato de 2026-09-30: quantidade inicial
-- + quantidade de compras RECEBIDAS no periodo - quantidade de vendas
-- CONCLUIDAS no periodo deve ser igual a quantidade atual registrada.
-- Retorne somente divergencias maiores que 0,000001, com loja, produto,
-- unidade, saldo calculado, saldo registrado e diferenca (registrado - calculado).
-- Considere movimentos de 2026-01-01 ate antes de 2026-10-01. Ordene por loja
-- e produto. Resultado esperado no banco original: nenhuma linha.
-- Dica: agregue entradas e saidas SEPARADAMENTE por loja/produto antes de
-- uni-las a estoques; datas de entrada sao data_recebimento.


-- E32: Reconciliacao de pagamentos.
-- Confira TODAS as vendas: uma CONCLUIDA deve ter pagamentos cuja soma seja
-- igual ao seu total liquido; uma CANCELADA deve ter total pago zero.
-- Retorne somente divergencias, com id da venda, status, quantidade de
-- pagamentos, valor esperado, valor pago e diferenca (pago - esperado),
-- com dinheiro em reais. Ordene pelo id. Resultado esperado: nenhuma linha.
-- Dica: agregue pagamentos por venda antes do JOIN. Use CASE para determinar
-- o valor esperado conforme o status e COALESCE para pagamentos ausentes.
-- Compare os totais em centavos inteiros; converta para reais so na exibicao.
