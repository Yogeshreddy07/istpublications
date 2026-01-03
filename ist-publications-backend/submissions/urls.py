from django.urls import path
from . import views

app_name = 'submissions'

urlpatterns = [
    # Submission creation
    path('create', views.CreateSubmissionView.as_view(), name='create-submission'),
    
    # Step endpoints
    path('<str:submission_id>/step/1', views.SaveStep1View.as_view(), name='save-step-1'),
    path('<str:submission_id>/step/2', views.SaveStep2View.as_view(), name='save-step-2'),
    path('<str:submission_id>/step/3', views.SaveStep3View.as_view(), name='save-step-3'),
    path('<str:submission_id>/step/4', views.SaveStep4View.as_view(), name='save-step-4'),
    path('<str:submission_id>/step/5', views.SaveStep5View.as_view(), name='save-step-5'),
    path('<str:submission_id>/step/6/finalize', views.FinalizeSubmissionView.as_view(), name='finalize-submission'),
    
    # Retrieval endpoints
    path('<str:submission_id>', views.GetSubmissionView.as_view(), name='get-submission'),
]
