from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator

from core.models import User, BaseModel
from helper.enum import SchoomMaterialCategory

# Create your models here.

class SchoolMaterial(BaseModel):
    """ --- MATERIALS THAT ARE VALUABLE FOR SELL --- """

    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    name = models.CharField(_("Name of the material being uploaded"), max_length=255, null=False, blank=False)

    category = models.CharField(_("Category Item belong e.g Book, Handout"), max_length=255, choices=SchoomMaterialCategory.choices)

    doc = models.FileField(upload_to="material", null=False, blank=False, validators=[FileExtensionValidator(['pdf', 'txt', 'docx'])])
    
    description = models.TextField(_("Describe your content"), max_length=5000, null=True, blank=True)

    price = models.FloatField(_("Price of the material"), default=0)

    prefered_level = models.ForeignKey('school.Level', on_delete=models.SET_NULL, null=True)

    sold = models.IntegerField(_("Number of copies of this item sold"), default=0)

    is_global = models.BooleanField(_("If this item should be global and accessed in other schools"), null=False, blank=False)

    is_downloadable = models.BooleanField(_("Can others save this material to their devices"), default=False)

    class Meta:
        ordering = ('sold',)
        verbose_name = _("SchoolMaterial")
        verbose_name_plural = _("SchoolMaterial")
        
    def __str__(self):
        return self.name
    

class Customer(BaseModel):
    """ --- SOMEONE WHO BUYS A PRODUCT AND THE PRODUCT THEY BAUGHT ---"""

    product = models.ForeignKey(SchoolMaterial, on_delete=models.CASCADE)

    buyer = models.ForeignKey(User, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        self.product.sold += 1
        self.product.save()


