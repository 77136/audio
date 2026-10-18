-- MERCADO BOM BAIRRO | GABARITO SQLITE
-- Selecione e execute somente o bloco do exercicio desejado.
-- Cada E01..E32 contem exatamente uma instrucao SELECT (com ou sem WITH).
-- Dinheiro permanece em centavos durante calculos e comparacoes.
-- 100.0 converte centavos para reais com divisao decimal.

-- E01: Primeira consulta.
SELECT id, codigo, nome, preco_venda_centavos / 100.0 AS preco_reais
FROM produtos
ORDER BY id
LIMIT 10;

-- E02: Filtros combinados.
SELECT id, nome, unidade, preco_venda_centavos / 100.0 AS preco_reais
FROM produtos
WHERE ativo = 1
  AND preco_venda_centavos BETWEEN 1000 AND 2500
ORDER BY preco_venda_centavos, id;

-- E03: Busca parcial de texto.
SELECT id, nome
FROM produtos
WHERE nome LIKE '%arroz%'
ORDER BY nome, id;

-- E04: Informacao ausente.
SELECT id, nome, cidade
FROM clientes
WHERE email IS NULL
ORDER BY id;

-- E05: Ordenacao e limite.
SELECT nome, preco_venda_centavos / 100.0 AS preco_reais
FROM produtos
ORDER BY preco_venda_centavos DESC, id
LIMIT 5;

-- E06: Intervalo de datas.
SELECT id, loja_id, data_venda, canal
FROM vendas
WHERE status = 'CONCLUIDA'
  AND data_venda >= '2026-06-01'
  AND data_venda < '2026-07-01'
ORDER BY data_venda, id;

-- E07: Resumo do cadastro.
SELECT COUNT(*) AS quantidade_produtos,
       MIN(preco_venda_centavos) / 100.0 AS menor_preco_reais,
       MAX(preco_venda_centavos) / 100.0 AS maior_preco_reais,
       ROUND(AVG(preco_venda_centavos) / 100.0, 2) AS preco_medio_reais
FROM produtos
WHERE ativo = 1;

-- E08: Agrupamento e filtro de grupos.
SELECT categoria_id, COUNT(*) AS quantidade_produtos,
       ROUND(AVG(preco_venda_centavos) / 100.0, 2) AS preco_medio_reais
FROM produtos
WHERE ativo = 1
GROUP BY categoria_id
HAVING COUNT(*) >= 8
ORDER BY categoria_id;

-- E09: Relacionamentos obrigatorios.
SELECT p.id, p.nome AS produto, c.nome AS categoria, m.nome AS marca,
       p.preco_venda_centavos / 100.0 AS preco_reais
FROM produtos AS p
INNER JOIN categorias AS c ON c.id = p.categoria_id
INNER JOIN marcas AS m ON m.id = p.marca_id
ORDER BY c.nome, p.nome, p.id;

-- E10: Relacionamento opcional.
SELECT v.venda_id, l.nome AS loja, v.data_venda,
       COALESCE(c.nome, 'Nao identificado') AS cliente,
       v.total_centavos / 100.0 AS total_reais
FROM vw_vendas_resumo AS v
INNER JOIN lojas AS l ON l.id = v.loja_id
LEFT JOIN clientes AS c ON c.id = v.cliente_id
WHERE v.status = 'CONCLUIDA'
ORDER BY v.venda_id
LIMIT 20;

-- E11: Clientes sem compras usando LEFT JOIN.
-- O status fica no ON para preservar os clientes sem venda concluida.
SELECT c.id, c.nome
FROM clientes AS c
LEFT JOIN vendas AS v ON v.cliente_id = c.id AND v.status = 'CONCLUIDA'
WHERE v.id IS NULL
ORDER BY c.id;

-- E12: Relacionamento muitos para muitos.
SELECT p.id, p.nome AS produto, COUNT(*) AS quantidade_fornecedores,
       MIN(pf.custo_centavos) / 100.0 AS menor_custo_reais,
       MAX(pf.custo_centavos) / 100.0 AS maior_custo_reais
