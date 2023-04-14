from django.shortcuts import render
from django.views.generic import ListView
# Create your views here.


class ThemeListView(ListView):
    template_name = 'puzzle_theme.html'
    context_object_name = 'themes'

    def get_queryset(self):
        return


def theme_detail(request, theme):
    return render(request, 'puzzle_detail.html', context={'theme': theme})


def theme_detail_all(request, category):
    if category == 'all':
        return render(request, 'puzzle_detail.html', context={'theme': 'all'})
    elif category == 'attack':
        return render(request, 'puzzle_attack.html', context={'theme': 'attack'})


def opening_list(request):
    return render(request, 'opening_list.html')


def opening_detail(request, name):
    return render(request, 'opening_detail.html', context={'name': name})


def opening_detail_puzzle(request, name: str):
    return render(request, 'puzzle_opening.html', context={'name': name})


def opening_stratigy_puzzle(request, name):
    return render(request, 'opening_stratigy_puzzle.html', context={'name': name})
