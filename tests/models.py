from djongo import models


# --- Basic Models --- #
# Generic, DRF compliant model, with all DRF fields
class GenericModel(models.Model):
    big_int = models.BigIntegerField()
    bool = models.BooleanField()
    char = models.CharField()
    comma_int = models.CommaSeparatedIntegerField()
    date = models.DateField()
    date_time = models.DateTimeField()
    decimal = models.DecimalField(max_digits=10, decimal_places=5)
    email = models.EmailField()
    float = models.FloatField()
    integer = models.IntegerField()
    null_bool = models.NullBooleanField()
    pos_int = models.PositiveIntegerField()
    pos_small_int = models.PositiveSmallIntegerField()
    slug = models.SlugField()
    small_int = models.SmallIntegerField()
    text = models.TextField()
    time = models.TimeField()
    url = models.URLField()
    ip = models.GenericIPAddressField()
    uuid = models.UUIDField()

    # TODO: add these
    # basic_file = models.FileField()
    # image = models.ImageField()

    objects = models.DjongoManager()


# Model with its primary key set as its ObjectID
class ObjIDModel(models.Model):
    _id = models.ObjectIdField()
    int_field = models.IntegerField()
    char_field = models.CharField(max_length=5)

    objects = models.DjongoManager()


# Model a variant for DRF standard arguments
class OptionsModel(models.Model):
    db_column_id = models.ObjectIdField(db_column='_id')
    null_char = models.CharField(null=True)
    blank_char = models.TextField(blank=True)
    choice_char = models.CharField(choices=['Foo', 'Bar', 'Baz'])
    default_email = models.EmailField(default='noonecares@no.nope')
    read_only_int = models.IntegerField(editable=False)
    # NOTE: By default, custom error messages are not conserved. This is
    # just here to make sure it does not crash the serializer
    custom_error = models.IntegerField(error_messages={
        'blank': 'You tried to submit a blank integer, you dingus'
    })
    help_char = models.CharField(help_text='Super helpful text')
    unique_int = models.IntegerField(unique=True)

    objects = models.DjongoManager()


# --- Embedded Model Containing Models --- #
# Model for use w/ testing embedded models
class EmbedModel(models.Model):
    _id = models.ObjectIdField(primary_key=False)
    int_field = models.IntegerField()
    char_field = models.CharField(max_length=5)

    objects = models.DjongoManager()

    def __eq__(self, other):
        return (isinstance(other, EmbedModel) and
                self.char_field == other.char_field and
                self.int_field == other.int_field)

    def __str__(self):
        return str(self._id) + ":" + str(self.int_field) + "-" + str(self.char_field)

    class Meta:
        abstract = True


# Model for use w/ testing nested embedded models,
class ContainerModel(models.Model):
    _id = models.ObjectIdField()
    embed_field = models.EmbeddedModelField(model_container=EmbedModel)

    objects = models.DjongoManager()

    def __str__(self):
        return str(self._id) + "-(" + str(self.embed_field) + ")"


# Model for testing w/ embedded models which contain other embedded models
class DeepContainerModel(models.Model):
    str_id = models.CharField(primary_key=True)
    deep_embed = models.EmbeddedModelField(model_container=ContainerModel)

    objects = models.DjongoManager()


# Model for use w/ testing nested arrays of embedded models,
class ArrayContainerModel(models.Model):
    _id = models.ObjectIdField()
    embed_list = models.ArrayModelField(model_container=EmbedModel)

    objects = models.DjongoManager()


# A model with both an abstract and non-abstract embedded model
# Both should still function, one simply also has a pk which needs to
# be used and validated
class DualEmbedModel(models.Model):
    _id = models.ObjectIdField()
    generic_val = models.EmbeddedModelField(
        model_container=GenericModel
    )
    embed_val = models.EmbeddedModelField(
        model_container=EmbedModel
    )

    objects = models.DjongoManager()


# --- Relation Containing Models --- #
# Model with a reverse relation (see RelationContainerModel)
class ReverseRelatedModel(models.Model):
    _id = models.ObjectIdField()
    boolean = models.BooleanField(default=True)

    objects = models.DjongoManager()


# Model with most types of relations
class RelationContainerModel(models.Model):
    _id = models.ObjectIdField()
    fk_field = models.ForeignKey(to=GenericModel,
                                 on_delete=models.CASCADE)
    mfk_field = models.ManyToManyField(to=ReverseRelatedModel,
                                       blank=True,
                                       related_name='container_field')

    objects = models.DjongoManager()
