from django.http import HttpResponseNotAllowed
from django.test import RequestFactory, SimpleTestCase, override_settings

from .middleware import CustomErrorPageMiddleware


@override_settings(
	STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage'
)
class ErrorPageTests(SimpleTestCase):
	def setUp(self):
		self.factory = RequestFactory()

	@override_settings(DEBUG=False)
	def test_custom_404_template_is_used(self):
		response = self.client.get('/totally-missing-page/')
		self.assertEqual(response.status_code, 404)
		self.assertTemplateUsed(response, 'core/errors/error_page.html')
		self.assertContains(response, 'Page not found', status_code=404)

	@override_settings(DEBUG=False)
	def test_middleware_renders_method_not_allowed(self):
		request = self.factory.post('/blocked-endpoint/')
		original_response = HttpResponseNotAllowed(['GET'])
		middleware = CustomErrorPageMiddleware(lambda req: original_response)

		rendered = middleware.process_response(request, original_response)

		self.assertEqual(rendered.status_code, 405)
		self.assertIn('Method not allowed', rendered.content.decode())
		self.assertEqual(rendered['Allow'], 'GET')
