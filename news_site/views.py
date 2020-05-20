from django.shortcuts import render
from .forms import SearchForm
from .models import Article

from plotly.offline import plot
from plotly.graph_objs import Scatter

from chartit import DataPool, Chart, PivotDataPool, PivotChart
from django.db.models import Avg, Sum, Count

from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import HoverTool, LassoSelectTool, WheelZoomTool, PointDrawTool, ColumnDataSource
from bokeh.palettes import Category20c, Spectral6
from bokeh.transform import cumsum
import numpy as np
from numpy import pi
import pandas as pd
from bokeh.resources import CDN
from datetime import datetime as dt

from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import matplotlib as plt
import io
import urllib, base64

# Create your views here.

def index(request): 
    """The home page for news_site."""

    if request.method != "POST":
        #No data submitted: render home page
        form = SearchForm()

        #Display a blank form
        context = {
            "form": form,
        }

        return render(request, "news_site/index.html", context)

# BOKEH DEMO
def results(request):
    disease_query = request.GET.get("disease").lower()

    ### POLARITY VS. DATE ###
    # NYT Data
    polarity_nyt = Article.objects.order_by('date').filter(disease__icontains=disease_query, source__icontains='nytimes.com').values_list("polarity", flat=True)
    date_nyt = Article.objects.order_by('date').filter(disease__icontains=disease_query, source__icontains='nytimes.com').values_list("date", flat=True)
    polar_list_nyt = polarity_nyt
    date_list_nyt = [dt.strptime(d,'%Y-%m-%d') for d in date_nyt]
    nyt_dict = dict(zip(date_list_nyt, polar_list_nyt))
    nyt_dates, nyt_polarity = nyt_dict.keys(), nyt_dict.values()
    
    # PBS Data
    polarity_pbs = Article.objects.order_by('date').filter(disease__icontains=disease_query, source__icontains='pbs.org').values_list("polarity", flat=True)
    date_pbs = Article.objects.order_by('date').filter(disease__icontains=disease_query, source__icontains='pbs.org').values_list("date", flat=True)
    polar_list_pbs = polarity_pbs
    date_list_pbs = [dt.strptime(d,'%Y-%m-%d') for d in date_pbs]
    pbs_dict = dict(zip(date_list_pbs, polar_list_pbs))

    # Remove outlier date
    if disease_query == 'swine flu':
        for k, v in list(pbs_dict.items()):
            if k > dt(2012,1,1):
                pbs_dict.pop(k)

    pbs_dates, pbs_polarity = pbs_dict.keys(), pbs_dict.values()

    # CNN Data
    polarity_cnn = Article.objects.order_by('date').filter(disease__icontains=disease_query, source__icontains='cnn.com').values_list("polarity", flat=True)
    date_cnn = Article.objects.order_by('date').filter(disease__icontains=disease_query, source__icontains='cnn.com').values_list("date", flat=True)
    polar_list_cnn = polarity_cnn
    date_list_cnn = [dt.strptime(d,'%Y-%m-%d') for d in date_cnn]
    cnn_dict = dict(zip(date_list_cnn, polar_list_cnn))
    cnn_dates, cnn_polarity = cnn_dict.keys(), cnn_dict.values()

    title = 'Media Polarity Over Time - ' + disease_query.title()

    p = figure(title=title, 
    x_axis_label = 'Date',
    y_axis_label = 'Polarity Score',
    x_axis_type = 'datetime',
    plot_width = 800,
    plot_height = 300,)

    p.title.text_font_size = '16pt'

    p.line(list(nyt_dates), list(nyt_polarity), legend='NYT', color='blue', line_width = 2)
    p.line(list(pbs_dates), list(pbs_polarity), legend='PBS', color='green', line_width = 2)
    p.line(list(cnn_dates), list(cnn_polarity), legend='CNN', color='red', line_width = 2)

    # p.add_tools(HoverTool(renderers=[p]))

    p.legend.location = "top_left"

    script, div = components(p)

    ### SUBJECTIVITY VS. DATE ###
    # NYT Data
    subj_nyt = Article.objects.order_by('date').filter(disease__icontains=disease_query, source__icontains='nytimes.com').values_list("subjectivity", flat=True)
    date_nyt = Article.objects.order_by('date').filter(disease__icontains=disease_query, source__icontains='nytimes.com').values_list("date", flat=True)
    subj_list_nyt = subj_nyt
    date_list_nyt = [dt.strptime(d,'%Y-%m-%d') for d in date_nyt]
    nyt_dict = dict(zip(date_list_nyt, subj_list_nyt))

    # remove 0 subjectivity values
    for k, v in list(nyt_dict.items()):
        if v == 0 or v == 1:
            nyt_dict.pop(k)

    nyt_dates, nyt_subj = nyt_dict.keys(), nyt_dict.values()
    
    # PBS Data
    subj_pbs = Article.objects.order_by('date').filter(disease__icontains=disease_query, source__icontains='pbs.org').values_list("subjectivity", flat=True)
    date_pbs = Article.objects.order_by('date').filter(disease__icontains=disease_query, source__icontains='pbs.org').values_list("date", flat=True)
    subj_list_pbs = subj_pbs
    date_list_pbs = [dt.strptime(d,'%Y-%m-%d') for d in date_pbs]
    pbs_dict = dict(zip(date_list_pbs, subj_list_pbs))
    
    # remove 0 subjectivity values
    for k, v in list(pbs_dict.items()):
        if v == 0 or v == 1:
            pbs_dict.pop(k)
    
    pbs_dates, pbs_subj = pbs_dict.keys(), pbs_dict.values()

    # CNN Data
    subj_cnn = Article.objects.order_by('date').filter(disease__icontains=disease_query, source__icontains='cnn.com').values_list("subjectivity", flat=True)
    date_cnn = Article.objects.order_by('date').filter(disease__icontains=disease_query, source__icontains='cnn.com').values_list("date", flat=True)
    subj_list_cnn = subj_cnn
    date_list_cnn = [dt.strptime(d,'%Y-%m-%d') for d in date_cnn]
    cnn_dict = dict(zip(date_list_cnn, subj_list_cnn))
    
    # remove 0 subjectivity values
    for k, v in list(cnn_dict.items()):
        if v == 0 or v == 1:
            cnn_dict.pop(k)
    
    cnn_dates, cnn_subj = cnn_dict.keys(), cnn_dict.values()

    title = 'Media Subjectivity Over Time - ' + disease_query.title()

    p2 = figure(title=title, 
    x_axis_label = 'Date',
    y_axis_label = 'Subjectivity Score',
    x_axis_type = 'datetime',
    plot_width = 800,
    plot_height = 300,)

    p2.title.text_font_size = '16pt'

    p2.line(list(nyt_dates), list(nyt_subj), legend='NYT', color='blue', line_width = 2)
    p2.line(list(pbs_dates), list(pbs_subj), legend='PBS', color='green', line_width = 2)
    p2.line(list(cnn_dates), list(cnn_subj), legend='CNN', color='red', line_width = 2)

    p2.legend.location = "top_left"

    script2, div2 = components(p2)


    ### Article Volume ###
    nyt_data = Article.objects.order_by('date').filter(disease__icontains=disease_query, source__icontains='nytimes.com')
    pbs_data = Article.objects.order_by('date').filter(disease__icontains=disease_query, source__icontains='pbs.org')
    cnn_data = Article.objects.order_by('date').filter(disease__icontains=disease_query, source__icontains='cnn.com')

    x = {
        'NYT': len(nyt_data),
        'PBS': len(pbs_data),
        'CNN': len(cnn_data)
    }

    data = pd.Series(x).reset_index(name='value').rename(columns={'index':'Source'})
    data['angle'] = data['value']/data['value'].sum() * 2*pi
    data['color'] = ['blue','green','red']

    title = 'Article Volume By Source - ' + disease_query.title()

    p3 = figure(plot_height=350, title=title, toolbar_location=None,
           tools="hover", tooltips="@Source: @value",)

    p3.wedge(x=0, y=1, radius=0.4,
        start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
        line_color="white", fill_color='color', legend_field='Source', source=data)

    p3.title.text_font_size = '16pt'

    script3, div3 = components(p3)

    # Disease description dataframe
    descriptions_df = pd.DataFrame()
    descriptions_df['name'] = ['coronavirus', 'swine flu']
    descriptions_df['description'] = ['Coronavirus disease (COVID-19) is an infectious disease caused by a newly discovered coronavirus. Most people infected with the COVID-19 virus will experience mild to moderate respiratory illness and recover without requiring special treatment. Older people, and those with underlying medical problems like cardiovascular disease, diabetes, chronic respiratory disease, and cancer are more likely to develop serious illness. The COVID-19 virus spreads primarily through droplets of saliva or discharge from the nose when an infected person coughs or sneezes. At this time, there are no specific vaccines or treatments for COVID-19.', 
                          'Swine Flu (aka Swine Influenza, H1N1): In the spring of 2009, a novel influenza A (H1N1) virus emerged. It was detected first in the United States and spread quickly across the United States and the world. This new H1N1 virus contained a unique combination of influenza genes not previously identified in animals or people. This virus was designated as influenza A (H1N1) pdm09 virus.']
    descriptions_df['deaths'] = ['As of May 8th 2020, there are 1.31 million confirmed cases and 77 thousand deaths in the United States. Globally, there are 3.9 million cases and 272 thousand deaths.',
    'From April 12, 2009 to April 10, 2010, CDC estimated there were 60.8 million cases (range: 43.3-89.3 million), 274,304 hospitalizations (range: 195,086-402,719), and 12,469 deaths (range: 8868-18,306) in the United States due to the (H1N1)pdm09 virus. Additionally, CDC estimated that 151,700-575,400 people worldwide died from (H1N1)pdm09 virus infection during the first year the virus circulated.']
    
    if disease_query.lower() in list(descriptions_df['name']):
        div_descript = descriptions_df[ descriptions_df['name'] == disease_query ]['description'].values[0]
        div_deaths = descriptions_df[ descriptions_df['name'] == disease_query ]['deaths'].values[0]
    else:
        div_descript = 'No results found. Please search again.'
        div_deaths = ''

    heading = "Bias Results - " + disease_query.title()

    # # Word cloud
    # stopwords = list(STOPWORDS)
    # adtn = ['associated','press','how','—', 'said', 'will', 'one', 'said.', "it's", 'says', 'may', 'hi', 'wa', '...', 'watch:', 'coronavirus,', 'say', 'ha', 'thi', '\x97', '-', '|', '04', 'de', 'sam', '.', "flu:", 'news:', "cnn's"]
    # for i in adtn:
    #     stopwords.append(i)
    # word_data = Article.objects.filter(disease__icontains=disease_query).values_list('text', flat=True)

    # text = " ".join(text for text in word_data)
    # wc = WordCloud(stopwords=stopwords, max_words=10).generate(text)
    # plt.figure()
    # plt.imshow(wc, interpolation='bilinear')
    # plt.axis('off')
    # fig = plt.gcf()
    # image = io.BytesIO()
    # plt.savefig(image, format='png')
    # image.seek(0)
    # string = base64.b64encode(image.read())

    # image_64 = 'data:image/png;base64' + urllib.parse.quote(string)

    # Article search results
    qs = Article.objects.filter(disease__icontains=disease_query).order_by('-date')
    form = SearchForm()

    # Rendering context
    context = {'script': script, 'div':div, 'script2': script2,
                'div2':div2, 'script3': script3, 'div3':div3, 
                'div_descript':div_descript, 'div_deaths':div_deaths, 
                'heading':heading, 
                'form': form,
                'queryset':qs}

    return render(request, 'news_site/results.html' , context)