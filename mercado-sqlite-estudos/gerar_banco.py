"""Gera o kit didatico localmente usando apenas a biblioteca padrao do Python."""
from collections import defaultdict
from datetime import date, datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
import random
import sqlite3

BASE = Path(__file__).resolve().parent
RNG = random.Random(20261017)
FINAL = date(2026, 9, 30)


def cents(quantity, price):
    return int((Decimal(str(quantity)) * price).quantize(Decimal('1'), rounding=ROUND_HALF_UP))


def quantity(milli):
    return milli / 1000


def quote(value):
    if value is None:
        return 'NULL'
    if isinstance(value, str):
        return "'" + value.replace("'", "''") + "'"
    return str(value)


TABLES = {}


def rows(table, columns, values):
    TABLES[table] = (columns.split(), values)


rows('lojas', 'id nome cidade bairro uf data_abertura', [
    (1, 'Bom Bairro - Centro', 'Campinas', 'Centro', 'SP', '2018-03-15'),
    (2, 'Bom Bairro - Jardim Sol', 'Campinas', 'Jardim Sol', 'SP', '2020-08-10'),
    (3, 'Bom Bairro - Vila Verde', 'Valinhos', 'Vila Verde', 'SP', '2022-05-20'),
])

catalogue = [
    ('Mercearia', 'Alimentos secos, graos e ingredientes', [
        ('Arroz branco 5 kg', 'UN', 2590), ('Feijao carioca 1 kg', 'UN', 799),
        ('Acucar cristal 1 kg', 'UN', 459), ('Farinha de trigo 1 kg', 'UN', 549),
        ('Macarrao espaguete 500 g', 'UN', 479), ('Oleo de soja 900 ml', 'UN', 799),
        ('Sal refinado 1 kg', 'UN', 249), ('Molho de tomate 300 g', 'UN', 269),
        ('Cafe torrado 500 g', 'UN', 2190), ('Aveia em flocos 170 g', 'UN', 599)]),
    ('Hortifruti', 'Frutas, verduras e legumes vendidos por peso', [
        ('Banana prata', 'KG', 699), ('Maca gala', 'KG', 1190), ('Laranja pera', 'KG', 499),
        ('Tomate italiano', 'KG', 799), ('Batata inglesa', 'KG', 599), ('Cebola', 'KG', 499),
        ('Cenoura', 'KG', 599), ('Abobrinha', 'KG', 699), ('Mamao formosa', 'KG', 799),
        ('Manga palmer', 'KG', 899)]),
    ('Acougue', 'Carnes refrigeradas vendidas por peso', [
        ('Patinho bovino', 'KG', 4490), ('Alcatra bovina', 'KG', 5490),
        ('Peito de frango', 'KG', 1990), ('Coxa de frango', 'KG', 1290),
        ('Lombo suino', 'KG', 2490), ('Costela bovina', 'KG', 3290),
        ('Carne moida bovina', 'KG', 3490), ('Linguica toscana', 'KG', 2290),
        ('File de tilapia', 'KG', 4990), ('Asa de frango', 'KG', 1790)]),
    ('Laticinios', 'Leites, queijos e derivados', [
        ('Leite integral 1 L', 'UN', 549), ('Leite desnatado 1 L', 'UN', 559),
        ('Iogurte morango 170 g', 'UN', 299), ('Manteiga 200 g', 'UN', 1190),
        ('Requeijao 200 g', 'UN', 899), ('Queijo mussarela', 'KG', 3990),
        ('Queijo prato', 'KG', 4490), ('Creme de leite 200 g', 'UN', 399),
        ('Leite condensado 395 g', 'UN', 649), ('Bebida lactea 900 g', 'UN', 799)]),
    ('Padaria', 'Paes, bolos e produtos de panificacao', [
        ('Pao frances', 'KG', 1690), ('Pao de forma 450 g', 'UN', 799),
        ('Pao integral 450 g', 'UN', 1090), ('Bisnaguinha 300 g', 'UN', 849),
        ('Bolo de cenoura 400 g', 'UN', 1590), ('Bolo de fuba 400 g', 'UN', 1390),
        ('Torrada 150 g', 'UN', 599), ('Pao de queijo', 'KG', 2990),
        ('Rosquinha 300 g', 'UN', 699), ('Pao de leite 300 g', 'UN', 749)]),
    ('Bebidas', 'Bebidas nao alcoolicas', [
        ('Agua mineral 1,5 L', 'UN', 299), ('Agua com gas 500 ml', 'UN', 249),
        ('Refrigerante cola 2 L', 'UN', 999), ('Refrigerante guarana 2 L', 'UN', 899),
        ('Suco de uva 1 L', 'UN', 1190), ('Suco de laranja 1 L', 'UN', 1090),
        ('Cha gelado 1,5 L', 'UN', 799), ('Agua de coco 1 L', 'UN', 899),
        ('Isotonico 500 ml', 'UN', 649), ('Energetico 250 ml', 'UN', 799)]),
    ('Limpeza', 'Produtos de limpeza domestica', [
        ('Detergente 500 ml', 'UN', 249), ('Sabao em po 800 g', 'UN', 1190),
        ('Amaciante 2 L', 'UN', 999), ('Agua sanitaria 1 L', 'UN', 449),
        ('Desinfetante 2 L', 'UN', 699), ('Limpador multiuso 500 ml', 'UN', 499),
        ('Esponja pacote 3 un', 'UN', 449), ('Lava roupas liquido 1 L', 'UN', 1490),
        ('Saco de lixo 50 L 10 un', 'UN', 799), ('Alcool 70 1 L', 'UN', 899)]),
    ('Higiene', 'Produtos de higiene pessoal', [
        ('Sabonete 85 g', 'UN', 249), ('Shampoo 350 ml', 'UN', 1290),
        ('Condicionador 350 ml', 'UN', 1390), ('Creme dental 90 g', 'UN', 499),
        ('Escova dental', 'UN', 699), ('Papel higienico 12 rolos', 'UN', 1890),
        ('Desodorante 150 ml', 'UN', 1190), ('Fio dental 50 m', 'UN', 799),
        ('Absorvente 8 un', 'UN', 599), ('Hastes flexiveis 75 un', 'UN', 449)]),
    ('Congelados', 'Alimentos mantidos congelados', [
        ('Pizza mussarela 460 g', 'UN', 1790), ('Lasanha bolonhesa 600 g', 'UN', 1990),
        ('Batata congelada 1 kg', 'UN', 1690), ('Hamburguer 672 g', 'UN', 1890),
        ('Nuggets 300 g', 'UN', 1290), ('Sorvete chocolate 1,5 L', 'UN', 2490),
        ('Polpa de acerola 100 g', 'UN', 349), ('Legumes congelados 300 g', 'UN', 899),
        ('Pao de queijo congelado 1 kg', 'UN', 2190), ('Acai congelado 1 L', 'UN', 2290)]),
    ('Biscoitos e doces', 'Biscoitos, chocolates e guloseimas', [
        ('Biscoito maisena 350 g', 'UN', 599), ('Biscoito recheado 120 g', 'UN', 349),
        ('Biscoito cream cracker 350 g', 'UN', 649), ('Chocolate ao leite 80 g', 'UN', 699),
        ('Chocolate amargo 80 g', 'UN', 799), ('Bala de frutas 100 g', 'UN', 399),
        ('Gelatina morango 20 g', 'UN', 199), ('Pipoca micro-ondas 100 g', 'UN', 449),
        ('Doce de leite 400 g', 'UN', 1190), ('Goiabada 300 g', 'UN', 699)]),
    ('Pet shop', 'Alimentos e cuidados para animais', [
        ('Racao caes adultos 3 kg', 'UN', 3990), ('Racao gatos adultos 1 kg', 'UN', 2490),
        ('Sache caes 100 g', 'UN', 299), ('Sache gatos 85 g', 'UN', 349),
        ('Areia sanitaria 4 kg', 'UN', 1590), ('Petisco caes 100 g', 'UN', 899),
        ('Petisco gatos 60 g', 'UN', 999), ('Tapete higienico 7 un', 'UN', 1890),
        ('Racao filhotes 1 kg', 'UN', 1790), ('Shampoo pet 500 ml', 'UN', 1290)]),
    ('Utilidades', 'Utensilios e descartaveis para casa', [
        ('Papel aluminio 7,5 m', 'UN', 599), ('Filme PVC 15 m', 'UN', 649),
        ('Guardanapo 50 un', 'UN', 349), ('Copo descartavel 100 un', 'UN', 899),
        ('Filtro de cafe 30 un', 'UN', 499), ('Fosforo 10 caixas', 'UN', 399),
        ('Pote reutilizavel 1 L', 'UN', 799), ('Pano de prato', 'UN', 599),
        ('Luva de limpeza par', 'UN', 699), ('Prendedor de roupa 12 un', 'UN', 499)]),
]
rows('categorias', 'id nome descricao', [(i, x[0], x[1]) for i, x in enumerate(catalogue, 1)])
brands = ['Campo Claro', 'Sabor da Vila', 'Boa Colheita', 'Serra Serena', 'Casa Leve',
          'Brisa Limpa', 'Dia Feliz', 'Fonte Azul', 'Forno Alegre', 'Doce Quintal',
          'Amigo Bicho', 'Lar Pratico', 'Pomar Novo', 'Vale Dourado', 'Viva Bem',
          'Cozinha Boa', 'Sol Nascente', 'Origem do Campo']