FROM produtos AS p
INNER JOIN produto_fornecedores AS pf ON pf.produto_id = p.id
GROUP BY p.id, p.nome
HAVING COUNT(*) >= 2
ORDER BY quantidade_fornecedores DESC, p.id;

-- E13: Faturamento e ticket medio por loja.
SELECT l.nome AS loja, COUNT(*) AS quantidade_vendas,
       SUM(v.total_centavos) / 100.0 AS faturamento_reais,
       ROUND(AVG(v.total_centavos) / 100.0, 2) AS ticket_medio_reais
FROM vw_vendas_resumo AS v
INNER JOIN lojas AS l ON l.id = v.loja_id
WHERE v.status = 'CONCLUIDA'
GROUP BY l.id, l.nome
ORDER BY SUM(v.total_centavos) DESC, l.id;

-- E14: Clientes com maior gasto.
SELECT c.id, c.nome, COUNT(*) AS quantidade_vendas,
       SUM(v.total_centavos) / 100.0 AS gasto_total_reais
FROM clientes AS c
INNER JOIN vw_vendas_resumo AS v ON v.cliente_id = c.id
WHERE v.status = 'CONCLUIDA'
GROUP BY c.id, c.nome
HAVING SUM(v.total_centavos) > 100000
ORDER BY SUM(v.total_centavos) DESC, c.id;

-- E15: Produtos com maior receita.
SELECT produto_id, produto, unidade,
       ROUND(SUM(quantidade), 3) AS quantidade_vendida,
       COUNT(DISTINCT venda_id) AS quantidade_vendas,
       SUM(total_centavos) / 100.0 AS receita_reais
FROM vw_itens_venda
WHERE status = 'CONCLUIDA'
GROUP BY produto_id, produto, unidade
ORDER BY SUM(total_centavos) DESC, produto_id
LIMIT 10;

-- E16: Descontos por canal.
SELECT canal, COUNT(*) AS quantidade_vendas,
       SUM(valor_bruto_centavos) / 100.0 AS valor_bruto_reais,
       SUM(desconto_centavos) / 100.0 AS descontos_reais,
       SUM(total_centavos) / 100.0 AS receita_reais,
       ROUND(100.0 * SUM(desconto_centavos)
             / NULLIF(SUM(valor_bruto_centavos), 0), 2) AS taxa_desconto_percentual
FROM vw_vendas_resumo
WHERE status = 'CONCLUIDA'
GROUP BY canal
ORDER BY canal;

-- E17: Uma venda, varios pagamentos.
-- A subconsulta tem uma linha por venda, evitando multiplicar os valores.
SELECT v.venda_id, p.quantidade_pagamentos,
       v.total_centavos / 100.0 AS total_venda_reais,
       p.total_pago_centavos / 100.0 AS total_pago_reais
FROM vw_vendas_resumo AS v
INNER JOIN (
    SELECT venda_id, COUNT(*) AS quantidade_pagamentos,
           SUM(valor_centavos) AS total_pago_centavos
    FROM pagamentos
    GROUP BY venda_id
) AS p ON p.venda_id = v.venda_id
WHERE v.status = 'CONCLUIDA'
  AND p.quantidade_pagamentos >= 2
ORDER BY v.venda_id;

-- E18: Receita recebida por forma de pagamento.
SELECT f.nome AS forma_pagamento,
       COUNT(DISTINCT p.venda_id) AS quantidade_vendas,
       SUM(p.valor_centavos) / 100.0 AS total_recebido_reais
FROM pagamentos AS p
INNER JOIN formas_pagamento AS f ON f.id = p.forma_pagamento_id
INNER JOIN vendas AS v ON v.id = p.venda_id
WHERE v.status = 'CONCLUIDA'
GROUP BY f.id, f.nome
ORDER BY SUM(p.valor_centavos) DESC, f.nome;

-- E19: Produtos nunca vendidos usando NOT EXISTS.
SELECT p.id, p.codigo, p.nome
FROM produtos AS p
WHERE NOT EXISTS (
    SELECT 1
    FROM itens_venda AS i
    INNER JOIN vendas AS v ON v.id = i.venda_id
    WHERE i.produto_id = p.id
      AND v.status = 'CONCLUIDA'
)
ORDER BY p.id;

