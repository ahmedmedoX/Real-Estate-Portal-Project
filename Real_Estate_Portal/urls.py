from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('',views.home, name='home'),
    path('contact_us/',views.contact_us, name='contact_us'),
    path('about/',views.about,name='about'),

    path('login/',views.login_user, name='login'),
    path('logout/',views.logout_user, name='logout'),
    path('signup/',views.sign_up, name='sign_up'),
    path('signup2/',views.sign_up2, name='sign_up2'),
    path('update_profile/',views.update_profile, name='update_profile'),
    path('delete_confirm/',views.delete_confirm, name='delete_confirm'),
    path('delete_account/',views.delete_account, name='delete_account'),
    path('profile/',views.profile,name='profile'),
    path('favorite/',views.favorite,name='favorite'),

    path('search/',views.search,name='search'),
    path('search_type/<str:type>',views.type_search,name='type_search'),
    path('search_area/<str:area>',views.area_search,name='area_search'),

    path('property/<int:id>',views.property,name='property'),
    path('list_property/',views.list_property,name='list_property'),
    path('rent_property/',views.rent_property,name='rent_property'),
    path('insert_property/',views.insert_property,name='insert_property'),
    path('your_properties/',views.your_properties,name='your_properties'),
    path('edit_property/<int:id>',views.edit_property,name='edit_property'),
    path('update_property/<int:id>',views.update_property,name='update_property'),
    path('delete_property/<int:id>',views.delete_property,name='delete_property'),
    path('delete_property_confirm/<int:id>',views.delete_property_confirm,name='delete_property_confirm'),
    path('delete_all/',views.delete_all,name='delete_all'),
    path('delete_all_confirm/',views.delete_all_confirm,name='delete_all_confirm'),

    path('add_favourite/',views.add_favourite,name='add_favourite'),

    path('reset_password/',auth_views.PasswordResetView.as_view(template_name='PasswordReset.html'),name='reset_password'),
    path('reset_password_sent/',auth_views.PasswordResetDoneView.as_view(template_name='PasswordResetSent.html'),name='password_reset_done'),
    path('reset/<uidb64>/<token>',auth_views.PasswordResetConfirmView.as_view(template_name='PasswordResetConfirm.html'),name='password_reset_confirm'),
    path('reset_password_complete/',auth_views.PasswordResetCompleteView.as_view(template_name='PasswordResetComplete.html'),name='password_reset_complete')
]
