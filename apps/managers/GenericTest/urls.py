from rest_framework import routers
from django.urls import path
from apps.managers.GenericTest.views import (GenericTest2,
                                             GenericTest,
                                             GenericTest3,
                                             GenericTest4,
                                             ListMixinTest,
                                             CreateMixinTest,
                                             DestroyMixinTest,
                                             UpdateMixinTest,)

urlpatterns = [
    path('test/', GenericTest2.as_view()),
    path('test2/', GenericTest.as_view()),
    path('test3/', GenericTest3.as_view()),
    path('test4/<int:pk>', GenericTest4.as_view()),
    path('testMixin5/', ListMixinTest.as_view()),
    path('testMixin6/', CreateMixinTest.as_view()),
    path('testMixin7/<int:pk>', DestroyMixinTest.as_view()),
    path('testMixin8/<int:pk>', UpdateMixinTest.as_view())
]