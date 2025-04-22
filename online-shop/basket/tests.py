import json
from decimal import Decimal

from django.contrib.auth.models import AnonymousUser, User
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory, TestCase
from django.middleware.csrf import CsrfViewMiddleware, get_token
from rest_framework.test import APIClient

from basket.models import Basket, BasketItem
from basket.views import BasketItemAPIView
from basket.session_cart import SessionCart
from catalog.models import Category, SubCategory
from product.models import Product


class BasketTest(TestCase):

    """ Класс для тестирования корзины (Basket) анонимным пользователем и авторизованным  """

    def setUp(self):
        self.category = Category.objects.create(title='Category 1')
        self.subcategory = SubCategory.objects.create(title='SubCategory 1', category=self.category)
        self.factory = RequestFactory()
        self.view = BasketItemAPIView.as_view()
        self.user = User.objects.create_user(username='test', password='password')
        self.anonymous = AnonymousUser()
        self.product = Product.objects.create(
            title='Test Product',
            description='Short description',
            fullDescription='Full description of the product',
            price=Decimal('10.50'),
            count=5,
            freeDelivery=True,
            category=self.category,
            subcategory=self.subcategory,
            rating=Decimal('4.5'),
            is_limited=True,
            is_banner=False,
        )
        self.product2 = Product.objects.create(
            title='Second Product',
            description='Desc',
            fullDescription='Full desc',
            price=Decimal('20.00'),
            count=10,
            freeDelivery=False,
            category=self.category,
            subcategory=self.subcategory,
            rating=Decimal('3.5'),
            is_limited=False,
            is_banner=False,
        )

    def request_user(self):
        request = self.factory.get('/basket/')
        request.user = self.user
        return self.view(request)

    def request_anonymous(self):
        request = self.factory.get('/basket/')
        request.user = self.anonymous
        self.add_session_to_request(request)
        return self.view(request)

    def add_csrf_to_request(self, request):
        if not hasattr(request, 'session'):
            from django.contrib.sessions.middleware import SessionMiddleware
            SessionMiddleware(lambda r: None).process_request(request)
            request.session.save()
        csrf_token = get_token(request)
        request.META['CSRF_COOKIE'] = csrf_token
        request.META['HTTP_X_CSRFTOKEN'] = csrf_token
        CsrfViewMiddleware(lambda r: None).process_view(request, None, (), {})

    def add_session_to_request(self, request):
        """ Функция для создания сессии для анонимного пользователя """
        def get_response(request):
            return None

        middleware = SessionMiddleware(get_response)
        middleware.process_request(request)
        request.session.save()

    def test_get_authenticated_user_returns_basket_items(self):

        """ Тест работы View для авторизованного пользователя """

        self.basket = Basket.objects.create(user=self.user)
        self.basket_item = BasketItem.objects.create(basket=self.basket, product=self.product, amount=15)

        response = self.request_user()

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, list)
        self.assertTrue(response.data[0]['title'] == 'Test Product')
        self.assertEqual(response.data[0]['id'], self.product.id)
        self.assertTrue(response.data[0]['count'] == 15)

    def test_get_unauthenticated_user_returns_basket_items(self):

        """ Тест работы View для не авторизованного пользователя """

        request = self.factory.get('/basket/')
        request.user = self.anonymous

        self.add_session_to_request(request)
        self.basket = SessionCart(request)
        self.basket.add(self.product, quantity=3)

        response = self.view(request)

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, list)
        self.assertTrue(response.data[0]['count'] == 3)

    def test_empty_basket_anonymous_user(self):

        """ Тест работы View с пустой корзиной и анонимным пользователем """

        response = self.request_anonymous()

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, list)
        self.assertTrue(len(response.data) == 0)

    def test_empty_basket_authenticated_user(self):

        """ Тест работы View с пустой корзиной и авторизованным пользователем """

        response = self.request_user()

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, list)
        self.assertTrue(len(response.data) == 0)

    def test_multiplay_add_product(self):

        """ Тест View с добавлением нескольких продуктов в корзину авторизованного пользователя """

        basket = Basket.objects.create(user=self.user)
        BasketItem.objects.create(basket=basket, product=self.product, amount=3)
        BasketItem.objects.create(basket=basket, product=self.product2, amount=7)

        response = self.request_user()

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, list)
        self.assertTrue(len(response.data) == 2)
        self.assertTrue(response.data[0]['count'] + response.data[1]['count'] == 10)

    def test_delete_basket_item_authenticated(self):
        basket = Basket.objects.create(user=self.user)
        basket_item = BasketItem.objects.create(basket=basket, product=self.product, amount=10)

        client = APIClient()
        client.force_authenticate(user=self.user)

        response = client.delete(
            '/basket/',
            data={"id": basket_item.id, "count": 5},
            format='json'
        )

        self.assertIn(response.status_code, (200, 204))