from django.views import generic
from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView, BSModalDeleteView

from django.contrib.auth.mixins import LoginRequiredMixin

from django.db.models import Count, Q, Sum, Avg, DecimalField
from django.db.models.functions import Coalesce
from datetime import datetime, timedelta
from decimal import Decimal

from django.urls import reverse_lazy

from django.contrib import messages
from django.core.exceptions import ValidationError

from . import models, forms


# Create your views here.
class StockListView(LoginRequiredMixin,generic.ListView):
    template_name = 'main_app/list.html'
    model = models.Stock

    def get_context_data(self, **kwargs):
        context = super(StockListView, self).get_context_data(**kwargs)
        context['sum'] = models.Stock.objects.sum_all()
        context['form'] = forms.StockForm()
        context['update_date'] = self.request.session.get('update_date')
        return context


class StockCreateView(LoginRequiredMixin,BSModalCreateView):
    template_name = 'main_app/stock_form.html'
    form_class = forms.StockModelForm
    success_url = reverse_lazy('main_app:list')
    error_message = 'Something went wrong obtaining the YFinance data.'

    def form_valid(self, form):
        """If the form is valid, save the associated model and lookup the stock data."""
        self.object = form.save(commit=False)
        stock_data = self.object.get_stock_data()
        try:
            self.object.product = stock_data['longName']
            self.object.currency = stock_data['currency']
            self.object.exchange = stock_data['exchange']
            self.object.price = stock_data['regularMarketPrice']
            self.object.value = self.object.price * self.object.shares
        except:
            messages.error(self.request, self.error_message)
            raise ValidationError(self.error_message)

        return super().form_valid(form)


class StockUpdateView(StockCreateView,BSModalUpdateView):
    model = models.Stock
    template_name = 'main_app/update_stock_form.html'
    form_class = forms.StockModelForm
    success_url = reverse_lazy('main_app:list')


class StockDeleteView(LoginRequiredMixin,BSModalDeleteView):
    model = models.Stock
    template_name = 'main_app/delete_stock_form.html'
    success_url = reverse_lazy('main_app:list')


class StockFormView(LoginRequiredMixin,generic.FormView):
    template_name = 'main_app/list.html'
    form_class = forms.StockForm
    success_url = reverse_lazy('main_app:list')

    def post(self, request, *args, **kwargs):
        dt_update = datetime.now()
        try:
            dt_last_update = datetime.strptime(request.session['update_date'], "%d/%m/%Y %H:%M")
        except:
            dt_last_update = dt_update - timedelta(days=2)
        request.session['update_date'] = dt_update.strftime("%d/%m/%Y %H:%M")
        for stock in models.Stock.objects.all():
            stock_data = stock.get_stock_data()
            try:
                if ((dt_update - dt_last_update).total_seconds() / 3600) > 24:
                    stock.prev_price = stock.price
                stock.product = stock_data['longName']
                stock.currency = stock_data['currency']
                stock.exchange = stock_data['exchange']
                stock.price = Decimal(stock_data['regularMarketPrice'])
                stock.value = stock.price * stock.shares
                stock.price_change_perc = (stock.price - stock.prev_price) / stock.prev_price * 100
                stock.value_change = (stock.price - stock.prev_price) * stock.shares
                stock.save()
            except:
                print("Updating stock data failed.")
                raise
        return super().post(request, *args, **kwargs)


class StockView(LoginRequiredMixin,generic.View):
    def get(self, request, *args, **kwargs):
        view = StockListView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = StockFormView.as_view()
        return view(request, *args, **kwargs)


class CategoryUpdateView(LoginRequiredMixin,BSModalUpdateView):
    model = models.Category
    template_name = 'main_app/update_category_form.html'
    form_class = forms.CategoryModelForm
    success_url = reverse_lazy('main_app:invest')


class CategoryInvestView(LoginRequiredMixin,generic.ListView):
    template_name = 'main_app/invest.html'
    model = models.Category

    def get_queryset(self):
        investment_value = self.request.session.get('investment_value')
        if not isinstance(investment_value, int):
            investment_value = 0

        qs = models.Category.objects.annotate(
            cat_invest_value=(models.Stock.objects.sum_all() + investment_value) * Avg('target') / 100 - Coalesce(
                Sum('stocks__value'), 0, output_field=DecimalField()),
            no_of_invest_stocks=Count('stocks', filter=Q(stocks__invest=True)),
        )
        return qs

    def get_context_data(self, **kwargs):
        context = super(CategoryInvestView, self).get_context_data(**kwargs)
        context['sum'] = models.Stock.objects.sum_all()

        investment_value = self.request.session.get('investment_value')
        if not isinstance(investment_value, int):
            investment_value = 0
        context['form'] = forms.InvestmentForm(initial={'investment_value': investment_value})

        qs_stock = models.Stock.objects.filter(invest=True)

        try:
            for stock in qs_stock:
                cat = context['object_list'].get(pk=stock.category_id)
                stock.stock_invest_value = cat.cat_invest_value / cat.no_of_invest_stocks
                stock.stock_invest_shares = stock.stock_invest_value / stock.price
        except:
            print('Adding stock_invest_value failed')

        context['stock_list'] = qs_stock
        return context


class InvestmentFormView(LoginRequiredMixin,generic.FormView):
    template_name = 'main_app/invest.html'
    form_class = forms.InvestmentForm
    success_url = reverse_lazy('main_app:invest')

    def get_context_data(self, **kwargs):
        context = super(InvestmentFormView, self).get_context_data(**kwargs)
        context['sum'] = models.Stock.objects.sum_all()
        return context

    def post(self, request, *args, **kwargs):
        request.session['investment_value'] = int(request.POST['investment_value'])
        return super().post(request, *args, **kwargs)


class InvestView(LoginRequiredMixin,generic.View):
    def get(self, request, *args, **kwargs):
        view = CategoryInvestView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = InvestmentFormView.as_view()
        return view(request, *args, **kwargs)
