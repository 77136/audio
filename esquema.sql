-- Mercado Bom Bairro: dados inteiramente ficticios para estudar SQLite.
-- Dinheiro em centavos inteiros. Quantidades em UN ou KG, conforme produtos.unidade.
-- As datas e horas sao locais e cobrem janeiro a setembro de 2026.

CREATE TABLE lojas (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL UNIQUE,
    cidade TEXT NOT NULL,
    bairro TEXT NOT NULL,
    uf TEXT NOT NULL CHECK (length(uf) = 2),
    data_abertura TEXT NOT NULL
);

CREATE TABLE categorias (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL UNIQUE,
    descricao TEXT NOT NULL
);

CREATE TABLE marcas (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL UNIQUE
);

CREATE TABLE fornecedores (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL,
    cidade TEXT NOT NULL,
    uf TEXT NOT NULL CHECK (length(uf) = 2),
    email TEXT UNIQUE,
    prazo_entrega_dias INTEGER NOT NULL CHECK (prazo_entrega_dias >= 0),
    ativo INTEGER NOT NULL DEFAULT 1 CHECK (ativo IN (0, 1))
);

CREATE TABLE produtos (
    id INTEGER PRIMARY KEY,
    codigo TEXT NOT NULL UNIQUE,
    nome TEXT NOT NULL,
    categoria_id INTEGER NOT NULL REFERENCES categorias(id),
    marca_id INTEGER NOT NULL REFERENCES marcas(id),
    unidade TEXT NOT NULL CHECK (unidade IN ('UN', 'KG')),
    preco_venda_centavos INTEGER NOT NULL CHECK (preco_venda_centavos > 0),
    custo_centavos INTEGER NOT NULL CHECK (custo_centavos > 0),
    ativo INTEGER NOT NULL DEFAULT 1 CHECK (ativo IN (0, 1))
);

-- Tabela de ligacao: um produto pode ter varios fornecedores e vice-versa.
CREATE TABLE produto_fornecedores (
    produto_id INTEGER NOT NULL REFERENCES produtos(id),
    fornecedor_id INTEGER NOT NULL REFERENCES fornecedores(id),
    custo_centavos INTEGER NOT NULL CHECK (custo_centavos > 0),
    principal INTEGER NOT NULL CHECK (principal IN (0, 1)),
    PRIMARY KEY (produto_id, fornecedor_id)
);

CREATE TABLE clientes (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL,
    email TEXT UNIQUE,
    cidade TEXT NOT NULL,
    bairro TEXT NOT NULL,
    data_cadastro TEXT NOT NULL,
    data_nascimento TEXT,
    aceita_marketing INTEGER NOT NULL CHECK (aceita_marketing IN (0, 1))
);

CREATE TABLE funcionarios (
    id INTEGER PRIMARY KEY,
    loja_id INTEGER NOT NULL REFERENCES lojas(id),
    nome TEXT NOT NULL,
    cargo TEXT NOT NULL CHECK (cargo IN ('GERENTE', 'CAIXA', 'REPOSITOR', 'COMPRADOR')),
    data_admissao TEXT NOT NULL,
    salario_centavos INTEGER NOT NULL CHECK (salario_centavos > 0),
    ativo INTEGER NOT NULL DEFAULT 1 CHECK (ativo IN (0, 1)),
    UNIQUE (id, loja_id)
);

CREATE TABLE formas_pagamento (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL UNIQUE
);

CREATE TABLE compras (
    id INTEGER PRIMARY KEY,
    loja_id INTEGER NOT NULL REFERENCES lojas(id),
    fornecedor_id INTEGER NOT NULL REFERENCES fornecedores(id),
    data_pedido TEXT NOT NULL,
    data_recebimento TEXT,
    status TEXT NOT NULL CHECK (status IN ('RECEBIDA', 'PENDENTE', 'CANCELADA')),
    CHECK ((status = 'RECEBIDA' AND data_recebimento IS NOT NULL
            AND data_recebimento >= data_pedido)
        OR (status IN ('PENDENTE', 'CANCELADA') AND data_recebimento IS NULL)),
    UNIQUE (id, fornecedor_id)
);

