from django.urls import path
from .views import BookListView, BookDetailView, delete_review, SearchResultsView


urlpatterns = [
    path("", BookListView.as_view(), name="book_list"),
    path("<uuid:pk>/", BookDetailView.as_view(), name="book_detail"),
    path("<int:review_id>/delete_review/", delete_review, name="review_delete"),
    path("search/", SearchResultsView.as_view(), name="search_results"),
]
