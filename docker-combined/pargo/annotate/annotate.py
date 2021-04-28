# MIT LINCENCE. 2021
#
# This file is part of an academic capstone project,reasosnd
# and it is made for AMD as part of efforts to automate
# the open source ROCM math libraries performance analytics.
# Contact The AMD rocm team for use and improvements on the project.
# The team: Victor Tuah Kumi, Aidan Forester, Javier Vite, Ahmed Iqbal
# Reach Victor Tuah Kumi on LinkedIn

"""Annotation factory for method arguments in library"""
from typing import Annotated, Union


class AnnotationFactory:
    """Annotate the arg variables"""
    def __init__(self, type_hint):
        self.type_hint = type_hint

    def __getitem__(self, key):
        if isinstance(key, tuple):
            return Annotated[(self.type_hint, ) + key]
        return Annotated[self.type_hint, key]

    def __repr__(self):
        return f"{self.__class__.__name__}({self.type_hint})"


STRING = Union[str, None]
PATH = AnnotationFactory(str)
PATH = PATH[('path',
            'path to .dat file for suite-data or .txt for specs info')]
PATH_LIST = AnnotationFactory(list)
PATH_LIST = PATH_LIST['strings']
DAT_FILE_PATH = Union[str, list, None]
STRING_LIST = AnnotationFactory(list)
STRING_LIST = STRING_LIST['strings']
DICT = AnnotationFactory(dict)
DICT = DICT['key: string, value: list']
STRING_TUPLE = AnnotationFactory(tuple)
STRING_TUPLE = STRING_TUPLE['strings']