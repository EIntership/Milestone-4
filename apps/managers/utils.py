import glob
import sys
from typing import Any

from dateutil import parser
from django.db.models import QuerySet, ForeignKey, ManyToManyField
from django.db.models import TextChoices
from rest_framework.serializers import Serializer


class Colors(TextChoices):
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RED = '\u001b[31m'
    YELLOW = '\u001b[33m'
