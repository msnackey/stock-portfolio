from django import forms as dj_forms
from bootstrap_modal_forms import forms
from . import models
import yfinance as yf


class InvestmentForm(dj_forms.Form):
    investment_value = dj_forms.IntegerField(label='Investment',
                                             widget=dj_forms.TextInput(attrs={'style': 'width:100px'}))


class StockForm(dj_forms.Form):
    pass


class StockModelForm(forms.BSModalModelForm):
    class Meta:
        model = models.Stock
        fields = ('ticker', 'category', 'sri', 'invest', 'shares', )
        labels = {'sri': 'SRI'}
        help_texts = {'ticker': 'e.g. ABCD.EF', }

    def clean(self):
        cleaned_data = self.cleaned_data
        try:
            stock_data = yf.Ticker(cleaned_data['ticker']).info
            cleaned_data['product'] = stock_data['longName']
            cleaned_data['currency'] = stock_data['currency']
            cleaned_data['exchange'] = stock_data['exchange']
            cleaned_data['price'] = stock_data['regularMarketPrice']
        except:
            self.add_error('ticker', 'Ticker is not valid.')
        return cleaned_data


class CategoryModelForm(forms.BSModalModelForm):
    class Meta:
        model = models.Category
        fields = ('target', )