CREATE TABLE itens_compra (
    id INTEGER PRIMARY KEY,
    compra_id INTEGER NOT NULL,
    fornecedor_id INTEGER NOT NULL,
    produto_id INTEGER NOT NULL,
    quantidade REAL NOT NULL CHECK (quantidade > 0),
    custo_unitario_centavos INTEGER NOT NULL CHECK (custo_unitario_centavos > 0),
    UNIQUE (compra_id, produto_id),
    -- Garante que o fornecedor oferece o produto e pertence a esta compra.
    FOREIGN KEY (compra_id, fornecedor_id) REFERENCES compras(id, fornecedor_id),
    FOREIGN KEY (produto_id, fornecedor_id)
        REFERENCES produto_fornecedores(produto_id, fornecedor_id)
);

CREATE TABLE vendas (
    id INTEGER PRIMARY KEY,
    loja_id INTEGER NOT NULL REFERENCES lojas(id),
    cliente_id INTEGER REFERENCES clientes(id),
    funcionario_id INTEGER NOT NULL,
    data_venda TEXT NOT NULL,
    canal TEXT NOT NULL CHECK (canal IN ('LOJA', 'DELIVERY', 'RETIRADA')),
    status TEXT NOT NULL CHECK (status IN ('CONCLUIDA', 'CANCELADA')),
    -- O funcionario que registrou a venda deve ser da mesma loja.
    FOREIGN KEY (funcionario_id, loja_id) REFERENCES funcionarios(id, loja_id)
);

CREATE TABLE itens_venda (
    id INTEGER PRIMARY KEY,
    venda_id INTEGER NOT NULL REFERENCES vendas(id),
    produto_id INTEGER NOT NULL REFERENCES produtos(id),
    quantidade REAL NOT NULL CHECK (quantidade > 0),
    preco_unitario_centavos INTEGER NOT NULL CHECK (preco_unitario_centavos > 0),
    custo_unitario_centavos INTEGER NOT NULL CHECK (custo_unitario_centavos > 0),
    desconto_centavos INTEGER NOT NULL DEFAULT 0
        CHECK (desconto_centavos >= 0
           AND desconto_centavos <= (CAST(ROUND(quantidade * 1000) AS INTEGER)
                                      * preco_unitario_centavos + 500) / 1000),
    UNIQUE (venda_id, produto_id)
);

-- Uma venda pode ser paga usando mais de uma forma de pagamento.
CREATE TABLE pagamentos (
    id INTEGER PRIMARY KEY,
    venda_id INTEGER NOT NULL REFERENCES vendas(id),
    forma_pagamento_id INTEGER NOT NULL REFERENCES formas_pagamento(id),
    valor_centavos INTEGER NOT NULL CHECK (valor_centavos > 0),
    data_pagamento TEXT NOT NULL
);

-- Retrato em 30/09/2026, apos os movimentos do periodo.
-- Abertura em 01/01/2026 + compras recebidas - vendas concluidas = quantidade_atual.
CREATE TABLE estoques (
    loja_id INTEGER NOT NULL REFERENCES lojas(id),
    produto_id INTEGER NOT NULL REFERENCES produtos(id),
    quantidade_inicial REAL NOT NULL CHECK (quantidade_inicial >= 0),
    quantidade_atual REAL NOT NULL CHECK (quantidade_atual >= 0),
    quantidade_minima REAL NOT NULL CHECK (quantidade_minima >= 0),
    data_referencia TEXT NOT NULL,
    PRIMARY KEY (loja_id, produto_id)
);

CREATE INDEX idx_produtos_categoria ON produtos(categoria_id);
CREATE INDEX idx_produtos_marca ON produtos(marca_id);
CREATE INDEX idx_produto_fornecedores_fornecedor ON produto_fornecedores(fornecedor_id);
CREATE UNIQUE INDEX idx_fornecedor_principal ON produto_fornecedores(produto_id) WHERE principal = 1;
CREATE INDEX idx_funcionarios_loja ON funcionarios(loja_id);
CREATE INDEX idx_compras_loja_data ON compras(loja_id, data_pedido);
CREATE INDEX idx_compras_fornecedor ON compras(fornecedor_id);
CREATE INDEX idx_itens_compra_compra ON itens_compra(compra_id);
CREATE INDEX idx_itens_compra_fornecedor ON itens_compra(produto_id, fornecedor_id);
CREATE INDEX idx_vendas_data ON vendas(data_venda);
CREATE INDEX idx_vendas_loja_data ON vendas(loja_id, data_venda);
CREATE INDEX idx_vendas_cliente ON vendas(cliente_id);
CREATE INDEX idx_vendas_funcionario ON vendas(funcionario_id, loja_id);
CREATE INDEX idx_itens_venda_produto ON itens_venda(produto_id);
CREATE INDEX idx_pagamentos_venda ON pagamentos(venda_id);
CREATE INDEX idx_pagamentos_forma ON pagamentos(forma_pagamento_id);
CREATE INDEX idx_estoques_produto ON estoques(produto_id);

