from rest_framework import status

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from django.conf import settings
import os
from datetime import datetime


def format_serializer_errors(ser_errors):
    errors = []
    if isinstance(ser_errors, list):
        for i in ser_errors:
            for field, error in i.items():
                try:
                    errors.append(f'{field}: {error[0]}')
                except:
                    errors.append(f'{field}: {error}')

    elif isinstance(ser_errors, dict):
        for field, error in ser_errors.items():
            try:
                errors.append(f'{field}: {error[0]}')
            except:
                errors.append(f'{field}: {error}')
    return ', '.join(errors)


def success(self, msg):
    response = {
        "message": msg,
        "status": "success",
        "code": status.HTTP_200_OK
    }
    return response


def error(self, msg, errmsg=None):
    response = {
        "errmsg": str(errmsg),
        "message": str(msg),
        "status": "failed",
        "code": status.HTTP_400_BAD_REQUEST
    }
    return response

