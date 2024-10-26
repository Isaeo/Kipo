from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from .models import Part
from openai import OpenAI
import environ
from pathlib import Path
import os
env = environ.Env()
BASE_DIR = Path(__file__).resolve().parent.parent
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))
api_key = env('OPENAI_API_KEY')
print(api_key)
client = OpenAI(api_key= api_key)



completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": "Write a haiku about recursion in programming."
        }
    ]
)

print(completion.choices[0].message)
def index(request):
    return render(request, "search/index.html")


def find_substitute(request):
    query = request.POST.get("query", "") if request.method == "POST" else request.GET.get("query", "")
    data = []

    if query:
        # Perform full-text search
        fquery = generate_keywords(query)
        print(fquery)
        search_query = SearchQuery(fquery)
        results = Part.objects.annotate(
            rank=SearchRank('search_vector', search_query)
        ).filter(rank__gte=0.12).order_by('-rank')
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
    ).filter(rank__gte=0.2).order_by('-rank')

    # Load datasheet content dynamically for each product
    for product in results:
        product.datasheet_content = product.load_datasheet_content()

    return render(request, "search/results.html", {"results": results})


def generate_keywords(user_input):
    prompt = (
        f"Extract key searchable terms from this input to help find electronic components or parts. "
        f"The input is: '{user_input}'"
        f"The Database we are querying is segmented into the following columns, in order of importance, with different formats: "

        f"1. 'mfr_part_number': The manufacturer part number, a unique identifier for each product. "
        f"2. 'mouser_part_number': A distributor-specific part number used by Mouser Electronics. "
        f"3. 'manufacturer': The name of the company that produces the part, like 'Phoenix Contact' or 'Molex'. "
        f"4. 'product_category': The general category or type of product, such as 'connectors', 'resistors', or 'relays'. "
        f"5. 'ip_rating': The IP (Ingress Protection) rating, which indicates the product's level of protection against dust and water, like 'IP67' or 'IP44'. "
        f"6. 'termination_style': The method by which the product connects to other parts, such as 'screw connection', 'crimp', or 'solder'. "
        f"7. 'contact_gender': Specifies whether the connector is 'male' or 'female', 'pin'  or 'socket. "
        f"8. 'datasheet_content': A freeform txt of the product datasheet from which most of the other data was extracted, you may include anything that seems like technical or descriptive specifications for a part"


        f"Based on these categories, identify keywords that are likely to match relevant fields in the database. You need not find a keyword for each column, only retrieve words that exist in the input "
        f"Format your reply as a simple string containing only all the keywords"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system",
                 "content": "You are an assistant that extracts key searchable terms for electronic components."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5
        )
        keywords = response.choices[0].message.content.strip()
        #print(keywords)
        return keywords
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return user_input  # fallback to original input if API fails