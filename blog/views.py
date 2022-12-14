from django.shortcuts import render, get_object_or_404, reverse, redirect
from django.views import generic, View
from django.views.generic import UpdateView
from django.http import HttpResponseRedirect
from django.utils.text import slugify
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Post
from .forms import CommentForm, BlogForm


# Create your views here.

# class based views - allow us to make
# resuable views which inherit from each other
# allows us yo view our blog 
# MVT - model,view,teplates

def about(request):
    """
    renders about page
    """
    return render(request, "about.html")


class PostList(generic.ListView):
    model = Post
    queryset = Post.objects.filter(status=1).order_by("-created_on")
    template_name = "index.html"
    paginate_by = 6


class PostDetails(View):

    def get(self, request, slug, *args, **kwargs):
        queryset = Post.objects.filter(status=1)
        post = get_object_or_404(queryset, slug=slug)
        comments = post.comments.filter(approved=True).order_by("-created_on")
        liked = False
        if post.likes.filter(id=self.request.user.id).exists():
            liked = True

        return render(
            request,
            "post_detail.html",
            {
                "post": post,
                "comments": comments,
                "commented": False,
                "liked": liked,
                "comment_form": CommentForm(),
            },
        )
        
    def post(self, request, slug, *args, **kwargs):

        queryset = Post.objects.filter(status=1)
        post = get_object_or_404(queryset, slug=slug)
        comments = post.comments.filter(approved=True).order_by("-created_on")
        liked = False
        if post.likes.filter(id=self.request.user.id).exists():
            liked = True

        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            comment_form.instance.email = request.user.email
            comment_form.instance.name = request.user.username
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.save()
        else:
            comment_form = CommentForm()

        return render(
            request,
            "post_detail.html",
            {
                "post": post,
                "comments": comments,
                "commented": True,
                "comment_form": comment_form,
                "liked": liked
            },
        )


class PostLike(View):
    
    def post(self, request, slug, *args, **kwargs):
        post = get_object_or_404(Post, slug=slug)
        if post.likes.filter(id=request.user.id).exists():
            post.likes.remove(request.user)
        else:
            post.likes.add(request.user)

        return HttpResponseRedirect(reverse('post_detail', args=[slug]))


class YourBlogs(View):

    def get(self, request):
        """
        your_recipes view, get method
        """
        post = Post.objects.filter(author=request.user)
        paginator = Paginator(post, 6)  
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request, 'your_blogs.html', {"page_obj": page_obj,})
        

class AddBlogs(View):

    def get(self, request):
        """
        What happens for a GET request
        """
        context = {'blog_form': BlogForm()}
        return render(request, 'add_blogs.html', context)
        

    def post(self, request):
        """
        What happens for a POST request
        """
        blog_form = BlogForm(request.POST, request.FILES)

        if  blog_form.is_valid():
            blog = blog_form.save(commit=False)
            blog.author = request.user
            blog.slug = slugify('-'.join([blog.title, str(blog.author)]), allow_unicode=False)
            blog.save()
            messages.success(request, 'Your Blog is awaiting approval.')
            return redirect('your_blogs')
            
        else:
            messages.error(request, 'Error: Something went wrong, please try again.')  # noqa: E501
            # create message error 
            blog_form = BlogForm()

        return render(
            request,
            "add_blogs.html",
            {
                 "blog_form": blog_form
            },
        )


class AllPosts(generic.ListView):
    """
    all the posts, and display 9 posts
    per page
    """
    model = Post
    queryset = Post.objects.filter(status=1).order_by('-created_on')  # noqa: E501
    template_name = 'all_post.html'
    paginate_by = 9


class EditBlog(UpdateView):
    """ 
    User Edits there blog  
    """
    model = Post
    template_name = 'editblog.html'
    form_class = BlogForm


def delete_blogs(request, post_id):
    """
    Deletes there own blogs
    """
    post = get_object_or_404(Post, id=post_id)
    post.delete()
    return redirect(reverse(
        'your_blogs'))


def search_blog(request):
    """ 
    Search bar view, template form youtube.
    """
    # https://www.youtube.com/watch?v=AGtae4L5BbI
    if request.method == "POST":
        searched = request.POST['searched']
        posts = Post.objects.filter(title__icontains=searched)
        return render(request, 'search_blog.html',
        {'searched': searched, 'posts': posts})
    else:
        return render(request, 'search_blog.html', {})
