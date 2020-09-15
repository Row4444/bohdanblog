from django.shortcuts import render, get_object_or_404


class ArticleMixin:
    name = None
    context = None
    template = None

    def get(self, request):
        return render(request, self.template, {self.name: self.context})
