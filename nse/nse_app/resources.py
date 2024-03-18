from import_export import resources
from .models import IndexPrice,Index

class indexresources (resources.ModelResource):
    class Meta:
        model = IndexPrice

class Indexresources (resources.ModelResource):
    class Meta:
        model = Index