"""Valida a base de estudo e recria o relatório e a página de resultados.

Uso: python3 validar_banco.py
Usa apenas a biblioteca padrão. O banco em disco é aberto somente para leitura;
o script SQL completo é importado exclusivamente em um banco na memória.
"""

from collections import defaultdict
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from html import escape
from pathlib import Path
import hashlib
import re
import sqlite3


BASE = Path(__file__).resolve().parent
REFERENCE = "2026-09-30"
EXERCISE_MARKER = re.compile(r"^-- (E\d{2}):\s*(.+?)\s*$", re.MULTILINE)
MANUAL_HEADING = "VALIDAÇÃO NO NAVEGADOR — REGISTRO MANUAL"


def money(quantity, price):
    """Arredondamento decimal independente das expressões das views."""
    return int((Decimal(str(quantity)) * price).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def milli(value):
    return int((Decimal(str(value)) * 1000).to_integral_value())


def blocks(path):
    text = path.read_text(encoding="utf-8")
    markers = list(EXERCISE_MARKER.finditer(text))
    result = []
    for index, marker in enumerate(markers):
        end = markers[index + 1].start() if index + 1 < len(markers) else len(text)
        result.append((marker.group(1), marker.group(2), text[marker.end():end].strip()))
    return result


def run():
    previous_report = BASE / "validacao.txt"
    manual = ""
    if previous_report.exists():
        _, separator, content = previous_report.read_text(encoding="utf-8").partition(MANUAL_HEADING)
        current_hash = hashlib.sha256((BASE / "mercado.db").read_bytes()).hexdigest()
        if separator and f"SHA-256 da base: {current_hash}" in content:
            manual = content.strip()
    report = [
        "MERCADO BOM BAIRRO — VALIDAÇÃO LOCAL",
        "Base inteiramente fictícia; período: janeiro a setembro de 2026.",
        f"Referência do estoque: {REFERENCE}.",
        f"Motor utilizado nesta validação: SQLite {sqlite3.sqlite_version} (Python stdlib).",
        "Banco original aberto em modo somente leitura; reconstrução SQL em :memory:.",
        "Comando para repetir: python3 validar_banco.py",
        "",
    ]
    failures = []
    passed = 0

    def check(name, condition, detail=""):
        nonlocal passed
        status = "OK" if condition else "FALHOU"
        report.append(f"[{status}] {name}" + (f" — {detail}" if detail else ""))
        if condition:
            passed += 1
        else:
            failures.append(name)

    def no_rows(name, connection, query):
        rows = connection.execute(query).fetchall()
        check(name, not rows, f"{len(rows)} inconsistências" + (f"; amostra: {rows[:3]}" if rows else ""))

    connection = sqlite3.connect((BASE / "mercado.db").as_uri() + "?mode=ro", uri=True)
    connection.execute("PRAGMA query_only = ON")
    check("Integridade física", connection.execute("PRAGMA integrity_check").fetchall() == [("ok",)])
    no_rows("Chaves estrangeiras", connection, "PRAGMA foreign_key_check")

    tables = [row[0] for row in connection.execute(
        "SELECT name FROM sqlite_schema WHERE type = 'table' ORDER BY name")]
    views = [row[0] for row in connection.execute(
        "SELECT name FROM sqlite_schema WHERE type = 'view' ORDER BY name")]
    check("Estrutura esperada", len(tables) == 15 and len(views) == 4,
          f"{len(tables)} tabelas e {len(views)} views")
    report.append("")
    report.append("CONTAGENS DE REGISTROS")
    total = 0
    for table in tables:
        count = connection.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
        report.append(f"{table}: {count}")
        total += count
    report.extend([f"Total nas tabelas: {total}", "", "RECONSTRUÇÃO DO SCRIPT SQL"])

    memory = sqlite3.connect(":memory:")
    memory.executescript((BASE / "01_mercado.sql").read_text(encoding="utf-8"))
    memory.execute("PRAGMA query_only = ON")
    check("Importação completa de 01_mercado.sql", True)
    check("Integridade da reconstrução", memory.execute("PRAGMA integrity_check").fetchall() == [("ok",)])
    no_rows("Chaves estrangeiras da reconstrução", memory, "PRAGMA foreign_key_check")
    objects = "SELECT type, name, sql FROM sqlite_schema WHERE name NOT LIKE 'sqlite_%' ORDER BY type, name"
    check("Estruturas SQL idênticas", connection.execute(objects).fetchall() == memory.execute(objects).fetchall())
    for name in tables + views:
        original = sorted(connection.execute(f'SELECT * FROM "{name}"').fetchall(), key=repr)
        rebuilt = sorted(memory.execute(f'SELECT * FROM "{name}"').fetchall(), key=repr)
        check(f"Dados idênticos: {name}", original == rebuilt, f"{len(original)} linhas")

    report.extend(["", "CONSISTÊNCIA DOS NEGÓCIOS"])
    sales = {row[0]: row[1:] for row in connection.execute(
        "SELECT id, loja_id, cliente_id, funcionario_id, data_venda, canal, status FROM vendas")}
    payments = defaultdict(int)
    for sale_id, value in connection.execute("SELECT venda_id, valor_centavos FROM pagamentos"):
        payments[sale_id] += value
    totals = defaultdict(int)
    item_disagreements = []
    for item_id, sale_id, quantity, price, cost, discount, view_gross, view_total, view_cost in connection.execute("""
        SELECT i.id, i.venda_id, i.quantidade, i.preco_unitario_centavos,
               i.custo_unitario_centavos, i.desconto_centavos,
               v.bruto_centavos, v.total_centavos, v.custo_total_centavos
        FROM itens_venda i JOIN vw_itens_venda v ON v.item_venda_id = i.id
    """):
        gross = money(quantity, price)
        totals[sale_id] += gross - discount
        if (gross, gross - discount, money(quantity, cost)) != (view_gross, view_total, view_cost):
            item_disagreements.append(item_id)
    check("Valores dos itens versus cálculo decimal independente", not item_disagreements,
          f"{len(item_disagreements)} divergências")
    bad_payments = [sale_id for sale_id, sale in sales.items()
                    if sale[-1] == "CONCLUIDA" and payments[sale_id] != totals[sale_id]]
    cancelled_payments = [sale_id for sale_id, sale in sales.items()
                          if sale[-1] == "CANCELADA" and payments[sale_id] != 0]
    check("Pagamentos conferem exatamente em centavos", not bad_payments,
          f"{sum(sale[-1] == 'CONCLUIDA' for sale in sales.values())} vendas concluídas; "
          f"{len(bad_payments)} divergências")
    check("Vendas canceladas sem pagamentos", not cancelled_payments,
          f"{sum(sale[-1] == 'CANCELADA' for sale in sales.values())} canceladas; "
          f"{len(cancelled_payments)} com pagamento")
    for name, query in [
        ("Vendas com itens", "SELECT v.id FROM vendas v LEFT JOIN itens_venda i ON i.venda_id=v.id WHERE i.id IS NULL"),
        ("Compras com itens", "SELECT c.id FROM compras c LEFT JOIN itens_compra i ON i.compra_id=c.id WHERE i.id IS NULL"),
        ("Cadastro de cliente anterior à venda", "SELECT v.id FROM vendas v JOIN clientes c ON c.id=v.cliente_id WHERE c.data_cadastro>date(v.data_venda)"),
        ("Admissão anterior à venda", "SELECT v.id FROM vendas v JOIN funcionarios f ON f.id=v.funcionario_id WHERE f.data_admissao>date(v.data_venda)"),
        ("Funcionário caixa da mesma loja", "SELECT v.id FROM vendas v JOIN funcionarios f ON f.id=v.funcionario_id WHERE f.loja_id<>v.loja_id OR f.cargo<>'CAIXA'"),
        ("Abertura da loja anterior às vendas", "SELECT v.id FROM vendas v JOIN lojas l ON l.id=v.loja_id WHERE l.data_abertura>date(v.data_venda)"),
        ("Abertura da loja anterior às compras", "SELECT c.id FROM compras c JOIN lojas l ON l.id=c.loja_id WHERE l.data_abertura>c.data_pedido"),
        ("Pagamento na data e hora da venda", "SELECT p.id FROM pagamentos p JOIN vendas v ON v.id=p.venda_id WHERE p.data_pagamento<>v.data_venda"),
        ("Fornecedor autorizado para cada item de compra", "SELECT i.id FROM itens_compra i JOIN compras c ON c.id=i.compra_id LEFT JOIN produto_fornecedores pf ON pf.fornecedor_id=c.fornecedor_id AND pf.produto_id=i.produto_id WHERE pf.produto_id IS NULL OR i.fornecedor_id<>c.fornecedor_id"),
        ("Um fornecedor principal por produto", "SELECT p.id FROM produtos p LEFT JOIN produto_fornecedores pf ON pf.produto_id=p.id AND pf.principal=1 GROUP BY p.id HAVING COUNT(pf.fornecedor_id)<>1"),
        ("Status e recebimento das compras", "SELECT id FROM compras WHERE (status='RECEBIDA' AND (data_recebimento IS NULL OR data_recebimento<data_pedido)) OR (status<>'RECEBIDA' AND data_recebimento IS NOT NULL)"),
        ("Delivery e retirada com cliente identificado", "SELECT id FROM vendas WHERE canal IN ('DELIVERY','RETIRADA') AND cliente_id IS NULL"),
        ("Produtos inativos sem vendas", "SELECT i.id FROM itens_venda i JOIN produtos p ON p.id=i.produto_id WHERE p.ativo=0"),
        ("Dinheiro em centavos inteiros nos pagamentos", "SELECT id FROM pagamentos WHERE valor_centavos<=0 OR typeof(valor_centavos)<>'integer'"),
        ("Dinheiro em centavos inteiros nos itens", "SELECT id FROM itens_venda WHERE typeof(preco_unitario_centavos)<>'integer' OR typeof(custo_unitario_centavos)<>'integer' OR typeof(desconto_centavos)<>'integer'"),
    ]:
        no_rows(name, connection, query)

    dates_count = 0
    invalid_dates = []
    for table, columns in [
        ("lojas", ["data_abertura"]), ("clientes", ["data_cadastro", "data_nascimento"]),
        ("funcionarios", ["data_admissao"]), ("compras", ["data_pedido", "data_recebimento"]),
        ("vendas", ["data_venda"]), ("pagamentos", ["data_pagamento"]),
        ("estoques", ["data_referencia"]),
    ]:
        for column in columns:
            for row_id, value in connection.execute(f"SELECT rowid,{column} FROM {table} WHERE {column} IS NOT NULL"):
                dates_count += 1
                try:
                    datetime.fromisoformat(value)
                except ValueError:
                    invalid_dates.append((table, column, row_id))
    check("Datas válidas", not invalid_dates, f"{dates_count} datas examinadas")

    for table, columns in [
        ("itens_venda", ["quantidade"]), ("itens_compra", ["quantidade"]),
        ("estoques", ["quantidade_inicial", "quantidade_atual", "quantidade_minima"]),
    ]:
        invalid = []
        for column in columns:
            for row_id, value, unit in connection.execute(
                f"SELECT i.rowid,i.{column},p.unidade FROM {table} i JOIN produtos p ON p.id=i.produto_id"
            ):
                number = Decimal(str(value))
                if number * 1000 != (number * 1000).to_integral_value() or (
                    unit == "UN" and number != number.to_integral_value()
                ):
                    invalid.append((row_id, column))
        check(f"Quantidades de {table}: UN inteiras e KG até 3 casas", not invalid,
              f"{len(invalid)} inconsistências")

    stocks = {(row[0], row[1]): row[2:] for row in connection.execute(
        "SELECT loja_id, produto_id, quantidade_inicial, quantidade_atual, data_referencia FROM estoques")}
    check("Todas as combinações de loja e produto possuem estoque", len(stocks) ==
          connection.execute("SELECT COUNT(*) FROM lojas").fetchone()[0] *
          connection.execute("SELECT COUNT(*) FROM produtos").fetchone()[0], f"{len(stocks)} posições")
    events = defaultdict(list)
    for store, product, purchase, received, quantity in connection.execute("""
        SELECT c.loja_id, i.produto_id, c.id, c.data_recebimento, i.quantidade
        FROM compras c JOIN itens_compra i ON i.compra_id=c.id WHERE c.status='RECEBIDA'
    """):
        events[(store, product)].append((received + " 06:00:00", milli(quantity), "compra", purchase))
    for store, product, sale_id, when, quantity in connection.execute("""
        SELECT v.loja_id, i.produto_id, v.id, v.data_venda, i.quantidade
        FROM vendas v JOIN itens_venda i ON i.venda_id=v.id WHERE v.status='CONCLUIDA'
    """):
        events[(store, product)].append((when, -milli(quantity), "venda", sale_id))
    final_errors, negative_balances = [], []
    minimum = None
    bad_references = []
    for key, (opening, current, reference) in stocks.items():
        balance = milli(opening)
        minimum = balance if minimum is None else min(minimum, balance)
        if reference != REFERENCE:
            bad_references.append(key)
        for when, change, kind, origin in sorted(events[key]):
            balance += change
            minimum = min(minimum, balance)
            if balance < 0:
                negative_balances.append((key, when, kind, origin, balance))
        if balance != milli(current):
            final_errors.append((key, balance, milli(current)))
    check("Movimentos cobertos pelo cadastro de estoque", not set(events).difference(stocks))
    check("Data de referência dos estoques", not bad_references, REFERENCE)
    check("Saldo inicial + compras recebidas - vendas concluídas = saldo final", not final_errors,
          f"{len(stocks)} posições; {len(final_errors)} divergências")
    check("Estoque cronológico nunca negativo", not negative_balances,
          f"{sum(map(len, events.values()))} movimentos; mínimo {minimum / 1000:g}; "
          "recebimentos às 06:00 e vendas no horário registrado")

    report.extend(["", "EXECUÇÃO DAS 32 RESPOSTAS DO GABARITO"])
    answers = blocks(BASE / "03_gabarito.sql")
    check("Identificadores E01 a E32, únicos e em ordem", [row[0] for row in answers] ==
          [f"E{number:02d}" for number in range(1, 33)])
    questions = {identifier: body for identifier, _, body in blocks(BASE / "02_exercicios.sql")}
    results = []
    for identifier, title, body in answers:
        # sqlite3.execute recusa múltiplas instruções; query_only impede alterações.
        sql = "\n".join(line for line in body.splitlines() if not line.lstrip().startswith("--")).strip()
        try:
            if not re.match(r"^(SELECT|WITH)\b", sql, re.IGNORECASE):
                raise ValueError("A resposta precisa ser SELECT ou WITH.")
            cursor = connection.execute(sql)
            rows = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            check(f"{identifier}: {title}", True,
                  f"{len(rows)} {'linha' if len(rows) == 1 else 'linhas'}; uma consulta de leitura")
            if identifier in ("E31", "E32"):
                check(f"{identifier} retorna zero inconsistências", not rows, f"{len(rows)} linhas")
            question_lines = []
            for line in questions.get(identifier, "").splitlines():
                if line.startswith("-- Dica:"):
                    break
                if line.startswith("-- "):
                    question_lines.append(line[3:])
            results.append((identifier, title, " ".join(question_lines), sql, columns, rows))
        except (sqlite3.Error, ValueError, TypeError) as error:
            check(f"{identifier}: execução", False, str(error))

    report.extend(["", f"RESULTADO: {passed} verificações aprovadas; {len(failures)} falhas."])
    if failures:
        report.extend(["Falhas:"] + [f"- {name}" for name in failures])
    else:
        report.append("Base e respostas aprovadas em todas as verificações acima.")
        (BASE / "04_resultados_esperados.html").write_text(render_html(results), encoding="utf-8")
        report.append("04_resultados_esperados.html recriado a partir das consultas executadas.")
    summary = f"RESULTADO: {passed} verificações aprovadas; {len(failures)} falhas."
    if manual:
        report.extend(["", MANUAL_HEADING, manual])
    (BASE / "validacao.txt").write_text("\n".join(report) + "\n", encoding="utf-8")
    memory.close()
    connection.close()
    print(summary)
    if failures:
        raise SystemExit(1)


def cell(value, column):
    if value is None:
        return '<td class="null"><span>NULL</span></td>'
    if isinstance(value, (int, float)):
        if "reais" in column or "percentual" in column:
            display = f"{value:.2f}"
        elif isinstance(value, float):
            display = f"{value:.12g}"
        else:
            display = str(value)
        return f'<td class="number">{escape(display)}</td>'
    return f"<td>{escape(str(value))}</td>"


def render_html(results):
    cards = []
    for identifier, title, question, sql, columns, rows in results:
        total = len(rows)
        if total:
            headers = "".join(f'<th scope="col">{escape(column)}</th>' for column in columns)
            body = "".join("<tr>" + "".join(cell(value, column) for value, column in zip(row, columns)) + "</tr>"
                           for row in rows[:10])
            table = f'<div class="table-scroll" tabindex="0" aria-label="Resultado {identifier}"><table><thead><tr>{headers}</tr></thead><tbody>{body}</tbody></table></div>'
            preview = (f"Prévia: primeiras 10 de {total} linhas, na ordem da consulta."
                       if total > 10 else f"Resultado completo: {total} {'linha' if total == 1 else 'linhas'}.")
        else:
            table = '<p class="empty">Nenhuma linha. A consulta de conferência não encontrou inconsistências.</p>'
            preview = "Resultado completo: 0 linhas. Este é o resultado esperado."
        cards.append(f'''<article id="{identifier}" class="exercise">
<div class="exercise-top"><span class="id">{identifier}</span><span class="count">{total} {'linha' if total == 1 else 'linhas'} no total</span></div>
<h2>{escape(title)}</h2><p class="question">{escape(question)}</p>
<p class="preview">{escape(preview)}</p>{table}
<details><summary>Ver a consulta do gabarito</summary><pre><code>{escape(sql)}</code></pre></details>
<a class="top-link" href="#indice">Voltar ao índice ↑</a></article>''')
    navigation = "".join(f'<a href="#{identifier}" title="{escape(title, quote=True)}">{identifier}</a>'
                         for identifier, title, *_ in results)
    return '''<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light"><title>Resultados esperados · Mercado Bom Bairro</title>
<style>
:root{--ink:#183038;--muted:#52666a;--paper:#f6f5ee;--line:#d9e2dc;--green:#176953;--mint:#e6f2e8;--navy:#132e36;--orange:#f6c06a}
*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:24px}body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.65 ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}.wrap{width:min(1160px,calc(100% - 40px));margin:auto}header{background:var(--navy);color:#f9faf2;padding:46px 0 38px}.eyebrow{color:#f6d399;font-size:.77rem;font-weight:750;letter-spacing:.15em;text-transform:uppercase}h1{font-size:clamp(2rem,5vw,3.4rem);line-height:1.1;letter-spacing:-.035em;margin:15px 0 20px}header p{max-width:820px;color:#d0e0d7;margin-bottom:0}a{color:var(--green);text-underline-offset:3px}header a{display:inline-block;color:#f6d399;margin-top:22px}a:focus-visible,summary:focus-visible,[tabindex]:focus-visible{outline:3px solid #c4841b;outline-offset:4px}main{padding-bottom:30px}.intro{margin:28px 0;padding:18px 22px;background:var(--mint);border-left:4px solid var(--green);border-radius:0 12px 12px 0}.intro p{margin:0}.intro code{background:#f7fbf5;padding:1px 5px;border-radius:4px}nav{padding:6px 0 28px;display:grid;grid-template-columns:repeat(16,1fr);gap:7px}nav a{display:block;text-align:center;padding:7px 4px;background:#fff;border:1px solid var(--line);border-radius:7px;font-size:.78rem;font-weight:750;text-decoration:none}nav a:hover{background:var(--mint)}.exercise{padding:28px;background:white;border:1px solid var(--line);border-radius:16px;margin-bottom:22px;min-width:0}.exercise-top{display:flex;align-items:center;justify-content:space-between;gap:12px}.id{font-size:.78rem;letter-spacing:.06em;font-weight:800;background:var(--mint);color:var(--green);padding:4px 9px;border-radius:6px}.count{font-size:.78rem;color:var(--muted)}h2{font-size:1.45rem;line-height:1.25;letter-spacing:-.02em;margin:17px 0 12px}.question{font-size:.94rem;color:var(--muted);max-width:970px;margin:0 0 18px}.preview{font-size:.81rem;font-weight:700;margin:0 0 12px;color:var(--green)}.table-scroll{overflow:auto;border:1px solid var(--line);border-radius:10px;max-width:100%}table{border-collapse:collapse;width:100%;text-align:left;font-size:.82rem;line-height:1.45}th,td{padding:11px 13px;border-bottom:1px solid #e6ebe5;vertical-align:top}th{background:#edf2ec;color:#27483f;white-space:nowrap}tr:last-child td{border-bottom:0}tbody tr:nth-child(even){background:#fafbf8}.number{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}.null span{display:inline-block;padding:1px 6px;font:700 .72rem ui-monospace,monospace;letter-spacing:.04em;border:1px dashed #89979a;background:#f0f2f2;color:#566469;border-radius:4px}.empty{padding:18px 20px;background:var(--mint);border-radius:10px;font-size:.93rem;color:var(--green);margin:0}details{margin-top:20px;border-top:1px solid var(--line);padding-top:15px}summary{font-size:.85rem;font-weight:700;cursor:pointer}pre{background:#102830;color:#e7f6ee;padding:18px;border-radius:10px;overflow:auto;font:13px/1.6 ui-monospace,SFMono-Regular,Consolas,monospace;margin:14px 0 0}.top-link{display:inline-block;font-size:.78rem;margin-top:16px}footer{padding:0 0 35px;color:var(--muted);font-size:.8rem}footer p{margin-bottom:8px}@media(max-width:900px){nav{grid-template-columns:repeat(8,1fr)}}@media(max-width:580px){.wrap{width:calc(100% - 28px)}header{padding:30px 0}.exercise{padding:20px 16px}nav{grid-template-columns:repeat(4,1fr)}h2{font-size:1.25rem}th,td{padding:10px}pre{font-size:12px}.intro{padding:16px}table{font-size:.77rem}}@media print{body{background:white;font-size:10pt}header{background:white;color:var(--ink);padding:0}header p{color:var(--muted)}header a,nav,.top-link,details{display:none}.wrap{width:100%}.exercise{border-radius:0;break-inside:avoid;padding:15px;margin-top:15px}.table-scroll{overflow:visible}table{font-size:8pt}th,td{padding:6px}.intro{margin:15px 0}}
</style></head><body>
<header><div class="wrap"><div class="eyebrow">Mercado Bom Bairro · laboratório de SQL</div>
<h1>Confira o que sua consulta devolveu.</h1><p>Resultados das 32 respostas executadas sobre a base original. Compare as colunas, a ordem e a quantidade de linhas com o que apareceu no SQLiteOnline.</p>
<a href="LEIA-ME.html">← Voltar ao guia de estudo</a></div></header>
<main class="wrap"><aside class="intro"><p><strong>Como conferir:</strong> até 10 linhas, o resultado está completo. Acima disso, mostramos uma prévia das primeiras 10 e informamos o total. <code>NULL</code> indica ausência de valor. Valores em colunas com “reais” têm duas casas decimais. E31 e E32 devem retornar zero linhas.</p></aside>
<nav id="indice" aria-label="Escolher exercício">''' + navigation + '''</nav>
''' + "\n".join(cards) + '''</main><footer class="wrap"><p>Resultados calculados com o SQLite da biblioteca padrão do Python. Os dados cobrem janeiro a setembro de 2026; o estoque é um retrato de 30/09/2026.</p>
<p>Se você alterar a base, os resultados poderão mudar. Para recriar esta página e o relatório, execute <code>python3 validar_banco.py</code> na pasta do pacote.</p>
<a href="LEIA-ME.html">Guia de estudo</a> · <a href="03_gabarito.sql">Consultas do gabarito</a> · <a href="validacao.txt">Relatório de validação</a></footer>
</body></html>
'''


if __name__ == "__main__":
    run()
