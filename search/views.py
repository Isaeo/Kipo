from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from .models import Part

def index(request):
    return render(request, "search/index.html")


def find_substitute(request):
    query = request.POST.get("query", "") if request.method == "POST" else request.GET.get("query", "")
    data = []

    if query:
        # Perform full-text search
        search_query = SearchQuery(query, search_type='websearch')
        results = Part.objects.annotate(
            rank=SearchRank('search_vector', search_query)
        ).filter(rank__gte=0.06).order_by('-rank')
        # Format results to match substitute.html's expected structure
        data = [
            {
                "mpn": product.mouser_part_number,
                "description": {
                    "IP Rating": product.ip_rating,
                    "Product": product.product_category,
                    "Contact Gender": product.contact_gender,
                    "Termination": product.termination_style,
                }
            }
            for product in results
        ]

    return render(request, "search/substitute.html", {"data": data, "query": query})

def compare_parts(request):
    parts = Part.objects.all().values()  # Fetch all parts
    return render(request, "search/comparison.html", {"parts": parts})


def search_products(request):
    query = request.GET.get("query", "")
    search_query = SearchQuery(query)
    results = Product.objects.annotate(
        rank=SearchRank(SearchVector('mfr_part_number', 'manufacturer', 'product_category'), search_query)
    ).filter(rank__gte=0.1).order_by('-rank')

    # Load datasheet content dynamically for each product
    for product in results:
        product.datasheet_content = product.load_datasheet_content()

    return render(request, "search/results.html", {"results": results})