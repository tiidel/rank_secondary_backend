from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    
    def has_permission(self, request, view):
        
        if request.user.is_superuser:
            
            return True
        
        return False
    
    

from rest_framework import permissions


class IsStaff(permissions.BasePermission):
    
    def has_permission(self, request, view):
        
        if request.user.is_authenticated:
            
            return request.user.groups.filter(name='Staff').exists()
        
        return False
    
    

class IsTeacher(permissions.BasePermission):
    
    def has_permission(self, request, view):
        
        if request.user.is_authenticated:
            
            return request.user.groups.filter(name='Teacher').exists()
        
        return False


class IsAccountant(permissions.BasePermission):
    
    def has_permission(self, request, view):
        
        if request.user.is_authenticated:
            
            return request.user.groups.filter(name='Accountant').exists()
        
        return False


class IsSecretary(permissions.BasePermission):
    
    def has_permission(self, request, view):
        
        if request.user.is_authenticated:
            
            return request.user.groups.filter(name='Secretary').exists()
        
        return False


class IsGuardian(permissions.BasePermission):
    
    def has_permission(self, request, view):
        
        if request.user.is_authenticated:
            
            return request.user.groups.filter(name='Guardian').exists()
        
        return False
    

class IsStudent(permissions.BasePermission):
    
    def has_permission(self, request, view):
        
        if request.user.is_authenticated:
            
            return request.user.groups.filter(name='Student').exists()
        
        return False
    
