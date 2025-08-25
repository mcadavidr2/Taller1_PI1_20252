import matplotlib
matplotlib.use('Agg')  # Para evitar problemas en servidores sin interfaz gráfica
import matplotlib.pyplot as plt
import io, base64

from django.shortcuts import render
from django.http import HttpResponse
from .models import Movie


def home(request):
    searchTerm = request.GET.get('searchMovie')
    if searchTerm:
        movies = Movie.objects.filter(title__icontains=searchTerm)
    else:
        movies = Movie.objects.all()
    return render(request, 'home.html', {'searchTerm': searchTerm, 'movies': movies})


def about(request):
    return HttpResponse('<h1>Welcome to About page</h1>')


def signup(request):
    email = request.GET.get('email')
    return render(request, 'signup.html', {'email': email})


def statistics_view(request):
    # Obtener todos los años de las películas (ordenados)
    years = Movie.objects.values_list('year', flat=True).distinct().order_by('year')

    # Diccionario para almacenar la cantidad de películas por año
    movie_counts_by_year = {}
    for year in years:
        if year:
            movies_in_year = Movie.objects.filter(year=year)
        else:
            movies_in_year = Movie.objects.filter(year__isnull=True)
            year = "None"
        movie_counts_by_year[year] = movies_in_year.count()

    # Configuración de la gráfica
    bar_width = 0.5
    bar_positions = range(len(movie_counts_by_year))

    plt.bar(bar_positions, movie_counts_by_year.values(), width=bar_width, align='center')
    plt.title('Movies per year')
    plt.xlabel('Year')
    plt.ylabel('Number of movies')
    plt.xticks(bar_positions, movie_counts_by_year.keys(), rotation=90)
    plt.subplots_adjust(bottom=0.3)

    # Guardar la gráfica en memoria
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    plt.close()

    # Convertir la imagen a base64 para enviarla al template
    graphic = base64.b64encode(image_png).decode('utf-8')

    # Renderizar la plantilla con la gráfica
    return render(request, 'statistics.html', {'graphic': graphic})
