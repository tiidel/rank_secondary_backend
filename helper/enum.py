
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
    
    Middleschool: Any = 'middleschool', 'Middleschool'
    
    JuniorHigh: Any = 'juniorhigh', 'JuniorHigh'
    
    Highschool: Any = 'highschool', 'Highschool'
    

class FeeInstallments(models.TextChoices):
    """--- How school fees is payed ---"""
    
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
    