-- E20: Clientes de mais de um canal usando EXISTS.
SELECT c.id, c.nome
FROM clientes AS c
WHERE EXISTS (
    SELECT 1
    FROM vendas AS v
    WHERE v.cliente_id = c.id
      AND v.status = 'CONCLUIDA'
      AND v.canal = 'LOJA'
)
AND EXISTS (
    SELECT 1
    FROM vendas AS v
    WHERE v.cliente_id = c.id
      AND v.status = 'CONCLUIDA'
      AND v.canal = 'DELIVERY'
)
ORDER BY c.id;

-- E21: Comparacao com a media da propria categoria.
SELECT p.id, p.nome, c.nome AS categoria,
       p.preco_venda_centavos / 100.0 AS preco_reais
FROM produtos AS p
INNER JOIN categorias AS c ON c.id = p.categoria_id
WHERE p.ativo = 1
  AND p.preco_venda_centavos > (
      SELECT AVG(p2.preco_venda_centavos)
      FROM produtos AS p2
      WHERE p2.categoria_id = p.categoria_id
        AND p2.ativo = 1
  )
ORDER BY c.nome, p.preco_venda_centavos DESC, p.id;

-- E22: Classificacao com CASE.
-- GROUP BY pode usar o alias da expressao no SQLite.
SELECT CASE
           WHEN total_centavos < 5000 THEN 'Ate R$ 49,99'
           WHEN total_centavos < 15000 THEN 'De R$ 50 a R$ 149,99'
           ELSE 'A partir de R$ 150'
       END AS faixa_valor,
       COUNT(*) AS quantidade_vendas,
       SUM(total_centavos) / 100.0 AS receita_reais
FROM vw_vendas_resumo
WHERE status = 'CONCLUIDA'
GROUP BY faixa_valor
ORDER BY MIN(total_centavos);

-- E23: Primeira CTE.
WITH resumo_mensal AS (
    SELECT strftime('%Y-%m', data_venda) AS mes,
           COUNT(*) AS quantidade_vendas,
           SUM(total_centavos) AS receita_centavos
    FROM vw_vendas_resumo
    WHERE status = 'CONCLUIDA'
      AND data_venda >= '2026-01-01'
      AND data_venda < '2026-10-01'
    GROUP BY strftime('%Y-%m', data_venda)
)
SELECT mes, quantidade_vendas, receita_centavos / 100.0 AS receita_reais,
       ROUND(receita_centavos / 100.0 / quantidade_vendas, 2) AS ticket_medio_reais
FROM resumo_mensal
ORDER BY mes;

-- E24: Necessidade de reposicao.
SELECT loja, produto, unidade, quantidade_atual, quantidade_minima,
       ROUND(quantidade_minima - quantidade_atual, 3) AS quantidade_para_repor
FROM vw_estoque_detalhado
WHERE data_referencia = '2026-09-30'
  AND precisa_repor = 1
ORDER BY loja, produto, produto_id;

-- E25: Margem bruta por categoria.
SELECT c.nome AS categoria,
       SUM(i.total_centavos) / 100.0 AS receita_reais,
       SUM(i.custo_total_centavos) / 100.0 AS custo_reais,
       SUM(i.total_centavos - i.custo_total_centavos) / 100.0 AS margem_bruta_reais,
       ROUND(100.0 * SUM(i.total_centavos - i.custo_total_centavos)
             / NULLIF(SUM(i.total_centavos), 0), 2) AS margem_bruta_percentual
FROM vw_itens_venda AS i
INNER JOIN categorias AS c ON c.id = i.categoria_id
WHERE i.status = 'CONCLUIDA'
GROUP BY c.id, c.nome
ORDER BY SUM(i.total_centavos - i.custo_total_centavos) DESC, c.nome;

