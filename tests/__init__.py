"""Pacote de testes.

Faz duas coisas ao ser importado (antes de qualquer teste rodar):
  1. Garante a raiz do projeto no sys.path.
  2. Instala stubs leves para as dependências externas da integração com
     Google Sheets (gspread, oauth2client, googleapiclient), permitindo importar
     o pacote GoogleSheets sem rede nem credenciais.

pandas e reportlab são dependências reais de tennis_manager e não são stubadas.
"""
import os
import sys
import types

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def _missing(name):
    try:
        __import__(name)
        return False
    except ImportError:
        return True


def _module(name):
    mod = types.ModuleType(name)
    sys.modules[name] = mod
    return mod


# oauth2client.service_account --------------------------------------------
if _missing("oauth2client"):
    oauth2client = _module("oauth2client")
    service_account = _module("oauth2client.service_account")

    class _ServiceAccountCredentials:
        @staticmethod
        def from_json_keyfile_name(*args, **kwargs):
            raise RuntimeError("stub: credenciais não disponíveis em testes")

    service_account.ServiceAccountCredentials = _ServiceAccountCredentials
    oauth2client.service_account = service_account


# googleapiclient.discovery -----------------------------------------------
if _missing("googleapiclient"):
    googleapiclient = _module("googleapiclient")
    discovery = _module("googleapiclient.discovery")

    discovery.build = lambda *a, **k: None

    class _Resource:
        pass

    discovery.Resource = _Resource
    googleapiclient.discovery = discovery


# gspread + gspread.utils --------------------------------------------------
if _missing("gspread"):
    gspread = _module("gspread")

    class _Client:
        pass

    class _Spreadsheet:
        pass

    gspread.Client = _Client
    gspread.Spreadsheet = _Spreadsheet
    gspread.authorize = lambda *a, **k: None

    utils = _module("gspread.utils")

    def rowcol_to_a1(row, col):
        letters = ""
        c = col
        while c > 0:
            c, rem = divmod(c - 1, 26)
            letters = chr(65 + rem) + letters
        return f"{letters}{row}"

    utils.rowcol_to_a1 = rowcol_to_a1

    class _ValueInputOption:
        class raw:
            value = "RAW"

        class user_entered:
            value = "USER_ENTERED"

    utils.ValueInputOption = _ValueInputOption
    gspread.utils = utils
