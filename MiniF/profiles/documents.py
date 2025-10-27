from django_elasticsearch_dsl import Document, Index

from .models import StartupProfile

from django_elasticsearch_dsl import fields

startup_index = Index('startup_profiles')



@startup_index.doc_type

class StartupDocument(Document):
    """Document for StartupProfile model"""

    industry_name = fields.TextField(
        attr="industry_id.industry_name",
        fields={
            "raw": fields.KeywordField(),
        }
    )

    class Django:

        model = StartupProfile

        fields = [
            'company_name',
            'description',
            'location',
        ]
