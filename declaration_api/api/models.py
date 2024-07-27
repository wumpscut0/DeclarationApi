from django.db import models


class Declaration(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    header = models.CharField(max_length=1000)
    author = models.CharField(max_length=300)
    views = models.IntegerField()
    position = models.IntegerField()

    @staticmethod
    def get_jsonify_declaration_by_id(id_: str):
        declaration = Declaration.objects.get(id=id_)
        return {
            "id": id_,
            "header": declaration.header,
            "author": declaration.author,
            "views": declaration.views,
            "position": declaration.position,
        }
