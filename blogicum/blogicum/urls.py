from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.forms import UserCreationForm
from django.urls import include, path, reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView

handler404 = 'pages.views.page_not_found'
handler500 = 'pages.views.server_error'
handler403 = 'pages.views.csrf_failure'
urlpatterns = [
path('admin/', admin.site.urls),
    path('auth/', include('django.contrib.auth.urls')),
    # Используем CBV для статичных страниц:
    path(
        'about/', 
        TemplateView.as_view(template_name='pages/about.html'), 
        name='about'
    ),
    path(
        'rules/', 
        TemplateView.as_view(template_name='pages/rules.html'), 
        name='rules'
    ),
    path('', include('blog.urls', namespace='blog')),
    path('admin/', admin.site.urls),
    path('auth/', include('users.urls')),
    path('auth/', include('django.contrib.auth.urls')),
    path('', include('blog.urls', namespace='blog')),
    path('pages/', include('pages.urls', namespace='pages')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)