from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from rest_framework.permissions import BasePermission

from orders.models import Order

class IsOrderPending(BasePermission):
    
    message=_("Updating or deleting closed order is not allowed")

    def has_object_permission(self, request, view, obj):
        if view.action in ("retrieve"):
            return True
        return obj.status=="P"


class IsOrderItemBuyerOrAdmin(BasePermission):
    
    def has_permission(self, request, view):
        order_id=view.kwargs.get("order_id")
        order=get_object_or_404(Order,id=order_id)
        return order.buyer==request.user or request.user.is_staff 
    
    def has_object_permission(self, request, view, obj):
        return obj.order.buyer == request.user or request.user.is_staff

    
    
class IsOrderByBuyerOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated is True
    
    def has_object_permission(self,request,view,obj):
        return obj.buyer == request.user or request.user.is_staff
    
    

class IsOrderItemPending(BasePermission):
    message=_("Creating, updating, or deleting order items for a close order is not allowed")

    def has_permission(self, request, view):
        order_id=view.kwargs.get("order_id")
        order=get_object_or_404(Order,id=order_id)

        if view.action in ("list",):
            return True
        
        return order.status=="P"
    
    def has_object_permission(self, request, view, obj):
        if view.action in ("retrieve",):
            return True
        
        return obj.order.status=="P"