# core/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json

from .models import Cliente, Produto, Venda, ItemVenda
from .forms import ClienteForm, ProdutoForm, VendaForm, ItemVendaForm

# --- Views Gerais ---

def index(request):
    """ Tela de Menu Principal """
    return render(request, 'core/index.html')

# --- Views de Cliente (CRUD) ---

def cliente_lista(request):
    clientes = Cliente.objects.all().order_by('nome')
    return render(request, 'core/cliente_list.html', {'clientes': clientes})

def cliente_criar(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente cadastrado com sucesso!')
            return redirect('core:cliente_lista')
    else:
        form = ClienteForm()
    return render(request, 'core/cliente_form.html', {'form': form, 'titulo': 'Novo Cliente'})

def cliente_editar(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente atualizado com sucesso!')
            return redirect('core:cliente_lista')
    else:
        form = ClienteForm(instance=cliente)
    return render(request, 'core/cliente_form.html', {'form': form, 'titulo': 'Editar Cliente'})

@require_POST
def cliente_excluir(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    try:
        cliente.delete()
        messages.success(request, 'Cliente excluído com sucesso!')
    except Exception as e:
        messages.error(request, f'Não foi possível excluir o cliente: {e}')
    return redirect('core:cliente_lista')

# --- Views de Produto (CRUD) ---

def produto_lista(request):
    produtos = Produto.objects.all().order_by('descricao')
    return render(request, 'core/produto_list.html', {'produtos': produtos})

def produto_criar(request):
    if request.method == 'POST':
        form = ProdutoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Produto cadastrado com sucesso!')
            return redirect('core:produto_lista')
    else:
        form = ProdutoForm()
    return render(request, 'core/produto_form.html', {'form': form, 'titulo': 'Novo Produto'})

def produto_editar(request, pk):
    produto = get_object_or_404(Produto, pk=pk)
    if request.method == 'POST':
        form = ProdutoForm(request.POST, instance=produto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Produto atualizado com sucesso!')
            return redirect('core:produto_lista')
    else:
        form = ProdutoForm(instance=produto)
    return render(request, 'core/produto_form.html', {'form': form, 'titulo': 'Editar Produto'})

@require_POST
def produto_excluir(request, pk):
    produto = get_object_or_404(Produto, pk=pk)
    try:
        produto.delete()
        messages.success(request, 'Produto excluído com sucesso!')
    except Exception as e:
        messages.error(request, f'Não foi possível excluir o produto: {e}')
    return redirect('core:produto_lista')

# --- Views de Vendas ---

def venda_lista(request):
    vendas = Venda.objects.all().order_by('-data_venda')
    return render(request, 'core/venda_list.html', {'vendas': vendas})

def venda_detalhe(request, pk):
    venda = get_object_or_404(Venda.objects.select_related('cliente').prefetch_related('itens__produto'), pk=pk)
    return render(request, 'core/venda_detalhe.html', {'venda': venda})


def venda_criar(request):
    clientes = Cliente.objects.all().order_by('nome')
    produtos_disponiveis = Produto.objects.filter(estoque__gt=0).order_by('descricao')

    if request.method == 'POST':
        cliente_id = request.POST.get('cliente')
        itens_venda_json = request.POST.get('itens_venda')

        if not cliente_id:
            messages.error(request, 'Por favor, selecione um cliente para a venda.')
            return redirect('core:venda_criar')

        itens_venda_data = json.loads(itens_venda_json) if itens_venda_json else []

        if not itens_venda_data:
            messages.error(request, 'Adicione pelo menos um item à venda.')
            return redirect('core:venda_criar')

        try:
            with transaction.atomic():
                cliente = get_object_or_404(Cliente, pk=cliente_id)
                nova_venda = Venda.objects.create(cliente=cliente)
                total_venda = 0

                for item_data in itens_venda_data:
                    produto = get_object_or_404(Produto, pk=item_data['produto_id'])
                    quantidade = int(item_data['quantidade'])

                    if quantidade <= 0:
                        raise ValueError(f"Quantidade inválida para o produto {produto.descricao}.")
                    if produto.estoque < quantidade:
                        raise ValueError(f"Estoque insuficiente para o produto {produto.descricao}. Disponível: {produto.estoque}")

                    ItemVenda.objects.create(
                        venda=nova_venda,
                        produto=produto,
                        quantidade=quantidade,
                        preco_unitario=produto.valor
                    )
                    produto.estoque -= quantidade
                    produto.save()
                    total_venda += quantidade * produto.valor

                nova_venda.valor_total = total_venda
                nova_venda.save()

                messages.success(request, f'Venda #{nova_venda.id} realizada com sucesso!')
                return redirect('core:venda_detalhe', pk=nova_venda.id)

        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'Erro ao finalizar a venda: {e}')
        
        # Se houve erro, recarregar a página com os dados do POST (ou vazio)
        return render(request, 'core/venda_criar.html', {
            'clientes': clientes,
            'produtos_disponiveis': produtos_disponiveis,
            'venda_form': VendaForm(initial={'cliente': cliente_id}),
            'itens_venda_json_initial': itens_venda_json # Para repopular o carrinho se der erro
        })
    else:
        venda_form = VendaForm()
        return render(request, 'core/venda_criar.html', {
            'clientes': clientes,
            'produtos_disponiveis': produtos_disponiveis,
            'venda_form': venda_form,
            'itens_venda_json_initial': '[]' # Inicia o carrinho vazio
        })

@require_POST
def adicionar_item_venda(request):
    """ API para adicionar um item à lista de itens da venda (no frontend) """
    try:
        data = json.loads(request.body)
        produto_id = data.get('produto_id')
        quantidade = int(data.get('quantidade', 1))

        produto = get_object_or_404(Produto, pk=produto_id)

        if quantidade <= 0:
            return JsonResponse({'success': False, 'message': 'Quantidade inválida.'}, status=400)
        if produto.estoque < quantidade:
            return JsonResponse({'success': False, 'message': f'Estoque insuficiente. Disponível: {produto.estoque}'}, status=400)

        item = {
            'produto_id': produto.id,
            'descricao': produto.descricao,
            'valor_unitario': float(produto.valor),
            'quantidade': quantidade,
            'total_item': float(produto.valor * quantidade),
        }
        return JsonResponse({'success': True, 'item': item})
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Requisição JSON inválida.'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@require_POST
def remover_item_venda(request):
    """ API para remover um item da lista de itens da venda (no frontend) """
    try:
        data = json.loads(request.body)
        produto_id = data.get('produto_id')

        # Não precisa verificar o produto no DB, apenas indicar que foi removido
        # A lógica de remoção será no JS do front-end
        return JsonResponse({'success': True, 'produto_id': produto_id})
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Requisição JSON inválida.'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)