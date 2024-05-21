"""
URL configuration for DriveMonitoringApp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from DataStorage import views as Sv
from django.conf import settings
from django.conf.urls.static import static

#Here are the accesible urls, the format is ("PATH", FUNCTION CALLED, NAME), The static part on the end is just to work with static files and allow the urls to acces the static content
urlpatterns = [
    path('admin/', admin.site.urls),
    path('driveMonitoring', Sv.driveMonitoring, name="driveMonitoring"),
    path('driveMonitoring/', Sv.driveMonitoring, name="driveMonitoringD"),
    path('loadPins', Sv.loadPins, name="loadPins"),
    path('loadPins/', Sv.loadPins, name="loadPinsD"),
    path('storage/getLogs', Sv.getLogs),
    path('storage/getData', Sv.getData),
    path('storage/test', Sv.showTestView),
    path('storage/plotGeneration', Sv.generateDatePlots),
    path('storage/getLoadPins', Sv.getLoadPins),
    path('storage/generateHotPlots', Sv.generateHotPlots),
    path('storage/hotPlotGeneration', Sv.generateDriveHotPlots),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
