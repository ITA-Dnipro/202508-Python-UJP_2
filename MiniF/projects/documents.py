from django_elasticsearch_dsl import Document, Index

from .models import StartupProject

from django_elasticsearch_dsl import fields

startup_index = Index('startup_projects')

@startup_index.doc_type

class StartupDocument(Document):
    """Document for StartupProject model"""

    startup_name = fields.TextField(
        attr="startup_profile_id.company_name",
        fields={
            "raw": fields.KeywordField(),
        }
    )

    class Django:

        model = StartupProject

        fields = [
            'title',
            'description',
            'status',
        ]
