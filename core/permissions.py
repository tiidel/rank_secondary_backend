from rest_framework import permissions


class IsStaff(permissions.BasePermission):
    
    def has_permission(self, request, view):
        
        if request.user.is_staff:
            
            return True
        
        return False
    
    

class Teacher(permissions.BasePermission):
    
    def has_permission(self, request, view):
        
        if request.user.is_teacher:
            
            return True
        
        return False