rows('marcas', 'id nome', list(enumerate(brands, 1)))
suppliers = []
for i in range(1, 21):
    suppliers.append((i, f'Distribuidora Ficticia {i:02d}',
                      ['Campinas', 'Valinhos', 'Jundiai', 'Sumare', 'Limeira'][(i-1) % 5],
                      'SP', f'fornecedor{i:02d}@example.com', 1 + i % 5, 1))
rows('fornecedores', 'id nome cidade uf email prazo_entrega_dias ativo', suppliers)

products, links = [], []
for cat, (_, _, items) in enumerate(catalogue, 1):
    for offset, (name, unit, price) in enumerate(items):
        pid = (cat - 1) * 10 + offset + 1
        cost = int(price * RNG.uniform(.58, .79))
        products.append((pid, f'MER-{pid:04d}', name, cat,
                         (cat * 3 + offset) % len(brands) + 1, unit, price, cost,
                         0 if pid in (119, 120) else 1))
        primary = ((cat - 1) % 10) * 2 + offset % 2 + 1
        secondary = primary + 1 if primary % 2 else primary - 1
        links.extend([(pid, primary, cost, 1), (pid, secondary, cents(1.04, cost), 0)])
rows('produtos', 'id codigo nome categoria_id marca_id unidade preco_venda_centavos custo_centavos ativo', products)
rows('produto_fornecedores', 'produto_id fornecedor_id custo_centavos principal', links)
by_product = {p[0]: p for p in products}
by_supplier = defaultdict(list)
for pid, sid, cost, main in links:
    by_supplier[sid].append((pid, cost))

