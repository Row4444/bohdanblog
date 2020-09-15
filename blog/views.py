from django.contrib import messages
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, FormView, CreateView, UpdateView

from blog.forms import ArticleForm, CommentForm
from blog.models import Article, Comment
from blog.utils import ArticleMixin


class ArticleView(ListView):
    template_name = 'blog/allposts.html'
    model = Article

  #  queryset = Article.objects.filter(status='a').order_by('date').reverse()

    def get_ordering(self):
        ordering = self.request.GET.get('order', '-date')
        # searching = self.request.GET.get('searching', False)
        # if searching:
        #     return searching
        return ordering

    def get_queryset(self):
        ordering = self.get_ordering()
        if ordering == '-date':
            return Article.objects.filter(status='a').order_by('-date')
        elif ordering == 'date':
            return Article.objects.filter(status='a').order_by('date')


class MyArticleView(ListView):
    template_name = 'blog/allposts.html'

    def get_queryset(self):
        return Article.objects.filter(author=self.request.user)


class NewArticleView(View):
    def get(self, request):
        if not request.user.is_authenticated or not request.user.is_verify:
            raise Http404('Register, please.')
        form = ArticleForm()
        return render(request, 'blog/newarticle.html', {'form': form})

    def post(self, request):
        if request.method == 'POST':
            newArticle = ArticleForm(request.POST)
            if newArticle.is_valid():
                article = newArticle.save(commit=False)
                article.body = newArticle.cleaned_data['body']
                article.title = newArticle.cleaned_data['title']
                article.author = request.user
                if request.user.is_redactor:
                    article.status = 'approve'
                article.save()
        return redirect('all')


class CommentCreate(View):
    def post(self, request, id):
        article = Article.objects.get(id=id)
        author = request.user
        if request.user.is_authenticated and request.user.is_verify:
            if request.method == 'POST':
                comment = CommentForm(request.POST)
                if comment.is_valid():
                    newComment = comment.save(commit=False)
                    newComment.post = article
                    newComment.author = author
                    newComment.body = comment.cleaned_data['body']
                    newComment.save()
        return redirect('detail_url', id)


class ArticleDetailView(CommentCreate):
    def get(self, request, id):
        article = get_object_or_404(Article, id=id)
        comments = Comment.objects.filter(post=article)
        comment_form = CommentForm()
        return render(request, 'blog/article.html',
                      {'article': article, 'comment_form': comment_form, 'comments': comments})


