
from typing import Any 

from django.utils.translation import gettext_lazy as _

from django.db import models



class ServerPlan(models.TextChoices):
    """--- Roles for Staff members ---"""
    
    Free: Any = 'free', 'Free'
    
    Standard: Any = 'standard', 'Standard'
    
    Premium: Any = 'premium', 'Premium'
    
    Promo: Any = 'promo', 'Promo'
    
    
    
class UserRole(models.TextChoices):
    """--- Roles for Staff members ---"""
    
    Teacher: Any = 'teacher', 'Teacher'
    
    Accountant: Any = 'accountant', 'Accountant'
    
    Secretary: Any = 'secretary', 'Secretary'
    
    Student: Any = 'student', 'Student'

    Guardian: Any = 'guardian', 'Guardian'

    Admin: Any = 'admin', 'Admin'

    Cleaner: Any = 'cleaner', 'Cleaner'

    Librarian: Any = 'librarian', 'Librarian'

    Driver: Any = 'driver', 'Driver'

    Cook: Any = 'cook', 'Cook'

    Gardener: Any = 'gardener', 'Gardener'

    Security: Any = 'security', 'Security'

    Nurse: Any = 'nurse', 'Nurse'

    Counselor: Any = 'counselor', 'Counselor'

    Other: Any = 'other', 'Other'


class GuardianType(models.TextChoices):
    """--- Type of guadian student has ---"""
    
    Mother: Any = 'mother', 'Mother'
    
    Father: Any = 'father', 'Father'
    
    Uncle: Any = 'uncle', 'Uncle'
    
    Aunt: Any = 'aunt', 'Aunt'
    
    Other: Any = 'other', 'Other'
    


class EducationType(models.TextChoices):
    """--- Type of school this is ---"""
    
    General: Any = 'general', 'General'
    
    Technical: Any = 'technical', 'Technical'
    
    Commercial: Any = 'commercial', 'Commercial'
    
    Other: Any = 'Other', 'Other'


class LevelChoices(models.TextChoices):
    """--- Levels in the school ---"""
    
    Nursery: Any = 'nursery', 'Nursery'

    Primary: Any = 'primary', 'Primary'
    
    Middleschool: Any = 'Middle School', 'Middle School'

    Form: Any = 'form', 'Form'
    
    JuniorHigh: Any = 'Junior High', 'Junior High'
    
    Highschool: Any = 'High School', 'High School'
    

class FeeInstallments(models.TextChoices):
    """--- How school fees is payed ---"""
    
    Non: Any = 'none', 'None'
    
    First: Any = 'first', 'First'
    
    Second: Any = 'second', 'Second'
    
    Complete: Any = 'complete', 'Complete'
    

class JobApplicantStatus(models.TextChoices):
    """--- Applicant status as application is forwarded ---"""
    
    Active: Any = 'active', 'Active'
    
    New: Any = 'new', 'New'
    
    Accepted: Any = 'accepted', 'Accepted'
    
    Low: Any = 'Low', 'Low'
    
    Unqualified: Any = 'unqualified', 'Unqualified'
    


# ============= COMMERCE ================

class SchoomMaterialCategory(models.TextChoices):
    """ --- Simple list of accepted Categories --- """

    Book: Any = 'book', 'Book'

    Merchandise: Any = 'merchandise', 'Merchandise'
    
    PastQuestion: Any = 'past question', 'PastQuestion'
    
    Tutorial: Any = 'tutorial', 'Tutorial'

