from django.urls import path
from . import views
#create urls here..
app_name = 'account'
urlpatterns =[
    path('login/',views.logInPage,name='login'),
    path('signup/',views.signUpPage,name='signup'),
    path('logout/',views.log_out,name='logout'),
]