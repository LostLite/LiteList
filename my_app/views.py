import requests
from django.shortcuts import render
from django.core.paginator import Paginator
from requests.compat import quote_plus
from bs4 import BeautifulSoup
from .models import Search


BASE_CRAIGSLIST_URL = 'https://kenya.craigslist.org/search/?query={}'
BASE_IMAGE_URL = 'https://images.craigslist.org/{}_300x300.jpg'


# Create your views here.
def home(request):
    return render(request, 'base.html')


def new_search(request):
    search = request.POST.get('search')
    final_postings = []
    

    if search:
        try:
            existing_search, created = Search.objects.get_or_create(search=search)
            existing_search.hits += 1
            existing_search.save()

            # Get web page adn extract source code
            data = requests.get(BASE_CRAIGSLIST_URL.format(quote_plus(search))).text

            # create BeautifulSoup object for import
            soup = BeautifulSoup(data, features='html.parser')

            # extract into a list all the <a> tags whose class name is 'result-title'
            post_listings = soup.find_all('li', { 'class': 'result-row' })

            for post in post_listings:
                post_title = post.find(class_='result_title')
                post_url = post.find('a').get('href')

                if post.find(class_='result_price'):
                    post_price = post.find(class_='result_price').text
                else:
                    post_price = 'N/A'

                if post.find(class_='result-image').get('data-ids'):
                    post_image_id = post.find(class_='result-image').get('data-ids').split(',')[0].split(':')[1]
                    post_image_url = BASE_IMAGE_URL.format(post_image_id)
                    print(post_image_url)
                else:
                    post_image_url = 'https://craigslist.org/images/peace.jpg'

                final_postings.append((post_title, post_url, post_price, post_image_url))

        except (KeyError, Search.DoesNotExist): 
            search = 'Provide a valid search value'
    
    else:
        search = 'Provide a valid search value'

    paginator = Paginator(final_postings, 6)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'search': search,
        'final_postings': final_postings,
        'page_obj': page_obj,
    }

    return render(request, 'my_app/new_search.html', context)
