from django.views import generic
from .models import Post


class IndexView(generic.ListView):
    model = Post
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.order_by('-created_at')


class CategoryView(generic.ListView):
    model = Post
    paginate_by = 10

    def get_queryset(self):
        """
        category = get_object_or_404(Category, pk=self.kwargs['pk'])
        queryset = Post.objects.order_by('created_at').filter(category=category)
        """
        category_pk = self.kwargs['pk']
        queryset = Post.objects.order_by('-created_at').filter(category__pk=category_pk)
        return queryset


class DetailView(generic.DetailView):
    model = Post