-- A quantidade tem ate tres casas decimais. Multiplicar milésimos inteiros
-- e dividir por 1000 evita a imprecisao de REAL no arredondamento monetario.
CREATE VIEW vw_itens_venda AS
SELECT i.id AS item_venda_id, i.venda_id, i.produto_id, p.nome AS produto,
       p.categoria_id, p.unidade, v.loja_id, v.cliente_id, v.funcionario_id,
       v.data_venda, v.canal, v.status, i.quantidade,
       i.preco_unitario_centavos, i.custo_unitario_centavos, i.desconto_centavos,
       (CAST(ROUND(i.quantidade * 1000) AS INTEGER) * i.preco_unitario_centavos + 500) / 1000 AS bruto_centavos,
       (CAST(ROUND(i.quantidade * 1000) AS INTEGER) * i.preco_unitario_centavos + 500) / 1000
           - i.desconto_centavos AS total_centavos,
       (CAST(ROUND(i.quantidade * 1000) AS INTEGER) * i.custo_unitario_centavos + 500) / 1000 AS custo_total_centavos
FROM itens_venda AS i
JOIN vendas AS v ON v.id = i.venda_id
JOIN produtos AS p ON p.id = i.produto_id;

CREATE VIEW vw_vendas_resumo AS
SELECT v.id AS venda_id, v.loja_id, v.cliente_id, v.funcionario_id,
       v.data_venda, v.canal, v.status,
       COUNT(i.id) AS quantidade_itens,
       COALESCE(SUM((CAST(ROUND(i.quantidade * 1000) AS INTEGER) * i.preco_unitario_centavos + 500) / 1000), 0)
           AS valor_bruto_centavos,
       COALESCE(SUM(i.desconto_centavos), 0) AS desconto_centavos,
       COALESCE(SUM((CAST(ROUND(i.quantidade * 1000) AS INTEGER) * i.preco_unitario_centavos + 500) / 1000
           - i.desconto_centavos), 0) AS total_centavos
FROM vendas AS v
LEFT JOIN itens_venda AS i ON i.venda_id = v.id
GROUP BY v.id, v.loja_id, v.cliente_id, v.funcionario_id, v.data_venda, v.canal, v.status;

CREATE VIEW vw_compras_resumo AS
SELECT c.id AS compra_id, c.loja_id, c.fornecedor_id,
       c.data_pedido, c.data_recebimento, c.status,
       COUNT(i.id) AS quantidade_itens,
       COALESCE(SUM((CAST(ROUND(i.quantidade * 1000) AS INTEGER) * i.custo_unitario_centavos + 500) / 1000), 0)
           AS total_centavos
FROM compras AS c
LEFT JOIN itens_compra AS i ON i.compra_id = c.id
GROUP BY c.id, c.loja_id, c.fornecedor_id, c.data_pedido, c.data_recebimento, c.status;

CREATE VIEW vw_estoque_detalhado AS
SELECT e.loja_id, l.nome AS loja, e.produto_id, p.nome AS produto,
       c.nome AS categoria, p.unidade, e.quantidade_inicial,
       e.quantidade_atual, e.quantidade_minima, e.data_referencia,
       CASE WHEN e.quantidade_atual < e.quantidade_minima THEN 1 ELSE 0 END AS precisa_repor,
       (CAST(ROUND(e.quantidade_atual * 1000) AS INTEGER) * p.custo_centavos + 500) / 1000 AS valor_custo_centavos
FROM estoques AS e
JOIN lojas AS l ON l.id = e.loja_id
JOIN produtos AS p ON p.id = e.produto_id
JOIN categorias AS c ON c.id = p.categoria_id;
