from django.test import TestCase
from django.urls import reverse, resolve
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from .models import Book, Review
from .views import BookDetailView

User = get_user_model()


class BookTests(TestCase):
    def setUp(self):
        self.permission = Permission.objects.get(codename="special_status")

    @classmethod
    def setUpTestData(cls):
        cls.book: Book = Book.objects.create(
            title="Harry potter",
            author="JK Rowling",
            price="100",
        )

        cls.user = User.objects.create_user(
            username="testuser", email="reviewuser@gmail.com", password="testpass124@"
        )
        cls.review = Review.objects.create(
            book=cls.book,
            author=cls.user,
            review="a good book",
        )

    def test_book_listing(self):
        self.client.login(email="reviewuser@gmail.com", password="testpass124@")
        self.assertEqual(self.book.title, "Harry potter")
        self.assertEqual(self.book.author, "JK Rowling")
        self.assertEqual(self.book.price, "100")
        self.assertEqual(self.book.__str__(), self.book.title)

    def test_book_list(self):
        self.client.login(email="reviewuser@gmail.com", password="testpass124@")
        response = self.client.get(reverse("book_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Harry potter")
        self.assertTemplateUsed(response, "books/book_list.html")

    def test_book_detail(self):
        self.client.login(email="reviewuser@gmail.com", password="testpass124@")
        self.user.user_permissions.add(self.permission)
        response = self.client.get(self.book.get_absolute_url())
        no_response = self.client.get("books/23145")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(no_response.status_code, 404)
        self.assertContains(response, "Harry potter")
        self.assertTemplateUsed(response, "books/book_detail.html")

    def test_resolve_function_url(self):
        view = resolve(self.book.get_absolute_url())
        self.assertEqual(view.func.__name__, BookDetailView.as_view().__name__)


# write test for review add and delete


class ReviveAddAndDelete(TestCase):
    def setUp(self):
        self.permission = Permission.objects.get(codename="special_status")

    @classmethod
    def setUpTestData(cls):
        cls.book: Book = Book.objects.create(
            title="Harry potter",
            author="JK Rowling",
            price="100",
        )

        cls.user = User.objects.create_user(
            username="testuser", email="reviewuser@gmail.com", password="testpass124@"
        )
        cls.review = Review.objects.create(
            book=cls.book,
            author=cls.user,
            review="a good book",
        )

    def test_review_add(self):
        self.client.login(email="reviewuser@gmail.com", password="testpass124@")

        self.user.user_permissions.add(self.permission)

        url = self.book.get_absolute_url()

        form_data = {
            "review": "Amazing book!",
        }
        response = self.client.post(url, form_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, url)

        new_review = Review.objects.filter(book=self.book, review=form_data["review"])
        self.assertTrue(new_review.exists())
        self.assertEqual(new_review.first().author, self.user)


class SearchTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.book: Book = Book.objects.create(
            title="Harry potter",
            author="JK Rowling",
            price="100",
        )

    def setUp(self):
        self.url = reverse("search_results")
        self.response = self.client.get(self.url, {"q": "kart"})

    def test_search(self):
        print(self.response)
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, "books/search_result.html")
        self.assertContains(self.response, "kartikey")
