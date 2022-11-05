from django.views import View
from django.shortcuts import render, redirect

from . import decorators


class ImportDataService(View):
    template_name = None
    form = None

    @decorators.check_status_import_data
    def get(self, request):
        return render(request, self.template_name, context={
            'form': self.form()
        })

    def post(self, request):
        form = self.form(request.POST, request.FILES)
        if form.is_valid():
            form.load(request)
            return redirect('import_data')
        return render(request, self.template_name, context={
            'form': form,
        })