-- E26: Ranking dentro de cada categoria.
WITH receita_produto AS (
    SELECT categoria_id, produto_id, produto,
           SUM(total_centavos) AS receita_centavos
    FROM vw_itens_venda
    WHERE status = 'CONCLUIDA'
    GROUP BY categoria_id, produto_id, produto
), ranking AS (
    SELECT categoria_id, produto_id, produto, receita_centavos,
           DENSE_RANK() OVER (
               PARTITION BY categoria_id
               ORDER BY receita_centavos DESC
           ) AS posicao
    FROM receita_produto
)
SELECT c.nome AS categoria, r.produto,
       r.receita_centavos / 100.0 AS receita_reais, r.posicao
FROM ranking AS r
INNER JOIN categorias AS c ON c.id = r.categoria_id
WHERE r.posicao <= 3
ORDER BY c.nome, r.posicao, r.produto_id;

-- E27: Comparacao com o mes anterior.
WITH receita_mensal AS (
    SELECT loja_id, strftime('%Y-%m', data_venda) AS mes,
           SUM(total_centavos) AS receita_centavos
    FROM vw_vendas_resumo
    WHERE status = 'CONCLUIDA'
      AND data_venda >= '2026-01-01'
      AND data_venda < '2026-10-01'
    GROUP BY loja_id, strftime('%Y-%m', data_venda)
), comparacao AS (
    SELECT loja_id, mes, receita_centavos,
           LAG(receita_centavos) OVER (
               PARTITION BY loja_id ORDER BY mes
           ) AS receita_anterior_centavos
    FROM receita_mensal
)
SELECT l.nome AS loja, c.mes, c.receita_centavos / 100.0 AS receita_reais,
       c.receita_anterior_centavos / 100.0 AS receita_anterior_reais,
       (c.receita_centavos - c.receita_anterior_centavos) / 100.0 AS variacao_reais
FROM comparacao AS c
INNER JOIN lojas AS l ON l.id = c.loja_id
ORDER BY l.nome, c.mes;

-- E28: Receita acumulada.
WITH receita_mensal AS (
    SELECT loja_id, strftime('%Y-%m', data_venda) AS mes,
           SUM(total_centavos) AS receita_centavos
    FROM vw_vendas_resumo
    WHERE status = 'CONCLUIDA'
      AND data_venda >= '2026-01-01'
      AND data_venda < '2026-10-01'
    GROUP BY loja_id, strftime('%Y-%m', data_venda)
)
SELECT l.nome AS loja, r.mes, r.receita_centavos / 100.0 AS receita_reais,
       SUM(r.receita_centavos) OVER (
           PARTITION BY r.loja_id
           ORDER BY r.mes
           ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
       ) / 100.0 AS receita_acumulada_reais
FROM receita_mensal AS r
INNER JOIN lojas AS l ON l.id = r.loja_id
ORDER BY l.nome, r.mes;

-- E29: Recencia, frequencia e valor dos clientes.
WITH resumo_cliente AS (
    SELECT cliente_id, MAX(data_venda) AS ultima_venda,
           COUNT(*) AS quantidade_vendas,
           SUM(total_centavos) AS gasto_centavos
    FROM vw_vendas_resumo
    WHERE status = 'CONCLUIDA'
      AND data_venda >= '2026-01-01'
      AND data_venda < '2026-10-01'
      AND cliente_id IS NOT NULL
    GROUP BY cliente_id
)
SELECT c.id, c.nome, date(r.ultima_venda) AS data_ultima_venda,
       CAST(julianday('2026-09-30') - julianday(date(r.ultima_venda)) AS INTEGER)
           AS dias_desde_ultima_venda,
       COALESCE(r.quantidade_vendas, 0) AS quantidade_vendas,
       COALESCE(r.gasto_centavos, 0) / 100.0 AS gasto_total_reais
FROM clientes AS c
LEFT JOIN resumo_cliente AS r ON r.cliente_id = c.id
ORDER BY COALESCE(r.gasto_centavos, 0) DESC, c.id;

