from django.contrib import admin
from django.utils.html import format_html
from .models import Categoria, Producto, Insumo, Pedido, ImagenReferencia


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'descripcion_corta']
    search_fields = ['nombre']
    
    def descripcion_corta(self, obj):
        return obj.descripcion[:50] + '...' if len(obj.descripcion) > 50 else obj.descripcion
    descripcion_corta.short_description = 'Descripción'


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'categoria', 'precio_base', 'activo', 'imagen_preview']
    list_filter = ['categoria', 'activo']
    search_fields = ['nombre', 'descripcion']
    list_editable = ['activo']
    
    def imagen_preview(self, obj):
        if obj.imagen_1:
            return format_html('<img src="{}" width="50" height="50" />', obj.imagen_1.url)
        return "Sin imagen"
    imagen_preview.short_description = 'Imagen'


class ImagenReferenciaInline(admin.TabularInline):
    model = ImagenReferencia
    extra = 1
    readonly_fields = ['fecha_subida']


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'nombre_cliente', 'estado_pedido', 'estado_pago',
        'plataforma', 'fecha_creacion', 'token_corto'
    ]
    list_filter = ['estado_pedido', 'estado_pago', 'plataforma', 'fecha_creacion']
    search_fields = ['nombre_cliente', 'email', 'token_seguimiento']
    readonly_fields = ['token_seguimiento', 'fecha_creacion', 'fecha_actualizacion']
    inlines = [ImagenReferenciaInline]

    fieldsets = (
        ('Información del Cliente', {
            'fields': ('nombre_cliente', 'email', 'telefono', 'red_social')
        }),
        ('Detalles del Pedido', {
            'fields': ('producto_referencia', 'descripcion_diseno', 'fecha_requerida', 'plataforma')
        }),
        ('Estados', {
            'fields': ('estado_pedido', 'estado_pago')
        }),
        ('Información Adicional', {
            'fields': ('presupuesto_aprobado', 'notas_internas')
        }),
        ('Metadatos', {
            'fields': ('token_seguimiento', 'fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )

    def token_corto(self, obj):
        return str(obj.token_seguimiento)[:8] + '...'
    token_corto.short_description = 'Token'


@admin.register(Insumo)
class InsumoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tipo', 'cantidad_disponible', 'unidad', 'estado_stock']
    list_filter = ['tipo', 'unidad']
    search_fields = ['nombre']
    list_editable = ['cantidad_disponible']
    
    def estado_stock(self, obj):
        if obj.cantidad_disponible == 0:
            return format_html('<span style="color: red;">⏹️ Sin stock</span>')
        elif obj.cantidad_disponible < 10:
            return format_html('<span style="color: orange;">⚠️ Bajo stock</span>')
        else:
            return format_html('<span style="color: green;">✅ En stock</span>')
    estado_stock.short_description = 'Estado'


@admin.register(ImagenReferencia)
class ImagenReferenciaAdmin(admin.ModelAdmin):
    list_display = ['pedido', 'descripcion', 'fecha_subida', 'imagen_preview']
    list_filter = ['fecha_subida']
    
    def imagen_preview(self, obj):
        if obj.imagen:
            return format_html('<img src="{}" width="50" height="50" />', obj.imagen.url)
        return "Sin imagen"
    imagen_preview.short_description = 'Vista previa'


# Personalización del panel
admin.site.site_header = "Administración de Tienda Personalizados"
admin.site.site_title = "Tienda Personalizados"
admin.site.index_title = "Panel de Control"
