from django.shortcuts import render
from .models import Product, Cart, CartItem, Order, OrderItem
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from .serializers import ProductSerializer, CartSerializer, AddCartItemSerializer, OrderSerializer

# Create your views here.
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by('name')
    serializer_class = ProductSerializer


class CartViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

    @action(detail=True, methods=['post'], url_path='add-item')
    def add_item(self, request, pk=None):
 
        cart = self.get_object()
        serializer = AddCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data['quantity']
        
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
            
        cart_serializer = self.get_serializer(cart)
        return Response(cart_serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'], url_path='place-order')
    def place_order(self, request, pk=None):

        cart = self.get_object()

        with transaction.atomic():
            total_price = sum(
                item.product.price * item.quantity for item in cart.items.all()
            )

            order = Order.objects.create(
                customer_name=cart.customer_name,
                customer_address=cart.customer_address,
                total_price=total_price
            )

            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price * cart_item.quantity
                )

            cart.delete()

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
    

class OrderViewSet(mixins.ListModelMixin,   
                   mixins.RetrieveModelMixin,  
                   viewsets.GenericViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer