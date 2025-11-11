# core/admin.py
from django.contrib import admin
from .models import Cliente, Produto, Venda, ItemVenda

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'telefone')
    search_fields = ('nome', 'telefone')

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('descricao', 'valor', 'estoque')
    search_fields = ('descricao',)
    list_filter = ('estoque',)

class ItemVendaInline(admin.TabularInline):
    model = ItemVenda
    extra = 0 # Não mostra campos extras vazios por padrão
    fields = ('produto', 'quantidade', 'preco_unitario', 'total_item')
    readonly_fields = ('preco_unitario', 'total_item') # Valor e total são calculados

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('produto')


@admin.register(Venda)
class VendaAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'data_venda', 'valor_total')
    list_filter = ('data_venda', 'cliente')
    search_fields = ('cliente__nome',)
    inlines = [ItemVendaInline]
    readonly_fields = ('valor_total',) # O valor total será calculado automaticamente

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if not instance.pk: # Apenas para novos itens
                # Certifica que preco_unitario é o valor atual do produto
                instance.preco_unitario = instance.produto.valor
            instance.save()
        formset.save_m2m() # Salva relações many-to-many, se houver
        super().save_formset(request, form, formset, change)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Recalcula o valor_total da venda após salvar itens
        obj.valor_total = sum(item.total_item for item in obj.itens.all())
        obj.save()