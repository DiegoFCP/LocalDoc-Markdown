from __future__ import annotations


class LocalDocError(Exception):
    """Base exception for user-safe LocalDoc failures."""

    user_message = "No se pudo completar la operacion."


class UnsupportedFileError(LocalDocError):
    user_message = "El formato del archivo no esta soportado."


class FileLimitError(LocalDocError):
    user_message = "El archivo o lote supera los limites configurados."


class InvalidStateTransitionError(LocalDocError):
    user_message = "El archivo no puede pasar al estado solicitado."


class ConversionFailedError(LocalDocError):
    user_message = "No se pudo convertir el documento."


class OcrUnavailableError(LocalDocError):
    user_message = "OCR no esta disponible en este equipo."

