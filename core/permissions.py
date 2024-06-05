from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    
    def has_permission(self, request, view):
        
        if request.user.is_superuser:
            
            return True
        
        return False


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
    

class IsGeneral(permissions.BasePermission):

    def has_permission(self, request, view):
        
        if request.user.is_authenticated:
            
            return request.user.groups.filter(name='General').exists()
        
        return False
    

class IsCleaner(permissions.BasePermission):

    def has_permission(self, request, view):
        
        if request.user.is_authenticated:
            
            return request.user.groups.filter(name='Cleaner').exists()
        
        return False
    

class IsDriver(permissions.BasePermission):

    def has_permission(self, request, view):
        
        if request.user.is_authenticated:
            
            return request.user.groups.filter(name='Driver').exists()
        
        return False
    

class IsCook(permissions.BasePermission):
    
        def has_permission(self, request, view):
            
            if request.user.is_authenticated:
                
                return request.user.groups.filter(name='Cook').exists()
            
            return False
        

class IsGardener(permissions.BasePermission):
        
        def has_permission(self, request, view):
            
            if request.user.is_authenticated:
                
                return request.user.groups.filter(name='Gardener').exists()
            
            return False
        

class IsOtherStaff(permissions.BasePermission):

    def has_permission(self, request, view):
        
        if request.user.is_authenticated:
            
            return request.user.groups.filter(name='Other Staff').exists()
        
        return False
    

class IsOwner(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        
        if request.user.is_authenticated:
            
            return obj.owner == request.user
        
        return False
    

class IsLibrarian(permissions.BasePermission):

    def has_permission(self, request, view):
        
        if request.user.is_authenticated:
            
            return request.user.groups.filter(name='Librarian').exists()
        
        return False
    

class IsNurse(permissions.BasePermission):

    def has_permission(self, request, view):
        
        if request.user.is_authenticated:
            
            return request.user.groups.filter(name='Nurse').exists()
        
        return False
    

class IsCounselor(permissions.BasePermission):

    def has_permission(self, request, view):
        
        if request.user.is_authenticated:
            
            return request.user.groups.filter(name='Counselor').exists()
        
        return False
    

class IsSecurity(permissions.BasePermission):

    def has_permission(self, request, view):
        
        if request.user.is_authenticated:
            
            return request.user.groups.filter(name='Security').exists()
        
        return False
    

class IsStudentOrGuardian(permissions.BasePermission):
    
        def has_permission(self, request, view):
            
            if request.user.is_authenticated:
                
                return request.user.groups.filter(name='Student').exists() or request.user.groups.filter(name='Guardian').exists()
            
            return False
        

class IsStudentOrGuardianOrTeacher(permissions.BasePermission):

    def has_permission(self, request, view):
        
        if request.user.is_authenticated:
            
            return request.user.groups.filter(name='Student').exists() or request.user.groups.filter(name='Guardian').exists() or request.user.groups.filter(name='Teacher').exists()
        
        return False
    



