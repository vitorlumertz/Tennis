"""Regressão: importar `match` antes de `tennisHelper` não deve quebrar.

Antes do fix isso lançava ImportError por causa do import circular entre
match.py e tennisHelper.py. Executar: python3 test_import_order.py
"""
import match  # noqa: F401  -- precisa ser o primeiro import do projeto
import tennisHelper  # noqa: F401

print("PASS: import de 'match' antes de 'tennisHelper' funciona")
