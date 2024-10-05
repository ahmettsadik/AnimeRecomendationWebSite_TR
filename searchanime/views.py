from django.shortcuts import render
from django.http import JsonResponse
from .models import Anime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

def load_anime_data():
    # Load anime data into a DataFrame
    anime_data = pd.DataFrame(list(Anime.objects.all().values()))

    # Clean and preprocess the genres
    anime_data['genres'] = anime_data['genres'].apply(lambda x: " ".join(x.lower() for x in x.split(',')))

    # TF-IDF vectorizer for feature extraction
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(anime_data['genres'])

    # Calculate cosine similarity matrix
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

    # Create a Series to map anime names to indices
    anime_indices = pd.Series(anime_data.index, index=anime_data['english_name']).drop_duplicates()

    return anime_data, cosine_sim, anime_indices

def autocomplete_view(request):
    if 'term' in request.GET:
        qs = Anime.objects.filter(english_name__istartswith=request.GET.get('term'))
        names = list(qs.values_list('english_name', flat=True))
        return JsonResponse(names, safe=False)
    return JsonResponse([], safe=False)

def search_view(request):
    return render(request, 'searchanime/search.html')

def get_recommendations(title, limit=5, offset=0):
    anime_data, cosine_sim, anime_indices = load_anime_data()
    
    if title not in anime_indices:
        raise KeyError(f"Anime title '{title}' not found in the dataset.")
    
    # Get the index of the given anime
    idx = anime_indices[title]
    
    # Get similarity scores for all anime
    sim_scores = list(enumerate(cosine_sim[idx]))
    
    # Sort the anime based on similarity scores
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    
    # Get the indices of the most similar anime
    sim_scores = sim_scores[1:51]  # Exclude the first one (itself)
    anime_indices_list = [i[0] for i in sim_scores]
    
    # Get the recommended anime based on similarity scores
    recommended_animes = anime_data.iloc[anime_indices_list]
    
    # Apply limit and offset
    recommended_animes = recommended_animes[offset:offset + limit]
    
    # Include similarity scores in the result
    recommended_animes['sim_scores'] = [sim_scores[i][1] for i in range(offset, offset + limit)]
    
    return recommended_animes

def öneri_view(request):
    if request.method == 'POST':
        anime_name = request.POST.get('anime_name')
        offset = int(request.POST.get('offset', 0))
        
        if not anime_name:
            return render(request, 'searchanime/search.html', {'error': "Anime adı boş olamaz."})
        
        try:
            öneriler = get_recommendations(anime_name, limit=5, offset=offset)
            no_more_recommendations = öneriler.empty
        except KeyError as e:
            return render(request, 'searchanime/search.html', {'error': str(e)})
        except IndexError:
            öneriler = pd.DataFrame()
            no_more_recommendations = True
        
        öneri_isimleri = [{'mal_id': anime['mal_id'], 'english_name': anime['english_name'], 'score': anime['score'], 'genres': anime['genres'], 'popularity': anime['popularity'], 'sim_scores': anime['sim_scores']*100} for _, anime in öneriler.iterrows()]
        return render(request, 'searchanime/öneri.html', {'öneriler': öneri_isimleri, 'anime_name': anime_name, 'offset': offset + 5, 'no_more_recommendations': no_more_recommendations})
    
    return render(request, 'searchanime/search.html')