-- E30: Desempenho dos fornecedores.
SELECT f.id, f.nome,
       SUM(CASE WHEN c.status = 'RECEBIDA' THEN 1 ELSE 0 END) AS pedidos_recebidos,
       SUM(CASE WHEN c.status = 'PENDENTE' THEN 1 ELSE 0 END) AS pedidos_pendentes,
       SUM(CASE WHEN c.status = 'CANCELADA' THEN 1 ELSE 0 END) AS pedidos_cancelados,
       ROUND(AVG(CASE WHEN c.status = 'RECEBIDA'
                      THEN julianday(c.data_recebimento) - julianday(c.data_pedido)
                 END), 2) AS prazo_medio_real_dias
FROM fornecedores AS f
LEFT JOIN compras AS c ON c.fornecedor_id = f.id
GROUP BY f.id, f.nome
ORDER BY f.id;

-- E31: Conferencia do estoque.
-- Entradas e saidas possuem uma linha por loja/produto antes dos JOINs.
WITH entradas AS (
    SELECT c.loja_id, i.produto_id, SUM(i.quantidade) AS quantidade_recebida
    FROM itens_compra AS i
    INNER JOIN compras AS c ON c.id = i.compra_id
    WHERE c.status = 'RECEBIDA'
      AND c.data_recebimento >= '2026-01-01'
      AND c.data_recebimento < '2026-10-01'
    GROUP BY c.loja_id, i.produto_id
), saidas AS (
    SELECT v.loja_id, i.produto_id, SUM(i.quantidade) AS quantidade_vendida
    FROM itens_venda AS i
    INNER JOIN vendas AS v ON v.id = i.venda_id
    WHERE v.status = 'CONCLUIDA'
      AND v.data_venda >= '2026-01-01'
      AND v.data_venda < '2026-10-01'
    GROUP BY v.loja_id, i.produto_id
), conferencia AS (
    SELECT e.loja_id, e.produto_id, e.quantidade_atual,
           e.quantidade_inicial + COALESCE(en.quantidade_recebida, 0)
               - COALESCE(s.quantidade_vendida, 0) AS saldo_calculado
    FROM estoques AS e
    LEFT JOIN entradas AS en ON en.loja_id = e.loja_id AND en.produto_id = e.produto_id
    LEFT JOIN saidas AS s ON s.loja_id = e.loja_id AND s.produto_id = e.produto_id
    WHERE e.data_referencia = '2026-09-30'
)
SELECT l.nome AS loja, p.nome AS produto, p.unidade,
       ROUND(c.saldo_calculado, 6) AS saldo_calculado,
       c.quantidade_atual AS saldo_registrado,
       ROUND(c.quantidade_atual - c.saldo_calculado, 6) AS diferenca
FROM conferencia AS c
INNER JOIN lojas AS l ON l.id = c.loja_id
INNER JOIN produtos AS p ON p.id = c.produto_id
WHERE ABS(c.quantidade_atual - c.saldo_calculado) > 0.000001
ORDER BY l.nome, p.nome, p.id;

-- E32: Reconciliacao de pagamentos.
-- A comparacao e exata em centavos inteiros; a divisao e so para exibicao.
WITH pagamentos_por_venda AS (
    SELECT venda_id, COUNT(*) AS quantidade_pagamentos,
           SUM(valor_centavos) AS valor_pago_centavos
    FROM pagamentos
    GROUP BY venda_id
), conferencia AS (
    SELECT v.venda_id, v.status,
           COALESCE(p.quantidade_pagamentos, 0) AS quantidade_pagamentos,
           CASE WHEN v.status = 'CONCLUIDA' THEN v.total_centavos ELSE 0 END
               AS valor_esperado_centavos,
           COALESCE(p.valor_pago_centavos, 0) AS valor_pago_centavos
    FROM vw_vendas_resumo AS v
    LEFT JOIN pagamentos_por_venda AS p ON p.venda_id = v.venda_id
)
SELECT venda_id, status, quantidade_pagamentos,
       valor_esperado_centavos / 100.0 AS valor_esperado_reais,
       valor_pago_centavos / 100.0 AS valor_pago_reais,
       (valor_pago_centavos - valor_esperado_centavos) / 100.0 AS diferenca_reais
FROM conferencia
WHERE valor_pago_centavos <> valor_esperado_centavos
ORDER BY venda_id;
