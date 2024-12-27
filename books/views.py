from typing import Any
from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.http import HttpResponseForbidden, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic.edit import FormMixin
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.db.models import Q

from .models import Book, Review
from .forms import ReviewForm


class BookListView(LoginRequiredMixin, ListView):
    model = Book
    template_name = "books/book_list.html"
    context_object_name = "book_list"
    login_url = "account_login"

    # def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
    #     print("IP Address for debug-toolbar: " + self.request.META["REMOTE_ADDR"])
    #     return super().get(request, *args, **kwargs)


class BookDetailView(
    LoginRequiredMixin, PermissionRequiredMixin, DetailView, FormMixin
):
    model = Book
    template_name = "books/book_detail.html"
    context_object_name = "book"
    form_class = ReviewForm
    login_url = "account_login"
    permission_required = "books.special_status"
    queryset = Book.objects.all().prefetch_related(
        "reviews__author",
    )

    def get_success_url(self) -> str:
        return self.get_object().get_absolute_url()

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()

        if form.is_valid():
            review: Review = form.save(commit=False)
            review.book = self.object
            review.author = self.request.user
            review.save()

            # if self.request.META.get("HTTP_HX_REQUEST"):
            if request.htmx:
                return HttpResponse(f"""
                                <li>
                                    {review.review} ({review.author.username})
                                </li>
                            """)

            messages.success(self.request, "Your view has been added")
            return redirect(self.get_success_url())
        else:
            if self.request.META.get("HX-Request"):
                return HttpResponse(form.errors.all(), status=400)

            messages.error(self.request, "Form is invalid try again later")
            return self.form_invalid(form)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        if "form" not in context:
            context["form"] = self.get_form()
        return context


@require_http_methods(["DELETE", "POST"])
@login_required
def delete_review(request, review_id: int):
    review = get_object_or_404(
        Review,
        id=review_id,
    )

    if request.user != review.author:
        return HttpResponseForbidden("Unauthorized")

    review.delete()
    # if request.META.get("HX-Request"):
    if request.htmx:
        return HttpResponse("", content_type="text/plain")

    return redirect(review.book.get_absolute_url())


class SearchResultsView(ListView):
    model = Book
    context_object_name = "book_list"
    template_name = "books/search_result.html"

    def get_queryset(self):
        query = self.request.GET.get("q")
        return Book.objects.filter(
            Q(title__icontains=query) | Q(author__icontains=query)
        )
