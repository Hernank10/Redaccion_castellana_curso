#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
run.py - Wrapper para Python portable con ._pth (modo isolated).

Uso:
    E:\PythonPortable_Django5\python.exe run.py check
    E:\PythonPortable_Django5\python.exe run.py runserver 127.0.0.1:8007
    E:\PythonPortable_Django5\python.exe run.py migrate
    E:\PythonPortable_Django5\python.exe run.py shell
r"""
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lms_vector.settings")

if __name__ == "__main__":
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)