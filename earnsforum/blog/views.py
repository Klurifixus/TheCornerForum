from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.views import View
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render, get_object_or_404
from .models import Post, Cartoon, CartoonPanel, SavedContent
from .form import CommentForm
from users1.models import UserProfile


class StartingPageView(ListView):
    template_name = "blog/index.html"
    model = Post
    ordering = ['-date']
    context_object_name = "posts"

    def get_queryset(self):
        queryset = super().get_queryset()
        # Display only the top 3 posts on the starting page
        data = queryset[:3]
        return data


class AllPostsView(ListView):
    template_name = "blog/all-posts.html"
    model = Post
    ordering = ['-date']
    context_object_name = "all_posts"  # Contains all posts for the 'all-posts' page


class SinglePostView(View):
    def is_stored_posts(self, request, post_id):
        stored_posts = request.session.get("stored_posts")
        return post_id in stored_posts if stored_posts else False

    def get(self, request, slug):
        try:
            post = get_object_or_404(Post, slug=slug)
            context = {
                "post": post,
                "post_tags": post.tags.all(),
                "comment_form": CommentForm(),
                "comments": post.comments.all().order_by('-id'),
                "saved_for_later": self.is_stored_posts(request, post.id)
            }
            return render(request, "blog/post-detail.html", context)
        except Http404:
            return render(request, "user1/404.html", {"message": "Post not found."})
        except Exception as e:
            # Log the error here if you have logging setup
            return render(request, "user1/error.html", {"message": "An unexpected error occurred."})

    @method_decorator(login_required)
    def post(self, request, slug):
        # Handle comment submission for a single post
        comment_form = CommentForm(request.POST)
        post = get_object_or_404(Post, slug=slug)

        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.user = request.user
            comment.post = post
            comment.save()
            return HttpResponseRedirect(reverse("blog:post-detail-page", args=[slug]))

        # Re-render the page with existing context and the invalid form
        context = {
            "post": post,
            "post_tags": post.tags.all(),
            "comment_form": comment_form,
            "comments": post.comments.all().order_by('-id'),
        }
        return render(request, "blog/post-detail.html", context)


class ReadLaterView(LoginRequiredMixin, View):
    """ def get(self, request):
        # stored_contents = request.session.get("stored_contents", {})
        posts = Post.objects.filter(id__in=stored_contents.get("posts", []))
        cartoons = Cartoon.objects.filter(
            id__in=stored_contents.get("cartoons", []))

        context = {
            "posts": posts,
            "cartoons": cartoons,
            "has_contents": bool(posts or cartoons)
        }
        return render(request, "blog/stored-posts.html", context) """

    def get(self, request):
        user_profile, created = UserProfile.objects.get_or_create(
            user=request.user)
        saved_content = user_profile.saved_content
        saved_content, _ = SavedContent.objects.get_or_create(
            user=request.user)

        # Get the saved posts and cartoons
        posts = saved_content.posts.all()
        cartoons = saved_content.cartoons.all()

        context = {
            "posts": posts,
            "cartoons": cartoons,
            "has_contents": bool(posts or cartoons)
        }
        return render(request, "blog/stored-posts.html", context)

    def post(self, request):
        # Get user's UserProfile and associated SavedContent
        user_profile = UserProfile.objects.get(user=request.user)
        saved_content = user_profile.saved_content

        content_type = request.POST.get("content_type")
        content_id = request.POST.get("content_id")

        if content_type == "post":
            post = get_object_or_404(Post, pk=content_id)
            if post in saved_content.posts.all():
                saved_content.posts.remove(post)
            else:
                saved_content.posts.add(post)
        elif content_type == "cartoon":
            cartoon = get_object_or_404(Cartoon, pk=content_id)
            if cartoon in saved_content.cartoons.all():
                saved_content.cartoons.remove(cartoon)
            else:
                saved_content.cartoons.add(cartoon)

        return redirect(request.POST.get('next', '/'))


class CartoonView(ListView):
    template_name = "blog/cartoon.html"
    model = Cartoon
    context_object_name = "cartoons"


def cartoon_detail(request, slug):
    cartoon = get_object_or_404(Cartoon, slug=slug)
    cartoon_panels = cartoon.panels.all().order_by('order')
    return render(request, "blog/cartoon-detail.html", {
        "cartoon": cartoon,
        "cartoon_panels": cartoon_panels,
    })
