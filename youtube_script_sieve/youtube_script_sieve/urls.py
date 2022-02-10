from django.contrib import admin
from django.urls import path
from django.conf.urls import re_path
from text_analyzer.views import index, analyzeText, addSynonym

urlpatterns = [
    re_path(r'^$', index, name="index"),
    re_path(r'^analyze/$', analyzeText, name="analyze"),
    re_path(r'^add-synonym/$', addSynonym, name="add-synonym"),
    # path('admin/', admin.site.urls),
]
