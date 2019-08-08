from rest_meets_djongo.fields import ObjectIdField

from pytest import fixture, mark


@mark.basic
@mark.field
class TestObjectIDField(object):

    field = ObjectIdField()

    @fixture(scope='class')
    def object_id(self):
        from bson import ObjectId
        return ObjectId()

    def test_to_internal_value(self, object_id):
        """
        For object ID fields, the internal data should be an ObjectID
        object, appropriately formatted w/ MongoDB's setup.

        We use an ObjectID key generated by Djongo previously, utilizing
        its ObjectIDField (for models) to do so
        """
        new_obj = self.field.to_internal_value(str(object_id))

        assert new_obj.__eq__(object_id)

    def test_to_representation(self, object_id):
        """
        Confirm that object ID objects can still be reconstructed once
        serialized. This allows for them to be used as primary key queries
        by DRF (I.E. '/students/5d08078b1f7eb051eafe2390')
        """
        ref_id = str(object_id)
        obj_id = self.field.to_representation(object_id)

        assert ref_id == obj_id

    def test_conversion_equivalence(self, object_id):
        """
        Confirm that serialization and de-serialization of ObjectIDs is a
        lossless operation (and thus its use won't create unexpected
        behaviours) by default.
        """
        obj_repr = self.field.to_representation(object_id)
        new_obj = self.field.to_internal_value(obj_repr)

        assert object_id.__eq__(new_obj)

    @mark.error
    def test_invalid_rejection(self, error_raised):
        """
        Confirm that invalid ObjectID values are rejected when
        attempting to serialize them
        """
        # Not a string data
        not_a_key = True
        with error_raised:
            self.field.run_validation(not_a_key)

        # Key not in correct format
        bad_key = "wrong"
        with error_raised:
            self.field.run_validation(bad_key)