given = ['Ana', 'Bruno', 'Carla', 'Diego', 'Elisa', 'Fabio', 'Gabriela', 'Henrique',
         'Isabela', 'Joao', 'Julia', 'Lucas', 'Mariana', 'Nicolas', 'Olivia',
         'Paulo', 'Renata', 'Sofia', 'Thiago', 'Vitoria', 'Camila', 'Rafael',
         'Livia', 'Felipe', 'Laura', 'Pedro', 'Luana', 'Andre', 'Beatriz', 'Gustavo']
last = ['Silva', 'Souza', 'Oliveira', 'Santos', 'Lima', 'Costa', 'Pereira',
        'Almeida', 'Ribeiro', 'Carvalho', 'Martins', 'Rocha', 'Gomes', 'Barbosa', 'Mendes']
customers = []
for i in range(1, 451):
    city = 'Valinhos' if i % 4 == 0 else 'Campinas'
    registered = date(2024, 1, 1) + timedelta(days=RNG.randrange(700))
    if i > 400:
        registered = date(2026, 9, 1) + timedelta(days=i % 29)
    born = None if i % 9 == 0 else str(date(1955, 1, 1) + timedelta(days=RNG.randrange(19000)))
    customers.append((i, f'{given[(i-1)%30]} {last[((i-1)//30)%15]} (F{i:03d})',
                      None if i % 8 == 0 else f'cliente{i:03d}@example.com', city,
                      ['Centro', 'Jardim Sol', 'Vila Verde', 'Santa Clara', 'Parque das Flores'][i % 5],
                      str(registered), born, 0 if i % 3 == 0 else 1))
