from djongo import models as djm_models

from rest_meets_djongo import meta_manager

import pytest


@pytest.mark.core
class TestMetaManager(object):
    @pytest.fixture
    def generic_fixture(self):
        """Provides GenericModel usage for the test"""
        from tests.models import GenericModel
        return GenericModel()

    @pytest.fixture
    def object_id_fixture(self):
        """Provides ObjIDModel usage for the test"""
        from tests.models import ObjIDModel
        return ObjIDModel()

    @pytest.fixture
    def base_relational_fixture(self):
        """Provides relation model usage for the test"""
        from tests.models import RelationContainerModel
        return RelationContainerModel()

    @pytest.fixture
    def mfk_field_fixture(self, base_relational_fixture):
        """Allows for relational fixture's w/ many-to-one field testing"""
        from tests.models import ReverseRelatedModel
        return base_relational_fixture, ReverseRelatedModel()

    @pytest.fixture
    def embedded_fixture(self):
        from tests.models import ContainerModel, EmbedModel
        return ContainerModel(), EmbedModel()

    @pytest.mark.basic
    def test_get_model_meta(self, generic_fixture):
        """
        Here just to throw an error if Django changes how meta is accessed
        """
        test_meta = meta_manager.get_model_meta(generic_fixture)
        real_meta = generic_fixture._meta

        assert test_meta.__eq__(real_meta)

    @pytest.mark.basic
    def test_get_generic_model_field_info(self, generic_fixture):
        """
        Confirm that models with only basic field types are properly managed
        """
        field_info = meta_manager.get_field_info(generic_fixture)

        # Confirm that the automatically generated 'pk' field was captured
        assert field_info.pk.name == 'id'
        assert isinstance(field_info.pk, djm_models.AutoField)

        # Confirm field types were caught correctly
        field_type_dict = {
            'big_int': djm_models.BigIntegerField,
            'bool': djm_models.BooleanField,
            'char': djm_models.CharField,
            'comma_int': djm_models.CommaSeparatedIntegerField,
            'date': djm_models.DateField,
            'date_time': djm_models.DateTimeField,
            'decimal': djm_models.DecimalField,
            'email': djm_models.EmailField,
            'float': djm_models.FloatField,
            'integer': djm_models.IntegerField,
            'null_bool': djm_models.NullBooleanField,
            'pos_int': djm_models.PositiveIntegerField,
            'pos_small_int': djm_models.PositiveSmallIntegerField,
            'slug': djm_models.SlugField,
            'small_int': djm_models.SmallIntegerField,
            'text': djm_models.TextField,
            'time': djm_models.TimeField,
            'url': djm_models.URLField,
            'ip': djm_models.GenericIPAddressField,
            'uuid': djm_models.UUIDField,
        }

        for key, val in field_type_dict.items():
            assert isinstance(field_info.fields[key], val)

        # Confirm that the `fields_and_pk` parameter was built correctly
        field_and_pk_type_dict = {
            'pk': djm_models.AutoField,
            'id': djm_models.AutoField,
            'big_int': djm_models.BigIntegerField,
            'bool': djm_models.BooleanField,
            'char': djm_models.CharField,
            'comma_int': djm_models.CommaSeparatedIntegerField,
            'date': djm_models.DateField,
            'date_time': djm_models.DateTimeField,
            'decimal': djm_models.DecimalField,
            'email': djm_models.EmailField,
            'float': djm_models.FloatField,
            'integer': djm_models.IntegerField,
            'null_bool': djm_models.NullBooleanField,
            'pos_int': djm_models.PositiveIntegerField,
            'pos_small_int': djm_models.PositiveSmallIntegerField,
            'slug': djm_models.SlugField,
            'small_int': djm_models.SmallIntegerField,
            'text': djm_models.TextField,
            'time': djm_models.TimeField,
            'url': djm_models.URLField,
            'ip': djm_models.GenericIPAddressField,
            'uuid': djm_models.UUIDField,
        }

        for key, val in field_and_pk_type_dict.items():
            assert isinstance(field_info.fields_and_pk[key], val)

    @pytest.mark.basic
    def test_get_field_info_unique_pk(self, object_id_fixture):
        """
        Confirm that, if the pk is explicitly set in a model, it is caught
        and sorted correctly when fetching field info for said model
        """
        field_info = meta_manager.get_field_info(object_id_fixture)

        # Confirm that the user specified PK was caught
        assert field_info.pk.name == '_id'  # Custom name specified by user
        assert isinstance(field_info.pk, djm_models.ObjectIdField)

        # Confirm that the unique pk is still excluded from the fields
        assert '_id' not in field_info.fields

        # Confirm that said pk is still caught in fields_and_pk
        assert '_id' in field_info.fields_and_pk
        assert field_info.fields_and_pk['pk'].name == '_id'

    @pytest.mark.relation
    def test_get_fk_relation_field_info(self, generic_fixture, base_relational_fixture):
        """
        Tests that one-to-many relation information is correctly sorted
        and managed by the get_field_info() function
        """
        field_info = meta_manager.get_field_info(base_relational_fixture)

        # Confirm that one-to-many relations are handled correctly
        fk_field_info = field_info.relations['fk_field']
        assert isinstance(fk_field_info.model_field, djm_models.ForeignKey)
        assert fk_field_info.related_model == generic_fixture.__class__
        assert not fk_field_info.to_many
        assert (fk_field_info.to_field == 'id')  # Primary key in related model
        assert not fk_field_info.has_through_model
        assert not fk_field_info.reverse

    @pytest.mark.relation
    def test_get_mtm_relation_field_info(self, mfk_field_fixture):
        """
        Tests that many-to-many relation information is correctly sorted
        and managed by the get_field_info() function
        """
        field_info = meta_manager.get_field_info(mfk_field_fixture[0])

        # Confirm that the one-to-many relation was handled correctly
        mfk_field_info = field_info.relations['mfk_field']
        assert isinstance(mfk_field_info.model_field, djm_models.ManyToManyField)
        assert mfk_field_info.related_model == mfk_field_fixture[1].__class__
        assert mfk_field_info.to_many
        # Many-to-Many fields lack a `to_field` parameter
        assert not mfk_field_info.has_through_model
        assert not mfk_field_info.reverse

    @pytest.mark.embed
    def test_get_embed_model_field_info(self, embedded_fixture):
        """
        Tests that embedded model fields are correctly caught and managed
        """
        field_info = meta_manager.get_field_info(embedded_fixture[0])

        # Confirm that embedded model info was caught correctly
        embed_field_info = field_info.embedded['embed_field']
        assert embed_field_info.model_field.model_container == embedded_fixture[1].__class__
        assert not embed_field_info.is_array