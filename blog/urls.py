from django.urls import path
from blog.views import ArticleView, NewArticleView, ArticleDetailView

urlpatterns = [
    path('', ArticleView.as_view(), name='all'),
    path('new/', NewArticleView.as_view(), name='new'),
    path('<int:id>/', ArticleDetailView.as_view(), name='detail_url'),
]