rows('clientes', 'id nome email cidade bairro data_cadastro data_nascimento aceita_marketing', customers)

staff, cashiers = [], defaultdict(list)
for store in range(1, 4):
    for offset in range(10):
        eid = (store - 1) * 10 + offset + 1
        role = 'GERENTE' if offset == 0 else 'CAIXA' if offset <= 5 else 'COMPRADOR' if offset == 6 else 'REPOSITOR'
        salary = {'GERENTE': 520000, 'CAIXA': 215000, 'COMPRADOR': 340000, 'REPOSITOR': 205000}[role]
        staff.append((eid, store, f'{given[eid-1]} Equipe {store}', role,
                      str(date(2023, 1, 1) + timedelta(days=eid * 17)), salary + (eid % 3) * 10000, 1))
        if role == 'CAIXA':
            cashiers[store].append(eid)
rows('funcionarios', 'id loja_id nome cargo data_admissao salario_centavos ativo', staff)
rows('formas_pagamento', 'id nome', [(1, 'Dinheiro'), (2, 'Pix'), (3, 'Cartao de debito'),
                                    (4, 'Cartao de credito'), (5, 'Vale-alimentacao')])

# Movimentos em milesimos de unidade/kg evitam erro no calculo de estoque.
events = defaultdict(list)
purchases, purchase_items = [], []
for month in range(1, 10):
    for offset in range(20):
        cid = (month-1) * 20 + offset + 1
        sid = offset + 1
        store = (cid + month) % 3 + 1
        ordered = date(2026, month, 2 + offset // 4)
        received = ordered + timedelta(days=1 + sid % 5)
        status = 'CANCELADA' if cid % 23 == 0 else 'PENDENTE' if cid > 170 else 'RECEBIDA'
        purchases.append((cid, store, sid, str(ordered), str(received) if status == 'RECEBIDA' else None, status))
        available = by_supplier[sid]
        chosen = RNG.sample(available, min(len(available), RNG.randint(5, 9)))
        for pid, cost in chosen:
            unit = by_product[pid][5]
            milli = RNG.randint(5000, 16000) if unit == 'KG' else RNG.randint(6, 20) * 1000
            historical_cost = cents(.94 + month * .006, cost)
            purchase_items.append((len(purchase_items)+1, cid, sid, pid, quantity(milli), historical_cost))
            if status == 'RECEBIDA':
                events[(store, pid)].append((f'{received} 06:00:00', milli))
rows('compras', 'id loja_id fornecedor_id data_pedido data_recebimento status', purchases)
rows('itens_compra', 'id compra_id fornecedor_id produto_id quantidade custo_unitario_centavos', purchase_items)

sales, sale_items, payments = [], [], []
all_dates = sorted(date(2026, 1, 1) + timedelta(days=RNG.randrange(273)) for _ in range(1500))
for vid, day in enumerate(all_dates, 1):
    store = RNG.choices([1, 2, 3], weights=[45, 32, 23])[0]
    channel = RNG.choices(['LOJA', 'DELIVERY', 'RETIRADA'], weights=[76, 16, 8])[0]
    customer = vid if vid <= 400 else None if channel == 'LOJA' and RNG.random() < .25 else RNG.randint(1, 400)
    status = 'CANCELADA' if vid % 29 == 0 else 'CONCLUIDA'
    when = f'{day} {RNG.randrange(8, 21):02d}:{RNG.randrange(60):02d}:{RNG.randrange(60):02d}'
    sales.append((vid, store, customer, RNG.choice(cashiers[store]), when, channel, status))
    # Os quatro ultimos produtos nunca sao vendidos, para praticar LEFT JOIN/NOT EXISTS.
    chosen = RNG.sample(range(1, 117), RNG.randint(3, 12))
    total = 0
    for pid in chosen:
        product = by_product[pid]
        milli = RNG.randint(250, 3200) if product[5] == 'KG' else RNG.choices([1, 2, 3, 4, 6], [45, 30, 15, 8, 2])[0] * 1000
        qty = quantity(milli)
        price = cents(.94 + day.month * .006 + RNG.choice([0, 0, .01]), product[6])
        cost = cents(.94 + day.month * .006, product[7])
        gross = cents(qty, price)
        discount = cents(RNG.choice([.05, .10, .15]), gross) if RNG.random() < .17 else 0
        sale_items.append((len(sale_items)+1, vid, pid, qty, price, cost, discount))
        total += gross - discount
        if status == 'CONCLUIDA':
            events[(store, pid)].append((when, -milli))
    if status == 'CONCLUIDA':
        methods = RNG.sample([1, 2, 3, 4, 5], 2) if vid % 7 == 0 else [RNG.choices([1, 2, 3, 4, 5], [15, 35, 23, 20, 7])[0]]
        first = total // 2 if len(methods) == 2 else total
        for index, method in enumerate(methods):
            amount = first if index == 0 else total - first
            payments.append((len(payments)+1, vid, method, amount, when))
rows('vendas', 'id loja_id cliente_id funcionario_id data_venda canal status', sales)
rows('itens_venda', 'id venda_id produto_id quantidade preco_unitario_centavos custo_unitario_centavos desconto_centavos', sale_items)
rows('pagamentos', 'id venda_id forma_pagamento_id valor_centavos data_pagamento', payments)

stocks = []
for store in range(1, 4):
    for pid in range(1, 121):
        current_delta = lowest = 0
        for _, movement in sorted(events[(store, pid)]):
            current_delta += movement
            lowest = min(lowest, current_delta)
        # O saldo inicial cobre o pior deficit cronologico, mais uma reserva variavel.
        minimum = (4 if by_product[pid][5] == 'KG' else 8) * 1000
        reserve = RNG.randint(0, 1500) if (pid + store) % 7 == 0 else RNG.randint(10000, 35000)
        if by_product[pid][5] == 'UN':
            reserve = (reserve // 1000) * 1000
        opening = -lowest + reserve
        stocks.append((store, pid, quantity(opening), quantity(opening + current_delta),
                       quantity(minimum), str(FINAL)))
rows('estoques', 'loja_id produto_id quantidade_inicial quantidade_atual quantidade_minima data_referencia', stocks)

schema = (BASE / 'esquema.sql').read_text(encoding='utf-8')
script = [
    '-- MERCADO BOM BAIRRO - base ficticia de estudo (SQLite).',
    '-- IMPORTANTE: execute em um banco NOVO/VAZIO; nao recrie em uma base ja populada.',
    '-- Alternativa simples: abra o arquivo mercado.db pronto no SQLiteOnline.',
    '-- Este script nao apaga tabelas existentes. Leia LEIA-ME.html.',
    'PRAGMA foreign_keys = ON;', 'BEGIN TRANSACTION;', schema,
]
for table, (columns, values) in TABLES.items():
    script.append(f'-- {table}: {len(values)} registros')
    # Blocos pequenos sao aceitos tanto pelo SQLite nativo quanto pelo editor web.
    for start in range(0, len(values), 100):
        group = values[start:start+100]
        script.append(f'INSERT INTO {table} ({", ".join(columns)}) VALUES\n' +
                      ',\n'.join('(' + ', '.join(quote(x) for x in row) + ')' for row in group) + ';')
script.extend(['COMMIT;', 'PRAGMA foreign_key_check;', 'PRAGMA integrity_check;',
               "SELECT 'Base pronta para estudar!' AS mensagem, COUNT(*) AS vendas FROM vendas;"])
sql = '\n\n'.join(script) + '\n'
(BASE / '01_mercado.sql').write_text(sql, encoding='utf-8')

path = BASE / 'mercado.db'
if path.exists():
    path.unlink()
with sqlite3.connect(path) as connection:
    connection.executescript(sql)
    assert connection.execute('PRAGMA integrity_check').fetchall() == [('ok',)]
    assert connection.execute('PRAGMA foreign_key_check').fetchall() == []
    assert connection.execute('SELECT COUNT(*) FROM sqlite_schema WHERE type="table"').fetchone()[0] == 15
print(f'Criados: {path.name}, 01_mercado.sql')
for table, (_, values) in TABLES.items():
    print(f'{table}: {len(values)}')
print(f'Total: {sum(len(values) for _, values in TABLES.values())} registros')
