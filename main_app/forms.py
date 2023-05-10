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
        fields = ('ticker', 'category', 'sri', 'invest', 'shares',)
        labels = {'sri': 'SRI'}
        help_texts = {'ticker': 'e.g. ABCD.EF', }

    def clean(self):
        """Overwriting the default clean method to obtain additional information with the yfinance package.
        It gets the stock name, currency, exchange and current price, if the ticker is valid.
        It raises an error if the ticker is invalid."""
        cleaned_data = self.cleaned_data
        try:
            stock_info = yf.Ticker(cleaned_data['ticker']).info
            cleaned_data['product'] = stock_info['longName']
            cleaned_data['currency'] = stock_info['currency']
            cleaned_data['exchange'] = stock_info['exchange']
            stock_price = yf.Ticker(cleaned_data['ticker']).history(period="1d")
            cleaned_data['price'] = stock_price.iloc[0]["Close"]
        except:
            self.add_error('ticker', 'Ticker is not valid.')
        return cleaned_data


class CategoryModelForm(forms.BSModalModelForm):
    class Meta:
        model = models.Category
        fields = ('target',)
