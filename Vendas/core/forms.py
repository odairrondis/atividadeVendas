# core/forms.py
from django import forms
from .models import Cliente, Produto, Venda, ItemVenda

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nome', 'telefone']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do Cliente'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(XX) XXXXX-XXXX'}),
        }

class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = ['descricao', 'valor', 'estoque']
        widgets = {
            'descricao': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Descrição do Produto'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'estoque': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
        }

class VendaForm(forms.ModelForm):
    class Meta:
        model = Venda
        fields = ['cliente']
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-select'}),
        }

class ItemVendaForm(forms.Form):
    # Este formulário é para adicionar produtos no front-end da tela de venda
    produto_id = forms.IntegerField(widget=forms.HiddenInput())
    quantidade = forms.IntegerField(min_value=1, initial=1,
                                    widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm text-center', 'min': '1'}))