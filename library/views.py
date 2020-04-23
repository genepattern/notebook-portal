import os
from django.http import HttpResponse
from django.template import loader
from django.views.static import serve
from django.contrib.auth import logout as logout_user
from django.shortcuts import redirect
import library.thumbnail as thumbnail


def logout(request):
    logout_user(request)
    return redirect('/')


def serve_thumbnail(request, id):
    # Lazily generate thumbnail if it does not exist
    if not thumbnail.exists(id):
        thumbnail.generate(id)

    path = thumbnail.thumbnail_path(id)

    # Serve the file
    response = serve(request, os.path.basename(path), os.path.dirname(path))
    return response


def dashboard(request):
    # Get the notebook model
    # notebooks = Notebook.objects.all()[0:5]

    # Display the dashboard template
    template = loader.get_template('pages/dashboard.html')
    context = {
        # 'notebooks': notebooks
    }
    return HttpResponse(template.render(context, request))


def workspace(request):
    # Display the workspace template
    template = loader.get_template('pages/workspace.html')
    return HttpResponse(template.render({}, request))


def library(request):
    # Display the library template
    template = loader.get_template('pages/library.html')
    return HttpResponse(template.render({}, request))


def jobs(request):
    # Display the jobs template
    template = loader.get_template('pages/jobs.html')
    return HttpResponse(template.render({}, request))


def analyses(request):
    # Display the analysis template
    template = loader.get_template('pages/analyses.html')
    return HttpResponse(template.render({}, request))


def docs(request):
    # Display the analysis template
    template = loader.get_template('pages/docs.html')
    return HttpResponse(template.render({}, request))


def run_analysis(request, lsid):
    # Display the run template
    template = loader.get_template('pages/run_analysis.html')
    return HttpResponse(template.render({'lsid': lsid}, request))


