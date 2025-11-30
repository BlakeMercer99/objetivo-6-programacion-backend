from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.db.models import Q

from .models import Producto, Categoria, Pedido
from .forms import SolicitudPedidoForm


def index(request):
    productos_destacados = Producto.objects.filter(activo=True)[:6]
    categorias = Categoria.objects.all()
    return render(request, 'tienda/index.html', {
        'productos_destacados': productos_destacados,
        'categorias': categorias
    })


def catalogo(request):
    productos = Producto.objects.filter(activo=True)
    categorias = Categoria.objects.all()
    
    categoria_id = request.GET.get('categoria')
    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)
    
    return render(request, 'tienda/catalogo.html', {
        'productos': productos,
        'categorias': categorias,
        'categoria_actual': categoria_id
    })


def detalle_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id, activo=True)
    return render(request, 'tienda/detalle_producto.html', {'producto': producto})


class IndexView(ListView):
    model = Producto
    template_name = 'tienda/index.html'
    context_object_name = 'productos_destacados'
    
    def get_queryset(self):
        return Producto.objects.filter(activo=True)[:6]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categorias'] = Categoria.objects.all()
        return context


class CatalogoView(ListView):
    model = Producto
    template_name = 'tienda/catalogo.html'
    context_object_name = 'productos'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Producto.objects.filter(activo=True)
        categoria_id = self.request.GET.get('categoria')
        if categoria_id:
            queryset = queryset.filter(categoria_id=categoria_id)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categorias'] = Categoria.objects.all()
        context['categoria_actual'] = self.request.GET.get('categoria')
        return context


class DetalleProductoView(DetailView):
    model = Producto
    template_name = 'tienda/detalle_producto.html'
    context_object_name = 'producto'


class SolicitarPedidoView(CreateView):
    model = Pedido
    form_class = SolicitudPedidoForm
    template_name = 'tienda/solicitar_pedido.html'
    success_url = reverse_lazy('tienda:pedido_exitoso') # Asegurando namespace
    
    def get_initial(self):
        initial = super().get_initial()
        producto_id = self.request.GET.get('producto')
        if producto_id:
            try:
                producto = Producto.objects.get(id=producto_id)
                initial['producto_referencia'] = producto
            except Producto.DoesNotExist:
                pass
        return initial
    
    def form_valid(self, form):
        response = super().form_valid(form)
        # Guardar el ID y el token del pedido en la sesión 
        self.request.session['ultimo_pedido_id'] = self.object.id
        self.request.session['token_seguimiento'] = str(self.object.token_seguimiento)
        return response


def pedido_exitoso(request):
    pedido_id = request.session.get('ultimo_pedido_id')
    token_seguimiento = request.session.get('token_seguimiento')
    
    if not pedido_id or not token_seguimiento:
        return redirect('tienda:index') # Asegurando namespace
    
    try:
        pedido = Pedido.objects.get(id=pedido_id)
        
        # CORRECCIÓN: Usamos la URL relativa para evitar que Codespaces use 'localhost:8000'
        # El navegador agregará automáticamente el host de Codespaces.
        url_relativa = pedido.get_absolute_url()
        
        context = {
            'pedido': pedido,
            'url_seguimiento': url_relativa 
        }
        
        # Limpiar la sesión
        if 'ultimo_pedido_id' in request.session:
            del request.session['ultimo_pedido_id']
        if 'token_seguimiento' in request.session:
            del request.session['token_seguimiento']
            
        return render(request, 'tienda/pedido_exitoso.html', context)
    except Pedido.DoesNotExist:
        return redirect('tienda:index') # Asegurando namespace


def seguimiento_pedido(request, token):
    pedido = get_object_or_404(Pedido, token_seguimiento=token)
    context = {
        'pedido': pedido,
        'imagenes_referencia': pedido.imagenes_referencia.all()
    }
    return render(request, 'tienda/seguimiento_pedido.html', context)