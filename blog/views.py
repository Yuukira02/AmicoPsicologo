from django.http import HttpResponseNotFound
from django.shortcuts import redirect, render, get_object_or_404
from braces.views import GroupRequiredMixin, LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import *
from .forms import *

import logging

logger = logging.getLogger()
TAG = "BLOG-view:"

class ListPostView(ListView): 
    model = Blog
    template_name="blog/home.html"

class MyBlogs(LoginRequiredMixin, ListView):
    model = Blog
    template_name = "blog/my_blogs.html"

    def get_queryset(self):
        arg = self.request.user.pk
        try: 
            qs = self.model.objects.filter(author=arg)
        except Blog.DoesNotExist: 
            errore = "L'oggetto non esiste. Risolto nel template"
            qs = ""

        return qs

class CreateBlogView(GroupRequiredMixin, CreateView):
    group_required = ["Psychologists"]
    template_name = "blog/create_blog.html"
    success_url = reverse_lazy('blog:myblogs')
    form_class = CreateBlogForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class ReadPostView(DetailView):
    model = Blog
    template_name = "blog/read_blog.html"

    def get_queryset(self):
        try: 
            pk = self.kwargs["pk"]
            qs = self.model.objects.filter(id=pk)
        except Blog.DoesNotExist:
            logger.warning(TAG, "Non esiste il blog")
            return HttpResponseNotFound("Blog not found")

        return qs

class UpdateBlogView(GroupRequiredMixin, LoginRequiredMixin, UpdateView):
    model = Blog
    group_required = ["Psychologists"]
    fields = ['title', 'topic', 'content']
    template_name = "blog/update_blog.html"
    success_url = reverse_lazy('blog:myblogs')

class DeleteBlogView(GroupRequiredMixin, LoginRequiredMixin, DeleteView):
    model = Blog
    group_required = ["Psychologists"]
    template_name = "blog/delete_blog.html"
    success_url = reverse_lazy('blog:myblogs')
    

def search(request):
    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            sstring = form.cleaned_data.get("search_string")
            topic = form.cleaned_data.get("search_where")
            return redirect("blog:search_results", sstring, topic)
    else:
        form = SearchForm()

    object_list = Blog.objects.all()
    context={
        "form":form, 
        "object_list":object_list, 
        }
    return render(request, template_name="blog/search.html", context=context)

class BlogSearchView(ListPostView):
    title = "La tua ricerca ha dato come risultato"

    def get_queryset(self):
        sstring = self.request.resolver_match.kwargs["sstring"] 
        where = self.request.resolver_match.kwargs["topic"]

        qq2 = self.model.objects.filter(title__icontains=sstring)
        qq3 = self.model.objects.filter(content__icontains=sstring)
        qq = qq2 | qq3
        
        if where == None:
            qq = qq.filter(topic=where)

        return qq


