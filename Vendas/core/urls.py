# core/urls.py
from django.urls import path
from . import views

app_name = 'core' # Define o namespace para suas URLs

urlpatterns = [
    path('', views.index, name='index'), # Tela de Menu

    # URLs para Clientes
    path('clientes/', views.cliente_lista, name='cliente_lista'),
    path('clientes/novo/', views.cliente_criar, name='cliente_criar'),
    path('clientes/editar/<int:pk>/', views.cliente_editar, name='cliente_editar'),
    path('clientes/excluir/<int:pk>/', views.cliente_excluir, name='cliente_excluir'),

    # URLs para Produtos
    path('produtos/', views.produto_lista, name='produto_lista'),
    path('produtos/novo/', views.produto_criar, name='produto_criar'),
    path('produtos/editar/<int:pk>/', views.produto_editar, name='produto_editar'),
    path('produtos/excluir/<int:pk>/', views.produto_excluir, name='produto_excluir'),

    # URLs para Vendas
    path('vendas/', views.venda_lista, name='venda_lista'),
    path('vendas/nova/', views.venda_criar, name='venda_criar'),
    path('vendas/<int:pk>/', views.venda_detalhe, name='venda_detalhe'),

    # API para adicionar item na venda (usado na venda_criar)
    path('vendas/adicionar_item/', views.adicionar_item_venda, name='adicionar_item_venda'),
    path('vendas/remover_item/', views.remover_item_venda, name='remover_item_venda'),
]